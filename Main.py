from tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np
import math
import keyboard
import pydirectinput
import pyautogui
import random
import mediapipe as mp
import win32api
import win32con
import statistics
from datetime import datetime
len_counts = 12
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

var = [0, 0]
dir = [0, 0]

is_moving = False
last_moving = datetime.now().timestamp()

finger_center = [0, 0]
finger_center_temp = [0, 0]

index_finger_press = False

FTH = False

FIH = False
FIS = [0,0]

FMH = False
FMS = [0,0]

HMS = 0

pyautogui.FAILSAFE = False
# =================================================================================================
def clickable():
    global last_moving
    if (datetime.now().timestamp() - last_moving < 0.5):
        return FALSE
    return TRUE
# ====================================================================================================== lens functions
def sobel_img(frame):
    x = abs(cv2.Sobel(frame, cv2.CV_16S, 1, 0))
    y = abs(cv2.Sobel(frame, cv2.CV_16S, 0, 1))
    x = cv2.convertScaleAbs(x)
    y = cv2.convertScaleAbs(y)
    return cv2.addWeighted(x, 0.5, y, 0.5, 0.3)

def gray_scale(frame):
    return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)

def canny(frame):
    temp = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    temp = cv2.GaussianBlur(temp, (7, 7), 0)
    return cv2.Canny(temp, 35, 60, 3)

def line_img(frame):
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
            cv2.line(cdst, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 50, 10)

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]),
                     (0, 255, 0), 1, cv2.LINE_AA)
    return cdstP

def lens(frame, option):
    mapping = {
        0:frame,
        1:np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8),
        2:np.zeros((360,640,3),dtype=np.uint8),
        3:np.ones((360,640,3),dtype=np.uint8)*255,
        4:abs(255-frame),
        5:sobel_img(frame),
        6:line_img(frame),
        7:abs(255-canny(frame)),
        8:abs(sobel_img(frame) + 255),
        9:cv2.addWeighted(abs(sobel_img(frame) + 30),0.7,frame,1,0),
        10:gray_scale(frame),
        11:cv2.addWeighted(sobel_img(255-frame),0.7,frame,1,0)
    }
    if option not in range(0,len(mapping)):
        return mapping.get(1)
    else:
        return mapping.get(option)
# ====================================================================================================== opencv image editor
def put_num(frame, key, val, x, y ,color):
    cv2.putText(img=frame, text=key+str(val), org=(x, y), fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=1, color=color, thickness=2, lineType=cv2.LINE_AA)
def put_Boolean(frame, key, value, line, color):
    cv2.putText(img=frame, text=key+": "+str(value), org=(30, 30*int(line)),fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=color, thickness=2, lineType=cv2.LINE_AA)
# ====================================================================================================== 林煜宸、許家碩
def move(hand_landmarks):
    # 許家碩
    finger_tips = [hand_landmarks.landmark[i].x * camera_width for i in [4,8,12,16,20]]# 大拇指 ~ 小指
    finger_center[0] = statistics.mean(finger_tips)  # 計算平均數
    # 林煜宸
    finger_y = [hand_landmarks.landmark[i].y * camera_height for i in [0,1,13,17]]
    finger_center[1] = statistics.mean(finger_y)  # 計算平均數

    if finger_center_temp[0] == 0:
        finger_center_temp[0] = finger_center[0]
        finger_center_temp[1] = finger_center[1]

    var[0], var[1] = abs(finger_center[0] - finger_center_temp[0]
                         ), abs(finger_center[1] - finger_center_temp[1])
    dir[0], dir[1] = np.sign(finger_center[0] - finger_center_temp[0]
                             ), np.sign(finger_center[1] - finger_center_temp[1])*(-1)

    moveCursor(var, dir, pyautogui.position()[0], pyautogui.position()[1])
    finger_center_temp[0] = finger_center[0]
    finger_center_temp[1] = finger_center[1]

def moveCursor(var, direct, x, y):  # call by move
    global last_moving
    if(var[0] > 2 or var[1] > 2):
        x += var[0] * mouse_move.get() * direct[0] * 2
        y += var[1] * mouse_move.get() * direct[1] * 2
        win32api.SetCursorPos((round(x), round(y)))
    if(var[0] > mouse_move.get() or var[1] > mouse_move.get()):
        last_moving = datetime.now().timestamp()
