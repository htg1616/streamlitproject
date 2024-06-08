import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from ing_theme_matplotlib import mpl_style
from PIL import Image

# matplotlib 스타일 설정
mpl_style(dark=True)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def page_home():
    """
    홈 페이지를 렌더링함.
    이미지와 텍스트를 포함함.
    """
    st.title('ETF 투자')
    st.subheader('내가 대구과학고에서 성공할 수 있었던 이유')
    img = Image.open('image.jpg')
    st.image(img)
    st.divider()
    st.markdown('**수석 재무관리사 황태균**')
    st.markdown(':trophy: 서울 사이버대학 경영학과 수석 :trophy:')
    st.markdown(':trophy: 2020 리만 브라더스 배 경영대회 1등 :trophy:')
    st.markdown(':trophy: 2020~2023 지점 챔피언 :trophy:')
    st.markdown('200만원을 벌려면 적성에 직업을 맞추고')
    st.markdown('2000만원을 벌려면 직업에 적성을 맞추어라')
    st.markdown(':telephone_receiver: 무료자산관리 상담신청 및 채용문의')
    st.markdown('010-0000-0000')
    st.divider()
    st.markdown(':star: 돈 관리와 지식이 없는분')
    st.markdown(':star: 스스로 시작하지 못하는 분')
    st.markdown(':star: 수입 지출 균형이 맞지 않는분')
    st.markdown(':fire: 여러분도 저와 ETF 투자와 함께라면 연봉 5억 가능합니다')
    st.markdown(':fire: 함께 배우고 함께 참여하세요.')

def get_startend():
    """
    시작 날짜와 종료 날짜를 입력받아 반환함.

    Returns:
        tuple: 시작 날짜와 종료 날짜 (datetime 형식)
    """
    col1, col2 = st.columns(2)
    start = col1.date_input('시작 날자: ', value=pd.to_datetime("2010-01-01"))
    end = col2.date_input('종료 날자: ', value=pd.to_datetime("2024-01-01"))
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    return (start, end)

def page_graph():
    """
    주식 종목의 종가 그래프를 출력함.
    종목 코드를 입력받아 해당 종목의 종가를 그래프로 표시함.
    """
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
                st.write(data.loc[pd.to_datetime(one_date)])
            else:
                st.write('휴장일 날짜이거나, 당시 없던 종목임.')
        else:
            st.error("데이터가 없거나 입력 정보가 잘못되었음. 다시 확인해주세요.")

def add_ticker_portfolio(ticker, weight):
    """
    포트폴리오에 종목과 비중을 추가함.

    Args:
        ticker (str): 주식 종목 코드
        weight (float): 주식 비중
    """
    if ticker and weight:
        if not ticker in st.session_state['portfolio_temp'].keys():
            st.session_state['portfolio_temp'][ticker] = weight
        else:
            st.session_state['portfolio_temp'][ticker] += weight

def remove_ticker_portfolio(ticker):
    """
    포트폴리오에서 종목을 제거함.

    Args:
        ticker (str): 제거할 주식 종목 코드
    """
    if ticker in st.session_state['portfolio_temp']:
        del st.session_state['portfolio_temp'][ticker]
        st.success(f"종목 '{ticker}'이(가) 제거되었음.")
    else:
        st.error("종목을 선택해주세요.")

def page_portfolio():
    """
    포트폴리오 페이지를 렌더링함.
    포트폴리오 이름을 입력받고 종목과 비중을 추가하거나 제거할 수 있음.
    """
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
        st.form_submit_button("종목 추가하기", on_click=add_ticker_portfolio, args=(ticker, weight))

        # 추가된 항목 보여주기
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
                st.success(f"'{name}' 포트폴리오가 성공적으로 추가되었음.")
                st.session_state['portfolio_temp'] = {}

def get_portfolio_weighted_price(portfolio, start, end):
    """
    포트폴리오의 종목과 가중치를 받아 날짜별 종가*가중치의 총합을 반환함.

    Args:
        portfolio (dict): 종목과 가중치로 이루어진 포트폴리오
        start (datetime): 시작 날짜
        end (datetime): 종료 날짜

    Returns:
        DataFrame: 날짜별 종가*가중치의 총합 데이터프레임
    """
    # 가중치 가격을 저장할 빈 데이터프레임 초기화
    portfolio_data = pd.DataFrame()

    weight_total = sum(portfolio.values())
    # 포트폴리오 사전을 순회함
    for ticker, weight in portfolio.items():
        # 주어진 티커에 대한 주식 데이터를 다운로드함
        data = yf.download(ticker, start=start, end=end)

        if not data.empty:
            # 'Close' 가격에 가중치를 곱함
            data['Weighted Close'] = data['Close'] * (weight / weight_total)

            if portfolio_data.empty:
                # 첫 번째 주식 데이터로 portfolio_data 데이터프레임을 초기화함
                portfolio_data = data[['Weighted Close']].copy()
            else:
                # 기존 portfolio_data 데이터프레임에 가중치 가격을 추가함
                portfolio_data = portfolio_data.add(data[['Weighted Close']], fill_value=0)

    # 'Weighted Close' 열을 'Close'로 이름을 변경하여 단일 주식 데이터프레임 형식과 일치시킴
    portfolio_data.rename(columns={'Weighted Close': 'Close'}, inplace=True)

    return portfolio_data

def page_compare():
    """
    여러 주식의 종가와 종가 추이를 비교하는 페이지를 렌더링함.
    사용자가 입력한 주식 종목의 종가와 상대 종가를 그래프로 표시함.
    """
    tickers = st.text_input('비교할 ETF 또는 주식의 종목코드를 입력하세요', 'SPY').split()
    start, end = get_startend()

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    for ticker in tickers:
        data = yf.download(ticker, start=start, end=end)
        # 주어진 날짜 이후의 가장 가까운 거래일 찾기
        idx_after = data.index.searchsorted(start, side='left')
        initialClose
