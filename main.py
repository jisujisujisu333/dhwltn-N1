import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="영화 흥행 예측기",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 흥행 예측기")
st.write(
    "영화 정보를 이용해 영화의 총 관객 수를 예측하는 "
    "다중 회귀 모델입니다."
)


# =========================================================
# 데이터 주소
# =========================================================
DAILY_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_daily.csv"
)

MOVIES_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)


# =========================================================
# 데이터 불러오기
# =========================================================
@st.cache_data
def load_data():
    daily = pd.read_csv(
        DAILY_URL,
        encoding="utf-8"
    )

    movies = pd.read_csv(
        MOVIES_URL,
        encoding="utf-8"
    )

    return daily, movies


try:
    daily, movies = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.stop()


# =========================================================
# 일별 데이터 기간 확인
# =========================================================
daily["날짜"] = pd.to_numeric(
    daily["날짜"],
    errors="coerce"
)

valid_dates = daily["날짜"].dropna()

if len(valid_dates) > 0:
    start_date = int(valid_dates.min())
    end_date = int(valid_dates.max())

    period_text = (
        f"{start_date // 10000}년 "
        f"{(start_date % 10000) // 100:02d}월 "
        f"{start_date % 100:02d}일"
        " ~ "
        f"{end_date // 10000}년 "
        f"{(end_date % 10000) // 100:02d}월 "
        f"{end_date % 100:02d}일"
    )
else:
    period_text = "기간을 확인할 수 없습니다."


# =========================================================
# 영화코드 정리 및 정렬
# =========================================================
movies["movieCd"] = movies["movieCd"].astype(str)

movies = movies.sort_values(
    "movieCd"
).reset_index(drop=True)


# =========================================================
# 첫 번째 행 표시
# =========================================================
st.subheader("📋 영화 정보 표의 첫 번째 행")

st.dataframe(
    movies.head(1),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 기본 정보
# =========================================================
st.subheader("📅 데이터 기간 및 영화 수")

info1, info2, info3 = st.columns(3)

with info1:
    st.metric(
        "일별 데이터 기준 기간",
        period_text
    )

with info2:
    st.metric(
        "영화 수",
        f"{len(movies):,}편"
    )

with info3:
    st.metric(
        "영화 정보 표 기준",
        "모든 영화 사용"
    )


# =========================================================
# 사용할 변수 선택
# =========================================================
st.subheader("⚙️ 예측에 사용할 변수 선택")

st.write(
    "체크한 변수만 다중 회귀 모델의 입력값으로 사용됩니다. "
    "`총 관객 수`는 예측 대상이므로 선택할 수 없습니다."
)


# 사용할 수 있는 변수
candidate_variables = [
    "openDt",
    "genre",
    "nation",
    "first_scrn",
    "first_show",
    "first_date",
    "peak",
    "first_week_audi",
    "days_in_top10"
]

variable_names = {
    "openDt": "개봉일",
    "genre": "장르",
    "nation": "국가",
    "first_scrn": "첫 관측일 스크린수",
    "first_show": "첫 관측일 상영횟수",
    "first_date": "10위권 첫 등장일",
    "peak": "성수기 개봉 여부",
    "first_week_audi": "첫 주 관객",
    "days_in_top10": "10위권 유지일수"
}


# 기본으로 선택할 변수
default_variables = [
    "genre",
    "nation",
    "first_scrn",
    "first_show",
    "peak",
    "first_week_audi",
    "days_in_top10"
]

selected_variables = []

cols = st.columns(3)

for i, variable in enumerate(candidate_variables):
    with cols[i % 3]:
        checked = st.checkbox(
            variable_names[variable],
            value=variable in default_variables,
            key=f"check_{variable}"
        )

        if checked:
            selected_variables.append(variable)


if len(selected_variables) == 0:
    st.warning("예측에 사용할 변수를 하나 이상 선택하세요.")
    st.stop()


# =========================================================
# 날짜 변수 처리
# =========================================================
model_df = movies.copy()

# 개봉일 → 연/월/일 관련 숫자 변수
if "openDt" in selected_variables:
    open_date = pd.to_datetime(
        model_df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    model_df["openDt_year"] = open_date.dt.year
    model_df["openDt_month"] = open_date.dt.month
    model_df["openDt_day"] = open_date.dt.day

    model_df = model_df.drop(columns=["openDt"])

# 10위권 첫 등장일 → 연/월/일 관련 숫자 변수
if "first_date" in selected_variables:
    first_date = pd.to_datetime(
        model_df["first_date"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    model_df["first_date_year"] = first_date.dt.year
    model_df["first_date_month"] = first_date.dt.month
    model_df["first_date_day"] = first_date.dt.day

    model_df = model_df.drop(columns=["first_date"])


# =========================================================
# 영화코드 순서 기준 테스트 / 학습 데이터 분리
# =========================================================
# 10편씩 묶어서 각 묶음의 앞 3편 → 테스트
# 나머지 7편 → 학습
model_df["순번"] = np.arange(len(model_df))

test_mask = (model_df["순번"] % 10) < 3

test_df = model_df[test_mask].copy()
train_df = model_df[~test_mask].copy()


# =========================================================
# 선택 변수에 실제 모델용 날짜 변수 반영
# =========================================================
model_features = []

for variable in selected_variables:

    if variable == "openDt":
        model_features.extend([
            "openDt_year",
            "openDt_month",
            "openDt_day"
        ])

    elif variable == "first_date":
        model_features.extend([
            "first_date_year",
            "first_date_month",
            "first_date_day"
        ])

    else:
        model_features.append(variable)


# 존재하는 변수만 사용
model_features = [
    col for col in model_features
    if col in model_df.columns
]


target = "total_audi"


# =========================================================
# X / y 생성
# =========================================================
X_train = train_df[model_features].copy()
y_train = pd.to_numeric(
    train_df[target],
    errors="coerce"
)

X_test = test_df[model_features].copy()
y_test = pd.to_numeric(
    test_df[target],
    errors="coerce"
)

# 총 관객 수가 없는 행 제거
train_valid = y_train.notna()
test_valid = y_test.notna()

X_train = X_train.loc[train_valid]
y_train = y_train.loc[train_valid]

X_test = X_test.loc[test_valid]
y_test = y_test.loc[test_valid]

test_movies = test_df.loc[test_valid].copy()


# =========================================================
# 숫자형 / 문자형 변수 구분
# =========================================================
numeric_features = X_train.select_dtypes(
    include=["number"]
).columns.tolist()

categorical_features = X_train.select_dtypes(
    exclude=["number"]
).columns.tolist()


# =========================================================
# 전처리
# =========================================================
numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)

categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numeric_transformer,
            numeric_features
        ),
        (
            "cat",
            categorical_transformer,
            categorical_features
        )
    ]
)


