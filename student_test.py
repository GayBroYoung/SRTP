import requests
import sys

cmd = sys.argv[1]

if cmd == "c_b":
	requests.post("http://127.0.0.1:5000/teacher_class_begin", data="02001002$C0258")
elif cmd == "s_l":
	requests.post("http://127.0.0.1:5000/student_login", data={"student_id":"3180105494"})
elif cmd == "i_s":
	requests.post("http://127.0.0.1:5000/img_stream")
elif cmd == "t_q":
	requests.post("http://127.0.0.1:5000/teacher_quit", data="02001002$C0258")
elif cmd == "ck":
	requests.post("http://127.0.0.1:5000/teacher_check_state", data="02001002")
elif cmd == "t_l":
	requests.post("http://127.0.0.1:5000/teacher_login", data={"teacher_id": "02001002"})
elif cmd == "t_r":
	requests.post("http://127.0.0.1:5000/teacher_regist", data="02001002$C0258$3180105494$3180101316$3180101111$3190101234")
elif cmd == "tcc":
	requests.post("http://127.0.0.1:5000/teacher_choose_course", data="02001002")
elif cmd == "auto":
	requests.post("http://127.0.0.1:5000/teacher_login", data={"teacher_id": "02001002"})
	requests.post("http://127.0.0.1:5000/teacher_regist", data="02001002$C0258$3180105494$3180101316$3180101111$3190101234")
	requests.post("http://127.0.0.1:5000/teacher_choose_course", data="02001002")
	requests.post("http://127.0.0.1:5000/teacher_class_begin", data="02001002$C0258")
	requests.post("http://127.0.0.1:5000/student_login", data={"student_id":"3180105494"})
	requests.post("http://127.0.0.1:5000/img_stream")
	requests.post("http://127.0.0.1:5000/img_stream")
	requests.post("http://127.0.0.1:5000/img_stream")
	requests.post("http://127.0.0.1:5000/teacher_check_state", data="02001002")
	requests.post("http://127.0.0.1:5000/img_stream")
	requests.post("http://127.0.0.1:5000/teacher_check_state", data="02001002")
	requests.post("http://127.0.0.1:5000/teacher_quit", data="02001002$C0258")

