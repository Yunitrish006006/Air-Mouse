from dataclasses import dataclass
from email.mime import image
from tkinter import *
from turtle import update
import cv2
import numpy as np
import math
import customtkinter as ctk
import os
from PIL import Image
import win32api
import win32con
from datetime import datetime
import win32com.client

class AppControl():
    data = None
    stablizor:list[int]=[]
    stamp:list[float]=[]
    gap:list[int]=[]
    def __init__(self,frame:Image) -> None:
        global data
        data = frame
    def get_timegap(time:float=datetime.now().timestamp()) -> float:
        return datetime.now().timestamp()-time
        
    def run(self) -> None:
        print(self.get_timegap())
    
    def getAction1(self,data,id:int=len(gap)):
        if(self.get_timegap(self.stamp[id])>self.gap[id]):
            data = data#do something
            win32api.SetCursorPos((round(960), round(540)))
            self.gap[id] = self.get_timegap(self.stamp[id])
            
    
class App(ctk.CTk):
    def select_frame_by_name(self, name) -> None:
        self.normal_mode_button.configure(fg_color=("gray75", "gray25") if name == "normal" else "transparent")
        self.game_mode_button.configure(fg_color=("gray75", "gray25") if name == "game" else "transparent")
        self.normal_mode_ui.grid_forget()
        self.game_window.grid_forget()
        if name == "normal":
            self.normal_mode_ui.grid(row=0, column=1, sticky="nsew")
        elif name == "game":
            self.game_window.grid(row=0, column=1, sticky="nsew")

    def change_appearance_mode_event(self, new_appearance_mode) -> None:
        ctk.set_appearance_mode(new_appearance_mode)
        
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    
    LenMode="NoLen"

    def __init__(self) -> None:
        super().__init__()
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src\\image")
        self.iconbitmap(os.path.join(image_path, "rat.ico"))
        self.title("\tAir Mouse")
        self.geometry("960x640")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # 載入影像
        global camera_update
        def camera_update() -> Image:
            ret, frame = self.camera.read()
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if(ret):
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
                if(self.LenMode == "Nolen"):
                    pass
                elif(self.LenMode == "noise"):
                    frame = np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8)
                elif(self.LenMode == "black"):
                    frame = np.zeros((360,640,3),dtype=np.uint8)
                elif(self.LenMode == "white"):
                    frame = np.ones((360,640,3),dtype=np.uint8)*255
                elif(self.LenMode == "sobel"):
                    frame = sobelize(frame)
                elif(self.LenMode == "lines"):
                    frame = linearization(frame)
                elif(self.LenMode == "revert"):
                    frame = abs(255-frame)
                elif(self.LenMode == "blur"):
                    frame = cv2.addWeighted(abs(sobelize(frame) + 30),0.7,frame,1,0)
                elif(self.LenMode == "GrayScale"):
                    frame = grayscalize(frame)
                elif(self.LenMode == "revert_sobel"):
                    frame = cv2.addWeighted(sobelize(255-frame),0.7,frame,1,0)
                return Image.fromarray(frame)
            else:
                return Image.fromarray(np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8))
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
        
        def getDeviceList() -> list[str]:
            deviceList:list[str]=["select your camera"]
            wmi = win32com.client.GetObject ("winmgmts:")
            for usb in wmi.InstancesOf ("Win32_USBHub"):
                deviceList.append(str(usb.DeviceID))
            return deviceList
        # 側邊攔
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Air Mouse", image=getIcon("rat.png",26,26),compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.normal_mode_button = getNavItems("normal","pc.png")
        self.normal_mode_button.grid(row=1, column=0, sticky="ew")

        self.game_mode_button = getNavItems("game","nv.png")
        self.game_mode_button.grid(row=2, column=0, sticky="ew")
        
        global switch
        switch = ctk.StringVar(value="off")
        self.switch = ctk.CTkSwitch(self.navigation_frame,text="開啟/關閉 滑鼠",variable=switch,onvalue="on",offvalue="off")
        self.switch.grid(row=3, column=0,sticky="s")
        self.switch.deselect()
        
        option = ["NoLen","noise","black","white","sobel","lines","revert","blur","GrayScale","revert_sobel"]
        def lenChange(choice): self.LenMode = choice
        self.cam_list = ctk.CTkComboBox(self.navigation_frame,values=option,command=lenChange)
        self.cam_list.grid(row=4, column=0,sticky="s")
        
        self.cam_list = ctk.CTkComboBox(self.navigation_frame,values=getDeviceList(),command=print("this function is not available"))
        self.cam_list.grid(row=5, column=0,sticky="s")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["System","Light", "Dark"],command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=10, sticky="s")
        
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
        
        self.select_frame_by_name("normal")

if __name__ == "__main__":
    app = App()
    def task() -> None:
        camera.configure(dark_image=camera_update())
        app.after(20, task)
    app.after(1,task())
    app.mainloop()