#!/usr/bin/env python
from multiprocessing import Process, Queue
from PIL import Image
import cv2
import numpy as np
import time
import sys, os
from stereocam import *
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
