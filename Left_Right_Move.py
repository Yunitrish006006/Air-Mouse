def moveCursor(var, move_type, direct, x, y): # call by Left_Right_move
    sensitive = 4 # 靈敏度
    if(var > 3):
        if (move_type == "left_right"):
            x += var * sensitive * direct
            win32api.SetCursorPos((round(x),round(y)))

def Left_Right_move(hand_landmarks): # call by hand_skeleton
    finger_tips = [5]
    finger_tips.insert(0,hand_landmarks.landmark[4].x * w) #大拇指
    finger_tips.insert(1,hand_landmarks.landmark[8].x * w)
    finger_tips.insert(2,hand_landmarks.landmark[12].x * w)
    finger_tips.insert(3,hand_landmarks.landmark[16].x * w)
    finger_tips.insert(4,hand_landmarks.landmark[20].x * w) #小指
    finger_center = statistics.mean(finger_tips);  #計算平均數

    if (finger_center_temp[0] == 0):
        finger_center_temp[0] = finger_center

    varitation = abs(finger_center - finger_center_temp[0])
    direction = np.sign(finger_center - finger_center_temp[0])*(-1)

    x = pyautogui.position()[0]
    y = pyautogui.position()[1]
    
    moveCursor(varitation,"left_right",direction,x,y)
    finger_center_temp[0] = finger_center
