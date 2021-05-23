from tensorflow import keras
import cv2
import numpy as np
import os,sys
g_dir = os.path.dirname(os.path.realpath(__file__))
def get_path(file_name):
    return os.path.join(g_dir,file_name)
class Predictor:
    def __init__(self):
        self.model1 = keras.models.load_model(get_path("model/model_0.h5"))
        self.model2 = keras.models.load_model(get_path("model/model_1_DA.h5"))
        self.model3 = keras.models.load_model(get_path("model/model_2.h5"))
        self.face = cv2.CascadeClassifier(get_path('face.xml')) # 创建人脸检测器    放在同目录

    def is_in_view(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)#将img转为回复图像，存放中gray中
        faces = self.face.detectMultiScale(gray,1.1,3) # 检测图像中的人脸
        if (len(faces) == 0):
            return False
        return True

    def predict(self, array, img):
        # is_in_view = self.model1.predict(array)
        array = keras.applications.xception.preprocess_input(array.reshape(1, 224, 224, 3))
        if not self.is_in_view(img):
            return False
        facing_direction = np.argmax(self.model2.predict(array),1)
        if facing_direction != 2:
            return False
        is_concentred = np.argmax(self.model3.predict(array),1)
        if is_concentred != 0:
            return False
        return True


