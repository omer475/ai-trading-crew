"""
AI Trading Crew — Dashboard (Landing Page)
"""

import streamlit as st
import os, sys

st.set_page_config(
    page_title="AI Trading Crew",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import inject_css, page_header, get_latest_report, regime_badge

inject_css()
page_header()

# ── Hero ──
st.markdown("""
<div style="text-align:center;padding:80px 20px 60px">
    <div class="hero-title">AI Trading Crew</div>
    <div class="hero-sub" style="max-width:540px;margin:12px auto 0">
        Multi-agent investment research covering 1,003 stocks across LSE and US markets.
        Scanned every two weeks.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Scan stats (if report exists) ──
report = get_latest_report()

if report:
    scan_date = report.get("scan_date", "Unknown")
    picks = report.get("picks", [])
    signals = report.get("all_scanned_signals", [])
    regime = report.get("regime", {})
    regime_val = regime.get("regime", "Unknown") if isinstance(regime, dict) else regime

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;max-width:800px;margin:0 auto 48px">
        <div class="card-sm" style="text-align:center">
            <div class="label">Last Scan</div>
            <div class="value-lg">{scan_date}</div>
        </div>
        <div class="card-sm" style="text-align:center">
            <div class="label">Stocks Scanned</div>
            <div class="value-lg">{len(signals):,}</div>
        </div>
        <div class="card-sm" style="text-align:center">
            <div class="label">Top Picks</div>
            <div class="value-lg">{len(picks)}</div>
        </div>
        <div class="card-sm" style="text-align:center">
            <div class="label">Market Regime</div>
            <div style="margin-top:6px">{regime_badge(regime_val)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 48px">
        <div class="caption">No scan report found. Run a scan from the Run Scan page.</div>
    </div>
    """, unsafe_allow_html=True)

# ── Navigation hint ──
st.markdown("""
<div style="text-align:center;padding:0 0 60px">
    <div style="font-size:14px;color:#86868b;margin-bottom:16px">Use the sidebar to navigate</div>
    <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap">
        <div class="card-sm" style="min-width:160px;text-align:center">
            <div class="value-sm">Overview</div>
            <div class="caption">Market regime & top picks</div>
        </div>
        <div class="card-sm" style="min-width:160px;text-align:center">
            <div class="value-sm">Top Picks</div>
            <div class="caption">AI-selected investments</div>
        </div>
        <div class="card-sm" style="min-width:160px;text-align:center">
            <div class="value-sm">Stocks</div>
            <div class="caption">Browse all scanned stocks</div>
        </div>
        <div class="card-sm" style="min-width:160px;text-align:center">
            <div class="value-sm">Run Scan</div>
            <div class="caption">Execute a new scan</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
