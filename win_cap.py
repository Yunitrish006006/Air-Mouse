from PIL import ImageGrab
import numpy as np
import cv2

image = ImageGrab.grab()
width, height = image.size

fourcc = cv2.VideoWriter_fourcc(*'XVID')
video = cv2.VideoWriter('test.avi', fourcc, 25, (width, height))

while True:
    img_rgb = ImageGrab.grab()
    img_bgr = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
    video.write(img_bgr)
    cv2.imshow('imm', img_bgr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()