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
# 블루 영화 포스터 스타일
# =========================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 50% 0%,
            #183d68 0%,
            #0d223d 30%,
            #071525 65%,
            #03080f 100%
        );

    color: white;
}


/* 제목 */

h1 {
    color: #70cfff !important;
    font-weight: 900;
    letter-spacing: -1px;
}

h2, h3 {
    color: #ffffff !important;
    font-weight: 800;
}


/* 설명 */

.stCaption {
    color: #a9c5dc !important;
}


/* 날짜 */

[data-testid="stDateInput"] {
    background-color: rgba(8, 25, 43, 0.85);
    border: 1px solid #24527c;
    border-radius: 12px;
    padding: 5px;
}


/* 통계 카드 */

[data-testid="stMetric"] {
    background:
        linear-gradient(
            135deg,
            rgba(17, 52, 82, 0.95),
            rgba(5, 18, 31, 0.95)
        );

    border: 1px solid #285d88;
    border-radius: 14px;
    padding: 10px;

    box-shadow:
        0 5px 20px rgba(0, 0, 0, 0.5);
}


[data-testid="stMetricLabel"] {
    color: #a9c5dc !important;
}


[data-testid="stMetricValue"] {
    color: #65c7ff !important;
    font-size: 23px !important;
    font-weight: 800;
}


/* =========================
   TOP 3 카드
   ========================= */

.top3-container {
    display: flex;
    gap: 14px;
    margin: 8px 0 18px 0;
}


.top3-card {
    flex: 1;

    min-height: 105px;

    padding: 14px 16px;

    border-radius: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(18, 55, 88, 0.95),
            rgba(5, 17, 30, 0.98)
        );

    border: 1px solid #285d88;

    box-shadow:
        0 6px 25px rgba(0, 0, 0, 0.5);
}


.top3-card.first {
    border: 2px solid #ffe16b;

    background:
        linear-gradient(
            145deg,
            rgba(60, 65, 43, 0.95),
            rgba(8, 25, 40, 0.98)
        );

    box-shadow:
        0 0 22px rgba(255, 225, 107, 0.18);
}


.top3-card.second {
    border: 2px solid #b9d7e8;
}


.top3-card.third {
    border: 2px solid #cd9b70;
}


.top3-rank {
    font-size: 25px;
    font-weight: 900;
    margin-bottom: 5px;
}


.top3-title {
    font-size: 17px;
    font-weight: 800;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}


.top3-info {
    color: #9ec4df;
    font-size: 12px;
    margin-top: 7px;
}


/* =========================
   영화 순위표
   ========================= */

.movie-table-box {

    background:
        linear-gradient(
            145deg,
            rgba(9, 29, 48, 0.98),
            rgba(3, 11, 19, 0.98)
        );

    border: 1px solid #245477;

    border-radius: 16px;

    overflow: hidden;

    box-shadow:
        0 8px 30px rgba(0, 0, 0, 0.6);

    margin-top: 5px;
}


.movie-table {

    width: 100%;

    border-collapse: collapse;

    color: #e8f5ff;

    font-size: 13px;
}


.movie-table thead {

    background:
        linear-gradient(
            90deg,
            #0b2945,
            #164d78,
            #0b2945
        );
}


.movie-table th {

    color: #ffffff;

    font-weight: 800;

    padding: 11px 8px;

    border-bottom:
        1px solid #3575a5;

    text-align: center;
}


.movie-table td {

    padding: 9px 8px;

    border-bottom:
        1px solid rgba(50, 110, 150, 0.25);

    text-align: center;
}


.movie-name {

    text-align: left !important;

    font-weight: 650;

    color: #edf8ff;
}


.movie-table tbody tr:hover {

    background:
        rgba(55, 160, 220, 0.12);
}


/* 순위 */

.rank-normal {

    font-weight: 800;

    color: #65c7ff;
}


.rank-1 {

    font-size: 20px;

    font-weight: 900;

    color: #ffe16b;
}


.rank-2 {

    font-size: 18px;

    font-weight: 900;

    color: #c9e3f2;
}


.rank-3 {

    font-size: 17px;

    font-weight: 900;

    color: #e2a97a;
}


/* 순위 변화 */

.up {

    color: #ff6b6b;

    font-size: 18px;

    font-weight: 900;
}


.down {

    color: #55b9ff;

    font-size: 18px;

    font-weight: 900;
}


.same {

    color: #7890a3;

    font-size: 17px;
}


/* 그래프 제목 */

.chart-title {

    color: #ffffff;

    font-size: 17px;

    font-weight: 800;

    border-left:
        4px solid #4dbdff;

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


# ==================================================
# TOP 3 크게 표시
# ==================================================

st.subheader("🏆 오늘의 TOP 3")


top3 = df.head(3)


top3_html = """
<div class="top3-container">
"""


medals = ["🥇", "🥈", "🥉"]
classes = ["first", "second", "third"]


for i, (_, row) in enumerate(top3.iterrows()):

    top3_html += f"""
    <div class="top3-card {classes[i]}">

        <div class="top3-rank">
            {medals[i]} {int(row["rank"])}위
        </div>

        <div class="top3-title">
            {row["movieNm"]}
        </div>

        <div class="top3-info">
            오늘 관객 {row["audiCnt"]:,}명
            &nbsp; · &nbsp;
            누적 {row["audiAcc"]:,}명
        </div>

    </div>
    """


top3_html += """
</div>
"""


st.markdown(
    top3_html,
    unsafe_allow_html=True
)


# ==================================================
# 1위 상세 정보
# ==================================================

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


# =========================
# HTML 표
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


rank_colors = [
    "#ffe16b",
    "#c9e3f2",
    "#e2a97a",
    "#65c7ff",
    "#5db7e8",
    "#55a6d9",
    "#4b96c7",
    "#4b8db7",
    "#4783a8",
    "#417999"
]


for _, row in table.iterrows():

    rank = int(row["rank"])

    color = rank_colors[rank - 1]

    change = make_arrow(
        row["rankInten"]
    )


    # 순위 표시

    if rank == 1:

        rank_html = (
            '<span class="rank-1">🥇</span>'
        )

    elif rank == 2:

        rank_html = (
            '<span class="rank-2">🥈</span>'
        )

    elif rank == 3:

        rank_html = (
            '<span class="rank-3">🥉</span>'
        )

    else:

        rank_html = (
            f'<span class="rank-normal" '
            f'style="color:{color}">'
            f'{rank}</span>'
        )


    # 순위 변동

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

        top10.sort_values(
            "audiCnt"
        ),

        x="audiCnt",

        y="display_movieNm",

        orientation="h",

        color="display_movieNm",

        labels={
            "audiCnt": "관객수",
            "display_movieNm": "영화"
        },

        color_discrete_sequence=[
            "#65c7ff",
            "#4db5ef",
            "#45a8df",
            "#3b9bd0",
            "#328fc1",
            "#2c83b2",
            "#2877a3",
            "#246b94",
            "#215f85",
            "#1d5376"
        ]
    )


    fig1.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(3,14,25,0.75)",

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
            gridcolor="#23435b"
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
            "#65c7ff",
            "#4db5ef",
            "#45a8df",
            "#3b9bd0",
            "#328fc1",
            "#2c83b2",
            "#2877a3",
            "#246b94",
            "#215f85",
            "#1d5376"
        ]
    )


    fig2.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(3,14,25,0.75)",

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