# ====================================================================================================== 龔品宇
def thumb_click(data):
    global FTH
    thumb1_x = data.landmark[1].x * camera_height
    thumb4_x = data.landmark[4].x * camera_height
    FTH = abs(thumb1_x-thumb4_x) < 20
    if FTH: win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    else: win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

# ====================================================================================================== 吳季旻
# middle_finger_press = False
# def right_click_old(hand_landmarks, frame):
#     global middle_finger_press
#     # 中指前端 食指末端 食指末端 無名指末端
#     pos_ys = [hand_landmarks.landmark[i].y *camera_height for i in [9,8,12,16]]

#     if middle_finger_press == False and pos_ys[2] > pos_ys[1] and pos_ys[2] > pos_ys[3]:
#         middle_finger_press = True
#     elif pos_ys[2] < pos_ys[3] and pos_ys[2] < pos_ys[3]:
#         # cx,cy = win32api.GetCursorPos()
#         # win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
#         # pyautogui.click(button='right')
#         middle_finger_press = False
#     put_Boolean(frame, "right pressed: ", "True", 4, color=(255, 255*int(middle_finger_press), 255*int(not middle_finger_press)))
# ====================================================================================================== 林昀佑
def to_mid(hand_landmarks):
    hand_root = hand_landmarks.landmark[0].y
    finger_top = [hand_landmarks.landmark[i].y * camera_width for i in [8,12,16,20]]
    finger_root = [hand_landmarks.landmark[i].y * camera_height for i in [5,9,13,17]]
    deltas = [abs(finger_top[i] - finger_root[i]) - abs(finger_root[i] - hand_root) for i in [0,1,2,3]]
    delta = statistics.mean(deltas)
    global HMS
    if(abs(HMS-(HMS*0.6+delta*0.4)))>2: HMS = (HMS*0.6+delta*0.4)
    if(HMS<50): win32api.SetCursorPos((int(window_width/2),int(window_height/2)))
            
def right_click(hand_landmarks):
    global index_finger_press
    finger_xs = [hand_landmarks.landmark[i].x * camera_width for i in [10,11,12]]
    finger_ys = [hand_landmarks.landmark[i].y * camera_height for i in [10,11,12]]
    def dis(x1,y1,x2,y2): return math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2,2))
    
    # Heron's formula
    a = dis(finger_xs[0],finger_ys[0],finger_xs[1],finger_ys[1])
    b = dis(finger_xs[1],finger_ys[1],finger_xs[2],finger_ys[2])
    c = dis(finger_xs[0],finger_ys[0],finger_xs[2],finger_ys[2])
    s = (a+b+c)/2
    alpha = math.sqrt(s*(s-a)*(s-b)*(s-c))
    beta = abs(finger_ys[0]-finger_ys[1]) + abs(finger_ys[1]-finger_ys[2])
    
    global FMS,FMH
    if(abs(FMS[0]-(FMS[0]*0.6+alpha*0.4)))>2: FMS[0] = (FMS[0]*0.6+alpha*0.4)
    if(abs(FMS[1]-(FMS[1]*0.6+beta*0.4)))>2: FMS[1] = (FMS[1]*0.6+beta*0.4)
    
    if(50-int(R_sensitive.get()) < 5 ):
        temp = datetime.now().timestamp() - last_moving < hold_time.get()/10
    else: temp = True
    
    if not gaming_mode.get():
        if(temp and FMH == False and FMS[1] < int(R_sensitive.get())):
            FMH = True
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
        elif(temp and FMH == True and FMS[1] >= int(R_sensitive.get())):
            FMH = False
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
      
