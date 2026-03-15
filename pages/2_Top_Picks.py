"""
AI Trading Crew — Top Picks Page
All AI recommendations. Click any card to see full analysis.
"""

import streamlit as st
import sys, os

st.set_page_config(page_title="Top Picks | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header, get_latest_report, normalize_pick, progress_bar

inject_css()
page_header()

# Hide button chrome — cards ARE the buttons
st.markdown("""<style>
    .picks-grid button {
        background: none !important; border: none !important;
        padding: 0 !important; margin: 0 !important;
        height: auto !important; min-height: 0 !important;
        color: transparent !important;
    }
</style>""", unsafe_allow_html=True)

report = get_latest_report()

if report and report.get("picks"):
    picks = report["picks"]

    st.markdown("""<div style="text-align:center;padding:32px 0 8px">
        <div style="font-size:36px;font-weight:700;color:#1d1d1f;letter-spacing:-1px">Top Picks</div>
        <div style="font-size:16px;color:#86868b;margin-top:6px">AI-selected from {0:,} stocks. Click any to see full analysis.</div>
    </div>""".format(report.get("stocks_scanned", 1003)), unsafe_allow_html=True)

    st.markdown('<div class="picks-grid">', unsafe_allow_html=True)

    for row_start in range(0, len(picks), 3):
        row_picks = picks[row_start:row_start + 3]
        cols = st.columns(3)
        for i, raw_pick in enumerate(row_picks):
            with cols[i]:
                pick = normalize_pick(raw_pick)
                tk = pick["ticker"]
                conf = pick["confidence"]
                tgt = pick.get("target", 0)
                price = pick["price"]
                upside = ((tgt - price) / price * 100) if price > 0 and tgt > 0 else 0
                reason = (pick.get("reason", "") or "")[:140]
                if len(pick.get("reason", "") or "") > 140:
                    reason += "..."

                if conf >= 75: pc = "#2e7d32"
                elif conf >= 55: pc = "#007aff"
                else: pc = "#ff9500"

                # Clickable card
                if st.button(tk, key=f"p_{row_start+i}", use_container_width=True):
                    st.session_state["selected_stock"] = tk
                    st.switch_page("pages/5_Analysis.py")

                st.markdown(f"""<div style="background:white;border:1px solid #f0f0f5;border-radius:16px;padding:22px 24px;
                    margin-top:-44px;margin-bottom:16px;pointer-events:none;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04)">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start">
                        <div>
                            <div style="font-size:12px;color:#86868b;font-weight:500">#{row_start+i+1}</div>
                            <div style="font-size:18px;font-weight:600;color:#1d1d1f;margin:4px 0 2px;letter-spacing:-0.3px">{pick["name"] or tk}</div>
                            <div style="font-size:12px;color:#86868b">{tk}</div>
                        </div>
                        <div style="text-align:right">
                            <div style="font-size:24px;font-weight:700;color:#1d1d1f;letter-spacing:-0.5px">${price:.2f}</div>
                            {f'<div style="font-size:12px;color:#2e7d32;font-weight:500;margin-top:2px">Target ${tgt:.2f} (+{upside:.0f}%)</div>' if tgt > 0 else ''}
                        </div>
                    </div>
                    <div style="margin:14px 0 6px">
                        <div style="background:#f0f0f5;border-radius:4px;height:4px;overflow:hidden">
                            <div style="height:4px;border-radius:4px;width:{conf}%;background:{pc}"></div>
                        </div>
                        <div style="font-size:11px;color:{pc};font-weight:500;margin-top:4px">{conf:.0f}% confidence</div>
                    </div>
                    <div style="font-size:12px;color:#6e6e73;line-height:1.5;margin-top:8px">{reason}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""<div style="text-align:center;padding:80px 0">
        <div style="font-size:22px;font-weight:600;color:#1d1d1f">No picks yet</div>
        <div style="font-size:14px;color:#86868b;margin-top:8px">Run a scan to get recommendations.</div>
    </div>""", unsafe_allow_html=True)
