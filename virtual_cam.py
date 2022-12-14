import pyvirtualcam as vc
import cv2
import numpy as np

if __name__ == '__main__':
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    fmt = vc.PixelFormat.BGR
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    with vc.Camera(width=1920,height=1080,fps=60,fmt=fmt) as cam:
        while True:
            ret , frame =cap.read()
            frame = cv2.resize(frame,(1920,1080),interpolation=cv2.BORDER_DEFAULT)
            f2 = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            # cv2.imshow('cam',frame)
            # f2 = cv2.resize(f2,(1920,1080),interpolation=cv2.INTER_CUBIC)
            # f2 = np.reshape(f2,[1080,1920,3])
            f2 = cv2.convertScaleAbs(f2)
            f3 = cv2.addWeighted(frame,1,f2,0.2,None)
            cam.send(frame=f3)
            cam.sleep_until_next_frame()
            if cv2.waitKey(1) == ord('q'): break
        cv2.destroyAllWindows