from tkinter import *
from PIL import Image,ImageTk
import cv2
import numpy as np
import math
import keyboard
import pyautogui
import random
import mediapipe as mp
import win32api
import statistics
len_mode = 0
len_counts = 12
depth = 200
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
w = 640
h = 360
sensitive = 10 # 靈敏度

var = [0,0]
dir = [0,0]

is_moving = False

finger_center = [0,0]
finger_center_temp = [0,0]

index_finger_press = False
previous_index_finger_var = 0
middle_finger_press = False

thumb_press = False

pyautogui.FAILSAFE = False
#===========================================================
def changemode_button():
    global len_mode
    len_switcher.set(len_mode)
def changemode_trackbar(value):
    global len_mode
    len_mode = int(value)
#===========================================================lens functions
def sobel_img(frame):
    x = abs(cv2.Sobel(frame,cv2.CV_16S,1,0))
    y = abs(cv2.Sobel(frame,cv2.CV_16S,0,1))
    x = cv2.convertScaleAbs(x)
    y = cv2.convertScaleAbs(y)
    return cv2.addWeighted(x,0.5,y,0.5,0.3)
def gray_scale(frame):
    return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2RGB)
def canny(frame):
    temp = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    temp = cv2.GaussianBlur(temp,(7,7),0)
    return cv2.Canny(temp,35,60,3)
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
            cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 50, 10)
    
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,255,0), 1, cv2.LINE_AA)
    return cdstP
#===========================================================
def lens(frame,option):
    # mapping = {
    #     0:frame,
    #     1:np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8),
    #     2:np.zeros((360,640,3),dtype=np.uint8),
    #     3:np.ones((360,640,3),dtype=np.uint8)*255,
    #     4:abs(255-frame),
    #     5:sobel_img(frame),
    #     6:line_img(frame),
    #     7:abs(255-canny(frame)),
    #     8:abs(sobel_img(frame) + 255),
    #     9:cv2.addWeighted(abs(sobel_img(frame) + 30),0.7,frame,1,0),
    #     10:(gray_scale(frame)%2)*125,
    #     11:cv2.addWeighted(np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8),0.2,abs(200-sobel_img(frame)),1,0),
    # }
    # if option not in range(0,len(mapping)):
    #     return mapping.get(1)
    # else:
    #     return mapping.get(option)
    return frame
#==========================================================================
def stablizer(landmark,finger_points):
    global pre_landmark
    pre_landmark = landmark
#==========================================================================
def debugger(landmark,finger_points):
    global pre_landmark
    names = ["wrist"
        ,"thumb_cmc","thumb_mcp","thumb_ip","thumb_tip"
        ,"index_mcp","index_pip","index_dip","index_tip"
        ,"middle_mcp","middle_pip","middle_dip","middle_tip"
        ,"ring_mcp","ring_pip","ring_dip","ring_tip"
        ,"pinky_mcp","pinky_pip","pinky_dip","pinky_tip"
        ]
    pre_landmark = landmark
    if keyboard.is_pressed('p'):
        for i in range(0,len(finger_points)):
            print(names[i],finger_points[i][0],finger_points[i][1],finger_points[i][2])
        print("")
#==========================================================================
def debug_sketch(landmark,width,height):
    finger_points = []
    fx = []
    fy = []
    fz = []
    names = ["wrist"
        ,"thumb_cmc","thumb_mcp","thumb_ip","thumb_tip"
        ,"index_mcp","index_pip","index_dip","index_tip"
        ,"middle_mcp","middle_pip","middle_dip","middle_tip"
        ,"ring_mcp","ring_pip","ring_dip","ring_tip"
        ,"pinky_mcp","pinky_pip","pinky_dip","pinky_tip"
        ]
    if landmark.multi_hand_landmarks:
        for hand_landmarks in landmark.multi_hand_landmarks:
            for i in hand_landmarks.landmark:
                x = i.x*width                       # 計算 x 座標
                y = i.y*height                      # 計算 y 座標
                z = i.z*depth                      # 計算 z 座標
                finger_points.append((int(x),int(y),-1*int(z)))
                fx.append(int(x))                   # 記錄 x 座標
                fy.append(int(y))                   # 記錄 y 座標
                fz.append(int(-1*z))                   # 記錄 z 座標
        if keyboard.is_pressed('c'):
            temp = ""
            for i,j in zip(range(0,21),names):
                if((i-1)%4 == 0): temp+="\n"
                temp+=j+"("+str(fx[i])+","+str(fy[i])+","+str(fz[i])+")\t"
            print(temp)
    return finger_points
