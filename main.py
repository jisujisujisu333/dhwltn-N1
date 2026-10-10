```python
# main.py — 뇌졸중 예측 실습실: 데이터 소개 첫 화면
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 뇌졸중 예측 실습실")
st.write(
    "건강 기록 5,110명분을 읽어 옵니다. "
    "왼쪽 메뉴에서 페이지를 넘기며 데이터를 살펴보고, 모델을 만들고, 채점합니다."
)

데이터주소 = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"


@st.cache_data
def 데이터_읽기():
    """CSV 파일을 읽어 온다."""
    return pd.read_csv(데이터주소, encoding="utf-8")


df = 데이터_읽기()

# 열 이름에 해당하는 우리말 뜻
우리말뜻 = {
    "id": "개인 식별 번호",
    "gender": "성별",
    "age": "나이",
    "hypertension": "고혈압 여부 (0: 없음, 1: 있음)",
    "heart_disease": "심장병 여부 (0: 없음, 1: 있음)",
    "ever_married": "결혼 여부",
    "work_type": "직업 유형",
    "Residence_type": "거주 지역 유형 (도시 또는 시골)",
    "avg_glucose_level": "평균 혈당 수치",
    "bmi": "체질량지수 (BMI)",
    "smoking_status": "흡연 상태",
    "stroke": "뇌졸중 발생 여부 (0: 없음, 1: 있음)"
}

st.subheader("한눈에 보기")

칸1, 칸2, 칸3, 칸4 = st.columns(4)

칸1.metric("전체 사람 수", f"{len(df):,}명")
칸2.metric("열 개수", f"{df.shape[1]}개")
칸3.metric("뇌졸중을 겪은 사람", f"{int(df['stroke'].sum()):,}명")
칸4.metric("뇌졸중 발생 비율", f"{df['stroke'].mean() * 100:.2f}%")

st.subheader("열마다 무엇이 들어 있는가")
st.caption("각 열의 영어 이름과 우리말 뜻을 확인하세요.")


def 값의_종류(열):
    """숫자 범위 또는 실제 값의 종류를 표시한다."""
    칸 = df[열].dropna()

    if len(칸) == 0:
        return "값 없음"

    if pd.api.types.is_numeric_dtype(칸) and 칸.nunique() > 2:
        return f"숫자 {칸.min():g} ~ {칸.max():g}"

    값들 = sorted(칸.unique().astype(str))
    return f"{len(값들)}가지 · " + " · ".join(값들)


열설명 = pd.DataFrame({
    "열 이름": df.columns,
    "우리말 뜻": [
        우리말뜻.get(열, "뜻 확인 필요")
        for 열 in df.columns
    ],
    "값의 종류": [
        값의_종류(열)
        for 열 in df.columns
    ],
    "빈 값 개수": [
        int(df[열].isna().sum())
        for 열 in df.columns
    ]
})

st.dataframe(
    열설명,
    width="stretch",
    hide_index=True
)

st.subheader("앞 다섯 줄 그대로 보기")
st.dataframe(
    df.head(5),
    width="stretch",
    hide_index=True
)

st.subheader("이 데이터는 어디서 왔는가")

출처_기본값 = """출처: 캐글 Stroke Prediction Dataset (게시자 fedesoriano, 2021-01-26 공개)
원본 주소: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
라이선스: Data files © Original Authors
게시자가 적은 문구: (Confidential Source) - Use only for educational purposes
이 수업에서는 교육 목적으로만 사용합니다."""

st.text_area(
    "데이터 출처",
    value=출처_기본값,
    height=170
)

st.caption(
    "이 데이터는 교육 목적으로만 사용합니다. "
    "데이터의 출처와 한계를 고려해야 하며, "
    "이 데이터로 만든 예측 결과를 실제 의학적 판단에 사용해서는 안 됩니다."
)
```
