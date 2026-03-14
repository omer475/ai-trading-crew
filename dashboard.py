"""
AI Trading Crew — Dashboard
Apple-inspired design. Beautiful, minimal, information-dense.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import asyncio, json, os, glob

st.set_page_config(page_title="AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="collapsed")

# ─── Apple Design System CSS ────────────────────────────────────────
st.markdown("""
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
#MainMenu, footer, header { visibility: hidden; }

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
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────

@st.cache_data(ttl=120)
def get_stock_data(sym, period="1y", interval="1d"):
    return yf.Ticker(sym).history(period=period, interval=interval)

@st.cache_data(ttl=300)
def get_stock_info(sym):
    return yf.Ticker(sym).info

@st.cache_data(ttl=300)
def get_financials(sym):
    t = yf.Ticker(sym)
    try: return {"income": t.quarterly_income_stmt, "balance": t.quarterly_balance_sheet, "cashflow": t.quarterly_cashflow}
    except: return {"income": pd.DataFrame(), "balance": pd.DataFrame(), "cashflow": pd.DataFrame()}

def calc_indicators(df):
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

def fmt(n):
    if n is None: return "—"
    a = abs(n)
    if a >= 1e12: return f"${n/1e12:.1f}T"
    if a >= 1e9: return f"${n/1e9:.1f}B"
    if a >= 1e6: return f"${n/1e6:.1f}M"
    return f"${n:,.0f}"

def pct(n):
    if n is None: return "—"
    return f"{n*100:.1f}%"

def metric_card(label, value, accent=None, subtitle=None):
    cls = f"card-sm card-{accent}" if accent else "card-sm"
    sub = f'<div class="caption" style="margin-top:4px">{subtitle}</div>' if subtitle else ""
    return f'<div class="{cls}"><div class="label">{label}</div><div class="value-lg">{value}</div>{sub}</div>'

def health_dot(value, good_threshold, bad_threshold, higher_is_better=True):
    if value is None: return '<span class="dot dot-orange"></span>'
    if higher_is_better:
        if value >= good_threshold: return '<span class="dot dot-green"></span>'
        elif value >= bad_threshold: return '<span class="dot dot-orange"></span>'
        else: return '<span class="dot dot-red"></span>'
    else:
        if value <= good_threshold: return '<span class="dot dot-green"></span>'
        elif value <= bad_threshold: return '<span class="dot dot-orange"></span>'
        else: return '<span class="dot dot-red"></span>'

def progress_bar(value, max_val=100, color="blue"):
    pct_w = min(max(value / max_val * 100, 0), 100) if max_val > 0 else 0
    return f'<div class="progress-bg"><div class="progress-fill progress-{color}" style="width:{pct_w}%"></div></div>'

def create_chart(df, sym, height=480):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name=sym, increasing_line_color="#34c759", decreasing_line_color="#ff3b30",
        increasing_fillcolor="#34c759", decreasing_fillcolor="#ff3b30"), row=1, col=1)
    if "SMA_50" in df: fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="50 SMA", line=dict(color="#007aff", width=1.5)), row=1, col=1)
    if "SMA_200" in df: fig.add_trace(go.Scatter(x=df.index, y=df["SMA_200"], name="200 SMA", line=dict(color="#af52de", width=1.5)), row=1, col=1)
    vc = ["#34c75966" if c >= o else "#ff3b3066" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=vc), row=2, col=1)
    if "RSI" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="#ff9500", width=1.5)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#ff3b3044", row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#34c75944", row=3, col=1)
        fig.update_yaxes(range=[0, 100], row=3, col=1)
    fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=height, margin=dict(l=50, r=20, t=10, b=20), xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, font=dict(size=11, color="#86868b")),
        font=dict(family="Inter", color="#1d1d1f"))
    fig.update_xaxes(gridcolor="#f5f5f7", showgrid=True, zeroline=False)
    fig.update_yaxes(gridcolor="#f5f5f7", showgrid=True, zeroline=False)
    return fig

