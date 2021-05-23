from enum import unique
from application.data import db

class Course(db.Model):
    __tablename__ = 'Course'
    id = db.Column(db.Integer,primary_key=True)
    course_name = db.Column(db.String(255))
    course_uid = db.Column(db.String(20),unique=True)
    course_intro = db.Column(db.Text)

    def __repr__(self) -> str:
        return "Course: id={};name={}".format(self.id,self.course_name)

class CourseEvaluation(db.Model):
    __tablename__ = 'CourseEvaluation'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_id = db.Column(db.Integer)
    index = db.Column(db.Integer)
    nr_concentrated = db.Column(db.Integer)
    nr_distracted = db.Column(db.Integer)
    nr_offline = db.Column(db.Integer)
    time_stamp = db.Column(db.DateTime)

    def __repr__(self) -> str:
        return f"{self.course_id}-{self.index} : {self.nr_concentrated}"

class CourseState(db.Model):
    __tablename__ = 'CourseState'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_id = db.Column(db.Integer)
    index = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    is_lecturing = db.Column(db.Boolean)

class Student(db.Model):
    __tablename__ = 'Student'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    student_name = db.Column(db.String(20))

class Student_Course(db.Model):
    __tablename__ = 'Student_Course'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    student_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)
    

class Teacher(db.Model):
    __tablename__ = 'Teacher'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    teacher_name = db.Column(db.String(20))

class Teacher_Course(db.Model):
    __tablename__ = 'Teacher_Course'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    teacher_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)

class CourseStateRecord(db.Model):
    __tablename__ = 'CourseStateRecord'
    row_id = db.Column(db.Integer,primary_key=True)
    course_id = db.Column(db.Integer)
    course_index = db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    state = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"{self.student_id} : ${self.course_id} ==> ${self.state}"
