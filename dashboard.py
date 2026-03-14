"""
AI Trading Crew — Full Trading Terminal
TradingView-style charts + Fundamental Analysis + Agent Decisions + Portfolio

Run: streamlit run dashboard.py
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import asyncio
import json

# ─── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Trading Crew",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for dark trading terminal look ────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .metric-card {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 16px;
        margin: 4px 0;
    }
    .agent-card {
        background: #1a1f2e;
        border-left: 3px solid #4a9eff;
        padding: 12px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
    }
    .buy-signal { border-left-color: #00c853 !important; }
    .sell-signal { border-left-color: #ff1744 !important; }
    .hold-signal { border-left-color: #ffc107 !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f2e;
        border-radius: 4px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ─────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_stock_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch stock data with caching."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    return df


@st.cache_data(ttl=300)
def get_stock_info(symbol: str) -> dict:
    """Fetch stock info with caching."""
    ticker = yf.Ticker(symbol)
    return ticker.info


@st.cache_data(ttl=300)
def get_financials(symbol: str) -> dict:
    """Fetch financial statements."""
    ticker = yf.Ticker(symbol)
    try:
        return {
            "income": ticker.quarterly_income_stmt,
            "balance": ticker.quarterly_balance_sheet,
            "cashflow": ticker.quarterly_cashflow,
        }
    except Exception:
        return {"income": pd.DataFrame(), "balance": pd.DataFrame(), "cashflow": pd.DataFrame()}


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all technical indicators."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    # Moving Averages
    df["SMA_20"] = close.rolling(20).mean()
    df["SMA_50"] = close.rolling(50).mean()
    df["SMA_200"] = close.rolling(200).mean()
    df["EMA_12"] = close.ewm(span=12).mean()
    df["EMA_26"] = close.ewm(span=26).mean()

    # MACD
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df["BB_Mid"] = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + (bb_std * 2)
    df["BB_Lower"] = df["BB_Mid"] - (bb_std * 2)

    # Stochastic
    low_14 = low.rolling(14).min()
    high_14 = high.rolling(14).max()
    df["Stoch_K"] = 100 * (close - low_14) / (high_14 - low_14)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()

    # ATR
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    # VWAP
    df["VWAP"] = (df["Volume"] * (high + low + close) / 3).cumsum() / df["Volume"].cumsum()

    # OBV
    obv = [0]
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.append(obv[-1] + df["Volume"].iloc[i])
        elif close.iloc[i] < close.iloc[i-1]:
            obv.append(obv[-1] - df["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["OBV"] = obv

    return df


def create_chart(df: pd.DataFrame, symbol: str, indicators: list) -> go.Figure:
    """Create TradingView-style candlestick chart with indicators."""

    # Determine subplot layout
    has_volume = "Volume" in indicators
    has_macd = "MACD" in indicators
    has_rsi = "RSI" in indicators
    has_stoch = "Stochastic" in indicators

    subplot_count = 1 + sum([has_volume, has_macd, has_rsi, has_stoch])
    row_heights = [0.5]
    if has_volume:
        row_heights.append(0.1)
    if has_macd:
        row_heights.append(0.15)
    if has_rsi:
        row_heights.append(0.12)
    if has_stoch:
        row_heights.append(0.12)

    fig = make_subplots(
        rows=subplot_count, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights,
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name=symbol,
        increasing_line_color="#00c853", decreasing_line_color="#ff1744",
        increasing_fillcolor="#00c853", decreasing_fillcolor="#ff1744",
    ), row=1, col=1)

    # Overlay indicators
    colors = {"SMA_20": "#ff9800", "SMA_50": "#2196f3", "SMA_200": "#e91e63",
              "EMA_12": "#4caf50", "EMA_26": "#f44336"}

    for ind in indicators:
        if ind in colors and ind in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[ind], name=ind,
                line=dict(color=colors[ind], width=1),
            ), row=1, col=1)

    if "Bollinger Bands" in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], name="BB Upper",
                                 line=dict(color="#7c4dff", width=1, dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], name="BB Lower",
                                 line=dict(color="#7c4dff", width=1, dash="dot"),
                                 fill="tonexty", fillcolor="rgba(124,77,255,0.05)"), row=1, col=1)

    if "VWAP" in indicators and "VWAP" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["VWAP"], name="VWAP",
                                 line=dict(color="#00bcd4", width=1, dash="dash")), row=1, col=1)

    # Volume subplot
    current_row = 2
    if has_volume:
        colors_vol = ["#00c853" if c >= o else "#ff1744"
                      for c, o in zip(df["Close"], df["Open"])]
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume",
                             marker_color=colors_vol, opacity=0.7), row=current_row, col=1)
        fig.update_yaxes(title_text="Volume", row=current_row, col=1)
        current_row += 1

    # MACD subplot
    if has_macd:
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                                 line=dict(color="#2196f3", width=1.5)), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"], name="Signal",
                                 line=dict(color="#ff9800", width=1.5)), row=current_row, col=1)
        hist_colors = ["#00c853" if v >= 0 else "#ff1744" for v in df["MACD_Hist"]]
        fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], name="MACD Hist",
                             marker_color=hist_colors, opacity=0.6), row=current_row, col=1)
        fig.update_yaxes(title_text="MACD", row=current_row, col=1)
        current_row += 1

    # RSI subplot
    if has_rsi:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                                 line=dict(color="#ab47bc", width=1.5)), row=current_row, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#ff1744", opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#00c853", opacity=0.5, row=current_row, col=1)
        fig.add_hrect(y0=30, y1=70, fillcolor="rgba(171,71,188,0.05)", line_width=0, row=current_row, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)
        current_row += 1

    # Stochastic subplot
    if has_stoch:
        fig.add_trace(go.Scatter(x=df.index, y=df["Stoch_K"], name="%K",
                                 line=dict(color="#2196f3", width=1.5)), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["Stoch_D"], name="%D",
                                 line=dict(color="#ff9800", width=1.5)), row=current_row, col=1)
        fig.add_hline(y=80, line_dash="dot", line_color="#ff1744", opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=20, line_dash="dot", line_color="#00c853", opacity=0.5, row=current_row, col=1)
        fig.update_yaxes(title_text="Stoch", range=[0, 100], row=current_row, col=1)

    # Layout
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=200 + (subplot_count * 150),
        margin=dict(l=60, r=20, t=40, b=20),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                    font=dict(size=10)),
        font=dict(color="#e0e0e0"),
    )

    fig.update_xaxes(gridcolor="#1e2530", showgrid=True)
    fig.update_yaxes(gridcolor="#1e2530", showgrid=True)

    return fig


def format_large_number(num):
    """Format large numbers (1.5T, 234.5B, etc.)."""
    if num is None:
        return "N/A"
    abs_num = abs(num)
    if abs_num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif abs_num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif abs_num >= 1e6:
        return f"${num/1e6:.2f}M"
    else:
        return f"${num:,.0f}"


# ─── SIDEBAR ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 AI Trading Crew")
    st.markdown("---")

    # Stock selector
    symbol = st.text_input("Stock Symbol", value="AAPL", max_chars=10).upper().strip()

    # Timeframe
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    with col2:
        interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

    st.markdown("---")

    # Indicators
    st.markdown("### Indicators")
    selected_indicators = st.multiselect(
        "Select Indicators",
        ["SMA_20", "SMA_50", "SMA_200", "EMA_12", "EMA_26",
         "Bollinger Bands", "VWAP", "Volume", "MACD", "RSI", "Stochastic"],
        default=["SMA_50", "SMA_200", "Volume", "MACD", "RSI"],
    )

    st.markdown("---")

    # AI Analysis button
    run_ai = st.button("🤖 Run AI Analysis", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### Watchlist")
    watchlist = st.text_area("Symbols (one per line)", "AAPL\nNVDA\nMSFT\nTSLA\nAMZN\nGOOGL\nMETA")
    watchlist_symbols = [s.strip().upper() for s in watchlist.split("\n") if s.strip()]


# ─── MAIN CONTENT ────────────────────────────────────────────────────

# Fetch data
try:
    df = get_stock_data(symbol, period, interval)
    info = get_stock_info(symbol)
    df = calculate_indicators(df)
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data for {symbol}: {e}")
    data_loaded = False

if data_loaded and not df.empty:
    current_price = df["Close"].iloc[-1]
    prev_close = df["Close"].iloc[-2] if len(df) > 1 else current_price
    price_change = current_price - prev_close
    price_change_pct = (price_change / prev_close) * 100

    # ─── Header Bar ──────────────────────────────────────────────
    h1, h2, h3, h4, h5, h6 = st.columns([2, 1, 1, 1, 1, 1])
    with h1:
        company_name = info.get("shortName", symbol)
        st.markdown(f"### {company_name} ({symbol})")
    with h2:
        color = "green" if price_change >= 0 else "red"
        arrow = "▲" if price_change >= 0 else "▼"
        st.metric("Price", f"${current_price:.2f}",
                  f"{arrow} {abs(price_change):.2f} ({abs(price_change_pct):.2f}%)")
    with h3:
        st.metric("Market Cap", format_large_number(info.get("marketCap")))
    with h4:
        st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A'):.1f}" if info.get("trailingPE") else "N/A")
    with h5:
        st.metric("52W High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
    with h6:
        st.metric("52W Low", f"${info.get('fiftyTwoWeekLow', 0):.2f}")

    # ─── Tabs ────────────────────────────────────────────────────
    tab_chart, tab_fundamentals, tab_agents, tab_watchlist = st.tabs(
        ["📊 Chart", "📋 Fundamentals", "🤖 AI Agents", "👀 Watchlist"]
    )

    # ═══ TAB 1: CHART ═══════════════════════════════════════════
    with tab_chart:
        fig = create_chart(df, symbol, selected_indicators)
        st.plotly_chart(fig, use_container_width=True)

        # Quick stats bar
        qs1, qs2, qs3, qs4, qs5, qs6 = st.columns(6)
        with qs1:
            rsi_val = df["RSI"].iloc[-1]
            rsi_color = "🔴" if rsi_val > 70 else "🟢" if rsi_val < 30 else "🟡"
            st.metric("RSI (14)", f"{rsi_color} {rsi_val:.1f}")
        with qs2:
            macd_val = df["MACD"].iloc[-1]
            st.metric("MACD", f"{'🟢' if macd_val > 0 else '🔴'} {macd_val:.2f}")
        with qs3:
            above_50 = "🟢 Above" if current_price > df["SMA_50"].iloc[-1] else "🔴 Below"
            st.metric("vs SMA 50", above_50)
        with qs4:
            above_200 = "🟢 Above" if current_price > df["SMA_200"].iloc[-1] else "🔴 Below"
            st.metric("vs SMA 200", above_200)
        with qs5:
            vol_avg = df["Volume"].rolling(20).mean().iloc[-1]
            vol_ratio = df["Volume"].iloc[-1] / vol_avg if vol_avg > 0 else 0
            st.metric("Vol Ratio", f"{vol_ratio:.2f}x")
        with qs6:
            atr_val = df["ATR"].iloc[-1]
            st.metric("ATR (14)", f"${atr_val:.2f}")

    # ═══ TAB 2: FUNDAMENTALS ════════════════════════════════════
    with tab_fundamentals:
        st.markdown(f"## {info.get('shortName', symbol)} — Fundamental Analysis")

        # Overview
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            st.markdown("### Valuation")
            st.metric("P/E (TTM)", f"{info.get('trailingPE', 0):.1f}" if info.get("trailingPE") else "N/A")
            st.metric("Forward P/E", f"{info.get('forwardPE', 0):.1f}" if info.get("forwardPE") else "N/A")
            st.metric("PEG Ratio", f"{info.get('pegRatio', 0):.2f}" if info.get("pegRatio") else "N/A")
            st.metric("P/B Ratio", f"{info.get('priceToBook', 0):.2f}" if info.get("priceToBook") else "N/A")
            st.metric("P/S Ratio", f"{info.get('priceToSalesTrailing12Months', 0):.2f}" if info.get("priceToSalesTrailing12Months") else "N/A")
            st.metric("EV/EBITDA", f"{info.get('enterpriseToEbitda', 0):.1f}" if info.get("enterpriseToEbitda") else "N/A")

        with f2:
            st.markdown("### Profitability")
            st.metric("Gross Margin", f"{info.get('grossMargins', 0)*100:.1f}%" if info.get("grossMargins") else "N/A")
            st.metric("Operating Margin", f"{info.get('operatingMargins', 0)*100:.1f}%" if info.get("operatingMargins") else "N/A")
            st.metric("Net Margin", f"{info.get('profitMargins', 0)*100:.1f}%" if info.get("profitMargins") else "N/A")
            st.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%" if info.get("returnOnEquity") else "N/A")
            st.metric("ROA", f"{info.get('returnOnAssets', 0)*100:.1f}%" if info.get("returnOnAssets") else "N/A")

        with f3:
            st.markdown("### Growth & Income")
            st.metric("Revenue Growth", f"{info.get('revenueGrowth', 0)*100:.1f}%" if info.get("revenueGrowth") else "N/A")
            st.metric("Earnings Growth", f"{info.get('earningsGrowth', 0)*100:.1f}%" if info.get("earningsGrowth") else "N/A")
            st.metric("EPS (TTM)", f"${info.get('trailingEps', 0):.2f}" if info.get("trailingEps") else "N/A")
            st.metric("Forward EPS", f"${info.get('forwardEps', 0):.2f}" if info.get("forwardEps") else "N/A")
            st.metric("Dividend Yield", f"{info.get('dividendYield', 0)*100:.2f}%" if info.get("dividendYield") else "N/A")
            st.metric("Payout Ratio", f"{info.get('payoutRatio', 0)*100:.1f}%" if info.get("payoutRatio") else "N/A")

        with f4:
            st.markdown("### Financial Health")
            st.metric("Total Cash", format_large_number(info.get("totalCash")))
            st.metric("Total Debt", format_large_number(info.get("totalDebt")))
            st.metric("Debt/Equity", f"{info.get('debtToEquity', 0):.1f}" if info.get("debtToEquity") else "N/A")
            st.metric("Current Ratio", f"{info.get('currentRatio', 0):.2f}" if info.get("currentRatio") else "N/A")
            st.metric("Free Cash Flow", format_large_number(info.get("freeCashflow")))
            st.metric("Op. Cash Flow", format_large_number(info.get("operatingCashflow")))

        st.markdown("---")

        # Financial Statements
        financials = get_financials(symbol)

        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("### Income Statement (Quarterly)")
            if not financials["income"].empty:
                income_display = financials["income"].iloc[:, :4]
                # Format columns
                income_display.columns = [c.strftime("%Y-%m-%d") if hasattr(c, "strftime") else str(c) for c in income_display.columns]
                st.dataframe(income_display.style.format(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x),
                           use_container_width=True, height=400)
            else:
                st.info("No income statement data available")

        with fc2:
            st.markdown("### Balance Sheet (Quarterly)")
            if not financials["balance"].empty:
                balance_display = financials["balance"].iloc[:, :4]
                balance_display.columns = [c.strftime("%Y-%m-%d") if hasattr(c, "strftime") else str(c) for c in balance_display.columns]
                st.dataframe(balance_display.style.format(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x),
                           use_container_width=True, height=400)
            else:
                st.info("No balance sheet data available")

        # Revenue & Earnings chart
        st.markdown("### Revenue & Net Income Trend")
        if not financials["income"].empty:
            income = financials["income"]
            rev_row = None
            ni_row = None
            for idx in income.index:
                if "revenue" in str(idx).lower() and "total" in str(idx).lower():
                    rev_row = idx
                if "net income" in str(idx).lower() and ni_row is None:
                    ni_row = idx

            if rev_row is not None:
                rev_data = income.loc[rev_row].dropna().sort_index()
                fig_rev = go.Figure()
                fig_rev.add_trace(go.Bar(
                    x=[d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in rev_data.index],
                    y=rev_data.values, name="Revenue",
                    marker_color="#4a9eff",
                ))
                if ni_row is not None:
                    ni_data = income.loc[ni_row].dropna().sort_index()
                    fig_rev.add_trace(go.Bar(
                        x=[d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in ni_data.index],
                        y=ni_data.values, name="Net Income",
                        marker_color="#00c853",
                    ))
                fig_rev.update_layout(
                    template="plotly_dark", paper_bgcolor="#0e1117",
                    plot_bgcolor="#0e1117", height=350,
                    barmode="group", legend=dict(orientation="h"),
                )
                st.plotly_chart(fig_rev, use_container_width=True)

        # Company description
        with st.expander("Company Description"):
            st.write(info.get("longBusinessSummary", "No description available."))

    # ═══ TAB 3: AI AGENTS ═══════════════════════════════════════
    with tab_agents:
        st.markdown(f"## 🤖 AI Trading Crew — Analysis for {symbol}")

        if run_ai:
            with st.spinner("Running AI analysis... (this takes 2-5 minutes as agents debate)"):
                try:
                    from config.llm_config import get_decision_client, get_analysis_client, get_manager_client
                    from autogen_agentchat.agents import AssistantAgent
                    from autogen_agentchat.teams import SelectorGroupChat
                    from autogen_agentchat.conditions import MaxMessageTermination
                    from agents.personas.definitions import PERSONAS
                    from agents.head_coach import HEAD_COACH_PROMPT
                    import re

                    DECISION_AGENT_IDS = {
                        "head_coach", "risk_portfolio", "risk_devils_advocate",
                        "risk_compliance", "ta_trend_follower", "fa_value_investor",
                        "macro_fed_watcher", "quant_stat_arb",
                    }

                    decision_client = get_decision_client()
                    analysis_client = get_analysis_client()
                    manager_client = get_manager_client()

                    test_personas = {
                        "ta_trend_follower": PERSONAS["ta_trend_follower"],
                        "fa_value_investor": PERSONAS["fa_value_investor"],
                        "macro_fed_watcher": PERSONAS["macro_fed_watcher"],
                        "risk_portfolio": PERSONAS["risk_portfolio"],
                        "risk_devils_advocate": PERSONAS["risk_devils_advocate"],
                    }

                    agents = []
                    for pid, persona in test_personas.items():
                        safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", persona["name"])
                        safe_name = re.sub(r"_+", "_", safe_name).strip("_")
                        client = decision_client if pid in DECISION_AGENT_IDS else analysis_client
                        agents.append(AssistantAgent(
                            name=safe_name,
                            system_message=persona["system_message"],
                            description=f"{persona['name']} - {persona['team']} team",
                            model_client=client,
                        ))

                    coach = AssistantAgent(
                        name="Head_Coach",
                        system_message=HEAD_COACH_PROMPT,
                        description="Head Coach - makes final decisions",
                        model_client=decision_client,
                    )

                    team = SelectorGroupChat(
                        participants=[coach] + agents,
                        model_client=manager_client,
                        termination_condition=MaxMessageTermination(max_messages=12),
                    )

                    task = (
                        f"Analyze {symbol} (current price: ${current_price:.2f}, "
                        f"P/E: {info.get('trailingPE', 'N/A')}, "
                        f"Market Cap: {format_large_number(info.get('marketCap'))}). "
                        f"Each specialist give your analysis, then Head Coach makes final decision. "
                        f"Be concise — max 300 words each."
                    )

                    messages = []

                    async def run_team():
                        async for msg in team.run_stream(task=task):
                            if hasattr(msg, "source") and hasattr(msg, "content"):
                                messages.append({"source": msg.source, "content": msg.content})

                    asyncio.run(run_team())
                    st.session_state["ai_messages"] = messages
                    st.session_state["ai_symbol"] = symbol

                except Exception as e:
                    st.error(f"Error running AI analysis: {e}")
                    import traceback
                    st.code(traceback.format_exc())

        # Display AI results
        if "ai_messages" in st.session_state and st.session_state.get("ai_symbol") == symbol:
            for msg in st.session_state["ai_messages"]:
                source = msg["source"]
                content = msg["content"]

                # Determine signal color
                content_lower = content.lower()
                if any(w in content_lower for w in ["buy", "bullish", "long"]):
                    signal_class = "buy-signal"
                    signal_emoji = "🟢"
                elif any(w in content_lower for w in ["sell", "bearish", "short"]):
                    signal_class = "sell-signal"
                    signal_emoji = "🔴"
                else:
                    signal_class = "hold-signal"
                    signal_emoji = "🟡"

                with st.expander(f"{signal_emoji} **{source}**", expanded=(source == "Head_Coach")):
                    st.markdown(content)
        else:
            st.info("Click **'🤖 Run AI Analysis'** in the sidebar to get agent recommendations.")

            # Show team overview
            st.markdown("### Your 50-Agent Trading Team")
            from agents.personas.definitions import TEAMS
            for team_key, team_info in TEAMS.items():
                with st.expander(f"**{team_info['name']}** ({len(team_info['members'])} agents)"):
                    for mid in team_info["members"]:
                        from agents.personas.definitions import PERSONAS as P
                        st.markdown(f"- **{P[mid]['name']}**")

    # ═══ TAB 4: WATCHLIST ═══════════════════════════════════════
    with tab_watchlist:
        st.markdown("## 👀 Watchlist")

        watchlist_data = []
        for ws in watchlist_symbols:
            try:
                ws_info = get_stock_info(ws)
                ws_df = get_stock_data(ws, period="5d", interval="1d")
                if not ws_df.empty:
                    ws_price = ws_df["Close"].iloc[-1]
                    ws_prev = ws_df["Close"].iloc[-2] if len(ws_df) > 1 else ws_price
                    ws_change = ((ws_price - ws_prev) / ws_prev) * 100

                    watchlist_data.append({
                        "Symbol": ws,
                        "Name": ws_info.get("shortName", ws)[:20],
                        "Price": f"${ws_price:.2f}",
                        "Change %": f"{'🟢' if ws_change >= 0 else '🔴'} {ws_change:+.2f}%",
                        "Market Cap": format_large_number(ws_info.get("marketCap")),
                        "P/E": f"{ws_info.get('trailingPE', 0):.1f}" if ws_info.get("trailingPE") else "N/A",
                        "52W High": f"${ws_info.get('fiftyTwoWeekHigh', 0):.2f}",
                        "52W Low": f"${ws_info.get('fiftyTwoWeekLow', 0):.2f}",
                    })
            except Exception:
                watchlist_data.append({"Symbol": ws, "Name": "Error", "Price": "N/A",
                                      "Change %": "N/A", "Market Cap": "N/A", "P/E": "N/A",
                                      "52W High": "N/A", "52W Low": "N/A"})

        if watchlist_data:
            wl_df = pd.DataFrame(watchlist_data)
            st.dataframe(wl_df, use_container_width=True, hide_index=True, height=400)

        # Mini charts
        st.markdown("### Quick Charts")
        chart_cols = st.columns(min(len(watchlist_symbols), 3))
        for i, ws in enumerate(watchlist_symbols[:6]):
            col_idx = i % 3
            with chart_cols[col_idx]:
                try:
                    ws_df = get_stock_data(ws, period="3mo", interval="1d")
                    if not ws_df.empty:
                        fig_mini = go.Figure()
                        color = "#00c853" if ws_df["Close"].iloc[-1] >= ws_df["Close"].iloc[0] else "#ff1744"
                        fig_mini.add_trace(go.Scatter(
                            x=ws_df.index, y=ws_df["Close"],
                            fill="tozeroy", fillcolor=f"rgba({','.join(str(int(color[i:i+2], 16)) for i in (1, 3, 5))},0.1)",
                            line=dict(color=color, width=2),
                        ))
                        fig_mini.update_layout(
                            template="plotly_dark", paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117", height=200,
                            title=dict(text=ws, font=dict(size=14)),
                            showlegend=False, margin=dict(l=0, r=0, t=30, b=0),
                            xaxis=dict(visible=False), yaxis=dict(visible=False),
                        )
                        st.plotly_chart(fig_mini, use_container_width=True)
                except Exception:
                    st.caption(f"{ws}: Error loading chart")

else:
    st.warning(f"No data available for '{symbol}'. Check the symbol and try again.")
