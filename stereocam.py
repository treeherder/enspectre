#!/usr/bin/env python
from multiprocessing import Process, Queue
from PIL import Image
import cv2
import numpy as np
import time           # Added

def frame_feed(task, angle):
   cv2.namedWindow ('autosize frame', cv2.WINDOW_NORMAL)
   while True:

      frame = task.get()
      if frame is None:
         break
      (h, w) = frame.shape[:2]
      center = (w / 2, h / 2)  #incase we change the shape/size farther down the line
      M = cv2.getRotationMatrix2D(center, angle, 1.0)
      frame = cv2.warpAffine(frame, M, (w, h))  #remap rotated frame to orignal
      cv2.imshow ('Process: {0}'.format(task), frame)
      if (cv2.waitKey(1) & 0xFF) == ord('q'):
         print ("user abort on {0}".format(task))
         cv2.destroyAllWindows()
         break
      else:
         continue
      if task.get()==None:
         print ("QUEUE object empty")
         continue
      else:
         frame = task.get()
         im = frame.fromstring(frame['mode'], frame['size'], frame['pixels'])
         num_im = np.asarray(im)
         cv2.imshow ('frame from array', num_im)


def make_mat(from_frame):
   frame_mat = {
      'pixels': from_frame.tostring(),
      'size': from_frame.size,
      'mode': from_frame.mode,
      }
   return (frame_mat)

if __name__ == '__main__':
   task_0 = Queue()
   task_1 = Queue()
   capture_0 = cv2.VideoCapture(0)
   capture_1 = cv2.VideoCapture(1)

   p = Process(target=frame_feed, args=(task_1, -90,))
   p.start()
   o = Process(target=frame_feed, args=(task_0, 90,))
   o.start()
   while True:
      flag0, frame0=capture_0.read()
      flag1, frame1=capture_1.read()

      task_0.put(frame0)
      task_1.put(frame1)
#      time.sleep(0.010)
      continue             #everything fails without a slight pause and the continue

      if flag0 == 0 or flag1==0:
         break
      im0 = frame.fromarray(frame0)
      mat_0 = make_mat(im0)
      task_0.put(mat_0)
      im1 = frame.fromarray(frame1)
      mat_0 = make_mat(im1)
      task_1.put(mat_1)
      
task_0.put(None)
task_1.put(None)
o.join()
p.join()
cv2.DestroyAllWindows()
