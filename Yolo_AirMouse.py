import array
from multiprocessing.dummy import Array
from turtle import color
import cv2
import numpy as np
import math
import tkinter
import customtkinter as ctk
import os
from PIL import Image
import win32api
import win32con
from typing import *
from datetime import datetime
import win32com.client
import torch
import pandas

from Main import gray_scale

class AppControl():
    data = None
    stablizor:List[int]=[]
    stamp:List[float]=[]
    gap:List[int]=[]
    def __init__(self,frame:Image) -> None:
        global data
        data = frame
    def get_timegap(time:float=datetime.now().timestamp()) -> float:
        return datetime.now().timestamp()-time
        
    def run(self) -> None:
        print(self.get_timegap())
    
    def getAction1(self,data,id:int=len(gap)):
        if(self.get_timegap(self.stamp[id])>self.gap[id]):
            data = data #do something
            win32api.SetCursorPos((round(960), round(540)))
            self.gap[id] = self.get_timegap(self.stamp[id])
class App(ctk.CTk):
    def select_frame_by_name(self, name) -> None:
        self.normal_mode_button.configure(fg_color=("gray75", "gray25") if name == "normal" else "transparent")
        self.game_mode_button.configure(fg_color=("gray75", "gray25") if name == "game" else "transparent")
        self.camera_mode_button.configure(fg_color=("gray75", "gray25") if name == "camera" else "transparent")
        self.normal_mode_ui.grid_forget()
        self.game_window.grid_forget()
        self.camera_window.grid_forget()
        if name == "normal":
            self.normal_mode_ui.grid(row=0, column=1, sticky="nsew")
        elif name == "game":
            self.game_window.grid(row=0, column=1, sticky="nsew")
        elif name == "camera":
            self.camera_window.grid(row=0, column=1, sticky="nsew")

    def change_appearance_mode_event(self, new_appearance_mode) -> None:
        ctk.set_appearance_mode(new_appearance_mode)
        
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    getYolo = torch.hub.load('ultralytics/yolov5','custom',path="best.pt")
    LenMode="NoLen"
    
    px = 30
    py = 30
    
    def detect_hand(self,frame):
        result = self.getYolo(frame)
        result.xyxy[0]
        return result.pandas().xyxy[0].to_numpy()
    
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
        global camera_update
        def len(frame:np.dtype,mode:str):
            def linearization(frame):
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
            def grayscalize(frame):
                return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)
            def sobelize(frame):
                    x = abs(cv2.Sobel(frame, cv2.CV_16S, 1, 0))
                    y = abs(cv2.Sobel(frame, cv2.CV_16S, 0, 1))
                    x = cv2.convertScaleAbs(x)
                    y = cv2.convertScaleAbs(y)
                    frame = cv2.addWeighted(x, 0.5, y, 0.5, 0.3)
                    return frame
            def enhancialize(frame):
                kernal = np.ones((3,3),np.uint8)
                frame = abs(255-frame)
                for i in range(0,3):
                    frame = cv2.dilate(frame,kernal,iterations=2)
                    frame = cv2.erode(frame,kernal,iterations=2)
                return frame
            def DE(frame):
                kernal = np.ones((2,2),np.uint8)
                for _ in range(0,30):
                    frame = cv2.erode(frame,kernal,iterations=2)
                    frame = cv2.dilate(frame,kernal,iterations=2)
                return frame
            if(mode == "Nolen"): pass
            elif(mode == "DE"): frame = DE(frame)
            elif(mode == "enhance"): frame = enhancialize(frame)
            elif(mode == "enhance_gray"): frame = gray_scale(enhancialize(frame))
            elif(mode == "noise"): frame = np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8)
            elif(mode == "black"): frame = np.zeros((360,640,3),dtype=np.uint8)
            elif(mode == "white"): frame = np.ones((360,640,3),dtype=np.uint8)*255
            elif(mode == "sobel"): frame = sobelize(frame)
            elif(mode == "sobel_gray"): frame = gray_scale(sobelize(frame))
            elif(mode == "lines"): frame = linearization(frame)
            elif(mode == "revert"): frame = abs(255-frame)
            elif(mode == "blur"): frame = cv2.addWeighted(abs(sobelize(frame) + 30),0.7,frame,1,0)
            elif(mode == "GrayScale"): frame = grayscalize(frame)
            elif(mode == "revert_sobel"): frame = cv2.addWeighted(sobelize(255-frame),0.7,frame,1,0)
            else:pass
            return frame            
        def camera_update() -> Image:
            _, frame = self.camera.read()
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame,0)
            if mouse_state.get()=="on":
                value:List[str]=self.detect_hand(frame)
                if debug_switch_state.get():
                    if(len(value)>0):
                        self.px = int((float(value[0][0])/2+float(value[0][2]))/2)
                        self.py = int((float(value[0][1])/2+float(value[0][3]))/2)
                        self.put_text(frame,str(value[0][6]),self.px,self.py,(255,0,0))
                    else:
                        print(self.px,self.py)
                        self.put_text(frame,"empty",self.px,self.py,(255,0,0))
            return Image.fromarray(len(frame,self.LenMode))
        def getIcon(name,width,height) -> ctk.CTkImage:
            return ctk.CTkImage(
                light_image=Image.open(os.path.join(image_path, name)),
                dark_image=Image.open(os.path.join(image_path, name)),
                size=(width, height))
        def getNavItems(name,icon) -> ctk.CTkButton:
            return ctk.CTkButton(
                self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text=name,
                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                image=getIcon(icon,32,32), anchor="w", command=lambda:self.select_frame_by_name(name))
        
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
        
        global mouse_state
        mouse_state = ctk.StringVar(value="off")
        self.mouse = ctk.CTkSwitch(self.navigation_frame,text="滑鼠功能",variable=mouse_state,onvalue="on",offvalue="off")
        self.mouse.grid(row=5, column=0, pady=10,sticky="s")
        self.mouse.deselect()
        
        global debug_switch_state
        debug_switch_state = ctk.StringVar(value="off")
        self.debug_switch = ctk.CTkSwitch(self.navigation_frame,text="除錯功能",variable=debug_switch_state,onvalue="on",offvalue="off")
        self.debug_switch.grid(row=6, column=0, pady=10,sticky="s")
        self.debug_switch.deselect()
        
        option = ["NoLen","GrayScale","DE","enhance","enhance_gray","sobel","sobel_gray","revert_sobel","blur","lines","noise","black","white","revert"]
        def lenChange(choice) -> None: self.LenMode = choice
        self.cam_list = ctk.CTkComboBox(self.navigation_frame,values=option,command=lenChange)
        self.cam_list.grid(row=7, column=0, pady=10,sticky="s")
        
        self.cam_list = ctk.CTkComboBox(self.navigation_frame,values=getDeviceList(),command=lambda x:print("you have selected " + str(x) +" as camera"))
        self.cam_list.grid(row=8, column=0, pady=10,sticky="s")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["System","Light", "Dark"],command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=9, column=0, padx=20, pady=10, sticky="s")
        
        # mutual components
        global camera
        camera = ctk.CTkImage(dark_image=camera_update(),size=(640,360))
        #normal mode
        self.normal_mode_ui = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.normal_mode_ui.grid_columnconfigure(0, weight=1)
        self.n_cam = ctk.CTkLabel(self.normal_mode_ui,text="",image=camera)
        self.n_cam.grid(row=0, column=0, padx=20, pady=10)
        
        self.n1_button = ctk.CTkButton(self.normal_mode_ui, text="CTkButton", compound="left")
        self.n1_button.grid(row=2, column=0, padx=20, pady=10)

        #game mode
        self.game_window = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.game_window.grid_columnconfigure(0, weight=1)
        self.game_camera = ctk.CTkLabel(self.game_window,text="",image=camera)
        self.game_camera.grid(row=0, column=0, padx=20, pady=10)
        
        #camera mode
        self.camera_window = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.camera_window.grid_columnconfigure(0, weight=1)
        self.camera_camera = ctk.CTkLabel(self.camera_window,text="",image=camera)
        self.camera_camera.grid(row=0, column=0, padx=20, pady=10)
        self.x = 0
        def snap():
            camera_update().save("Test/"+str(self.x)+".png")
            self.x+=1
        self.cheese_button = ctk.CTkButton(self.camera_window, text="cheese", compound="left",command=snap)
        self.cheese_button.grid(row=2, column=0, padx=20, pady=10)
        
        
        self.select_frame_by_name("camera")

if __name__ == "__main__":
    app = App()
    def task() -> None:
        camera.configure(dark_image=camera_update())
        app.after(20, task)
    app.after(1,task())
    app.mainloop()