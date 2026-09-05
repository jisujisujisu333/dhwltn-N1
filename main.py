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

# 인증키
API_KEY = st.secrets["KOBIS_KEY"]

# 일별 박스오피스 API
BOXOFFICE_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

# 영화 목록 API
MOVIE_LIST_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "movie/searchMovieList.json"
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
# 일별 박스오피스 가져오기
# =========================

@st.cache_data(ttl=3600)
def fetch_boxoffice(date_str):

    params = {
        "key": API_KEY,
        "targetDt": date_str,
        "itemPerPage": 50
    }

    response = requests.get(
        BOXOFFICE_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# =========================
# 영화 목록 추가 조회
# =========================

@st.cache_data(ttl=3600)
def fetch_movie_list():

    params = {
        "key": API_KEY,
        "itemPerPage": 100
    }

    response = requests.get(
        MOVIE_LIST_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# =========================
# 제목
# =========================

st.title("🎬 일별 박스오피스")

st.caption(
    f"조회 날짜: {selected_date}"
)


# =========================
# API 호출
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
        "API가 오류를 돌려주었습니다: "
        + data["faultInfo"].get("message", "")
    )

    st.info(
        "secrets의 KOBIS_KEY 값을 확인해 주세요."
    )

    st.stop()


# =========================
# 일별 박스오피스 자료
# =========================

movies = (
    data
    .get("boxOfficeResult", {})
    .get("dailyBoxOfficeList", [])
)


# 자료가 없는 경우
if not movies:

    st.warning(
        "그날은 아직 집계 전입니다"
    )

    st.stop()


df = pd.DataFrame(movies)


# =========================
# 숫자 변환
# =========================

number_columns = [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt"
]

for col in number_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# =========================
# 순위 정렬
# =========================

df = df.sort_values(
    "rank"
).reset_index(drop=True)


# =========================
# 30위까지 표시
# =========================

df = df.head(30).copy()


# =========================
# 영화명에 트로피
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
# 자료 개수 표시
# =========================

movie_count = len(df)

st.info(
    f"📊 현재 불러온 영화: "
    f"{movie_count}편"
)


# =========================
# 30위까지 없는 경우 안내
# =========================

if movie_count < 30:

    st.warning(
        "KOBIS에서 해당 날짜의 일별 박스오피스 "
        f"자료가 {movie_count}편만 제공되었습니다."
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
    "📋 박스오피스 순위표 (1~30위)"
)


table = df[
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

    if value < 0:
        return "↓"

    return "-"


table["rankInten"] = table[
    "rankInten"
].apply(make_arrow)


# =========================
# 컬럼명
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

    if value == "↓":

        return (
            "color: blue; "
            "font-weight: bold;"
        )

    return ""


styled_table = table.style.map(
    color_arrow,
    subset=["순위변동"]
)


# =========================
# 30위까지 표 출력
# =========================

st.dataframe(
    styled_table,
    hide_index=True,
    width="stretch",
    height=1100
)


# =========================
# 관객수 상위 10편
# =========================

st.subheader(
    "📈 관객수 상위 10편"
)


top10 = (
    df
    .sort_values(
        "audiCnt",
        ascending=False
    )
    .head(10)
    .copy()
)


top10["순위"] = (
    top10["rank"]
    .astype(int)
)


# =========================
# 그래프
# =========================

fig = px.scatter(
    top10,

    x="순위",
    y="audiCnt",

    size="audiCnt",

    color="display_movieNm",

    text="display_movieNm",

    hover_data={
        "순위": True,
        "display_movieNm": False,
        "audiCnt": ":,",
        "audiAcc": ":,"
    },

    labels={
        "순위": "순위",
        "audiCnt": "관객수",
        "display_movieNm": "영화"
    },

    title="관객수 상위 10편 비교",

    color_discrete_sequence=(
        px.colors.qualitative.Set2
    )
)


fig.update_traces(
    textposition="top center"
)


fig.update_layout(
    xaxis=dict(
        dtick=1
    ),

    xaxis_title="순위",

    yaxis_title="관객수",

    showlegend=True,

    legend_title="영화"
)


st.plotly_chart(
    fig,
    width="stretch"
)
