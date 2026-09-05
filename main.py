# 일별 박스오피스 — KOBIS 일별 박스오피스 API

import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# =========================
# 기본 설정
# =========================

st.set_page_config(
    page_title="일별 박스오피스",
    page_icon="🎬",
    layout="wide"
)


# =========================
# 영화관 느낌의 어두운 테마
# =========================

st.markdown("""
<style>

.stApp {
    background-color: #111111;
    color: #f5f5f5;
}

h1, h2, h3 {
    color: #ffffff;
}

.stCaption {
    color: #aaaaaa;
}

[data-testid="stMetric"] {
    background-color: #1c1c1c;
    border: 1px solid #333333;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stDataFrame"] {
    background-color: #181818;
}

.stAlert {
    background-color: #1c1c1c;
}

</style>
""", unsafe_allow_html=True)


# =========================
# 인증키
# =========================

API_KEY = st.secrets["KOBIS_KEY"]

URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)


# =========================
# 한국 시간
# =========================

KST = datetime.timezone(
    datetime.timedelta(hours=9)
)

yesterday = (
    datetime.datetime.now(KST).date()
    - datetime.timedelta(days=1)
)


# =========================
# 날짜 선택
# =========================

selected_date = st.date_input(
    "📅 조회할 날짜를 선택하세요",
    value=yesterday,
    max_value=yesterday
)

target_dt = selected_date.strftime("%Y%m%d")


# =========================
# API 호출
# =========================

@st.cache_data(ttl=3600)
def fetch_boxoffice(date_str):

    params = {
        "key": API_KEY,
        "targetDt": date_str,
        "itemPerPage": 50
    }

    res = requests.get(
        URL,
        params=params,
        timeout=10
    )

    res.raise_for_status()

    return res.json()


# =========================
# 제목
# =========================

st.title("🎬 일별 박스오피스")

st.caption(
    f"조회 날짜: {selected_date}"
)


# =========================
# 데이터 가져오기
# =========================

try:

    data = fetch_boxoffice(target_dt)

except requests.RequestException:

    st.error(
        "서버에 연결하지 못했습니다. "
        "인터넷 연결을 확인하고 잠시 뒤 새로고침해 주세요."
    )

    st.stop()


# =========================
# API 오류 확인
# =========================

if "faultInfo" in data:

    st.error(
        f"API가 오류를 돌려주었습니다: "
        f"{data['faultInfo'].get('message', '')}"
    )

    st.info(
        "secrets의 KOBIS_KEY 값을 확인해 주세요."
    )

    st.stop()


# =========================
# 영화 목록
# =========================

movies = (
    data
    .get("boxOfficeResult", {})
    .get("dailyBoxOfficeList", [])
)


if not movies:

    st.warning(
        "그날은 아직 집계 전입니다"
    )

    st.stop()


df = pd.DataFrame(movies)


# =========================
# 숫자 변환
# =========================

for col in [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt"
]:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# =========================
# 순위 정렬
# =========================

df = (
    df
    .sort_values("rank")
    .reset_index(drop=True)
)


# =========================
# 상위 5개 영화 트로피
# =========================

def make_movie_name(row):

    movie_name = row["movieNm"]

    if row["rank"] <= 5:

        movie_name = (
            "🏆 " + movie_name
        )

    return movie_name


df["display_movieNm"] = df.apply(
    make_movie_name,
    axis=1
)


# =========================
# 1위 영화
# =========================

top = df.iloc[0]


st.subheader(
    f"🥇 1위 — {top['display_movieNm']}"
)


c1, c2, c3 = st.columns(3)


c1.metric(
    "관객수",
    f"{top['audiCnt']:,}명"
)


c2.metric(
    "누적 관객수",
    f"{top['audiAcc']:,}명"
)


c3.metric(
    "스크린수",
    f"{top['scrnCnt']:,}개"
)


# =========================
# 순위표
# =========================

st.subheader(
    "📋 박스오피스 순위표"
)


table = df.head(20)[
    [
        "rank",
        "display_movieNm",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
        "rankInten"
    ]
].copy()


# =========================
# 순위 변동
# =========================

def make_arrow(value):

    if pd.isna(value):
        return "-"

    if value > 0:
        return "↑"

    elif value < 0:
        return "↓"

    return "-"


table["rankInten"] = (
    table["rankInten"]
    .apply(make_arrow)
)


# =========================
# 컬럼 이름
# =========================

table.columns = [
    "순위",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수",
    "순위변동"
]


# =========================
# 화살표 색상
# =========================

def color_arrow(value):

    if value == "↑":

        return (
            "color: red; "
            "font-weight: bold;"
        )

    elif value == "↓":

        return (
            "color: #4da6ff; "
            "font-weight: bold;"
        )

    return ""


styled_table = table.style.map(
    color_arrow,
    subset=["순위변동"]
)


st.dataframe(
    styled_table,
    hide_index=True,
    width="stretch",
    height=700
)


# ==================================================
# 그래프 영역
# ==================================================

st.subheader("📊 박스오피스 그래프")


top10 = (
    df
    .sort_values(
        "audiCnt",
        ascending=False
    )
    .head(10)
    .copy()
)


top10["display_movieNm"] = (
    top10.apply(
        make_movie_name,
        axis=1
    )
)


# ==================================================
# 그래프 1 — 가로 막대그래프
# ==================================================

st.markdown("### 🎞️ 관객수 TOP 10")


fig1 = px.bar(
    top10.sort_values("audiCnt"),

    x="audiCnt",
    y="display_movieNm",

    orientation="h",

    color="audiCnt",

    color_continuous_scale=[
        "#3b0a0a",
        "#7a1111",
        "#c62828",
        "#ff5252"
    ],

    labels={
        "audiCnt": "관객수",
        "display_movieNm": "영화"
    },

    title="관객수 상위 10편"
)


fig1.update_layout(
    paper_bgcolor="#111111",
    plot_bgcolor="#111111",

    font=dict(
        color="white"
    ),

    xaxis=dict(
        gridcolor="#333333",
        title="관객수"
    ),

    yaxis=dict(
        title=""
    ),

    coloraxis_colorbar=dict(
        title="관객수"
    )
)


fig1.update_traces(
    hovertemplate=(
        "<b>%{y}</b><br>"
        "관객수: %{x:,}명"
        "<extra></extra>"
    )
)


st.plotly_chart(
    fig1,
    width="stretch"
)


# ==================================================
# 그래프 2 — 도넛 그래프
# ==================================================

st.markdown("### 🍿 관객 점유율")


fig2 = px.pie(
    top10,

    names="display_movieNm",
    values="audiCnt",

    hole=0.45,

    title="상위 10편 관객 점유율",

    labels={
        "display_movieNm": "영화",
        "audiCnt": "관객수"
    },

    color_discrete_sequence=(
        px.colors.qualitative.Dark24
    )
)


fig2.update_layout(
    paper_bgcolor="#111111",
    plot_bgcolor="#111111",

    font=dict(
        color="white"
    ),

    legend=dict(
        bgcolor="#111111"
    )
)


fig2.update_traces(
    textposition="inside",
    textinfo="percent"
)


st.plotly_chart(
    fig2,
    width="stretch"
)
