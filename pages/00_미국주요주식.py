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
st.caption("세계 시장을 이끄는 대표 기업들의 최근 1년 성과")

stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Netflix": "NFLX",
    "Samsung": "005930.KS",
    "SK Hynix": "000660.KS"
}

@st.cache_data
def load_data():
    df = yf.download(
        list(stocks.values()),
        period="1y",
        auto_adjust=True,
        progress=False
    )["Close"]

    df.columns = stocks.keys()
    return df

data = load_data()

returns = ((data / data.iloc[0]) - 1) * 100
latest = returns.iloc[-1].sort_values(ascending=False)

# 상단 KPI
c1, c2, c3 = st.columns(3)

c1.metric(
    "🏆 최고 수익률",
    latest.index[0],
    f"{latest.iloc[0]:.1f}%"
)

c2.metric(
    "📈 평균 수익률",
    f"{latest.mean():.1f}%"
)

c3.metric(
    "📊 분석 종목",
    len(stocks)
)

st.divider()

# 누적 수익률
st.subheader("🚀 최근 1년 누적 수익률")

fig = px.line(
    returns,
    x=returns.index,
    y=returns.columns
)

fig.update_layout(
    height=700,
    hovermode="x unified",
    legend_title="종목",
)

st.plotly_chart(fig, use_container_width=True)

# 순위표
st.subheader("🏅 성과 랭킹")

rank_df = pd.DataFrame({
    "순위": range(1, len(latest)+1),
    "기업": latest.index,
    "수익률(%)": latest.values.round(2)
})

st.dataframe(
    rank_df,
    use_container_width=True,
    hide_index=True
)

# 막대그래프
st.subheader("📊 기업별 수익률 비교")

fig_bar = px.bar(
    rank_df,
    x="기업",
    y="수익률(%)",
    text="수익률(%)"
)

fig_bar.update_layout(height=600)

st.plotly_chart(fig_bar, use_container_width=True)

# TOP3
st.subheader("🥇 TOP 3 기업")

top3 = latest.head(3)

col1, col2, col3 = st.columns(3)

for col, (name, value) in zip([col1, col2, col3], top3.items()):
    col.metric(name, f"{value:.1f}%")

st.success(
    f"최근 1년 기준 가장 높은 성과를 기록한 기업은 "
    f"{latest.index[0]} ({latest.iloc[0]:.1f}%) 입니다."
)
