import win32api
import statistics
import numpy as np
import pyautogui
w = 640
h = 360
finger_center = [0,0]
finger_center_temp = [0,0]
varitation = [0,0]
direction = [0,0]

def moveMouse(var, direct, x, y):
    sensitive = 4 # 靈敏度
    if(var[0] > 3 or var[1] > 3):
        x += var[0] * sensitive * direct[0]
        y += var[1] * sensitive * direct[1] * 2
        win32api.SetCursorPos((round(x),round(y)))

def move(hand_landmarks):
    finger_tips = [5]
    finger_tips.insert(0,hand_landmarks.landmark[4].x * w) #大拇指
    finger_tips.insert(1,hand_landmarks.landmark[8].x * w)
    finger_tips.insert(2,hand_landmarks.landmark[12].x * w)
    finger_tips.insert(3,hand_landmarks.landmark[16].x * w)
    finger_tips.insert(4,hand_landmarks.landmark[20].x * w) #小指
    finger_center[0] = statistics.mean(finger_tips);  #計算平均數

    finger_y = [4]
    finger_y.insert(0,hand_landmarks.landmark[0].y * h)
    finger_y.insert(1,hand_landmarks.landmark[1].y * h)
    finger_y.insert(2,hand_landmarks.landmark[13].y * h)
    finger_y.insert(3,hand_landmarks.landmark[17].y * h)
    # finger_tips_pos.insert(4,hand_landmarks.landmark[17].y * h); #小指
    finger_center[1] = statistics.mean(finger_y);  #計算平均數
    if finger_center_temp[0] == 0:
        finger_center_temp[0] = finger_center[0]
        finger_center_temp[1] = finger_center[1]
    
    varitation[0], varitation[1] = abs(finger_center[0] - finger_center_temp[0]), abs(finger_center[1] - finger_center_temp[1])
    direction[0], direction[1] = np.sign(finger_center[0] - finger_center_temp[0])*(-1), np.sign(finger_center[1] - finger_center_temp[1])*(-1)
    
    x = pyautogui.position()[0]
    y = pyautogui.position()[1]
    
    moveMouse(varitation,direction,x,y)
    finger_center_temp[0] = finger_center[0]
    finger_center_temp[1] = finger_center[1]