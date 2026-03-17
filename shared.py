"""
AI Trading Crew — Shared Module
Apple-inspired design system, helper functions, data fetchers.
Imported by all pages.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yfinance as yf
import json, os, glob


# ─── Apple Design System CSS ────────────────────────────────────────

APPLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #fbfbfd;
    --card: #ffffff;
    --text: #1d1d1f;
    --text-secondary: #86868b;
    --text-tertiary: #aeaeb2;
    --border: #f0f0f5;
    --border-hover: #e8e8ed;
    --green: #34c759;
    --green-bg: #eafaf0;
    --red: #ff3b30;
    --red-bg: #fef0ef;
    --blue: #007aff;
    --blue-bg: #eef4ff;
    --orange: #ff9500;
    --orange-bg: #fff6e8;
    --purple: #af52de;
    --purple-bg: #f5eefa;
    --radius: 16px;
    --radius-sm: 10px;
    --shadow: 0 1px 3px rgba(0,0,0,0.04);
    --shadow-hover: 0 8px 24px rgba(0,0,0,0.06);
}

.stApp { background: var(--bg); font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
#MainMenu, footer { visibility: hidden; }
/* Keep the header visible so sidebar toggle arrow works */
header[data-testid="stHeader"] { background: transparent; }

/* ── Typography ── */
.hero-title { font-size: 44px; font-weight: 700; color: var(--text); letter-spacing: -1.5px; line-height: 1.1; }
.hero-sub { font-size: 18px; color: var(--text-secondary); font-weight: 400; margin-top: 8px; line-height: 1.5; }
.section-title { font-size: 26px; font-weight: 600; color: var(--text); letter-spacing: -0.5px; margin: 48px 0 6px; }
.section-sub { font-size: 14px; color: var(--text-secondary); margin-bottom: 20px; }
.label { font-size: 11px; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }
.value-xl { font-size: 32px; font-weight: 700; color: var(--text); letter-spacing: -1px; }
.value-lg { font-size: 22px; font-weight: 600; color: var(--text); letter-spacing: -0.5px; }
.value-md { font-size: 16px; font-weight: 600; color: var(--text); }
.value-sm { font-size: 14px; font-weight: 500; color: var(--text); }
.caption { font-size: 12px; color: var(--text-secondary); }

/* ── Cards ── */
.card {
    background: var(--card); border-radius: var(--radius); padding: 24px;
    border: 1px solid var(--border); box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}
.card:hover { box-shadow: var(--shadow-hover); border-color: var(--border-hover); }
.card-sm { background: var(--card); border-radius: var(--radius-sm); padding: 16px 18px; border: 1px solid var(--border); }

/* ── Accent Cards ── */
.card-green { background: var(--green-bg); border-color: transparent; }
.card-green .label { color: #2e7d32; }
.card-green .value-lg, .card-green .value-md { color: #1b5e20; }
.card-red { background: var(--red-bg); border-color: transparent; }
.card-red .label { color: #c62828; }
.card-red .value-lg, .card-red .value-md { color: #b71c1c; }
.card-blue { background: var(--blue-bg); border-color: transparent; }
.card-blue .label { color: #1565c0; }
.card-blue .value-lg, .card-blue .value-md { color: #0d47a1; }
.card-orange { background: var(--orange-bg); border-color: transparent; }
.card-orange .label { color: #e65100; }
.card-orange .value-lg, .card-orange .value-md { color: #bf360c; }
.card-purple { background: var(--purple-bg); border-color: transparent; }
.card-purple .label { color: #7b1fa2; }

/* ── Pick Header ── */
.pick-header {
    background: linear-gradient(135deg, #1d1d1f 0%, #3a3a3c 100%);
    border-radius: var(--radius); padding: 32px; color: white; margin-bottom: 24px;
}
.pick-header .label { color: rgba(255,255,255,0.5); }
.pick-header .value-xl { color: white; }
.pick-header .value-lg { color: white; }

/* ── Badges ── */
.badge { display: inline-block; padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: 0.3px; }
.badge-green { background: var(--green-bg); color: #2e7d32; }
.badge-red { background: var(--red-bg); color: #c62828; }
.badge-orange { background: var(--orange-bg); color: #e65100; }
.badge-blue { background: var(--blue-bg); color: #1565c0; }
.badge-purple { background: var(--purple-bg); color: #7b1fa2; }
.badge-gray { background: #f3f3f8; color: #6e6e73; }

/* ── Health Dot ── */
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }
.dot-green { background: var(--green); }
.dot-red { background: var(--red); }
.dot-orange { background: var(--orange); }

/* ── Metric Grid ── */
.metric-grid { display: grid; gap: 12px; }
.metric-grid-2 { grid-template-columns: 1fr 1fr; }
.metric-grid-3 { grid-template-columns: 1fr 1fr 1fr; }
.metric-grid-4 { grid-template-columns: 1fr 1fr 1fr 1fr; }

/* ── Progress Bar ── */
.progress-bg { background: #f0f0f5; border-radius: 6px; height: 6px; overflow: hidden; }
.progress-fill { height: 6px; border-radius: 6px; transition: width 0.5s ease; }
.progress-green { background: linear-gradient(90deg, #34c759, #30d158); }
.progress-orange { background: linear-gradient(90deg, #ff9500, #ffb340); }
.progress-red { background: linear-gradient(90deg, #ff3b30, #ff6961); }
.progress-blue { background: linear-gradient(90deg, #007aff, #5ac8fa); }

/* ── Reasoning Box ── */
.reasoning-box {
    background: linear-gradient(135deg, var(--blue-bg) 0%, #f0f0ff 100%);
    border-radius: var(--radius); padding: 24px; border-left: 4px solid var(--blue);
    margin: 16px 0 24px;
}
.reasoning-box p { font-size: 15px; color: #2c3e50; line-height: 1.7; margin: 0; }

/* ── Data Table ── */
.clean-table { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: var(--radius-sm); overflow: hidden; border: 1px solid var(--border); }
.clean-table th { background: #fafafa; padding: 10px 16px; font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; text-align: left; border-bottom: 1px solid var(--border); }
.clean-table td { padding: 10px 16px; font-size: 14px; color: var(--text); border-bottom: 1px solid var(--border); }
.clean-table tr:last-child td { border-bottom: none; }
.clean-table tr:hover td { background: #fafbfd; }

/* ── Streamlit Overrides ── */
.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid var(--border); background: transparent; }
.stTabs [data-baseweb="tab"] { background: transparent; border-radius: 0; border-bottom: 2px solid transparent; padding: 14px 24px; font-weight: 500; color: var(--text-secondary); font-size: 15px; }
.stTabs [aria-selected="true"] { border-bottom-color: var(--text) !important; color: var(--text) !important; font-weight: 600; }
[data-testid="stMetricValue"] { font-family: 'Inter'; font-weight: 600; }
[data-testid="stMetricLabel"] { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); }
.stButton > button { background: var(--text); color: white; border: none; border-radius: 12px; padding: 14px 32px; font-weight: 600; font-size: 16px; letter-spacing: -0.2px; transition: all 0.2s; }
.stButton > button:hover { background: #424245; transform: translateY(-1px); }
hr { border-color: var(--border); }
.stDataFrame { border-radius: var(--radius-sm); overflow: hidden; }

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown { font-family: 'Inter', -apple-system, sans-serif; }
</style>
"""


def inject_css():
    """Inject the Apple design system CSS into the page."""
    st.markdown(APPLE_CSS, unsafe_allow_html=True)


def _get_scan_status():
    """Read the background scan status file."""
    status_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", ".scan_status.json")
    if not os.path.exists(status_file):
        return None
    try:
        with open(status_file) as f:
            return json.load(f)
    except:
        return None


def page_header():
    """Render the shared navigation header bar + scan status indicator."""
    # Check if a scan is running
    scan = _get_scan_status()
    scan_bar = ""

    if scan and scan.get("status") == "running":
        pct = scan.get("progress", 0)
        msg = scan.get("message", "Scanning...")
        stage = scan.get("stage", "")
        scan_bar = f"""<div style="background:#1d1d1f;color:white;border-radius:10px;padding:10px 16px;margin-bottom:12px;
            display:flex;align-items:center;justify-content:space-between;gap:12px">
            <div style="display:flex;align-items:center;gap:10px">
                <div style="width:8px;height:8px;border-radius:50%;background:#34c759;animation:pulse 1.5s infinite"></div>
                <span style="font-size:13px;font-weight:600">System Running</span>
                <span style="font-size:12px;color:rgba(255,255,255,0.6)">{stage}</span>
            </div>
            <div style="display:flex;align-items:center;gap:12px;flex:1;max-width:400px">
                <div style="flex:1;background:rgba(255,255,255,0.15);border-radius:4px;height:4px;overflow:hidden">
                    <div style="width:{pct}%;height:4px;background:#34c759;border-radius:4px;transition:width 0.5s"></div>
                </div>
                <span style="font-size:12px;color:rgba(255,255,255,0.6);min-width:35px">{pct}%</span>
            </div>
        </div>
        <style>@keyframes pulse {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:0.3 }} }}</style>"""
    elif scan and scan.get("status") == "complete":
        scan_bar = f"""<div style="background:#eafaf0;border:1px solid #c8e6c9;border-radius:10px;padding:10px 16px;margin-bottom:12px;
            display:flex;align-items:center;gap:10px">
            <span style="font-size:13px;font-weight:600;color:#2e7d32">Scan Complete</span>
            <span style="font-size:12px;color:#4caf50">{scan.get("message","")}</span>
        </div>"""
    elif scan and scan.get("status") == "failed":
        scan_bar = f"""<div style="background:#fef0ef;border:1px solid #ffcdd2;border-radius:10px;padding:10px 16px;margin-bottom:12px;
            display:flex;align-items:center;gap:10px">
            <span style="font-size:13px;font-weight:600;color:#c62828">Scan Failed</span>
            <span style="font-size:12px;color:#e57373">{scan.get("error","")[:100]}</span>
        </div>"""

    st.markdown(f"""{scan_bar}<div style="display:flex;align-items:center;justify-content:space-between;padding:20px 0;border-bottom:1px solid #e8e8ed;margin-bottom:32px">
        <div><div style="font-size:20px;font-weight:700;color:#1d1d1f;letter-spacing:-0.5px">AI Trading Crew</div>
        <div style="font-size:12px;color:#86868b">1,003 stocks &middot; LSE + US &middot; Long-term</div></div>
    </div>""", unsafe_allow_html=True)


