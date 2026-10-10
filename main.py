import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon="🩺",
    layout="wide"
)

# 데이터 주소
데이터주소 = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"


@st.cache_data
def 데이터_읽기():
    return pd.read_csv(데이터주소, encoding="utf-8")


# 데이터 불러오기
df = 데이터_읽기()
df["뇌졸중"] = df["stroke"].map({
    1: "뇌졸중 있음",
    0: "뇌졸중 없음"
})

# 사이드바 네비게이션
with st.sidebar:
    st.title("🩺 뇌졸중 예측")
    st.caption("데이터 분석 실습실")
    st.divider()

    메뉴 = st.radio(
        "페이지 선택",
        [
            "🏠 데이터 소개",
            "🔍 데이터 탐색",
        ],
        label_visibility="collapsed"
    )

# 페이지 1: 데이터 소개
if 메뉴 == "🏠 데이터 소개":
    st.title("🩺 뇌졸중 예측 실습실")
    st.write(
        "건강 기록 데이터를 살펴보고, "
        "데이터 속 특징을 분석하는 실습 공간입니다."
    )

    st.subheader("📊 데이터 기본 정보")

    왼쪽, 가운데, 오른쪽 = st.columns(3)

    with 왼쪽:
        st.metric("전체 데이터 수", f"{len(df):,}명")

    with 가운데:
        st.metric(
            "뇌졸중 경험자",
            f"{int(df['stroke'].sum()):,}명"
        )

    with 오른쪽:
        st.metric(
            "전체 변수 수",
            f"{len(df.columns)}개"
        )

    st.subheader("📋 데이터 미리보기")
    st.dataframe(df.head(10), width="stretch", hide_index=True)

    st.subheader("📖 주요 데이터 설명")

    설명 = pd.DataFrame({
        "변수": [
            "age",
            "avg_glucose_level",
            "bmi",
            "hypertension",
            "heart_disease",
            "smoking_status",
            "stroke"
        ],
        "우리말 뜻": [
            "나이",
            "평균 혈당 수치",
            "체질량지수",
            "고혈압 여부",
            "심장병 여부",
            "흡연 상태",
            "뇌졸중 여부"
        ],
        "설명": [
            "기록된 사람의 나이",
            "평균 혈당 수치",
            "체질량지수이며 빈 값이 있을 수 있음",
            "1은 있음, 0은 없음",
            "1은 있음, 0은 없음",
            "흡연 상태를 나타내는 범주",
            "1은 뇌졸중 있음, 0은 없음"
        ]
    })

    st.dataframe(설명, width="stretch", hide_index=True)

    st.info(
        "왼쪽 사이드바에서 '데이터 탐색'을 선택하면 "
        "그래프와 통계표를 확인할 수 있습니다."
    )

