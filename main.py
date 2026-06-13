import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="글로벌 주식 분석기",
    page_icon="📈",
    layout="wide"
)

st.title("📈 글로벌 주식 1년 분석")
st.write("삼성전자, SK하이닉스, 구글, 마이크로소프트, 애플의 최근 1년 주가를 비교합니다.")

tickers = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "구글": "GOOGL",
    "마이크로소프트": "MSFT",
    "애플": "AAPL"
}

@st.cache_data
def load_data():
    data = yf.download(
        list(tickers.values()),
        period="1y",
        auto_adjust=True,
        progress=False
    )["Close"]

    data.columns = tickers.keys()
    return data

data = load_data()

# -----------------------
# 원본 주가 그래프
# -----------------------
st.subheader("📊 최근 1년 주가")

fig_price = px.line(
    data,
    x=data.index,
    y=data.columns,
    labels={"value": "주가", "index": "날짜"},
)

fig_price.update_layout(
    hovermode="x unified",
    height=600
)

st.plotly_chart(fig_price, use_container_width=True)

# -----------------------
# 누적 수익률 계산
# -----------------------
returns = (data / data.iloc[0] - 1) * 100

st.subheader("🚀 누적 수익률 비교 (%)")

fig_return = px.line(
    returns,
    x=returns.index,
    y=returns.columns,
    labels={"value": "수익률 (%)", "index": "날짜"},
)

fig_return.update_layout(
    hovermode="x unified",
    height=600
)

st.plotly_chart(fig_return, use_container_width=True)

# -----------------------
# 성과 분석
# -----------------------
final_returns = returns.iloc[-1].sort_values(ascending=False)

st.subheader("🏆 1년 성과 순위")

rank_df = pd.DataFrame({
    "종목": final_returns.index,
    "수익률(%)": final_returns.values.round(2)
})

st.dataframe(rank_df, use_container_width=True)

best_stock = final_returns.index[0]
best_return = final_returns.iloc[0]

st.success(
    f"최근 1년 동안 가장 높은 수익률을 기록한 종목은 "
    f"'{best_stock}'이며 수익률은 약 {best_return:.2f}% 입니다."
)

# -----------------------
# 변동성 분석
# -----------------------
daily_returns = data.pct_change().dropna()
volatility = daily_returns.std() * (252 ** 0.5) * 100

st.subheader("⚠️ 연간 변동성")

vol_df = pd.DataFrame({
    "종목": volatility.index,
    "변동성(%)": volatility.values.round(2)
})

fig_vol = px.bar(
    vol_df,
    x="종목",
    y="변동성(%)",
)

st.plotly_chart(fig_vol, use_container_width=True)

st.dataframe(vol_df, use_container_width=True)

# -----------------------
# 요약
# -----------------------
st.subheader("📌 투자 인사이트")

highest_return = final_returns.idxmax()
highest_vol = volatility.idxmax()
lowest_vol = volatility.idxmin()

st.markdown(f"""
- 최근 1년 최고 수익률 종목: **{highest_return}**
- 가장 변동성이 큰 종목: **{highest_vol}**
- 가장 안정적인 종목: **{lowest_vol}**
- 미국 빅테크와 한국 반도체 기업의 성과를 한눈에 비교할 수 있습니다.
""")