# ─── Data Fetchers ───────────────────────────────────────────────────

@st.cache_data(ttl=120)
def get_stock_data(sym, period="1y", interval="1d"):
    return yf.Ticker(sym).history(period=period, interval=interval)

@st.cache_data(ttl=300)
def get_stock_info(sym):
    return yf.Ticker(sym).info

@st.cache_data(ttl=300)
def get_financials(sym):
    t = yf.Ticker(sym)
    try:
        return {
            "income": t.quarterly_income_stmt,
            "balance": t.quarterly_balance_sheet,
            "cashflow": t.quarterly_cashflow,
        }
    except Exception:
        return {
            "income": pd.DataFrame(),
            "balance": pd.DataFrame(),
            "cashflow": pd.DataFrame(),
        }

def get_latest_report():
    """Load the most recent scan report JSON."""
    rd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    if not os.path.exists(rd):
        return None
    jf = sorted(glob.glob(os.path.join(rd, "*_scan.json")), reverse=True)
    if not jf:
        return None
    with open(jf[0]) as f:
        return json.load(f)


# ─── Calculation Helpers ─────────────────────────────────────────────

def calc_indicators(df):
    """Calculate SMA, EMA, MACD, RSI on a DataFrame."""
    c = df["Close"]
    df["SMA_50"] = c.rolling(50).mean()
    df["SMA_200"] = c.rolling(200).mean()
    df["EMA_12"] = c.ewm(span=12).mean()
    df["EMA_26"] = c.ewm(span=26).mean()
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
    delta = c.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss))
    return df


# ─── Formatting Helpers ─────────────────────────────────────────────

def fmt(n):
    """Format a number as a currency string with magnitude suffix."""
    if n is None:
        return "\u2014"
    a = abs(n)
    if a >= 1e12:
        return f"${n/1e12:.1f}T"
    if a >= 1e9:
        return f"${n/1e9:.1f}B"
    if a >= 1e6:
        return f"${n/1e6:.1f}M"
    return f"${n:,.0f}"


def pct(n):
    """Format a decimal as a percentage string."""
    if n is None:
        return "\u2014"
    return f"{n*100:.1f}%"


def metric_card(label, value, accent=None, subtitle=None):
    """Generate HTML for a small metric card."""
    cls = f"card-sm card-{accent}" if accent else "card-sm"
    sub = f'<div class="caption" style="margin-top:4px">{subtitle}</div>' if subtitle else ""
    return f'<div class="{cls}"><div class="label">{label}</div><div class="value-lg">{value}</div>{sub}</div>'


def health_dot(value, good_threshold, bad_threshold, higher_is_better=True):
    """Return an HTML span with a green/orange/red dot based on thresholds."""
    if value is None:
        return '<span class="dot dot-orange"></span>'
    if higher_is_better:
        if value >= good_threshold:
            return '<span class="dot dot-green"></span>'
        elif value >= bad_threshold:
            return '<span class="dot dot-orange"></span>'
        else:
            return '<span class="dot dot-red"></span>'
    else:
        if value <= good_threshold:
            return '<span class="dot dot-green"></span>'
        elif value <= bad_threshold:
            return '<span class="dot dot-orange"></span>'
        else:
            return '<span class="dot dot-red"></span>'


def progress_bar(value, max_val=100, color="blue"):
    """Generate HTML for a slim progress bar."""
    pct_w = min(max(value / max_val * 100, 0), 100) if max_val > 0 else 0
    return f'<div class="progress-bg"><div class="progress-fill progress-{color}" style="width:{pct_w}%"></div></div>'


def create_chart(df, sym, height=480):
    """Create a candlestick + volume + RSI chart with Plotly."""
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2],
    )
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name=sym,
        increasing_line_color="#34c759", decreasing_line_color="#ff3b30",
        increasing_fillcolor="#34c759", decreasing_fillcolor="#ff3b30",
    ), row=1, col=1)

    if "SMA_50" in df:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA_50"], name="50 SMA",
            line=dict(color="#007aff", width=1.5),
        ), row=1, col=1)
    if "SMA_200" in df:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA_200"], name="200 SMA",
            line=dict(color="#af52de", width=1.5),
        ), row=1, col=1)

    vc = [
        "rgba(52,199,89,0.4)" if c >= o else "rgba(255,59,48,0.4)"
        for c, o in zip(df["Close"], df["Open"])
    ]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker=dict(color=vc)), row=2, col=1)

    if "RSI" in df:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["RSI"], name="RSI",
            line=dict(color="#ff9500", width=1.5),
        ), row=3, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="rgba(255,59,48,0.3)", row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="rgba(52,199,89,0.3)", row=3, col=1)
        fig.update_yaxes(range=[0, 100], row=3, col=1)

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=50, r=20, t=10, b=20),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, font=dict(size=11, color="#86868b")),
        font=dict(family="Inter", color="#1d1d1f"),
    )
    fig.update_xaxes(gridcolor="#f5f5f7", showgrid=True, zeroline=False)
    fig.update_yaxes(gridcolor="#f5f5f7", showgrid=True, zeroline=False)
    return fig


def normalize_pick(pick):
    """Normalize pick field names from pipeline JSON to dashboard expected names."""
    return {
        "ticker": pick.get("symbol") or pick.get("ticker", ""),
        "name": pick.get("name", ""),
        "price": pick.get("price", 0),
        "confidence": (pick.get("confidence", 0) * 100) if pick.get("confidence", 0) <= 1 else pick.get("confidence", 0),
        "score": pick.get("combined_score") or pick.get("scanner_score") or pick.get("score", 0),
        "entry_low": pick.get("entry_low", 0),
        "entry_high": pick.get("entry_high", 0),
        "stop_loss": pick.get("stop_loss", 0),
        "target": pick.get("target_price") or pick.get("target", 0),
        "reason": pick.get("buy_reason") or pick.get("reason", ""),
        "agents_agreed": pick.get("agents_agreed", []),
        "agent_verdicts": pick.get("agent_verdicts", []),
        "hold_period": pick.get("holding_period") or pick.get("hold_period", "3-6 months"),
        "sector": pick.get("sector", ""),
        "market": pick.get("market", "US"),
        "verdict": pick.get("verdict", ""),
    }


def regime_badge(r):
    """Return an HTML badge for a market regime value."""
    if not r:
        return '<span class="badge badge-gray">Unknown</span>'
    if isinstance(r, dict):
        r = r.get("regime", "Unknown")
    rl = str(r).lower()
    if "strong" in rl and "bull" in rl:
        return f'<span class="badge badge-green">{r.replace("_"," ").title()}</span>'
    if "bull" in rl:
        return f'<span class="badge badge-green">{r.replace("_"," ").title()}</span>'
    if "strong" in rl and "bear" in rl:
        return f'<span class="badge badge-red">{r.replace("_"," ").title()}</span>'
    if "bear" in rl:
        return f'<span class="badge badge-red">{r.replace("_"," ").title()}</span>'
    if "volatile" in rl:
        return f'<span class="badge badge-orange">{r.replace("_"," ").title()}</span>'
    return f'<span class="badge badge-gray">{r.replace("_"," ").title()}</span>'


# ─── Stock Detail Renderer ──────────────────────────────────────────

