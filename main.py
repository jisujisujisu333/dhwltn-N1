import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# --------------------------------------------------
# 1. 기본 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 어제의 박스오피스")
st.write("한국 시간 기준 어제 하루 동안의 영화 박스오피스입니다.")


# --------------------------------------------------
# 2. 한국 시간 기준으로 '어제' 날짜 계산
# --------------------------------------------------
# 배포 서버가 한국 시간이 아닐 수 있기 때문에
# 서버의 현재 시간이 아니라 한국 시간(KST)을 사용합니다.
kst = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(kst)
yesterday_kst = today_kst - timedelta(days=1)

# KOBIS API에서 사용하는 날짜 형식: YYYYMMDD
target_date = yesterday_kst.strftime("%Y%m%d")

# 화면에 보여줄 날짜
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


# --------------------------------------------------
# 3. KOBIS API 주소
# --------------------------------------------------
API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)


# --------------------------------------------------
# 4. KOBIS API에서 데이터 가져오기
# --------------------------------------------------
# 같은 날짜를 다시 조회하면 1시간 동안 저장된 결과를 사용합니다.
# 따라서 API를 계속 호출하지 않습니다.
@st.cache_data(ttl=3600)
def get_boxoffice(target_dt):
    # Streamlit Cloud의 Secrets에서 인증키를 가져옵니다.
    # 코드에 실제 인증키를 직접 작성하지 않습니다.
    try:
        api_key = st.secrets["KOBIS_KEY"]
    except Exception:
        return {
            "success": False,
            "error": (
                "KOBIS_KEY를 찾을 수 없습니다.\n\n"
                "Streamlit Cloud의 Settings → Secrets에 "
                "KOBIS_KEY를 등록했는지 확인하세요."
            )
        }

    # API에 보낼 요청 정보
    params = {
        "key": api_key,
        "targetDt": target_dt
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=10
        )

        # HTTP 오류가 발생했는지 확인
        response.raise_for_status()

        # JSON 데이터로 변환
        data = response.json()

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": (
                "KOBIS API 요청에 실패했습니다.\n\n"
                "인터넷 연결, KOBIS API 주소 또는 API 서버 상태를 "
                "확인하세요.\n\n"
                f"오류 내용: {e}"
            )
        }

    except ValueError:
        return {
            "success": False,
            "error": (
                "KOBIS API의 응답을 JSON으로 읽을 수 없습니다.\n\n"
                "KOBIS API 서버 상태를 확인하세요."
            )
        }

    # --------------------------------------------------
    # 5. KOBIS API의 faultInfo 확인
    # --------------------------------------------------
    # 인증키가 틀린 경우에도 HTTP 상태코드가 200일 수 있으므로
    # 반드시 faultInfo가 있는지 확인해야 합니다.
    if "faultInfo" in data:
        fault = data["faultInfo"]

        if isinstance(fault, dict):
            fault_message = (
                fault.get("message")
                or fault.get("messageCd")
                or str(fault)
            )
        else:
            fault_message = str(fault)

        return {
            "success": False,
            "error": (
                "KOBIS API에서 오류를 반환했습니다.\n\n"
                "다음 내용을 확인하세요.\n"
                "• 인증키(KOBIS_KEY)가 정확한지\n"
                "• KOBIS API 사용 신청이 정상적으로 되었는지\n"
                "• API 사용 제한에 걸리지 않았는지\n\n"
                f"API 오류: {fault_message}"
            )
        }

    # --------------------------------------------------
    # 6. 영화 목록 가져오기
    # --------------------------------------------------
    try:
        boxoffice_result = data["boxOfficeResult"]
        movie_list = boxoffice_result["dailyBoxOfficeList"]
    except (KeyError, TypeError):
        return {
            "success": False,
            "error": (
                "KOBIS API 응답에서 영화 목록을 찾을 수 없습니다.\n\n"
                "KOBIS API 응답 형식이나 서버 상태를 확인하세요."
            )
        }

    # 영화 목록이 비어 있는 경우
    if not movie_list:
        return {
            "success": False,
            "error": (
                f"{target_dt} 날짜의 영화 박스오피스 데이터가 없습니다.\n\n"
                "조회 날짜에 영화 데이터가 실제로 존재하는지, "
                "KOBIS API가 정상적으로 응답했는지 확인하세요."
            )
        }

    return {
        "success": True,
        "data": movie_list
    }


