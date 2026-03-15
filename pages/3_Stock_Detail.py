"""
AI Trading Crew — Stock Detail Page
Browse ALL 1,003 stocks. Click any stock name to see full analysis.
"""

import streamlit as st
import pandas as pd
import sys, os

st.set_page_config(page_title="Stock Detail | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    inject_css, page_header, get_latest_report, normalize_pick,
    render_stock_detail, grade_from_scan_signals,
)
from tools.universe import get_universe, get_sector

inject_css()
page_header()

# ─── Build universe ──────────────────────────────────────────────────

@st.cache_data(ttl=600)
def build_universe():
    all_tk = get_universe("all")
    lse = set(get_universe("lse"))
    return pd.DataFrame([{"Ticker": t, "Market": "LSE" if t in lse else "US", "Sector": get_sector(t)} for t in all_tk])

universe = build_universe()

# ─── Load scan data ──────────────────────────────────────────────────

report = get_latest_report()
picks_map = {}
grades_map = {}
if report:
    for rp in report.get("picks", []):
        p = normalize_pick(rp)
        picks_map[p["ticker"]] = {"pick": p, "raw": rp}
    for item in report.get("all_scanned_signals", []):
        sym = item.get("symbol", "")
        sig = item.get("scanner_signals", {})
        if sig and sym:
            grades_map[sym] = grade_from_scan_signals(sig)
    for rp in report.get("picks", []):
        sig = rp.get("scanner_signals", {})
        sym = rp.get("symbol", "")
        if sig and sym and sym not in grades_map:
            grades_map[sym] = grade_from_scan_signals(sig)

# ─── Header ──────────────────────────────────────────────────────────

st.markdown('<div class="section-title" style="margin-top:0">Stock Detail</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-sub">Browse {len(universe):,} stocks. Click any stock name to open its analysis.</div>', unsafe_allow_html=True)

# ─── Filters ─────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1:
    search = st.text_input("Search", placeholder="Search ticker...", label_visibility="collapsed", key="sd_s").strip().upper()
with c2:
    mkt = st.selectbox("Market", ["All", "LSE", "US"], key="sd_m")
with c3:
    secs = sorted(universe["Sector"].unique().tolist())
    sec = st.selectbox("Sector", ["All Sectors"] + secs, key="sd_sec")
with c4:
    sort = st.selectbox("Sort", ["Grade (Best)", "Grade (Worst)", "Alphabetical", "Fundamental", "Financial Health", "Growth", "Technical"], key="sd_sort")

# ─── Filter + Sort ───────────────────────────────────────────────────

df = universe.copy()
if mkt != "All": df = df[df["Market"] == mkt]
if sec != "All Sectors": df = df[df["Sector"] == sec]
if search: df = df[df["Ticker"].str.contains(search, case=False, na=False)]

# Add grade data
df["_grade"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get("final", -1))
df["_rating"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get("rating", ""))

# Sort
sort_map = {
    "Grade (Best)": ("_grade", False),
    "Grade (Worst)": ("_grade", True),
    "Fundamental": ("fundamental", False),
    "Financial Health": ("financial_health", False),
    "Growth": ("growth", False),
    "Technical": ("technical", False),
}
if sort in sort_map:
    key, asc = sort_map[sort]
    if key != "_grade":
        df["_sort_key"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get(key, -1))
    else:
        df["_sort_key"] = df["_grade"]
    df["_has"] = (df["_sort_key"] >= 0).astype(int)
    df = df.sort_values(["_has", "_sort_key"], ascending=[False, asc])
    if "_sort_key" in df.columns: df = df.drop(columns=["_sort_key", "_has"])
else:
    df = df.sort_values("Ticker")

df = df.reset_index(drop=True)

# ─── Stats ───────────────────────────────────────────────────────────

n_graded = sum(1 for g in df["_grade"] if g >= 0)
n_picks = sum(1 for t in df["Ticker"] if t in picks_map)

st.markdown(f"""<div style="display:flex;gap:12px;margin:8px 0 20px;flex-wrap:wrap">
    <div class="card-sm"><div class="label">Results</div><div class="value-md">{len(df):,}</div></div>
    <div class="card-sm"><div class="label">Graded</div><div class="value-md">{n_graded}</div></div>
    {"<div class='card-sm card-blue'><div class='label'>AI Picks</div><div class='value-md'>" + str(n_picks) + "</div></div>" if n_picks else ""}
</div>""", unsafe_allow_html=True)

# ─── Stock Table (clickable stock names) ─────────────────────────────

# Show stocks as clickable buttons in a clean table layout
PAGE_SIZE = 30
if "sd_page" not in st.session_state:
    st.session_state["sd_page"] = 0