def calculate_recommendation(info, df=None):
    """
    Calculate a professional recommendation (Strong Sell → Strong Strong Buy)
    and predicted price targets based on fundamentals + technicals.
    Returns dict with: rating, rating_color, target_low, target_mid, target_high, reasoning
    """
    score = 0  # -10 to +10 scale
    reasons = []

    # Valuation score
    pe = info.get("trailingPE")
    fwd_pe = info.get("forwardPE")
    if pe and fwd_pe and fwd_pe < pe * 0.85:
        score += 2; reasons.append("Earnings acceleration (forward P/E significantly below trailing)")
    if pe and 0 < pe < 12:
        score += 2; reasons.append(f"Deep value at {pe:.0f}x earnings")
    elif pe and 0 < pe < 18:
        score += 1; reasons.append(f"Attractive valuation at {pe:.0f}x earnings")
    elif pe and pe > 35:
        score -= 1; reasons.append(f"Expensive at {pe:.0f}x earnings")

    # Profitability
    roe = info.get("returnOnEquity")
    margins = info.get("profitMargins")
    if roe and roe > 0.20:
        score += 1; reasons.append(f"Strong ROE of {roe*100:.0f}%")
    if margins and margins > 0.15:
        score += 1; reasons.append(f"Healthy margins at {margins*100:.0f}%")

    # Growth
    rev_growth = info.get("revenueGrowth")
    earn_growth = info.get("earningsGrowth")
    if rev_growth and rev_growth > 0.15:
        score += 2; reasons.append(f"Strong revenue growth of {rev_growth*100:.0f}%")
    elif rev_growth and rev_growth > 0.05:
        score += 1
    elif rev_growth and rev_growth < -0.05:
        score -= 1; reasons.append("Declining revenue")
    if earn_growth and earn_growth > 0.20:
        score += 1

    # Balance sheet
    de = info.get("debtToEquity")
    if de and de < 30:
        score += 1; reasons.append("Low debt levels")
    elif de and de > 150:
        score -= 1; reasons.append("High debt levels")

    # Dividends
    div_yield = info.get("dividendYield")
    if div_yield and div_yield > 0.03:
        score += 1; reasons.append(f"Attractive {div_yield*100:.1f}% dividend yield")

    # Technical (if df available)
    if df is not None and not df.empty:
        try:
            close = df["Close"].iloc[-1]
            sma50 = df["Close"].rolling(50).mean().iloc[-1]
            sma200 = df["Close"].rolling(200).mean().iloc[-1]
            if close > sma200 and close > sma50:
                score += 1; reasons.append("Uptrend confirmed (above 50 & 200 SMA)")
            elif close < sma200:
                score -= 1; reasons.append("Below 200-day moving average")
            if sma50 > sma200:
                score += 1  # golden cross
        except:
            pass

    # Analyst consensus
    rec = (info.get("recommendationKey") or "").lower()
    if rec in ("strong_buy", "buy"):
        score += 1
    elif rec in ("sell", "strong_sell"):
        score -= 1

    # Map score to rating
    if score >= 7: rating, color = "Strong Strong Buy", "#1b5e20"
    elif score >= 5: rating, color = "Strong Buy", "#2e7d32"
    elif score >= 3: rating, color = "Buy", "#34c759"
    elif score >= 1: rating, color = "Moderate Buy", "#66bb6a"
    elif score >= -1: rating, color = "Hold", "#ff9500"
    elif score >= -3: rating, color = "Moderate Sell", "#ff6b6b"
    elif score >= -5: rating, color = "Sell", "#ff3b30"
    else: rating, color = "Strong Sell", "#b71c1c"

    # Predicted prices
    curr = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    analyst_target = info.get("targetMeanPrice")
    analyst_low = info.get("targetLowPrice")
    analyst_high = info.get("targetHighPrice")

    if analyst_target and curr > 0:
        target_mid = analyst_target
        target_low = analyst_low or curr * 0.85
        target_high = analyst_high or curr * 1.30
    elif curr > 0:
        # Estimate based on score
        multiplier = 1 + (score * 0.03)  # +/-3% per score point
        target_mid = curr * multiplier
        target_low = curr * (multiplier - 0.10)
        target_high = curr * (multiplier + 0.10)
    else:
        target_mid = target_low = target_high = 0

    return {
        "rating": rating,
        "color": color,
        "score": score,
        "target_low": target_low,
        "target_mid": target_mid,
        "target_high": target_high,
        "upside": ((target_mid - curr) / curr * 100) if curr > 0 else 0,
        "reasons": reasons[:5],  # top 5 reasons
    }


@st.cache_data(ttl=600)
def _grade_stock_cached(sym):
    """Fetch info + price data and compute grades (cached)."""
    try:
        info = yf.Ticker(sym).info
        df = yf.Ticker(sym).history(period="1y", interval="1d")
    except Exception:
        info, df = {}, pd.DataFrame()
    return grade_stock(info, df)


def grade_from_scan_signals(signals):
    """
    Calculate a grade from scanner_signals data (already in the JSON report).
    No API calls needed — instant.
    """
    def _clamp(v):
        return max(0, min(100, round(v)))

    pe = signals.get("pe_ratio")
    fwd_pe = signals.get("forward_pe")
    rev_growth = signals.get("revenue_growth")
    margins = signals.get("profit_margins")
    pb = signals.get("price_to_book")
    rsi = signals.get("rsi", 50)
    above_50 = signals.get("above_sma_50", False)
    above_200 = signals.get("above_sma_200", False)
    golden = signals.get("golden_cross", False)
    macd_bull = signals.get("macd_bullish_cross", False)
    score = signals.get("score", 50)

    # Fundamental
    fund = 50
    if pe and pe > 0:
        if pe < 12: fund = 92
        elif pe < 18: fund = 75
        elif pe < 25: fund = 55
        else: fund = 35
    if fwd_pe and pe and fwd_pe < pe: fund += 10
    if pb and 0 < pb < 2: fund += 5
    fund = _clamp(fund)

    # Financial health (from margins as proxy)
    fh = 50
    if margins and margins > 0.20: fh = 85
    elif margins and margins > 0.10: fh = 65
    elif margins and margins > 0: fh = 50
    fh = _clamp(fh)

    # Growth
    gro = 50
    if rev_growth:
        if rev_growth > 0.20: gro = 92
        elif rev_growth > 0.10: gro = 70
        elif rev_growth > 0.05: gro = 55
        elif rev_growth > 0: gro = 40
        else: gro = 20
    gro = _clamp(gro)

    # Technical
    tech = 50
    if above_200: tech += 25
    if above_50: tech += 15
    if golden: tech += 15
    if rsi < 30: tech += 15
    elif 30 <= rsi <= 70: tech += 10
    else: tech -= 5
    if macd_bull: tech += 10
    tech = _clamp(tech)

    # Use scanner score as the anchor — this is what the pipeline ranked by
    quant = _clamp(min(score, 100))

    # Final grade = scanner score (this is what the pipeline ranked by)
    # Category grades provide breakdown detail, but final must match pipeline order
    final = _clamp(round(score))

    if final >= 85: rating, color = "Strong Strong Buy", "#1b5e20"
    elif final >= 75: rating, color = "Strong Buy", "#2e7d32"
    elif final >= 65: rating, color = "Buy", "#34c759"
    elif final >= 55: rating, color = "Moderate Buy", "#66bb6a"
    elif final >= 45: rating, color = "Hold", "#ff9500"
    elif final >= 35: rating, color = "Moderate Sell", "#ff6b6b"
    elif final >= 25: rating, color = "Sell", "#ff3b30"
    else: rating, color = "Strong Sell", "#b71c1c"

    return {
        "fundamental": fund, "financial_health": fh, "growth": gro,
        "technical": tech, "quantitative": quant, "dividend": 50, "sentiment": 50,
        "final": final, "rating": rating, "rating_color": color,
    }


