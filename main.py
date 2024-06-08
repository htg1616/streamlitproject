import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from ing_theme_matplotlib import mpl_style

#matplotlib 스타일 설정
mpl_style(dark=True)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def main_information():
    # ETF 이름, 시작, 종료 날짜 입력
    with st.form("maininfo"):
        ticker = st.text_input('ETF 또는 주식의 종목코드를 입력하세요', 'SPY')
        start = pd.to_datetime(st.date_input("시작 날짜: ", value=pd.to_datetime("2010-01-01")))
        end = pd.to_datetime(st.date_input("종료 날짜: ", value=pd.to_datetime("2024-01-01")))
        submitted = st.form_submit_button("선택 완료")

    # yfinance로 ETF 데이터 가져오기
    data = st.session_state['data'] = yf.download(ticker, start=start, end=end)
    # 주어진 날짜 이후의 가장 가까운 거래일 찾기
    idx_after = data.index.searchsorted(start, side='left')
    # 초기 및, 마지막 주가
    st.session_state['initialClose'] = data['Close'][idx_after]
    st.session_state['finalClose'] = data['Close'].asof(end)
    return (ticker, start, end, data)

def graph():
    ticker = st.text_input('주식 종목을 입력하세요', value='SPY')
    st.write('기간을 입력하세요')
    start = st.date_input('시작 날자: ', value=pd.to_datetime("2010-01-01"))
    end = st.date_input('종료 날자: ', value=pd.to_datetime("2024-01-01"))
    data = yf.download(ticker, start=start, end=end)

    st_graph_col1, st_graph_col2 = st.columns([7, 3])
    with st_graph_col1:
        fig1, ax1 = plt.subplots()  # 새로운 figure 생성
        ax1.plot(data.index, data['Close'], label=ticker)
        ax1.set_title(f'{ticker} 종가 추이')
        ax1.set_xlabel('날짜')
        ax1.set_ylabel('가격')
        ax1.legend()
        st.pyplot(fig1)

    with st_graph_col2:
        one_date = st.date_input(label='언제 주가를 알려줄까?', value=start, min_value=start, max_value=end)
        st.caption('사이드바에서 입력한 시작 날짜와 종료 날짜 사이 값으로 입력해주세요')
        if start <= one_date <= end:
            if one_date in data.index:
                st.write(data.loc[pd.to_datetime(one_date)]) #todo : 표로 바꾸기, 안됨 ㅅㅂ
            else:
                st.write('휴장일 날짜이거나, 당시 없던 종목입니다.')
        else:
            st.error("데이터가 없거나 입력 정보가 잘못되었습니다. 다시 확인해주세요.")

def add_ticker_portfolio(ticker):
    if not ticker in st.session_state['portfolio']
def portfolio(): #todo:테스트 하기
    with st.form("portfolio_form"):
        st.session_state['portfolio'] = {}
        # 포트폴리오 이름 입력
        name = st.text_input("포트폴리오 이름을 입력하세요.", key="portfolio_name")

        # 종목과 비중 입력
        ticker = st.text_input("추가할 종목 이름을 입력하세요.", key="stock_name")
        weight = st.number_input("종목 비중을 입력하세요. (단위: %)", min_value=0.0, max_value=100.0, step=0.1, key="stock_weight")

        # 종목 추가 버튼
        add_button = st.form_submit_button("종목 추가하기", on_click=)

        # 종목이 추가될 때 session_state에 저장하고 multiselect에 표시
        if add_button:
            if not ticker in portfolio.keys():
                st.session_state['portfolio']['ticker'] = weight
            else:
                portfolio[ticker] += weight

        # multiselect로 추가된 종목들을 보여주기
        st.write(portfolio) #todo

        # 포트폴리오 제출
        submit_button = st.form_submit_button("포트폴리오 제출")
        if submit_button:
            if name in st.session_state['portfolio']:
                st.error("이미 존재하는 포트폴리오 이름입니다. 다른 이름을 사용해주세요.")
            else:
                st.session_state['portfolio'][name] = portfolio
                st.success(f"'{name}' 포트폴리오가 성공적으로 추가되었습니다.")

