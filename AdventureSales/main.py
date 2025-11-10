# main.py 파일 내용 (시각화 CSV 저장 기능 추가)

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import time
import pandas as pd 
# clv_analysis.py에서 정의된 핵심 함수들을 불러옵니다.
from clv_analysis import load_and_prepare_data, calculate_rfm_score, train_and_score_clv_model

# 1. 전역 변수 초기화
clv_df: pd.DataFrame = None
clv_model = None

# 2. 애플리케이션 시작/종료 이벤트 관리 (lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    global clv_df, clv_model
    start_time = time.time()
    print("--- FastAPI 서비스 시작: 데이터 로딩 및 분석 ---")
    
    try:
        # 1. 데이터 로드 및 전처리
        full_df = load_and_prepare_data()
        
        # 2. RFM 및 CLV 점수 계산 및 모델 학습
        # train_and_score_clv_model 함수에서 clv_model.pkl 파일이 생성됩니다.
        rfm_df = calculate_rfm_score(full_df)
        clv_df = train_and_score_clv_model(rfm_df)
        
        # 💡 시각화를 위해 최종 결과를 CSV 파일로 저장하는 코드 추가 💡
        clv_df.to_csv('clv_analysis_results.csv', index=False)
        
        end_time = time.time()
        print(f"✅ CLV 분석 결과 로딩 및 모델 학습 완료. (소요 시간: {end_time - start_time:.2f}초)")
        
    except Exception as e:
        print(f"❌ 데이터 처리/분석 중 오류 발생: {e}")
        # 오류 시 빈 DataFrame을 할당하여 서버가 멈추지 않도록 합니다.
        clv_df = pd.DataFrame(columns=['CustomerKey', 'Predicted_CLV', 'CLV_Score']) 
    
    # 서버 실행
    yield
    
    # 애플리케이션 종료 시 정리 작업 (필요시)
    print("--- FastAPI 서비스 종료 ---")

# 3. FastAPI 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# 4. API 엔드포인트 정의
@app.get("/")
def read_root():
    return {"message": "CLV Prediction Service is running. Use /clv_score/{customer_key} to get CLV."}

@app.get("/clv_score/{customer_key}")
async def get_clv_score(customer_key: int):
    # 전역 변수인 clv_df에서 고객 키를 기준으로 데이터 조회
    if clv_df is None or clv_df.empty:
        raise HTTPException(status_code=503, detail="CLV data is not loaded or processing failed.")
    
    # CustomerKey는 정수형이므로, 일치하는 행을 찾습니다.
    result = clv_df[clv_df['CustomerKey'] == customer_key]
    
    if result.empty:
        raise HTTPException(status_code=404, detail=f"CustomerKey {customer_key} not found.")
    
    # 결과 포맷팅 (첫 번째 행 사용)
    customer_data = result.iloc[0]
    
    return {
        "CustomerKey": int(customer_data['CustomerKey']),
        "Predicted_CLV_USD": round(float(customer_data['Predicted_CLV']), 2),
        "CLV_Score": int(customer_data['CLV_Score'])
    }