import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울의 100년간 연평균 기온 변화")
st.write("1907년 이후 서울의 연평균 기온이 어떻게 변해 왔는지 확인해 보세요.")

# 데이터 불러오기
url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"
df = pd.read_csv(url)

# 날짜를 날짜 형식으로 변환
df["날짜"] = pd.to_datetime(df["날짜"])

# 연도 추출
df["연도"] = df["날짜"].dt.year

# 연도별 평균기온 계산
yearly_temp = (
    df.groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

# 100년 이상의 전체 데이터 중 최근 100년 표시
yearly_temp = yearly_temp.tail(100)

# 그래프
st.subheader("📈 연도별 연평균 기온")

st.line_chart(
    yearly_temp,
    x="연도",
    y="평균기온",
    x_label="연도",
    y_label="평균기온 (℃)"
)

# 간단한 정보
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("분석 시작 연도", f"{yearly_temp['연도'].min()}년")

with col2:
    st.metric("분석 종료 연도", f"{yearly_temp['연도'].max()}년")

with col3:
    변화 = yearly_temp["평균기온"].iloc[-1] - yearly_temp["평균기온"].iloc[0]
    st.metric("처음과 마지막 연도의 차이", f"{변화:+.1f} ℃")

st.caption("출처: 기상청 서울 기온 데이터(seoul.csv)")
