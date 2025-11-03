# scheduler.py (최종 버전: 모든 오류 방어 및 인코딩 자동 시도 적용)

import csv
import random
from typing import List, Dict, Tuple, Any

# =========================================================================
# ⚙️ 설정 상수 (Configuration Constants)
# =========================================================================

ROOMS = ["1215", "1216", "1217", "1418", "R_EXTRA"] 
START_HOUR = 9
END_HOUR = 18
DAYS = ["월", "화", "수", "목", "금"]

# 📌 배정 단위 정의
SW_CLASSES = ["SW-1A", "SW-1B", "SW-2A", "SW-2B", "SW-3A", "SW-3B", "SW-4"]
BD_CLASSES = ["BD-1", "BD-2", "BD-3"] 
ALL_CLASSES = SW_CLASSES + BD_CLASSES

# 📌 프로그램이 필수적으로 사용할 키 목록 정의
REQUIRED_KEYS = ["교과목명", "강좌담당교수", "수업주수", "교과목학점", "개설학년", "개설학과", "교과목코드", "수강인원"]

# 🎨 학년별 색상 매핑
COLOR_MAP = {
    "SW-1": "#ffe0e6", "SW-2": "#fff9c4", "SW-3": "#e3f2fd", "SW-4": "#e8f5e9",  
    "BD-1": "#ffe0e6", "BD-2": "#ffb6c1", "BD-3": "#d8bfd8", 
    "HEADER_MAIN": "#90caf9", "HEADER_TIME": "#bbdefb", "TEXT": "#000000",
}

# =========================================================================
# 📚 데이터 로드 함수 (load_courses) - 최종 인코딩/데이터 오류 방어
# =========================================================================

