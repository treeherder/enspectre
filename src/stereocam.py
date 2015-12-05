#!/usr/bin/env python
from multiprocessing import Process, Queue
from PIL import Image
import cv2
import numpy as np
import time

def frame_feed(task, angle, outqueue):
   while True:
      frame = task.get()  #get frame from process queue
      if frame is None:
         break
      (h, w) = frame.shape[:2]
      center = (w / 2, h / 2)  #incase we change the shape/size farther down the line
      M = cv2.getRotationMatrix2D(center, angle, 1.0)
      frame = cv2.warpAffine(frame, M, (w, h))  #remap rotated frame to orignal
  


if __name__ == '__main__':
   task_0 = Queue()
   task_1 = Queue()
   con_task = Queue()

   capture_0 = cv2.VideoCapture(0)
   capture_1 = cv2.VideoCapture(1)

   left_cam = Process(target=frame_feed, args=(task_1, -90, con_task))
   left_cam.start()
   right_cam = Process(target=frame_feed, args=(task_0, 90, con_task))
   right_cam.start()
   while True:
      flag0, frame0=capture_0.read()
      flag1, frame1=capture_1.read()

      task_0.put(frame0)
      task_1.put(frame1)

      combo = np.concatenate((frame0, frame1), axis=1)

      cv2.imshow('combined output  {0}'.format(time.Now()), combo)
      if (cv2.waitKey(1) & 0xFF) == ord('q'):
         print ("user abort by input")
         cv2.destroyAllWindows()
         exit(0)
         break
      
      continue             #everything fails without the continue?
