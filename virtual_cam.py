import pyvirtualcam as vc
import cv2

if __name__ == '__main__':
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    fmt = vc.PixelFormat.BGR
    with vc.Camera(width=1920,height=1080,fps=60,) as cam:
        while True:
            ret , frame =cap.read()
            frame = cv2.resize(frame,(1920,1080),interpolation=cv2.BORDER_DEFAULT)
            cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
            cv2.imshow('cam',frame)
            cam.send(frame=frame)
            cam.sleep_until_next_frame()
            if cv2.waitKey(1) == ord('q'): break
        cv2.destroyAllWindows