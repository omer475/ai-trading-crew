"""
AI Trading Crew — Stock Analysis Page
Dedicated full-page analysis for a single stock.
"""

import streamlit as st
import sys, os

st.set_page_config(page_title="Analysis | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header, get_latest_report, normalize_pick, render_stock_detail

inject_css()

# Minimal custom CSS for this page
st.markdown("""<style>
    .back-link { display:inline-flex; align-items:center; gap:6px; font-size:14px; font-weight:500;
        color:#86868b; text-decoration:none; padding:8px 0; cursor:pointer; transition:color 0.2s; }
    .back-link:hover { color:#1d1d1f; }
</style>""", unsafe_allow_html=True)

# Read from query params first (from table link), then session state
qp = st.query_params.get("ticker", "")
if qp:
    st.session_state["selected_stock"] = qp.upper()
selected = st.session_state.get("selected_stock", "")

if not selected:
    st.markdown("""<div style="text-align:center;padding:100px 0">
        <div style="font-size:24px;font-weight:600;color:#1d1d1f">No stock selected</div>
        <div style="font-size:14px;color:#86868b;margin-top:8px">Go to Stocks and click on any stock.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Minimal back navigation ──
col_back, _ = st.columns([1, 5])
with col_back:
    if st.button("< Stocks", type="secondary"):
        st.switch_page("pages/3_Stock_Detail.py")

# ── Load scan data ──
report = get_latest_report()
picks_map = {}
if report:
    for rp in report.get("picks", []):
        p = normalize_pick(rp)
        picks_map[p["ticker"]] = {"pick": p, "raw": rp}

# ── AI Pick indicator ──
scan_data = picks_map.get(selected)
if scan_data:
    st.markdown("""<div style="background:#eef4ff;border-radius:10px;padding:10px 16px;margin-bottom:16px;
        display:inline-flex;align-items:center;gap:8px">
        <span style="font-size:12px;font-weight:600;color:#1565c0">AI PICK</span>
        <span style="font-size:12px;color:#424245">Selected by AI scan</span>
    </div>""", unsafe_allow_html=True)
    render_stock_detail(selected, pick=scan_data["pick"], raw=scan_data["raw"], key_prefix=f"a_{selected}")
else:
    render_stock_detail(selected, pick=None, raw=None, key_prefix=f"a_{selected}")
