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


def get_startend():
    col1, col2 = st.columns(2)
    start = col1.date_input('시작 날자: ', value=pd.to_datetime("2010-01-01"))
    end = col2.date_input('종료 날자: ', value=pd.to_datetime("2024-01-01"))
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    return (start, end)

def graph():
    ticker = st.text_input('주식 종목을 입력하세요', value='SPY')
    start, end = get_startend()
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
        one_date = pd.to_datetime(one_date)
        st.caption('사이드바에서 입력한 시작 날짜와 종료 날짜 사이 값으로 입력해주세요')
        if start <= one_date <= end:
            if one_date in data.index:
                st.write(data.loc[pd.to_datetime(one_date)]) #todo : 표로 바꾸기, 안됨 ㅅㅂ
            else:
                st.write('휴장일 날짜이거나, 당시 없던 종목입니다.')
        else:
            st.error("데이터가 없거나 입력 정보가 잘못되었습니다. 다시 확인해주세요.")

def add_ticker_portfolio(ticker, weight):
    if ticker and weight:
        if not ticker in st.session_state['portfolio_temp'].keys():
            st.session_state['portfolio_temp'][ticker] = weight
        else:
            st.session_state['portfolio_temp'][ticker] += weight

def remove_ticker_portfolio(ticker):
    if ticker in st.session_state['portfolio_temp']:
        del st.session_state['portfolio_temp'][ticker]
        st.success(f"종목 '{ticker}'이(가) 제거되었습니다.")
    else:
        st.error("종목을 선택해주세요.")

def portfolio():
    with st.form("portfolio_form"):
        if not 'portfolio_temp' in st.session_state:
            st.session_state['portfolio_temp'] = {}
        temp = st.session_state['portfolio_temp']
        # 포트폴리오 이름 입력
        name = st.text_input("포트폴리오 이름을 입력하세요.", placeholder='이름을 입력하세요')

        st.divider()
        # 종목과 비중 입력
        ticker = st.text_input("추가할 종목 이름을 입력하세요.", value='SPY')
        weight = st.number_input("종목 비중을 입력하세요.", min_value=0.0, max_value=100.0, step=0.1)

        # 종목 추가 버튼
        st.form_submit_button("종목 추가하기", on_click=add_ticker_portfolio(ticker, weight))


        #추가된 항목 보여주기
        if temp:
            st.write(temp)
            selected_tickers = st.multiselect('제거할 종목을 선택하세요', list(temp.keys()))
            st.form_submit_button("종목 제거하기", on_click=remove_ticker_portfolio, args=(selected_tickers,))

        st.divider()
        # 포트폴리오 제출
        submit_button = st.form_submit_button("포트폴리오 제출")
        if submit_button:
            if not 'portfolio' in st.session_state:
                st.session_state['portfolio'] = {}
            if name in st.session_state['portfolio']:
                st.error("이미 존재하는 포트폴리오 이름입니다. 다른 이름을 사용해주세요.")
            else:
                st.session_state['portfolio'][name] = temp
                st.success(f"'{name}' 포트폴리오가 성공적으로 추가되었습니다.")
                st.session_state['portfolio_temp'] = {}


def get_portfolio_weighted_price(portfolio, start, end):
    # Initialize an empty DataFrame to store the weighted prices
    portfolio_data = pd.DataFrame()

    weight_total = sum(portfolio.values())
    # Iterate through the portfolio dictionary
    for ticker, weight in portfolio.items():
        # Download the stock data for the given ticker
        data = yf.download(ticker, start=start, end=end)

        if not data.empty:
            # Multiply the 'Close' price by the weight
            data['Weighted Close'] = data['Close'] * (weight / weight_total)

            if portfolio_data.empty:
                # Initialize the portfolio_data DataFrame with the first stock's data
                portfolio_data = data[['Weighted Close']].copy()
            else:
                # Add the weighted prices to the existing portfolio_data DataFrame
                portfolio_data = portfolio_data.add(data[['Weighted Close']], fill_value=0)

    # Rename the 'Weighted Close' column to 'Close' to match the single stock DataFrame format
    portfolio_data.rename(columns={'Weighted Close': 'Close'}, inplace=True)

    return portfolio_data

def compare():
    tickers = st.text_input(f'비교할 ETF 또는 주식의 종목코드를 입력하세요', 'SPY').split()
    start, end = get_startend()

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    for ticker in tickers:
        data = yf.download(ticker, start=start, end=end)
        # 주어진 날짜 이후의 가장 가까운 거래일 찾기
        idx_after = data.index.searchsorted(start, side='left')
        initialClose = data['Close'][idx_after]
        data['relative_Close'] = data['Close']/initialClose
        ax1.plot(data.index, data['Close'], label=ticker)
        ax2.plot(data.index, data['relative_Close'], label=ticker)


    ax1.legend()
    ax2.legend()
    ax1.set_title(f'{", ".join(tickers)} 종가 비교')
    ax2.set_title(f'{", ".join(tickers)} 종가 추이 비교')

    fig.tight_layout()
    st.pyplot(fig)

def backtest():
    start, end = get_startend()
    pt_or_stock = st.radio('선택하세요', ['포토폴리오', '단일종목'])
    if 'portfolio' in st.session_state and pt_or_stock == '포토폴리오':
        seleced_portfolio = st.selectbox('포토폴리오를 선택하세요', list(st.session_state['portfolio'].keys()))
        data = get_portfolio_weighted_price(st.session_state['portfolio'][seleced_portfolio], start, end)

    elif pt_or_stock == '단일종목':
        ticker = st.text_input('주식 종목을 입력하세요', value='SPY')
        data = yf.download(ticker, start=start, end=end)


    investment_select = st.radio('투자 방법을 선택하세요', ('일회성 투자', '적금형 투자'))
    st.divider()

    if investment_select:
        col1, col2 = st.columns(2, gap='medium')

    if investment_select == '일회성 투자':
        start_money = col1.number_input('투자할 금액을 입력하세요', value=1000, step=5, placeholder='만원 단위로 입력하세요')
        if start_money:
            end_money = round(start_money * data['Close'].iloc[-1] / data['Close'].iloc[0])
            col2.markdown(f"## 최종 금액: {end_money} 원")

    elif investment_select == '적금형 투자':
        month_money = col1.number_input('매월 투자할 금액을 입력하세요', value=100, step=10, placeholder='만원 단위로 입력하세요')
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

            col2.write(f"투자 기간 : {len(monthly_investments)}월")
            col2.write(f"최종 금액 : {final_value} 만원")
            col2.write(f"총 투자 금액 : {final_investment} 만원")
            col2.write(f"수익률 : {final_ROI:.2f}%")

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
    st.radio('페이지', ['주가 그래프','비교', '포토폴리오' ,'백테스트'], index=None, key='page')
    st.divider()

page = st.session_state['page']
if page == '주가 그래프':
    graph()
elif page == '포토폴리오':
    portfolio()
elif page == '비교':
    compare()
elif page == '백테스트':
    backtest()
