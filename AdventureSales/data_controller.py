# data_controller.py

from typing import List
from pydantic import BaseModel, Field
import pandas as pd
from data_model import get_top_100_data, setup_database

# 1. Pydantic 모델 정의: API/UI로 전달할 데이터의 구조를 명확히 합니다.
class TopCustomer(BaseModel):
    """최근 1년 구매액 Top 100 고객의 데이터 구조."""
    rank: int = Field(..., description="고객의 순위 (1~100)")
    customer_key: int = Field(..., description="고객 키 (CustomerKey)")
    customer_name: str = Field(..., description="고객 이름")
    total_spending: float = Field(..., description="최근 1년 총 구매액 (USD)")
    city: str = Field(..., description="고객의 도시")
    country: str = Field(..., description="고객의 국가")


# 2. 컨트롤러 로직
class AdventureController:
    
    def __init__(self):
        # DB 설정을 초기화 시도. (Gradio 앱 시작 전 데이터 준비)
        self.status_message = setup_database()

    def get_db_setup_status(self) -> str:
        """DB 설정 상태 메시지 반환."""
        return self.status_message

    def get_top_100_customers_data(self) -> List[TopCustomer]:
        """
        Model에서 Top 100 데이터를 가져와 Pydantic 모델 리스트로 변환하여 반환합니다.
        """
        df = get_top_100_data()
        
        if df.empty:
            return []

        # Pydantic 모델로 변환
        data_list = []
        for index, row in df.iterrows():
            # 순위는 1부터 시작 (index + 1)
            data_list.append(
                TopCustomer(
                    rank=index + 1,
                    customer_key=int(row['CustomerKey']),
                    customer_name=row['Customer'],
                    total_spending=round(row['Total Spending'], 2),
                    city=row['City'],
                    country=row['Country-Region']
                )
            )
            
        return data_list

    def get_top_100_for_gradio(self):
        """Gradio의 DataFrame 컴포넌트에 맞는 형식(List[List])으로 데이터를 반환합니다."""
        top_customers = self.get_top_100_customers_data()
        
        if not top_customers:
            return pd.DataFrame() # 빈 데이터프레임 반환

        # Pydantic 모델 리스트를 Gradio의 DataFrame에 적합한 Pandas DataFrame으로 변환
        data_for_gradio = [
            [
                customer.rank,
                customer.customer_key,
                customer.customer_name,
                f"${customer.total_spending:,.2f}", # 금액 포맷팅
                customer.city,
                customer.country
            ] 
            for customer in top_customers
        ]
        
        columns = ['순위', '고객 키', '고객 이름', '총 구매액 (USD)', '도시', '국가']
        return pd.DataFrame(data_for_gradio, columns=columns)