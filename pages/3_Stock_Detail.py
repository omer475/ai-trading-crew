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
all_tickers = set(universe["Ticker"].tolist())

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
    <div style="font-size:15px;color:#86868b;margin-top:6px">Type a ticker in the search box to open its analysis</div>
</div>""", unsafe_allow_html=True)

# ─── Search box (auto-navigates on exact match) ─────────────────────

search = st.text_input(
    "Search",
    placeholder="Type a ticker (e.g. AAPL, GPOR, BP.L) and press Enter...",
    label_visibility="collapsed",
    key="stock_search",
).strip().upper()

# Auto-navigate if exact ticker match
if search and search in all_tickers:
    st.session_state["selected_stock"] = search
    st.switch_page("pages/5_Analysis.py")

# ─── Filters ─────────────────────────────────────────────────────────

c1, c2, c3 = st.columns(3)
with c1: mkt = st.selectbox("Market", ["All", "LSE", "US"], key="m", label_visibility="collapsed")
with c2:
    secs = sorted(universe["Sector"].unique().tolist())
    sec = st.selectbox("Sector", ["All"] + secs, key="sec", label_visibility="collapsed")
with c3: sort = st.selectbox("Sort", ["Grade", "A–Z", "Z–A"], key="srt", label_visibility="collapsed")

# ─── Filter + Sort ───────────────────────────────────────────────────

df = universe.copy()
if mkt != "All": df = df[df["Market"] == mkt]
if sec != "All": df = df[df["Sector"] == sec]
if search and search not in all_tickers:
    df = df[df["Ticker"].str.contains(search, case=False, na=False)]

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

# ─── HTML Table ──────────────────────────────────────────────────────

PAGE_SIZE = 50
if "pg" not in st.session_state: st.session_state["pg"] = 0
total_pages = max(1, (len(df) + PAGE_SIZE - 1) // PAGE_SIZE)
page = min(st.session_state["pg"], total_pages - 1)
start, end = page * PAGE_SIZE, min((page + 1) * PAGE_SIZE, len(df))
page_df = df.iloc[start:end]

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

# ─── Pagination ──────────────────────────────────────────────────────

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
