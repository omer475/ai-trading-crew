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

st.markdown("""<div style="text-align:center;padding:40px 0 20px">
    <div style="font-size:36px;font-weight:700;color:#1d1d1f;letter-spacing:-1px">Stocks</div>
    <div style="font-size:15px;color:#86868b;margin-top:6px">Select a stock to open its analysis</div>
</div>""", unsafe_allow_html=True)

# ─── Filters ─────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
with c1: search = st.text_input("Search", placeholder="Ticker...", label_visibility="collapsed", key="s").strip().upper()
with c2: mkt = st.selectbox("Market", ["All", "LSE", "US"], key="m", label_visibility="collapsed")
with c3:
    secs = sorted(universe["Sector"].unique().tolist())
    sec = st.selectbox("Sector", ["All"] + secs, key="sec", label_visibility="collapsed")
with c4: sort = st.selectbox("Sort", ["Grade", "A–Z", "Z–A"], key="srt", label_visibility="collapsed")

# ─── Filter + Sort ───────────────────────────────────────────────────

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
elif sort == "Z–A":
    df = df.sort_values("Ticker", ascending=False)
else:
    df = df.sort_values("Ticker")
df = df.reset_index(drop=True)

st.markdown(f'<div style="text-align:center;color:#aeaeb2;font-size:12px;margin-bottom:16px">{len(df):,} stocks</div>', unsafe_allow_html=True)

# ─── Stock selector (auto-navigates on change) ───────────────────────

labels = []
for _, row in df.iterrows():
    tk = row["Ticker"]
    parts = [tk]
    parts.append(row["Market"])
    parts.append(row["Sector"])
    g = row["Grade"]
    if pd.notna(g): parts.append(f"{int(g)}/100")
    r = row["Rating"]
    if r: parts.append(r)
    if row["Status"]: parts.append(row["Status"])
    if row["Target"]: parts.append(row["Target"])
    labels.append("  ·  ".join(parts))

prev_selected = st.session_state.get("_stocks_prev_selection", None)

selected_idx = st.selectbox(
    "Select stock",
    range(len(labels)),
    format_func=lambda x: labels[x],
    label_visibility="collapsed",
    key="stock_selector",
)

selected_tk = df.iloc[selected_idx]["Ticker"]

# Auto-navigate when selection changes
if prev_selected is not None and selected_tk != prev_selected:
    st.session_state["selected_stock"] = selected_tk
    st.session_state["_stocks_prev_selection"] = selected_tk
    st.switch_page("pages/5_Analysis.py")

st.session_state["_stocks_prev_selection"] = selected_tk

# ─── Clickable table (same visual style, but rows navigate) ──────────

# CSS to make st.dataframe match the HTML table look
st.markdown("""<style>
    /* Hide row selection checkbox column */
    [data-testid="stDataFrame"] div[data-testid="column-header-0"],
    [data-testid="stDataFrame"] div[role="gridcell"]:first-child {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
    }
    /* Clean border */
    [data-testid="stDataFrame"] > div { border: none !important; }
    /* Row cursor */
    [data-testid="stDataFrame"] div[role="row"] { cursor: pointer !important; }
</style>""", unsafe_allow_html=True)

# Build display df
display = df[["Ticker", "Market", "Sector", "Grade", "Rating", "Status", "Target"]].copy()
display["Grade"] = display["Grade"].apply(lambda g: f"{int(g)}" if pd.notna(g) else "")

event = st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    height=620,
    on_select="rerun",
    selection_mode="single-row",
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
        "Market": st.column_config.TextColumn("Market", width="small"),
        "Sector": st.column_config.TextColumn("Sector", width="medium"),
        "Grade": st.column_config.TextColumn("Grade", width="small"),
        "Rating": st.column_config.TextColumn("Rating", width="medium"),
        "Status": st.column_config.TextColumn("Status", width="small"),
        "Target": st.column_config.TextColumn("Target", width="small"),
    },
)

# Navigate on row click
if event and event.selection and event.selection.rows:
    idx = event.selection.rows[0]
    if idx < len(df):
        st.session_state["selected_stock"] = df.iloc[idx]["Ticker"]
        st.switch_page("pages/5_Analysis.py")
