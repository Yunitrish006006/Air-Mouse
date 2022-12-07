import keyboard
import pyautogui
import pygetwindow

pyautogui.moveTo(0, 0, duration=0.001)
pyautogui.FAILSAFE = False
keep = True
screen_width = pyautogui.size()[0]
screen_height = pyautogui.size()[1]
x = pyautogui.position()[0]
y = pyautogui.position()[1]
vx = 16
vy = 16
while keep:
    if(keyboard.is_pressed('Esc')): keep = False
    # pyautogui.displayMousePosition()
    pyautogui.moveTo(x,y)
    x += vx
    y += vy
    if(x >= screen_width or x <= 0): vx *= -1
    if(y >= screen_height or y <= 0): vy *= -1
    
    # pyautogui.moveRel(vx,vy)
    # if(pyautogui.position()[0] >= screen_width or pyautogui.position()[0] <= 0): vx *= -1
    # if(pyautogui.position()[1] >= screen_height or pyautogui.position()[1] <= 0): vy *= -1
    
    # pyautogui.alert(text='', title=pygetwindow.getAllTitles()[0],button='ok')
    # print(pyautogui.position())
