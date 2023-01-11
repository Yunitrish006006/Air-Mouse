import array
from cmath import sqrt
from faulthandler import disable
import cv2
import numpy as np
import math
import tkinter
import customtkinter as ctk
import os
import pyautogui
from PIL import Image
import win32api
import win32con
from typing import *
from datetime import datetime
import win32com.client
pyautogui.FAILSAFE = False
#===============================================mediapipe settings=========================================
import mediapipe as mp
import statistics
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
HMS = [0,0]
#===============================================class title================================================
class Filter():
    layers = ["origin","grayscale","sobel","revert","de","enhance","blur","lines","noise","black","white"]
    def put_text(self,frame:np.dtype,text:str,x:int,y:int,color):
        cv2.putText(img=frame, text=text,org=(x,y), fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=1, color=color, thickness=2, lineType=cv2.LINE_AA)
    def linearization(self,frame:np.dtype):
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
    def grayscalize(self,frame:np.dtype):
        return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)
    def sobelize(self,frame:np.dtype):
        x = abs(cv2.Sobel(frame, cv2.CV_16S, 1, 0))
        y = abs(cv2.Sobel(frame, cv2.CV_16S, 0, 1))
        x = cv2.convertScaleAbs(x)
        y = cv2.convertScaleAbs(y)
        frame = cv2.addWeighted(x, 0.5, y, 0.5, 0.3)
        return frame
    def enhancialize(self,frame:np.dtype):
        kernal = np.ones((3,3),np.uint8)
        frame = abs(255-frame)
        for i in range(0,3):
            frame = cv2.dilate(frame,kernal,iterations=2)
            frame = cv2.erode(frame,kernal,iterations=2)
        return frame
    def DE(self,frame:np.dtype):
        kernal = np.array([[0,1,1,1,0],[1,1,0,1,1],[1,0,0,0,1],[1,1,0,1,1],[0,1,1,1,0]],dtype=np.uint8)
        for _ in range(0,3):
            frame = cv2.dilate(frame,kernal,iterations=3)
            frame = cv2.erode(frame,kernal,iterations=3)
        return frame
    def progress_filter(self,frame:np.dtype,operation:str):
        operations:list[str] = operation.split("_")
        error_message ="layer not exist:"
        for op in operations:
            if op in self.layers:
                if op == "origin":pass
                elif op == "grayscale":frame = self.grayscalize(self,frame)
                elif op == "sobel":frame = self.sobelize(self,frame)
                elif op == "revert":frame = abs(255-frame)
                elif op == "de":frame = self.DE(self,frame)
                elif op == "enhance":frame = self.enhancialize(self,frame)
                elif op == "blur":frame = cv2.addWeighted(abs(self.sobelize(self,frame) + 30),0.7,frame,1,0)
                elif op == "lines":frame = self.linearization(self,frame)
                elif op == "noise":frame = np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8)
                elif op == "black":frame = np.zeros((360,640,3),dtype=np.uint8)
                elif op == "white":frame = np.ones((360,640,3),dtype=np.uint8)*255
            else:
                error_message += " "+op
        if len(error_message.split(":"))<2:
            self.put_text(self,frame,error_message,10,10,(255,0,0))
        return frame
