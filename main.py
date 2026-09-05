import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 서울의 100년 연평균 기온 변화")
st.write("1926년부터 2025년까지 서울의 연평균 기온이 어떻게 변했는지 알아봅니다.")

# 데이터 주소
url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(url)

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"])

    # 연도 열 만들기
    df["연도"] = df["날짜"].dt.year

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    return df


df = load_data()

# 1926년 ~ 2025년 데이터만 선택
df_100 = df[(df["연도"] >= 1926) & (df["연도"] <= 2025)]

# 연도별 평균기온 계산
yearly_temp = (
    df_100.groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

# 그래프
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(
    yearly_temp["연도"],
    yearly_temp["평균기온"],
    linewidth=2
)

ax.set_title("서울의 100년 연평균 기온 변화", fontsize=18)
ax.set_xlabel("연도", fontsize=12)
ax.set_ylabel("연평균 기온 (℃)", fontsize=12)
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# 간단한 정보 표시
first_temp = yearly_temp.iloc[0]["평균기온"]
last_temp = yearly_temp.iloc[-1]["평균기온"]
change = last_temp - first_temp

col1, col2, col3 = st.columns(3)

col1.metric(
    "1926년 평균기온",
    f"{first_temp:.1f} ℃"
)

col2.metric(
    "2025년 평균기온",
    f"{last_temp:.1f} ℃"
)

col3.metric(
    "100년간 기온 변화",
    f"{change:+.1f} ℃"
)

st.subheader("📊 연도별 평균기온 데이터")
st.dataframe(yearly_temp, use_container_width=True)

st.caption("자료: 서울 기온 관측 데이터")
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(
    page_title="서울 일별 평균기온 분포",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울의 일별 평균기온 분포")
st.write("1926년부터 2025년까지 일별 평균기온이 어느 구간에 얼마나 몰려 있는지 확인합니다.")

# 데이터 주소
url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(url)

    df["날짜"] = pd.to_datetime(df["날짜"])
    df["연도"] = df["날짜"].dt.year
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    return df


df = load_data()

# 1926년 ~ 2025년 데이터 선택
df_100 = df[
    (df["연도"] >= 1926) &
    (df["연도"] <= 2025)
]

# 결측값 제거
temperatures = df_100["평균기온"].dropna()

# 히스토그램
fig, ax = plt.subplots(figsize=(14, 6))

ax.hist(
    temperatures,
    bins=30,
    edgecolor="black"
)

ax.set_title("서울의 일별 평균기온 분포", fontsize=18)
ax.set_xlabel("일별 평균기온 (℃)", fontsize=12)
ax.set_ylabel("일수", fontsize=12)
ax.grid(axis="y", alpha=0.3)

st.pyplot(fig)

# 가장 많이 나타난 구간 확인
st.subheader("📊 기온 분포 정보")

st.write(f"전체 일수: **{len(temperatures):,}일**")
st.write(f"최저 평균기온: **{temperatures.min():.1f} ℃**")
st.write(f"최고 평균기온: **{temperatures.max():.1f} ℃**")
st.write(f"전체 평균기온: **{temperatures.mean():.1f} ℃**")

st.caption("자료: 서울 기온 관측 데이터")
