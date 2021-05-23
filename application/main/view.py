from datetime import datetime
import os,sys
import re
import cv2
from flask.globals import request
from numpy.core.records import record
base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..')
sys.path.append(base_dir)

from requests_toolbelt.multipart import decoder
import pickle
from flask import abort
import base64
from io import BytesIO
from PIL import Image
import numpy as np
# from application.Predictor import Predictor

from application.encoder import StatusCode, img_receive, to_json, ret_json
from application.data import db,app,manager
import application.model as Model
import json
db.create_all()
# predicter = Predictor()

interval = 100

#####
'''
    record[f"{course_id}_{index}"] = {
        "student_flags" : {
            3180104668:state
        }
    }

'''
class StudentStateRecord:
    offline = 0x00
    distracted = 0x01
    concentrated = 0x02

    def __init__(self,student_ids) -> None:
        self.states = {}
        for id in student_ids:
            self.states[id] = StudentStateRecord.offline

    def change_state(self,student_id,value):
        if student_id not in self.states.keys():
            print("student id not exist!")
            return 
        if value not in [1,2,3]:
            print("invalid value")
            return 
        self.states[student_id] = value

records = {}

# 通过teacher_id获得该老师教授的所有课程的课程信息
@app.route("/get_teacher_course/<teacher_id>")
def get_teacher_course(teacher_id):
    clst = Model.Teacher_Course.query.filter_by(teacher_id=teacher_id).all()
    course_id_lst = [item.course_id for item in clst]
    course_lst = []
    for cid in course_id_lst:
        course = Model.Course.query.filter_by(id=cid).first()
        course_lst.append(to_json(course))

    return ret_json(StatusCode.SUCCESS,{"courses":course_lst})

# 通过student_id获得该老师教授的所有课程的课程信息
@app.route("/get_student_course/<student_id>")
def get_student_course(student_id):
    clst = Model.Student_Course.query.filter_by(student_id=student_id).all()
    course_id_lst = [item.course_id for item in clst]
    course_lst = []
    for cid in course_id_lst:
        course = Model.Course.query.filter_by(id=cid).first()
        course_lst.append(to_json(course))
    return ret_json(StatusCode.SUCCESS,{"courses":course_lst})
'''
学生登录接口：
post样例：
    {"student_id":3180104668}
'''
@app.route("/student_login/",methods=['POST'])
def student_login():
    pst_data = json.loads(request.get_data())
    if "student_id" not in pst_data:
        return ret_json(StatusCode.FORMAT_ERROR)

    student_id = pst_data["student_id"]
    # print(student_id)
    stu = Model.Student.query.filter_by(id=student_id).first()
    if stu is None:
        return ret_json(StatusCode.NOT_FOUND)
    
    return ret_json(StatusCode.SUCCESS,{"student":to_json(stu)})


'''
老师登录接口：
post样例：
    {"teacher_id":3180104668}
'''
@app.route("/teacher_login/",methods=['POST'])
def teacher_login():
    pst_data = json.loads(request.get_data())
    if "teacher_id" not in pst_data:
        return ret_json(StatusCode.FORMAT_ERROR)

    teacher_id = pst_data["teacher_id"]
    # print(student_id)
    tchr = Model.Teacher.query.filter_by(id=teacher_id).first()
    if tchr is None:
        abort(404)
    return ret_json(StatusCode.SUCCESS,{"teacher":to_json(tchr)})


@app.route("/register_course/",methods=['POST'])
def register_course():
    register_info = json.loads(request.get_data())
    try:
        teacher_id = register_info["teacher_id"]
        course_name = register_info["course_name"]
        course_intro = register_info["course_intro"]
        course_uid = register_info["course_uid"]
    except:
        import traceback
        traceback.print_exc()
        return ret_json(StatusCode.FORMAT_ERROR)
    try:
        tchr = Model.Teacher.query.filter_by(id=teacher_id).first()
        if tchr is None:
            return ret_json(StatusCode.NOT_FOUND,{"detail":"teacher id not exist"})
        course = Model.Course(course_name=course_name,course_uid=course_uid,course_intro=course_intro)
        # tc_map = Model.Teacher_Course(teacher_id=teacher_id,course_id=course.id)
        db.session.add(course)
        db.session.commit()
        tc_map = Model.Teacher_Course(teacher_id=teacher_id,course_id=course.id)
        db.session.add(tc_map)
        db.session.commit()
        
    except:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        abort(500)
    return ret_json(StatusCode.SUCCESS)