class AirMouseGUI(ctk.CTk):
    mode:str = "camera"
    stream:np.dtype = np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8)
    def window_toogle(self, name) -> None:
        self.normal_mode_button.configure(fg_color=("gray75", "gray25") if name == "normal" else "transparent")
        self.game_mode_button.configure(fg_color=("gray75", "gray25") if name == "game" else "transparent")
        self.camera_mode_button.configure(fg_color=("gray75", "gray25") if name == "camera" else "transparent")
        self.normal_window.grid_forget()
        self.game_window.grid_forget()
        self.camera_window.grid_forget()
        if name == "normal":
            self.normal_window.grid(row=0, column=1, sticky="nsew")
            self.mode = "normal"
        elif name == "game":
            self.game_window.grid(row=0, column=1, sticky="nsew")
            self.mode = "game"
        elif name == "camera":
            self.camera_window.grid(row=0, column=1, sticky="nsew")
            self.mode = "camera"
    stablizor:List[int]=[]
    stamp:List[float]=[]
    gap:List[int]=[]
    lst:List[str]=[]
    def get_timegap(time:float=datetime.now().timestamp()) -> float:
        return datetime.now().timestamp()-time
    def getAction1(self,data,id:int=len(gap)):
        if(self.get_timegap(self.stamp[id])>self.gap[id]):
            data = data #do something
            win32api.SetCursorPos((round(960), round(540)))
            self.gap[id] = self.get_timegap(self.stamp[id])
    def change_appearance_mode_event(self, new_appearance_mode) -> None:
        ctk.set_appearance_mode(new_appearance_mode)
    FilterMode:str="origin"
    handPosition:List[int]=[30,30]
    #===========================================debug=================================================
    def put_text(self,frame,val:str,x,y,color):
        cv2.putText(img=frame, text=val,org=(x,y), fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=1, color=color, thickness=2, lineType=cv2.LINE_AA)
    
    def __init__(self) -> None:
        super().__init__()
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src\\image")
        self.iconbitmap(os.path.join(image_path, "rat.ico"))
        self.title("   Air Mouse")
        self.geometry("960x640")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # 載入影像     
        def getIcon(name,width,height) -> ctk.CTkImage:
            return ctk.CTkImage(
                light_image=Image.open(os.path.join(image_path, name)),
                dark_image=Image.open(os.path.join(image_path, name)),
                size=(width, height))
        def getNavItems(name,icon) -> ctk.CTkButton:
            return ctk.CTkButton(
                self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text=name,
                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                image=getIcon(icon,32,32), anchor="w", command=lambda:self.window_toogle(name))
        
        def getDeviceList() -> List[str]:
            deviceList:List[str]=["default camera"]
            wmi = win32com.client.GetObject ("winmgmts:")
            for usb in wmi.InstancesOf ("Win32_USBHub"):
                deviceList.append(str(usb.DeviceID))
            return deviceList
        # 側邊攔
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="   Air Mouse", image=getIcon("rat.png",26,26),compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.normal_mode_button = getNavItems("normal","pc.png")
        self.normal_mode_button.grid(row=1, column=0, sticky="ew")

        self.game_mode_button = getNavItems("game","nv.png")
        self.game_mode_button.grid(row=2, column=0, sticky="ew")
        
        self.camera_mode_button = getNavItems("camera","camera.png")
        self.camera_mode_button.grid(row=3, column=0, sticky="ew")
        
        self.always_ontop = ctk.StringVar(value="off")
        topping_switch = ctk.CTkSwitch(self.navigation_frame,text="視窗置頂",variable=self.always_ontop,onvalue="on",offvalue="off",command=lambda:self.wm_attributes('-topmost',self.always_ontop.get()=="on"))
        topping_switch.grid(row=4, column=0, pady=10,sticky="s")
        topping_switch.deselect()
        
        self.mouse_state = ctk.StringVar(value="off")
        mouse = ctk.CTkSwitch(self.navigation_frame,text="滑鼠功能",variable=self.mouse_state,onvalue="on",offvalue="off")
        mouse.grid(row=5, column=0, pady=10,sticky="s")
        mouse.deselect()
        
        self.debug_switch_state = ctk.StringVar(value="off")
        debug_switch = ctk.CTkSwitch(self.navigation_frame,text="除錯功能",variable=self.debug_switch_state,onvalue="on",offvalue="off")
        debug_switch.grid(row=6, column=0, pady=10,sticky="s")
        debug_switch.deselect()
        
        option = ["origin","grayscale","revert_de","de","enhance","enhance_grayscale","sobel","sobel_grayscale","revert_sobel","blur","lines","noise","black","white","revert"]
        def filterChange(choice) -> None: self.FilterMode = choice
        self.cam_list = ctk.CTkComboBox(self.navigation_frame,values=option,command=filterChange)
        self.cam_list.grid(row=7, column=0, pady=10,sticky="s")
        
        self.cam_list = ctk.CTkComboBox(self.navigation_frame,values=getDeviceList(),command=lambda x:print("you have selected " + str(x) +" as camera"))
        self.cam_list.grid(row=8, column=0, pady=10,sticky="s")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["System","Light", "Dark"],command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=9, column=0, padx=20, pady=10, sticky="s")
        
        # mutual components
        self.camera_frame = ctk.CTkImage(dark_image=Image.fromarray(self.stream),size=(640,360))
        #normal mode
        self.normal_window = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.normal_window.grid_columnconfigure(5, weight=1)
        self.normal_cam = ctk.CTkLabel(self.normal_window,text="",image=self.camera_frame)
        self.normal_cam.grid(row=0, column=0, columnspan=5, padx=20, pady=10)
        
        self.n_mouseX_Label = ctk.CTkLabel(self.normal_window,text="X sensitive: ")
        self.n_mouseX_Label.grid(row=3, column=0, padx=20, pady=10)
        self.n_mouseX_sensitive = ctk.CTkSlider(self.normal_window, from_=0, to=8, number_of_steps=100)
        self.n_mouseX_sensitive.grid(row=3, column=1, columnspan=4, padx=(20, 10), pady=(10, 10), sticky="ew")
        
        self.n_mouseY_Label = ctk.CTkLabel(self.normal_window,text="Y sensitive: ")
        self.n_mouseY_Label.grid(row=4, column=0, padx=20, pady=10)
        self.n_mouseY_sensitive = ctk.CTkSlider(self.normal_window, from_=0, to=8, number_of_steps=100)
        self.n_mouseY_sensitive.grid(row=4, column=1, columnspan=4, padx=(20, 10), pady=(10, 10), sticky="ew")

        #game mode
        self.game_window = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.game_window.grid_columnconfigure(5, weight=1)
        self.game_camera = ctk.CTkLabel(self.game_window,text="",image=self.camera_frame)
        self.game_camera.grid(row=0, column=0, columnspan=5, padx=20, pady=10)
        
        self.g_mouseX_Label = ctk.CTkLabel(self.game_window,text="X sensitive: ")
        self.g_mouseX_Label.grid(row=1, column=0, padx=20, pady=10)
        self.g_mouseX_sensitive = ctk.CTkSlider(self.game_window, from_=0, to=8, number_of_steps=100)
        self.g_mouseX_sensitive.grid(row=1, column=1, columnspan=4, padx=(20, 10), pady=(10, 10), sticky="ew")
        
        self.g_mouseY_Label = ctk.CTkLabel(self.game_window,text="Y sensitive: ")
        self.g_mouseY_Label.grid(row=2, column=0, padx=20, pady=10)
        self.g_mouseY_sensitive = ctk.CTkSlider(self.game_window, from_=0, to=8, number_of_steps=100)
        self.g_mouseY_sensitive.grid(row=2, column=1, columnspan=4, padx=(20, 10), pady=(10, 10), sticky="ew")
        
        self.g_mouseR_Label = ctk.CTkLabel(self.game_window,text="R sensitive: ")
        self.g_mouseR_Label.grid(row=3, column=0, padx=20, pady=10)
        self.g_mouseR_sensitive = ctk.CTkSlider(self.game_window, from_=0, to=2, number_of_steps=100)
        self.g_mouseR_sensitive.grid(row=3, column=1, columnspan=4, padx=(20, 10), pady=(10, 10), sticky="ew")
        
        self.g_mouseL_Label = ctk.CTkLabel(self.game_window,text="L sensitive: ")
        self.g_mouseL_Label.grid(row=4, column=0, padx=20, pady=10)
        self.g_mouseL_sensitive = ctk.CTkSlider(self.game_window, from_=0, to=2, number_of_steps=100)
        self.g_mouseL_sensitive.grid(row=4, column=1, columnspan=4, padx=(20, 10), pady=(10, 10), sticky="ew")
        
        #camera mode
        self.camera_window = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.camera_window.grid_columnconfigure(0, weight=1)
        camera_camera = ctk.CTkLabel(self.camera_window,text="",image=self.camera_frame)
        camera_camera.grid(row=0, column=0, padx=20, pady=10)
        cheese_button = ctk.CTkButton(self.camera_window, text="snap shot #0", compound="left",command=lambda:[
            cv2.imwrite("Test/"+cheese_button._text+".png",self.stream),
            cheese_button.configure(text=cheese_button._text.split("#")[0]+"#"+str(int(cheese_button._text.split("#")[1])+1))
        ])
        cheese_button.grid(row=2, column=0, padx=20, pady=10)