def grade_stock(info, df=None):
    """
    Grade a stock 0-100 across multiple categories.
    Returns dict with per-category grades, a weighted final grade,
    a text rating, and a rating colour.
    """
    def _clamp(v):
        return max(0, min(100, v))

    # ── FUNDAMENTAL (weight 25%) ──
    fund = 50  # default
    pe = info.get("trailingPE")
    if pe is not None and pe > 0:
        if pe < 12:
            fund = 92
        elif pe < 18:
            fund = 70 + (18 - pe) / 6 * 20  # 70-90
        elif pe < 25:
            fund = 50 + (25 - pe) / 7 * 20  # 50-70
        elif pe <= 40:
            fund = 30 + (40 - pe) / 15 * 20  # 30-50
        else:
            fund = 10 + max(0, (60 - pe)) / 20 * 20  # 10-30
    fwd_pe = info.get("forwardPE")
    if pe and fwd_pe and pe > 0 and fwd_pe > 0 and fwd_pe < pe:
        fund += 10
    peg = info.get("pegRatio")
    if peg is not None:
        if 0 < peg < 1:
            fund += 15
        elif 1 <= peg <= 2:
            fund += 5
    ev_ebitda = info.get("enterpriseToEbitda")
    if ev_ebitda is not None and 0 < ev_ebitda < 10:
        fund += 10
    pb = info.get("priceToBook")
    if pb is not None and 0 < pb < 2:
        fund += 5
    fund = _clamp(fund)

    # ── FINANCIAL HEALTH (weight 20%) ──
    fh = 50
    cr = info.get("currentRatio")
    if cr is not None:
        if cr > 2:
            fh = 92
        elif cr > 1.5:
            fh = 70
        elif cr > 1:
            fh = 50
        else:
            fh = 30
    de = info.get("debtToEquity")
    if de is not None:
        if de < 30:
            fh = max(fh, 90)
        elif de < 50:
            fh = max(fh, 70)
        elif de < 100:
            fh = max(fh, 50)
        else:
            fh = min(fh, 40)
    fcf_v = info.get("freeCashflow")
    rev = info.get("totalRevenue")
    if fcf_v is not None and fcf_v > 0:
        fh += 15
        if rev and rev > 0:
            fcf_margin = fcf_v / rev * 100
            if fcf_margin > 15:
                fh += 10
    roe = info.get("returnOnEquity")
    if roe is not None:
        if roe > 0.20:
            fh += 15
        elif roe > 0.15:
            fh += 10
    roa = info.get("returnOnAssets")
    if roa is not None and roa > 0.10:
        fh += 10
    fh = _clamp(fh)

    # ── GROWTH (weight 20%) ──
    gro = 50
    rev_growth = info.get("revenueGrowth")
    if rev_growth is not None:
        if rev_growth > 0.20:
            gro = 92
        elif rev_growth > 0.10:
            gro = 70
        elif rev_growth > 0.05:
            gro = 55
        elif rev_growth >= 0:
            gro = 40
        else:
            gro = 20
    earn_growth = info.get("earningsGrowth")
    if earn_growth is not None:
        if earn_growth > 0.25:
            gro += 20
        elif earn_growth > 0.10:
            gro += 10
    if rev_growth is not None and earn_growth is not None:
        if rev_growth > 0 and earn_growth > 0:
            gro += 10
    gro = _clamp(gro)

    # ── TECHNICAL (weight 15%) ──
    tech = 50
    if df is not None and not df.empty and len(df) > 10:
        try:
            close = df["Close"].iloc[-1]
            sma50 = df["Close"].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
            sma200 = df["Close"].rolling(200).mean().iloc[-1] if len(df) >= 200 else None
            if sma200 is not None and not np.isnan(sma200) and close > sma200:
                tech += 25
            if sma50 is not None and not np.isnan(sma50) and close > sma50:
                tech += 15
            if (sma50 is not None and sma200 is not None
                    and not np.isnan(sma50) and not np.isnan(sma200)
                    and sma50 > sma200):
                tech += 15  # golden cross
            # RSI
            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            if not np.isnan(rsi):
                if rsi < 30:
                    tech += 15  # oversold opportunity
                elif rsi <= 70:
                    tech += 10  # neutral
                else:
                    tech -= 5   # overbought
            # MACD
            ema12 = df["Close"].ewm(span=12).mean()
            ema26 = df["Close"].ewm(span=26).mean()
            macd = ema12 - ema26
            macd_sig = macd.ewm(span=9).mean()
            if macd.iloc[-1] > macd_sig.iloc[-1]:
                tech += 10
        except Exception:
            pass
    tech = _clamp(tech)

    # ── QUANTITATIVE (weight 10%) ──
    quant = 50
    if df is not None and not df.empty and len(df) > 20:
        try:
            rets = df["Close"].pct_change().dropna()
            ann_vol = rets.std() * np.sqrt(252) * 100
            if ann_vol < 25:
                quant += 20
            elif ann_vol > 50:
                quant -= 10
        except Exception:
            pass
    beta = info.get("beta")
    if beta is not None:
        if 0.8 <= beta <= 1.2:
            quant += 10
        elif beta > 2.0:
            quant -= 10
    quant = _clamp(quant)

    # ── DIVIDEND (weight 5%) ──
    div_grade = 50
    div_yield = info.get("dividendYield")
    if div_yield is not None:
        if div_yield > 0.04:
            div_grade = 90
        elif div_yield > 0.02:
            div_grade = 70
        elif div_yield > 0.01:
            div_grade = 50
        elif div_yield == 0 or div_yield < 0.001:
            div_grade = 30
    payout = info.get("payoutRatio")
    if payout is not None and 0 < payout < 0.60:
        div_grade += 10
    div_grade = _clamp(div_grade)

    # ── SENTIMENT (weight 5%) ──
    sent = 50
    rec_key = (info.get("recommendationKey") or "").lower()
    if rec_key == "strong_buy":
        sent = 90
    elif rec_key == "buy":
        sent = 75
    elif rec_key == "hold":
        sent = 50
    elif rec_key in ("sell", "underperform"):
        sent = 25
    elif rec_key == "strong_sell":
        sent = 10
    if info.get("targetMeanPrice"):
        sent += 5
    sent = _clamp(sent)

    # ── FINAL GRADE (weighted average) ──
    final = (
        fund * 0.25
        + fh * 0.20
        + gro * 0.20
        + tech * 0.15
        + quant * 0.10
        + div_grade * 0.05
        + sent * 0.05
    )
    final = _clamp(round(final))

    # ── Rating based on final grade ──
    if final >= 85:
        rating, rating_color = "Strong Strong Buy", "#1b5e20"
    elif final >= 75:
        rating, rating_color = "Strong Buy", "#2e7d32"
    elif final >= 65:
        rating, rating_color = "Buy", "#34c759"
    elif final >= 55:
        rating, rating_color = "Moderate Buy", "#66bb6a"
    elif final >= 45:
        rating, rating_color = "Hold", "#ff9500"
    elif final >= 35:
        rating, rating_color = "Moderate Sell", "#ff6b6b"
    elif final >= 25:
        rating, rating_color = "Sell", "#ff3b30"
    else:
        rating, rating_color = "Strong Sell", "#b71c1c"

    return {
        "fundamental": _clamp(round(fund)),
        "financial_health": _clamp(round(fh)),
        "growth": _clamp(round(gro)),
        "technical": _clamp(round(tech)),
        "quantitative": _clamp(round(quant)),
        "dividend": _clamp(round(div_grade)),
        "sentiment": _clamp(round(sent)),
        "final": final,
        "rating": rating,
        "rating_color": rating_color,
    }


def render_recommendation_badge(rec):
    """Render a prominent recommendation badge."""
    bg_map = {
        "Strong Strong Buy": ("linear-gradient(135deg, #1b5e20, #2e7d32)", "white"),
        "Strong Buy": ("linear-gradient(135deg, #2e7d32, #43a047)", "white"),
        "Buy": ("#eafaf0", "#2e7d32"),
        "Moderate Buy": ("#eafaf0", "#388e3c"),
        "Hold": ("#fff8e1", "#f57f17"),
        "Moderate Sell": ("#fef0ef", "#c62828"),
        "Sell": ("#fef0ef", "#b71c1c"),
        "Strong Sell": ("linear-gradient(135deg, #b71c1c, #c62828)", "white"),
    }
    bg, fg = bg_map.get(rec["rating"], ("#f3f3f8", "#1d1d1f"))
    upside_text = f"+{rec['upside']:.1f}%" if rec["upside"] > 0 else f"{rec['upside']:.1f}%"
    upside_color = "#2e7d32" if rec["upside"] > 0 else "#c62828"

    return f"""<div style="background:{bg};color:{fg};border-radius:16px;padding:24px;margin:16px 0">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px">
            <div>
                <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;opacity:0.7">AI Recommendation</div>
                <div style="font-size:28px;font-weight:700;margin-top:4px">{rec['rating']}</div>
            </div>
            <div style="display:flex;gap:24px;flex-wrap:wrap">
                <div style="text-align:center">
                    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;opacity:0.7">Bear Case</div>
                    <div style="font-size:18px;font-weight:600">${rec['target_low']:.2f}</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;opacity:0.7">Target Price</div>
                    <div style="font-size:24px;font-weight:700">${rec['target_mid']:.2f}</div>
                    <div style="font-size:13px;font-weight:600;color:{upside_color}">{upside_text}</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;opacity:0.7">Bull Case</div>
                    <div style="font-size:18px;font-weight:600">${rec['target_high']:.2f}</div>
                </div>
            </div>
        </div>
    </div>"""