def get_latest_report():
    rd = os.path.join(os.path.dirname(__file__) or ".", "reports")
    if not os.path.exists(rd): return None
    jf = sorted(glob.glob(os.path.join(rd, "*_scan.json")), reverse=True)
    if not jf: return None
    with open(jf[0]) as f: return json.load(f)

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
    if not r: return '<span class="badge badge-gray">Unknown</span>'
    if isinstance(r, dict): r = r.get("regime", "Unknown")
    rl = str(r).lower()
    if "strong" in rl and "bull" in rl: return f'<span class="badge badge-green">{r.replace("_"," ").title()}</span>'
    if "bull" in rl: return f'<span class="badge badge-green">{r.replace("_"," ").title()}</span>'
    if "strong" in rl and "bear" in rl: return f'<span class="badge badge-red">{r.replace("_"," ").title()}</span>'
    if "bear" in rl: return f'<span class="badge badge-red">{r.replace("_"," ").title()}</span>'
    if "volatile" in rl: return f'<span class="badge badge-orange">{r.replace("_"," ").title()}</span>'
    return f'<span class="badge badge-gray">{r.replace("_"," ").title()}</span>'


# ═══ NAV ═════════════════════════════════════════════════════════════
st.markdown("""<div style="display:flex;align-items:center;justify-content:space-between;padding:20px 0;border-bottom:1px solid #e8e8ed;margin-bottom:32px">
    <div><div style="font-size:20px;font-weight:700;color:#1d1d1f;letter-spacing:-0.5px">AI Trading Crew</div>
    <div style="font-size:12px;color:#86868b">1,003 stocks &middot; LSE + US &middot; Long-term</div></div>
</div>""", unsafe_allow_html=True)

tab_home, tab_picks, tab_stock, tab_scan = st.tabs(["Overview", "Top Picks", "Stock Detail", "Run Scan"])