#============================================controlor (developing....)===================================
class Controlor():
    finger_len_average = 0
    palm_average = 0
    def caculate(self,data):
        hand_root = data.landmark[0].y
        self.finger_len_average = statistics.mean([(data.landmark[i].y - data.landmark[i-3].y) * camera_width for i in [8,12,16,20]])
        self.palm_average = ((abs(data.landmark[5].y - hand_root) + abs(data.landmark[17].y - hand_root))/2)*camera_width
    
    def do_center(self):
        return self.finger_len_average+self.palm_average>100 and abs(self.finger_len_average)<40
    
    def loopor(self,video:np.dtype,app:AirMouseGUI):
        results = hands.process(video)
        thresholds=[]
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                thresholds.append(to_mid(hand_landmarks))
                thresholds.append(self.do_center(hand_landmarks))
                move(hand_landmarks,int(app.g_mouseX_sensitive.get()),int(app.g_mouseY_sensitive.get()))
        return thresholds
    
def move(hand_landmarks,x_sensitive,y_sensitive):
    finger_tips = [hand_landmarks.landmark[i].x * camera_width for i in [0,5,9,13,17]]
    finger_center[0] = statistics.mean(finger_tips)
    finger_y = [hand_landmarks.landmark[i].y * camera_height for i in [0,1,13,17]]
    finger_center[1] = statistics.mean(finger_y)
    if finger_center_temp[0] == 0:
        finger_center_temp[0] = finger_center[0]
        finger_center_temp[1] = finger_center[1]
    var[0], var[1] = abs(finger_center[0] - finger_center_temp[0]), abs(finger_center[1] - finger_center_temp[1])
    dir[0], dir[1] = np.sign(finger_center[0] - finger_center_temp[0]), np.sign(finger_center[1] - finger_center_temp[1])*(-1)
    moveCursor(var, dir, pyautogui.position()[0], pyautogui.position()[1],x_sensitive,y_sensitive)
    finger_center_temp[0] = finger_center[0]
    finger_center_temp[1] = finger_center[1]

