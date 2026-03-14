"""
AI Trading Crew — Dashboard
Clean, minimal, Apple-inspired design.
Focused on pipeline results: scan 1,003 stocks, show top picks.

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
import os
import glob

# ─── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Trading Crew",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Apple-inspired minimal CSS ──────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Base */
    .stApp {
        background-color: #fbfbfd;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* Top nav */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 0;
        border-bottom: 1px solid #e8e8ed;
        margin-bottom: 40px;
    }
    .top-nav-brand {
        font-size: 22px;
        font-weight: 600;
        color: #1d1d1f;
        letter-spacing: -0.5px;
    }
    .top-nav-subtitle {
        font-size: 13px;
        color: #86868b;
        font-weight: 400;
    }

    /* Cards */
    .card {
        background: #ffffff;
        border-radius: 18px;
        padding: 28px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
        border: 1px solid #f0f0f5;
        transition: box-shadow 0.2s ease;
    }
    .card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
    }

    /* Stat cards */
    .stat-label {
        font-size: 12px;
        font-weight: 500;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 28px;
        font-weight: 600;
        color: #1d1d1f;
        letter-spacing: -0.5px;
    }
    .stat-value-sm {
        font-size: 20px;
        font-weight: 600;
        color: #1d1d1f;
    }
    .stat-change-up {
        font-size: 14px;
        font-weight: 500;
        color: #34c759;
    }
    .stat-change-down {
        font-size: 14px;
        font-weight: 500;
        color: #ff3b30;
    }

    /* Pick cards */
    .pick-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        border: 1px solid #f0f0f5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .pick-rank {
        font-size: 13px;
        font-weight: 600;
        color: #86868b;
    }
    .pick-name {
        font-size: 18px;
        font-weight: 600;
        color: #1d1d1f;
        margin: 4px 0;
    }
    .pick-ticker {
        font-size: 14px;
        color: #86868b;
        font-weight: 400;
    }
    .pick-price {
        font-size: 24px;
        font-weight: 600;
        color: #1d1d1f;
    }

    /* Confidence bar */
    .confidence-bar-bg {
        background: #f0f0f5;
        border-radius: 6px;
        height: 8px;
        margin: 8px 0;
    }
    .confidence-bar-fill {
        border-radius: 6px;
        height: 8px;
    }
    .confidence-high { background: #34c759; }
    .confidence-med { background: #ff9500; }
    .confidence-low { background: #ff3b30; }

    /* Regime badge */
    .regime-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .regime-bull { background: #e8f5e9; color: #2e7d32; }
    .regime-strong-bull { background: #c8e6c9; color: #1b5e20; }
    .regime-bear { background: #fbe9e7; color: #c62828; }
    .regime-strong-bear { background: #ffcdd2; color: #b71c1c; }
    .regime-neutral { background: #f3f3f8; color: #6e6e73; }
    .regime-volatile { background: #fff3e0; color: #e65100; }

    /* Section headers */
    .section-title {
        font-size: 28px;
        font-weight: 600;
        color: #1d1d1f;
        letter-spacing: -0.5px;
        margin: 40px 0 8px 0;
    }
    .section-subtitle {
        font-size: 15px;
        color: #86868b;
        font-weight: 400;
        margin-bottom: 24px;
    }

    /* Agent verdict */
    .verdict-buy {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        background: #e8f5e9;
        color: #2e7d32;
    }
    .verdict-pass {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        background: #fbe9e7;
        color: #c62828;
    }
    .verdict-watch {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        background: #fff8e1;
        color: #f57f17;
    }

    /* Clean table */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Buttons */
    .stButton > button {
        background: #1d1d1f;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: -0.2px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #424245;
        color: white;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #e8e8ed;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 0;
        border-bottom: 2px solid transparent;
        padding: 12px 24px;
        font-weight: 500;
        color: #86868b;
        font-size: 15px;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: #1d1d1f !important;
        color: #1d1d1f !important;
    }

    /* Metric override */
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1d1d1f;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif;
        color: #86868b;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #1d1d1f;
    }

    /* Divider */
    hr { border-color: #f0f0f5; }
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ─────────────────────────────────────────────────

@st.cache_data(ttl=120)
def get_stock_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    return ticker.history(period=period, interval=interval)

@st.cache_data(ttl=300)
def get_stock_info(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    return ticker.info

@st.cache_data(ttl=300)
def get_financials(symbol: str) -> dict:
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
    close = df["Close"]
    df["SMA_50"] = close.rolling(50).mean()
    df["SMA_200"] = close.rolling(200).mean()
    df["EMA_12"] = close.ewm(span=12).mean()
    df["EMA_26"] = close.ewm(span=26).mean()
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def fmt(num):
    if num is None: return "N/A"
    a = abs(num)
    if a >= 1e12: return f"${num/1e12:.1f}T"
    if a >= 1e9: return f"${num/1e9:.1f}B"
    if a >= 1e6: return f"${num/1e6:.1f}M"
    return f"${num:,.0f}"


def create_sparkline(df, color="#1d1d1f"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"], mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({','.join(str(int(color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))},0.04)",
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), height=120,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig


def create_chart(df, symbol):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name=symbol, increasing_line_color="#34c759", decreasing_line_color="#ff3b30",
        increasing_fillcolor="#34c759", decreasing_fillcolor="#ff3b30",
    ), row=1, col=1)

    if "SMA_50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="50 SMA",
                                 line=dict(color="#007aff", width=1.5)), row=1, col=1)
    if "SMA_200" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_200"], name="200 SMA",
                                 line=dict(color="#af52de", width=1.5)), row=1, col=1)

    vol_colors = ["#34c759" if c >= o else "#ff3b30" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume",
                         marker_color=vol_colors, opacity=0.5), row=2, col=1)

    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                                 line=dict(color="#ff9500", width=1.5)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#ff3b30", opacity=0.3, row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#34c759", opacity=0.3, row=3, col=1)
        fig.update_yaxes(range=[0, 100], row=3, col=1)

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=560, margin=dict(l=50, r=20, t=20, b=20),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                    font=dict(size=12, color="#86868b")),
        font=dict(family="Inter, sans-serif", color="#1d1d1f"),
    )
    fig.update_xaxes(gridcolor="#f0f0f5", showgrid=True, zeroline=False)
    fig.update_yaxes(gridcolor="#f0f0f5", showgrid=True, zeroline=False)

    return fig


def get_latest_report():
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    if not os.path.exists(report_dir):
        return None
    json_files = sorted(glob.glob(os.path.join(report_dir, "*_scan.json")), reverse=True)
    if not json_files:
        return None
    with open(json_files[0]) as f:
        return json.load(f)


def regime_badge(regime_str):
    r = regime_str.lower().replace("_", "-") if regime_str else "neutral"
    cls = "regime-neutral"
    if "strong-bull" in r or "strong_bull" in r: cls = "regime-strong-bull"
    elif "bull" in r: cls = "regime-bull"
    elif "strong-bear" in r or "strong_bear" in r: cls = "regime-strong-bear"
    elif "bear" in r: cls = "regime-bear"
    elif "volatile" in r: cls = "regime-volatile"
    label = regime_str.replace("_", " ").title() if regime_str else "Neutral"
    return f'<span class="regime-badge {cls}">{label}</span>'


# ─── NAV BAR ─────────────────────────────────────────────────────────
st.markdown("""
<div class="top-nav">
    <div>
        <div class="top-nav-brand">AI Trading Crew</div>
        <div class="top-nav-subtitle">1,003 stocks &middot; LSE + US &middot; Long-term investing</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── TABS ─────────────────────────────────────────────────────────────
