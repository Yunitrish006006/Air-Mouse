from email.mime import image
import tkinter
from turtle import update
import cv2
import numpy as np
import customtkinter as ctk
import os
from PIL import Image
# import win32com.client


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
            if ret: 
                frame = Image.fromarray(frame)
            else: 
                frame = Image.fromarray(np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8))
            return frame
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
        
        # def getDeviceList() -> list[str]:
        #     deviceList:list[str]=["select your camera"]
        #     wmi = win32com.client.GetObject ("winmgmts:")
        #     for usb in wmi.InstancesOf ("Win32_USBHub"):
        #         deviceList.append(str(usb.DeviceID))
        #     return deviceList
        def count_camera() -> int:
            count = 0
            for i in range(10):
                cap = cv2.VideoCapture(i)
                if not cap.isOpened(): break
                else: count+=1
            return count
        # 模式選擇面板
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Air Mouse", image=getIcon("rat.png",26,26),compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.normal_mode_button = getNavItems("normal","pc.png")
        self.normal_mode_button.grid(row=1, column=0, sticky="ew")

        self.game_mode_button = getNavItems("game","nv.png")
        self.game_mode_button.grid(row=2, column=0, sticky="ew")
        
        
        # self.cam_list = ctk.CTkComboBox(self.navigation_frame,width=160,values=["device: "+str(i) for i in range(count_camera())])
        # self.cam_list.grid(row=5, column=0,sticky="s")

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
        
        self.n1_button = ctk.CTkButton(self.normal_mode_ui, text="CTkButton", image=getIcon("rat.png",100,100), compound="left")
        self.n1_button.grid(row=2, column=0, padx=20, pady=10)

        #game mode
        self.game_window = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.game_window.grid_columnconfigure(0, weight=1)
        self.game_camera = ctk.CTkLabel(self.game_window,text="",image=camera)
        self.game_camera.grid(row=0, column=0, padx=20, pady=10)
        
        self.select_frame_by_name("normal")

if __name__ == "__main__":
    app = App()
    def task():
        camera.configure(dark_image=camera_update())
        app.after(1, task)
    app.after(1,task())
    app.mainloop()