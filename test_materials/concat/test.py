import numpy as np, cv2
while True:
  er1, img1 = cv2.VideoCapture(0).read()
  er2, img2 = cv2.VideoCapture(1).read()
  if er1 == True and er2 == True:
    vis = np.concatenate((img1, img2), axis=1)
    cv2.imshow('out', vis)
    if (cv2.waitKey(1) & 0xFF) == ord('q'):
      break
  