"""
AI Trading Crew — Stock Detail Page
Browse ALL 1,003 stocks in a clean table. Click any stock to see full analysis.
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

# ─── Build universe ─────────────────────────────────────────────────

@st.cache_data(ttl=600)
def build_universe_df():
    all_tickers = get_universe("all")
    lse_set = set(get_universe("lse"))
    rows = []
    for tk in all_tickers:
        rows.append({"Ticker": tk, "Market": "LSE" if tk in lse_set else "US", "Sector": get_sector(tk)})
    return pd.DataFrame(rows)

universe_df = build_universe_df()

# ─── Scan data ───────────────────────────────────────────────────────

report = get_latest_report()
scan_picks_map = {}
scan_grades_map = {}
if report and report.get("picks"):
    for rp in report["picks"]:
        np_ = normalize_pick(rp)
        scan_picks_map[np_["ticker"]] = {"pick": np_, "raw": rp}
        signals = rp.get("scanner_signals", {})
        if signals:
            scan_grades_map[np_["ticker"]] = grade_from_scan_signals(signals)

# ─── Header ──────────────────────────────────────────────────────────

st.markdown('<div class="section-title" style="margin-top:0">Stock Detail</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-sub">Browse {len(universe_df):,} stocks. Search, filter, sort, then click any stock.</div>', unsafe_allow_html=True)

# ─── Search + Filters row ────────────────────────────────────────────

s1, s2, s3, s4 = st.columns([2, 1, 1, 1])

with s1:
    search = st.text_input("Search", placeholder="Search by ticker or name...", label_visibility="collapsed", key="sd_search").strip().upper()

with s2:
    market_f = st.selectbox("Market", ["All", "LSE", "US"], key="sd_market")

with s3:
    sectors = sorted(universe_df["Sector"].unique().tolist())
    sector_f = st.selectbox("Sector", ["All Sectors"] + sectors, key="sd_sector")

with s4:
    sort_options = ["Alphabetical", "Final Grade (Best)", "Final Grade (Worst)", "Fundamental", "Financial Health", "Growth", "Technical"]
    sort_by = st.selectbox("Sort by", sort_options, key="sd_sort")

# ─── Apply filters ───────────────────────────────────────────────────

df = universe_df.copy()
if market_f != "All":
    df = df[df["Market"] == market_f]
if sector_f != "All Sectors":
    df = df[df["Sector"] == sector_f]
if search:
    df = df[df["Ticker"].str.contains(search, case=False, na=False)]

# ─── Add grades + sort ───────────────────────────────────────────────

grade_key_map = {
    "Final Grade (Best)": ("final", False),
    "Final Grade (Worst)": ("final", True),
    "Fundamental": ("fundamental", False),
    "Financial Health": ("financial_health", False),
    "Growth": ("growth", False),
    "Technical": ("technical", False),
}

if sort_by in grade_key_map:
    key, asc = grade_key_map[sort_by]
    df["Grade"] = df["Ticker"].map(lambda t: scan_grades_map.get(t, {}).get(key, None))
    df["Rating"] = df["Ticker"].map(lambda t: scan_grades_map.get(t, {}).get("rating", ""))
    # Graded first, then ungraded
    df["_has"] = df["Grade"].notna().astype(int)
    df = df.sort_values(["_has", "Grade"], ascending=[False, asc]).drop(columns=["_has"])
else:
    df["Grade"] = df["Ticker"].map(lambda t: scan_grades_map.get(t, {}).get("final", None))
    df["Rating"] = df["Ticker"].map(lambda t: scan_grades_map.get(t, {}).get("rating", ""))
    df = df.sort_values("Ticker")

# Add scan pick info
df["AI Pick"] = df["Ticker"].map(lambda t: "Yes" if t in scan_picks_map else "")
df["Target"] = df["Ticker"].map(lambda t: f"${scan_picks_map[t]['pick'].get('target',0):.2f}" if t in scan_picks_map and scan_picks_map[t]['pick'].get('target') else "")
df["Confidence"] = df["Ticker"].map(lambda t: f"{scan_picks_map[t]['pick'].get('confidence',0):.0f}%" if t in scan_picks_map else "")

# Format grade column
df["Grade"] = df["Grade"].map(lambda g: f"{g:.0f}/100" if pd.notna(g) else "—")

# ─── Stats bar ───────────────────────────────────────────────────────

n_picks = sum(1 for t in df["Ticker"] if t in scan_picks_map)
st.markdown(f"""<div style="display:flex;gap:12px;margin:12px 0 20px;flex-wrap:wrap">
    <div class="card-sm"><div class="label">Showing</div><div class="value-md">{len(df):,}</div></div>
    <div class="card-sm"><div class="label">LSE</div><div class="value-md">{len(df[df['Market']=='LSE']):,}</div></div>
    <div class="card-sm"><div class="label">US</div><div class="value-md">{len(df[df['Market']=='US']):,}</div></div>
    <div class="card-sm"><div class="label">Sectors</div><div class="value-md">{df['Sector'].nunique()}</div></div>
    {"<div class='card-sm card-blue'><div class='label'>AI Picks</div><div class='value-md'>" + str(n_picks) + "</div></div>" if n_picks else ""}
