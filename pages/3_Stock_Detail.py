"""
AI Trading Crew — Stocks
Browse all 1,003 stocks. Select any to open analysis.
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
    <div style="font-size:16px;color:#86868b;margin-top:6px">Browse 1,003 stocks. Select any to open its analysis.</div>
</div>""", unsafe_allow_html=True)

# ─── Filters ─────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
with c1:
    search = st.text_input("Search", placeholder="Search ticker...", label_visibility="collapsed", key="sd_s").strip().upper()
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

# ─── Count + select ──────────────────────────────────────────────────

st.markdown(f'<div style="text-align:center;color:#86868b;font-size:13px;margin-bottom:16px">{len(df):,} results</div>', unsafe_allow_html=True)

# Build labels for selectbox
labels = []
for _, row in df.iterrows():
    tk = row["Ticker"]
    grade = row["_grade"]
    rating = row["_rating"]
    parts = [tk, row["Sector"], row["Market"]]
    if grade >= 0:
        parts.append(f"{grade:.0f}/100 {rating}")
    if tk in picks_map:
        tgt = picks_map[tk]["pick"].get("target", 0)
        parts.append(f"AI Pick" + (f" ${tgt:.0f}" if tgt else ""))
    labels.append(" · ".join(parts))

# Default to session state
default_idx = 0
sel_from_session = st.session_state.get("selected_stock", "")
if sel_from_session:
    for i, row in df.iterrows():
        if row["Ticker"] == sel_from_session:
            default_idx = df.index.get_loc(i) if i in df.index else 0
            break

selected_idx = st.selectbox(
    "Select a stock",
    range(len(labels)),
    index=default_idx,
    format_func=lambda x: labels[x],
    label_visibility="collapsed",
)

selected_tk = df.iloc[selected_idx]["Ticker"]

col_a, col_b = st.columns([1, 5])
with col_a:
    if st.button("Open Analysis"):
        st.session_state["selected_stock"] = selected_tk
        st.switch_page("pages/5_Analysis.py")

st.markdown("")

# ─── Stock list as clean HTML table ──────────────────────────────────

PAGE_SIZE = 50
if "sd_page" not in st.session_state:
    st.session_state["sd_page"] = 0
total_pages = max(1, (len(df) + PAGE_SIZE - 1) // PAGE_SIZE)
page = min(st.session_state["sd_page"], total_pages - 1)
start, end = page * PAGE_SIZE, min((page + 1) * PAGE_SIZE, len(df))
page_df = df.iloc[start:end]

# Build HTML table
rows_html = ""
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

    pick_badge = ""
    if is_pick:
        tgt = picks_map[tk]["pick"].get("target", 0)
        pick_badge = f'<span style="background:#eef4ff;color:#1565c0;padding:2px 8px;border-radius:8px;font-size:10px;font-weight:600">AI Pick{f" ${tgt:.0f}" if tgt else ""}</span>'

    rows_html += f"""<tr style="border-bottom:1px solid #f5f5f7">
        <td style="padding:12px 16px;font-size:14px;font-weight:600;color:#1d1d1f">{tk}</td>
        <td style="padding:12px 16px;font-size:13px;color:#86868b">{row['Market']}</td>
        <td style="padding:12px 16px;font-size:13px;color:#424245">{row['Sector']}</td>
        <td style="padding:12px 16px;font-size:15px;font-weight:600;color:{gc}">{grade_str}</td>
        <td style="padding:12px 16px;font-size:12px;color:{gc};font-weight:500">{rating}</td>
        <td style="padding:12px 16px">{pick_badge}</td>
    </tr>"""

st.markdown(f"""<table style="width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;border:1px solid #f0f0f5;box-shadow:0 1px 3px rgba(0,0,0,0.04)">
    <thead>
        <tr style="border-bottom:2px solid #e8e8ed">
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#86868b;text-transform:uppercase;letter-spacing:0.5px;text-align:left">Ticker</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#86868b;text-transform:uppercase;letter-spacing:0.5px;text-align:left">Market</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#86868b;text-transform:uppercase;letter-spacing:0.5px;text-align:left">Sector</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#86868b;text-transform:uppercase;letter-spacing:0.5px;text-align:left">Grade</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#86868b;text-transform:uppercase;letter-spacing:0.5px;text-align:left">Rating</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#86868b;text-transform:uppercase;letter-spacing:0.5px;text-align:left">Status</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>""", unsafe_allow_html=True)

# Pagination
st.markdown("")
pc1, pc2, pc3 = st.columns([1, 2, 1])
with pc1:
    if page > 0 and st.button("Previous", key="prev"):
        st.session_state["sd_page"] = page - 1
        st.rerun()
with pc2:
    st.markdown(f'<div style="text-align:center;padding:8px;color:#86868b;font-size:13px">Page {page+1} of {total_pages} · {start+1}–{end} of {len(df):,}</div>', unsafe_allow_html=True)
with pc3:
    if end < len(df) and st.button("Next", key="nxt"):
        st.session_state["sd_page"] = page + 1
        st.rerun()
