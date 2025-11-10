# data_model.py

import pandas as pd
import sqlite3
import datetime as dt

# DB 파일 이름
DB_PATH = 'Adventure.db' 
# Excel 파일 이름 (프로젝트 폴더에 있어야 합니다)
EXCEL_PATH = 'AdventureWorks_Sales.xlsx'
TOP_N = 100 

# Excel 파일의 7개 시트 이름과 DB 테이블 이름 매핑
SHEET_NAMES = {
    'Sales_data': 'sales',
    'Customer_data': 'customer',
    'Product_data': 'product',
    'Date_data': 'date',
    'Reseller_data': 'reseller',
    'Sales Territory_data': 'sales_territory',
    'Sales Order_data': 'sales_order'
}

def setup_database():
    """Excel 파일에서 데이터를 읽어와 DB에 7개 테이블을 저장하고, Top 100 고객 테이블을 생성합니다."""
    try:
        # 1. Excel 파일의 7개 시트 읽기
        data_frames = {}
        for sheet_name, table_name in SHEET_NAMES.items():
            # pandas의 ExcelFile 객체를 사용해 성능 개선
            with pd.ExcelFile(EXCEL_PATH) as xls:
                 data_frames[table_name] = pd.read_excel(xls, sheet_name=sheet_name)
        
        # 2. SQLite DB 연결 및 7개 테이블 저장
        conn = sqlite3.connect(DB_PATH)
        for table_name, df in data_frames.items():
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # 3. Top 100 고객 테이블 계산 및 저장 (수정된 부분)
        sales_df = data_frames['sales']
        date_df = data_frames['date']
        
        # 🚨 수정: CustomerKey가 -1인 데이터 (측정 불가 또는 Not Applicable) 제외 🚨
        sales_df = sales_df[sales_df['CustomerKey'] != -1].copy()

        # 날짜 조인을 위한 전처리
        sales_date_df = pd.merge(sales_df, date_df[['DateKey', 'Date']], 
                                 left_on='OrderDateKey', right_on='DateKey', how='left')
        sales_date_df['OrderDate'] = pd.to_datetime(sales_date_df['Date'])
        
        # 최근 1년 기준일 설정
        PRESENT = sales_date_df['OrderDate'].max()
        ONE_YEAR_AGO = PRESENT - dt.timedelta(days=365)

        # 최근 1년 데이터 필터링
        recent_sales = sales_date_df[sales_date_df['OrderDate'] >= ONE_YEAR_AGO]
        
        # 고객별 총 구매액 계산
        customer_spending = recent_sales.groupby('CustomerKey')['Sales Amount'].sum().reset_index()
        customer_spending.columns = ['CustomerKey', 'Total Spending']
        
        # Top 100 고객 선정
        top_100_customers = customer_spending.nlargest(TOP_N, 'Total Spending')
        
        # customer_df와 조인하여 고객 상세 정보 추가
        customer_df = data_frames['customer'][['CustomerKey', 'Customer', 'City', 'Country-Region']]
        top_100_details = pd.merge(top_100_customers, customer_df, 
                                   on='CustomerKey', how='left')
        
        # 'top_100_customers'라는 별도 테이블로 저장
        top_100_details.to_sql('top_100_customers', conn, if_exists='replace', index=False)
        
        conn.close()
        return f"✅ DB 설정 및 Top {TOP_N} 고객 테이블 저장이 완료되었습니다. (Adventure.db)"
    
    except FileNotFoundError:
        return f"❌ 오류: '{EXCEL_PATH}' 파일을 찾을 수 없습니다. 프로젝트 폴더에 넣어주세요."
    except Exception as e:
        return f"❌ DB 설정 중 오류 발생: {e}"


def get_top_100_data():
    """DB에서 Top 100 고객 데이터를 불러옵니다."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Top 100 고객 테이블 로드
        top_100_df = pd.read_sql('SELECT * FROM top_100_customers ORDER BY "Total Spending" DESC', conn)
        conn.close()
        return top_100_df
    except Exception as e:
        conn.close()
        print(f"Top 100 데이터 로드 오류: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    # 이 파일을 직접 실행하여 DB를 설정할 수 있습니다.
    print(setup_database())