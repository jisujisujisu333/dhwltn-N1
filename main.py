# 일별 박스오피스 — KOBIS 일별 박스오피스 API
import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="일별 박스오피스",
    page_icon="🎬",
    layout="wide"
)

# 인증키는 비밀 금고(secrets)에서 불러온다
API_KEY = st.secrets["KOBIS_KEY"]

URL = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"

# 한국 시간 기준으로 어제 날짜를 계산한다
KST = datetime.timezone(datetime.timedelta(hours=9))
yesterday = datetime.datetime.now(KST).date() - datetime.timedelta(days=1)

# 날짜 선택
selected_date = st.date_input(
    "📅 조회할 날짜를 선택하세요",
    value=yesterday,
    max_value=yesterday
)

target_dt = selected_date.strftime("%Y%m%d")


@st.cache_data(ttl=3600)
def fetch_boxoffice(date_str):
    """KOBIS API에서 해당 날짜의 일별 박스오피스를 받아 온다."""
    params = {
        "key": API_KEY,
        "targetDt": date_str,
        "itemPerPage": 50
    }

    res = requests.get(URL, params=params, timeout=10)
    res.raise_for_status()

    return res.json()


st.title("🎬 일별 박스오피스")
st.caption(f"조회 날짜: {selected_date}")

try:
    data = fetch_boxoffice(target_dt)

except requests.RequestException:
    st.error(
        "서버에 연결하지 못했습니다. "
        "인터넷 연결을 확인하고 잠시 뒤 새로고침해 주세요."
    )
    st.stop()


# API 오류 확인
if "faultInfo" in data:
    st.error(
        f"API가 오류를 돌려주었습니다: "
        f"{data['faultInfo'].get('message', '')}"
    )
    st.info(
        "비밀 금고(secrets)의 KOBIS_KEY 값이 올바른지 확인해 주세요."
    )
    st.stop()


# 영화 목록 가져오기
movies = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])


# 영화 목록이 없으면 안내
if not movies:
    st.warning("그날은 아직 집계 전입니다")
    st.stop()


df = pd.DataFrame(movies)


# 숫자로 변환
for col in ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# 순위순으로 정렬
df = df.sort_values("rank")


# 상위 5개 영화에 트로피 추가
def make_movie_name(row):
    movie_name = row["movieNm"]

    if row["rank"] <= 5:
        movie_name = "🏆 " + movie_name

    return movie_name


df["display_movieNm"] = df.apply(make_movie_name, axis=1)


# =========================
# 1위 영화
# =========================

top = df.iloc[0]

st.subheader(f"🥇 1위 — {top['display_movieNm']}")

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
# 전체 순위표 - 30위까지
# =========================

st.subheader("📋 박스오피스 순위표")

table = df.head(30)[
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


# 순위 변동 화살표
def make_arrow(value):
    if value > 0:
        return "↑"
    elif value < 0:
        return "↓"
    else:
        return "-"


table["rankInten"] = table["rankInten"].apply(make_arrow)


# 컬럼 이름 변경
table.columns = [
    "순위",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수",
    "순위변동"
]


# 화살표 색상
def color_arrow(value):
    if value == "↑":
        return "color: red; font-weight: bold;"
    elif value == "↓":
        return "color: blue; font-weight: bold;"
    else:
        return ""


styled_table = table.style.map(
    color_arrow,
    subset=["순위변동"]
)


st.dataframe(
    styled_table,
    hide_index=True,
    width="stretch"
)


# =========================
# 관객수 상위 10편 그래프
# =========================

st.subheader("📈 관객수 상위 10편")

top10 = (
    df.sort_values("audiCnt", ascending=False)
    .head(10)
    .copy()
)

# 그래프용 영화 이름
top10["display_movieNm"] = top10.apply(
    make_movie_name,
    axis=1
)

# 순위 표시용
top10["순위"] = top10["rank"].astype(int)


# 점 그래프
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
    color_discrete_sequence=px.colors.qualitative.Set2
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
