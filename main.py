import re
from itertools import combinations

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="급식 규칙 찾기",
    page_icon="🍱",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/teacher188-netizen/"
    "2026-datascience/refs/heads/main/sangok_meals.csv"
)

st.title("🍱 급식 규칙 찾기")
st.caption(
    "우리 학교 중식 데이터로 메뉴 사이의 연관 규칙을 찾아봅니다."
)


# --------------------------------------------------
# 데이터 읽기
# --------------------------------------------------
@st.cache_data
def load_data(url):
    df = pd.read_csv(url, encoding="utf-8")

    # 열 이름의 앞뒤 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 열 이름은 대소문자 및 공백 차이를 허용
    column_map = {
        re.sub(r"\s+", "", str(col)).lower(): col
        for col in df.columns
    }

    required = ["날짜", "식사", "메뉴"]
    missing = [
        col for col in required
        if re.sub(r"\s+", "", col).lower() not in column_map
    ]

    if missing:
        raise ValueError(
            f"필수 열을 찾을 수 없습니다: {', '.join(missing)}"
        )

    df = df.rename(
        columns={
            column_map["날짜"]: "날짜",
            column_map["식사"]: "식사",
            column_map["메뉴"]: "메뉴",
        }
    )

    df = df[["날짜", "식사", "메뉴"]].copy()
    df["식사"] = df["식사"].astype("string").str.strip()
    df["메뉴"] = df["메뉴"].fillna("").astype(str)
    df["날짜"] = df["날짜"].astype("string").str.strip()

    # 중식만 선택: '중식'이라는 값이 포함된 경우
    lunch = df[
        df["식사"].str.contains("중식", na=False)
    ].copy()

    # 괄호와 괄호 안의 내용 제거
    # 예: 사과(친환경) -> 사과
    # 일반 괄호와 대괄호 형태를 모두 처리
    def clean_menu(name):
        name = str(name).strip()

        previous = None
        while previous != name:
            previous = name
            name = re.sub(r"\([^()]*\)", "", name)
            name = re.sub(r"\[[^\[\]]*\]", "", name)
            name = re.sub(r"（[^（）]*）", "", name)
            name = re.sub(r"【[^【】]*】", "", name)

        return re.sub(r"\s+", " ", name).strip()

    def split_menus(value):
        result = []
        seen = set()

        for raw in value.split("|"):
            menu = clean_menu(raw)

            # 빈 메뉴 및 동일 식단 내 중복 메뉴 제외
            if menu and menu not in seen:
                result.append(menu)
                seen.add(menu)

        return result

    lunch["메뉴목록"] = lunch["메뉴"].map(split_menus)

    # 메뉴가 하나도 없는 식단은 분석에서 제외
    lunch = lunch[lunch["메뉴목록"].map(bool)].reset_index(drop=True)

    return lunch


# --------------------------------------------------
# 연관 규칙 계산
# --------------------------------------------------
@st.cache_data
def make_rules(meal_lists):
    n = len(meal_lists)

    if n == 0:
        return pd.DataFrame(
            columns=[
                "조건", "결과", "동시",
                "지지도", "신뢰도", "향상도",
            ]
        ), {}, 0

    # 메뉴별 등장 일수
    menu_counts = {}
    # 순서가 없는 메뉴 쌍별 동시 등장 일수
    pair_counts = {}

    for menus in meal_lists:
        for menu in menus:
            menu_counts[menu] = menu_counts.get(menu, 0) + 1

        for a, b in combinations(sorted(set(menus)), 2):
            pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1

    rules = []

    for (a, b), count in pair_counts.items():
        support = count / n
        support_a = menu_counts[a] / n
        support_b = menu_counts[b] / n

        # A -> B
        rules.append({
            "조건": a,
            "결과": b,
            "동시": count,
            "지지도": support,
            "신뢰도": count / menu_counts[a],
            "향상도": support / (support_a * support_b),
        })

        # B -> A: 역방향 규칙도 별도 계산
        rules.append({
            "조건": b,
            "결과": a,
            "동시": count,
            "지지도": support,
            "신뢰도": count / menu_counts[b],
            "향상도": support / (support_a * support_b),
        })

    rules_df = pd.DataFrame(rules)

    if not rules_df.empty:
        rules_df = rules_df.sort_values(
            ["향상도", "신뢰도", "동시"],
            ascending=[False, False, False],
        ).reset_index(drop=True)

    return rules_df, menu_counts, len(pair_counts)


# --------------------------------------------------
# 앱 실행
# --------------------------------------------------
try:
    with st.spinner("급식 데이터를 불러오는 중입니다..."):
        meals = load_data(DATA_URL)

except Exception as exc:
    st.error(f"CSV를 읽거나 처리하지 못했습니다: {exc}")
    st.info(
        "인터넷 연결과 CSV 주소, 그리고 날짜·식사·메뉴 열을 확인해 주세요."
    )
    st.stop()

if meals.empty:
    st.warning("분석할 중식 데이터가 없습니다.")
    st.stop()

meal_lists = meals["메뉴목록"].tolist()
rules, menu_counts, pair_count = make_rules(meal_lists)