# 페이지 2: 데이터 탐색
elif 메뉴 == "🔍 데이터 탐색":
    st.title("🔍 데이터 탐색")
    st.write(
        "모델을 만들기 전에 데이터를 살펴봅니다. "
        "화면의 값을 교재의 빈 표에 적으세요."
    )

    # 1. 나이와 평균 혈당 분포
    st.subheader("1. 나이와 평균 혈당은 어떻게 퍼져 있는가")

    왼쪽, 오른쪽 = st.columns(2)

    with 왼쪽:
        그림 = px.histogram(
            df,
            x="age",
            nbins=40,
            title="나이 분포",
            labels={"age": "나이", "count": "사람 수"}
        )
        st.plotly_chart(그림, width="stretch")

    with 오른쪽:
        그림 = px.histogram(
            df,
            x="avg_glucose_level",
            nbins=40,
            title="평균 혈당 분포",
            labels={
                "avg_glucose_level": "평균 혈당",
                "count": "사람 수"
            }
        )
        st.plotly_chart(그림, width="stretch")

    # 2. 뇌졸중 경험 여부에 따른 비교
    st.subheader(
        "2. 뇌졸중을 겪은 사람과 겪지 않은 사람은 무엇이 다른가"
    )

    왼쪽, 오른쪽 = st.columns(2)

    with 왼쪽:
        그림 = px.box(
            df,
            x="뇌졸중",
            y="age",
            color="뇌졸중",
            title="나이 비교",
            labels={"age": "나이"}
        )
        st.plotly_chart(그림, width="stretch")

    with 오른쪽:
        그림 = px.box(
            df,
            x="뇌졸중",
            y="avg_glucose_level",
            color="뇌졸중",
            title="평균 혈당 비교",
            labels={"avg_glucose_level": "평균 혈당"}
        )
        st.plotly_chart(그림, width="stretch")

    두무리 = df.groupby("뇌졸중").agg(
        평균_나이=("age", "mean"),
        평균_혈당=("avg_glucose_level", "mean"),
        고혈압_비율=("hypertension", "mean"),
        심장병_비율=("heart_disease", "mean"),
        사람_수=("id", "size")
    ).reset_index()

    두무리["평균_나이"] = 두무리["평균_나이"].round(1)
    두무리["평균_혈당"] = 두무리["평균_혈당"].round(1)
    두무리["고혈압_비율"] = (
        두무리["고혈압_비율"] * 100
    ).round(1).astype(str) + "%"
    두무리["심장병_비율"] = (
        두무리["심장병_비율"] * 100
    ).round(1).astype(str) + "%"

    두무리 = 두무리.rename(columns={
        "뇌졸중": "구분",
        "평균_나이": "평균 나이",
        "평균_혈당": "평균 혈당",
        "고혈압_비율": "고혈압 비율",
        "심장병_비율": "심장병 비율",
        "사람_수": "사람 수"
    })

    st.subheader("📋 뇌졸중 여부별 통계")
    st.dataframe(두무리, width="stretch", hide_index=True)

    # 3. 고혈압과 심장병에 따른 뇌졸중 비율
    st.subheader(
        "3. 고혈압과 심장병이 있으면 뇌졸중 비율이 다른가"
    )

    def 비율표(열, 이름):
        표 = df.groupby(열)["stroke"].mean().reset_index()
        표[열] = 표[열].map({
            1: f"{이름} 있음",
            0: f"{이름} 없음"
        })
        표["뇌졸중 비율(%)"] = (
            표["stroke"] * 100
        ).round(2)

        return 표.rename(
            columns={열: "구분"}
        )[["구분", "뇌졸중 비율(%)"]]

    왼쪽, 오른쪽 = st.columns(2)

    with 왼쪽:
        표 = 비율표("hypertension", "고혈압")
        그림 = px.bar(
            표,
            x="구분",
            y="뇌졸중 비율(%)",
            title="고혈압 여부별 뇌졸중 비율",
            text="뇌졸중 비율(%)",
            color="구분"
        )
        그림.update_traces(textposition="outside")
        st.plotly_chart(그림, width="stretch")

        st.dataframe(표, width="stretch", hide_index=True)

    with 오른쪽:
        표 = 비율표("heart_disease", "심장병")
        그림 = px.bar(
            표,
            x="구분",
            y="뇌졸중 비율(%)",
            title="심장병 여부별 뇌졸중 비율",
            text="뇌졸중 비율(%)",
            color="구분"
        )
        그림.update_traces(textposition="outside")
        st.plotly_chart(그림, width="stretch")

        st.dataframe(표, width="stretch", hide_index=True)

    # 4. BMI 결측값 분석
    st.subheader("4. bmi가 비어 있는 사람들은 누구인가")

    빈사람 = df[df["bmi"].isna()]

    빈값표 = pd.DataFrame({
        "구분": ["bmi가 비어 있는 사람", "전체"],
        "사람 수": [len(빈사람), len(df)],
        "그중 뇌졸중": [
            int(빈사람["stroke"].sum()),
            int(df["stroke"].sum())
        ],
        "뇌졸중 비율(%)": [
            round(빈사람["stroke"].mean() * 100, 2),
            round(df["stroke"].mean() * 100, 2)
        ]
    })

    st.dataframe(빈값표, width="stretch", hide_index=True)

    st.caption(
        "비어 있다는 것도 데이터입니다. "
        "이 사람들을 어떻게 할지는 다음 시간에 정합니다."
    )

    # 5. 흡연 상태 분석
    st.subheader("5. 흡연 상태에는 어떤 값이 적혀 있는가")

    흡연 = df["smoking_status"].value_counts().reset_index()
    흡연.columns = ["흡연 상태", "사람 수"]
    흡연["비율(%)"] = (
        흡연["사람 수"] / len(df) * 100
    ).round(1)

    st.dataframe(흡연, width="stretch", hide_index=True)

    그림 = px.bar(
        흡연,
        x="흡연 상태",
        y="사람 수",
        color="흡연 상태",
        text="사람 수",
        title="흡연 상태별 인원수"
    )
    그림.update_traces(textposition="outside")
    st.plotly_chart(그림, width="stretch")

    st.caption("데이터 탐색을 마쳤습니다. 각 표와 그래프의 특징을 기록해 보세요.")
