from mimetypes import init
from tarfile import FIFOTYPE
import tkinter as tk
from tkinter.tix import COLUMN
from tracemalloc import Snapshot
import customtkinter as ctk
import os
from PIL import Image
import cv2
import numpy as np
import math
import win32com.client

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

class AirMouseUI(ctk.CTk):
    main_frame:ctk.CTkFrame = None
    mouse_state:ctk.StringVar = None
    always_ontop:ctk.StringVar = None
    debug_mode:ctk.StringVar = None
    stream:np.dtype = np.random.randint(0, 255, size=(360, 640, 3),dtype=np.uint8)
    camera_frame = ctk.CTkImage(dark_image=Image.fromarray(stream),size=(640,360))
    FilterMode:str = "origin"
    FileCount = 2550000
    def __init__(self):
        ctk.CTk.__init__(self)
        self._frame = None
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src\\image")
        self.iconbitmap(os.path.join(image_path, "rat.ico"))
        self.title("   Air Mouse")
        self.geometry("960x640")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
        def getIcon(name:str,width,height) -> ctk.CTkImage:
                return ctk.CTkImage(
                    light_image=Image.open(os.path.join(image_path, name)),
                    dark_image=Image.open(os.path.join(image_path, name)),
                    size=(width, height))
        def getTab(page) -> ctk.CTkButton:
            return ctk.CTkButton(
                self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text=page.page_name,
                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                image=getIcon(page.page_icon,32,32), anchor="w", command=lambda:self.switch_frame(page))
        def getSwitch(row:int,var:ctk.StringVar,text:str,command=lambda:print("no function input")):
            switch = ctk.CTkSwitch(self.navigation_frame,text=text,variable=var,onvalue="on",offvalue="off",command=command)
            switch.grid(row=row,column=0,pady=10,sticky="s")
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(10, weight=1)
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="   Air Mouse", image=getIcon("rat.png",26,26),compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        
        option = ["origin","grayscale","revert_de","de","enhance","enhance_grayscale","sobel","sobel_grayscale","revert_sobel","blur","lines","noise","black","white","revert"]
        def filterChange(choice) -> None: self.FilterMode = choice
        self.filter_list = ctk.CTkComboBox(self.navigation_frame,values=option,command=filterChange)
        self.filter_list.grid(row=7, column=0, pady=10,sticky="s")
        
        self.mouse_state = ctk.StringVar(value="off")
        self.always_ontop = ctk.StringVar(value="off")
        self.debug_mode = ctk.StringVar(value="off")
        for c,name in zip([i for i in range(3)],[Normal,Game,Camera]):
            self.tab = getTab(name)
            self.tab.grid(row=c, column=0, sticky="ew")
        
        getSwitch(4,self.mouse_state,"滑鼠功能")
        getSwitch(5,self.always_ontop,"視窗置頂",lambda:self.wm_attributes('-topmost',self.always_ontop.get()=="on"))
        getSwitch(6,self.debug_mode,"除錯功能")
        
        
        def getDeviceList() -> list[str]:
            deviceList:list[str]=["default camera"]
            wmi = win32com.client.GetObject ("winmgmts:")
            for usb in wmi.InstancesOf ("Win32_USBHub"):
                deviceList.append(str(usb.DeviceID))
            return deviceList
        self.cam_list = ctk.CTkComboBox(self.navigation_frame,values=getDeviceList(),command=lambda x:print("you have selected " + str(x) +" as camera"))
        self.cam_list.grid(row=8, column=0, pady=10,sticky="s")
        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["System","Light", "Dark"],command=ctk.set_appearance_mode)
        self.appearance_mode_menu.grid(row=9, column=0, padx=20, pady=10, sticky="s")
        self.switch_frame(Camera)
        
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self.main_frame is not None:
            self.main_frame.destroy()
        self.main_frame = new_frame
        self.main_frame.grid(row=0, column=1, sticky="nsew")
    
    def snapshot(self):
         cv2.imwrite("Test/"+str(self.FileCount)+".png",self.stream)



class Normal(ctk.CTkFrame):
    page_icon = "pc.png"
    page_name = "normal"
    def __init__(self, master: AirMouseUI):
        ctk.CTkFrame.__init__(self, master)
        ctk.CTkFrame.configure(self,fg_color='transparent')
        ctk.CTkLabel(self, text=self.page_name, font=('Helvetica', 18, "bold")).grid_columnconfigure(5, weight=1)
        ctk.CTkLabel(self,text="",image=master.camera_frame).grid(row=0, column=0, columnspan=5, padx=70, pady=10)
class Game(ctk.CTkFrame):
    page_icon = "nv.png"
    page_name = "game"
    def __init__(self, master: AirMouseUI):
        ctk.CTkFrame.__init__(self, master)
        ctk.CTkFrame.configure(self,fg_color='transparent')
        ctk.CTkLabel(self, text=self.page_name, font=('Helvetica', 18, "bold")).grid_columnconfigure(5, weight=1)
        ctk.CTkLabel(self,text="",image=master.camera_frame).grid(row=0, column=0, columnspan=5, padx=70, pady=10)
class Camera(ctk.CTkFrame):
    page_icon = "camera.png"
    page_name = "camera"
    def __init__(self, master: AirMouseUI):
        ctk.CTkFrame.__init__(self, master)
        ctk.CTkFrame.configure(self,fg_color='transparent')
        ctk.CTkLabel(self, text=self.page_name, font=('Helvetica', 18, "bold")).grid_columnconfigure(5, weight=1)
        ctk.CTkLabel(self,text="",image=master.camera_frame).grid(row=0, column=0, columnspan=5, padx=70, pady=10)
        ctk.CTkButton(self, text="Photo",command=lambda:master.snapshot()).grid(row=8,column=2,pady=100)
            

if __name__ == "__main__":
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    camera.set(cv2.CAP_PROP_FPS, 60)
    camera_width = camera.get(3)
    camera_height = camera.get(4)
    app = AirMouseUI()
    window_width = app.winfo_screenwidth()
    window_height = app.winfo_screenheight()
    def task() -> None:
        ret , video = camera.read()
        if ret: video = cv2.cvtColor(video, cv2.COLOR_BGR2RGB)
        app.stream = Filter.progress_filter(Filter,video,app.FilterMode)
        app.camera_frame.configure(dark_image=Image.fromarray(app.stream))
        app.after(10, task)
    app.after(10,task())
    app.mainloop()