@app.route("/operate_class/",methods=['POST'])
def begin_class():
    post_info = json.loads(request.get_data())
    course_id = post_info["course_id"]
    course_type = post_info["course_type"]
    current_time = datetime.now()
    
    course = Model.Course.query.filter_by(id=course_id).first()
    course_index = Model.CourseState.query.filter_by(course_id=course_id).all()
    size = len(course_index)
    if course is None:
        return ret_json(StatusCode.NOT_FOUND)
    if course_type == "begin":

        key_ = f"{course_id}_{size+1}"
        # 找到所有该课程的学生id
        students = Model.Student_Course.query.filter_by(course_id=course_id).all()
        students = [item.id for item in students]
        if key_ not in records.keys():
            records[key_] = StudentStateRecord(students)
        rcd : StudentStateRecord = records[key_]
        
        course_state = Model.CourseState(course_id=course_id,index=size+1,start_time=current_time,is_lecturing=True)
        db.session.add(course_state)
        db.session.commit()
        # print(course_state)
        students = Model.Student_Course.query.filter_by(course_id=course_id).all()
        # records[f"{course_id}_{size+1}"] = StudentStateRecord([item.student_id for item in students])
        return_data = {"course_id":course_state.id,"course_index":size+1}
        
        return ret_json(StatusCode.SUCCESS,{"course":return_data})
    if course_type == "end":
        # find the not ending course
        course_state = Model.CourseState.query.filter_by(course_id=course_id,index = size).first()
        # return to_json
        if course_state is None:
            ret_json(StatusCode.NOT_FOUND,{"detail":"course id not exist"})
        
        course_state.end_time = current_time
        course_state.is_lecturing = False
        # db.session.add(course_state)
        state_info = Model.CourseStateRecord.query.filter_by(course_index=size,course_id=course_id).all()
        result = calculate(state_info)
        result["nr_offline"] = len(state_info) - result["nr_concentrated"] - result["nr_distracted"]
        print(size,course_id)
        Model.CourseStateRecord.query.filter_by(course_index=size,course_id=course_id).delete()
        db.session.commit()
        return ret_json(StatusCode.SUCCESS,{"detail":"exit class" + str(course_id) + " " + str(size)})
    return ret_json(StatusCode.FORMAT_ERROR)
    
# 获取正在进行的课程
@app.route("/get_lecturing_course",methods=['POST'])
def get_lecturing_course():
    post_data = json.loads(request.get_data())
    usr_type = post_data["user_type"]
    usr_id = post_data["id"]

    if usr_type != "teacher" and usr_type != "student":
        return ret_json(StatusCode.FORMAT_ERROR)
    courses = []
    # 多表联合查询 得到当前和用户有关联的所有课程中正在上课的课程
    if usr_type == "teacher":
        courses = Model.CourseState.query\
            .filter(Model.CourseState.is_lecturing == True)\
            .join(Model.Teacher_Course,Model.Teacher_Course.course_id == Model.CourseState.course_id)\
            .filter(Model.Teacher_Course.teacher_id == usr_id)\
            .all()

    elif usr_type == "student":
        
        courses = Model.CourseState.query\
            .filter(Model.CourseState.is_lecturing == True)\
            .join(Model.Student_Course,Model.Student_Course.course_id == Model.CourseState.course_id)\
            .filter(Model.Student_Course.student_id == usr_id)\
            .all() 

    courses = [{"course_id":course.course_id , "course_index" : course.index} for course in courses]
    return ret_json(StatusCode.SUCCESS,{"courses":courses})

@app.route("/img_stream",methods=['POST'])
def img_stream():
    # return request.data
    try:
        multipart_data = request.form
        student_id = request.form.get("student_id")
        course_index = request.form.get("course_index")
        course_id = request.form.get("course_id")
        img = request.form.get("img")
        byte_data = base64.b64decode(img)
        image_data = BytesIO(byte_data)
        pil_img = Image.open(image_data)
        # pil_img.save("main.jpeg")
        image = pil_img.resize((224,224))
        arr = np.array(image)
        cv_img = cv2.cvtColor(np.array(pil_img),cv2.COLOR_RGB2BGR)  
        # student_id = int(data["student_id"])
        # course_id  = int(data["course_id"])
        # course_index = int(data["course_index"])
        # img_content = request.files["img"]
        # arr,img = img_receive(img_content)
        # print(img)
        # array, img = img_receive(request)
        # predicter.predict(arr, cv_img)
        # TODO:
        # 添加记录
        res = True # tor.predict(array, img)
        stu = Model.CourseStateRecord.query.filter_by(course_id=course_id,course_index=course_index,student_id=student_id).first()
        print(stu)
        if res:
            stu.state = StudentStateRecord.concentrated  
        else:
            stu.state = StudentStateRecord.distracted
        db.session.add(stu)
        db.session.commit()
        return ret_json(StatusCode.SUCCESS,{"result":res})
    except:
        import traceback,sys
        traceback.print_exc()
        return ret_json(StatusCode.INTERNAL_ERROR)
    # 直接将结果存储到临时的表格中

