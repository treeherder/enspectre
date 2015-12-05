#!/usr/bin/env python
from multiprocessing import Process, Queue
from PIL import Image
import cv2
import numpy as np
from datetime import datetime

class Camera(Process):
   def __init__(self, task, angle):
      super(Camera, self).__init__()
      self.task = task
      self.angle = angle

   def frame_feed(self):
      while True:
         frame = self.task.get()  #get frame from process queue
         if frame is None:
            break
         (h, w) = frame.shape[:2]
         center = (w / 2, h / 2)  #incase we change the shape/size farther down the line
         M = cv2.getRotationMatrix2D(center, seelf.angle, 1.0)
         frame = cv2.warpAffine(frame, M, (w, h))  #remap rotated frame to orignal
  


if __name__ == '__main__':
   task_right = Queue()
   task_left = Queue()
   con_task = Queue()

   capture_0 = cv2.VideoCapture(0)
   capture_1 = cv2.VideoCapture(1)

   left_cam = Camera(task_left, -90,)
   left_cam.start()
   right_cam = Camera(task_right, 90,)
   right_cam.start()
   while True:
      flag0, frame0=capture_0.read()
      flag1, frame1=capture_1.read()

      task_right.put(frame0)
      task_left.put(frame1)

      combo = np.concatenate((frame0, frame1), axis=1)

      cv2.imshow('combined output', combo)
      if (cv2.waitKey(1) & 0xFF) == ord('q'):
         print ("user abort by input")
         cv2.destroyAllWindows()
         exit(0)
         break
      
      continue             #everything fails without the continue?
