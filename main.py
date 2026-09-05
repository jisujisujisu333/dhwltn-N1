import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️"
)

st.title("🌡️ 서울의 100년 연평균 기온 변화")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

# 데이터 불러오기
df = pd.read_csv(DATA_URL)

# 날짜 변환
df["날짜"] = pd.to_datetime(df["날짜"])

# 연도 만들기
df["연도"] = df["날짜"].dt.year

# 평균기온 숫자 변환
df["평균기온"] = pd.to_numeric(
    df["평균기온"],
    errors="coerce"
)

# 1926~2025년 데이터만 사용
df = df[
    (df["연도"] >= 1926) &
    (df["연도"] <= 2025)
]

# 연도별 평균기온 계산
yearly_temp = (
    df.groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

# 그래프
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    yearly_temp["연도"],
    yearly_temp["평균기온"],
    linewidth=2
)

ax.set_title("서울의 연평균 기온 변화")
ax.set_xlabel("연도")
ax.set_ylabel("연평균 기온 (℃)")
ax.grid(True, alpha=0.3)

st.pyplot(fig)
plt.close(fig)

# 주요 수치
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
    "100년간 변화",
    f"{change:+.1f} ℃"
)

st.write(
    "위 그래프를 통해 서울의 연평균 기온이 "
    "100년 동안 어떻게 변화했는지 확인할 수 있습니다."
)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="서울 일별 평균기온 분포",
    page_icon="📊"
)

st.title("📊 서울의 일별 평균기온 분포")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

# 데이터 불러오기
df = pd.read_csv(DATA_URL)

# 날짜 변환
df["날짜"] = pd.to_datetime(df["날짜"])

# 연도 만들기
df["연도"] = df["날짜"].dt.year

# 평균기온 숫자 변환
df["평균기온"] = pd.to_numeric(
    df["평균기온"],
    errors="coerce"
)

# 1926~2025년 데이터만 사용
df = df[
    (df["연도"] >= 1926) &
    (df["연도"] <= 2025)
]

# 결측값 제거
temperatures = df["평균기온"].dropna()

# 히스토그램
fig, ax = plt.subplots(figsize=(12, 6))

ax.hist(
    temperatures,
    bins=30,
    edgecolor="black"
)

ax.set_title("서울의 일별 평균기온 분포")
ax.set_xlabel("일별 평균기온 (℃)")
ax.set_ylabel("일수")
ax.grid(axis="y", alpha=0.3)

st.pyplot(fig)
plt.close(fig)

# 주요 수치
col1, col2, col3 = st.columns(3)

col1.metric(
    "전체 관측 일수",
    f"{len(temperatures):,}일"
)

col2.metric(
    "가장 낮은 평균기온",
    f"{temperatures.min():.1f} ℃"
)

col3.metric(
    "가장 높은 평균기온",
    f"{temperatures.max():.1f} ℃"
)

st.write(
    f"전체 일별 평균기온의 평균은 "
    f"**{temperatures.mean():.1f} ℃**입니다."
)

st.write(
    "히스토그램을 통해 어떤 기온 구간에 "
    "일수가 많이 몰려 있는지 확인할 수 있습니다."
)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="서울 최저기온과 최고기온",
    page_icon="🔵"
)

st.title("🔵 서울의 일별 최저기온과 최고기온 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

# 데이터 불러오기
df = pd.read_csv(DATA_URL)

# 날짜 변환
df["날짜"] = pd.to_datetime(df["날짜"])

# 연도 만들기
df["연도"] = df["날짜"].dt.year

# 기온 숫자 변환
df["최저기온"] = pd.to_numeric(
    df["최저기온"],
    errors="coerce"
)

df["최고기온"] = pd.to_numeric(
    df["최고기온"],
    errors="coerce"
)

# 1926~2025년 데이터만 사용
df = df[
    (df["연도"] >= 1926) &
    (df["연도"] <= 2025)
]

# 필요한 데이터만 사용
scatter_data = df.dropna(
    subset=["최저기온", "최고기온"]
)

# 산점도
fig, ax = plt.subplots(figsize=(10, 7))

ax.scatter(
    scatter_data["최저기온"],
    scatter_data["최고기온"],
    alpha=0.3,
    s=10
)

ax.set_title(
    "서울의 일별 최저기온과 최고기온의 관계"
)

ax.set_xlabel("최저기온 (℃)")
ax.set_ylabel("최고기온 (℃)")

ax.grid(True, alpha=0.3)

st.pyplot(fig)
plt.close(fig)

# 상관계수
correlation = scatter_data["최저기온"].corr(
    scatter_data["최고기온"]
)

# 주요 수치
col1, col2, col3 = st.columns(3)

col1.metric(
    "최저기온 평균",
    f"{scatter_data['최저기온'].mean():.1f} ℃"
)

col2.metric(
    "최고기온 평균",
    f"{scatter_data['최고기온'].mean():.1f} ℃"
)

col3.metric(
    "상관계수",
    f"{correlation:.2f}"
)

st.write(
    "상관계수가 1에 가까울수록 "
    "최저기온이 높을 때 최고기온도 높아지는 "
    "관계가 강하다는 의미입니다."
)
