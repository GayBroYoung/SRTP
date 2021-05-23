import numpy as np
import cv2
import requests
import flask
from flask.globals import request
from flask import Request
from PIL import Image

class Uploader:
    def __init__(self,url):
        self.url = url
    
    # img is np.array matrix,conducted by cv2
    def upload_img(self,img):
        _ , img_encoded = cv2.imencode('.jpg',img)
        img_arr = np.array(img_encoded)
        img_stream = img_arr.tobytes()
        requests.post(self.url,files={'img_file':img_stream})

class Receiver:
    def __init__(self) -> None:
        self.cnt = 0

    def receive(self,request:Request):
        files = request.files
        img_content = files.get('img_file').stream.read()
        img_array = np.frombuffer(img_content,np.uint8)
        img = cv2.imdecode(img_array,cv2.IMREAD_COLOR)
        pimg = Image.fromstring("RGB", cv2.GetSize(img), img.toString())
        array = numpy.array(pimg)
        return array, img
        # cv2.imwrite('./imgs/img_{}.jpg'.format(self.cnt),img)
        self.cnt += 1