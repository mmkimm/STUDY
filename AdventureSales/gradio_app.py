# gradio_app.py 파일 내용 (AttributeError를 해결한 최종 버전)

import gradio as gr
from data_controller import AdventureController
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# io 모듈은 더 이상 필요하지 않습니다.
# import io 

# 컨트롤러 인스턴스 생성 (DB 설정 및 Top 100 계산 완료)
controller = AdventureController()

# 1. 시각화 함수: Matplotlib 그래프를 PNG 파일로 저장하고 파일 경로를 반환
def plot_top_10_spending(df: pd.DataFrame):
    """Top 10 고객의 구매액 막대 그래프를 생성하고 파일 경로를 반환합니다."""
    
    if df.empty:
        return None 

    # 금액 포맷팅을 풀기 위해 (데이터프레임의 '총 구매액 (USD)' 컬럼은 문자열로 포맷되어 있음)
    df['Spending_Clean'] = df['총 구매액 (USD)'].str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
    top_10 = df.head(10).sort_values(by='Spending_Clean', ascending=True)

    # 그래프 생성
    plt.figure(figsize=(10, 6))
    # FutureWarning 경고를 피하기 위해 hue를 명시적으로 설정합니다.
    sns.barplot(x='Spending_Clean', y='고객 이름', data=top_10, palette='viridis', hue='고객 이름', legend=False) 
    plt.title('Top 10 Customers by Recent Total Spending', fontsize=16)
    plt.xlabel('Total Spending (USD)', fontsize=12)
    plt.ylabel('Customer Name', fontsize=12)
    plt.tight_layout()

    # 🚨 수정된 부분: 이미지를 파일로 저장하고 파일 경로를 반환합니다.
    PLOT_FILE_NAME = "top_10_spending_graph.png"
    plt.savefig(PLOT_FILE_NAME, format='png')
    plt.close() # 메모리 누수 방지
    
    return PLOT_FILE_NAME # 파일 경로 (문자열) 반환


# 2. 메인 Gradio UI 로직
def run_dashboard():
    
    # 컨트롤러에서 Top 100 데이터 로드
    top_100_df = controller.get_top_100_for_gradio()
    db_status = controller.get_db_setup_status()
    
    # UI 구성
    with gr.Blocks(title="AdventureWorks Sales Dashboard (MVC)") as demo:
        gr.Markdown(
            f"""
            # 📊 AdventureWorks Sales Dashboard (MVC + Gradio)
            ### 🎯 **과제 목표: MVC 패턴 및 Pydantic을 적용한 Gradio UI 구성**
            **DB 설정 상태:** {db_status}
            ---
            """
        )
        
        # 탭 구성
        with gr.Tabs():
            
            with gr.TabItem("💰 최근 1년 Top 100 고객"):
                gr.Markdown("## 최근 1년간 구매액이 높은 Top 100 고객 목록")
                
                # Top 100 고객 테이블 (데이터프레임 컴포넌트)
                gr.DataFrame(
                    value=top_100_df,
                    headers=['순위', '고객 키', '고객 이름', '총 구매액 (USD)', '도시', '국가'],
                    row_count=10, 
                    col_count=(6, 'fixed'),
                    interactive=False
                )
            
            with gr.TabItem("📈 Top 10 시각화"):
                gr.Markdown("## Top 10 고객 구매액 시각화")
                
                if not top_100_df.empty:
                    # value=에 파일 경로 (문자열)가 전달되도록 수정되었습니다.
                    gr.Image(
                        value=plot_top_10_spending(top_100_df),
                        label="Top 10 Customers Spending Graph",
                        interactive=False
                    )
                else:
                    gr.Markdown("데이터 로드에 실패하여 시각화를 표시할 수 없습니다.")
                    

    # Gradio 애플리케이션 실행
    demo.launch(server_name="0.0.0.0", server_port=8000)

if __name__ == "__main__":
    run_dashboard()