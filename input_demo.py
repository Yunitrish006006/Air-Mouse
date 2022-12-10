import keyboard
import pyautogui
# import pygetwindow

def afk_mouse_abs():
    pyautogui.FAILSAFE = False
    keep = True
    screen_width = pyautogui.size()[0]
    screen_height = pyautogui.size()[1]
    x = pyautogui.position()[0]
    y = pyautogui.position()[1]
    vx = 16
    vy = 16
    while keep:
        if(keyboard.is_pressed('esc+shift')): keep = False
        pyautogui.moveTo(x,y)
        x += vx
        y += vy
        if(x >= screen_width or x <= 0): vx *= -1
        if(y >= screen_height or y <= 0): vy *= -1
def afk_mouse_rel():
    pyautogui.FAILSAFE = False
    keep = True
    screen_width = pyautogui.size()[0]
    screen_height = pyautogui.size()[1]
    vx = 16
    vy = 16
    while keep:
        if(keyboard.is_pressed('esc+shift')): keep = False
        pyautogui.moveRel(vx,vy)
        x = pyautogui.position()[0]
        y = pyautogui.position()[1]
        if(x >= screen_width-2 or x <= 1): vx *= -1
        if(y >= screen_height-2 or y <= 1): vy *= -1
afk_mouse_rel()