# ═══ TAB 1: OVERVIEW ════════════════════════════════════════════════
with tab_home:
    report = get_latest_report()
    if report:
        picks = report.get("picks", [])
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="card"><div class="label">Market Regime</div><div style="margin-top:10px">{regime_badge(report.get("regime"))}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="card"><div class="label">Last Scan</div><div class="value-lg" style="margin-top:4px">{report.get("scan_date","—")}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="card"><div class="label">Stocks Scanned</div><div class="value-xl" style="margin-top:4px">{report.get("stocks_scanned",0):,}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="card"><div class="label">Top Picks</div><div class="value-xl" style="margin-top:4px">{len(picks)}</div></div>', unsafe_allow_html=True)

        if picks:
            st.markdown('<div class="section-title">Top Recommendations</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">AI-selected from 1,003 stocks. Updated every 2 weeks.</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(picks), 3))
            for i, raw_pick in enumerate(picks[:3]):
                with cols[i]:
                    pick = normalize_pick(raw_pick)
                    tk = pick["ticker"]
                    conf = pick["confidence"]
                    reason = pick["reason"]
                    p_color = "green" if conf >= 75 else "orange" if conf >= 60 else "red"
                    st.markdown(f"""<div class="card">
                        <div class="caption">#{i+1} Pick</div>
                        <div class="value-lg" style="margin:6px 0 2px">{pick["name"] or tk}</div>
                        <div class="caption">{tk} &middot; {pick["sector"]}</div>
                        <div class="value-xl" style="margin:16px 0 12px">${pick["price"]:.2f}</div>
                        <div class="label">Confidence</div>
                        {progress_bar(conf, 100, p_color)}
                        <div class="caption" style="margin-top:6px">{conf:.0f}%</div>
                        <div style="margin-top:16px;font-size:14px;color:#424245;line-height:1.6">{reason[:180]}{'...' if len(reason)>180 else ''}</div>
                    </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="text-align:center;padding:100px 0">
            <div class="hero-title">AI Trading Crew</div>
            <div class="hero-sub" style="max-width:460px;margin:12px auto 0">50 AI agents scan 1,003 stocks across LSE and US markets to find the best long-term investments.</div>
            <div style="margin-top:48px;font-size:14px;color:#86868b">Go to <b>Run Scan</b> to start your first analysis.</div>
        </div>""", unsafe_allow_html=True)


# ═══ TAB 2: TOP PICKS ═══════════════════════════════════════════════
with tab_picks:
    report = get_latest_report()
    if report and report.get("picks"):
        picks = report["picks"]
        st.markdown('<div class="section-title">All Recommendations</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-sub">{len(picks)} stocks from {report.get("stocks_scanned",1003):,} scanned on {report.get("scan_date","—")}</div>', unsafe_allow_html=True)

        for i, raw_pick in enumerate(picks):
            pick = normalize_pick(raw_pick)
            tk = pick["ticker"]
            name = pick["name"] or tk
            price = pick["price"]
            conf = pick["confidence"]
            entry_lo = pick["entry_low"] or price*0.95
            entry_hi = pick["entry_high"] or price*1.02
            sl = pick["stop_loss"] or price*0.85
            tgt = pick["target"] or price*1.40
            reason = pick["reason"]
            agents = pick.get("agent_verdicts") or pick.get("agents_agreed", [])
            hold = pick["hold_period"]
            sector = pick["sector"]
            market = pick["market"]
            upside = ((tgt-price)/price*100) if price else 0
            downside = ((price-sl)/price*100) if price else 0
            rr = upside/downside if downside > 0 else 0

            with st.expander(f"#{i+1}  {name} ({tk})  —  ${price:.2f}  —  {conf:.0f}% confidence", expanded=(i<2)):

                # ── Dark Header Card ──
                st.markdown(f"""<div class="pick-header">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start">
                        <div>
                            <div class="label">#{i+1} RECOMMENDATION</div>
                            <div style="font-size:28px;font-weight:700;margin:8px 0 4px">{name}</div>
                            <div style="font-size:14px;color:rgba(255,255,255,0.5)">{tk} &middot; {sector} &middot; {market}</div>
                        </div>
                        <div style="text-align:right">
                            <div class="value-xl">${price:.2f}</div>
                            <div style="margin-top:8px">{progress_bar(conf, 100, "blue")}</div>
                            <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px">{conf:.0f}% confidence</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                # ── AI Reasoning ──
                if reason:
                    st.markdown(f"""<div class="reasoning-box">
                        <div class="label" style="color:#1565c0;margin-bottom:10px">AI REASONING</div>
                        <p>{reason}</p>
                    </div>""", unsafe_allow_html=True)

                # ── Trade Plan Cards ──
                tp1, tp2, tp3, tp4, tp5 = st.columns(5)
                with tp1:
                    st.markdown(metric_card("Entry Range", f"${entry_lo:.2f}–${entry_hi:.2f}", "blue"), unsafe_allow_html=True)
                with tp2:
                    st.markdown(metric_card("Target Price", f"${tgt:.2f}", "green", f"+{upside:.1f}% upside"), unsafe_allow_html=True)
                with tp3:
                    st.markdown(metric_card("Stop Loss", f"${sl:.2f}", "red", f"-{downside:.1f}% risk"), unsafe_allow_html=True)
                with tp4:
                    rr_color = "green" if rr >= 2 else "orange" if rr >= 1 else "red"
                    st.markdown(metric_card("Risk / Reward", f"{rr:.1f}x", rr_color), unsafe_allow_html=True)
                with tp5:
                    st.markdown(metric_card("Hold Period", hold, "purple"), unsafe_allow_html=True)

                st.markdown("")

                # ── Fetch live data ──
                try:
                    sdf = get_stock_data(tk, "2y", "1d")
                    info = get_stock_info(tk)
                    fin = get_financials(tk)
                    ok = not sdf.empty
                except:
                    ok = False; sdf = pd.DataFrame(); info = {}; fin = {"income":pd.DataFrame(),"balance":pd.DataFrame(),"cashflow":pd.DataFrame()}

                if ok:
                    sdf = calc_indicators(sdf)
                    curr = sdf["Close"].iloc[-1]

                    t_chart, t_fund, t_health, t_statements, t_agents = st.tabs([
                        "Chart", "Fundamentals", "Financial Health", "Statements", "Agent Verdicts"
                    ])

                    # ════════════════════════════════════════════
                    # CHART TAB
                    # ════════════════════════════════════════════
                    with t_chart:
                        st.plotly_chart(create_chart(sdf, tk, 520), use_container_width=True)

                        # Price context row
                        h52 = info.get("fiftyTwoWeekHigh", 0) or 0
                        l52 = info.get("fiftyTwoWeekLow", 0) or 0
                        sma50 = sdf["SMA_50"].iloc[-1] if "SMA_50" in sdf else 0
                        sma200 = sdf["SMA_200"].iloc[-1] if "SMA_200" in sdf else 0
                        rsi = sdf["RSI"].iloc[-1] if "RSI" in sdf else 50
                        macd = sdf["MACD"].iloc[-1] if "MACD" in sdf else 0

                        pc = st.columns(6)
                        labels = ["52W High", "52W Low", "SMA 50", "SMA 200", "RSI (14)", "MACD"]
                        vals = [f"${h52:.2f}", f"${l52:.2f}", f"${sma50:.2f}", f"${sma200:.2f}", f"{rsi:.0f}", f"{macd:.3f}"]
                        dots = [
                            health_dot(curr, h52*0.95, h52*0.85),
                            health_dot(curr, l52*1.15, l52*1.05),
                            health_dot(1 if curr > sma50 else 0, 1, 0.5),
                            health_dot(1 if curr > sma200 else 0, 1, 0.5),
                            health_dot(rsi, 40, 30) if rsi < 50 else health_dot(100-rsi, 40, 30),
                            health_dot(1 if macd > 0 else 0, 1, 0.5),
                        ]
                        for j in range(6):
                            with pc[j]:
                                st.markdown(f'<div class="card-sm"><div class="label">{labels[j]}</div><div class="value-md" style="margin-top:4px">{dots[j]} {vals[j]}</div></div>', unsafe_allow_html=True)

                    # ════════════════════════════════════════════
                    # FUNDAMENTALS TAB
                    # ════════════════════════════════════════════
                    with t_fund:

                        # Valuation
                        st.markdown('<div class="section-title" style="margin-top:8px">Valuation</div>', unsafe_allow_html=True)
                        vc = st.columns(6)
                        val_items = [
                            ("P/E (TTM)", info.get("trailingPE"), None),
                            ("Forward P/E", info.get("forwardPE"), None),
                            ("PEG Ratio", info.get("pegRatio"), None),
                            ("P/B Ratio", info.get("priceToBook"), None),
                            ("P/S Ratio", info.get("priceToSalesTrailing12Months"), None),
                            ("EV/EBITDA", info.get("enterpriseToEbitda"), None),
                        ]
                        for j, (lbl, val, _) in enumerate(val_items):
                            with vc[j]:
                                v = f"{val:.2f}" if val else "—"
                                st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">{v}</div></div>', unsafe_allow_html=True)

                        # Profitability with health dots
                        st.markdown('<div class="section-title">Profitability</div>', unsafe_allow_html=True)
                        prof = st.columns(5)
                        prof_items = [
                            ("Gross Margin", info.get("grossMargins"), 0.4, 0.2, True),
                            ("Operating Margin", info.get("operatingMargins"), 0.2, 0.1, True),
                            ("Net Margin", info.get("profitMargins"), 0.15, 0.05, True),
                            ("ROE", info.get("returnOnEquity"), 0.15, 0.08, True),
                            ("ROA", info.get("returnOnAssets"), 0.08, 0.03, True),
                        ]
                        for j, (lbl, val, g, b, hib) in enumerate(prof_items):
                            with prof[j]:
                                dot = health_dot(val, g, b, hib) if val else ""
                                v = pct(val)
                                st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">{dot} {v}</div></div>', unsafe_allow_html=True)

                        # Growth
                        st.markdown('<div class="section-title">Growth</div>', unsafe_allow_html=True)
                        gc = st.columns(5)
                        growth_items = [
                            ("Revenue Growth", info.get("revenueGrowth"), 0.1, 0, True),
                            ("Earnings Growth", info.get("earningsGrowth"), 0.1, 0, True),
                            ("Revenue (TTM)", None, None, None, None),
                            ("EPS (TTM)", None, None, None, None),
                            ("Forward EPS", None, None, None, None),
                        ]
                        for j, (lbl, val, g, b, hib) in enumerate(growth_items):
                            with gc[j]:
                                if lbl == "Revenue (TTM)":
                                    st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">{fmt(info.get("totalRevenue"))}</div></div>', unsafe_allow_html=True)
                                elif lbl == "EPS (TTM)":
                                    eps = info.get("trailingEps")
                                    st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">${eps:.2f}</div></div>' if eps else f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">—</div></div>', unsafe_allow_html=True)
                                elif lbl == "Forward EPS":
                                    feps = info.get("forwardEps")
                                    st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">${feps:.2f}</div></div>' if feps else f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">—</div></div>', unsafe_allow_html=True)
                                else:
                                    dot = health_dot(val, g, b, hib) if val is not None else ""
                                    st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">{dot} {pct(val)}</div></div>', unsafe_allow_html=True)

                        # Dividends
                        st.markdown('<div class="section-title">Dividends & Returns</div>', unsafe_allow_html=True)
                        dc = st.columns(5)
                        dy = info.get("dividendYield")
                        dr = info.get("dividendRate")
                        pr_ = info.get("payoutRatio")
                        exd = info.get("exDividendDate")
                        avg5 = info.get("fiveYearAvgDividendYield")
                        div_vals = [
                            ("Dividend Yield", f"{dy*100:.2f}%" if dy else "—"),
                            ("Annual Dividend", f"${dr:.2f}" if dr else "—"),
                            ("Payout Ratio", f"{pr_*100:.0f}%" if pr_ else "—"),
                            ("Ex-Dividend", "—"),
                            ("5Y Avg Yield", f"{avg5:.2f}%" if avg5 else "—"),
                        ]
                        if exd:
                            try: div_vals[3] = ("Ex-Dividend", datetime.fromtimestamp(exd).strftime("%b %d, %Y"))
                            except: pass
                        for j, (lbl, v) in enumerate(div_vals):
                            with dc[j]:
                                accent = "green" if lbl == "Dividend Yield" and dy and dy > 0.02 else None
                                st.markdown(metric_card(lbl, v, accent), unsafe_allow_html=True)

                        # Enterprise Value
                        st.markdown('<div class="section-title">Enterprise Value</div>', unsafe_allow_html=True)
                        ev = st.columns(4)
                        with ev[0]: st.markdown(metric_card("Market Cap", fmt(info.get("marketCap")), "blue"), unsafe_allow_html=True)
                        with ev[1]: st.markdown(metric_card("Enterprise Value", fmt(info.get("enterpriseValue"))), unsafe_allow_html=True)
                        with ev[2]: st.markdown(metric_card("EV/Revenue", f"{info.get('enterpriseToRevenue',0):.2f}" if info.get("enterpriseToRevenue") else "—"), unsafe_allow_html=True)
                        with ev[3]:
                            fcf = info.get("freeCashflow",0) or 0
                            mc = info.get("marketCap",1) or 1
                            st.markdown(metric_card("FCF Yield", f"{fcf/mc*100:.1f}%" if mc > 1 else "—", "green" if fcf/mc > 0.04 else None), unsafe_allow_html=True)

                        # Revenue chart
                        if not fin["income"].empty:
                            inc = fin["income"]
                            rev_r = next((x for x in inc.index if "revenue" in str(x).lower() and "total" in str(x).lower()), None)
                            ni_r = next((x for x in inc.index if "net income" in str(x).lower()), None)
                            if rev_r:
                                st.markdown('<div class="section-title">Revenue & Earnings Trend</div>', unsafe_allow_html=True)
                                rd = inc.loc[rev_r].dropna().sort_index()
                                fig_r = go.Figure()
                                fig_r.add_trace(go.Bar(x=[d.strftime("%b %Y") if hasattr(d,"strftime") else str(d) for d in rd.index], y=rd.values, name="Revenue", marker_color="#007aff", marker_cornerradius=6))
                                if ni_r:
                                    nd = inc.loc[ni_r].dropna().sort_index()
                                    fig_r.add_trace(go.Bar(x=[d.strftime("%b %Y") if hasattr(d,"strftime") else str(d) for d in nd.index], y=nd.values, name="Net Income", marker_color="#34c759", marker_cornerradius=6))
                                fig_r.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300, barmode="group", legend=dict(orientation="h"), margin=dict(l=50,r=20,t=10,b=40), font=dict(family="Inter",color="#1d1d1f"))
                                fig_r.update_xaxes(gridcolor="#f5f5f7"); fig_r.update_yaxes(gridcolor="#f5f5f7")
                                st.plotly_chart(fig_r, use_container_width=True)

                    # ════════════════════════════════════════════
                    # FINANCIAL HEALTH TAB
                    # ════════════════════════════════════════════
                    with t_health:
                        st.markdown('<div class="section-title" style="margin-top:8px">Balance Sheet</div>', unsafe_allow_html=True)
                        b = st.columns(6)
                        cash = info.get("totalCash",0) or 0
                        debt = info.get("totalDebt",0) or 0
                        net = cash - debt
                        with b[0]: st.markdown(metric_card("Total Cash", fmt(cash), "green"), unsafe_allow_html=True)
                        with b[1]: st.markdown(metric_card("Total Debt", fmt(debt), "red" if debt > cash else None), unsafe_allow_html=True)
                        with b[2]:
                            nc_color = "green" if net > 0 else "red"
                            st.markdown(metric_card("Net Cash/Debt", fmt(net), nc_color), unsafe_allow_html=True)
                        with b[3]:
                            de = info.get("debtToEquity")
                            de_dot = health_dot(de, 50, 100, False) if de else ""
                            st.markdown(f'<div class="card-sm"><div class="label">Debt/Equity</div><div class="value-lg" style="margin-top:4px">{de_dot} {f"{de:.0f}" if de else "—"}</div></div>', unsafe_allow_html=True)
                        with b[4]:
                            cr = info.get("currentRatio")
                            cr_dot = health_dot(cr, 1.5, 1.0, True) if cr else ""
                            st.markdown(f'<div class="card-sm"><div class="label">Current Ratio</div><div class="value-lg" style="margin-top:4px">{cr_dot} {f"{cr:.2f}" if cr else "—"}</div></div>', unsafe_allow_html=True)
                        with b[5]:
                            qr = info.get("quickRatio")
                            qr_dot = health_dot(qr, 1.0, 0.5, True) if qr else ""
                            st.markdown(f'<div class="card-sm"><div class="label">Quick Ratio</div><div class="value-lg" style="margin-top:4px">{qr_dot} {f"{qr:.2f}" if qr else "—"}</div></div>', unsafe_allow_html=True)

                        st.markdown('<div class="section-title">Cash Flow</div>', unsafe_allow_html=True)
                        cf = st.columns(4)
                        ocf = info.get("operatingCashflow",0) or 0
                        fcf = info.get("freeCashflow",0) or 0
                        rev_ttm = info.get("totalRevenue",1) or 1
                        with cf[0]: st.markdown(metric_card("Operating Cash Flow", fmt(ocf), "green" if ocf > 0 else "red"), unsafe_allow_html=True)
                        with cf[1]: st.markdown(metric_card("Free Cash Flow", fmt(fcf), "green" if fcf > 0 else "red"), unsafe_allow_html=True)
                        with cf[2]: st.markdown(metric_card("FCF Margin", f"{fcf/rev_ttm*100:.1f}%" if rev_ttm > 1 else "—"), unsafe_allow_html=True)
                        with cf[3]: st.markdown(metric_card("OCF/Debt", f"{ocf/debt:.2f}x" if debt > 0 else "No Debt", "green" if debt == 0 or (debt > 0 and ocf/debt > 0.3) else None), unsafe_allow_html=True)

                        # Volatility & Risk
                        st.markdown('<div class="section-title">Volatility & Risk</div>', unsafe_allow_html=True)
                        rets = sdf["Close"].pct_change().dropna()
                        v20 = rets.tail(20).std() * np.sqrt(252) * 100
                        v60 = rets.tail(60).std() * np.sqrt(252) * 100
                        mdd = ((sdf["Close"] / sdf["Close"].cummax()) - 1).min() * 100
                        sharpe = (rets.mean()*252) / (rets.std()*np.sqrt(252)) if rets.std() > 0 else 0
                        beta = info.get("beta")
                        rc = st.columns(5)
                        with rc[0]: st.markdown(metric_card("20d Volatility", f"{v20:.1f}%"), unsafe_allow_html=True)
                        with rc[1]: st.markdown(metric_card("60d Volatility", f"{v60:.1f}%"), unsafe_allow_html=True)
                        with rc[2]: st.markdown(metric_card("Max Drawdown", f"{mdd:.1f}%", "red" if mdd < -30 else None), unsafe_allow_html=True)
                        with rc[3]: st.markdown(metric_card("Sharpe (1Y)", f"{sharpe:.2f}", "green" if sharpe > 0.5 else None), unsafe_allow_html=True)
                        with rc[4]: st.markdown(metric_card("Beta", f"{beta:.2f}" if beta else "—"), unsafe_allow_html=True)

                        # Analyst targets
                        st.markdown('<div class="section-title">Analyst Consensus</div>', unsafe_allow_html=True)
                        ac = st.columns(4)
                        with ac[0]: st.markdown(metric_card("Target Mean", f"${info.get('targetMeanPrice',0):.2f}" if info.get("targetMeanPrice") else "—", "blue"), unsafe_allow_html=True)
                        with ac[1]: st.markdown(metric_card("Target High", f"${info.get('targetHighPrice',0):.2f}" if info.get("targetHighPrice") else "—"), unsafe_allow_html=True)
                        with ac[2]: st.markdown(metric_card("Target Low", f"${info.get('targetLowPrice',0):.2f}" if info.get("targetLowPrice") else "—"), unsafe_allow_html=True)
                        with ac[3]:
                            rec = (info.get("recommendationKey","") or "").upper()
                            rec_color = "green" if rec in ("BUY","STRONG_BUY") else "red" if rec in ("SELL","UNDERPERFORM") else "orange"
                            st.markdown(metric_card("Recommendation", rec or "—", rec_color), unsafe_allow_html=True)

                    # ════════════════════════════════════════════
                    # STATEMENTS TAB (with dates)
                    # ════════════════════════════════════════════
                    with t_statements:
                        def show_statement(title, df_raw, key_words):
                            st.markdown(f'<div class="section-title" style="margin-top:8px">{title}</div>', unsafe_allow_html=True)
                            if df_raw.empty:
                                st.info(f"No {title.lower()} data available")
                                return
                            display = df_raw.iloc[:, :6].copy()
                            display.columns = [c.strftime("%b %d, %Y") if hasattr(c,"strftime") else str(c) for c in display.columns]
                            rows = [idx for idx in display.index if any(k in str(idx).lower() for k in key_words)]
                            show = display.loc[rows] if rows else display.head(15)
                            st.dataframe(show.style.format(lambda x: fmt(x) if isinstance(x,(int,float,np.integer,np.floating)) else x), use_container_width=True)

                        show_statement("Quarterly Income Statement", fin["income"],
                            ["total revenue","cost of revenue","gross profit","operating income","operating expense","net income","ebitda","diluted eps","basic eps","research","interest expense","tax"])
                        show_statement("Quarterly Balance Sheet", fin["balance"],
                            ["total assets","total liab","stockholder","current assets","current liab","cash and cash","total debt","long term debt","retained","goodwill","net tangible"])
                        show_statement("Quarterly Cash Flow", fin["cashflow"],
                            ["operating cash","free cash","capital expend","depreciation","stock based","change in working","repurchase","dividends","issuance"])

                    # ════════════════════════════════════════════
                    # AGENT VERDICTS TAB
                    # ════════════════════════════════════════════
                    with t_agents:
                        if agents:
                            for ag in agents:
                                a_name = ag.get("name","Agent")
                                a_v = ag.get("verdict","WATCH")
                                a_conf = ag.get("confidence",0)
                                a_reason = ag.get("reasoning","")
                                border = "#34c759" if a_v=="BUY" else "#ff3b30" if a_v=="PASS" else "#ff9500"
                                badge_cls = "badge-green" if a_v=="BUY" else "badge-red" if a_v=="PASS" else "badge-orange"
                                st.markdown(f"""<div class="card" style="border-left:4px solid {border};margin-bottom:12px">
                                    <div style="display:flex;justify-content:space-between;align-items:center">
                                        <div><span style="font-weight:600;font-size:16px">{a_name}</span> <span class="badge {badge_cls}" style="margin-left:8px">{a_v}</span></div>
                                        <span class="caption">Confidence: {a_conf}%</span>
                                    </div>
                                    {"<div style='margin-top:12px;font-size:14px;color:#424245;line-height:1.7'>" + a_reason + "</div>" if a_reason else ""}
                                </div>""", unsafe_allow_html=True)
                        else:
                            st.info("Agent verdicts appear after running a full scan with AI enabled.")

                        desc = info.get("longBusinessSummary","")
                        if desc:
                            st.markdown('<div class="section-title">About</div>', unsafe_allow_html=True)
                            st.markdown(f"""<div class="card"><div style="font-size:14px;color:#424245;line-height:1.7">{desc}</div>
                                <div style="margin-top:16px;display:flex;gap:24px;flex-wrap:wrap">
                                    <div><span class="label">Industry</span><br><span class="value-sm">{info.get("industry","—")}</span></div>
                                    <div><span class="label">Employees</span><br><span class="value-sm">{info.get("fullTimeEmployees","—"):,}</span></div>
                                    <div><span class="label">Country</span><br><span class="value-sm">{info.get("country","—")}</span></div>
                                    <div><span class="label">Website</span><br><span class="value-sm">{info.get("website","—")}</span></div>
                                </div>
                            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;padding:60px 0"><div style="font-size:22px;font-weight:600;color:#1d1d1f">No picks yet</div><div class="caption" style="margin-top:8px">Run a scan to get recommendations.</div></div>', unsafe_allow_html=True)


# ═══ TAB 3: STOCK DETAIL ════════════════════════════════════════════
with tab_stock:
    st.markdown('<div class="section-title" style="margin-top:0">Stock Detail</div>', unsafe_allow_html=True)
    symbol = st.text_input("", value="AAPL", max_chars=10, placeholder="Enter symbol (AAPL, BP.L, NVDA)", label_visibility="collapsed").upper().strip()
    if symbol:
        try:
            df = get_stock_data(symbol, "1y", "1d")
            info = get_stock_info(symbol)
            if not df.empty:
                df = calc_indicators(df)
                p = df["Close"].iloc[-1]
                prev = df["Close"].iloc[-2] if len(df)>1 else p
                ch = p - prev; ch_pct = ch/prev*100
                arrow = "+" if ch >= 0 else ""
                ch_color = "var(--green)" if ch >= 0 else "var(--red)"

                st.markdown(f"""<div class="card" style="margin:16px 0 24px">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div style="font-size:22px;font-weight:600">{info.get("shortName",symbol)}</div>
                            <div class="caption">{symbol} &middot; {info.get("sector","")}</div>
                        </div>
                        <div style="text-align:right">
                            <span class="value-xl">${p:.2f}</span>
                            <span style="color:{ch_color};font-weight:600;margin-left:12px">{arrow}{ch:.2f} ({arrow}{ch_pct:.2f}%)</span>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                st.plotly_chart(create_chart(df, symbol), use_container_width=True)

                fc = st.columns(6)
                items = [("P/E", info.get("trailingPE")), ("Forward P/E", info.get("forwardPE")),
                         ("Div Yield", info.get("dividendYield")), ("ROE", info.get("returnOnEquity")),
                         ("Gross Margin", info.get("grossMargins")), ("Rev Growth", info.get("revenueGrowth"))]
                for j, (lbl, v) in enumerate(items):
                    with fc[j]:
                        if lbl in ("P/E","Forward P/E"):
                            val = f"{v:.1f}" if v else "—"
                        else:
                            val = pct(v)
                        st.markdown(f'<div class="card-sm"><div class="label">{lbl}</div><div class="value-lg" style="margin-top:4px">{val}</div></div>', unsafe_allow_html=True)
        except: st.error(f"Could not load {symbol}")


# ═══ TAB 4: RUN SCAN ════════════════════════════════════════════════
with tab_scan:
    st.markdown('<div class="section-title" style="margin-top:0">Run Scan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Scan 1,003 stocks. AI agents find the best long-term investments.</div>', unsafe_allow_html=True)

    sc1, sc2 = st.columns(2)
    with sc1: scan_market = st.selectbox("Market", ["All (LSE + US)", "London Stock Exchange", "US Stocks"])
    with sc2: scan_top = st.selectbox("Top N picks", [5, 10, 15, 20], index=1)
    skip_ai = st.checkbox("Quick scan (skip AI — faster)", value=False)
    st.markdown("")
    if st.button("Start Scan", use_container_width=True):
        mm = {"All (LSE + US)":"all","London Stock Exchange":"lse","US Stocks":"us"}
        with st.status("Scanning...", expanded=True) as status:
            try:
                import subprocess
                cmd = ["python3","pipeline.py","--market",mm[scan_market],"--top",str(scan_top)]
                if skip_ai: cmd.append("--skip-ai")
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, cwd=os.path.dirname(__file__) or ".")
                out_area = st.empty(); lines = []
                for line in iter(proc.stdout.readline, ""):
                    lines.append(line.rstrip()); out_area.code("\n".join(lines[-20:]))
                proc.wait()
                if proc.returncode == 0:
                    status.update(label="Scan complete!", state="complete")
                    st.success("Switch to **Overview** or **Top Picks** to see results.")
                    st.cache_data.clear()
                else: status.update(label="Error", state="error")
            except Exception as e: st.error(str(e))

    rd = os.path.join(os.path.dirname(__file__) or ".","reports")
    if os.path.exists(rd):
        jf = sorted(glob.glob(os.path.join(rd,"*_scan.json")), reverse=True)
        if jf:
            st.markdown("---")
            st.markdown("#### Past Scans")
            for f in jf[:10]:
                st.markdown(f"**{os.path.basename(f).replace('_scan.json','')}**")
