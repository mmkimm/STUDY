import csv
import random

# CSV 파일 경로
COURSES_FILE = "courses_data.csv"

# 강의실
ROOMS = ["1215", "1216", "1217", "1418", "1419"]

# 수업 시간 (09:00 ~ 18:00, 1시간 단위)
START_HOUR = 9
END_HOUR = 18

# 요일
DAYS = ["월", "화", "수", "목", "금"]

def load_courses(file_path):
    courses = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            courses.append({
                "과목명": row["교과목명"],
                "교수": row["강좌담당교수"],
                "수업주수": int(row["수업주수"]),
                "학점": int(row["교과목학점"])
            })
    return courses

def schedule_courses(courses):
    schedule = {}
    professor_schedule = {}

    for course in courses:
        assigned = False
        random.shuffle(DAYS)
        random.shuffle(ROOMS)
        for day in DAYS:
            for room in ROOMS:
                start_hour = START_HOUR
                while start_hour + course["학점"] <= END_HOUR:
                    conflict = False
                    for h in range(start_hour, start_hour + course["학점"]):
                        if (day, h, room) in schedule or (day, h, course["교수"]) in professor_schedule:
                            conflict = True
                            break
                    if not conflict:
                        for h in range(start_hour, start_hour + course["학점"]):
                            schedule[(day, h, room)] = course["과목명"]
                            professor_schedule[(day, h, course["교수"])] = course["과목명"]
                        assigned = True
                        break
                    start_hour += 1
                if assigned:
                    break
            if assigned:
                break
        if not assigned:
            print(f"⚠️ {course['과목명']} 배정 실패 - 시간/강의실 부족")
    return schedule

def print_schedule(schedule):
    print("=== 강의 시간표 ===")
    for day in DAYS:
        print(f"\n[{day}]")
        for hour in range(START_HOUR, END_HOUR):
            row = f"{hour}:00 - "
            for room in ROOMS:
                key = (day, hour, room)
                course = schedule.get(key, "")
                row += f"{room}:{course}\t"
            print(row)

def save_schedule_csv(schedule, filename="schedule.csv"):
    """
    schedule 딕셔너리를 CSV로 저장
    CSV 컬럼: 요일, 시간, 강의실, 과목
    """
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["요일", "시간", "강의실", "과목"])  # 헤더
        for (day, hour, room), subject in schedule.items():
            writer.writerow([day, hour, room, subject])
    print(f"✅ 시간표 CSV 저장 완료: {filename}")

if __name__ == "__main__":
    courses = load_courses(COURSES_FILE)
    schedule = schedule_courses(courses)
    print_schedule(schedule)
    save_schedule_csv(schedule)