def moveCursor(var, direct, x, y,x_sensitive,y_sensitive):  # call by move
    global last_moving
    if(var[0] > 2 or var[1] > 2):
        x += var[0] * x_sensitive * direct[0] * 2
        y += var[1] * y_sensitive * direct[1] * 2 * -1
        win32api.SetCursorPos((round(x), round(y)))
    if(var[0] > y_sensitive or var[1] > y_sensitive):
        last_moving = datetime.now().timestamp()
# ====================================================================================================== 龔品宇
def thumb_click(data):
    global FTH
    thumb1_x = data.landmark[1].x * camera_height
    thumb4_x = data.landmark[4].x * camera_height
    FTH = abs(thumb1_x-thumb4_x) < 20
    if FTH: win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    else: win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def to_mid(hand_landmarks):
    hand_root = hand_landmarks.landmark[0].y
    deltas = [(hand_landmarks.landmark[i].y - hand_landmarks.landmark[i-3].y) * camera_width for i in [8,12,16,20]]
    delta = statistics.mean(deltas)
    beta = ((abs(hand_landmarks.landmark[5].y - hand_root) + abs(hand_landmarks.landmark[17].y - hand_root))/2)*camera_width
    global HMS
    if(abs(HMS[0]-(HMS[0]*0.6+delta*0.4)))>2: HMS[0] = (HMS[0]*0.6+delta*0.4)
    if(abs(HMS[1]-(HMS[1]*0.6+(delta+beta)*0.4)))>2: HMS[1] = (HMS[1]*0.6+(delta+beta)*0.4)
    if HMS[1]>100 and abs(HMS[0])<40:win32api.SetCursorPos((int(window_width/2),int(window_height/2)))
    # if(HMS[0]<40): win32api.SetCursorPos((int(window_width/2),int(window_height/2)))
    return HMS
            
def right_click(hand_landmarks,rs,app:AirMouseGUI):
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
    
    if(50-int(rs) < 5 ):
        temp = datetime.now().timestamp() - last_moving < 10/10
    else: temp = True
    
    if not app.mode=="game":
        if(temp and FMH == False and FMS[1] < int(rs)):
            FMH = True
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
        elif(temp and FMH == True and FMS[1] >= int(rs)):
            FMH = False
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)

def get_D(hand_landmarks,a:int,b:int):
    try:
        ax = hand_landmarks.landmark[a].x
        ay = hand_landmarks.landmark[a].y
        bx = hand_landmarks.landmark[b].x
        by = hand_landmarks.landmark[b].y
        return int(sqrt(pow((ax*camera_width-bx*camera_width),2)+pow((ay*camera_height-by*camera_height),2)))
    except:
        return -99

