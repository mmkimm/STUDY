# main.py (최종 버전: 사용자 친화적 에러 출력 및 이미지 경로 수정)

from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import uvicorn
from scheduler import run_scheduler 
import traceback # 디버깅을 위해 traceback 모듈 사용

app = FastAPI()

# 2. 업로드된 파일을 임시 저장할 디렉토리 설정
UPLOAD_DIR = "uploaded_csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 📌 3. 정적 파일(이미지) 제공 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 필수 헤더 목록 (에러 메시지 출력용)
REQUIRED_HEADERS_STR = "교과목명, 강좌담당교수, 수업주수, 교과목학점, 개설학년, 개설학과, 교과목코드, 수강인원"


# =========================================================================
# 💡 1. 메인 페이지: 파일 업로드 폼 제공
# =========================================================================
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>강의실 배정 프로그램</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0 0 0 / 10%); }}
            h1 {{ color: #333; text-align: center; }}
            p {{ text-align: center; color: #555; }}
            form {{ text-align: center; margin-top: 30px; padding: 20px; border: 1px dashed #ccc; border-radius: 5px; }}
            input[type="file"] {{ padding: 10px; margin: 10px 0; display: block; width: 80%; margin: 10px auto; }}
            input[type="submit"] {{ 
                background-color: #4CAF50; color: white; padding: 10px 20px; 
                border: none; border-radius: 5px; cursor: pointer; font-size: 16px; 
                transition: background-color 0.3s;
            }}
            input[type="submit"]:hover {{ background-color: #45a049; }}
            
            /* 이미지 스타일 */
            .csv-image-container {{ 
                margin-top: 25px; 
                margin-bottom: 30px; 
                text-align: center; 
                padding: 15px; 
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f8f8f8;
            }}
            .csv-image-container img {{
                max-width: 100%;
                height: auto;
                border: 2px solid #555;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏛️ 강의실 배정 프로그램 🗓️</h1>
            <p>강의실 배정을 시작하기 위해 CSV 파일을 업로드 해 주세요. (헤더 양식이 **정확히 일치해야 합니다.**)</p>
            
            <div class="csv-image-container">
                <p style="font-weight: bold; margin-bottom: 10px; color: #333;">[필수 CSV 파일 양식 (헤더 행)]</p>
                <p style="font-family: monospace; font-weight: bold; background-color: #fff; padding: 5px; border-radius: 3px; border: 1px solid #ccc;">{REQUIRED_HEADERS_STR}</p>
                <img src="/static/csv_header_example.png" alt="CSV 파일 필수 헤더 양식" title="CSV 파일의 첫 번째 줄은 이와 같아야 합니다.">
            </div>
            
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".csv" required>
                <input type="submit" value="▶️ 파일 업로드 및 배정 시작">
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# =========================================================================
# 💡 2. 파일 업로드 및 스케줄링 실행 라우터 (개선된 에러 처리)
# =========================================================================
@app.post("/upload", response_class=HTMLResponse)
async def upload_file_and_run_scheduler(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        await file.close()
        return HTMLResponse(content="<h1>오류: CSV 파일만 업로드할 수 있습니다.</h1>")
    
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    # 비동기 파일 저장 로직
    try:
        contents = await file.read() 
        with open(file_location, "wb") as buffer:
            buffer.write(contents)
            
    except Exception as e:
        return HTMLResponse(content=f"<h1>파일 저장 중 오류 발생: {e}</h1>")
    finally:
        await file.close()

    # 4. 저장된 파일 경로를 사용하여 스케줄러 실행
    try:
        schedule_html = run_scheduler(file_location) 
    
    # 📌 [수정] scheduler.py에서 발생시킨 ValueError (헤더 오류)를 사용자 친화적으로 출력
    except ValueError as ve:
        error_message = str(ve)
        
        # '헤더 오류:'가 포함된 경우 (scheduler.py에서 발생시킨 오류)
        if error_message.startswith("헤더 오류:"):
            title = "⚠️ 필수 파일 양식 오류 발생!"
            guide_message = f"""
                <p style="font-size: 1.1em; font-weight: bold; color: #d84315;">{error_message}</p>
                <hr style="border-top: 1px solid #ffab91;">
                <p>업로드하신 CSV 파일의 첫 번째 행(헤더)을 확인해 주세요.</p>
                <p>필수 헤더 양식: <span style="font-family: monospace; font-weight: bold; background-color: #fff; padding: 2px 4px; border-radius: 3px;">{REQUIRED_HEADERS_STR}</span></p>
            """
        else:
            # 기타 ValueError (데이터 로드 실패 등)
            title = "⚠️ 스케줄러 데이터 처리 오류 발생"
            guide_message = f"""
                <p style="font-size: 1.1em; font-weight: bold; color: #d84315;">{error_message}</p>
                <hr style="border-top: 1px solid #ffab91;">
                <p>CSV 파일 내용(특히 숫자 필드)이나 파일의 인코딩(CP949 또는 UTF-8)을 확인해 주세요.</p>
            """

        return HTMLResponse(content=f"""
            <div style="max-width: 800px; margin: 50px auto; padding: 20px; border: 3px solid #ff5722; border-radius: 8px; background-color: #ffe0b2; color: #d84315; font-family: Arial, sans-serif;">
                <h1 style="color: #d84315;">{title}</h1>
                {guide_message}
                <a href="/" style="display: block; margin-top: 20px; text-align: center; color: #d84315; text-decoration: underline;">◀️ 파일 재업로드 페이지로 돌아가기</a>
            </div>
        """)
        
    except Exception as e:
        # 기타 모든 오류는 이전처럼 상세 traceback 출력
        error_trace = traceback.format_exc()
        return HTMLResponse(content=f"""
            <h1>스케줄러 실행 중 예상치 못한 오류 발생: {e}</h1>
            <p>파일 경로 확인: **{file_location}**</p>
            <pre style="white-space: pre-wrap; word-wrap: break-word; background-color: #eee; padding: 10px; border-radius: 5px;">
                {error_trace}
            </pre>
        """)

    # 5. 결과 HTML 반환
    return HTMLResponse(content=schedule_html)


# =========================================================================
# 💡 서버 실행
# =========================================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)