def load_courses(file_path: str) -> List[Dict[str, Any]]:
    courses = []
    
    encoding_list = ['utf-8', 'cp949', 'latin-1'] # 시도할 인코딩 목록
    reader = None
    f = None # f 변수를 명시적으로 None으로 초기화
    
    # 📌 1. 파일 열기 시도 (인코딩 방어 로직)
    for encoding in encoding_list:
        try:
            # newline=''은 CSV 파일 읽기 시 줄바꿈 문제 방지에 유용
            f = open(file_path, "r", encoding=encoding, newline='') 
            reader = csv.DictReader(f)
            # 성공적으로 열렸으면 루프 탈출
            break 
        except UnicodeDecodeError:
            if f:
                f.close() # 실패했으면 파일 핸들 닫고 다음 인코딩 시도
                f = None
            continue
        except FileNotFoundError:
            # 파일이 없으면 즉시 오류 발생
            raise 

    if reader is None:
        raise ValueError("파일 인코딩 오류: UTF-8, CP949, Latin-1 인코딩으로 파일 내용을 읽을 수 없습니다. 파일을 확인해주세요.")
    
    # 파일을 닫는 로직은 데이터 처리 후에 실행
    try:
        # 📌 2. 헤더 검사 및 오류 발생
        actual_headers = set(reader.fieldnames) if reader.fieldnames else set()
        required_keys = set(REQUIRED_KEYS)
        
        missing_keys = required_keys - actual_headers
        
        if missing_keys:
            raise ValueError(f"헤더 오류: 다음 필수 헤더가 누락되었거나 이름이 잘못되었습니다. -> **{', '.join(sorted(missing_keys))}**")

        course_map = {} 
        
        # 📌 3. 데이터 처리 및 정제
        for row in reader:
            try:
                # 4가지 숫자 필드 모두 공백 제거 및 숫자 유효성 검사 적용
                
                # 3-1. 교과목학점 (필요시간)
                credits_str = row.get("교과목학점", "0").strip()
                credits = int(credits_str) if credits_str.isdigit() else 0
                
                # 3-2. 개설학년
                grade_str = row.get("개설학년", "0").strip()
                grade = int(grade_str) if grade_str.isdigit() else 0
                
                # 3-3. 수강인원
                capacity_str = row.get("수강인원", "0").strip()
                capacity = int(capacity_str) if capacity_str.isdigit() else 0
                
                # 3-4. 수업주수
                weeks_str = row.get("수업주수", "0").strip()
                weeks = int(weeks_str) if weeks_str.isdigit() else 0
                
                
                # 필수 데이터 (학점/학년/수강인원)가 0이거나 유효하지 않으면 이 강의는 건너뜀
                if credits == 0 or grade == 0 or capacity == 0:
                    continue 
                
                # 고유 ID 생성 (강좌담당교수 사용)
                course_id = f"{row['교과목명']}_{row['강좌담당교수']}_{capacity}"
                
                # 학과명 정규화 (소프트웨어융합과(2022) 등을 처리)
                dept = row["개설학과"].strip()
                
                course_map[course_id] = {
                    "과목명": row["교과목명"],
                    "교수": row["강좌담당교수"],
                    "필요시간": credits, 
                    "학년": grade,      
                    "학과": dept, # 정규화된 학과명 사용
                    "주수": weeks,
                }
            except ValueError:
                # 데이터 처리 중 기타 오류 발생 시 해당 행 건너뛰기
                pass
        
        # 📌 4. 데이터 그룹화 및 최종 코스 목록 생성
        final_courses = []
        course_counts = {}
        
        valid_sw_depts = ["소프트웨어융합과", "코딩전공", "소프트웨어융합학과", "소프트웨어융합과(2022)"]
        
        for course_id, course in course_map.items():
            key = (course['과목명'], course['교수'], course['학과'])
            course_counts[key] = course_counts.get(key, 0) + 1
            count = course_counts[key]
            grade = course['학년']
            
            if course['학과'] in valid_sw_depts:
                if grade == 4:
                    class_unit = "SW-4"
                elif grade in [1, 2, 3]:
                    # 1학년, 2학년, 3학년 분반 로직 (A, B)
                    if count == 1:
                        class_unit = f"SW-{grade}A"
                    elif count >= 2:
                        class_unit = f"SW-{grade}B"
                    else: 
                        continue
                else:
                    continue
                
            elif course['학과'] == "빅데이터과":
                if 1 <= grade <= 3:
                    class_unit = f"BD-{grade}"
                else:
                    continue
            else:
                continue # 알 수 없는 학과는 건너뜀
                
            course['배정_단위'] = class_unit
            course['id'] = course_id
            final_courses.append(course)
        
        unique_courses = []
        seen_ids = set()
        for course in final_courses:
            if course['id'] not in seen_ids:
                unique_courses.append(course)
                seen_ids.add(course['id'])
        
        return unique_courses
        
    finally:
        # 파일이 열려있다면 반드시 닫음 (f가 None이 아닐 경우)
        if f:
            f.close()


# =========================================================================
# ⚙️ 시간표 배정 함수 (schedule_courses) 
# =========================================================================

def schedule_courses(courses: List[Dict[str, Any]]) -> Tuple[Dict[Tuple[str, int, str], Tuple[str, str, str]], List[str]]:
    room_schedule = {} 
    professor_schedule = {}
    class_schedule = {}
    unassigned_courses = []

    courses.sort(key=lambda x: x['필요시간']) 
    random.shuffle(courses)

    for course in courses:
        assigned = False
        required_hours = course["필요시간"]
        room_priority = sorted(ROOMS, key=lambda r: 1 if r == "R_EXTRA" else 0)
        class_unit = course["배정_단위"]

        for day in random.sample(DAYS, len(DAYS)):
            for room in room_priority:
                start_hour = START_HOUR
                while start_hour + required_hours <= END_HOUR:
                    
                    conflict = False
                    
                    for h in range(start_hour, start_hour + required_hours):
                        if (day, h, room) in room_schedule:
                            conflict = True
                            break
                        if (day, h, course["교수"]) in professor_schedule:
                            conflict = True
                            break
                        if (day, h, class_unit) in class_schedule:
                            conflict = True
                            break
                            
                    if not conflict:
                        for h in range(start_hour, start_hour + required_hours):
                            room_schedule[(day, h, room)] = (course["과목명"], class_unit, course["교수"])
                            professor_schedule[(day, h, course["교수"])] = course["과목명"]
                            class_schedule[(day, h, class_unit)] = course["과목명"]
                        
                        assigned = True
                        break 
                    
                    start_hour += 1 

                if assigned:
                    break
            if assigned:
                break
        
        if not assigned:
            unassigned_courses.append(course['과목명'] + f" ({class_unit})")
            
    return room_schedule, unassigned_courses

