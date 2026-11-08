
# --------------------------------------------------
# 디자인 CSS
# --------------------------------------------------

st.markdown("""
<style>
    /* 전체 배경 및 기본 글씨 */
    .stApp {
        background-color: #F4F7FC;
        color: #26364A;
    }

    /* 전체 기본 글씨 색상 */
    p, span, label, li, div {
        color: #26364A;
    }

    /* 제목 */
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #183B66 !important;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 15px;
        color: #52677F !important;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 750;
        color: #234B78 !important;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* 안내 카드 */
    .info-card {
        background-color: #E5EFFB;
        border-left: 5px solid #3978B9;
        padding: 17px 20px;
        border-radius: 10px;
        color: #294968 !important;
        margin-bottom: 22px;
        line-height: 1.7;
    }

    .info-card * {
        color: #294968 !important;
    }

    /* 요약 카드 */
    .summary-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE6F2;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 13px;
        box-shadow: 0 2px 7px rgba(30, 70, 110, 0.04);
    }

    .summary-question {
        font-size: 17px;
        font-weight: 750;
        color: #245384 !important;
        margin-bottom: 10px;
    }

    .summary-answer {
        font-size: 15px;
        color: #26364A !important;
        line-height: 1.8;
        white-space: pre-wrap;
    }

    /* 탭 */
    div[data-baseweb="tab-list"] {
        gap: 10px;
    }

    button[data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 700;
        color: #334B67 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1E5A96 !important;
    }

    /* 입력창 */
    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #26364A !important;
        border: 1px solid #C7D7E9;
        border-radius: 9px;
        caret-color: #245384;
    }

    div[data-testid="stTextArea"] textarea::placeholder {
        color: #8292A5 !important;
    }

    /* 입력창 제목 */
    div[data-testid="stTextArea"] label {
        color: #26364A !important;
    }

    /* 데이터 편집 표 */
    div[data-testid="stDataEditor"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        color: #26364A !important;
    }

    div[data-testid="stDataEditor"] * {
        color: #26364A !important;
    }

    /* 데이터 표 */
    div[data-testid="stDataFrame"] * {
        color: #26364A !important;
    }

    /* 일반 안내 문구 */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #64748B !important;
    }

    /* 버튼 */
    .stButton button {
        border-radius: 8px;
        color: #FFFFFF !important;
        background-color: #3978B9;
        border: none;
    }

    .stButton button:hover {
        background-color: #245B91;
        color: #FFFFFF !important;
    }

    /* 구분선 */
    hr {
        border-color: #D1DDEA;
    }

</style>
""", unsafe_allow_html=True)