tab_home, tab_picks, tab_stock, tab_scan = st.tabs([
    "Overview", "Top Picks", "Stock Detail", "Run Scan"
])


# ═══════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════
with tab_home:
    report = get_latest_report()

    if report:
        scan_date = report.get("scan_date", "Unknown")
        regime = report.get("regime", "Unknown")
        picks = report.get("picks", [])
        stocks_scanned = report.get("stocks_scanned", 0)

        # Hero stats
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="card">
                <div class="stat-label">Market Regime</div>
                <div style="margin-top:8px">{regime_badge(regime)}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="card">
                <div class="stat-label">Last Scan</div>
                <div class="stat-value-sm">{scan_date}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="card">
                <div class="stat-label">Stocks Scanned</div>
                <div class="stat-value">{stocks_scanned:,}</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="card">
                <div class="stat-label">Top Picks</div>
                <div class="stat-value">{len(picks)}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Top 3 picks preview
        if picks:
            st.markdown('<div class="section-title">Top Recommendations</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">AI-selected from 1,003 stocks. Updated every 2 weeks.</div>', unsafe_allow_html=True)

            cols = st.columns(min(len(picks), 3))
            for i, pick in enumerate(picks[:3]):
                with cols[i]:
                    ticker = pick.get("ticker", "")
                    name = pick.get("name", ticker)
                    price = pick.get("price", 0)
                    confidence = pick.get("confidence", 0)
                    score = pick.get("score", 0)
                    reason = pick.get("reason", "Strong fundamentals and growth potential.")

                    conf_class = "confidence-high" if confidence >= 75 else "confidence-med" if confidence >= 60 else "confidence-low"

                    st.markdown(f"""<div class="card">
                        <div class="pick-rank">#{i+1} Pick</div>
                        <div class="pick-name">{name}</div>
                        <div class="pick-ticker">{ticker}</div>
                        <div style="margin:16px 0">
                            <div class="pick-price">${price:.2f}</div>
                        </div>
                        <div class="stat-label">Confidence</div>
                        <div class="confidence-bar-bg">
                            <div class="confidence-bar-fill {conf_class}" style="width:{confidence}%"></div>
                        </div>
                        <div style="font-size:13px;color:#86868b;margin-top:4px">{confidence}%</div>
                        <div style="margin-top:12px;font-size:14px;color:#424245;line-height:1.5">{reason[:150]}{'...' if len(reason)>150 else ''}</div>
                    </div>""", unsafe_allow_html=True)

                    # Mini chart
                    try:
                        mini_df = get_stock_data(ticker, period="3mo", interval="1d")
                        if not mini_df.empty:
                            color = "#34c759" if mini_df["Close"].iloc[-1] >= mini_df["Close"].iloc[0] else "#ff3b30"
                            st.plotly_chart(create_sparkline(mini_df, color), use_container_width=True)
                    except Exception:
                        pass

    else:
        # No report yet — welcome screen
        st.markdown("")
        st.markdown("")
        st.markdown("""
        <div style="text-align:center;padding:80px 0">
            <div style="font-size:48px;font-weight:600;color:#1d1d1f;letter-spacing:-1px">
                Welcome to AI Trading Crew
            </div>
            <div style="font-size:18px;color:#86868b;margin-top:12px;max-width:500px;margin-left:auto;margin-right:auto;line-height:1.6">
                50 AI agents scan 1,003 stocks across the London Stock Exchange and US markets
                to find the best long-term investment opportunities for you.
            </div>
            <div style="margin-top:40px;font-size:15px;color:#86868b">
                Go to <b>Run Scan</b> to start your first analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# TAB 2: TOP PICKS
# ═══════════════════════════════════════════════════════════════════════
with tab_picks:
    report = get_latest_report()

    if report and report.get("picks"):
        picks = report["picks"]

        st.markdown('<div class="section-title">All Recommendations</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-subtitle">{len(picks)} stocks selected from {report.get("stocks_scanned", 1003):,} scanned on {report.get("scan_date", "N/A")}</div>', unsafe_allow_html=True)

        for i, pick in enumerate(picks):
            ticker = pick.get("ticker", "")
            name = pick.get("name", ticker)
            price = pick.get("price", 0)
            confidence = pick.get("confidence", 0)
            entry_low = pick.get("entry_low", price * 0.95)
            entry_high = pick.get("entry_high", price * 1.02)
            stop_loss = pick.get("stop_loss", price * 0.85)
            target = pick.get("target", price * 1.40)
            reason = pick.get("reason", "")
            agents = pick.get("agents_agreed", [])
            hold_period = pick.get("hold_period", "3-6 months")
            sector = pick.get("sector", "")
            market = pick.get("market", "US")

            upside = ((target - price) / price * 100) if price > 0 else 0
            risk = ((price - stop_loss) / price * 100) if price > 0 else 0

            with st.expander(f"**#{i+1}  {name}** ({ticker})  —  ${price:.2f}  —  Confidence: {confidence}%", expanded=(i < 3)):
                p1, p2 = st.columns([2, 1])

                with p1:
                    # Chart
                    try:
                        chart_df = get_stock_data(ticker, period="1y", interval="1d")
                        if not chart_df.empty:
                            chart_df = calculate_indicators(chart_df)
                            fig = create_chart(chart_df, ticker)
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        st.info(f"Chart unavailable for {ticker}")

                with p2:
                    st.markdown(f"**Sector:** {sector}")
                    st.markdown(f"**Market:** {market}")
                    st.markdown(f"**Hold Period:** {hold_period}")
                    st.markdown("---")

                    st.metric("Entry Range", f"${entry_low:.2f} — ${entry_high:.2f}")
                    st.metric("Target Price", f"${target:.2f}", f"+{upside:.1f}%")
                    st.metric("Stop Loss", f"${stop_loss:.2f}", f"-{risk:.1f}%")

                    st.markdown("---")

                    # Agent verdicts
                    if agents:
                        st.markdown("**Agent Verdicts**")
                        for agent in agents:
                            a_name = agent.get("name", "Agent")
                            a_verdict = agent.get("verdict", "WATCH")
                            v_class = "verdict-buy" if a_verdict == "BUY" else "verdict-pass" if a_verdict == "PASS" else "verdict-watch"
                            st.markdown(f'{a_name} <span class="{v_class}">{a_verdict}</span>', unsafe_allow_html=True)

                if reason:
                    st.markdown(f"**Why:** {reason}")

    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 0">
            <div style="font-size:24px;font-weight:600;color:#1d1d1f">No picks yet</div>
            <div style="font-size:15px;color:#86868b;margin-top:8px">Run a scan to get your first recommendations.</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# TAB 3: STOCK DETAIL
# ═══════════════════════════════════════════════════════════════════════
with tab_stock:
    st.markdown('<div class="section-title">Stock Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Look up any stock for detailed analysis.</div>', unsafe_allow_html=True)

    symbol = st.text_input("Enter symbol", value="AAPL", max_chars=10,
                           label_visibility="collapsed",
                           placeholder="Enter stock symbol (e.g. AAPL, BP.L, NVDA)").upper().strip()

    if symbol:
        try:
            df = get_stock_data(symbol, "1y", "1d")
            info = get_stock_info(symbol)

            if not df.empty:
                df = calculate_indicators(df)
                price = df["Close"].iloc[-1]
                prev = df["Close"].iloc[-2] if len(df) > 1 else price
                change = price - prev
                change_pct = (change / prev) * 100

                # Header
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                with c1:
                    st.markdown(f"### {info.get('shortName', symbol)}")
                    change_class = "stat-change-up" if change >= 0 else "stat-change-down"
                    arrow = "+" if change >= 0 else ""
                    st.markdown(f"""
                        <span class="stat-value">${price:.2f}</span>
                        <span class="{change_class}">&nbsp; {arrow}{change:.2f} ({arrow}{change_pct:.2f}%)</span>
                    """, unsafe_allow_html=True)
                with c2:
                    st.metric("Market Cap", fmt(info.get("marketCap")))
                with c3:
                    pe = info.get("trailingPE")
                    st.metric("P/E", f"{pe:.1f}" if pe else "N/A")
                with c4:
                    dy = info.get("dividendYield")
                    st.metric("Div Yield", f"{dy*100:.2f}%" if dy else "N/A")
                with c5:
                    rsi = df["RSI"].iloc[-1]
                    st.metric("RSI", f"{rsi:.0f}")

                # Chart
                fig = create_chart(df, symbol)
                st.plotly_chart(fig, use_container_width=True)

                # Fundamentals
                st.markdown("---")
                st.markdown("#### Fundamentals")

                f1, f2, f3, f4 = st.columns(4)
                with f1:
                    st.metric("Forward P/E", f"{info.get('forwardPE', 0):.1f}" if info.get("forwardPE") else "N/A")
                    st.metric("P/B Ratio", f"{info.get('priceToBook', 0):.2f}" if info.get("priceToBook") else "N/A")
                    st.metric("EV/EBITDA", f"{info.get('enterpriseToEbitda', 0):.1f}" if info.get("enterpriseToEbitda") else "N/A")
                with f2:
                    st.metric("Gross Margin", f"{info.get('grossMargins', 0)*100:.1f}%" if info.get("grossMargins") else "N/A")
                    st.metric("Net Margin", f"{info.get('profitMargins', 0)*100:.1f}%" if info.get("profitMargins") else "N/A")
                    st.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%" if info.get("returnOnEquity") else "N/A")
                with f3:
                    st.metric("Revenue Growth", f"{info.get('revenueGrowth', 0)*100:.1f}%" if info.get("revenueGrowth") else "N/A")
                    st.metric("EPS (TTM)", f"${info.get('trailingEps', 0):.2f}" if info.get("trailingEps") else "N/A")
                    st.metric("Free Cash Flow", fmt(info.get("freeCashflow")))
                with f4:
                    st.metric("Total Cash", fmt(info.get("totalCash")))
                    st.metric("Total Debt", fmt(info.get("totalDebt")))
                    st.metric("Debt/Equity", f"{info.get('debtToEquity', 0):.0f}" if info.get("debtToEquity") else "N/A")

                # Revenue chart
                financials = get_financials(symbol)
                if not financials["income"].empty:
                    income = financials["income"]
                    rev_row = next((idx for idx in income.index if "revenue" in str(idx).lower() and "total" in str(idx).lower()), None)
                    ni_row = next((idx for idx in income.index if "net income" in str(idx).lower()), None)

                    if rev_row:
                        st.markdown("#### Revenue & Earnings")
                        rev_data = income.loc[rev_row].dropna().sort_index()
                        fig_rev = go.Figure()
                        fig_rev.add_trace(go.Bar(
                            x=[d.strftime("%b %Y") if hasattr(d, "strftime") else str(d) for d in rev_data.index],
                            y=rev_data.values, name="Revenue", marker_color="#007aff",
                        ))
                        if ni_row:
                            ni_data = income.loc[ni_row].dropna().sort_index()
                            fig_rev.add_trace(go.Bar(
                                x=[d.strftime("%b %Y") if hasattr(d, "strftime") else str(d) for d in ni_data.index],
                                y=ni_data.values, name="Net Income", marker_color="#34c759",
                            ))
                        fig_rev.update_layout(
                            template="plotly_white", paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)", height=300,
                            barmode="group", legend=dict(orientation="h"),
                            margin=dict(l=50, r=20, t=10, b=40),
                            font=dict(family="Inter", color="#1d1d1f"),
                        )
                        fig_rev.update_xaxes(gridcolor="#f0f0f5")
                        fig_rev.update_yaxes(gridcolor="#f0f0f5")
                        st.plotly_chart(fig_rev, use_container_width=True)

                # Company description
                desc = info.get("longBusinessSummary", "")
                if desc:
                    with st.expander("About"):
                        st.write(desc)

        except Exception as e:
            st.error(f"Could not load data for {symbol}.")


# ═══════════════════════════════════════════════════════════════════════
# TAB 4: RUN SCAN
# ═══════════════════════════════════════════════════════════════════════
with tab_scan:
    st.markdown('<div class="section-title">Run Scan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Scan 1,003 stocks and let 50 AI agents find the best investments.</div>', unsafe_allow_html=True)

    sc1, sc2 = st.columns(2)
    with sc1:
        scan_market = st.selectbox("Market", ["All (LSE + US)", "London Stock Exchange", "US Stocks"], index=0)
    with sc2:
        scan_top = st.selectbox("Show top N picks", [5, 10, 15, 20], index=1)

    skip_ai = st.checkbox("Quick scan (skip AI analysis — faster but less accurate)", value=False)

    st.markdown("")

    if st.button("Start Scan", use_container_width=True):
        market_map = {"All (LSE + US)": "all", "London Stock Exchange": "lse", "US Stocks": "us"}
        market_arg = market_map[scan_market]

        with st.status("Scanning...", expanded=True) as status:
            st.write("Stage 1: Checking market regime...")

            try:
                import subprocess
                cmd = ["python3", "pipeline.py", "--market", market_arg, "--top", str(scan_top)]
                if skip_ai:
                    cmd.append("--skip-ai")

                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1, cwd=os.path.dirname(__file__) or ".",
                )

                output_area = st.empty()
                full_output = []

                for line in iter(process.stdout.readline, ""):
                    full_output.append(line.rstrip())
                    # Show last 20 lines
                    display = "\n".join(full_output[-20:])
                    output_area.code(display, language=None)

                    # Update status message based on output
                    ll = line.lower()
                    if "stage 2" in ll or "scanning" in ll:
                        st.write("Stage 2: Scanning stocks...")
                    elif "stage 3" in ll or "ai analysis" in ll:
                        st.write("Stage 3: AI agents analyzing top candidates...")
                    elif "stage 4" in ll or "ranking" in ll:
                        st.write("Stage 4: Ranking final picks...")
                    elif "stage 5" in ll or "report" in ll:
                        st.write("Stage 5: Generating report...")

                process.wait()

                if process.returncode == 0:
                    status.update(label="Scan complete!", state="complete")
                    st.success("Done! Switch to the **Overview** or **Top Picks** tab to see results.")
                    st.cache_data.clear()
                else:
                    status.update(label="Scan failed", state="error")
                    st.error("Scan encountered an error. Check the output above.")

            except Exception as e:
                status.update(label="Error", state="error")
                st.error(f"Failed to start scan: {e}")

    # Show past reports
    report_dir = os.path.join(os.path.dirname(__file__) or ".", "reports")
    if os.path.exists(report_dir):
        json_files = sorted(glob.glob(os.path.join(report_dir, "*_scan.json")), reverse=True)
        if json_files:
            st.markdown("---")
            st.markdown("#### Past Scans")
            for jf in json_files[:10]:
                fname = os.path.basename(jf)
                date = fname.replace("_scan.json", "")
                html_file = jf.replace(".json", ".html")
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{date}**")
                with col_b:
                    if os.path.exists(html_file):
                        st.markdown(f"[Open Report]({html_file})")