def left_click(hand_landmarks):
    global index_finger_press
    finger_xs = [hand_landmarks.landmark[i].x * camera_width for i in [6,7,8]]
    finger_ys = [hand_landmarks.landmark[i].y * camera_height for i in [6,7,8]]
    def dis(x1,y1,x2,y2): return math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2,2))
    
    # Heron's formula
    a = dis(finger_xs[0],finger_ys[0],finger_xs[1],finger_ys[1])
    b = dis(finger_xs[1],finger_ys[1],finger_xs[2],finger_ys[2])
    c = dis(finger_xs[0],finger_ys[0],finger_xs[2],finger_ys[2])
    s = (a+b+c)/2
    alpha = math.sqrt(s*(s-a)*(s-b)*(s-c))
    beta = abs(finger_ys[0]-finger_ys[1]) + abs(finger_ys[1]-finger_ys[2])
    
    global FIS,FIH
    if(abs(FIS[0]-(FIS[0]*0.6+alpha*0.4)))>2: FIS[0] = (FIS[0]*0.6+alpha*0.4)
    if(abs(FIS[1]-(FIS[1]*0.6+beta*0.4)))>2: FIS[1] = (FIS[1]*0.6+beta*0.4)
    
    if(50-int(L_sensitive.get()) < 5 ):
        temp = datetime.now().timestamp() - last_moving < hold_time.get()/10
    else: temp = True
    if not gaming_mode.get():
        if(temp and FIH == False and FIS[1] < int(L_sensitive.get())):
            FIH = True
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
                
        elif(temp and FIH == True and FIS[1] >= int(L_sensitive.get())):
            FIH = False
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    else:
        if temp and FIS[1] < int(L_sensitive.get()):
            FIH = True
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
        # elif temp and FIS[1] >= int(L_sensitive.get()):
        else:
        #     FIH = False
        #     win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
# ====================================================================================================== 
def hand_skeleton(frame):
    results = hands.process(frame)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            to_mid(hand_landmarks)
            global FIH,FMH
            if(HMS>50):
                FIH = False
                FMH = False
                left_click(hand_landmarks)
                right_click(hand_landmarks)
                thumb_click(hand_landmarks)
                move(hand_landmarks)
            if data_display.get():
                check_cmaera_from(frame, hand_landmarks)
    return frame

def check_cmaera_from(frame, hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    middle_top = hand_landmarks.landmark[9]
    distance = middle_top.y*camera_height - wrist.y*camera_height
    put_num(frame,"distance: ",distance,40,360-20,(255,0,0))
    if 100 > distance and distance > 30:
        put_num(frame,"screen_right_top_camera",0, round(80), round(360-40),(255,0,0))
    else:
        put_num(frame,"unknown",0, round(80), round(360-40),(255,0,0))

def camera_cap():
    ret, frame = camera.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if len_on.get(): temp = lens(frame, len_mode.get())
        else: temp = frame
        if air_mouse_on.get():hand_skeleton(frame)
        if data_display.get():
                put_num(frame,"HMS: ",int(HMS),640-180,360-120,(255*int(HMS<50),125,125))
                put_Boolean(frame, "S: ", str(FTH), 2, color=(0, 255, 0))
                
                put_num(frame, "FMS: "+str(round(FMS[0]))+" , ",round(FMS[1]), 640-140, 20,(255,0,0))
                put_Boolean(frame, "["+str(int(R_sensitive.get()))+"] R: ", str(FMH), 4, color=(255, 255*int(FMH), 255*int(not FMH)))
                
                put_num(frame, "FIS: "+str(round(FIS[0]))+" , ", round(FIS[1]), 640-260, 20,(255,0,0))
                put_Boolean(frame, "["+str(int(L_sensitive.get()))+"] L: ", str(FIH), 3, color=(255, 255*int(FIH), 255*int(not FIH)))
                
                put_num(frame,"camera: "+str(int(camera_width))+" x ",int(camera_height),30,20,(255,0,0))

        temp = Image.fromarray(temp)
        temp = ImageTk.PhotoImage(image=temp)
        panel.imgtk = temp
        panel.config(image=temp)
        root.after(1, camera_cap)

def get_cam_list():
    usb_port = 0
    while True:
        camera = cv2.VideoCapture(usb_port)
        if not camera.isOpened():
            break
        else:
            is_reading, img = camera.read()
            cv2.imshow(str(usb_port), img)
            camera_width = camera.get(3)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %
                      (usb_port, camera_height, camera_width))
        usb_port += 1
        camera.release()
    return usb_port

# ======================================================================================================
if __name__ == '__main__':
# ====================================================================================================== ui sets
    root = Tk()
    root.title("手部滑鼠 - 期末專題")
    root.geometry("640x640")
    panel = Label(root)
    panel.pack(padx=10, pady=10)
    root.config(cursor="arrow")
    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()
# ======================================================================================================camera sets
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    camera.set(cv2.CAP_PROP_FPS, 60)
    camera_width = camera.get(3)
    camera_height = camera.get(4)
