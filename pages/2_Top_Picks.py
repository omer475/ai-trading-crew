"""
AI Trading Crew — Top Picks
"""

import streamlit as st
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
    <div style="font-size:16px;color:#86868b;margin-top:6px">AI-selected from {report.get("stocks_scanned",1003):,} stocks</div>
</div>""", unsafe_allow_html=True)

# Render all picks as clean cards
for i, raw_pick in enumerate(picks):
    pick = normalize_pick(raw_pick)
    tk = pick["ticker"]
    conf = pick["confidence"]
    tgt = pick.get("target", 0)
    price = pick["price"]
    upside = ((tgt - price) / price * 100) if price > 0 and tgt > 0 else 0
    reason = (pick.get("reason", "") or "")[:200]
    if len(pick.get("reason", "") or "") > 200: reason += "..."

    if conf >= 75: bar_color = "#34c759"
    elif conf >= 55: bar_color = "#007aff"
    else: bar_color = "#ff9500"

    st.markdown(f"""<div style="background:white;border:1px solid #f0f0f5;border-radius:16px;padding:24px 28px;margin-bottom:12px;
        box-shadow:0 1px 3px rgba(0,0,0,0.04)">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:24px;flex-wrap:wrap">
            <div style="flex:1;min-width:200px">
                <div style="font-size:12px;color:#86868b;font-weight:500">#{i+1}</div>
                <div style="font-size:20px;font-weight:600;color:#1d1d1f;margin:4px 0;letter-spacing:-0.3px">{pick["name"] or tk}</div>
                <div style="font-size:13px;color:#86868b">{tk}</div>
            </div>
            <div style="text-align:right">
                <div style="font-size:28px;font-weight:700;color:#1d1d1f;letter-spacing:-0.5px">${price:.2f}</div>
                {f'<div style="font-size:13px;color:#2e7d32;font-weight:500">Target ${tgt:.2f} (+{upside:.0f}%)</div>' if tgt > 0 else ''}
            </div>
        </div>
        <div style="margin:16px 0 8px">
            <div style="background:#f5f5f7;border-radius:3px;height:3px;overflow:hidden">
                <div style="height:3px;border-radius:3px;width:{min(conf,100)}%;background:{bar_color}"></div>
            </div>
            <div style="font-size:11px;color:{bar_color};font-weight:500;margin-top:4px">{conf:.0f}% confidence</div>
        </div>
        {f'<div style="font-size:13px;color:#6e6e73;line-height:1.6">{reason}</div>' if reason else ''}
    </div>""", unsafe_allow_html=True)

# Selection dropdown at the bottom
st.markdown('<div style="margin-top:32px"></div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:15px;font-weight:600;color:#1d1d1f;margin-bottom:8px">Open full analysis</div>', unsafe_allow_html=True)

options = [f"{normalize_pick(p)['ticker']} — {normalize_pick(p)['name'] or normalize_pick(p)['ticker']}" for p in picks]
selected_idx = st.selectbox("Pick", range(len(picks)), format_func=lambda x: options[x], label_visibility="collapsed")

if st.button("Open", use_container_width=False):
    st.session_state["selected_stock"] = normalize_pick(picks[selected_idx])["ticker"]
    st.switch_page("pages/5_Analysis.py")
