"""
AI Trading Crew — Top Picks
"""

import streamlit as st
import pandas as pd
import sys, os

st.set_page_config(page_title="Top Picks | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header, get_latest_report, normalize_pick
inject_css()
page_header()

report = get_latest_report()

if not report or not report.get("picks"):
    st.markdown('<div style="text-align:center;padding:80px 0"><div style="font-size:22px;font-weight:600;color:#1d1d1f">No picks yet</div><div style="font-size:14px;color:#86868b;margin-top:8px">Run a scan first.</div></div>', unsafe_allow_html=True)
    st.stop()

picks = report["picks"]

st.markdown(f"""<div style="text-align:center;padding:32px 0 24px">
    <div style="font-size:36px;font-weight:700;color:#1d1d1f;letter-spacing:-1px">Top Picks</div>
    <div style="font-size:16px;color:#86868b;margin-top:6px">AI-selected from {report.get("stocks_scanned",1003):,} stocks · Click any row to open analysis</div>
</div>""", unsafe_allow_html=True)

rows = []
for i, rp in enumerate(picks):
    p = normalize_pick(rp)
    tgt = p.get("target", 0)
    price = p["price"]
    upside = ((tgt - price) / price * 100) if price > 0 and tgt > 0 else 0
    rows.append({
        "Rank": i + 1,
        "Company": p["name"] or p["ticker"],
        "Ticker": p["ticker"],
        "Price": f"${price:.2f}",
        "Target": f"${tgt:.2f}" if tgt else "",
        "Upside": f"+{upside:.0f}%" if upside > 0 else "",
        "Confidence": f"{p['confidence']:.0f}%",
    })

table = pd.DataFrame(rows)

event = st.dataframe(
    table,
    use_container_width=True,
    hide_index=True,
    height=min(len(table) * 40 + 50, 500),
    on_select="rerun",
    selection_mode="single-row",
)

if event and event.selection and event.selection.rows:
    row_idx = event.selection.rows[0]
    if row_idx < len(picks):
        p = normalize_pick(picks[row_idx])
        st.session_state["selected_stock"] = p["ticker"]
        st.switch_page("pages/5_Analysis.py")
