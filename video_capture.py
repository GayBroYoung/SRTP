import cv2
import numpy as np
from protocal import Uploader

cap = cv2.VideoCapture(0)
frame_interval = 10
frame_max_count = 50

cnt = 0
uploader = Uploader('http://127.0.0.1:5000/img_stream')


while True:
    ret,frame = cap.read()
    key = cv2.waitKey(1)
    frame = cv2.flip(frame,1)
    cnt += 1
    if cnt == frame_interval:
        cnt = 0
        uploader.upload_img(frame)

    cv2.imshow('capture',frame)
    if key == ord('q'):
        break
cap.release()