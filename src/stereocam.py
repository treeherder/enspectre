#!/usr/bin/env python
from multiprocessing import Process, Queue
from PIL import Image
import cv2
import numpy as np
import time
def image_display(left, right, outqueue):
   while True:
      left_frame= left.get()              
      right_frame = right.get()# Added
      image = np.concatenate((left_frame, right_frame), axis=1)


      outqueue.put(image)

      continue                             # Added



if __name__ == '__main__':
   taskqueue = Queue()
   outqueue = Queue()
   leftqueue = Queue()
   rightqueue = Queue()
   left_handle = cv2.VideoCapture(0)
   right_handle = cv2.VideoCapture(1)
   p = Process(target=image_display, args=(leftqueue, rightqueue, outqueue))
   p.start()
   while True:
      flag, left_image=left_handle.read()

      flag, right_image=right_handle.read()

      leftqueue.put(left_image)  # Added
      rightqueue.put(right_image)  # Added
      input_frame = outqueue.get()
      cv2.imshow('combined output', input_frame)
      if (cv2.waitKey(10) & 0xFF) == ord('q'):
         print ("user abort by input")
         cv2.destroyAllWindows()
         exit(0)
         break


taskqueue.put(None)
p.join()
cv2.destroyAllWindows()