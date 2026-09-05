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
# 영화관 느낌의 배경
# =========================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at top,
            #5a1010 0%,
            #2a0808 35%,
            #0d0d0d 75%
        );
    color: white;
}

h1 {
    color: #ff5555 !important;
    font-weight: 800;
}

h2, h3 {
    color: white !important;
}

.stCaption {
    color: #cccccc !important;
}

[data-testid="stDateInput"] {
    background-color: #1c1c1c;
    border-radius: 10px;
}

[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        #351010,
        #181818
    );

    border: 1px solid #8b2525;
    padding: 8px;
    border-radius: 10px;
}

[data-testid="stMetricValue"] {
    color: #ff5555 !important;
    font-size: 22px !important;
}

[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

.stAlert {
    background-color: #1c1515;
    border-radius: 10px;
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
    "📅 조회할 날짜",
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
        "itemPerPage": 10
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
    f"조회 날짜: {selected_date} · 한국 시간 기준"
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
# API 오류
# =========================

if "faultInfo" in data:

    st.error(
        f"API 오류: "
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
# 숫자로 변환
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
# 상위 5개 트로피
# =========================

def make_movie_name(row):

    movie_name = row["movieNm"]

    if row["rank"] <= 5:

        movie_name = "🏆 " + movie_name

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


# ==================================================
# 순위표 TOP 10
# ==================================================

st.subheader(
    "📋 박스오피스 순위표 TOP 10"
)


table = df.head(10)[
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
# 알록달록한 순위 색상
# =========================

rank_colors = [
    "#ff3b30",
    "#ff9500",
    "#ffcc00",
    "#34c759",
    "#00c7be",
    "#30a9de",
    "#5856d6",
    "#af52de",
    "#ff2d55",
    "#ff6b6b"
]


def color_rank(row):

    rank = int(row["순위"])
    color = rank_colors[rank - 1]

    return [
        f"color: {color}; font-weight: bold; font-size: 13px;"
        if col == "순위"
        else "font-size: 13px;"
        for col in row.index
    ]


styled_table = table.style.apply(
    color_rank,
    axis=1
)


# =========================
# 순위 변동 색상
# =========================

def color_arrow(value):

    if value == "↑":

        return (
            "color: #ff3b30; "
            "font-weight: bold; "
            "font-size: 16px;"
        )

    elif value == "↓":

        return (
            "color: #30a9de; "
            "font-weight: bold; "
            "font-size: 16px;"
        )

    return "color: #aaaaaa;"


styled_table = styled_table.map(
    color_arrow,
    subset=["순위변동"]
)


st.dataframe(
    styled_table,
    hide_index=True,
    width="stretch",
    height=330
)


# ==================================================
# 그래프용 데이터
# ==================================================

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
# 그래프 2개 좌우 배치
# ==================================================

st.subheader("📊 관객수 TOP 10")

g1, g2 = st.columns(2)


# ==================================================
# 왼쪽 — 막대그래프
# ==================================================

with g1:

    st.markdown("### 🎞️ 영화별 관객수")

    fig1 = px.bar(
        top10.sort_values("audiCnt"),
        x="audiCnt",
        y="display_movieNm",
        orientation="h",
        color="display_movieNm",

        labels={
            "audiCnt": "관객수",
            "display_movieNm": "영화"
        },

        color_discrete_sequence=[
            "#ff3b30",
            "#ff9500",
            "#ffcc00",
            "#34c759",
            "#00c7be",
            "#30a9de",
            "#5856d6",
            "#af52de",
            "#ff2d55",
            "#ff6b6b"
        ]
    )

    fig1.update_layout(
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",

        font=dict(
            color="white",
            size=10
        ),

        height=330,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=20
        ),

        showlegend=False,

        xaxis=dict(
            gridcolor="#333333"
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
# 오른쪽 — 도넛그래프
# ==================================================

with g2:

    st.markdown("### 🍿 상위 10편 관객 점유율")

    fig2 = px.pie(
        top10,

        names="display_movieNm",
        values="audiCnt",

        hole=0.50,

        color="display_movieNm",

        color_discrete_sequence=[
            "#ff3b30",
            "#ff9500",
            "#ffcc00",
            "#34c759",
            "#00c7be",
            "#30a9de",
            "#5856d6",
            "#af52de",
            "#ff2d55",
            "#8e8e93"
        ]
    )

    fig2.update_layout(
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",

        font=dict(
            color="white",
            size=9
        ),

        height=330,

        margin=dict(
            l=5,
            r=5,
            t=20,
            b=10
        ),

        legend=dict(
            bgcolor="#111111",
            font=dict(
                color="white",
                size=9
            )
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
