# ==================================================
# 순위표 10위
# ==================================================

st.subheader("📋 박스오피스 순위표 TOP 10")

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


table["rankInten"] = table["rankInten"].apply(make_arrow)


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
    "#ff3b30",  # 빨강
    "#ff9500",  # 주황
    "#ffcc00",  # 노랑
    "#34c759",  # 초록
    "#00c7be",  # 청록
    "#30a9de",  # 파랑
    "#5856d6",  # 보라
    "#af52de",  # 자주
    "#ff2d55",  # 분홍
    "#ff6b6b"   # 연빨강
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


# 순위 변동 색상
def color_arrow(value):

    if value == "↑":
        return "color: #ff3b30; font-weight: bold; font-size: 16px;"

    elif value == "↓":
        return "color: #30a9de; font-weight: bold; font-size: 16px;"

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
