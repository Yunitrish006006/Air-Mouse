import torch
import cv2
model = torch.hub.load('ultralytics/yolov5','custom',path="best.pt")

def detect_hand():
    img = camera.read()[1]
    result = model(img)
    result.xyxy[0]
    return result.pandas().xyxy[0]

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
    result.xyxy[0]
    print(result.pandas().xyxy[0])

