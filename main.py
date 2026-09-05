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

# =========================
# 전체 디자인
# =========================
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 50% 0%, #245d91 0%, #102f50 30%,
        #071b31 65%, #020914 100%);
    color: white;
}

h1 {
    color: #6edcff !important;
    font-weight: 900;
}

h2, h3 {
    color: #ffffff !important;
    font-weight: 800;
}

.stCaption {
    color: #a9d8f5 !important;
}

/* 날짜 선택 */
[data-testid="stDateInput"] {
    background: rgba(12, 42, 70, 0.9);
    border: 1px solid #3289c7;
    border-radius: 12px;
}

/* TOP 3 */
.top3-container {
    display: flex;
    gap: 15px;
    margin: 8px 0 20px 0;
}

.top3-card {
    flex: 1;
    min-height: 120px;
    padding: 16px;
    border-radius: 18px;
    background: linear-gradient(
        145deg,
        rgba(22, 82, 126, 0.95),
        rgba(6, 25, 45, 0.98)
    );
    box-shadow: 0 8px 25px rgba(0,0,0,0.45);
}

.top3-card.first {
    border: 2px solid #ffd84d;
    background: linear-gradient(
        145deg,
        #385c82,
        #102b48
    );
    box-shadow: 0 0 25px rgba(255,216,77,0.25);
}

.top3-card.second {
    border: 2px solid #bde8ff;
    background: linear-gradient(
        145deg,
        #236b91,
        #102b48
    );
}

.top3-card.third {
    border: 2px solid #ffb36b;
    background: linear-gradient(
        145deg,
        #315f83,
        #172b45
    );
}

.top3-rank {
    font-size: 27px;
    font-weight: 900;
    margin-bottom: 7px;
}

.top3-title {
    font-size: 18px;
    font-weight: 900;
    color: white;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.top3-info {
    color: #b9e5ff;
    font-size: 12px;
    margin-top: 9px;
}

/* 영화 테이블 */
.movie-table-box {
    background: linear-gradient(
        145deg,
        rgba(11, 43, 70, 0.98),
        rgba(3, 15, 29, 0.98)
    );
    border: 1px solid #286d9e;
    border-radius: 17px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.55);
}

.movie-table {
    width: 100%;
    border-collapse: collapse;
    color: #eaf8ff;
    font-size: 13px;
}

.movie-table thead {
    background: linear-gradient(
        90deg,
        #0d4c75,
        #1689c4,
        #0d4c75
    );
}

.movie-table th {
    color: white;
    font-weight: 900;
    padding: 12px 8px;
    text-align: center;
}

.movie-table td {
    padding: 9px 8px;
    text-align: center;
    border-bottom: 1px solid rgba(70,160,210,0.2);
}

.movie-table tbody tr:nth-child(odd) {
    background: rgba(21, 74, 110, 0.25);
}

.movie-table tbody tr:nth-child(even) {
    background: rgba(4, 30, 52, 0.4);
}

.movie-table tbody tr:hover {
    background: rgba(54, 184, 255, 0.18);
}

.movie-name {
    text-align: left !important;
    font-weight: 700;
    color: #f1fbff;
}

/* 순위 */
.rank-normal {
    font-weight: 900;
    color: #6edcff;
}

.rank-1 {
    font-size: 22px;
    color: #ffd84d;
}

.rank-2 {
    font-size: 20px;
    color: #d5efff;
}

.rank-3 {
    font-size: 19px;
    color: #ffb36b;
}

/* 순위 변동 */
.up {
    color: #ff657a;
    font-size: 19px;
    font-weight: 900;
}

.down {
    color: #55bfff;
    font-size: 19px;
    font-weight: 900;
}

.same {
    color: #829caf;
    font-size: 18px;
}

