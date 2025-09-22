from fastapi import FastAPI
from typing import Union

app = FastAPI()  # FastAPI 서버 객체 생성

# 1) 기본 루트 API
@app.get("/")
def read_root():
    return {"message": "Welcome to Student API!"}

# 2) 학생 정보 조회 API
@app.get("/students/{student_id}")
def get_student(student_id: int, detail: Union[bool, None] = False):
    # 예제용 가짜 데이터
    students = {
        1: {"name": "김민수", "age": 20, "major": "컴퓨터공학"},
        2: {"name": "박지훈", "age": 22, "major": "전자공학"},
        3: {"name": "이서연", "age": 21, "major": "경영학"}
    }

    student = students.get(student_id)
    if not student:
        return {"error": "Student not found"}

    if detail:
        return student  # 모든 정보 반환
    else:
        return {"name": student["name"]}  # 이름만 반환