# =========================================================================
# 🎨 HTML 시각화 함수 (generate_full_html_schedule) 
# =========================================================================

def generate_full_html_schedule(schedule: Dict[Tuple[str, int, str], Tuple[str, str, str]], unassigned_courses: List[str]) -> str:
    
    TEXT_COLOR = COLOR_MAP["TEXT"] 
    BG_COLOR_MAIN_HEADER = COLOR_MAP["HEADER_MAIN"]
    BG_COLOR_TIME_HEADER = COLOR_MAP["HEADER_TIME"]
    BG_COLOR_EMPTY = "#ffffff" 
    
    THICK_BORDER = "2px solid #555"
    THIN_BORDER = "1px solid #ddd"

    def get_course_bg_color(class_unit: str) -> str:
        key = class_unit[:4] if class_unit.startswith("SW-") and (class_unit.endswith('A') or class_unit.endswith('B')) else class_unit
        key = key[:4] if key.startswith("BD-") else key 
        return COLOR_MAP.get(key, BG_COLOR_EMPTY)

    
    full_html = f"<h2 style='text-align: center; color: {TEXT_COLOR};'>🏛️ 강의실 배정 결과 시간표 (학과 통합/분리) 🗓️</h2>"
    
    if unassigned_courses:
        full_html += f"<div style='border: 2px solid red; padding: 10px; margin: 10px 0; background-color: #ffe0e0; color: #cc0000; font-weight: bold;'>⚠️ 배정 실패 과목: {', '.join(unassigned_courses)} - 시간/강의실/교수 충돌</div>"

    
    table_style = f"width: 100%; border-collapse: collapse; text-align: center; font-size: 13px; color: {TEXT_COLOR}; table-layout: fixed;"
    header_style = f"padding: 8px; background-color: {BG_COLOR_MAIN_HEADER}; font-weight: bold; border: {THIN_BORDER}; border-bottom: {THICK_BORDER}; color: {TEXT_COLOR};"
    time_header_style = f"padding: 5px; font-weight: bold; background-color: {BG_COLOR_TIME_HEADER}; border: {THIN_BORDER}; color: {TEXT_COLOR};"
    cell_style = f"padding: 5px; height: 60px; border: {THIN_BORDER}; vertical-align: middle;"

    full_html += f"<table border='0' style='{table_style}'>"
    
    # 메인 헤더 (요일별 시간)
    full_html += "<thead><tr>"
    full_html += f"<th rowspan='2' colspan='2' style='{header_style}'>학과/학년/반</th>" 
    
    for i, day in enumerate(DAYS):
        day_header_style = header_style
        if i < len(DAYS) - 1:
            day_header_style += f" border-right: {THICK_BORDER};"
        
        full_html += f"<th colspan='{END_HOUR - START_HOUR}' style='{day_header_style}'>{day}</th>"
    full_html += "</tr>"
    
    # 시간 헤더
    full_html += "<tr>"
    for day_index, _ in enumerate(DAYS):
        for hour_index, hour in enumerate(range(START_HOUR, END_HOUR)):
            time_style = time_header_style
            if hour_index == END_HOUR - START_HOUR - 1 and day_index < len(DAYS) - 1:
                time_style += f" border-right: {THICK_BORDER};"

            full_html += f"<th style='{time_style}'>{hour}:00</th>"
    full_html += "</tr></thead>"
    
    full_html += "<tbody>"
    
    # 📌 1. SW 통합 그룹 출력 (소프트웨어융합과, 코딩전공)
    full_html += f"<tr><td colspan='{2 + len(DAYS) * (END_HOUR - START_HOUR)}' style='{header_style}; background-color: #b3e5fc; border-top: {THICK_BORDER};'>⭐ 소프트웨어 통합 학과 시간표 (소프트웨어융합과/코딩전공) ⭐</td></tr>"
    
    for i, class_unit in enumerate(SW_CLASSES):
        grade_base_color = get_course_bg_color(class_unit)
        is_last_in_grade = (class_unit.endswith('B') and class_unit != 'SW-3B') or (class_unit == 'SW-4') or (class_unit == 'SW-3B')
        
        full_html += "<tr>"
        
        grade_num = class_unit[3]
        
        grade_header_style = f"border: {THIN_BORDER}; border-right: {THIN_BORDER}; background-color: {COLOR_MAP['HEADER_TIME']}; color: {TEXT_COLOR}; font-weight: bold;"
        if is_last_in_grade:
             grade_header_style += f" border-bottom: {THICK_BORDER};"
        
        if class_unit.endswith('A'):
            full_html += f"<td rowspan='2' style='{grade_header_style}'>{grade_num}학년</td>"
        elif class_unit == 'SW-4':
            full_html += f"<td colspan='2' style='{grade_header_style}'>{grade_num}학년</td>"
        
        if class_unit.endswith('A') or class_unit.endswith('B'):
            class_display = class_unit[-1] + '반'
            ban_header_style = f"border: {THIN_BORDER}; background-color: {BG_COLOR_TIME_HEADER}; font-size: 11px; color: {TEXT_COLOR}; font-weight: bold;"
            if is_last_in_grade:
                ban_header_style += f" border-bottom: {THICK_BORDER};"
            full_html += f"<td style='{ban_header_style}'>{class_display}</td>"
        
        for day_index, day in enumerate(DAYS):
            for hour_index, hour in enumerate(range(START_HOUR, END_HOUR)):
                cell_content = ""
                
                for room in ROOMS:
                    key = (day, hour, room)
                    if key in schedule:
                        course_name, unit, professor_name = schedule[key]
                        
                        if unit == class_unit:
                            cell_content = (
                                f"<div style='font-weight: bold; color: {TEXT_COLOR};'>{course_name}</div>"
                                f"<div style='font-size: 11px; color: {TEXT_COLOR};'>({professor_name})</div>"
                                f"<div style='font-size: 10px; color: #333; margin-top: 3px;'>{room}</div>" 
                            )
                            break

                final_cell_style = cell_style
                if cell_content:
                    final_cell_style += f" background-color: {grade_base_color}; font-weight: 500;"
                else:
                    final_cell_style += f" background-color: {BG_COLOR_EMPTY};"
                
                if hour_index == END_HOUR - START_HOUR - 1 and day_index < len(DAYS) - 1:
                    final_cell_style += f" border-right: {THICK_BORDER};"
                
                if is_last_in_grade:
                    final_cell_style += f" border-bottom: {THICK_BORDER};"

                full_html += f"<td style='{final_cell_style}'>{cell_content}</td>"
                
        full_html += "</tr>"

    # 📌 2. BD 독립 그룹 출력 (빅데이터과)
    full_html += f"<tr><td colspan='{2 + len(DAYS) * (END_HOUR - START_HOUR)}' style='{header_style}; background-color: #b3e5fc; border-top: {THICK_BORDER};'>⭐ 빅데이터과 독립 시간표 ⭐</td></tr>"

    for i, class_unit in enumerate(BD_CLASSES):
        grade_base_color = get_course_bg_color(class_unit)
        is_last_in_bd = (i == len(BD_CLASSES) - 1)
        
        full_html += "<tr>"
        
        grade_num = class_unit[3]
        
        bd_header_style = f"border: {THIN_BORDER}; background-color: {COLOR_MAP['HEADER_TIME']}; color: {TEXT_COLOR}; font-weight: bold;"
        if is_last_in_bd:
            bd_header_style += f" border-bottom: {THICK_BORDER};"
            
        full_html += f"<td colspan='2' style='{bd_header_style}'>{grade_num}학년</td>"

        for day_index, day in enumerate(DAYS):
            for hour_index, hour in enumerate(range(START_HOUR, END_HOUR)):
                cell_content = ""
                
                for room in ROOMS:
                    key = (day, hour, room)
                    if key in schedule:
                        course_name, unit, professor_name = schedule[key]
                        
                        if unit == class_unit:
                            cell_content = (
                                f"<div style='font-weight: bold; color: {TEXT_COLOR};'>{course_name}</div>"
                                f"<div style='font-size: 11px; color: {TEXT_COLOR};'>({professor_name})</div>"
                                f"<div style='font-size: 10px; color: #333; margin-top: 3px;'>{room}</div>"
                            )
                            break

                final_cell_style = cell_style
                if cell_content:
                    final_cell_style += f" background-color: {grade_base_color}; font-weight: 500;"
                else:
                    final_cell_style += f" background-color: {BG_COLOR_EMPTY};"

                if hour_index == END_HOUR - START_HOUR - 1 and day_index < len(DAYS) - 1:
                    final_cell_style += f" border-right: {THICK_BORDER};"
                
                if is_last_in_bd:
                    final_cell_style += f" border-bottom: {THICK_BORDER};"
                
                full_html += f"<td style='{final_cell_style}'>{cell_content}</td>"
                
        full_html += "</tr>"

    full_html += "</tbody></table>"
    
    # 5. 강의실 사용 현황 (R_EXTRA)
    full_html += f"<h3 style='margin-top: 30px; color: {TEXT_COLOR};'>⚠️ 임시 할당 강의실 사용 현황 (R_EXTRA)</h3>"
    used_extra_room = False
    extra_room_details = ""
    for (day, hour, room), (course, unit, professor) in schedule.items():
        if room == "R_EXTRA":
            extra_room_details += f"<li>{day} {hour}:00 ({unit}, {professor}): **{course}**</li>"
            used_extra_room = True
            
    if used_extra_room:
        full_html += f"<ul style='color: #cc0000; font-weight: bold;'>{extra_room_details}</ul>"
    else:
        full_html += "<p style='color: green;'>✅ 추가 강의실 (R_EXTRA)는 사용되지 않았습니다.</p>"
        
    return full_html


