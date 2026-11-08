
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="내가 만든 모델 소개",
    page_icon="📝",
    layout="wide"
)

# --------------------------------------------------
# 디자인 CSS
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FC;
    }

    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #183B66;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 15px;
        color: #64748B;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 750;
        color: #234B78;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .info-card {
        background-color: #E8F1FC;
        border-left: 5px solid #3978B9;
        padding: 17px 20px;
        border-radius: 10px;
        color: #294968;
        margin-bottom: 22px;
        line-height: 1.7;
    }

    .summary-card {
        background-color: white;
        border: 1px solid #DCE6F2;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 13px;
        box-shadow: 0 2px 7px rgba(30, 70, 110, 0.04);
    }

    .summary-question {
        font-size: 17px;
        font-weight: 750;
        color: #245384;
        margin-bottom: 10px;
    }

    .summary-answer {
        font-size: 15px;
        color: #334155;
        line-height: 1.8;
        white-space: pre-wrap;
    }

    div[data-baseweb="tab-list"] {
        gap: 10px;
    }

    button[data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 700;
    }

    div[data-testid="stTextArea"] textarea {
        background-color: white;
        border: 1px solid #D5E1EF;
        border-radius: 9px;
    }

    div[data-testid="stDataEditor"] {
        background-color: white;
        border-radius: 10px;
    }

    .stButton button {
        border-radius: 8px;
    }

    hr {
        border-color: #DCE6F2;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 제목
# --------------------------------------------------

st.markdown(
    '<div class="main-title">📝 내가 만든 모델 소개</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '나만의 예측 모델을 설명하고 평가 결과를 정리해 보자.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="info-card">
    <b>📌 작성 안내</b><br>
    이 페이지는 데이터를 불러오거나 모델을 학습하지 않아.
    앞 페이지에서 확인한 분석 결과를 직접 옮겨 적고,
    모델을 만들면서 알게 된 점을 정리하는 작성지야.
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 작성 항목과 결과 표 초기 상태
# --------------------------------------------------

questions = [
    ("data_description", "무슨 데이터입니까"),
    ("prediction_features", "무엇을 보고 맞힙니까"),
    ("preprocessing_changes", "무엇을 고쳤습니까"),
    ("screening_center_use", "이 모델을 검진센터가 사용해도 됩니까"),
    ("model_limit", "이 모델이 못 하는 것 한 가지")
]

metric_names = [
    "정확도",
    "재현율",
    "F1",
    "찾아낸 환자",
    "헛짚은 사람"
]

if "model_intro_answers" not in st.session_state:
    st.session_state["model_intro_answers"] = {
        key: "" for key, _ in questions
    }

if "model_intro_results" not in st.session_state:
    st.session_state["model_intro_results"] = pd.DataFrame({
        "평가 항목": metric_names,
        "고치기 전": [""] * len(metric_names),
        "고친 뒤": [""] * len(metric_names)
    })


# --------------------------------------------------
# 탭 구성
# --------------------------------------------------

write_tab, summary_tab = st.tabs([
    "✍️ 작성하기",
    "📄 한 장으로 보기"
])


# --------------------------------------------------
# 탭 1: 작성하기
# --------------------------------------------------

with write_tab:

    st.markdown(
        '<div class="section-title">1. 내가 만든 모델 설명</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "각 질문에 답을 여러 줄로 작성해 줘. "
        "아직 정하지 못한 항목은 비워 두어도 돼."
    )

    for index, (key, question) in enumerate(questions, start=1):

        st.markdown(
            f"""
            <div style="
                background-color:#FFFFFF;
                border:1px solid #DCE6F2;
                border-left:4px solid #3978B9;
                border-radius:9px;
                padding:12px 16px;
                margin-top:13px;
                margin-bottom:5px;
            ">
                <span style="color:#3978B9;font-weight:800;">
                    QUESTION {index}
                </span>
                <span style="color:#234B78;font-weight:750;">
                    &nbsp; {question}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.text_area(
            question,
            key=f"answer_{key}",
            height=110,
            placeholder=f"{question}에 대한 내용을 적어 줘.",
            label_visibility="collapsed"
        )

    st.divider()

    st.markdown(
        '<div class="section-title">2. 평가 결과 비교</div>',
        unsafe_allow_html=True
    )

    st.write(
        "앞 페이지에서 확인한 값을 직접 옮겨 적어 줘. "
        "인원수는 명 단위로, 비율은 백분율이나 소수 등 "
        "확인하기 쉬운 형식으로 적으면 돼."
    )

    edited_results = st.data_editor(
        st.session_state["model_intro_results"],
        key="model_intro_results_editor",
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        disabled=["평가 항목"],
        column_config={
            "평가 항목": st.column_config.TextColumn(
                "평가 항목",
                width="medium"
            ),
            "고치기 전": st.column_config.TextColumn(
                "고치기 전",
                width="large"
            ),
            "고친 뒤": st.column_config.TextColumn(
                "고친 뒤",
                width="large"
            )
        }
    )

    st.session_state["model_intro_results"] = edited_results

    st.markdown("""
    <div style="
        background-color:#EAF2FB;
        padding:13px 17px;
        border-radius:9px;
        color:#496783;
        font-size:13px;
        margin-top:15px;
    ">
        💡 입력 내용은 현재 페이지의 세션에서만 사용해.
        별도의 파일 저장이나 외부 전송 기능은 없어.
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# 탭 2: 한 장으로 보기
# --------------------------------------------------

with summary_tab:

    st.markdown(
        '<div class="section-title">📄 내가 만든 모델 소개</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "작성하기 탭에 입력한 내용을 한 화면에 모아 본다."
    )

    for index, (key, question) in enumerate(questions, start=1):

        answer = st.session_state.get(
            f"answer_{key}",
            ""
        )

        if answer and answer.strip():
            answer_html = (
                f'<div class="summary-answer">'
                f'{answer.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}'
                f'</div>'
            )
        else:
            answer_html = (
                '<div style="color:#94A3B8;font-size:14px;">'
                '아직 적지 않음'
                '</div>'
            )

        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-question">
                    {index}. {question}
                </div>
                {answer_html}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-title">6. 평가 결과 비교</div>',
        unsafe_allow_html=True
    )

    results = st.session_state.get(
        "model_intro_results",
        pd.DataFrame({
            "평가 항목": metric_names,
            "고치기 전": [""] * len(metric_names),
            "고친 뒤": [""] * len(metric_names)
        })
    )

    display_results = results.copy()

    for column in ["고치기 전", "고친 뒤"]:
        display_results[column] = display_results[column].apply(
            lambda value: (
                "아직 적지 않음"
                if pd.isna(value) or not str(value).strip()
                else str(value)
            )
        )

    st.dataframe(
        display_results,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("""
    <div style="
        background-color:#EAF2FB;
        padding:13px 17px;
        border-radius:9px;
        color:#496783;
        font-size:13px;
        margin-top:18px;
    ">
        📌 이 화면은 작성한 내용을 확인하기 위한 것이야.
        입력한 내용은 외부로 보내거나 파일로 저장하지 않아.
    </div>
    """, unsafe_allow_html=True)
