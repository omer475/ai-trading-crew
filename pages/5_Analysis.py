"""
AI Trading Crew — Stock Analysis Page
Dedicated full-page analysis for a single stock.
Reads ticker from query_params first, then session_state.
"""

import streamlit as st
import sys, os

st.set_page_config(
    page_title="Analysis | AI Trading Crew",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header, get_latest_report, normalize_pick, render_stock_detail

inject_css()
page_header()

# ── Read ticker: query params first, then session state ──
qp = st.query_params.get("ticker", "")
if qp:
    st.session_state["selected_stock"] = qp.upper()
selected = st.session_state.get("selected_stock", "")

if not selected:
    st.markdown("""<div style="text-align:center;padding:100px 0">
        <div style="font-size:24px;font-weight:600;color:#1d1d1f">No stock selected</div>
        <div style="font-size:14px;color:#86868b;margin-top:8px">Go to Stocks and click on any row.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Back link ──
st.page_link("pages/3_Stocks.py", label="< Back to Stocks")

# ── Load scan data ──
report = get_latest_report()
picks_map = {}
raw_signals_map = {}

if report:
    # Build pick lookup
    for rp in report.get("picks", []):
        p = normalize_pick(rp)
        picks_map[p["ticker"]] = {"pick": p, "raw": rp}

    # Build signals lookup (for stocks not in picks but in scan)
    for sig in report.get("all_scanned_signals", []):
        sym = sig.get("symbol", "")
        raw_signals_map[sym] = sig

# ── AI Pick indicator ──
scan_data = picks_map.get(selected)

if scan_data:
    st.markdown("""<div style="background:#eef4ff;border-radius:10px;padding:10px 16px;margin-bottom:16px;
        display:inline-flex;align-items:center;gap:8px">
        <span style="font-size:12px;font-weight:600;color:#1565c0">AI PICK</span>
        <span style="font-size:12px;color:#424245">Selected by AI scan</span>
    </div>""", unsafe_allow_html=True)
    render_stock_detail(
        selected,
        pick=scan_data["pick"],
        raw=scan_data["raw"],
        key_prefix=f"a_{selected}",
    )
else:
    # Not a pick — check if it's in the scanned signals for extra context
    raw = raw_signals_map.get(selected)
    render_stock_detail(
        selected,
        pick=None,
        raw=raw,
        key_prefix=f"a_{selected}",
    )
