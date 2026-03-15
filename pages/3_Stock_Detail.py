"""
AI Trading Crew — Stock Detail Page
Browse ALL 1,003 stocks with filters, sorting, and full analysis.
"""

import streamlit as st
import pandas as pd
import sys, os

st.set_page_config(page_title="Stock Detail | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    inject_css, page_header, get_latest_report, normalize_pick,
    render_stock_detail, calculate_recommendation, get_stock_info,
    _grade_stock_cached, grade_stock,
)
from tools.universe import get_universe, SECTOR_MAP, get_sector

inject_css()
page_header()

# ─── Build the full universe list ────────────────────────────────────

@st.cache_data(ttl=600)
def build_universe_df():
    """Build a DataFrame of all stocks in the universe with basic metadata."""
    all_tickers = get_universe("all")
    lse_tickers = set(get_universe("lse"))

    rows = []
    for tk in all_tickers:
        market = "LSE" if tk in lse_tickers else "US"
        sector = get_sector(tk)
        rows.append({
            "Ticker": tk,
            "Market": market,
            "Sector": sector,
        })
    return pd.DataFrame(rows)


universe_df = build_universe_df()

# ─── Check for scan data to enrich ───────────────────────────────────

report = get_latest_report()
scan_picks_map = {}
if report and report.get("picks"):
    for rp in report["picks"]:
        np_ = normalize_pick(rp)
        scan_picks_map[np_["ticker"]] = {"pick": np_, "raw": rp}

# ─── Header ──────────────────────────────────────────────────────────

st.markdown('<div class="section-title" style="margin-top:0">Stock Detail</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-sub">Browse and analyze all {len(universe_df):,} stocks. Filter by market, sector, or search by ticker.</div>', unsafe_allow_html=True)

# ─── Filters ─────────────────────────────────────────────────────────

with st.container():
    f1, f2, f3 = st.columns([1, 1, 2])

    with f1:
        market_filter = st.selectbox(
            "Market",
            ["All", "LSE", "US"],
            index=0,
            key="stock_detail_market",
        )

    with f2:
        all_sectors = sorted(universe_df["Sector"].unique().tolist())
        sector_filter = st.selectbox(
            "Sector",
            ["All Sectors"] + all_sectors,
            index=0,
            key="stock_detail_sector",
        )

    with f3:
        search_query = st.text_input(
            "Search",
            value=st.session_state.get("selected_stock", ""),
            placeholder="Type a ticker (e.g. AAPL, BP.L, NVDA) or search...",
            key="stock_detail_search",
        ).strip().upper()

# ─── Apply filters ───────────────────────────────────────────────────

filtered = universe_df.copy()

if market_filter != "All":
    filtered = filtered[filtered["Market"] == market_filter]

if sector_filter != "All Sectors":
    filtered = filtered[filtered["Sector"] == sector_filter]

if search_query:
    filtered = filtered[filtered["Ticker"].str.contains(search_query, case=False, na=False)]

# ─── Sort ────────────────────────────────────────────────────────────

GRADE_SORT_OPTIONS = [
    "Final Grade (Best First)",
    "Final Grade (Worst First)",
    "Fundamental Grade",
    "Financial Health Grade",
    "Growth Grade",
    "Technical Grade",
]

GRADE_KEY_MAP = {
    "Final Grade (Best First)": "final",
    "Final Grade (Worst First)": "final",
    "Fundamental Grade": "fundamental",
    "Financial Health Grade": "financial_health",
    "Growth Grade": "growth",
    "Technical Grade": "technical",
}

sort_col = st.columns([1, 3])
with sort_col[0]:
    sort_option = st.selectbox(
        "Sort by",
        ["Alphabetical", "Market"] + GRADE_SORT_OPTIONS,
        index=0,
        key="stock_detail_sort",
    )

# ─── Compute grades for filtered stocks when sorting by grade ────────

grades_map = {}  # ticker -> grade dict