</div>""", unsafe_allow_html=True)

# ─── Stock Table ─────────────────────────────────────────────────────

display_df = df[["Ticker", "Market", "Sector", "Grade", "Rating", "AI Pick", "Target", "Confidence"]].reset_index(drop=True)

# Show the table
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=min(len(display_df) * 35 + 40, 600),
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
        "Market": st.column_config.TextColumn("Market", width="small"),
        "Sector": st.column_config.TextColumn("Sector", width="medium"),
        "Grade": st.column_config.TextColumn("Grade", width="small"),
        "Rating": st.column_config.TextColumn("Rating", width="medium"),
        "AI Pick": st.column_config.TextColumn("AI", width="small"),
        "Target": st.column_config.TextColumn("Target", width="small"),
        "Confidence": st.column_config.TextColumn("Conf", width="small"),
    },
)

# ─── Stock Selector (click to open) ──────────────────────────────────

st.markdown("")

# Build ticker list for the selectbox
ticker_list = display_df["Ticker"].tolist()
if not ticker_list:
    st.info("No stocks match your filters.")
    st.stop()

# Default to session state or first ticker
default_tk = st.session_state.get("selected_stock", "")
default_idx = 0
if default_tk in ticker_list:
    default_idx = ticker_list.index(default_tk)

# Create labels with grade info
labels = []
for tk in ticker_list:
    grade = scan_grades_map.get(tk, {}).get("final")
    rating = scan_grades_map.get(tk, {}).get("rating", "")
    pick_info = ""
    if tk in scan_picks_map:
        p = scan_picks_map[tk]["pick"]
        tgt = p.get("target", 0)
        pick_info = f" | Target: ${tgt:.2f}" if tgt else ""
    if grade:
        labels.append(f"{tk} — {rating} ({grade:.0f}/100){pick_info}")
    else:
        labels.append(tk)

col_select, col_btn = st.columns([3, 1])
with col_select:
    selected_idx = st.selectbox(
        "Select a stock to view full analysis",
        range(len(ticker_list)),
        index=default_idx,
        format_func=lambda i: labels[i],
        key="sd_picker",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    open_clicked = st.button("Open Analysis", use_container_width=True, type="primary")

selected_ticker = ticker_list[selected_idx]
st.session_state["selected_stock"] = selected_ticker

# ─── Render analysis when button clicked or stock selected ───────────

# Auto-open if navigated from another page
auto_open = st.session_state.pop("selected_stock_source", None) is not None

if open_clicked or auto_open or st.session_state.get("sd_detail_open") == selected_ticker:
    st.session_state["sd_detail_open"] = selected_ticker
    st.markdown("---")

    scan_data = scan_picks_map.get(selected_ticker)
    if scan_data:
        st.markdown(f"""<div class="card-sm card-blue" style="margin-bottom:16px">
            <div class="label">AI PICK</div>
            <div class="value-sm" style="margin-top:4px">This stock was selected in the latest scan with full AI analysis.</div>
        </div>""", unsafe_allow_html=True)
        render_stock_detail(selected_ticker, pick=scan_data["pick"], raw=scan_data["raw"], key_prefix=f"sd_{selected_ticker}")
    else:
        render_stock_detail(selected_ticker, pick=None, raw=None, key_prefix=f"sd_{selected_ticker}")
