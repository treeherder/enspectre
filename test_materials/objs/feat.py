import cv2
import numpy as np
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

f =Feature(0)

while True:
    cv2.imshow('frame2',f.detect())
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    elif k == ord('s'):
        cv2.imwrite('opticalfb.png',frame2)
        cv2.imwrite('opticalhsv.png',rgb)
    prvs = next

cap.release()
cv2.destroyAllWindows()