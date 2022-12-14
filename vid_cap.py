import cv2

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

#cv2.namedWindow("live", cv2.WINDOW_AUTOSIZE); # 命名一個視窗，可不寫
while(True):
    # 擷取影像
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # 彩色轉灰階
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_x = abs(cv2.Sobel(frame,cv2.CV_16S,1,0))
    img_y = abs(cv2.Sobel(frame,cv2.CV_16S,0,1))
    img_x = cv2.convertScaleAbs(img_x)
    img_y = cv2.convertScaleAbs(img_y)
    img_e = cv2.addWeighted(img_x,0.5,img_y,0.5,0.3)
    #others


    # 顯示圖片
    cv2.imshow('live', img_e)
    #cv2.imshow('live', gray)

    # 按下 q 鍵離開迴圈
    if cv2.waitKey(1) == ord('q'):
        break

# 釋放該攝影機裝置
cap.release()
cv2.destroyAllWindows()