#!/usr/bin/env python
from multiprocessing import Process, Queue
from PIL import Image
import cv2
import numpy as np
import time
import sys, os


def image_display(left, right, outqueue): 
   while True:
      left_frame = left.get()              
      right_frame = right.get()
   
      
      image = np.concatenate((left_frame, right_frame), axis=1)
      outqueue.put(image)

      continue                             # Added


class Reader(Process):
   def __init__(self,framequeue, printqueue):
      Process.__init__(self)
      self.que=printqueue
      self.frame = framequeue

   def image_print(self):
      im = Image.fromarray(self.frame.get())
      im_dict = {
      'pixels': im.tobytes(),
      'size': im.size,
      'mode': im.mode,
      }
      return(im_dict)
   def run(self):
        self.que.put(self.image_print())



class Printr(Process):
   #this process will write numpy arrays to the pid.out
   #useful for debugging, mainly exists as proof-of-concept
   def __init__(self, toprint):
      Process.__init__(self)
      self.toprint = toprint
   def run(self):
      self.initialize_logging()
      print(self.toprint.get())
   def initialize_logging(self):
      #having tons of trouble with latency printing from stdout
      sys.stdout = open(str(os.getpid()) + ".out", "a")
      sys.stderr = open(str(os.getpid()) + "_error.out", "a")


class Feature():
   def __init__(self, cap_idx):
      self.cap = cv2.VideoCapture(cap_idx)
      self.begin()
   def unfiltered(self):
      self.ret, self.frame = self.cap.read()
      return(self.frame)
   def begin(self):
      self.frame1 = self.unfiltered()
      self.prvs = cv2.cvtColor(self.frame1,cv2.COLOR_BGR2GRAY)
      self.hsv = np.zeros_like(self.frame1)
      self.hsv[...,1] = 255

      r,h,c,w = 200,20,300,20  #row, height, column, width  
      self.track_window = (r,h,c,w)
      self.roi = self.frame[r:r+h, c:c+w]
      self.hsv_roi =  cv2.cvtColor(self.frame1, cv2.COLOR_BGR2HSV)
      self.mask = cv2.inRange(self.hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
      self.roi_hist = cv2.calcHist([self.hsv_roi],[0],self.mask,[180],[0,180])
      cv2.normalize(self.roi_hist,self.roi_hist,0,255,cv2.NORM_MINMAX)

      # Setup the termination criteria, either 10 iteration or move by at least 1 pt
      self.term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )


   def detect(self):
      self.ret, self.frame2 = self.cap.read()
      self.next = cv2.cvtColor(self.frame2,cv2.COLOR_BGR2GRAY)
      self.flow = cv2.calcOpticalFlowFarneback(self.prvs, self.next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
      self.mag, self.ang = cv2.cartToPolar(self.flow[...,0], self.flow[...,1])
      self.hsv[...,0] = self.ang*180/np.pi/2
      self.hsv[...,2] = cv2.normalize(self.mag,None,0,255,cv2.NORM_MINMAX)
      self.rgb = cv2.cvtColor(self.hsv,cv2.COLOR_HSV2BGR)

      self.dst = cv2.calcBackProject([self.rgb],[0],self.roi_hist,[0,180],1)
      # apply meanshift to get the new location
      self.ret, self.track_window = cv2.meanShift(self.dst, self.track_window, self.term_crit)

      # Draw it on image
      self.x,self.y,self.w,self.h = self.track_window
      self.img2 = cv2.rectangle(self.rgb, (self.x,self.y), (self.x+self.w,self.y+self.h), 255,2)
      return (self.img2)
      


if __name__ == '__main__':
   #queues to handle the exchange of data between processes 
   taskqueue = Queue()
   
   printer = Queue()
   outqueue = Queue()
   
   leftqueue = Queue()
   rightqueue = Queue()

   #instantiate  capture class
   left_handle = Feature(1)
   right_handle = Feature(0)


   eyes = Process(target=image_display, args=(leftqueue, rightqueue, outqueue))
   eyes.start()

   r= Reader(taskqueue, printer).start()
   #p = Printr(printer).start()
   #enable Printer for debugging log
   while True:

      left_image=left_handle.detect()
      #left_image=left_handle.unfiltered()

      #right_image=right_handle.unfiltered()

      right_image=right_handle.detect()

      leftqueue.put(left_image)
      rightqueue.put(right_image)
      input_frame = outqueue.get()
      taskqueue.put(input_frame)
      cv2.imshow('combined output', input_frame)
      stroke = (cv2.waitKey(30) & 0xFF)
      if stroke == ord('q'):
         print ("user abort by input")
         cv2.destroyAllWindows()
         exit(0)
         break
      elif stroke == ord('w'):
         print ("writing output")
         cv2.imwrite("sample.png", input_frame)
         continue
      elif stroke == ord('r'):
         print ("resetting orientation")
         left_handle.begin()
         right_handle.begin()
         continue

      continue

taskqueue.put(None)
cv2.destroyAllWindows()