def render_grade_card(grades, rec, pick=None):
    """Render a grade card showing final grade + category grades + price targets."""
    final = grades["final"]
    rating = grades["rating"]
    rating_color = grades["rating_color"]

    # Use scan targets when available (consistency with table), fall back to analyst targets
    if pick and pick.get("target") and pick["target"] > 0:
        rec = dict(rec)  # don't mutate original
        rec["target_mid"] = pick["target"]
        rec["target_low"] = pick.get("entry_low") or pick["target"] * 0.93
        rec["target_high"] = pick.get("entry_high") or pick["target"] * 1.07
        curr_price = pick.get("price", 0)
        if curr_price > 0:
            rec["upside"] = (rec["target_mid"] - curr_price) / curr_price * 100

    # Pick ring colour based on grade
    if final >= 75:
        ring_color = "#34c759"
        ring_track = "#eafaf0"
    elif final >= 55:
        ring_color = "#007aff"
        ring_track = "#eef4ff"
    elif final >= 45:
        ring_color = "#ff9500"
        ring_track = "#fff6e8"
    else:
        ring_color = "#ff3b30"
        ring_track = "#fef0ef"

    # Upside from recommendation
    upside_text = f"+{rec['upside']:.1f}%" if rec["upside"] > 0 else f"{rec['upside']:.1f}%"
    upside_color = "#2e7d32" if rec["upside"] > 0 else "#c62828"

    # Category cards
    categories = [
        ("Fundamental", grades["fundamental"], "25%"),
        ("Financial Health", grades["financial_health"], "20%"),
        ("Growth", grades["growth"], "20%"),
        ("Technical", grades["technical"], "15%"),
        ("Quantitative", grades["quantitative"], "10%"),
        ("Dividend", grades["dividend"], "5%"),
        ("Sentiment", grades["sentiment"], "5%"),
    ]

    cat_cards_html = ""
    for cat_name, cat_grade, cat_weight in categories:
        if cat_grade >= 75:
            cg_color = "#34c759"
            cg_bg = "#eafaf0"
        elif cat_grade >= 55:
            cg_color = "#007aff"
            cg_bg = "#eef4ff"
        elif cat_grade >= 45:
            cg_color = "#ff9500"
            cg_bg = "#fff6e8"
        else:
            cg_color = "#ff3b30"
            cg_bg = "#fef0ef"
        cat_cards_html += f"""<div style="flex:1;min-width:100px;background:{cg_bg};border-radius:12px;padding:12px 14px;text-align:center">
            <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#86868b">{cat_name}</div>
            <div style="font-size:24px;font-weight:700;color:{cg_color};margin:4px 0">{cat_grade}</div>
            <div style="font-size:10px;color:#aeaeb2">wt {cat_weight}</div>
        </div>"""

    # SVG circular gauge for final grade
    pct_val = final / 100
    circumference = 2 * 3.14159 * 42
    dash = pct_val * circumference
    gap = circumference - dash

    return f"""<div style="background:white;border:1px solid #f0f0f5;border-radius:16px;padding:24px;margin:16px 0;box-shadow:0 1px 3px rgba(0,0,0,0.04)">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px">
            <div style="display:flex;align-items:center;gap:20px">
                <div style="position:relative;width:100px;height:100px">
                    <svg width="100" height="100" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="42" fill="none" stroke="{ring_track}" stroke-width="6"/>
                        <circle cx="50" cy="50" r="42" fill="none" stroke="{ring_color}" stroke-width="6"
                                stroke-dasharray="{dash:.1f} {gap:.1f}"
                                stroke-linecap="round"
                                transform="rotate(-90 50 50)"/>
                    </svg>
                    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">
                        <div style="font-size:28px;font-weight:700;color:#1d1d1f;line-height:1">{final}</div>
                        <div style="font-size:10px;color:#86868b">/100</div>
                    </div>
                </div>
                <div>
                    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:#86868b">Stock Grade</div>
                    <div style="font-size:24px;font-weight:700;color:{rating_color};margin-top:2px">{rating}</div>
                </div>
            </div>
            <div style="display:flex;gap:24px;flex-wrap:wrap">
                <div style="text-align:center">
                    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#86868b">Bear Case</div>
                    <div style="font-size:18px;font-weight:600;color:#1d1d1f">${rec['target_low']:.2f}</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#86868b">Target Price</div>
                    <div style="font-size:24px;font-weight:700;color:#1d1d1f">${rec['target_mid']:.2f}</div>
                    <div style="font-size:13px;font-weight:600;color:{upside_color}">{upside_text}</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#86868b">Bull Case</div>
                    <div style="font-size:18px;font-weight:600;color:#1d1d1f">${rec['target_high']:.2f}</div>
                </div>
            </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:20px;flex-wrap:wrap">
            {cat_cards_html}
        </div>
    </div>"""