def compare(): #todo:포토폴리오 기능 미완
    if 'portfoilo' in st.session_state:
        selected_portfolio = st.multiselect(st.session_state['portfolio'].keys())
    else:
        selected_portfolio = []
    start = st.session_state['start'] if 'start' in st.session_state else pd.to_datetime("2010-01-01")
    end = st.session_state['end'] if 'end' in st.session_state else pd.to_datetime("2024-01-01")
    selected_tickers = st.text_input(f'비교할 ETF 또는 주식의 종목코드를 입력하세요', 'QQQ' if ticker == 'SPY' else 'SPY').split()
    compare_tickers = selected_portfolio + selected_tickers

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    for compare_ticker in compare_tickers:
        compare_data = yf.download(compare_ticker, start=start, end=end)
        # 주어진 날짜 이후의 가장 가까운 거래일 찾기
        compare_idx_after = compare_data.index.searchsorted(start, side='left')
        compare_initialClose = compare_data['Close'][compare_idx_after]
        compare_data['relative_Close'] = compare_data['Close']/compare_initialClose
        ax1.plot(compare_data.index, compare_data['Close'], label=compare_ticker)
        ax2.plot(compare_data.index, compare_data['relative_Close'], label=compare_ticker)

    ax1.legend()
    ax2.legend()
    ax1.set_title(f'{", ".join(compare_tickers)} 종가 비교')
    ax2.set_title(f'{", ".join(compare_tickers)} 종가 추이 비교')

    fig.tight_layout()
    st.pyplot(fig)

def backtest(ticker, start, end, data):
    investment_select = st.radio('투자 방법을 선택하세요', ('일회성 투자', '적금형 투자'))
    st.divider()

    if investment_select:
        backtest_col1, backtest_col2 = st.columns(2, gap='medium')

    if investment_select == '일회성 투자':
        start_money = backtest_col1.number_input('투자할 금액을 입력하세요', value=1000, step=10, placeholder='만원 단위로 입력하세요')
        if start_money:
            end_money = round(start_money * data['Close'].iloc[-1] / data['Close'].iloc[0])
            backtest_col2.markdown(f"## 최종 금액: {end_money} 원")

    elif investment_select == '적금형 투자':
        month_money = backtest_col1.number_input('매월 투자할 금액을 입력하세요', value=100, step=10, placeholder='만원 단위로 입력하세요')
        if month_money:
            # 월별 투자 금액 계산
            monthly_investments = pd.DataFrame(index=pd.date_range(start=start, end=end, freq='MS')) # MS is month start frequency
            monthly_investments['Investment'] = month_money
            monthly_investments['Total Investment'] = monthly_investments['Investment'].cumsum()

            # 월별 총 주식수 계산
            monthly_investments['Close'] = data['Close'].reindex(monthly_investments.index, method='ffill')  # Fill forward missing values
            monthly_investments['Units'] = monthly_investments['Investment'] / monthly_investments['Close']
            monthly_investments['Total Units'] = monthly_investments['Units'].cumsum()

            #월별 총 금액, 수익률 계산
            monthly_investments['Total Value'] = monthly_investments['Total Units'] * monthly_investments['Close']
            monthly_investments['Total ROI'] = (monthly_investments['Total Value'] / monthly_investments['Total Investment'] - 1) * 100

            final_value = round(monthly_investments['Total Value'].iloc[-1])
            final_investment = round(monthly_investments['Total Investment'].iloc[-1])
            final_ROI = monthly_investments['Total ROI'].iloc[-1]

            backtest_col2.write(f"투자 기간 : {len(monthly_investments)}월")
            backtest_col2.write(f"최종 금액 : {final_value} 만원")
            backtest_col2.write(f"총 투자 금액 : {final_investment} 만원")
            backtest_col2.write(f"수익률 : {final_ROI:.2f}%")

            #수익 그래프
            fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
            ax1.plot(monthly_investments['Total ROI'], label='ROI')
            ax2.plot(monthly_investments['Total Value'], label='Value')
            ax2.plot(monthly_investments['Total Investment'], label='Investment')
            ax2.legend()
            st.pyplot(fig)

#사이드바 구성
with st.sidebar:
    st.title('ETF 투자 도우미')
    st.radio('페이지', ['주가 그래프', '포토폴리오','비교' ,'백테스트'], index=None, key='page')
    st.divider()
    ticker, start, end, data = main_information()

page = st.session_state['page']
if page == '주가 그래프':
    graph()
elif page == '포토폴리오':
    portfolio()
elif page == '비교':
    compare()
elif page == '백테스트':
    backtest(ticker, start, end, data)
