# 어제의 박스오피스 — KOBIS 일별 박스오피스 API
import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="어제의 박스오피스", page_icon="🎬", layout="wide")

# 인증키는 비밀 금고(secrets)에서 불러온다 — 코드에 직접 쓰지 않는다
API_KEY = st.secrets["KOBIS_KEY"]
URL = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"

# '어제'를 한국 시간 기준으로 계산한다 (배포 서버의 시계는 한국 시간이 아니다)
KST = datetime.timezone(datetime.timedelta(hours=9))
yesterday = datetime.datetime.now(KST).date() - datetime.timedelta(days=1)

# --------------------------------------------------
# 날짜 선택
# --------------------------------------------------
# 가장 최근에 선택할 수 있는 날짜는 어제이다.
selected_date = st.date_input(
    "📅 조회할 날짜를 선택하세요",
    value=yesterday,
    max_value=yesterday
)

target_dt = selected_date.strftime("%Y%m%d")


@st.cache_data(ttl=3600)  # 같은 날짜는 한 시간 동안 기억해 두고 API를 다시 부르지 않는다
def fetch_boxoffice(date_str):
    """KOBIS API에서 해당 날짜의 일별 박스오피스를 받아 온다."""
    params = {"key": API_KEY, "targetDt": date_str}
    res = requests.get(URL, params=params, timeout=10)
    res.raise_for_status()
    return res.json()


st.title("🎬 어제의 박스오피스")
st.caption(f"조회 날짜: {selected_date}")

try:
    data = fetch_boxoffice(target_dt)
except requests.RequestException:
    st.error("서버에 연결하지 못했습니다. 인터넷 연결을 확인하고 잠시 뒤 새로고침해 주세요.")
    st.stop()

# 인증키가 틀리면 상태코드는 200이지만 faultInfo 상자가 온다
if "faultInfo" in data:
    st.error(f"API가 오류를 돌려주었습니다: {data['faultInfo'].get('message', '')}")
    st.info("비밀 금고(secrets)의 KOBIS_KEY 값이 올바른지 확인해 주세요.")
    st.stop()

movies = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])

# 영화 목록이 비어서 오면 — 해당 날짜의 데이터가 아직 없는 경우
if not movies:
    st.warning("그날은 아직 집계 전입니다.")
    st.info("다른 날짜를 선택해 주세요.")
    st.stop()

df = pd.DataFrame(movies)

# 숫자가 글자로 오므로 숫자로 바꿔야 정렬과 그래프에 쓸 수 있다
for col in ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]:
    df[col] = pd.to_numeric(df[col])

# --------------------------------------------------
# 영화명에 순위 변화와 트로피 표시
# --------------------------------------------------
def make_movie_name(row):
    # 영화의 누적 관객수가 100만 명을 넘으면 트로피를 붙인다
    trophy = " 🏆" if row["audiAcc"] > 1_000_000 else ""

    # 전날보다 순위가 오른 경우
    if row["rankInten"] > 0:
        return f"🔺 {row['movieNm']}{trophy}"

    # 전날보다 순위가 내려간 경우
    elif row["rankInten"] < 0:
        return f"🔻 {row['movieNm']}{trophy}"

    # 순위 변화가 없는 경우
    else:
        return f"{row['movieNm']}{trophy}"


df["display_movieNm"] = df.apply(make_movie_name, axis=1)


# 1위 영화는 지표 카드 세 장으로 크게
top = df.sort_values("rank").iloc[0]
st.subheader(f"🥇 1위 — {top['movieNm']}")

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


# 전체 순위표
st.subheader("📋 순위표")

table = df.sort_values("rank")[
    [
        "rank",
        "display_movieNm",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt"
    ]
]

table.columns = [
    "순위",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수"
]

st.dataframe(
    table,
    hide_index=True,
    width="stretch"
)


# 관객수 상위 5편은 막대그래프로
st.subheader("📊 관객수 상위 5편")

top5 = df.sort_values(
    "audiCnt",
    ascending=False
).head(5)

fig = px.bar(
    top5,
    x="movieNm",
    y="audiCnt",
    labels={
        "movieNm": "영화명",
        "audiCnt": "관객수"
    }
)

st.plotly_chart(
    fig,
    width="stretch"
)
