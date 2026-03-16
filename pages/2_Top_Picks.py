"""
AI Trading Crew — Top Picks
Clickable HTML table with <a> tag rows. No st.button(), no st.dataframe().
"""

import streamlit as st
import sys, os

st.set_page_config(
    page_title="Top Picks | AI Trading Crew",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header, get_latest_report, normalize_pick

inject_css()
page_header()

report = get_latest_report()

if not report or not report.get("picks"):
    st.markdown("""<div style="text-align:center;padding:80px 0">
        <div style="font-size:22px;font-weight:600;color:#1d1d1f">No picks yet</div>
        <div style="font-size:14px;color:#86868b;margin-top:8px">Run a scan first.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

picks = report["picks"]
total_scanned = report.get("stocks_scanned", 1003)

# ── Title ──
st.markdown(f"""<div style="padding:24px 0 28px">
    <div class="hero-title" style="font-size:36px">Top Picks</div>
    <div class="hero-sub" style="font-size:15px">AI-selected from {total_scanned:,} stocks &middot; Click any row</div>
</div>""", unsafe_allow_html=True)

# ── Clickable HTML table ──
# Header style shared across columns
HS = ("padding:12px 16px;font-size:11px;font-weight:600;color:#aeaeb2;"
      "text-transform:uppercase;letter-spacing:0.8px;text-align:left")

# Grid template for rows
GRID = "grid-template-columns: 40px 1fr 100px 100px 100px 90px 100px"

# Build header
header = f"""<div style="display:grid;{GRID};border-bottom:1px solid #e8e8ed;padding:0 4px">
    <div style="{HS}">#</div>
    <div style="{HS}">Company</div>
    <div style="{HS}">Ticker</div>
    <div style="{HS}">Price</div>
    <div style="{HS}">Target</div>
    <div style="{HS}">Upside</div>
    <div style="{HS}">Confidence</div>
</div>"""

# Build rows
rows = ""
CS = "padding:14px 16px;font-size:14px;display:flex;align-items:center"

for i, rp in enumerate(picks):
    p = normalize_pick(rp)
    tk = p["ticker"]
    name = p["name"] or tk
    price = p["price"]
    tgt = p.get("target", 0)
    upside = ((tgt - price) / price * 100) if price > 0 and tgt > 0 else 0
    conf = p["confidence"]

    if conf >= 75:
        conf_color = "#2e7d32"
    elif conf >= 55:
        conf_color = "#007aff"
    else:
        conf_color = "#ff9500"

    upside_str = f"+{upside:.1f}%" if upside > 0 else "—"
    upside_color = "#2e7d32" if upside > 0 else "#86868b"
    tgt_str = f"${tgt:.2f}" if tgt > 0 else "—"

    rows += f"""<a href="/Analysis?ticker={tk}" target="_self"
        style="display:grid;{GRID};text-decoration:none;color:inherit;
               border-bottom:1px solid #f0f0f5;padding:0 4px;
               transition:background 0.15s"
        onmouseover="this.style.background='#f8f9fa'"
        onmouseout="this.style.background='transparent'">
        <div style="{CS};font-size:13px;color:#86868b;font-weight:500">{i + 1}</div>
        <div style="{CS};font-weight:600;color:#1d1d1f">{name}</div>
        <div style="{CS};font-size:13px;color:#86868b">{tk}</div>
        <div style="{CS};font-weight:600;color:#1d1d1f">${price:.2f}</div>
        <div style="{CS};font-size:13px;color:#2e7d32">{tgt_str}</div>
        <div style="{CS};font-size:13px;font-weight:500;color:{upside_color}">{upside_str}</div>
        <div style="{CS};font-weight:600;color:{conf_color}">{conf:.0f}%</div>
    </a>"""

# Render
st.markdown(f"""
<div style="background:white;border:1px solid #f0f0f5;border-radius:16px;overflow:hidden;
            box-shadow:0 1px 3px rgba(0,0,0,0.04)">
    {header}
    {rows}
</div>
""", unsafe_allow_html=True)