def render_stock_detail(tk, pick=None, raw=None, key_prefix="detail"):
    """Render a full professional stock analysis.

    Parameters
    ----------
    tk : str
        Ticker symbol (e.g. "AAPL", "BP.L").
    pick : dict | None
        Normalized pick dict (from normalize_pick) if this stock was in a scan.
    raw : dict | None
        Raw pick dict from the pipeline JSON (for agent verdicts, scanner signals).
    key_prefix : str
        Unique prefix for Plotly chart keys to avoid duplicate element IDs.
    """
    try:
        sdf = get_stock_data(tk, "2y", "1d")
        info = get_stock_info(tk)
        fin = get_financials(tk)
        if sdf.empty:
            st.warning(f"No data available for {tk}")
            return
    except Exception:
        st.error(f"Could not load data for {tk}")
        return

    sdf = calc_indicators(sdf)
    curr = sdf["Close"].iloc[-1]

    # ── A. Hero Header ──
    prev = sdf["Close"].iloc[-2] if len(sdf) > 1 else curr
    ch = curr - prev
    ch_pct = ch / prev * 100
    arrow = "+" if ch >= 0 else ""

    st.markdown(f"""<div class="pick-header">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
                <div style="font-size:28px;font-weight:700;margin-bottom:4px">{info.get("shortName", tk)}</div>
                <div style="font-size:14px;color:rgba(255,255,255,0.5)">{tk} &middot; {info.get("sector","")} &middot; {info.get("industry","")}</div>
            </div>
            <div style="text-align:right">
                <div class="value-xl">${curr:.2f}</div>
                <div style="font-size:14px;color:{'rgba(52,199,89,0.9)' if ch >= 0 else 'rgba(255,59,48,0.9)'};margin-top:4px">{arrow}{ch:.2f} ({arrow}{ch_pct:.2f}%)</div>
            </div>
        </div>
        <div style="display:flex;gap:32px;margin-top:20px">
            <div><span style="font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.5px">Market Cap</span><br><span style="font-size:16px;font-weight:600;color:white">{fmt(info.get("marketCap"))}</span></div>
            <div><span style="font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.5px">Sector</span><br><span style="font-size:16px;font-weight:600;color:white">{info.get("sector", "\u2014")}</span></div>
            <div><span style="font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.5px">P/E</span><br><span style="font-size:16px;font-weight:600;color:white">{f'{info["trailingPE"]:.1f}' if info.get("trailingPE") is not None else "\u2014"}</span></div>
            <div><span style="font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.5px">Div Yield</span><br><span style="font-size:16px;font-weight:600;color:white">{f'{info["dividendYield"]*100:.2f}%' if info.get("dividendYield") is not None else "\u2014"}</span></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── GRADE CARD (single source of truth for rating) ──
    grades = grade_stock(info, sdf)
    # Use calculate_recommendation only for price targets and reasoning text
    rec = calculate_recommendation(info, sdf)
    st.markdown(render_grade_card(grades, rec, pick=pick), unsafe_allow_html=True)

    # Show reasoning from either scan pick or calculated
    if pick and pick.get("reason"):
        pass  # Will be shown in the Analysis Summary section below
    elif rec["reasons"]:
        reasons_html = " &middot; ".join(rec["reasons"])
        st.markdown(f'<div style="font-size:13px;color:#86868b;margin:-8px 0 16px;line-height:1.6">{reasons_html}</div>', unsafe_allow_html=True)

    # ── B. Analysis Summary (if from scan pick) ──
    if pick and pick.get("reason"):
        st.markdown(f"""<div class="reasoning-box">
            <div class="label" style="color:#1565c0;margin-bottom:10px">WHY THIS STOCK WAS PICKED</div>
            <p>{pick["reason"]}</p>
        </div>""", unsafe_allow_html=True)

    if pick:
        price = pick.get("price", curr)
        entry_lo = pick.get("entry_low") or price * 0.95
        entry_hi = pick.get("entry_high") or price * 1.02
        sl = pick.get("stop_loss") or price * 0.85
        tgt = pick.get("target") or price * 1.40
        upside = ((tgt - price) / price * 100) if price else 0
        downside = ((price - sl) / price * 100) if price else 0
        rr = upside / downside if downside > 0 else 0
        hold = pick.get("hold_period", "4-8 months")
        conf = pick.get("confidence", 0)

        tpc = st.columns(5)
        with tpc[0]:
            st.markdown(metric_card("Entry Range", f"${entry_lo:.2f} \u2013 ${entry_hi:.2f}", "blue"), unsafe_allow_html=True)
        with tpc[1]:
            st.markdown(metric_card("Target", f"${tgt:.2f}", "green", f"+{upside:.1f}%"), unsafe_allow_html=True)
        with tpc[2]:
            st.markdown(metric_card("Stop Loss", f"${sl:.2f}", "red", f"-{downside:.1f}%"), unsafe_allow_html=True)
        with tpc[3]:
            st.markdown(metric_card("Risk/Reward", f"{rr:.1f}x", "green" if rr >= 2 else "orange" if rr >= 1 else "red"), unsafe_allow_html=True)
        with tpc[4]:
            st.markdown(metric_card("Hold", hold, "purple"), unsafe_allow_html=True)
        st.markdown("")

        # Confidence bar
        p_color = "green" if conf >= 75 else "orange" if conf >= 60 else "red"
        st.markdown(f"""<div class="card-sm" style="margin-bottom:24px">
            <div class="label">Confidence Score</div>
            <div class="value-lg" style="margin:4px 0 8px">{conf:.0f}%</div>
            {progress_bar(conf, 100, p_color)}
        </div>""", unsafe_allow_html=True)

    # ── Scanner signals (if from a pick) ──
    if raw and raw.get("scanner_signals"):
        signals = raw["scanner_signals"]
        sg = st.columns(6)
        rsi_v = signals.get("rsi", 50)
        with sg[0]:
            st.markdown(metric_card("RSI", f"{rsi_v:.0f}", "green" if rsi_v < 30 else "red" if rsi_v > 70 else None, "Oversold" if rsi_v < 30 else "Overbought" if rsi_v > 70 else "Neutral"), unsafe_allow_html=True)
        with sg[1]:
            st.markdown(metric_card("P/E", f"{signals.get('pe_ratio',0):.1f}" if signals.get("pe_ratio") else "\u2014"), unsafe_allow_html=True)
        with sg[2]:
            st.markdown(metric_card("Fwd P/E", f"{signals.get('forward_pe',0):.1f}" if signals.get("forward_pe") else "\u2014"), unsafe_allow_html=True)
        with sg[3]:
            st.markdown(metric_card("Rev Growth", f"{signals.get('revenue_growth',0)*100:.1f}%" if signals.get("revenue_growth") else "\u2014", "green" if (signals.get("revenue_growth") or 0) > 0.1 else None), unsafe_allow_html=True)
        with sg[4]:
            st.markdown(metric_card("Margins", f"{signals.get('profit_margins',0)*100:.1f}%" if signals.get("profit_margins") else "\u2014"), unsafe_allow_html=True)
        with sg[5]:
            st.markdown(metric_card("P/B", f"{signals.get('price_to_book',0):.2f}" if signals.get("price_to_book") else "\u2014"), unsafe_allow_html=True)
        st.markdown("")

    # ── C. Technical Analysis Section ──
    st.markdown('<div class="section-title" style="margin-top:8px">Technical Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Trend, momentum, volume, support/resistance \u2014 what the chart says.</div>', unsafe_allow_html=True)
    st.plotly_chart(create_chart(sdf, tk, 520), use_container_width=True, key=f"{key_prefix}_chart_{tk}")

    h52 = info.get("fiftyTwoWeekHigh", 0) or 0
    l52 = info.get("fiftyTwoWeekLow", 0) or 0
    sma50 = sdf["SMA_50"].iloc[-1] if "SMA_50" in sdf else 0
    sma200 = sdf["SMA_200"].iloc[-1] if "SMA_200" in sdf else 0
    rsi_v = sdf["RSI"].iloc[-1] if "RSI" in sdf else 50

    pc = st.columns(6)
    for j, (lbl, val) in enumerate([
        ("52W High", f"${h52:.2f}"), ("52W Low", f"${l52:.2f}"),
        ("SMA 50", f"${sma50:.2f}"), ("SMA 200", f"${sma200:.2f}"),
        ("RSI", f"{rsi_v:.0f}"), ("Beta", f"{info.get('beta',0):.2f}" if info.get('beta') else "\u2014"),
    ]):
        with pc[j]:
            st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-md" style="margin-top:4px">{val}</div></div>', unsafe_allow_html=True)

    # Trend assessment
    macd_v = sdf["MACD"].iloc[-1] if "MACD" in sdf else 0
    macd_sig = sdf["MACD_Signal"].iloc[-1] if "MACD_Signal" in sdf else 0
    golden = sma50 > sma200 if sma50 and sma200 else False

    st.markdown('<div class="section-title">Trend Assessment</div>', unsafe_allow_html=True)
    ta = st.columns(4)
    with ta[0]:
        trend = "Bullish" if curr > sma200 and curr > sma50 else "Neutral" if curr > sma200 else "Bearish"
        t_color = "green" if trend == "Bullish" else "red" if trend == "Bearish" else "orange"
        st.markdown(metric_card("Overall Trend", trend, t_color), unsafe_allow_html=True)
    with ta[1]:
        st.markdown(metric_card("MA Cross", "Golden Cross" if golden else "Death Cross", "green" if golden else "red"), unsafe_allow_html=True)
    with ta[2]:
        st.markdown(metric_card("MACD Signal", "Bullish" if macd_v > macd_sig else "Bearish", "green" if macd_v > macd_sig else "red", f"MACD: {macd_v:.3f}"), unsafe_allow_html=True)
    with ta[3]:
        rsi_state = "Oversold" if rsi_v < 30 else "Overbought" if rsi_v > 70 else "Neutral"
        st.markdown(metric_card("RSI State", rsi_state, "green" if rsi_v < 30 else "red" if rsi_v > 70 else None, f"RSI: {rsi_v:.0f}"), unsafe_allow_html=True)

    # Support & Resistance
    st.markdown('<div class="section-title">Support & Resistance</div>', unsafe_allow_html=True)
    recent = sdf.tail(60)
    r20 = recent["High"].rolling(20).max().iloc[-1]
    s20 = recent["Low"].rolling(20).min().iloc[-1]
    r60 = sdf.tail(120)["High"].max()
    s60 = sdf.tail(120)["Low"].min()
    sr = st.columns(4)
    with sr[0]:
        st.markdown(metric_card("Resistance (20d)", f"${r20:.2f}", "red" if curr > r20 * 0.98 else None), unsafe_allow_html=True)
    with sr[1]:
        st.markdown(metric_card("Support (20d)", f"${s20:.2f}", "green" if curr < s20 * 1.02 else None), unsafe_allow_html=True)
    with sr[2]:
        st.markdown(metric_card("Resistance (60d)", f"${r60:.2f}"), unsafe_allow_html=True)
    with sr[3]:
        st.markdown(metric_card("Support (60d)", f"${s60:.2f}"), unsafe_allow_html=True)

    # Moving Average Table
    st.markdown('<div class="section-title">Moving Averages</div>', unsafe_allow_html=True)
    ma_data = []
    for p in [20, 50, 100, 200]:
        ma = sdf["Close"].rolling(p).mean().iloc[-1]
        if not np.isnan(ma):
            diff = ((curr - ma) / ma) * 100
            ma_data.append({
                "Period": f"SMA {p}",
                "Value": f"${ma:.2f}",
                "vs Price": f"{diff:+.2f}%",
                "Signal": "Bullish" if curr > ma else "Bearish",
            })
    if ma_data:
        st.dataframe(pd.DataFrame(ma_data), use_container_width=True, hide_index=True)

    # ── D. Fundamental Analysis Section ──
    st.markdown('<div class="section-title">Fundamental Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Valuation, profitability, growth, dividends \u2014 what the business is worth.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:0">Valuation</div>', unsafe_allow_html=True)
    vc_cols = st.columns(6)
    for j, (lbl, key) in enumerate([
        ("P/E", "trailingPE"), ("Fwd P/E", "forwardPE"), ("PEG", "pegRatio"),
        ("P/B", "priceToBook"), ("P/S", "priceToSalesTrailing12Months"), ("EV/EBITDA", "enterpriseToEbitda"),
    ]):
        with vc_cols[j]:
            v = info.get(key)
            dot_html = ""
            if v is not None:
                if lbl == "P/E":
                    dot_html = health_dot(v, 20, 30, False)
                elif lbl == "PEG":
                    dot_html = health_dot(v, 1.0, 2.0, False)
            st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">{dot_html} {f"{v:.2f}" if v else "\u2014"}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Profitability</div>', unsafe_allow_html=True)
    pf = st.columns(5)
    for j, (lbl, key, g, b) in enumerate([
        ("Gross Margin", "grossMargins", 0.4, 0.2),
        ("Op Margin", "operatingMargins", 0.2, 0.1),
        ("Net Margin", "profitMargins", 0.15, 0.05),
        ("ROE", "returnOnEquity", 0.15, 0.08),
        ("ROA", "returnOnAssets", 0.08, 0.03),
    ]):
        with pf[j]:
            v = info.get(key)
            dot = health_dot(v, g, b, True) if v else ""
            st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">{dot} {pct(v)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Growth</div>', unsafe_allow_html=True)
    gi = st.columns(5)
    with gi[0]:
        rg = info.get("revenueGrowth")
        st.markdown(metric_card("Rev Growth", pct(rg), "green" if (rg or 0) > 0.1 else None), unsafe_allow_html=True)
    with gi[1]:
        eg = info.get("earningsGrowth")
        st.markdown(metric_card("Earnings Growth", pct(eg), "green" if (eg or 0) > 0.1 else None), unsafe_allow_html=True)
    with gi[2]:
        st.markdown(metric_card("Revenue", fmt(info.get("totalRevenue"))), unsafe_allow_html=True)
    with gi[3]:
        st.markdown(metric_card("EPS", f"${info['trailingEps']:.2f}" if info.get("trailingEps") else "\u2014"), unsafe_allow_html=True)
    with gi[4]:
        st.markdown(metric_card("Market Cap", fmt(info.get("marketCap")), "blue"), unsafe_allow_html=True)

    st.markdown('<div class="section-title">Dividends</div>', unsafe_allow_html=True)
    di = st.columns(4)
    with di[0]:
        dy = info.get("dividendYield")
        st.markdown(metric_card("Div Yield", f"{dy*100:.2f}%" if dy else "\u2014", "green" if dy and dy > 0.02 else None), unsafe_allow_html=True)
    with di[1]:
        dr = info.get("dividendRate")
        st.markdown(metric_card("Div Rate", f"${dr:.2f}" if dr else "\u2014"), unsafe_allow_html=True)
    with di[2]:
        pr = info.get("payoutRatio")
        st.markdown(metric_card("Payout Ratio", pct(pr), "orange" if pr and pr > 0.8 else None), unsafe_allow_html=True)
    with di[3]:
        exd = info.get("exDividendDate")
        if isinstance(exd, (int, float)) and exd > 0:
            from datetime import datetime
            try:
                exd_str = datetime.fromtimestamp(exd).strftime("%b %d, %Y")
            except Exception:
                exd_str = "\u2014"
        elif isinstance(exd, str):
            exd_str = exd
        else:
            exd_str = "\u2014"
        st.markdown(metric_card("Ex-Dividend", exd_str), unsafe_allow_html=True)

    # Revenue & Earnings chart
    if not fin["income"].empty:
        inc = fin["income"]
        rev_r = next((x for x in inc.index if "revenue" in str(x).lower() and "total" in str(x).lower()), None)
        ni_r = next((x for x in inc.index if "net income" in str(x).lower()), None)
        if rev_r:
            st.markdown('<div class="section-title">Revenue & Earnings</div>', unsafe_allow_html=True)
            rd_data = inc.loc[rev_r].dropna().sort_index()
            fig_r = go.Figure()
            fig_r.add_trace(go.Bar(
                x=[d.strftime("%b %Y") if hasattr(d, "strftime") else str(d) for d in rd_data.index],
                y=rd_data.values, name="Revenue", marker_color="#007aff",
            ))
            if ni_r:
                nd = inc.loc[ni_r].dropna().sort_index()
                fig_r.add_trace(go.Bar(
                    x=[d.strftime("%b %Y") if hasattr(d, "strftime") else str(d) for d in nd.index],
                    y=nd.values, name="Net Income", marker_color="#34c759",
                ))
            fig_r.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=300, barmode="group",
                legend=dict(orientation="h"),
                margin=dict(l=50, r=20, t=10, b=40),
                font=dict(family="Inter", color="#1d1d1f"),
            )
            fig_r.update_xaxes(gridcolor="#f5f5f7")
            fig_r.update_yaxes(gridcolor="#f5f5f7")
            st.plotly_chart(fig_r, use_container_width=True, key=f"{key_prefix}_revenue_{tk}")

    # ── E. Quantitative Analysis Section ──
    st.markdown('<div class="section-title">Quantitative Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Volatility, risk metrics, return distribution, factor exposure.</div>', unsafe_allow_html=True)

    rets = sdf["Close"].pct_change().dropna()
    v20 = rets.tail(20).std() * np.sqrt(252) * 100
    v60 = rets.tail(60).std() * np.sqrt(252) * 100
    mdd = ((sdf["Close"] / sdf["Close"].cummax()) - 1).min() * 100
    sharpe = (rets.mean() * 252) / (rets.std() * np.sqrt(252)) if rets.std() > 0 else 0
    sortino_rets = rets[rets < 0]
    sortino = (rets.mean() * 252) / (sortino_rets.std() * np.sqrt(252)) if len(sortino_rets) > 0 and sortino_rets.std() > 0 else 0

    # Volatility
    st.markdown('<div class="section-title" style="margin-top:0">Volatility</div>', unsafe_allow_html=True)
    qv = st.columns(5)
    with qv[0]:
        st.markdown(metric_card("20d Vol (Ann.)", f"{v20:.1f}%", "red" if v20 > 40 else None), unsafe_allow_html=True)
    with qv[1]:
        st.markdown(metric_card("60d Vol (Ann.)", f"{v60:.1f}%"), unsafe_allow_html=True)
    with qv[2]:
        st.markdown(metric_card("Max Drawdown", f"{mdd:.1f}%", "red" if mdd < -30 else None), unsafe_allow_html=True)
    with qv[3]:
        st.markdown(metric_card("Sharpe Ratio", f"{sharpe:.2f}", "green" if sharpe > 0.5 else "red" if sharpe < 0 else None), unsafe_allow_html=True)
    with qv[4]:
        st.markdown(metric_card("Sortino Ratio", f"{sortino:.2f}", "green" if sortino > 1 else None), unsafe_allow_html=True)

    # Historical vol chart
    if len(rets) > 20:
        roll_vol = rets.rolling(20).std() * np.sqrt(252) * 100
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=roll_vol.index, y=roll_vol.values, name="20d Vol",
            fill="tozeroy", line=dict(color="#007aff", width=1.5),
            fillcolor="rgba(0,122,255,0.1)",
        ))
        fig_vol.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=200, margin=dict(l=50, r=20, t=10, b=20),
            legend=dict(orientation="h"),
            font=dict(family="Inter", color="#1d1d1f"),
        )
        fig_vol.update_xaxes(gridcolor="#f5f5f7")
        fig_vol.update_yaxes(gridcolor="#f5f5f7")
        st.plotly_chart(fig_vol, use_container_width=True, key=f"{key_prefix}_vol_{tk}")

    # Risk metrics
    st.markdown('<div class="section-title">Risk Metrics</div>', unsafe_allow_html=True)
    var_95 = np.percentile(rets, 5) * 100 if len(rets) > 20 else 0
    rm_cols = st.columns(4)
    with rm_cols[0]:
        st.markdown(metric_card("Sharpe Ratio", f"{sharpe:.2f}", "green" if sharpe > 0.5 else "red" if sharpe < 0 else None), unsafe_allow_html=True)
    with rm_cols[1]:
        st.markdown(metric_card("Sortino Ratio", f"{sortino:.2f}", "green" if sortino > 1 else None), unsafe_allow_html=True)
    with rm_cols[2]:
        st.markdown(metric_card("Max Drawdown", f"{mdd:.1f}%", "red" if mdd < -30 else None), unsafe_allow_html=True)
    with rm_cols[3]:
        st.markdown(metric_card("VaR (95%)", f"{var_95:.2f}%", "red" if var_95 < -3 else None, "Daily worst 5th percentile"), unsafe_allow_html=True)

    # Return distribution
    st.markdown('<div class="section-title">Return Distribution</div>', unsafe_allow_html=True)
    avg_daily = rets.mean() * 100
    best_day = rets.max() * 100
    worst_day = rets.min() * 100
    pos_days = (rets > 0).sum() / len(rets) * 100 if len(rets) > 0 else 0
    from scipy import stats as scipy_stats
    try:
        skew_val = float(scipy_stats.skew(rets))
        kurt_val = float(scipy_stats.kurtosis(rets))
    except Exception:
        skew_val = 0.0
        kurt_val = 0.0

    qr = st.columns(6)
    with qr[0]:
        st.markdown(metric_card("Avg Daily", f"{avg_daily:.3f}%"), unsafe_allow_html=True)
    with qr[1]:
        st.markdown(metric_card("Best Day", f"+{best_day:.1f}%", "green"), unsafe_allow_html=True)
    with qr[2]:
        st.markdown(metric_card("Worst Day", f"{worst_day:.1f}%", "red"), unsafe_allow_html=True)
    with qr[3]:
        st.markdown(metric_card("Win Rate", f"{pos_days:.0f}%", "green" if pos_days > 52 else None), unsafe_allow_html=True)
    with qr[4]:
        st.markdown(metric_card("Skewness", f"{skew_val:.2f}", "red" if skew_val < -0.5 else None), unsafe_allow_html=True)
    with qr[5]:
        st.markdown(metric_card("Kurtosis", f"{kurt_val:.2f}", "orange" if kurt_val > 3 else None), unsafe_allow_html=True)

    # Factor exposure
    st.markdown('<div class="section-title">Factor Exposure</div>', unsafe_allow_html=True)
    beta = info.get("beta", 0) or 0
    mcap = info.get("marketCap", 0) or 0
    pe = info.get("trailingPE", 0) or 0
    fe = st.columns(6)
    with fe[0]:
        st.markdown(metric_card("Beta", f"{beta:.2f}" if beta else "\u2014", "orange" if beta > 1.3 else None, "High Beta" if beta > 1.3 else "Low Beta" if beta < 0.7 else "Market"), unsafe_allow_html=True)
    with fe[1]:
        size = "Large Cap" if mcap > 10e9 else "Mid Cap" if mcap > 2e9 else "Small Cap"
        st.markdown(metric_card("Size Factor", size, None, fmt(mcap)), unsafe_allow_html=True)
    with fe[2]:
        val_label = "Deep Value" if pe < 12 else "Value" if pe < 18 else "Growth" if pe < 30 else "Expensive"
        st.markdown(metric_card("Value Factor", val_label, "green" if pe < 15 else None, f"P/E {pe:.1f}" if pe else "\u2014"), unsafe_allow_html=True)
    with fe[3]:
        mom_3m = ((curr - sdf["Close"].iloc[-63]) / sdf["Close"].iloc[-63] * 100) if len(sdf) > 63 else 0
        st.markdown(metric_card("Momentum (3m)", f"{mom_3m:+.1f}%", "green" if mom_3m > 5 else "red" if mom_3m < -5 else None), unsafe_allow_html=True)
    with fe[4]:
        mom_6m = ((curr - sdf["Close"].iloc[-126]) / sdf["Close"].iloc[-126] * 100) if len(sdf) > 126 else 0
        st.markdown(metric_card("Momentum (6m)", f"{mom_6m:+.1f}%", "green" if mom_6m > 10 else "red" if mom_6m < -10 else None), unsafe_allow_html=True)
    with fe[5]:
        mom_12m = ((curr - sdf["Close"].iloc[-252]) / sdf["Close"].iloc[-252] * 100) if len(sdf) > 252 else 0
        st.markdown(metric_card("Momentum (12m)", f"{mom_12m:+.1f}%", "green" if mom_12m > 15 else "red" if mom_12m < -15 else None), unsafe_allow_html=True)

    # Correlation with SPY
    try:
        if not tk.upper().startswith("SPY"):
            spy_data = get_stock_data("SPY", "1y", "1d")
            if not spy_data.empty:
                spy_rets = spy_data["Close"].pct_change().dropna()
                stock_rets_1y = sdf["Close"].pct_change().dropna().tail(len(spy_rets))
                spy_rets = spy_rets.tail(len(stock_rets_1y))
                if len(stock_rets_1y) > 20 and len(spy_rets) > 20:
                    common_idx = stock_rets_1y.index.intersection(spy_rets.index)
                    if len(common_idx) > 20:
                        corr = stock_rets_1y.loc[common_idx].corr(spy_rets.loc[common_idx])
                        st.markdown(f"""<div class="card-sm" style="margin-top:12px">
                            <div class="label">Correlation with SPY</div>
                            <div class="value-lg" style="margin-top:4px">{corr:.3f}</div>
                            <div class="caption">{"Highly correlated" if corr > 0.7 else "Moderately correlated" if corr > 0.4 else "Low correlation"} ({len(common_idx)} trading days)</div>
                        </div>""", unsafe_allow_html=True)
    except Exception:
        pass

    # ── F. Financial Health Section ──
    st.markdown('<div class="section-title">Financial Health</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Balance sheet strength, cash flow quality, analyst consensus.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:0">Balance Sheet</div>', unsafe_allow_html=True)
    bs = st.columns(6)
    cash = info.get("totalCash", 0) or 0
    debt = info.get("totalDebt", 0) or 0
    with bs[0]:
        st.markdown(metric_card("Cash", fmt(cash), "green"), unsafe_allow_html=True)
    with bs[1]:
        st.markdown(metric_card("Debt", fmt(debt), "red" if debt > cash else None), unsafe_allow_html=True)
    with bs[2]:
        st.markdown(metric_card("Net Cash/Debt", fmt(cash - debt), "green" if cash > debt else "red"), unsafe_allow_html=True)
    with bs[3]:
        de = info.get("debtToEquity")
        st.markdown(f'<div class="card-sm"><div class="label">D/E Ratio</div><div class="value-lg" style="margin-top:4px">{health_dot(de, 50, 100, False) if de else ""} {f"{de:.0f}" if de else "\u2014"}</div></div>', unsafe_allow_html=True)
    with bs[4]:
        cr = info.get("currentRatio")
        st.markdown(f'<div class="card-sm"><div class="label">Current Ratio</div><div class="value-lg" style="margin-top:4px">{health_dot(cr, 1.5, 1.0, True) if cr else ""} {f"{cr:.2f}" if cr else "\u2014"}</div></div>', unsafe_allow_html=True)
    with bs[5]:
        qr_v = info.get("quickRatio")
        st.markdown(f'<div class="card-sm"><div class="label">Quick Ratio</div><div class="value-lg" style="margin-top:4px">{health_dot(qr_v, 1.0, 0.5, True) if qr_v else ""} {f"{qr_v:.2f}" if qr_v else "\u2014"}</div></div>', unsafe_allow_html=True)

    # Cash Flow
    st.markdown('<div class="section-title">Cash Flow</div>', unsafe_allow_html=True)
    cf = st.columns(4)
    ocf = info.get("operatingCashflow", 0) or 0
    fcf_v = info.get("freeCashflow", 0) or 0
    rev = info.get("totalRevenue", 0) or 0
    with cf[0]:
        st.markdown(metric_card("Operating CF", fmt(ocf), "green" if ocf > 0 else "red"), unsafe_allow_html=True)
    with cf[1]:
        st.markdown(metric_card("Free Cash Flow", fmt(fcf_v), "green" if fcf_v > 0 else "red"), unsafe_allow_html=True)
    with cf[2]:
        fcf_margin = (fcf_v / rev * 100) if rev > 0 else 0
        st.markdown(metric_card("FCF Margin", f"{fcf_margin:.1f}%", "green" if fcf_margin > 10 else None), unsafe_allow_html=True)
    with cf[3]:
        fcf_yield = (fcf_v / mcap * 100) if mcap > 0 else 0
        st.markdown(metric_card("FCF Yield", f"{fcf_yield:.1f}%", "green" if fcf_yield > 5 else None), unsafe_allow_html=True)

    # Analyst Consensus
    st.markdown('<div class="section-title">Analyst Consensus</div>', unsafe_allow_html=True)
    at = st.columns(4)
    with at[0]:
        rec = (info.get("recommendationKey", "") or "").replace("_", " ").title()
        st.markdown(metric_card("Recommendation", rec or "\u2014", "green" if "buy" in rec.lower() else "red" if "sell" in rec.lower() else "orange"), unsafe_allow_html=True)
    with at[1]:
        st.markdown(metric_card("Target Low", f"${info.get('targetLowPrice', 0):.2f}" if info.get("targetLowPrice") else "\u2014"), unsafe_allow_html=True)
    with at[2]:
        st.markdown(metric_card("Target Mean", f"${info.get('targetMeanPrice', 0):.2f}" if info.get("targetMeanPrice") else "\u2014", "blue"), unsafe_allow_html=True)
    with at[3]:
        st.markdown(metric_card("Target High", f"${info.get('targetHighPrice', 0):.2f}" if info.get("targetHighPrice") else "\u2014"), unsafe_allow_html=True)

    # ── G. Financial Statements ──
    st.markdown('<div class="section-title">Financial Statements</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Quarterly data with dates.</div>', unsafe_allow_html=True)

    def _show_stmt(title, df_raw, keys, stmt_key):
        st.markdown(f'<div class="section-title" style="margin-top:8px;font-size:20px">{title}</div>', unsafe_allow_html=True)
        if df_raw.empty:
            st.info("No data available")
            return
        d = df_raw.iloc[:, :6].copy()
        d.columns = [c.strftime("%b %d, %Y") if hasattr(c, "strftime") else str(c) for c in d.columns]
        rows = [i for i in d.index if any(k in str(i).lower() for k in keys)]
        display_df = d.loc[rows] if rows else d.head(15)
        st.dataframe(
            display_df.style.format(
                lambda x: fmt(x) if isinstance(x, (int, float, np.integer, np.floating)) else x
            ),
            use_container_width=True,
        )

    _show_stmt("Income Statement", fin["income"],
               ["total revenue", "gross profit", "operating income", "net income", "ebitda", "diluted eps", "research", "interest"],
               "income")
    _show_stmt("Balance Sheet", fin["balance"],
               ["total assets", "total liab", "stockholder", "current assets", "current liab", "cash and cash", "total debt", "retained"],
               "balance")
    _show_stmt("Cash Flow", fin["cashflow"],
               ["operating cash", "free cash", "capital expend", "depreciation", "stock based", "repurchase", "dividends"],
               "cashflow")

    # ── H. About & Agent Verdicts ──
    st.markdown('<div class="section-title">About & Analysis</div>', unsafe_allow_html=True)

    if raw and raw.get("agent_verdicts"):
        st.markdown('<div class="section-title" style="font-size:20px;margin-top:8px">Agent Verdicts</div>', unsafe_allow_html=True)
        for ag in raw["agent_verdicts"]:
            a_name = ag.get("name", "Agent")
            a_v = ag.get("verdict", "WATCH")
            a_conf = ag.get("confidence", 0)
            if a_conf <= 1:
                a_conf *= 100
            a_reason = ag.get("reasoning", "")
            border = "#34c759" if a_v == "BUY" else "#ff3b30" if a_v == "PASS" else "#ff9500"
            badge_cls = "badge-green" if a_v == "BUY" else "badge-red" if a_v == "PASS" else "badge-orange"
            st.markdown(f"""<div class="card" style="border-left:4px solid {border};margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div><span style="font-weight:600;font-size:16px">{a_name}</span> <span class="badge {badge_cls}" style="margin-left:8px">{a_v}</span></div>
                    <span class="caption">{a_conf:.0f}%</span>
                </div>
                {"<div style='margin-top:12px;font-size:14px;color:#424245;line-height:1.7'>" + a_reason + "</div>" if a_reason else ""}
            </div>""", unsafe_allow_html=True)

    desc = info.get("longBusinessSummary", "")
    if desc:
        st.markdown('<div class="section-title" style="font-size:20px">Company Description</div>', unsafe_allow_html=True)
        emp_val = info.get("fullTimeEmployees")
        if isinstance(emp_val, (int, float)):
            emp = f"{int(emp_val):,}"
        else:
            emp = "\u2014"
        st.markdown(f"""<div class="card"><div style="font-size:14px;color:#424245;line-height:1.7">{desc}</div>
            <div style="margin-top:16px;display:flex;gap:24px;flex-wrap:wrap">
                <div><span class="label">Industry</span><br><span class="value-sm">{info.get("industry", "\u2014")}</span></div>
                <div><span class="label">Employees</span><br><span class="value-sm">{emp}</span></div>
                <div><span class="label">Country</span><br><span class="value-sm">{info.get("country", "\u2014")}</span></div>
                <div><span class="label">Website</span><br><span class="value-sm">{info.get("website", "\u2014")}</span></div>
            </div>
        </div>""", unsafe_allow_html=True)
