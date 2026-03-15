"""
AI Trading Crew — Dashboard (Multi-page Entry Point)
Apple-inspired design. Navigate using the sidebar pages.
"""

import streamlit as st

st.set_page_config(
    page_title="AI Trading Crew",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from shared import inject_css, page_header, get_latest_report, regime_badge

inject_css()
page_header()

# ─── Landing page / redirect ────────────────────────────────────────

report = get_latest_report()

if report:
    picks = report.get("picks", [])

    st.markdown("""<div style="text-align:center;padding:60px 0 30px">
        <div class="hero-title">AI Trading Crew</div>
        <div class="hero-sub" style="max-width:520px;margin:12px auto 0">
            50 AI agents scan 1,003 stocks across LSE and US markets to find the best long-term investments.
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="card"><div class="label">Market Regime</div><div style="margin-top:10px">{regime_badge(report.get("regime"))}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="card"><div class="label">Last Scan</div><div class="value-lg" style="margin-top:4px">{report.get("scan_date","\u2014")}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card"><div class="label">Stocks Scanned</div><div class="value-xl" style="margin-top:4px">{report.get("stocks_scanned",0):,}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="card"><div class="label">Top Picks</div><div class="value-xl" style="margin-top:4px">{len(picks)}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""<div style="text-align:center;padding:20px 0 40px">
        <div class="caption">Use the sidebar to navigate between pages</div>
        <div style="margin-top:24px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
            <div class="card-sm" style="min-width:180px;text-align:center"><div class="label">Overview</div><div class="value-sm" style="margin-top:4px">Market regime + top 3 picks</div></div>
            <div class="card-sm" style="min-width:180px;text-align:center"><div class="label">Top Picks</div><div class="value-sm" style="margin-top:4px">All AI recommendations</div></div>
            <div class="card-sm" style="min-width:180px;text-align:center"><div class="label">Stock Detail</div><div class="value-sm" style="margin-top:4px">Browse & analyze all 1,003 stocks</div></div>
            <div class="card-sm" style="min-width:180px;text-align:center"><div class="label">Run Scan</div><div class="value-sm" style="margin-top:4px">Start a new analysis</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

else:
    st.markdown("""<div style="text-align:center;padding:100px 0">
        <div class="hero-title">AI Trading Crew</div>
        <div class="hero-sub" style="max-width:460px;margin:12px auto 0">
            50 AI agents scan 1,003 stocks across LSE and US markets to find the best long-term investments.
        </div>
        <div style="margin-top:48px;font-size:14px;color:#86868b">
            Go to <b>Run Scan</b> in the sidebar to start your first analysis.
        </div>
    </div>""", unsafe_allow_html=True)
