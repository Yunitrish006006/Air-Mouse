import cv2
import pyautogui
if __name__=='__main__':
    # 選擇第二隻攝影機
    cap = cv2.VideoCapture(1)
    i = 0
    save_path = 'datas/test/'      # 儲存路徑(可自行修改)
    file_name = 'test'  

    while(True):
    # 從攝影機擷取一張影像
        ret, frame = cap.read()

        # 顯示圖片
        cv2.imshow('frame', frame)

        # 若按下 q 鍵則離開迴圈
        if cv2.waitKey(1) & 0xFF == ord('q'): break
        # 若按下 c 鍵則是拍照
        if pyautogui.hotkey('c'): 
            cv2.imwrite(save_path + file_name + '_' + str(i) + '.jpg',frame)
            print('save:',file_name + '_' + str(i) + '.jpg')
            i = i + 1
    # 釋放攝影機
    cap.release()

    # 關閉所有 OpenCV 視窗
    cv2.destroyAllWindows()