if rules.empty:
    st.warning(
        "함께 나온 메뉴 쌍이 없습니다. "
        "둘 이상의 메뉴가 포함된 식단이 있는지 확인해 주세요."
    )
    st.stop()


# --------------------------------------------------
# 필터 및 정렬
# --------------------------------------------------
with st.sidebar:
    st.header("🔎 규칙 찾기")

    menu_options = ["전체 메뉴"] + sorted(menu_counts.keys())

    selected_menu = st.selectbox(
        "메뉴 선택",
        menu_options,
        help="선택한 메뉴가 조건 또는 결과에 포함된 규칙만 표시합니다.",
    )

    sort_option = st.selectbox(
        "정렬 기준",
        ["향상도 순", "신뢰도 순", "동시 순"],
    )

    min_count = st.number_input(
        "최소 동시 등장 일수",
        min_value=1,
        max_value=len(meals),
        value=1,
        step=1,
    )

    st.caption(
        "동시 등장 일수는 선택한 조건과 결과 메뉴가 "
        "함께 나온 급식 일수입니다."
    )


# --------------------------------------------------
# 통계
# --------------------------------------------------
filtered = rules[rules["동시"] >= min_count].copy()

if selected_menu != "전체 메뉴":
    filtered = filtered[
        (filtered["조건"] == selected_menu)
        | (filtered["결과"] == selected_menu)
    ].copy()

sort_columns = {
    "향상도 순": ["향상도", "신뢰도", "동시"],
    "신뢰도 순": ["신뢰도", "향상도", "동시"],
    "동시 순": ["동시", "향상도", "신뢰도"],
}

filtered = filtered.sort_values(
    sort_columns[sort_option],
    ascending=[False, False, False],
).reset_index(drop=True)

m1, m2, m3 = st.columns(3)

m1.metric("급식 일수", f"{len(meals):,}일")
m2.metric("메뉴 종류 수", f"{len(menu_counts):,}종")
m3.metric("함께 나온 메뉴 쌍 수", f"{pair_count:,}쌍")

st.divider()


# --------------------------------------------------
# 규칙 표
# --------------------------------------------------
st.subheader("📋 메뉴 연관 규칙")

st.caption(
    f"표시 중인 방향성 규칙: {len(filtered):,}개 · "
    f"정렬: {sort_option}"
)

if filtered.empty:
    st.info("선택한 조건에 해당하는 규칙이 없습니다.")
else:
    display_df = filtered[
        ["조건", "결과", "동시", "지지도", "신뢰도", "향상도"]
    ].copy()

    # 보기 편하도록 비율 지표는 소수점 4자리로 표시
    display_df["지지도"] = display_df["지지도"].map(
        lambda x: f"{x:.4f}"
    )
    display_df["신뢰도"] = display_df["신뢰도"].map(
        lambda x: f"{x:.4f}"
    )
    display_df["향상도"] = display_df["향상도"].map(
        lambda x: f"{x:.4f}"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    st.download_button(
        "📥 현재 규칙 CSV 다운로드",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="급식_연관규칙.csv",
        mime="text/csv",
    )


# --------------------------------------------------
# 향상도 상위 10개 그래프
# --------------------------------------------------
st.divider()
st.subheader("📊 향상도 상위 10개 규칙")

st.caption(
    "현재 메뉴 필터와 최소 동시 등장 일수를 적용한 결과에서 "
    "향상도가 높은 규칙을 표시합니다."
)

top10 = filtered.sort_values(
    ["향상도", "신뢰도", "동시"],
    ascending=[False, False, False],
).head(10).copy()

if top10.empty:
    st.info("그래프로 표시할 규칙이 없습니다.")
else:
    # 조건 -> 결과 방향을 그래프에 명확히 표시
    top10["규칙"] = top10.apply(
        lambda row: f"{row['조건']} → {row['결과']}",
        axis=1,
    )

    # 가로 막대그래프는 위에서 1위가 보이도록 역순으로 정렬
    top10 = top10.sort_values(
        ["향상도", "신뢰도", "동시"],
        ascending=[True, True, True],
    )

    fig = px.bar(
        top10,
        x="향상도",
        y="규칙",
        orientation="h",
        text="향상도",
        hover_data={
            "동시": True,
            "지지도": ":.4f",
            "신뢰도": ":.4f",
            "향상도": ":.4f",
            "규칙": False,
        },
        labels={
            "향상도": "향상도 (Lift)",
            "규칙": "연관 규칙",
            "동시": "동시 등장 일수",
            "지지도": "지지도",
            "신뢰도": "신뢰도",
        },
        title="향상도 상위 10개",
    )

    fig.update_traces(
        texttemplate="%{x:.3f}",
        textposition="outside",
        cliponaxis=False,
    )

    fig.update_layout(
        height=max(350, 45 * len(top10) + 100),
        yaxis_title="",
        xaxis_title="향상도",
        margin=dict(l=10, r=50, t=60, b=30),
    )

    st.plotly_chart(fig, use_container_width=True)

st.caption(
    "해석 팁: 향상도 1은 두 메뉴의 독립적인 등장과 같은 수준, "
    "1 초과는 양의 연관성, 1 미만은 음의 연관성을 뜻합니다. "
    "연관성은 인과관계를 의미하지 않습니다."
)
