"""
AI Trading Crew — Stocks
"""

import streamlit as st
import pandas as pd
import sys, os

st.set_page_config(page_title="Stocks | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header, get_latest_report, normalize_pick, grade_from_scan_signals
from tools.universe import get_universe, get_sector

inject_css()
page_header()

@st.cache_data(ttl=600)
def build_universe():
    all_tk = get_universe("all")
    lse = set(get_universe("lse"))
    return pd.DataFrame([{"Ticker": t, "Market": "LSE" if t in lse else "US", "Sector": get_sector(t)} for t in all_tk])

universe = build_universe()

report = get_latest_report()
picks_map, grades_map = {}, {}
if report:
    for rp in report.get("picks", []):
        p = normalize_pick(rp)
        picks_map[p["ticker"]] = {"pick": p, "raw": rp}
    for item in report.get("all_scanned_signals", []):
        sym, sig = item.get("symbol", ""), item.get("scanner_signals", {})
        if sig and sym:
            grades_map[sym] = grade_from_scan_signals(sig)

st.markdown("""<div style="text-align:center;padding:40px 0 16px">
    <div style="font-size:36px;font-weight:700;color:#1d1d1f;letter-spacing:-1px">Stocks</div>
    <div style="font-size:16px;color:#86868b;margin-top:6px">Click any row to open its analysis</div>
</div>""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: search = st.text_input("Search", placeholder="Ticker...", label_visibility="collapsed", key="s").strip().upper()
with c2: mkt = st.selectbox("Market", ["All", "LSE", "US"], key="m", label_visibility="collapsed")
with c3:
    secs = sorted(universe["Sector"].unique().tolist())
    sec = st.selectbox("Sector", ["All"] + secs, key="sec", label_visibility="collapsed")
with c4: sort = st.selectbox("Sort", ["Grade", "A-Z", "Z-A"], key="srt", label_visibility="collapsed")

df = universe.copy()
if mkt != "All": df = df[df["Market"] == mkt]
if sec != "All": df = df[df["Sector"] == sec]
if search: df = df[df["Ticker"].str.contains(search, case=False, na=False)]

df["Grade"] = df["Ticker"].map(lambda t: int(grades_map[t]["final"]) if t in grades_map else None)
df["Rating"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get("rating", ""))
df["Status"] = df["Ticker"].map(lambda t: "AI Pick" if t in picks_map else "")
df["Target"] = df["Ticker"].map(lambda t: f"${picks_map[t]['pick']['target']:.0f}" if t in picks_map and picks_map[t]['pick'].get('target') else "")

if sort == "Grade":
    df = df.sort_values("Grade", ascending=False, na_position="last")
elif sort == "Z-A":
    df = df.sort_values("Ticker", ascending=False)
else:
    df = df.sort_values("Ticker")
df = df.reset_index(drop=True)

display = df[["Ticker", "Market", "Sector", "Grade", "Rating", "Status", "Target"]].copy()

st.markdown(f'<div style="text-align:center;color:#86868b;font-size:13px;margin-bottom:12px">{len(display):,} results</div>', unsafe_allow_html=True)

event = st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    height=600,
    on_select="rerun",
    selection_mode="single-row",
)

if event and event.selection and event.selection.rows:
    row_idx = event.selection.rows[0]
    if row_idx < len(df):
        st.session_state["selected_stock"] = df.iloc[row_idx]["Ticker"]
        st.switch_page("pages/5_Analysis.py")
