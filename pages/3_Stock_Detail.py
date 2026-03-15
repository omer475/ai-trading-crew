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

# ─── Visual table (read-only, for browsing) ──────────────────────────

PAGE_SIZE = 50
if "pg" not in st.session_state: st.session_state["pg"] = 0
total_pages = max(1, (len(df) + PAGE_SIZE - 1) // PAGE_SIZE)
page = min(st.session_state["pg"], total_pages - 1)
start, end = page * PAGE_SIZE, min((page + 1) * PAGE_SIZE, len(df))
page_df = df.iloc[start:end]

# Build clean HTML table
rows_html = ""
for _, row in page_df.iterrows():
    tk = row["Ticker"]
    g = row["Grade"]
    grade_str = f"{int(g)}" if pd.notna(g) else ""
    rating = row["Rating"]
    status = row["Status"]
    target = row["Target"]

    if pd.notna(g) and g >= 75: gc = "#2e7d32"
    elif pd.notna(g) and g >= 55: gc = "#007aff"
    elif pd.notna(g) and g >= 45: gc = "#ff9500"
    elif pd.notna(g) and g >= 0: gc = "#ff3b30"
    else: gc = "#d1d1d6"

    status_html = f'<span style="background:#eef4ff;color:#1565c0;padding:2px 8px;border-radius:8px;font-size:10px;font-weight:600">{status}</span>' if status else ""
    target_html = f'<span style="color:#86868b;font-size:12px;margin-left:6px">{target}</span>' if target else ""

    rows_html += f"""<tr>
        <td style="padding:11px 16px;font-size:14px;font-weight:600;color:#1d1d1f">{tk}</td>
        <td style="padding:11px 16px;font-size:13px;color:#86868b">{row['Market']}</td>
        <td style="padding:11px 16px;font-size:13px;color:#424245">{row['Sector']}</td>
        <td style="padding:11px 16px;font-size:15px;font-weight:700;color:{gc}">{grade_str}</td>
        <td style="padding:11px 16px;font-size:12px;color:{gc};font-weight:500">{rating}</td>
        <td style="padding:11px 16px">{status_html}{target_html}</td>
    </tr>"""

st.markdown(f"""<table style="width:100%;border-collapse:collapse;margin-top:8px">
    <thead>
        <tr style="border-bottom:1px solid #e8e8ed">
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Ticker</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Market</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Sector</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Grade</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Rating</th>
            <th style="padding:10px 16px;font-size:11px;font-weight:600;color:#aeaeb2;text-transform:uppercase;letter-spacing:0.8px;text-align:left">Status</th>
        </tr>
    </thead>
    <tbody style="border-top:none">{rows_html}</tbody>
</table>""", unsafe_allow_html=True)

# Pagination
if total_pages > 1:
    st.markdown("")
    pc1, pc2, pc3 = st.columns([1, 2, 1])
    with pc1:
        if page > 0 and st.button("← Previous"):
            st.session_state["pg"] = page - 1
            st.rerun()
    with pc2:
        st.markdown(f'<div style="text-align:center;padding:8px;color:#aeaeb2;font-size:12px">Page {page+1} of {total_pages}</div>', unsafe_allow_html=True)
    with pc3:
        if end < len(df) and st.button("Next →"):
            st.session_state["pg"] = page + 1
            st.rerun()
