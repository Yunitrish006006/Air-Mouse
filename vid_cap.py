import cv2
import numpy as np
import math
if __name__ == '__main__':
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1080)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,360)

    cv2.namedWindow("live", cv2.WINDOW_AUTOSIZE); # 命名一個視窗，可不寫
    while(True):
        # 擷取影像
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # 彩色轉灰階
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #edge founder
        img_x = abs(cv2.Sobel(frame,cv2.CV_16S,1,0))
        img_y = abs(cv2.Sobel(frame,cv2.CV_16S,0,1))
        img_x = cv2.convertScaleAbs(img_x)
        img_y = cv2.convertScaleAbs(img_y)
        img_e = cv2.addWeighted(img_x,0.5,img_y,0.5,0.3)
        #canny
        image_c = cv2.Canny(img_gray, 50, 200, 3)
        image_canny = cv2.convertScaleAbs(image_c)
        #houghLines
        # dst = cv2.Canny(frame, 50, 200, None, 3)
        # cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
        # cdstP = np.copy(cdst)
        # lines = cv2.HoughLines(dst, 1, np.pi / 180, 150, None, 0, 0)
        # if lines is not None:
        #     for i in range(0, len(lines)):
        #         rho = lines[i][0][0]
        #         theta = lines[i][0][1]
        #         a = math.cos(theta)
        #         b = math.sin(theta)
        #         x0 = a * rho
        #         y0 = b * rho
        #         pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        #         pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
        #         cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
        # linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 50, 10)
        
        # if linesP is not None:
        #     for i in range(0, len(linesP)):
        #         l = linesP[i][0]
        #         cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
        #mixer
        img_e = (255-img_e)
        img_all = cv2.addWeighted(img_e,1,frame,0,0)
        # img_all = cv2.cvtColor(img_all,cv2.COLOR_RGB2GRAY)
        # 顯示圖片
        cv2.imshow('live', img_all)

        # 按下 q 鍵離開迴圈
        if cv2.waitKey(1) == ord('q'):
            break

    # 釋放該攝影機裝置
    cap.release()
    cv2.destroyAllWindows()