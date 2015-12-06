#!/usr/bin/env python
from multiprocessing import Process, Queue
from PIL import Image
import cv2
import numpy as np
import time
import sys, os


def image_display(left, right, outqueue):
   while True:
      left_frame= left.get()              
      right_frame = right.get()# Added
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



if __name__ == '__main__':
   #queues to handle the exchange of data between processes 
   taskqueue = Queue()
   
   printer = Queue()
   outqueue = Queue()
   
   leftqueue = Queue()
   rightqueue = Queue()

   #instantiate  capture class
   left_handle = cv2.VideoCapture(1)
   right_handle = cv2.VideoCapture(0)


   eyes = Process(target=image_display, args=(leftqueue, rightqueue, outqueue))
   eyes.start()

   r= Reader( taskqueue, printer).start()
   #p = Printr(printer).start()
   #enable Printer for debugging log
   while True:

      flag, left_image=left_handle.read()

      flag, right_image=right_handle.read()

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