/* 그래프 제목 */
.chart-title {
    color: #ffffff;
    font-size: 17px;
    font-weight: 900;
    border-left: 5px solid #4fd4ff;
    padding-left: 10px;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# API
# =========================
API_KEY = st.secrets["KOBIS_KEY"]

URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

KST = datetime.timezone(datetime.timedelta(hours=9))

yesterday = (
    datetime.datetime.now(KST).date()
    - datetime.timedelta(days=1)
)

selected_date = st.date_input(
    "📅 조회할 날짜",
    value=yesterday,
    max_value=yesterday
)

target_dt = selected_date.strftime("%Y%m%d")


@st.cache_data(ttl=3600)
def fetch_boxoffice(date_str):
    params = {
        "key": API_KEY,
        "targetDt": date_str,
        "itemPerPage": 10
    }

    response = requests.get(
        URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()
    return response.json()


# =========================
# 제목
# =========================
st.title("🎬 일별 박스오피스")
st.caption(f"조회 날짜: {selected_date} · 한국 시간 기준")


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


if "faultInfo" in data:
    st.error(
        f"API 오류: "
        f"{data['faultInfo'].get('message', '')}"
    )
    st.info("secrets의 KOBIS_KEY 값을 확인해 주세요.")
    st.stop()


movies = (
    data
    .get("boxOfficeResult", {})
    .get("dailyBoxOfficeList", [])
)


if not movies:
    st.warning("그날은 아직 집계 전입니다")
    st.stop()


# =========================
# 데이터 정리
# =========================
df = pd.DataFrame(movies)

for col in [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt"
]:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = (
    df
    .sort_values("rank")
    .reset_index(drop=True)
)


def make_movie_name(row):
    if row["rank"] <= 5:
        return "🏆 " + row["movieNm"]
    return row["movieNm"]


df["display_movieNm"] = df.apply(
    make_movie_name,
    axis=1
)


# =========================
# TOP 3
# =========================
st.subheader("🏆 오늘의 TOP 3")

top3 = df.head(3)

medals = ["🥇", "🥈", "🥉"]
classes = ["first", "second", "third"]

top3_parts = [
    '<div class="top3-container">'
]

for i, (_, row) in enumerate(top3.iterrows()):
    top3_parts.append(
        f'<div class="top3-card {classes[i]}">'
        f'<div class="top3-rank">'
        f'{medals[i]} {int(row["rank"])}위'
        f'</div>'
        f'<div class="top3-title">'
        f'{row["movieNm"]}'
        f'</div>'
        f'<div class="top3-info">'
        f'오늘 관객 {int(row["audiCnt"]):,}명'
        f'　·　'
        f'누적 {int(row["audiAcc"]):,}명'
        f'</div>'
        f'</div>'
    )

top3_parts.append("</div>")

st.markdown(
    "".join(top3_parts),
    unsafe_allow_html=True
)


# =========================
# 1위 정보
# =========================
top = df.iloc[0]

st.subheader(
    f"🥇 1위 — {top['movieNm']}"
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "🎟️ 오늘 관객수",
    f"{int(top['audiCnt']):,}명"
)

c2.metric(
    "🍿 누적 관객수",
    f"{int(top['audiAcc']):,}명"
)

c3.metric(
    "🎞️ 스크린수",
    f"{int(top['scrnCnt']):,}개"
)


# =========================
# TOP 10 테이블
# =========================
st.subheader("📋 박스오피스 TOP 10")

table = df.head(10).copy()


def make_arrow(value):
    if pd.isna(value):
        return "-"

    if value > 0:
        return "↑"

    if value < 0:
        return "↓"

    return "-"


html_parts = [
    '<div class="movie-table-box">',
    '<table class="movie-table">',
    '<thead>',
    '<tr>',
    '<th>순위</th>',
    '<th>영화명</th>',
    '<th>개봉일</th>',
    '<th>관객수</th>',
    '<th>누적관객</th>',
    '<th>스크린수</th>',
    '<th>순위변동</th>',
    '</tr>',
    '</thead>',
    '<tbody>'
]


for _, row in table.iterrows():

    rank = int(row["rank"])
    change = make_arrow(row["rankInten"])

    if rank == 1:
        rank_html = '<span class="rank-1">🥇</span>'

    elif rank == 2:
        rank_html = '<span class="rank-2">🥈</span>'

    elif rank == 3:
        rank_html = '<span class="rank-3">🥉</span>'

    else:
        rank_html = (
            f'<span class="rank-normal">'
            f'{rank}'
            f'</span>'
        )

    if change == "↑":
        change_html = '<span class="up">↑</span>'

    elif change == "↓":
        change_html = '<span class="down">↓</span>'

    else:
        change_html = '<span class="same">−</span>'

    html_parts.append(
        f'<tr>'
        f'<td>{rank_html}</td>'
        f'<td class="movie-name">'
        f'{row["display_movieNm"]}'
        f'</td>'
        f'<td>{row["openDt"]}</td>'
        f'<td>{int(row["audiCnt"]):,}</td>'
        f'<td>{int(row["audiAcc"]):,}</td>'
        f'<td>{int(row["scrnCnt"]):,}</td>'
        f'<td>{change_html}</td>'
        f'</tr>'
    )


html_parts.extend([
    '</tbody>',
    '</table>',
    '</div>'
])


st.markdown(
    "".join(html_parts),
    unsafe_allow_html=True
)


# =========================
# 그래프
# =========================
top10 = (
    df
    .sort_values(
        "audiCnt",
        ascending=False
    )
    .head(10)
    .copy()
)

st.subheader("📊 관객수 TOP 10")

g1, g2 = st.columns(2)


# =========================
# 그래프 1
# =========================
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
        y="movieNm",
        orientation="h",
        color="movieNm",
        labels={
            "audiCnt": "관객수",
            "movieNm": "영화"
        },
        color_discrete_sequence=[
            "#55d6ff",
            "#45b8f2",
            "#3c9fe0",
            "#5686ff",
            "#756cff",
            "#9a67e8",
            "#c36ee8",
            "#e26fc0",
            "#f2789b",
            "#ff9b6b"
        ]
    )

    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(3,18,34,0.75)",
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
            gridcolor="#24516d"
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


# =========================
# 그래프 2
# =========================
with g2:

    st.markdown(
        '<div class="chart-title">'
        '🍿 TOP 10 관객 점유율'
        '</div>',
        unsafe_allow_html=True
    )

    fig2 = px.pie(
        top10,
        names="movieNm",
        values="audiCnt",
        hole=0.55,
        color="movieNm",
        color_discrete_sequence=[
            "#55d6ff",
            "#45b8f2",
            "#3c9fe0",
            "#5686ff",
            "#756cff",
            "#9a67e8",
            "#c36ee8",
            "#e26fc0",
            "#f2789b",
            "#ff9b6b"
        ]
    )

    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(3,18,34,0.75)",
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