#==========================================================================
def put_num(frame,key,val,x,y):
    cv2.putText(img=frame,text=key+str(val),org=(x,y),fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=1,color=(255,255,255),thickness=2,lineType=cv2.LINE_AA)
def put_Boolean(frame,key,value,line,color):
    cv2.putText(img=frame,text=key+": "+str(value),org=(30,30*int(line)),fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=1,color=color,thickness=2,lineType=cv2.LINE_AA)
#==========================================================================林煜宸、許家碩
def move(hand_landmarks):
    #許家碩
    finger_tips = [5]
    finger_tips.insert(0,hand_landmarks.landmark[4].x * w) #大拇指
    finger_tips.insert(1,hand_landmarks.landmark[8].x * w)
    finger_tips.insert(2,hand_landmarks.landmark[12].x * w)
    finger_tips.insert(3,hand_landmarks.landmark[16].x * w)
    finger_tips.insert(4,hand_landmarks.landmark[20].x * w) #小指
    finger_center[0] = statistics.mean(finger_tips);  #計算平均數
    #林煜宸
    finger_y = [4]
    finger_y.insert(0,hand_landmarks.landmark[0].y * h)
    finger_y.insert(1,hand_landmarks.landmark[1].y * h)
    finger_y.insert(2,hand_landmarks.landmark[13].y * h)
    finger_y.insert(3,hand_landmarks.landmark[17].y * h)
    finger_center[1] = statistics.mean(finger_y);  #計算平均數
    
    if finger_center_temp[0] == 0:
        finger_center_temp[0] = finger_center[0]
        finger_center_temp[1] = finger_center[1]
    
    var[0], var[1] = abs(finger_center[0] - finger_center_temp[0]), abs(finger_center[1] - finger_center_temp[1])
    dir[0], dir[1] = np.sign(finger_center[0] - finger_center_temp[0]), np.sign(finger_center[1] - finger_center_temp[1])*(-1)
    
    moveCursor(var,dir,pyautogui.position()[0],pyautogui.position()[1])
    finger_center_temp[0] = finger_center[0]
    finger_center_temp[1] = finger_center[1]

def moveCursor(var, direct, x, y): # call by move
    global sensitive
    global is_moving
    is_moving = TRUE
    if(var[0] > 3 or var[1] > 3):
        x += var[0] * sensitive * direct[0]
        y += var[1] * sensitive * direct[1] * 2
        win32api.SetCursorPos((round(x),round(y)))

#========================================================================== 龔品宇
def thumb_click(data,frame):
    global thumb_press
    thumb1_x=0
    thumb4_x=0
    for i in range(21):
        if i == 2  :
            thumb1_x=data.landmark[i].x*frame.shape[1]
        if i == 4:
            thumb4_x=data.landmark[i].x*frame.shape[1]
    if abs(thumb1_x-thumb4_x)<30:
        thumb_press = True
    else:
        thumb_press = False
    
    put_Boolean(frame,"thumb pressed: ",str(thumb_press),2,color=(0,255,0))
#==========================================================================吳季旻
def right_click(hand_landmarks,frame):
    global middle_finger_press
    y0 = hand_landmarks.landmark[9].y * h   # 取得中指前端 y 座標
    y1 = hand_landmarks.landmark[8].y * h   # 取得食指末端 y 座標
    y2 = hand_landmarks.landmark[12].y * h   # 取得中指末端 y 座標
    y3 = hand_landmarks.landmark[16].y * h   # 取得無名指末端 y 座標


    if middle_finger_press==False and y2>y1 and y2>y3:
        #print("right release")
        middle_finger_press=True
    elif y2<y1 and y2<y3:
        pyautogui.click(button='right')
        #print("right press")
        middle_finger_press=False
    if middle_finger_press==False:
        put_Boolean(frame,"right pressed: ","True",4,color=(255,0,255))
    else:
        put_Boolean(frame,"right pressed: ","False",4,color=(255,255,0))
