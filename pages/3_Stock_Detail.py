"""
AI Trading Crew — Stocks
Browse all 1,003 stocks. Click any to open analysis.
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

# ─── Data ────────────────────────────────────────────────────────────

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

# ─── Header ──────────────────────────────────────────────────────────

st.markdown("""<div style="text-align:center;padding:40px 0 16px">
    <div style="font-size:36px;font-weight:700;color:#1d1d1f;letter-spacing:-1px">Stocks</div>
    <div style="font-size:16px;color:#86868b;margin-top:6px">1,003 stocks across LSE and US markets</div>
</div>""", unsafe_allow_html=True)

# ─── Filters ─────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
with c1:
    search = st.text_input("Search", placeholder="Ticker...", label_visibility="collapsed", key="sd_s").strip().upper()
with c2:
    mkt = st.selectbox("Market", ["All", "LSE", "US"], key="sd_m", label_visibility="collapsed")
with c3:
    secs = sorted(universe["Sector"].unique().tolist())
    sec = st.selectbox("Sector", ["All"] + secs, key="sd_sec", label_visibility="collapsed")
with c4:
    sort = st.selectbox("Sort", ["Grade", "A-Z", "Z-A"], key="sd_sort", label_visibility="collapsed")

# ─── Filter + Sort ───────────────────────────────────────────────────

df = universe.copy()
if mkt != "All": df = df[df["Market"] == mkt]
if sec != "All": df = df[df["Sector"] == sec]
if search: df = df[df["Ticker"].str.contains(search, case=False, na=False)]

df["_grade"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get("final", -1))
df["_rating"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get("rating", ""))

if sort == "Grade":
    df["_has"] = (df["_grade"] >= 0).astype(int)
    df = df.sort_values(["_has", "_grade"], ascending=[False, False]).drop(columns=["_has"])
elif sort == "Z-A":
    df = df.sort_values("Ticker", ascending=False)
else:
    df = df.sort_values("Ticker")
df = df.reset_index(drop=True)

# ─── Count ───────────────────────────────────────────────────────────

st.markdown(f'<div style="text-align:center;color:#86868b;font-size:13px;margin-bottom:24px">{len(df):,} results</div>', unsafe_allow_html=True)

# ─── Pagination ──────────────────────────────────────────────────────

PAGE_SIZE = 30
if "sd_page" not in st.session_state:
    st.session_state["sd_page"] = 0
total_pages = max(1, (len(df) + PAGE_SIZE - 1) // PAGE_SIZE)
page = min(st.session_state["sd_page"], total_pages - 1)
start, end = page * PAGE_SIZE, min((page + 1) * PAGE_SIZE, len(df))
page_df = df.iloc[start:end]

# ─── Stock List ──────────────────────────────────────────────────────

# Each stock is a row: click the ticker to open analysis
for _, row in page_df.iterrows():
    tk = row["Ticker"]
    grade = row["_grade"]
    rating = row["_rating"]
    is_pick = tk in picks_map

    grade_str = f"{grade:.0f}" if grade >= 0 else "—"
    if grade >= 75: gc = "#2e7d32"
    elif grade >= 55: gc = "#007aff"
    elif grade >= 45: gc = "#ff9500"
    elif grade >= 0: gc = "#ff3b30"
    else: gc = "#d1d1d6"

    pick_info = ""
    if is_pick:
        tgt = picks_map[tk]["pick"].get("target", 0)
        pick_info = f'<span style="background:#eef4ff;color:#1565c0;padding:2px 8px;border-radius:8px;font-size:10px;font-weight:600;margin-left:8px">AI Pick{f" ${tgt:.0f}" if tgt else ""}</span>'

    # Row layout
    rc1, rc2, rc3, rc4, rc5 = st.columns([1.5, 0.8, 2, 0.8, 2])

    with rc1:
        # Ticker as a clickable link-style button
        if st.button(tk, key=f"t_{tk}"):
            st.session_state["selected_stock"] = tk
            st.switch_page("pages/5_Analysis.py")

    with rc2:
        st.markdown(f'<div style="padding:6px 0;font-size:13px;color:#86868b">{row["Market"]}</div>', unsafe_allow_html=True)

    with rc3:
        st.markdown(f'<div style="padding:6px 0;font-size:13px;color:#424245">{row["Sector"]}</div>', unsafe_allow_html=True)

    with rc4:
        st.markdown(f'<div style="padding:6px 0;font-size:15px;font-weight:600;color:{gc}">{grade_str}</div>', unsafe_allow_html=True)

    with rc5:
        st.markdown(f'<div style="padding:4px 0;font-size:12px;color:{gc};font-weight:500">{rating}{pick_info}</div>', unsafe_allow_html=True)

    # Subtle divider line
    st.markdown('<div style="border-bottom:1px solid #f5f5f7;margin:0"></div>', unsafe_allow_html=True)

# ─── Pagination controls ─────────────────────────────────────────────

st.markdown("")
pc1, pc2, pc3 = st.columns([1, 2, 1])
with pc1:
    if page > 0 and st.button("Previous", key="prev"):
        st.session_state["sd_page"] = page - 1
        st.rerun()
with pc2:
    st.markdown(f'<div style="text-align:center;padding:8px;color:#86868b;font-size:13px">{start+1}–{end} of {len(df):,}</div>', unsafe_allow_html=True)
with pc3:
    if end < len(df) and st.button("Next", key="nxt"):
        st.session_state["sd_page"] = page + 1
        st.rerun()
