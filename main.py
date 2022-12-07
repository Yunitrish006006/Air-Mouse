import keyboard
import pyautogui

print(pyautogui.size())
pyautogui.moveTo(0, 0, duration=0.001)
pyautogui.FAILSAFE = False
keep = True
while keep:
    if(keyboard.is_pressed('Esc')): keep = False
    # pyautogui.moveTo(1920/2, 1080/2)
    pyautogui.alert(text='', title='', button='OK')