#==========================================================================林昀佑
def left_click(hand_landmarks,frame):
    global index_finger_press
    global previous_index_finger_var
    index_finger_ys = [hand_landmarks.landmark[i].y*h for i in range(5,8)]
    index_finger_xs = [hand_landmarks.landmark[i].x*w for i in range(5,8)]
    
    delta = math.sqrt(math.pow(index_finger_xs[0] - index_finger_xs[2],2) + math.pow(index_finger_ys[0] - index_finger_ys[2],2))
    
    put_num(frame,"index delta:",round(previous_index_finger_var-delta),round(640-180),round(60))
    if(index_finger_press):
        put_Boolean(frame,"left pressed: ",str(index_finger_press),3,color=(255,0,255))
    else:
        put_Boolean(frame,"left pressed: ",str(index_finger_press),3,color=(255,255,0))
        
    if(abs(previous_index_finger_var-delta) > sensitive-3 and not is_moving):
        global counter
        if previous_index_finger_var-delta > 0 and index_finger_press == False:
            index_finger_press = True
            pyautogui.click(clicks=1)
            # x, y = win32api.GetCursorPos()
            # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        elif(index_finger_press == True):
            index_finger_press = False
    
    if(abs(previous_index_finger_var-delta) > sensitive-3): previous_index_finger_var = delta
    else: previous_index_finger_var = previous_index_finger_var
    
def hand_skeleton(frame,width,height):
    results = hands.process(frame)
    global is_moving
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            is_moving = FALSE
            left_click(hand_landmarks,frame)
            right_click(hand_landmarks,frame)
            thumb_click(hand_landmarks,frame)
            move(hand_landmarks)
            put_num(frame,"screen width:",w,round(640-180),round(90))
            put_num(frame,"screen height:",h,round(640-180),round(120))
            put_num(frame,check_cmaera_from(frame,hand_landmarks),0,round(80),round(360-40))
            check_cmaera_from(frame,hand_landmarks)
    return frame

def check_cmaera_from(frame,hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    middle_top = hand_landmarks.landmark[12]
    put_num(frame,"x: ",middle_top.x*w - wrist.x*w,640-180,360-80)
    put_num(frame,"y: ",middle_top.y*h - wrist.y*h,640-180,360-40)
    if middle_top.y*h - wrist.y*h > 150 :
        return "screen_right_top_camera"
    else:
        return "unknown"
#================================================================
def camera_cap():
    ret,frame = camera.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        hand_skeleton(frame,camera.get(3),camera.get(4))
        temp = lens(frame,len_mode)
        temp = Image.fromarray(temp)
        temp = ImageTk.PhotoImage(image=temp)
        panel.imgtk = temp
        panel.config(image=temp)
        root.after(1,camera_cap)
    
def get_cam_list():
    usb_port = 0
    while True:
        camera = cv2.VideoCapture(usb_port)
        if not camera.isOpened():
            break
        else:
            is_reading, img = camera.read()
            cv2.imshow(str(usb_port),img)
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(usb_port,h,w))
        usb_port +=1
        camera.release()
    return usb_port

if __name__ == '__main__':
    #==================================================================================================================ui sets
    root = Tk()
    root.title("手部滑鼠 - 期末專題")
    root.geometry("640x640")
    panel = Label(root)
    panel.pack(padx=10,pady=10)
    root.config(cursor="arrow")
    #==================================================================================================================camera sets
    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT,360)
    camera.set(cv2.CAP_PROP_FPS,60)
    #==================================================================================================================line1
    len_button = Button(text="隨機濾鏡",command=lambda:len_switcher.set(random.randint(0,len_counts)),font=('Arial',20,'bold'))
    len_button.place(x=30,y=400,width=200,height=60)
    mouse_button = Button(text="mouse",command=pyautogui.rightClick(),font=('Arial',20,'bold'))
    mouse_button.place(x=260,y=400,width=100,height=60)
    len_switcher = Scale(root, from_=0, to=len_counts,orient=HORIZONTAL,command=changemode_trackbar)
    len_switcher.place(x=420,y=400,width=200,height=60)
    #==================================================================================================================
    with mp_hands.Hands(
        # static_image_mode=True,
        min_detection_confidence=0.3,
        max_num_hands=1,
        min_tracking_confidence=0.3,
        model_complexity=0) as hands:
            camera_cap()
            root.mainloop()

    camera.release()
    cv2.destroyAllWindows()
