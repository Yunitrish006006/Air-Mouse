import torch
import cv2

model = torch.hub.load('ultralytics/yolov5','custom',path="best.pt")

# img = "data/project/val/images/img1.jpg"
camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
camera.set(cv2.CAP_PROP_FPS, 60)

if not camera.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, img = camera.read()
    result = model(img)
    result.print()
    if cv2.waitKey(5) == ord('q'):
        break    # 按下 q 鍵停止
camera.release()