# =========================================================
# 다중 회귀 모델
# =========================================================
model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "regression",
            LinearRegression()
        )
    ]
)


# =========================================================
# 학습
# =========================================================
model.fit(
    X_train,
    y_train
)


# =========================================================
# 테스트 데이터 예측
# =========================================================
predicted = model.predict(X_test)

# 음수 예측값 방지
predicted = np.maximum(
    predicted,
    0
)


# =========================================================
# 평가
# =========================================================
r2 = r2_score(
    y_test,
    predicted
)

mae = mean_absolute_error(
    y_test,
    predicted
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predicted
    )
)

# 평균 절대 백분율 오차
nonzero_mask = y_test != 0

if nonzero_mask.sum() > 0:
    mape = np.mean(
        np.abs(
            (
                y_test[nonzero_mask].to_numpy()
                - predicted[nonzero_mask]
            )
            / y_test[nonzero_mask].to_numpy()
        )
    ) * 100
else:
    mape = np.nan


# =========================================================
# 평가 결과
# =========================================================
st.subheader("📊 모델 학습 및 평가 결과")

result1, result2, result3, result4 = st.columns(4)

with result1:
    st.metric(
        "학습에 사용한 영화",
        f"{len(X_train):,}편"
    )

with result2:
    st.metric(
        "평가한 영화",
        f"{len(X_test):,}편"
    )

with result3:
    st.metric(
        "평가 점수 (R²)",
        f"{r2:.3f}"
    )

with result4:
    st.metric(
        "평균 절대 오차",
        f"{mae:,.0f}명"
    )

st.write(
    f"**RMSE:** {rmse:,.0f}명"
)

st.write(
    f"**평균 절대 백분율 오차(MAPE):** "
    f"{mape:.2f}%"
    if not np.isnan(mape)
    else "**평균 절대 백분율 오차(MAPE):** 계산할 수 없습니다."
)