@app.route("/get_course_info/<course_id>")
def get_course_info(course_id):
    course_state_lst = [] 
    course_state_lst = Model.CourseState.query.filter_by(course_id=course_id).all()
    print("state lst")
    rset = []
    for item in course_state_lst:
        res_item = {}
        res_item["course_id"] = item.course_id        
        res_item["index"] = item.index        
        res_item["start_time"] = item.start_time.strftime("%Y-%m-%d %H:%M:%S") if item.start_time is not None else None       
        res_item["end_time"] = item.end_time.strftime("%Y-%m-%d %H:%M:%S")  if item.end_time is not None else None    
        res_item["is_lecturing"] = item.is_lecturing
        rset.append(res_item)       

    return json.dumps({"header":StatusCode.SUCCESS,"course_history":rset})

# 返回当前状态下 某一课程的人员信息：
@app.route("/get_current_evaluation/",methods=['POST'])
def get_current_evaluation():
    data = json.loads(request.get_data())
    course_id = data["course_id"]
    course_index = data["index"]
    student_states = Model.CourseStateRecord.query.filter_by(course_id=course_id,course_index=course_index).all()
    total_num = len(Model.Student_Course.query.filter_by(course_id=course_id).all())
    result = {}
    current_time = datetime.now()
    if len(student_states) == 0:
        result = {
            "nr_concentrated":0,
            "nr_distracted":0,
            "nr_offline":total_num
        }
    else:
        result = calculate(student_states)
        result["nr_offline"] = total_num - (result["nr_distracted"] + result["nr_concentrated"])

    ev = Model.CourseEvaluation(course_id=course_id,index=course_index,
        nr_concentrated=result["nr_concentrated"],
        nr_distracted = result["nr_distracted"],
        nr_offline = result["nr_offline"],
        time_stamp=current_time)
    db.session.add(ev)
    db.session.commit()
    return json.dumps(result)

# 学生加入课程，post index，course-Id student-id
# 
@app.route("/student_join_class",methods=['POST'])
def student_join_class():
    info = json.loads(request.get_data())
    course_index = info["index"]
    course_id = info["course_id"]
    student_id = info["student_id"]
    course_state_info = Model.CourseStateRecord.query.filter_by(course_id=course_id,course_index=course_index,student_id=student_id).first()
    if course_state_info is not None:
        return json.dumps({"header":200})
    course_state_info = Model.CourseStateRecord(course_id=course_id,course_index=course_index,student_id=student_id,state=StudentStateRecord.distracted)
    db.session.add(course_state_info)
    db.session.commit()
    return json.dumps({"header":"record generated"})

@app.route("/student_leave_class",methods=['POST'])
def student_leave_class():
    info = json.loads(request.get_data())
    course_index = info["index"]
    course_id = info["course_id"]
    student_id = info["student_id"]
    course_state_info = Model.CourseStateRecord.query.filter_by(course_id=course_id,course_index=course_index,student_id=student_id).first()
    if course_state_info is not None:
        db.session.delete(course_state_info)
        db.session.commit()
    return json.dumps({"header":"record deleted"})

def calculate(info):
    nr_distracted,nr_concentrated= 0,0
    for state in info:
        v = state.state
        if v == StudentStateRecord.distracted:
            nr_distracted += 1
        elif v == StudentStateRecord.concentrated:
            nr_concentrated += 1
    result = {
        "nr_concentrated" : nr_concentrated,
        "nr_distracted" : nr_distracted,
    }
    return result

@app.route("/get_user_info",methods=['POST'])
def get_user_info():
    data = json.loads(request.get_data())
    print(data)
    type = data["user_type"]
    user = {}
    if type == "student":
        user = Model.Student.query.filter_by(id=data["user_id"]).first()
    elif type == "teacher":
        user = Model.Student.query.filter_by(id=data["user_id"]).first()
    return to_json(user)

@app.route('/get_course_evaluation',methods=["POST"])
def get_course_evaluation():
    data = json.loads(request.get_data())
    course_id = data["course_id"]
    course_index = data["course_index"]
    course_info = Model.CourseEvaluation.query.filter_by(course_id = course_id,index=course_index).all()
    course_history = []
    for item in course_info:
        data = {}
        data["course_id"] = item.course_id
        data["course_index"] = item.index
        data["nr_concentrated"] = item.nr_concentrated
        data["nr_distracted"] = item.nr_distracted
        data["nr_offline"] = item.nr_offline
        course_history.append(data)

    return ret_json(obj={"history":course_history})
    # for item in sorted_list:
    #     item.time_stamp = item.time_stamp.strftime("%H:%M:%S")
    #     item = to_json(item)

    # return to_json(course_info[0])

@app.route('/test')
def test():
    return "true"

if __name__ == '__main__':
    app.run(debug=True)