if sort_option in GRADE_SORT_OPTIONS:
    # Limit to 50 stocks to avoid excessive API calls
    tickers_to_grade = filtered["Ticker"].tolist()[:50]
    if len(filtered) > 50:
        st.info(f"Grading the first 50 of {len(filtered):,} filtered stocks. Narrow your filters for more precise sorting.")

    progress_placeholder = st.empty()
    progress_placeholder.markdown(
        '<div style="font-size:13px;color:#86868b;margin:4px 0">Calculating grades...</div>',
        unsafe_allow_html=True,
    )

    for tk in tickers_to_grade:
        try:
            grades_map[tk] = _grade_stock_cached(tk)
        except Exception:
            grades_map[tk] = {
                "fundamental": 50, "financial_health": 50, "growth": 50,
                "technical": 50, "quantitative": 50, "dividend": 50,
                "sentiment": 50, "final": 50, "rating": "Hold",
                "rating_color": "#ff9500",
            }

    progress_placeholder.empty()

    # Add grade column and sort
    grade_key = GRADE_KEY_MAP[sort_option]
    filtered = filtered.copy()
    filtered["_grade"] = filtered["Ticker"].map(
        lambda t: grades_map.get(t, {}).get(grade_key, 50)
    )
    ascending = sort_option == "Final Grade (Worst First)"
    filtered = filtered.sort_values("_grade", ascending=ascending)
    filtered = filtered.drop(columns=["_grade"])
elif sort_option == "Alphabetical":
    filtered = filtered.sort_values("Ticker")
elif sort_option == "Market":
    filtered = filtered.sort_values(["Market", "Ticker"])

# ─── Stats ───────────────────────────────────────────────────────────

st.markdown(f"""<div style="display:flex;gap:16px;margin:16px 0 24px">
    <div class="card-sm"><div class="label">Showing</div><div class="value-md">{len(filtered):,} stocks</div></div>
    <div class="card-sm"><div class="label">LSE</div><div class="value-md">{len(filtered[filtered['Market']=='LSE']):,}</div></div>
    <div class="card-sm"><div class="label">US</div><div class="value-md">{len(filtered[filtered['Market']=='US']):,}</div></div>
    <div class="card-sm"><div class="label">Sectors</div><div class="value-md">{filtered['Sector'].nunique()}</div></div>
    {"<div class='card-sm card-blue'><div class='label'>From Scan</div><div class='value-md'>" + str(sum(1 for t in filtered['Ticker'] if t in scan_picks_map)) + " picks</div></div>" if scan_picks_map else ""}
</div>""", unsafe_allow_html=True)

# ─── Stock Selection ─────────────────────────────────────────────────

# Build display options
display_options = []
for _, row in filtered.iterrows():
    tk = row["Ticker"]
    grade_info = grades_map.get(tk)
    base = f"{tk} | {row['Sector']} | {row['Market']}"
    parts = []
    if grade_info:
        parts.append(f"Grade: {grade_info['final']}/100 ({grade_info['rating']})")
    if tk in scan_picks_map:
        p = scan_picks_map[tk]["pick"]
        conf = p.get("confidence", 0)
        parts.append(f"AI PICK ({conf:.0f}%)")
    if parts:
        display_options.append(f"{base} | {' | '.join(parts)}")
    else:
        display_options.append(base)

if not display_options:
    st.info("No stocks match your filters. Try adjusting the market, sector, or search query.")
    st.stop()

# Determine default index
default_idx = 0
selected_stock_from_session = st.session_state.get("selected_stock", "")
if selected_stock_from_session:
    for i, opt in enumerate(display_options):
        if opt.startswith(selected_stock_from_session + " |"):
            default_idx = i
            break

selected_display = st.selectbox(
    "Select Stock",
    display_options,
    index=default_idx,
    key="stock_detail_selector",
    label_visibility="collapsed",
)

# Extract ticker from display string
selected_ticker = selected_display.split(" | ")[0].strip()

# Store in session state
st.session_state["selected_stock"] = selected_ticker

# ─── Clear session navigation flag ──────────────────────────────────
if "selected_stock_source" in st.session_state:
    del st.session_state["selected_stock_source"]

# ─── Render full analysis ────────────────────────────────────────────

if selected_ticker:
    st.markdown("---")

    # Check if this stock is in the scan results
    scan_data = scan_picks_map.get(selected_ticker)

    if scan_data:
        # Show with full scan data (AI reasoning + agent verdicts)
        st.markdown(f"""<div class="card-sm card-blue" style="margin-bottom:16px">
            <div class="label">AI PICK</div>
            <div class="value-sm" style="margin-top:4px">This stock was selected in the latest scan. Full AI analysis and agent verdicts are shown below.</div>
        </div>""", unsafe_allow_html=True)
        render_stock_detail(
            selected_ticker,
            pick=scan_data["pick"],
            raw=scan_data["raw"],
            key_prefix=f"stockdetail_{selected_ticker}",
        )
    else:
        # Show live data analysis only
        render_stock_detail(
            selected_ticker,
            pick=None,
            raw=None,
            key_prefix=f"stockdetail_{selected_ticker}",
        )