def left_click(hand_landmarks,ls,app:AirMouseGUI):
    
    alpha = get_D(hand_landmarks,8,12)
    beta = ((get_D(hand_landmarks,8,6)+get_D(hand_landmarks,12,10)) - (get_D(hand_landmarks,16,14)+get_D(hand_landmarks,20,18))) 
    
    global FIS,FIH
    if(abs(FIS[0]-(FIS[0]*0.6+alpha*0.4)))>2: FIS[0] = (FIS[0]*0.6+alpha*0.4)
    if(abs(FIS[1]-(FIS[1]*0.6+beta*0.4)))>2: FIS[1] = (FIS[1]*0.6+beta*0.4)
    
    print(FIS)
    
    if(50-int(ls) < 5 ):
        temp = datetime.now().timestamp() - last_moving < 10/10
    else: temp = True
    if(temp and FIH == False and FIS[0] < 45):
        FIH = True
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
            
    elif(temp and FIH == True and FIS[1] >= 45):
        FIH = False
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def hand_skeleton(frame):
    results = hands.process(frame)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            to_mid(hand_landmarks)
            global FIH,FMH
            if(HMS>50):
                FIH = False
                FMH = False
                # left_click(hand_landmarks)
                # right_click(hand_landmarks)
                # thumb_click(hand_landmarks)
            move(hand_landmarks,int(app.g_mouseX_sensitive.get()),int(app.g_mouseY_sensitive.get()))
            print(hand_landmarks)
    return frame

def control_hub(video:np.dtype,app:AirMouseGUI):
    results = hands.process(video)
    thresholds=[]
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thresholds.append(to_mid(hand_landmarks))
            global FIH,FMH
            if(abs(HMS[0])>50):
                FIH = False
                FMH = False
                left_click(hand_landmarks,int(app.g_mouseL_sensitive.get()),app)
                right_click(hand_landmarks,int(app.g_mouseR_sensitive.get()),app)
                move(hand_landmarks,int(app.g_mouseX_sensitive.get()),int(app.g_mouseY_sensitive.get()))
    return thresholds

def show_debug(data:np.dtype):
    processed_data = hands.process(data)
    if not processed_data.multi_hand_landmarks: return data
    for hand_points in processed_data.multi_hand_landmarks:
        mp_drawing.draw_landmarks(data, hand_points, mp_hands.HAND_CONNECTIONS)
    return data

if __name__ == "__main__":
#==================================================================================
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    camera.set(cv2.CAP_PROP_FPS, 60)
    camera_width = camera.get(3)
    camera_height = camera.get(4)
    app = AirMouseGUI()
    controlor = Controlor()
    app.window_toogle("normal")
    # app.debug_switch_state.set("on")
    # app.mouse_state.set("on")
    # app.always_ontop.set("on")
    window_width = app.winfo_screenwidth()
    window_height = app.winfo_screenheight()
#==================================================================================
    with mp_hands.Hands(
        min_detection_confidence=0.3,
        max_num_hands=1,
        min_tracking_confidence=0.3,
        model_complexity=0
        ) as hands:
            def task() -> None:
                ret , video = camera.read()
                if ret:
                    # video = cv2.flip(video, 1)
                    video = cv2.cvtColor(video, cv2.COLOR_BGR2RGB)
                    # video = cv2.flip(video,0)
                app_title = " Air Mouse "
                app.stream = Filter.progress_filter(Filter,video,app.FilterMode)
                threshholds = []
                if app.mouse_state.get() == "on":
                    app_title += "🔓"
                    threshholds = control_hub(app.stream,app)
                elif app.mouse_state.get() == "off":
                    app_title += "🔒"
                
                if app.debug_switch_state.get() == "on":
                    app_title+="⚙️"
                    app.stream = show_debug(app.stream)
                    if len(threshholds)>0:
                        Filter.put_text(Filter,app.stream,"to mid: "+str(round(threshholds[0][0]))+","+str(round(threshholds[0][1])),10,60,(200,40,40))
                elif app.debug_switch_state.get() == "off":
                    app.stream = app.stream
                
                if app.always_ontop.get() == "on":
                    app_title += "🔖"
                
                app.title(app_title)
                app.camera_frame.configure(dark_image=Image.fromarray(app.stream))
                app.after(10, task)
            
            app.after(10,task())
            app.mainloop()