total_pages = max(1, (len(df) + PAGE_SIZE - 1) // PAGE_SIZE)
page = st.session_state["sd_page"]
start = page * PAGE_SIZE
end = min(start + PAGE_SIZE, len(df))
page_df = df.iloc[start:end]

# Table header
st.markdown("""<div style="display:grid;grid-template-columns:120px 60px 140px 60px 120px 80px;gap:8px;padding:8px 12px;border-bottom:2px solid #1d1d1f;margin-bottom:4px">
    <div style="font-size:11px;font-weight:700;color:#1d1d1f;text-transform:uppercase;letter-spacing:0.5px">Stock</div>
    <div style="font-size:11px;font-weight:700;color:#1d1d1f;text-transform:uppercase;letter-spacing:0.5px">Market</div>
    <div style="font-size:11px;font-weight:700;color:#1d1d1f;text-transform:uppercase;letter-spacing:0.5px">Sector</div>
    <div style="font-size:11px;font-weight:700;color:#1d1d1f;text-transform:uppercase;letter-spacing:0.5px">Grade</div>
    <div style="font-size:11px;font-weight:700;color:#1d1d1f;text-transform:uppercase;letter-spacing:0.5px">Rating</div>
    <div style="font-size:11px;font-weight:700;color:#1d1d1f;text-transform:uppercase;letter-spacing:0.5px">Status</div>
</div>""", unsafe_allow_html=True)

# Table rows with clickable stock names
for _, row in page_df.iterrows():
    tk = row["Ticker"]
    grade = row["_grade"]
    rating = row["_rating"]
    is_pick = tk in picks_map

    grade_str = f"{grade:.0f}" if grade >= 0 else "—"
    if grade >= 75: grade_color = "#2e7d32"
    elif grade >= 55: grade_color = "#007aff"
    elif grade >= 45: grade_color = "#ff9500"
    elif grade >= 0: grade_color = "#ff3b30"
    else: grade_color = "#aeaeb2"

    status = ""
    if is_pick:
        p = picks_map[tk]["pick"]
        tgt = p.get("target", 0)
        status = f'<span style="background:#eef4ff;color:#1565c0;padding:2px 8px;border-radius:8px;font-size:11px;font-weight:600">AI Pick</span>'
        if tgt: status += f' <span style="color:#86868b;font-size:11px">${tgt:.0f}</span>'

    cols = st.columns([2, 1, 2.5, 1, 2, 1.5])
    with cols[0]:
        if st.button(tk, key=f"btn_{tk}", use_container_width=True):
            st.session_state["sd_selected"] = tk
    with cols[1]:
        st.markdown(f'<div style="padding:8px 0;font-size:13px;color:#86868b">{row["Market"]}</div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div style="padding:8px 0;font-size:13px;color:#424245">{row["Sector"]}</div>', unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f'<div style="padding:8px 0;font-size:14px;font-weight:600;color:{grade_color}">{grade_str}</div>', unsafe_allow_html=True)
    with cols[4]:
        st.markdown(f'<div style="padding:8px 0;font-size:13px;color:{grade_color}">{rating}</div>', unsafe_allow_html=True)
    with cols[5]:
        st.markdown(f'<div style="padding:6px 0">{status}</div>', unsafe_allow_html=True)

# Pagination
st.markdown("")
pc1, pc2, pc3 = st.columns([1, 2, 1])
with pc1:
    if page > 0:
        if st.button("Previous", key="sd_prev"):
            st.session_state["sd_page"] = page - 1
            st.rerun()
with pc2:
    st.markdown(f'<div style="text-align:center;padding:8px;color:#86868b;font-size:13px">Page {page+1} of {total_pages} &middot; Showing {start+1}–{end} of {len(df):,}</div>', unsafe_allow_html=True)
with pc3:
    if end < len(df):
        if st.button("Next", key="sd_next"):
            st.session_state["sd_page"] = page + 1
            st.rerun()

# ─── Selected stock from navigation ──────────────────────────────────

selected = st.session_state.get("sd_selected") or st.session_state.get("selected_stock")

# Clear navigation flag
if "selected_stock_source" in st.session_state:
    selected = st.session_state.get("selected_stock", "")
    del st.session_state["selected_stock_source"]

# ─── Render analysis ─────────────────────────────────────────────────

if selected:
    st.session_state["selected_stock"] = selected
    st.markdown("---")

    scan_data = picks_map.get(selected)
    if scan_data:
        st.markdown(f"""<div class="card-sm card-blue" style="margin-bottom:16px">
            <div class="label">AI PICK</div>
            <div class="value-sm" style="margin-top:4px">Selected by AI scan with full analysis.</div>
        </div>""", unsafe_allow_html=True)
        render_stock_detail(selected, pick=scan_data["pick"], raw=scan_data["raw"], key_prefix=f"sd_{selected}")
    else:
        render_stock_detail(selected, pick=None, raw=None, key_prefix=f"sd_{selected}")
