"""
AI Trading Crew — Stock Analysis Page
Dedicated full-page analysis for a single stock.
Opens when you click a stock from any page.
"""

import streamlit as st
import sys, os

st.set_page_config(page_title="Analysis | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    inject_css, page_header, get_latest_report, normalize_pick,
    render_stock_detail,
)

inject_css()
page_header()

# ─── Get selected stock ──────────────────────────────────────────────

selected = st.session_state.get("selected_stock", "")

if not selected:
    st.markdown("""<div style="text-align:center;padding:80px 0">
        <div style="font-size:28px;font-weight:600;color:#1d1d1f">No stock selected</div>
        <div style="font-size:15px;color:#86868b;margin-top:8px">Go to the Stocks page and click on a stock to view its analysis.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ─── Load scan data ──────────────────────────────────────────────────

report = get_latest_report()
picks_map = {}
if report:
    for rp in report.get("picks", []):
        p = normalize_pick(rp)
        picks_map[p["ticker"]] = {"pick": p, "raw": rp}

# ─── Back button ─────────────────────────────────────────────────────

if st.button("Back to Stocks"):
    st.switch_page("pages/3_Stock_Detail.py")

# ─── Render full analysis ────────────────────────────────────────────

scan_data = picks_map.get(selected)

if scan_data:
    st.markdown(f"""<div style="background:#eef4ff;border-radius:12px;padding:14px 20px;margin-bottom:20px;display:flex;align-items:center;gap:12px">
        <div style="font-size:13px;font-weight:600;color:#1565c0">AI PICK</div>
        <div style="font-size:13px;color:#424245">This stock was selected by the AI scan with full analysis and agent verdicts.</div>
    </div>""", unsafe_allow_html=True)
    render_stock_detail(selected, pick=scan_data["pick"], raw=scan_data["raw"], key_prefix=f"analysis_{selected}")
else:
    render_stock_detail(selected, pick=None, raw=None, key_prefix=f"analysis_{selected}")
