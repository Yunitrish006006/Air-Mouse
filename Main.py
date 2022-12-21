from tkinter import *
from PIL import Image,ImageTk
import cv2
import numpy as np
import math
import keyboard
import pydirectinput
import pyautogui

len_mode = 0
def changemode_button():
    global len_mode
    len_mode = (len_mode+1)%7
    len_switcher.set(len_mode)
def changemode_trackbar(value):
    global len_mode
    len_mode = int(value)

def lens(frame,option):
    mapping = {
        0:frame,
        1:np.empty((360,640,3),np.uint8),
        2:np.zeros((360,640,3),np.uint8),
        3:np.ones((360,640,3),np.uint8)*255,
        4:abs(255-frame),
        5:l2(frame,1),
        6:l2(frame,3),
        7:cv2.Canny(frame, 50, 200, 3),
    }
    if option not in range(0,7): return mapping.get(1)
    return mapping.get(option)

def l2(frame,img_mode):
    # 彩色轉灰階
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #edge founder
    img_x = abs(cv2.Sobel(frame,cv2.CV_16S,1,0))
    img_y = abs(cv2.Sobel(frame,cv2.CV_16S,0,1))
    img_x = cv2.convertScaleAbs(img_x)
    img_y = cv2.convertScaleAbs(img_y)
    img_e = cv2.addWeighted(img_x,0.5,img_y,0.5,0.3)
    # #canny
    image_c = cv2.Canny(img_gray, 50, 200, 3)
    image_canny = cv2.convertScaleAbs(image_c)
    # #houghLines
    dst = cv2.Canny(frame, 50, 200, None, 3)
    cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    cdstP = np.copy(cdst)
    lines = cv2.HoughLines(dst, 1, np.pi / 180, 150, None, 0, 0)
    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
            pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
            cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 50, 10)
    
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
    img_all = cv2.addWeighted(img_e,0.6,frame,0.4,0)
    img_all = cv2.addWeighted(cdstP,0.6,frame,0.3,0)
    img_all = cv2.cvtColor(img_all,cv2.COLOR_RGB2GRAY)
    # 顯示圖片
    if(img_mode == 0): img_e = frame
    elif(img_mode == 1): img_e = img_e
    elif(img_mode == 2): img_e = abs(img_e + 255)
    elif(img_mode == 3): img_e = cv2.addWeighted(abs(img_e + 30),0.7,frame,1,0)
    elif(img_mode == 4): img_e = (255-img_e)
    elif(img_mode == 5): img_e = img_all
    else: img_e = frame
    return img_e

def camera_cap():
    ret,frame = camera.read()
    if ret:
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        temp = lens(frame,len_mode)
        temp = Image.fromarray(temp)
        temp = ImageTk.PhotoImage(image=temp)
        panel.imgtk = temp
        panel.config(image=temp)
        root.after(1,camera_cap)

def call_out():
    # pydirectinput.moveRel(700, -30, duration=3)
    # pyautogui.rightClick()
    # pyautogui.leftClick()
    # pydirectinput.keyDown('ctrl')
    # pydirectinput.keyDown('alt')
    # pydirectinput.keyDown('delete')
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('alt')
    pyautogui.keyDown('delete')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('alt')
    pyautogui.keyUp('delete')

if __name__ == '__main__':
    camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT,360)
    root = Tk()
    root.title("ui")
    # root.geometry("640x480")
    panel = Label(root)
    panel.pack(padx=10,pady=10)
    root.config(cursor="arrow")
    #
    len_button = Button(text="更換濾鏡",command=changemode_button,font=('Arial',30,'bold'))
    len_button.pack(anchor="sw",fill="none")
    #
    len_button = Button(text="mouse",command=call_out,font=('Arial',30,'bold'))
    len_button.pack(anchor="n",fill="none")
    #
    len_switcher = Scale(root, from_=0, to=10,orient=HORIZONTAL,command=changemode_trackbar)
    len_switcher.pack()
    #
    camera_cap()

    root.mainloop()

    camera.release()
    cv2.destroyAllWindows()