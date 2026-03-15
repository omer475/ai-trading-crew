"""
AI Trading Crew — Stock Detail Page
Browse ALL 1,003 stocks in a table. Click any row to see full analysis.
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
    # Load top picks
    for rp in report.get("picks", []):
        p = normalize_pick(rp)
        picks_map[p["ticker"]] = {"pick": p, "raw": rp}
        sig = rp.get("scanner_signals", {})
        if sig:
            grades_map[p["ticker"]] = grade_from_scan_signals(sig)
    # Load ALL candidates
    for rp in report.get("all_candidates", []):
        sig = rp.get("scanner_signals", {})
        sym = rp.get("symbol") or sig.get("symbol", "")
        if sig and sym and sym not in grades_map:
            grades_map[sym] = grade_from_scan_signals(sig)
    # Load ALL scanned stocks (every stock gets a grade)
    for item in report.get("all_scanned_signals", []):
        sym = item.get("symbol", "")
        sig = item.get("scanner_signals", {})
        if sig and sym and sym not in grades_map:
            grades_map[sym] = grade_from_scan_signals(sig)

# ─── Header ──────────────────────────────────────────────────────────

st.markdown('<div class="section-title" style="margin-top:0">Stock Detail</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-sub">Browse {len(universe):,} stocks. Search, filter, sort — click any row to open analysis.</div>', unsafe_allow_html=True)

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
    sort = st.selectbox("Sort", ["Alphabetical", "Grade (Best)", "Grade (Worst)", "Fundamental", "Financial Health", "Growth", "Technical"], key="sd_sort")

# ─── Filter + Sort ───────────────────────────────────────────────────

df = universe.copy()
if mkt != "All": df = df[df["Market"] == mkt]
if sec != "All Sectors": df = df[df["Sector"] == sec]
if search: df = df[df["Ticker"].str.contains(search, case=False, na=False)]

# Add grade columns
df["Grade"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get("final"))
df["Rating"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get("rating", ""))
df["Pick"] = df["Ticker"].map(lambda t: "AI Pick" if t in picks_map else "")
df["Target"] = df["Ticker"].map(lambda t: f"${picks_map[t]['pick'].get('target',0):.2f}" if t in picks_map and picks_map[t]['pick'].get('target') else "")

# Sort
sort_map = {"Grade (Best)": ("final", False), "Grade (Worst)": ("final", True), "Fundamental": ("fundamental", False), "Financial Health": ("financial_health", False), "Growth": ("growth", False), "Technical": ("technical", False)}
if sort in sort_map:
    key, asc = sort_map[sort]
    df["_s"] = df["Ticker"].map(lambda t: grades_map.get(t, {}).get(key, -1))
    df["_h"] = (df["_s"] >= 0).astype(int)
    df = df.sort_values(["_h", "_s"], ascending=[False, asc]).drop(columns=["_s", "_h"])
else:
    df = df.sort_values("Ticker")

df = df.reset_index(drop=True)

# Format grade for display
df["Grade_Display"] = df["Grade"].map(lambda g: f"{g:.0f}" if pd.notna(g) else "—")

# ─── Stats ───────────────────────────────────────────────────────────

n_picks = sum(1 for t in df["Ticker"] if t in picks_map)
st.markdown(f"""<div style="display:flex;gap:12px;margin:8px 0 16px;flex-wrap:wrap">
    <div class="card-sm"><div class="label">Results</div><div class="value-md">{len(df):,}</div></div>
    <div class="card-sm"><div class="label">LSE</div><div class="value-md">{len(df[df['Market']=='LSE']):,}</div></div>
    <div class="card-sm"><div class="label">US</div><div class="value-md">{len(df[df['Market']=='US']):,}</div></div>
    {"<div class='card-sm card-blue'><div class='label'>AI Picks</div><div class='value-md'>" + str(n_picks) + "</div></div>" if n_picks else ""}
</div>""", unsafe_allow_html=True)

# ─── Table with row selection ────────────────────────────────────────

table_df = df[["Ticker", "Market", "Sector", "Grade_Display", "Rating", "Pick", "Target"]].copy()
table_df.columns = ["Ticker", "Market", "Sector", "Grade", "Rating", "Status", "Target"]

event = st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    height=min(len(table_df) * 35 + 40, 500),
    on_select="rerun",
    selection_mode="single-row",
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
        "Market": st.column_config.TextColumn("Market", width="small"),
        "Sector": st.column_config.TextColumn("Sector", width="medium"),
        "Grade": st.column_config.TextColumn("Grade", width="small"),
        "Rating": st.column_config.TextColumn("Rating", width="small"),
        "Status": st.column_config.TextColumn("Status", width="small"),
        "Target": st.column_config.TextColumn("Target", width="small"),
    },
)

# ─── Get selected stock ──────────────────────────────────────────────

selected_ticker = None

# From table click
if event and event.selection and event.selection.rows:
    row_idx = event.selection.rows[0]
    if row_idx < len(df):
        selected_ticker = df.iloc[row_idx]["Ticker"]

# From session state (navigated from another page)
if not selected_ticker and st.session_state.get("selected_stock_source"):
    selected_ticker = st.session_state.get("selected_stock", "")
    st.session_state.pop("selected_stock_source", None)

# ─── Render analysis ─────────────────────────────────────────────────

if selected_ticker:
    st.session_state["selected_stock"] = selected_ticker
    st.markdown("---")

    scan_data = picks_map.get(selected_ticker)
    if scan_data:
        st.markdown(f"""<div class="card-sm card-blue" style="margin-bottom:16px">
            <div class="label">AI PICK</div>
            <div class="value-sm" style="margin-top:4px">Selected in the latest scan with AI analysis and agent verdicts.</div>
        </div>""", unsafe_allow_html=True)
        render_stock_detail(selected_ticker, pick=scan_data["pick"], raw=scan_data["raw"], key_prefix=f"sd_{selected_ticker}")
    else:
        render_stock_detail(selected_ticker, pick=None, raw=None, key_prefix=f"sd_{selected_ticker}")
else:
    st.markdown("""<div style="text-align:center;padding:40px 0;color:#86868b">
        <div style="font-size:16px;font-weight:500">Click any row in the table above to see its full analysis</div>
        <div style="font-size:13px;margin-top:8px">Stocks with grades and ratings were analyzed in the latest scan</div>
    </div>""", unsafe_allow_html=True)
