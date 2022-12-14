import cv2
import pyautogui
import os
path = os.path.dirname(os.path.realpath(__file__))
print(path)
if __name__=='__main__':
    # 選擇第二隻攝影機
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    i = 0

    while(True):
        # 若按下 q 鍵則離開迴圈
        #
        # 若按下 c 鍵則是拍照
        if cv2.waitKey(1) & 0xFF == ord('c'):     
            ret, frame = cap.read()
            cv2.imwrite(path + "\\" + str(i) + '.jpg',frame)
            print('save:',path + "\\" + str(i) + '.jpg')
            i = i + 1
        elif cv2.waitKey(1) & 0xFF == ord('q'): break
        else:
            ret, frame = cap.read()
            cv2.imshow('frame', frame)
    # 釋放攝影機
    cap.release()

    # 關閉所有 OpenCV 視窗
    cv2.destroyAllWindows()