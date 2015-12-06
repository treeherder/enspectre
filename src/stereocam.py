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
        self.ret, self.frame1 = self.cap.read()
        self.prvs = cv2.cvtColor(self.frame1,cv2.COLOR_BGR2GRAY)
        self.hsv = np.zeros_like(self.frame1)
        self.hsv[...,1] = 255

    def detect(self):
        self.ret, self.frame2 = self.cap.read()
        self.next = cv2.cvtColor(self.frame2,cv2.COLOR_BGR2GRAY)

        self.flow = cv2.calcOpticalFlowFarneback(self.prvs, self.next, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        self.mag, self.ang = cv2.cartToPolar(self.flow[...,0], self.flow[...,1])
        self.hsv[...,0] = self.ang*180/np.pi/2
        self.hsv[...,2] = cv2.normalize(self.mag,None,0,255,cv2.NORM_MINMAX)
        self.rgb = cv2.cvtColor(self.hsv,cv2.COLOR_HSV2BGR)
        return (self.rgb)




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

   r= Reader( taskqueue, printer).start()
   #p = Printr(printer).start()
   #enable Printer for debugging log
   while True:

      left_image=left_handle.detect()

      right_image=right_handle.detect()

      leftqueue.put(left_image)  # Added
      rightqueue.put(right_image)  # Added
      input_frame = outqueue.get()
      taskqueue.put(input_frame)
      cv2.imshow('combined output', input_frame)

      if (cv2.waitKey(10) & 0xFF) == ord('q'):
         print ("user abort by input")
         cv2.destroyAllWindows()
         exit(0)
         break
      if (cv2.waitKey(10) & 0xFF) == ord('w'):

         print ("writing output")
         cv2.imwrite("sample.png", input_frame)
         continue

      continue

taskqueue.put(None)
p.join()
cv2.destroyAllWindows()