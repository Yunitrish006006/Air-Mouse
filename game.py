import pydirectinput
import keyboard
import time
import win32api, win32con
cycle = False
amo = False
turn = False
while True:
    if(keyboard.is_pressed('shift')): 
        cycle = False
        amo = False
        turn = False
    elif(keyboard.is_pressed('=')):
        pydirectinput.keyDown('w')
        time.sleep(20)
        pydirectinput.keyUp('w')
    elif(keyboard.is_pressed('-')): cycle = True
    elif(keyboard.is_pressed(']')): amo = True
    elif(keyboard.is_pressed('[')): turn = True
    
    if(cycle):
        for i in range(1,10):
            pydirectinput.keyDown('1')
            pydirectinput.keyUp('1')
            pydirectinput.keyDown('2')
            pydirectinput.keyUp('2')
            pydirectinput.keyDown('3')
            pydirectinput.keyUp('3')
        cycle = False
    if(amo):
        for i in range(1,100):
            pydirectinput.click(clicks=1)
            time.sleep(0.01)
        amo = False
    if(turn):
        # pydirectinput.moveTo(100,100,pydirectinput.MOUSEEVENTF_MOVE)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, 300, 300, 0, 0)
        # for i in range(1,100):
        #     pydirectinput.move(20, None)
        #     time.sleep(0.1)
        turn = False