import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from ing_theme_matplotlib import mpl_style
mpl_style(dark=True)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 제목
st.title('ETF 투자 도우미')

# ETF 이름, 시작, 종료 날짜 입력
with st.sidebar:
    ticker = st.text_input('ETF 또는 주식의 종목코드를 입력하세요', 'SPY')
    start_date = st.date_input("시작 날짜: ", value=pd.to_datetime("2010-01-01"))
    end_date = st.date_input("종료 날짜: ", value=pd.to_datetime("2024-01-01"))

st.divider()
st_graph, st_compare, st_backtest = st.tabs(['주가 그래프', '비교', '백테스트'])

# yfinance로 ETF 데이터 가져오기
data = yf.download(ticker, start=start_date, end=end_date)

with st_graph:
    if not data.empty:
        fig1, ax1 = plt.subplots()  # 새로운 figure 생성
        ax1.plot(data.index, data['Close'], label=ticker)
        ax1.set_title(f'{ticker} 종가 추이')
        ax1.set_xlabel('날짜')
        ax1.set_ylabel = ('종가')
        ax1.legend()
        st.pyplot(fig1)

    else:
        st.error("데이터가 없거나 입력 정보가 잘못되었습니다. 다시 확인해주세요.")

with st_compare:
    compare_tickers = st.text_input('비교할 ETF 또는 주식의 종목코드를 입력하세요', 'QQQ' if ticker == 'SPY' else 'SPY').split()
    fig2, (ax2, ax3) = plt.subplots(2, 1)  # 새로운 figure 생성
    ax2.plot(data.index, data['Close'], label=ticker)
    for compare_ticker in compare_tickers:
        compare_data = yf.download(compare_ticker, start=start_date, end=end_date)
        ax2.plot(compare_data.index, compare_data['Close'], label=compare_ticker)
    ax2.legend()

    plt.title(f'{ticker} 대 {", ".join(compare_tickers)} 종가 비교')


