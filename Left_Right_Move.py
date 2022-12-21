sensitive = 4 # 靈敏度
finger_center_temp = 0
def Left_Right_Move():
    global finger_center_temp
    finger_tips = [5]
    finger_tips.insert(0,hand_landmarks.landmark[4].x * w); #大拇指
    finger_tips.insert(1,hand_landmarks.landmark[8].x * w);
    finger_tips.insert(2,hand_landmarks.landmark[12].x * w);
    finger_tips.insert(3,hand_landmarks.landmark[16].x * w);
    finger_tips.insert(4,hand_landmarks.landmark[20].x * w); #小指
    finger_center = statistics.mean(finger_tips);  #計算平均數
    if finger_center_temp == 0:
        finger_center_temp = finger_center
    
    varitation = abs(finger_center - finger_center_temp)
    direction = np.sign(finger_center - finger_center_temp)*(-1)
    
    x = pyautogui.position()[0]
    y = pyautogui.position()[1]
    
    moveMouse(varitation,direction,x,y)
    finger_center_temp = finger_center

def moveMouse(var, direct, x, y):
    if(var > 3):
        x += var * sensitive * direct
        win32api.SetCursorPos((round(x),round(y)))

# 在迴圈中直接呼叫Left_Right_Move就好
