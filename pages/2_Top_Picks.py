"""
AI Trading Crew — Top Picks Page
All picks from the latest scan. Click any to navigate to Stock Detail.
"""

import streamlit as st
import sys, os

st.set_page_config(page_title="Top Picks | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    inject_css, page_header, get_latest_report, normalize_pick,
    metric_card, progress_bar, render_stock_detail,
)

inject_css()
page_header()

report = get_latest_report()

if report and report.get("picks"):
    picks = report["picks"]
    st.markdown('<div class="section-title" style="margin-top:0">All Recommendations</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{len(picks)} stocks from {report.get("stocks_scanned",1003):,} scanned on {report.get("scan_date","\u2014")}</div>', unsafe_allow_html=True)

    # ── Pick Grid ──
    # Show all picks as cards in a grid, 3 per row
    for row_start in range(0, len(picks), 3):
        row_picks = picks[row_start:row_start + 3]
        cols = st.columns(3)
        for i, raw_pick in enumerate(row_picks):
            with cols[i]:
                pick = normalize_pick(raw_pick)
                tk = pick["ticker"]
                conf = pick["confidence"]
                p_color = "green" if conf >= 75 else "orange" if conf >= 60 else "red"
                reason_preview = (pick.get("reason", "") or "")[:120]
                if len(pick.get("reason", "") or "") > 120:
                    reason_preview += "..."

                st.markdown(f"""<div class="card" style="margin-bottom:4px">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start">
                        <div>
                            <div class="caption">#{row_start + i + 1}</div>
                            <div class="value-lg" style="margin:4px 0 2px">{pick["name"] or tk}</div>
                            <div class="caption">{tk} &middot; {pick.get("sector","")}</div>
                        </div>
                        <div style="text-align:right">
                            <div class="value-xl">${pick["price"]:.2f}</div>
                        </div>
                    </div>
                    <div style="margin:12px 0 8px">
                        {progress_bar(conf, 100, p_color)}
                        <div class="caption" style="margin-top:4px">{conf:.0f}% confidence</div>
                    </div>
                    <div style="font-size:13px;color:#6e6e73;line-height:1.5;margin-top:8px">{reason_preview}</div>
                </div>""", unsafe_allow_html=True)

                if st.button(f"View Analysis", key=f"picks_btn_{row_start + i}", use_container_width=True):
                    st.session_state["selected_stock"] = tk
                    st.session_state["selected_stock_source"] = "picks"
                    st.switch_page("pages/3_Stock_Detail.py")

    st.markdown("---")

    # ── Also allow dropdown selection for quick access ──
    st.markdown('<div class="section-title">Quick Select</div>', unsafe_allow_html=True)
    pick_options = []
    for i, rp in enumerate(picks):
        np_ = normalize_pick(rp)
        pick_options.append(f"#{i+1} \u2014 {np_['name'] or np_['ticker']} ({np_['ticker']}) \u2014 {np_['confidence']:.0f}%")

    selected_idx = st.selectbox(
        "Select a pick",
        range(len(picks)),
        format_func=lambda x: pick_options[x],
        label_visibility="collapsed",
    )

    raw = picks[selected_idx]
    pick = normalize_pick(raw)
    render_stock_detail(pick["ticker"], pick=pick, raw=raw, key_prefix=f"toppicks_{selected_idx}")

else:
    st.markdown("""<div style="text-align:center;padding:60px 0">
        <div style="font-size:22px;font-weight:600;color:#1d1d1f">No picks yet</div>
        <div class="caption" style="margin-top:8px">Run a scan to get recommendations.</div>
    </div>""", unsafe_allow_html=True)