st.write(
    "**평가 점수(R²)**는 학습에 사용하지 않은 테스트 영화의 "
    "실제 총 관객 수와 예측값이 얼마나 잘 맞는지를 나타냅니다."
)


# =========================================================
# 사용 변수 표시
# =========================================================
st.subheader("🔎 현재 회귀 모델에 사용한 변수")

selected_names = [
    variable_names[v]
    for v in selected_variables
]

st.write(
    " · ".join(selected_names)
)


# =========================================================
# 테스트 영화 예측 결과
# =========================================================
result_df = pd.DataFrame({
    "영화코드": test_movies["movieCd"].values,
    "영화명": test_movies["movieNm"].values,
    "실제 총 관객 수": y_test.values,
    "예측 총 관객 수": predicted
})

result_df["예측 오차"] = (
    result_df["예측 총 관객 수"]
    - result_df["실제 총 관객 수"]
)

result_df["절대 오차"] = (
    result_df["예측 오차"].abs()
)

result_df = result_df.sort_values(
    "영화코드"
).reset_index(drop=True)


st.subheader("🎞️ 테스트 영화의 실제값과 예측값")

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 1,000명 미만 예측 영화
# =========================================================
under_1000 = predicted < 1000
under_1000_count = int(under_1000.sum())

st.subheader("📉 1,000명 미만 예측")

st.write(
    f"예측 총 관객 수가 1,000명보다 작게 나온 영화는 "
    f"**{under_1000_count}편**입니다."
)


# =========================================================
# 산점도
# =========================================================
st.subheader("📈 실제 관객 수와 예측 관객 수")

# 로그 그래프에서 1,000명 미만 예측값은 1,000에 붙임
plot_predicted = np.maximum(
    predicted,
    1000
)

actual_values = y_test.to_numpy()

# 대각선 범위
min_value = max(
    1000,
    min(
        actual_values.min(),
        plot_predicted.min()
    )
)

max_value = max(
    actual_values.max(),
    plot_predicted.max()
)

diagonal_x = np.array([
    min_value,
    max_value
])

diagonal_y = diagonal_x.copy()


fig = go.Figure()


# 실제값-예측값 산점도
fig.add_trace(
    go.Scatter(
        x=actual_values,
        y=plot_predicted,
        mode="markers",
        name="테스트 영화",
        customdata=np.column_stack([
            test_movies["movieCd"].values,
            test_movies["movieNm"].values,
            y_test.values,
            predicted
        ]),
        marker=dict(
            size=9,
            opacity=0.75
        ),
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>"
            "영화코드: %{customdata[0]}<br>"
            "실제 관객: %{customdata[2]:,.0f}명<br>"
            "예측 관객: %{customdata[3]:,.0f}명"
            "<extra></extra>"
        )
    )
)


# 실제값 = 예측값 대각선
fig.add_trace(
    go.Scatter(
        x=diagonal_x,
        y=diagonal_y,
        mode="lines",
        name="실제값 = 예측값",
        line=dict(
            dash="dash",
            width=2
        )
    )
)


fig.update_layout(
    xaxis=dict(
        title="실제 총 관객 수",
        type="log",
        range=[
            np.log10(1000),
            np.log10(max_value * 1.1)
        ]
    ),
    yaxis=dict(
        title="예측한 총 관객 수",
        type="log",
        range=[
            np.log10(1000),
            np.log10(max_value * 1.1)
        ]
    ),
    height=650,
    hovermode="closest",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# 분석 조건
# =========================================================
st.subheader("📌 분석 조건")

st.write(
    f"- 일별 데이터 기준 기간: **{period_text}**"
)

st.write(
    f"- 영화 정보 표의 전체 영화: **{len(movies):,}편**"
)

st.write(
    f"- 학습 영화: **{len(X_train):,}편**"
)

st.write(
    f"- 평가 영화: **{len(X_test):,}편**"
)

st.write(
    "- 영화코드 순으로 정렬한 뒤 10편마다 앞의 3편을 "
    "테스트용으로 사용하고, 나머지 7편을 학습용으로 사용"
)

st.write(
    "- 영화 정보 표의 모든 영화를 학습 또는 평가에 사용"
)

st.write(
    "- 테스트 데이터는 모델 학습 과정에 사용하지 않음"
)