# =========================================================================
# 🚀 메인 스케줄러 실행 함수 (run_scheduler)
# =========================================================================
def run_scheduler(file_path: str) -> str:
    """
    주요 실행 함수. CSV 파일 경로를 받아 스케줄링을 실행하고 HTML을 반환합니다.
    """
    
    try:
        courses = load_courses(file_path)
    except ValueError as e:
        # load_courses에서 발생한 헤더/인코딩 오류를 그대로 전달
        return f"<div style='border: 2px solid red; padding: 20px; background-color: #ffe0e0; color: #cc0000; font-weight: bold;'>❌ 데이터 로드 실패: {e}</div>"
    except Exception:
        # 기타 알 수 없는 오류
        return f"<div style='border: 2px solid red; padding: 20px; background-color: #ffe0e0; color: #cc0000; font-weight: bold;'>❌ 알 수 없는 오류가 발생했습니다. 파일 내용을 다시 한번 확인해주세요.</div>"


    if not courses:
        # 데이터가 필터링 등으로 인해 완전히 비어버린 경우
        return f"<div style='border: 2px solid orange; padding: 20px; background-color: #fff3e0; color: #ff9800; font-weight: bold;'>⚠️ 경고: 파일에서 유효한 강의 데이터를 찾지 못했습니다. CSV 파일의 **개설학년, 교과목학점, 수강인원** 필드가 숫자로 채워져 있는지 확인해주세요.</div>"
    
    schedule, unassigned = schedule_courses(courses)
    
    html_output = generate_full_html_schedule(schedule, unassigned)
    
    return html_output