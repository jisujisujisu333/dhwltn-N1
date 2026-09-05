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
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    return df


df = load_data()

# 날짜가 정상적으로 입력된 데이터만 사용
df = df.dropna(
    subset=["날짜", "평균기온"]
)

# 1926~2025년 데이터
df = df[
    (df["날짜"].dt.year >= 1926) &
    (df["날짜"].dt.year <= 2025)
].copy()

# 연도 만들기
df["연도"] = df["날짜"].dt.year

# 연평균 기온
yearly_temp = (
    df.groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

# 그래프
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(
    yearly_temp["연도"],
    yearly_temp["평균기온"],
    marker="o",
    markersize=3,
    linewidth=1.5
)

ax.set_title(
    "서울의 연평균 기온 변화",
    fontsize=18
)

ax.set_xlabel("연도")
ax.set_ylabel("연평균 기온 (℃)")

# 연도 표시
ax.set_xticks(
    range(1926, 2026, 10)
)

ax.set_xlim(1926, 2025)

ax.grid(
    True,
    alpha=0.3
)

plt.xticks(rotation=45)

fig.tight_layout()

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
    "1926년부터 2025년까지 서울의 연평균 기온 변화를 나타낸 그래프입니다."
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


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    return df


df = load_data()

# 1926~2025년
df = df[
    (df["날짜"].dt.year >= 1926) &
    (df["날짜"].dt.year <= 2025)
].copy()

temperatures = df["평균기온"].dropna()

# 히스토그램
fig, ax = plt.subplots(figsize=(14, 6))

ax.hist(
    temperatures,
    bins=30,
    edgecolor="black"
)

ax.set_title(
    "서울의 일별 평균기온 분포",
    fontsize=18
)

ax.set_xlabel("일별 평균기온 (℃)")
ax.set_ylabel("일수")

ax.grid(
    axis="y",
    alpha=0.3
)

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)

col1, col2, col3 = st.columns(3)

col1.metric(
    "전체 관측 일수",
    f"{len(temperatures):,}일"
)

col2.metric(
    "최저 평균기온",
    f"{temperatures.min():.1f} ℃"
)

col3.metric(
    "최고 평균기온",
    f"{temperatures.max():.1f} ℃"
)

st.write(
    f"분석 기간: **1926년 1월 1일 ~ 2025년 12월 31일**"
)

st.write(
    f"전체 일별 평균기온의 평균은 "
    f"**{temperatures.mean():.1f} ℃**입니다."
)import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="서울 최저기온과 최고기온",
    page_icon="🔵"
)

st.title("🔵 서울의 일별 최저기온과 최고기온 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    df["최저기온"] = pd.to_numeric(
        df["최저기온"],
        errors="coerce"
    )

    df["최고기온"] = pd.to_numeric(
        df["최고기온"],
        errors="coerce"
    )

    return df


df = load_data()

# 1926~2025년
df = df[
    (df["날짜"].dt.year >= 1926) &
    (df["날짜"].dt.year <= 2025)
].copy()

# 결측값 제거
scatter_data = df.dropna(
    subset=[
        "날짜",
        "최저기온",
        "최고기온"
    ]
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
    "서울의 일별 최저기온과 최고기온의 관계",
    fontsize=18
)

ax.set_xlabel("최저기온 (℃)")
ax.set_ylabel("최고기온 (℃)")

ax.grid(
    True,
    alpha=0.3
)

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)

# 상관계수
correlation = scatter_data[
    "최저기온"
].corr(
    scatter_data["최고기온"]
)

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
    "분석 기간: **1926년 ~ 2025년**"
)

st.write(
    "상관계수가 1에 가까울수록 "
    "최저기온이 높을 때 최고기온도 높아지는 "
    "관계가 강합니다."
)