# ====================================================================================================== ui contents
    len_button = Button(root,text="隨機濾鏡", command=lambda: len_mode.set(random.randint(0, len_counts)), font=('Arial', 16, 'bold'))
    len_button.place(x=30, y=400, width=160, height=60)
    
    def on_mouse_on():
        global FIH
        FIH = False
    
    air_mouse_on = BooleanVar()
    air_mouse_switch = Checkbutton(root,text="開啟滑鼠", font=('Arial', 16, 'bold'),variable = air_mouse_on, onvalue = True, offvalue = False, command= lambda: on_mouse_on())
    air_mouse_switch.deselect()
    air_mouse_switch.place(x=200, y=380, width=160, height=60)
    
    len_on = BooleanVar()
    len_switch = Checkbutton(root,text="開啟濾鏡", font=('Arial', 16, 'bold'),variable = len_on, onvalue = True, offvalue = False)
    len_switch.deselect()
    len_switch.place(x=200, y=420, width=160, height=60)
    
    data_display = BooleanVar()
    data_display_switch = Checkbutton(root,text="開啟除錯", font=('Arial', 16, 'bold'),variable = data_display, onvalue = True, offvalue = False)
    data_display_switch.select()
    data_display_switch.place(x=200, y=460, width=160, height=60)
    
    keeptop = BooleanVar()
    keeptop_switch = Checkbutton(root,text="視窗置頂", font=('Arial', 16, 'bold'),variable = keeptop, onvalue = True, offvalue = False,command=lambda:root.attributes('-topmost',keeptop.get()))
    keeptop_switch.select()
    keeptop_switch.place(x=200, y=500, width=160, height=60)
    
    #額外新增功能
    gaming_mode = BooleanVar()
    gaming_switch = Checkbutton(root,text="遊戲模式", font=('Arial', 16, 'bold'),variable = gaming_mode, onvalue = True, offvalue = False)
    gaming_switch.deselect()
    gaming_switch.place(x=200, y=540, width=160, height=60)
    
    len_mode = Scale(root, from_=0, to=len_counts,orient=HORIZONTAL,label="濾鏡編號")
    len_mode.set(0)
    len_mode.place(x=30, y=490, width=160, height=60)
    
    mouse_move_label = Label(root,text="move")
    mouse_move_label.place(x=360, y=390, width=60, height=40)
    mouse_move = Scale(root, from_=1, to=10,orient=HORIZONTAL)
    mouse_move.set(4)
    mouse_move.place(x=420, y=380, width=200, height=40)
    
    mouse_click_label = Label(root,text="click")
    mouse_click_label.place(x=360, y=430, width=60, height=40)
    mouse_click = Scale(root, from_=1, to=10,orient=HORIZONTAL)
    mouse_click.set(4)
    mouse_click.place(x=420, y=420, width=200, height=40)
    
    L_sensitive_label = Label(root,text="L sensitive")
    L_sensitive_label.place(x=360, y=480, width=60, height=40)
    L_sensitive = Scale(root, from_=1, to=50,orient=HORIZONTAL)
    L_sensitive.set(26)
    L_sensitive.place(x=420, y=470, width=200, height=40)
    
    R_sensitive_label = Label(root,text="R sensitive")
    R_sensitive_label.place(x=360, y=530, width=60, height=40)
    R_sensitive = Scale(root, from_=1, to=50,orient=HORIZONTAL)
    R_sensitive.set(26)
    R_sensitive.place(x=420, y=520, width=200, height=40)
    
    hold_time_label = Label(root,text="hold time")
    hold_time_label.place(x=360, y=580, width=60, height=40)
    hold_time = Scale(root, from_=1, to=25,orient=HORIZONTAL)
    hold_time.set(10)
    hold_time.place(x=420, y=570, width=200, height=40)
# ======================================================================================================
    with mp_hands.Hands(
        min_detection_confidence=0.3,
        max_num_hands=1,
        min_tracking_confidence=0.3,
        model_complexity=0
        ) as hands:
        camera_cap()
        root.bind('<Control-m>', lambda e: air_mouse_switch.toggle())
        root.bind('<Control-l>', lambda e: len_switch.toggle())
        root.mainloop()
        
    camera.release()
    cv2.destroyAllWindows()