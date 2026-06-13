import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="글로벌 TOP10 주식",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 글로벌 TOP10 주식 대시보드")
st.caption("최근 1년간 세계 대표 기업들의 주가 성과 분석")

stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Netflix": "NFLX",
    "AMD": "AMD",
    "Broadcom": "AVGO"
}

@st.cache_data(ttl=3600)
def load_data():

    combined = pd.DataFrame()

    progress = st.progress(0)

    total = len(stocks)

    for i, (name, ticker) in enumerate(stocks.items()):

        try:
            df = yf.download(
                ticker,
                period="1y",
                auto_adjust=True,
                progress=False,
                threads=False
            )

            if not df.empty:
                combined[name] = df["Close"]

        except Exception:
            pass

        progress.progress((i + 1) / total)

    progress.empty()

    combined = combined.sort_index()

    # 거래일 차이 보정
    combined = combined.ffill()

    # 전부 비어있는 행 제거
    combined = combined.dropna(how="all")

    return combined


with st.spinner("주가 데이터를 불러오는 중..."):
    data = load_data()

if data.empty:
    st.error("주가 데이터를 가져오지 못했습니다.")
    st.stop()

# -----------------------------
# 누적 수익률 계산
# -----------------------------

returns = ((data / data.iloc[0]) - 1) * 100

latest_returns = returns.iloc[-1].sort_values(ascending=False)

# -----------------------------
# KPI
# -----------------------------

c1, c2, c3 = st.columns(3)

c1.metric(
    "🏆 최고 수익률",
    latest_returns.index[0],
    f"{latest_returns.iloc[0]:.2f}%"
)

c2.metric(
    "📈 평균 수익률",
    f"{latest_returns.mean():.2f}%"
)

c3.metric(
    "📊 분석 종목 수",
    len(data.columns)
)

st.divider()

# -----------------------------
# 원본 주가 그래프
# -----------------------------

st.subheader("📈 최근 1년 주가")

fig_price = px.line(
    data,
    x=data.index,
    y=data.columns,
    template="plotly_dark"
)

fig_price.update_traces(
    connectgaps=True
)

fig_price.update_layout(
    hovermode="x unified",
    height=700,
    legend_title="기업"
)

st.plotly_chart(
    fig_price,
    use_container_width=True
)

# -----------------------------
# 수익률 그래프
# -----------------------------

st.subheader("🚀 누적 수익률 비교")

fig_return = px.line(
    returns,
    x=returns.index,
    y=returns.columns,
    template="plotly_dark"
)

fig_return.update_traces(
    connectgaps=True
)

fig_return.update_layout(
    hovermode="x unified",
    height=700,
    legend_title="기업"
)

st.plotly_chart(
    fig_return,
    use_container_width=True
)

# -----------------------------
# 랭킹
# -----------------------------

st.subheader("🏅 수익률 순위")

rank_df = pd.DataFrame({
    "순위": range(1, len(latest_returns) + 1),
    "기업": latest_returns.index,
    "수익률(%)": latest_returns.values.round(2)
})

st.dataframe(
    rank_df,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# 막대그래프
# -----------------------------

st.subheader("📊 기업별 수익률")

fig_bar = px.bar(
    rank_df,
    x="기업",
    y="수익률(%)",
    text="수익률(%)",
    template="plotly_dark"
)

fig_bar.update_layout(
    height=600
)

st.plotly_chart(
    fig_bar,
    use_container_width=True
)

# -----------------------------
# 변동성 분석
# -----------------------------

daily_returns = data.pct_change().dropna()

volatility = (
    daily_returns.std() *
    (252 ** 0.5) *
    100
).sort_values(ascending=False)

vol_df = pd.DataFrame({
    "기업": volatility.index,
    "변동성(%)": volatility.values.round(2)
})

st.subheader("⚠️ 변동성 분석")

fig_vol = px.bar(
    vol_df,
    x="기업",
    y="변동성(%)",
    text="변동성(%)",
    template="plotly_dark"
)

st.plotly_chart(
    fig_vol,
    use_container_width=True
)

# -----------------------------
# TOP3
# -----------------------------

st.subheader("🥇 TOP 3")

top3 = latest_returns.head(3)

col1, col2, col3 = st.columns(3)

for col, (name, value) in zip(
    [col1, col2, col3],
    top3.items()
):
    col.metric(
        name,
        f"{value:.2f}%"
    )

# -----------------------------
# AI 요약
# -----------------------------

st.subheader("📌 투자 인사이트")

st.info(
    f"""
최근 1년 기준 가장 높은 수익률을 기록한 기업은
{latest_returns.index[0]}이며,
수익률은 {latest_returns.iloc[0]:.2f}%입니다.

가장 변동성이 높은 종목은
{volatility.index[0]}입니다.

변동성이 높은 종목은 큰 수익 가능성과 함께
큰 손실 위험도 존재합니다.
"""
)
