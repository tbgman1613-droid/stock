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
st.caption("삼성전자, SK하이닉스, 구글, 마이크로소프트, 애플 비교")

stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "구글": "GOOGL",
    "마이크로소프트": "MSFT",
    "애플": "AAPL"
}


@st.cache_data(ttl=3600)
def load_data():

    result = pd.DataFrame()

    for name, ticker in stocks.items():

        try:

            df = yf.download(
                ticker,
                period="1y",
                auto_adjust=True,
                progress=False,
                threads=False
            )

            if not df.empty:
                result[name] = df["Close"]

        except Exception:
            pass

    result = result.sort_index()

    # 거래일 차이 보정
    result = result.ffill()

    # 빈 행 제거
    result = result.dropna(how="all")

    return result


data = load_data()

if data.empty:
    st.error("주가 데이터를 가져오지 못했습니다.")
    st.stop()

# ------------------------
# 탭 구성
# ------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 원본 주가",
    "🚀 성과 비교",
    "🏆 수익률 순위",
    "⚠️ 변동성"
])

# =====================================================
# 탭1 원본 주가
# =====================================================

with tab1:

    st.subheader("원본 주가")

    selected = st.multiselect(
        "종목 선택",
        data.columns,
        default=list(data.columns)
    )

    fig = px.line(
        data[selected],
        x=data.index,
        y=selected
    )

    fig.update_traces(connectgaps=True)

    fig.update_layout(
        hovermode="x unified",
        height=650
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# 탭2 성과 비교
# =====================================================

with tab2:

    st.subheader("상대 성과 비교")

    normalized = data.div(data.iloc[0]).mul(100)

    fig = px.line(
        normalized,
        x=normalized.index,
        y=normalized.columns
    )

    fig.update_traces(connectgaps=True)

    fig.update_layout(
        hovermode="x unified",
        height=650,
        yaxis_title="시작값 = 100"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "모든 종목을 시작값 100으로 맞춰 성과를 비교합니다."
    )

# =====================================================
# 탭3 수익률 순위
# =====================================================

with tab3:

    returns = (
        data.div(data.iloc[0])
        .subtract(1)
        .multiply(100)
    )

    final_returns = (
        returns.iloc[-1]
        .sort_values(ascending=False)
    )

    rank_df = pd.DataFrame({
        "순위": range(
            1,
            len(final_returns)+1
        ),
        "종목": final_returns.index,
        "수익률(%)": final_returns.values.round(2)
    })

    st.dataframe(
        rank_df,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        rank_df,
        x="종목",
        y="수익률(%)",
        text="수익률(%)"
    )

    fig.update_layout(
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    best_stock = final_returns.index[0]
    best_return = final_returns.iloc[0]

    st.success(
        f"🏆 최근 1년 최고 수익률 종목: "
        f"{best_stock} ({best_return:.2f}%)"
    )

# =====================================================
# 탭4 변동성
# =====================================================

with tab4:

    daily_returns = (
        data.pct_change(fill_method=None)
        .dropna()
    )

    volatility = (
        daily_returns.std()
        * (252 ** 0.5)
        * 100
    ).sort_values(ascending=False)

    vol_df = pd.DataFrame({
        "종목": volatility.index,
        "변동성(%)": volatility.values.round(2)
    })

    st.dataframe(
        vol_df,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        vol_df,
        x="종목",
        y="변동성(%)",
        text="변동성(%)"
    )

    fig.update_layout(
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        f"가장 안정적인 종목: {volatility.idxmin()} | "
        f"가장 변동성이 큰 종목: {volatility.idxmax()}"
    )
