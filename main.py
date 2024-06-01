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

# 제목
st.title('ETF 투자 도우미')

# ETF 이름, 시작, 종료 날짜 입력
with st.sidebar:
    ticker = st.text_input('ETF 또는 주식의 종목코드를 입력하세요', 'SPY')
    start_date = pd.to_datetime(st.date_input("시작 날짜: ", value=pd.to_datetime("2010-01-01")))
    end_date = pd.to_datetime(st.date_input("종료 날짜: ", value=pd.to_datetime("2024-01-01")))

st.divider()
st_graph, st_compare, st_backtest = st.tabs(['주가 그래프', '비교', '백테스트'])

# yfinance로 ETF 데이터 가져오기
data = yf.download(ticker, start=start_date, end=end_date)
# 주어진 날짜 이후의 가장 가까운 거래일 찾기
idx_after = data.index.searchsorted(start_date, side='left')
initialClose = data['Close'][idx_after]
finalClose = data['Close'].asof(end_date)

with st_graph:
    if not data.empty:
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
            one_date = pd.to_datetime(st.date_input(label='언제 주가를 알려줄까?', value=start_date, min_value=start_date, max_value=end_date))
            st.caption('사이드바에서 입력한 시작 날짜와 종료 날짜 사이 값으로 입력해주세요')
            if start_date <= one_date <= end_date:
                if one_date in data.index:
                    st.write(data.loc[one_date])
                else:
                    st.write('휴장일 날짜이거나, 당시 없던 종목입니다.')
    else:
        st.error("데이터가 없거나 입력 정보가 잘못되었습니다. 다시 확인해주세요.")

with st_compare:
    compare_tickers = st.text_input('비교할 ETF 또는 주식의 종목코드를 입력하세요', 'QQQ' if ticker == 'SPY' else 'SPY').split()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(data.index, data['Close'], label=ticker)

    data['relative_Close'] = data['Close']/initialClose
    ax2.plot(data.index, data['relative_Close'], label=ticker)

    for compare_ticker in compare_tickers:
        compare_data = yf.download(compare_ticker, start=start_date, end=end_date)
        # 주어진 날짜 이후의 가장 가까운 거래일 찾기
        compare_idx_after = compare_data.index.searchsorted(start_date, side='left')
        compare_initialClose = compare_data['Close'][compare_idx_after]
        compare_data['relative_Close'] = compare_data['Close']/compare_initialClose
        ax1.plot(compare_data.index, compare_data['Close'], label=compare_ticker)
        ax2.plot(compare_data.index, compare_data['relative_Close'], label=compare_ticker)

    ax1.legend()
    ax2.legend()

    st.pyplot(fig)

    plt.title(f'{ticker} 대 {", ".join(compare_tickers)} 종가 비교')

with st_backtest:
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
        monthly_investments = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date, freq='MS')) # MS is month start frequency
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
        ax2.plot(monthly_investments['Total Investment'], label='Investment')
        ax2.plot(monthly_investments['Total Value'], label='Value')
        st.pyplot(fig)
