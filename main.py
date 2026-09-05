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
# 영화관 포스터 스타일
# =========================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 50% 0%,
            #651313 0%,
            #320909 30%,
            #150505 65%,
            #080808 100%
        );

    color: white;
}


/* 제목 */

h1 {
    color: #ff4d4d !important;
    font-weight: 900;
    letter-spacing: -1px;
}

h2, h3 {
    color: white !important;
    font-weight: 800;
}


/* 설명 */

.stCaption {
    color: #cfcfcf !important;
}


/* 날짜 선택 */

[data-testid="stDateInput"] {
    background-color: rgba(25, 10, 10, 0.8);
    border: 1px solid #682020;
    border-radius: 12px;
    padding: 5px;
}


/* 통계 카드 */

[data-testid="stMetric"] {
    background:
        linear-gradient(
            135deg,
            rgba(80, 15, 15, 0.9),
            rgba(20, 10, 10, 0.95)
        );

    border: 1px solid #742323;
    border-radius: 14px;
    padding: 10px;

    box-shadow:
        0 4px 18px rgba(0, 0, 0, 0.45);
}


[data-testid="stMetricLabel"] {
    color: #bbbbbb !important;
}


[data-testid="stMetricValue"] {
    color: #ff5555 !important;
    font-size: 23px !important;
    font-weight: 800;
}


/* 알림 */

.stAlert {
    background-color: rgba(35, 12, 12, 0.9);
    border-radius: 12px;
}


/* 표 전체 */

.movie-table-box {
    background:
        linear-gradient(
            145deg,
            rgba(35, 10, 10, 0.97),
            rgba(12, 12, 12, 0.98)
        );

    border: 1px solid #632020;
    border-radius: 16px;

    overflow: hidden;

    box-shadow:
        0 8px 30px rgba(0, 0, 0, 0.55);

    margin-top: 5px;
}


/* 표 */

.movie-table {
    width: 100%;
    border-collapse: collapse;
    color: #eeeeee;
    font-size: 13px;
}


/* 표 제목 */

.movie-table thead {
    background:
        linear-gradient(
            90deg,
            #4d0b0b,
            #751414,
            #4d0b0b
        );
}


.movie-table th {
    color: #ffffff;
    font-weight: 800;
    padding: 11px 8px;
    border-bottom: 1px solid #8b2b2b;
    text-align: center;
}


/* 표 내용 */

.movie-table td {
    padding: 9px 8px;
    border-bottom: 1px solid rgba(130, 40, 40, 0.35);
    text-align: center;
}


/* 영화명 */

.movie-name {
    text-align: left !important;
    font-weight: 650;
    color: #f1f1f1;
}


/* 마우스를 올렸을 때 */

.movie-table tbody tr:hover {
    background: rgba(180, 30, 30, 0.15);
}


/* 1~3위 강조 */

.rank-1 {
    font-size: 18px;
    font-weight: 900;
}

.rank-2 {
    font-size: 16px;
    font-weight: 800;
}

.rank-3 {
    font-size: 15px;
    font-weight: 800;
}


/* 순위 숫자 */

.rank-normal {
    font-weight: 700;
}


/* 상승 */

.up {
    color: #ff4d4d;
    font-size: 18px;
    font-weight: 900;
}


/* 하락 */

.down {
    color: #4da6ff;
    font-size: 18px;
    font-weight: 900;
}


/* 유지 */

.same {
    color: #888888;
    font-size: 17px;
}


/* 그래프 제목 */

.chart-title {
    color: #ffffff;
    font-size: 17px;
    font-weight: 800;

    border-left: 4px solid #ff3b30;
    padding-left: 9px;

    margin-bottom: 4px;
}

</style>
""", unsafe_allow_html=True)


# =========================
# API 설정
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
    "📋 박스오피스 TOP 10"
)


table = df.head(10).copy()


# =========================
# 순위 변동 표시
# =========================

def make_arrow(value):

    if pd.isna(value):
        return "-"

    if value > 0:
        return "↑"

    elif value < 0:
        return "↓"

    return "-"


# =========================
# HTML 표 만들기
# =========================

html = """
<div class="movie-table-box">

<table class="movie-table">

<thead>

<tr>
<th>순위</th>
<th>영화명</th>
<th>개봉일</th>
<th>관객수</th>
<th>누적관객</th>
<th>스크린수</th>
<th>순위변동</th>
</tr>

</thead>

<tbody>
"""


# 순위별 색상

rank_colors = [
    "#ff3b30",
    "#ff9500",
    "#ffd60a",
    "#34c759",
    "#00c7be",
    "#30a9de",
    "#5856d6",
    "#af52de",
    "#ff2d55",
    "#ff6b6b"
]


for _, row in table.iterrows():

    rank = int(row["rank"])

    color = rank_colors[rank - 1]

    # 순위 변동

    change = make_arrow(row["rankInten"])

    if change == "↑":

        change_html = (
            '<span class="up">↑</span>'
        )

    elif change == "↓":

        change_html = (
            '<span class="down">↓</span>'
        )

    else:

        change_html = (
            '<span class="same">−</span>'
        )


    # 순위 강조

    if rank == 1:

        rank_html = (
            f'<span class="rank-1" '
            f'style="color:{color}">🥇</span>'
        )

    elif rank == 2:

        rank_html = (
            f'<span class="rank-2" '
            f'style="color:{color}">🥈</span>'
        )

    elif rank == 3:

        rank_html = (
            f'<span class="rank-3" '
            f'style="color:{color}">🥉</span>'
        )

    else:

        rank_html = (
            f'<span class="rank-normal" '
            f'style="color:{color}">'
            f'{rank}</span>'
        )


    html += f"""

<tr>

<td>
{rank_html}
</td>

<td class="movie-name">
{row["display_movieNm"]}
</td>

<td>
{row["openDt"]}
</td>

<td>
{row["audiCnt"]:,}
</td>

<td>
{row["audiAcc"]:,}
</td>

<td>
{row["scrnCnt"]:,}
</td>

<td>
{change_html}
</td>

</tr>

"""


html += """
</tbody>

</table>

</div>
"""


st.markdown(
    html,
    unsafe_allow_html=True
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
# 그래프
# ==================================================

st.subheader(
    "📊 관객수 TOP 10"
)


g1, g2 = st.columns(2)


# ==================================================
# 왼쪽 — 막대그래프
# ==================================================

with g1:

    st.markdown(
        '<div class="chart-title">'
        '🎞️ 영화별 관객수'
        '</div>',
        unsafe_allow_html=True
    )

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

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(15,5,5,0.75)",

        font=dict(
            color="white",
            size=10
        ),

        height=330,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=20
        ),

        showlegend=False,

        xaxis=dict(
            gridcolor="#3b2020"
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

    st.markdown(
        '<div class="chart-title">'
        '🍿 상위 10편 관객 점유율'
        '</div>',
        unsafe_allow_html=True
    )


    fig2 = px.pie(

        top10,

        names="display_movieNm",

        values="audiCnt",

        hole=0.55,

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

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(15,5,5,0.75)",

        font=dict(
            color="white",
            size=9
        ),

        height=330,

        margin=dict(
            l=5,
            r=5,
            t=10,
            b=10
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)",

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
