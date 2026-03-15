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

st.markdown(f"""<div style="text-align:center;padding:32px 0 20px">
    <div style="font-size:36px;font-weight:700;color:#1d1d1f;letter-spacing:-1px">Top Picks</div>
    <div style="font-size:15px;color:#86868b;margin-top:6px">AI-selected from {report.get("stocks_scanned",1003):,} stocks · Select any to open analysis</div>
</div>""", unsafe_allow_html=True)

# Selector — auto-navigates on change
labels = []
for i, rp in enumerate(picks):
    p = normalize_pick(rp)
    tgt = p.get("target", 0)
    price = p["price"]
    upside = ((tgt - price) / price * 100) if price > 0 and tgt > 0 else 0
    parts = [f"#{i+1}", p["name"] or p["ticker"], p["ticker"], f"${price:.2f}"]
    if tgt: parts.append(f"Target ${tgt:.2f} (+{upside:.0f}%)")
    parts.append(f"{p['confidence']:.0f}%")
    labels.append("  ·  ".join(parts))

prev = st.session_state.get("_picks_prev", None)

selected_idx = st.selectbox(
    "Select",
    range(len(labels)),
    format_func=lambda x: labels[x],
    label_visibility="collapsed",
    key="picks_sel",
)

selected_tk = normalize_pick(picks[selected_idx])["ticker"]

if prev is not None and selected_tk != prev:
    st.session_state["selected_stock"] = selected_tk
    st.session_state["_picks_prev"] = selected_tk
    st.switch_page("pages/5_Analysis.py")

st.session_state["_picks_prev"] = selected_tk

# Visual table
rows_html = ""
for i, rp in enumerate(picks):
    p = normalize_pick(rp)
    tgt = p.get("target", 0)
    price = p["price"]
    upside = ((tgt - price) / price * 100) if price > 0 and tgt > 0 else 0
    conf = p["confidence"]

    if conf >= 75: cc = "#2e7d32"
    elif conf >= 55: cc = "#007aff"
    else: cc = "#ff9500"

    rows_html += f"""<tr>
        <td style="padding:12px 16px;font-size:13px;color:#86868b;font-weight:500">{i+1}</td>
        <td style="padding:12px 16px;font-size:14px;font-weight:600;color:#1d1d1f">{p["name"] or p["ticker"]}</td>
        <td style="padding:12px 16px;font-size:13px;color:#86868b">{p["ticker"]}</td>
        <td style="padding:12px 16px;font-size:15px;font-weight:600;color:#1d1d1f">${price:.2f}</td>
        <td style="padding:12px 16px;font-size:13px;color:#2e7d32">{f"${tgt:.2f}" if tgt else ""}</td>
        <td style="padding:12px 16px;font-size:13px;color:#2e7d32;font-weight:500">{f"+{upside:.0f}%" if upside > 0 else ""}</td>
        <td style="padding:12px 16px;font-size:14px;font-weight:600;color:{cc}">{conf:.0f}%</td>
    </tr>"""

st.markdown(f"""<table style="width:100%;border-collapse:collapse;margin-top:16px">
    <thead>
        <tr style="border-bottom:1px solid #e8e8ed">
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">#</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Company</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Ticker</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Price</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Target</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Upside</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Confidence</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>""", unsafe_allow_html=True)
