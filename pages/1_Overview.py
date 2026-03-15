"""
AI Trading Crew — Overview Page
Market regime, top 3 picks as cards, click to navigate to stock detail.
"""

import streamlit as st
import sys, os

st.set_page_config(page_title="Overview | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    inject_css, page_header, get_latest_report, normalize_pick,
    regime_badge, metric_card, progress_bar, render_stock_detail,
)

inject_css()
page_header()

report = get_latest_report()

if report:
    picks = report.get("picks", [])

    # ── Market Regime & Stats ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="card"><div class="label">Market Regime</div><div style="margin-top:10px">{regime_badge(report.get("regime"))}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="card"><div class="label">Last Scan</div><div class="value-lg" style="margin-top:4px">{report.get("scan_date","\u2014")}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card"><div class="label">Stocks Scanned</div><div class="value-xl" style="margin-top:4px">{report.get("stocks_scanned",0):,}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="card"><div class="label">Top Picks</div><div class="value-xl" style="margin-top:4px">{len(picks)}</div></div>', unsafe_allow_html=True)

    # ── Regime Details ──
    regime_data = report.get("regime")
    if isinstance(regime_data, dict):
        st.markdown('<div class="section-title">Market Regime Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Current market environment assessment.</div>', unsafe_allow_html=True)

        r_cols = st.columns(4)
        with r_cols[0]:
            score = regime_data.get("composite_score", 0)
            st.markdown(metric_card("Composite Score", f"{score:+.3f}", "green" if score > 0.2 else "red" if score < -0.2 else None), unsafe_allow_html=True)
        with r_cols[1]:
            conf = regime_data.get("confidence", 0)
            if conf <= 1:
                conf *= 100
            st.markdown(metric_card("Confidence", f"{conf:.0f}%"), unsafe_allow_html=True)
        with r_cols[2]:
            strat = regime_data.get("strategy", {})
            st.markdown(metric_card("Strategy", strat.get("strategy", "\u2014").replace("_", " ").title()), unsafe_allow_html=True)
        with r_cols[3]:
            st.markdown(metric_card("Position Size", f"{strat.get('position_size_multiplier', 1.0):.2f}x"), unsafe_allow_html=True)

        desc = strat.get("description", "")
        if desc:
            st.markdown(f"""<div class="reasoning-box" style="margin-top:16px">
                <div class="label" style="color:#1565c0;margin-bottom:8px">STRATEGY RECOMMENDATION</div>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

    if picks:
        st.markdown('<div class="section-title">Top Recommendations</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">AI-selected from 1,003 stocks. Click any stock to see full analysis.</div>', unsafe_allow_html=True)

        # Stock selector cards — top 3
        cols = st.columns(min(len(picks), 3))
        for i, raw_pick in enumerate(picks[:3]):
            with cols[i]:
                pick = normalize_pick(raw_pick)
                tk = pick["ticker"]
                conf = pick["confidence"]
                p_color = "green" if conf >= 75 else "orange" if conf >= 60 else "red"
                st.markdown(f"""<div class="card">
                    <div class="caption">#{i+1} Pick</div>
                    <div class="value-lg" style="margin:6px 0 2px">{pick["name"] or tk}</div>
                    <div class="caption">{tk} &middot; {pick.get("sector","")}</div>
                    <div class="value-xl" style="margin:16px 0 8px">${pick["price"]:.2f}</div>
                    {progress_bar(conf, 100, p_color)}
                    <div class="caption" style="margin-top:4px">{conf:.0f}% confidence</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"View Full Analysis", key=f"overview_btn_{i}", use_container_width=True):
                    st.session_state["selected_stock"] = tk
                    st.session_state["selected_stock_source"] = "overview"
                    st.switch_page("pages/3_Stock_Detail.py")

else:
    st.markdown("""<div style="text-align:center;padding:100px 0">
        <div class="hero-title">AI Trading Crew</div>
        <div class="hero-sub" style="max-width:460px;margin:12px auto 0">
            50 AI agents scan 1,003 stocks across LSE and US markets to find the best long-term investments.
        </div>
        <div style="margin-top:48px;font-size:14px;color:#86868b">
            Go to <b>Run Scan</b> to start your first analysis.
        </div>
    </div>""", unsafe_allow_html=True)
