from application.main.view import StudentStateRecord
from protocal import Receiver
from flask import Flask, jsonify
import cv2
from flask.globals import request
import numpy as np
import json 
import os
# from Predictor import Predictor
from flask_sqlalchemy import SQLAlchemy

from application.data import app,db
import application.model as Model

img_que = []
courses = {}
counts = {}
cnt = 0
rcver = Receiver()

db.create_all()
# predictor = Predictor()

def ret_error(info:dict):
    info["header"] = "error"
    return json.dumps(info)

def ret_success(info:dict):
    info["header"] = "success"
    return json.dumps(info)

# 学生登录入口，需要传递学号，e.g. form={"student_id":"3180105494"}，返回值为是否成功登录
@app.route("/student_login", methods=['POST'])
def student_login():
    student_id = request.form["student_id"]
    teacher_id = 0
    for teacher in courses.keys():
        if student_id in courses[teacher].keys():
            teacher_id = teacher
            break
    if teacher_id == 0:
        return ret_error({"info":"The student is not belong to this courses!"})
    return ret_success({"info":"teacher login success","id":teacher_id})


# 教师登录入口，需要传递教师编号，e.g. form={"teacher_id": "02001002"})，返回值为是否成功登录
@app.route("/teacher_login", methods=['POST'])
def teacher_login():
    teacher_id = request.form["teacher_id"]
    filePath = "users\\" + str(teacher_id)
    # 创建老师
    state = os.path.exists(filePath)
    if state == False:
        os.makedirs(filePath)
    return ret_success({"info":"Teacher login success"})


# 教师注册课程，需要传递教师编号、课程编号以及所有参与本课程的学生编号，e.g. data="02001002$C0258$3180105494$3180101316$3180101111$3190101234"，返回值为是否注册成功
@app.route("/teacher_regist", methods=['POST'])
def teacher_regist():
    data = json.loads(request.data)
    teacher_id = data["teacher_id"]
    course_id = data["course_id"]
    students = data["students"]
    filePath = "users\\" + str(teacher_id) + "\\"  + str(course_id) + "_" + "student.txt"
    file = open(filePath, 'w') #
    for student in students:
        file.write(str(student) + '\n')
    file.close()
    filePath = "users\\" + str(teacher_id) + "\\" + str(course_id) + "_" + "state.txt"
    file = open(filePath, 'w')
    file.write('0' + '\n')
    return "Teacher regist success" 


# 教师选择课程按钮，需要传递教师编号，e.g. data="02001002"，返回值为当前教师开课的列表，以json格式返回
@app.route("/teacher_choose_course", methods=["POST"])
def teacher_choose():
    teacher_id = request.data.decode()
    names = os.listdir("users\\" + str(teacher_id))
    courses = []
    for name in names:
        courses.append(name.split('_')[0])
    return jsonify(courses)


# 教师开始上课按钮，需要传递教师编号和课程编号，e.g. data="02001002$C0258"，返回值为是否成功开始
@app.route("/teacher_class_begin", methods=["POST"])
def teacher_class_begin():
    data = json.loads(request.data)
    teacher_id = data["teacher_id"]
    course_id = data["course_id"]
    filePath = "users\\" + str(teacher_id) + "\\" + str(course_id) + "_" + "state.txt"
    file = open(filePath, 'r+')
    course_data_before = file.readlines()
    count = course_data_before[len(course_data_before) - 1]
    file.close()
    counts[teacher_id] = count
    filePath = "users\\" + str(teacher_id) + "\\" + str(course_id) + "_" + "student.txt"
    file = open(filePath)
    student_dict = {}
    students = file.readlines()
    for i in range(0, len(students)):
        student_dict[students[i].replace("\n", "")] = []
    courses[teacher_id] = student_dict
    file.close()
    return ret_success({"info":"Class success"})


# 教师检查学生状态函数，需要参数教师编号，e.g. data="02001002"，返回值为全体学生状态的list，以json格式发送
@app.route("/teacher_check_state", methods=['POST'])
def teacher_check():
    teacher_id = request.data.decode()
    state = {}
    for student in courses[teacher_id].keys():
        state[student] = (courses[teacher_id][student][len(courses[teacher_id][student]) - 1])
    return jsonify(state)


# 教师下课，需要参数教师编号、课程编号，e.g. data="02001002$C0258"
@app.route("/teacher_quit", methods=["POST"])
def teacher_quit():
    data = json.loads(request.data)
    teacher_id = data["teacher_id"]
    course_id = data["course_id"]
    # TODO: save the responding data of this teacher
    filePath = "users\\" + str(teacher_id) + "\\" + str(course_id) + "_" + "state.txt"
    file = open(filePath, 'a')
    for student in courses[teacher_id].keys():
        for item in courses[teacher_id][student]:
            file.write(str(item) + ' ')
        file.write('\n')
    file.write(str(int(counts[teacher_id]) + 1)  + '\n')
    file.close()
    courses.pop(teacher_id)
    counts.pop(teacher_id)
    return "Quit success"


# 学生发送图像，需发送课程id，index、学生编号，返回学生是否认真听课（True/False）
@app.route("/img_stream",methods=['POST'])
def stream():
    try:
        data = json.loads(request.data)
        course_id = data["course_id"]
        course_index = data["course_index"]
        student_id = data["student_id"]
        array, img = rcver.receive(request)
        res = True # tor.predict(array, img)
        stu = Model.CourseState.query.filter_by(course_id=course_id,index=course_index,student_id=student_id).first()
        stu.state = StudentStateRecord.concentrated if res else StudentStateRecord.distracted
        db.session.add(stu)
        db.session.commit()
        # courses[teacher_id][student_id].append(res)
        return ret_success({"result":res})
    except:
        import traceback,sys
        traceback.print_exc()
        return jsonify({"header":"error","info":"img_upload_fail"})


@app.route("/post_test",methods=['POST'])
def post_test():
    for item in request.form.items():
        print(item)
    return "success"

@app.route("/query_db/",methods=['GET'])
def test():
    stu = Model.Student(student_name="杨育潭",id=3180104668)
    db.session.add(stu)
    db.session.commit()
    return "success"

def get_image(img_byte):
    global cnt 
    cv2.imwrite('main.jpg',img_byte)
    cnt += 1

if __name__ == '__main__':
    app.run(debug=True)