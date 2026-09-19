import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="기온 예측기",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 예측기")
st.write("서울의 과거 연평균기온을 바탕으로 선형회귀를 이용해 예상 기온을 확인합니다.")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "bb860932644270ad1199f10d3e7670e30231bce4/data/seoul.csv"
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온 숫자 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 필요한 데이터만 사용
    df = df.dropna(subset=["날짜", "평균기온"])

    # 연도 생성
    df["연도"] = df["날짜"].dt.year

    return df


df = load_data()

# --------------------------------------------------
# 2025년 이후 데이터 제외
# --------------------------------------------------
df = df[df["연도"] <= 2025].copy()

# --------------------------------------------------
# 연도별 관측일 수와 평균기온 계산
# --------------------------------------------------
yearly = (
    df.groupby("연도")
    .agg(
        평균기온=("평균기온", "mean"),
        관측일수=("평균기온", "count")
    )
    .reset_index()
)

# 관측일이 300일 이상인 해만 사용
yearly = yearly[yearly["관측일수"] >= 300].copy()

# 회귀에 사용할 시작 연도
REGRESSION_START_YEAR = 1908

# 1908년 이전 자료는 회귀에서 제외
yearly = yearly[yearly["연도"] >= REGRESSION_START_YEAR].copy()

# --------------------------------------------------
# 독립변수: 1908년부터 지난 연수
# --------------------------------------------------
yearly["지난연수"] = yearly["연도"] - REGRESSION_START_YEAR

# --------------------------------------------------
# 선형회귀 계산
# y = a*x + b
# --------------------------------------------------
x = yearly["지난연수"].to_numpy()
y = yearly["평균기온"].to_numpy()

slope, intercept = np.polyfit(x, y, 1)

# 예측값
yearly["회귀예측기온"] = slope * yearly["지난연수"] + intercept

# 상관계수
correlation = np.corrcoef(x, y)[0, 1]

# --------------------------------------------------
# 회귀선 표시용 데이터
# 1908년부터 2100년까지
# --------------------------------------------------
future_years = np.arange(REGRESSION_START_YEAR, 2101)
future_elapsed = future_years - REGRESSION_START_YEAR
future_prediction = slope * future_elapsed + intercept

# --------------------------------------------------
# 슬라이더
# --------------------------------------------------
selected_year = st.slider(
    "📅 예상 기온을 확인할 연도를 선택하세요",
    min_value=1900,
    max_value=2100,
    value=2025,
    step=1
)

# 선택 연도의 예상 기온
selected_elapsed = selected_year - REGRESSION_START_YEAR
predicted_temperature = slope * selected_elapsed + intercept

# --------------------------------------------------
# 선택한 연도 예상 기온
# --------------------------------------------------
st.subheader(f"🌡️ {selected_year}년 예상 연평균기온")

st.metric(
    label="회귀모델 예상 기온",
    value=f"{predicted_temperature:.2f} °C"
)

# --------------------------------------------------
# 회귀 정보
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("회귀에 사용된 연도 수", f"{len(yearly)}년")

with col2:
    st.metric("시작 연도", f"{yearly['연도'].min()}년")

with col3:
    st.metric("끝 연도", f"{yearly['연도'].max()}년")

with col4:
    st.metric("상관계수", f"{correlation:.3f}")

# --------------------------------------------------
# 산점도 + 회귀선
# --------------------------------------------------
fig = go.Figure()

# 실제 연평균기온 산점도
fig.add_trace(
    go.Scatter(
        x=yearly["연도"],
        y=yearly["평균기온"],
        mode="markers",
        name="실제 연평균기온",
        marker=dict(
            size=7,
            opacity=0.75
        ),
        customdata=yearly["관측일수"],
        hovertemplate=(
            "<b>%{x}년</b><br>"
            "평균기온: %{y:.2f} °C<br>"
            "관측일수: %{customdata}일"
            "<extra></extra>"
        )
    )
)

# 회귀선
fig.add_trace(
    go.Scatter(
        x=future_years,
        y=future_prediction,
        mode="lines",
        name="회귀 직선",
        line=dict(
            width=3
        ),
        hovertemplate=(
            "<b>%{x}년</b><br>"
            "회귀 예상기온: %{y:.2f} °C"
            "<extra></extra>"
        )
    )
)

# 선택한 연도 표시
fig.add_trace(
    go.Scatter(
        x=[selected_year],
        y=[predicted_temperature],
        mode="markers",
        name=f"{selected_year}년 예상값",
        marker=dict(
            size=14,
            symbol="star"
        ),
        hovertemplate=(
            f"<b>{selected_year}년</b><br>"
            "예상기온: %{y:.2f} °C"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    title="서울 연평균기온과 선형회귀",
    xaxis_title="연도",
    yaxis_title="연평균기온 (°C)",
    xaxis=dict(
        tickmode="linear",
        dtick=10,
        range=[1900, 2100]
    ),
    hovermode="closest",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# 회귀식 및 데이터 조건
# --------------------------------------------------
st.subheader("📊 회귀 분석 정보")

st.write(
    f"**회귀식:** 연평균기온 = "
    f"{slope:.4f} × (연도 - 1908) + {intercept:.4f}"
)

st.write(
    f"**상관계수:** {correlation:.4f}"
)

st.write(
    "※ 2025년 이후의 데이터와 연간 관측일수가 300일 미만인 연도는 "
    "회귀 분석에서 제외했습니다."
)

st.write(
    f"※ 최종적으로 **{len(yearly)}개 연도**의 데이터를 이용했으며, "
    f"**{yearly['연도'].min()}년~{yearly['연도'].max()}년**의 자료로 "
    "회귀 직선을 계산했습니다."
)
