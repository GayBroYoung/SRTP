import json
from flask.wrappers import Request
import numpy as np
import cv2
from PIL import Image

def to_json(obj):
    dict = obj.__dict__
    if "_sa_instance_state" in dict:
        del dict["_sa_instance_state"]
        return dict

def ret_json(status_code=None,obj:dict=None):
    if obj is None:
        obj = {}
    obj["header"] = StatusCode.SUCCESS if status_code is None else status_code

    return json.dumps(obj)

def img_receive(img_content):
    img_array = np.array(img_content)
    img = cv2.imdecode(img_array,cv2.IMREAD_COLOR)
    pimg = Image.fromstring("RGB", cv2.GetSize(img), img.toString())
    array = np.array(pimg)
    return array, img

class StatusCode:
    SUCCESS = 200
    FORMAT_ERROR = 101
    NOT_FOUND = 404
    DATABASE_ERROR = 500
    INTERNAL_ERROR = 600