# --------------------------------------------------
# 7. API 호출
# --------------------------------------------------
result = get_boxoffice(target_date)


# --------------------------------------------------
# 8. 오류가 발생하면 안내 메시지 표시
# --------------------------------------------------
if not result["success"]:
    st.error(result["error"])
    st.info(
        "💡 Streamlit Cloud에서 사용하는 경우 "
        "Settings → Secrets에 다음과 같이 인증키를 등록하세요:\n\n"
        "KOBIS_KEY = \"발급받은_인증키\""
    )
    st.stop()


# --------------------------------------------------
# 9. 영화 데이터를 DataFrame으로 변환
# --------------------------------------------------
df = pd.DataFrame(result["data"])


# --------------------------------------------------
# 10. 숫자로 사용해야 하는 값들을 숫자형으로 변환
# --------------------------------------------------
# KOBIS API에서는 숫자도 문자열로 전달되므로
# 정렬과 그래프에 사용할 수 있도록 숫자로 변환합니다.
number_columns = [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
    "showCnt"
]

for column in number_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0).astype(int)


# --------------------------------------------------
# 11. 순위를 기준으로 정렬
# --------------------------------------------------
df = df.sort_values("rank").reset_index(drop=True)


# --------------------------------------------------
# 12. 조회 날짜 표시
# --------------------------------------------------
st.subheader(f"📅 {display_date} 박스오피스")


# --------------------------------------------------
# 13. 1위 영화 정보
# --------------------------------------------------
first_movie = df.iloc[0]

st.markdown(
    f"## 🥇 1위: {first_movie['movieNm']}"
)

# 지표 카드 3개
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "일일 관객수",
        f"{first_movie['audiCnt']:,}명"
    )

with col2:
    st.metric(
        "누적 관객수",
        f"{first_movie['audiAcc']:,}명"
    )

with col3:
    st.metric(
        "스크린수",
        f"{first_movie['scrnCnt']:,}개"
    )


# --------------------------------------------------
# 14. 관객수 상위 5편 막대그래프
# --------------------------------------------------
st.subheader("📊 관객수 상위 5편")

top5 = (
    df.sort_values("audiCnt", ascending=False)
    .head(5)
    .copy()
)

# 영화명을 인덱스로 설정
chart_data = top5.set_index("movieNm")[["audiCnt"]]

# Streamlit 기본 막대그래프
st.bar_chart(chart_data)


# --------------------------------------------------
# 15. 전체 박스오피스 표
# --------------------------------------------------
st.subheader("🎞️ 전체 박스오피스")

# 화면에 보여줄 열만 선택
table_df = df[
    [
        "rank",
        "movieNm",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt"
    ]
].copy()

# 사용자가 보기 좋은 한국어 열 이름으로 변경
table_df.columns = [
    "순위",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수"
]

# 숫자에 천 단위 쉼표를 표시하기 위한 표시용 DataFrame
display_df = table_df.copy()

display_df["관객수"] = display_df["관객수"].map(
    lambda x: f"{x:,}"
)

display_df["누적관객"] = display_df["누적관객"].map(
    lambda x: f"{x:,}"
)

display_df["스크린수"] = display_df["스크린수"].map(
    lambda x: f"{x:,}"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 16. 데이터 기준 안내
# --------------------------------------------------
st.caption(
    f"조회 기준일: {display_date} | "
    "출처: 영화진흥위원회(KOBIS) 일일 박스오피스 API"
)

st.caption(
    "※ 데이터는 KOBIS API에서 제공하는 일일 박스오피스 집계 결과를 사용합니다."
)
