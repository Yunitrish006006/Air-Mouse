from win32gui import FindWindow, GetWindowRect
from PIL import ImageGrab
import numpy as np
import cv2
image = ImageGrab.grab()
width, height = image.size

fourcc = cv2.VideoWriter_fourcc(*'XVID')
video = cv2.VideoWriter('test.avi', fourcc, 25, (width, height))

import pyautogui

while True:
    # img_rgb = ImageGrab.grab()
    img_rgb = ImageGrab.grab()
    mtitle = ""
    for x in pyautogui.getAllWindows(): 
        if(x.title!="" and (x.title)[0:9] == "Minecraft"):mtitle = x.title
    x1,y1,x2,y2 = GetWindowRect(FindWindow(None,mtitle))

    img_rgb = ImageGrab.grab(bbox=(x1,y1,x2,y2))
    img_bgr = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(np.array(img_rgb),cv2.COLOR_RGB2GRAY)
    
    img_x = abs(cv2.Sobel(img_bgr,cv2.CV_16S,1,0))
    img_x = cv2.convertScaleAbs(img_x)

    img_y = abs(cv2.Sobel(img_bgr,cv2.CV_16S,0,1))
    img_y = cv2.convertScaleAbs(img_y)
    
    img_e = cv2.addWeighted(img_x,1,img_y,1,0)

    video.write(img_bgr)
    cv2.imshow('live', img_e)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

video.release()
cv2.destroyAllWindows()