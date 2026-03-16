"""
AI Trading Crew — Stocks Browser
Browse all scanned stocks with filters, sort, pagination, clickable <a> rows.
No st.button() in the table. No st.dataframe().
"""

import streamlit as st
import sys, os

st.set_page_config(
    page_title="Stocks | AI Trading Crew",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header, get_latest_report, grade_from_scan_signals

inject_css()
page_header()

report = get_latest_report()

if not report or not report.get("all_scanned_signals"):
    st.markdown("""<div style="text-align:center;padding:80px 0">
        <div style="font-size:22px;font-weight:600;color:#1d1d1f">No scan data</div>
        <div style="font-size:14px;color:#86868b;margin-top:8px">Run a scan first.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

all_signals = report["all_scanned_signals"]

# ── Pre-compute grades for every stock ──
@st.cache_data
def build_stock_list(_signals):
    """Build enriched stock list with grades from scan signals (no API calls)."""
    rows = []
    for sig in _signals:
        sym = sig["symbol"]
        ss = sig.get("scanner_signals", {})
        grades = grade_from_scan_signals(ss)
        market = "LSE" if sym.endswith(".L") else "US"
        rows.append({
            "symbol": sym,
            "name": ss.get("company_name", sym),
            "market": market,
            "price": ss.get("price", 0),
            "score": sig.get("score", 0),
            "grade": grades["final"],
            "rating": grades["rating"],
            "rating_color": grades["rating_color"],
            "fundamental": grades["fundamental"],
            "financial_health": grades["financial_health"],
            "growth": grades["growth"],
            "technical": grades["technical"],
            "target_price": ss.get("resistance", 0) or 0,
            "pe_ratio": ss.get("pe_ratio"),
            "revenue_growth": ss.get("revenue_growth"),
            "profit_margins": ss.get("profit_margins"),
            "market_cap": ss.get("market_cap", 0),
            "rsi": ss.get("rsi", 50),
        })
    return rows

stocks = build_stock_list(all_signals)
total_count = len(stocks)

# ── Title ──
st.markdown(f"""<div style="padding:24px 0 20px">
    <div class="hero-title" style="font-size:36px">Stocks</div>
    <div class="hero-sub" style="font-size:15px">{total_count:,} stocks &middot; Click any row to analyze</div>
</div>""", unsafe_allow_html=True)

# ── Search box (auto-navigate on exact match) ──
search = st.text_input(
    "Search",
    placeholder="Type a ticker (e.g. GPOR) and press Enter...",
    label_visibility="collapsed",
    key="stocks_search",
).strip().upper()

all_symbols = {s["symbol"].upper() for s in stocks}
if search and search in all_symbols:
    st.query_params["ticker"] = search
    st.switch_page("pages/5_Analysis.py")

# ── Filter row ──
fc1, fc2, fc3 = st.columns([1, 1, 2])

with fc1:
    market_filter = st.selectbox("Market", ["All", "LSE", "US"], key="stocks_market")
with fc2:
    # Since there's no sector data in the JSON, provide a simple placeholder
    sector_filter = st.selectbox("Sector", ["All"], key="stocks_sector")
with fc3:
    sort_option = st.selectbox("Sort", [
        "Grade (Best First)",
        "Grade (Worst First)",
        "Alphabetical (A-Z)",
        "Alphabetical (Z-A)",
        "Fundamental Score",
        "Financial Health Score",
        "Growth Score",
        "Technical Score",
        "Highest Target Price",
        "Highest Upside %",
        "Highest Confidence",
    ], key="stocks_sort")

# ── Apply filters ──
filtered = stocks

if search:
    search_lower = search.lower()
    filtered = [s for s in filtered if search_lower in s["symbol"].lower() or search_lower in s["name"].lower()]

if market_filter != "All":
    filtered = [s for s in filtered if s["market"] == market_filter]

# ── Apply sort ──
if sort_option == "Grade (Best First)":
    filtered.sort(key=lambda s: s["grade"], reverse=True)
elif sort_option == "Grade (Worst First)":
    filtered.sort(key=lambda s: s["grade"])
elif sort_option == "Alphabetical (A-Z)":
    filtered.sort(key=lambda s: s["symbol"])
elif sort_option == "Alphabetical (Z-A)":
    filtered.sort(key=lambda s: s["symbol"], reverse=True)
elif sort_option == "Fundamental Score":
    filtered.sort(key=lambda s: s["fundamental"], reverse=True)
elif sort_option == "Financial Health Score":
    filtered.sort(key=lambda s: s["financial_health"], reverse=True)
elif sort_option == "Growth Score":
    filtered.sort(key=lambda s: s["growth"], reverse=True)
elif sort_option == "Technical Score":
    filtered.sort(key=lambda s: s["technical"], reverse=True)
elif sort_option == "Highest Target Price":
    filtered.sort(key=lambda s: s["target_price"], reverse=True)
elif sort_option == "Highest Upside %":
    def _upside(s):
        if s["price"] > 0 and s["target_price"] > 0:
            return (s["target_price"] - s["price"]) / s["price"] * 100
        return -999
    filtered.sort(key=_upside, reverse=True)
elif sort_option == "Highest Confidence":
    filtered.sort(key=lambda s: s["score"], reverse=True)

# ── Results count ──
st.markdown(f"""<div style="font-size:13px;color:#86868b;padding:8px 0 12px">
    Showing {len(filtered):,} of {total_count:,} stocks
</div>""", unsafe_allow_html=True)

# ── Pagination ──
PER_PAGE = 50
total_pages = max(1, (len(filtered) + PER_PAGE - 1) // PER_PAGE)

if "stocks_page" not in st.session_state:
    st.session_state["stocks_page"] = 0

page = st.session_state["stocks_page"]
if page >= total_pages:
    page = total_pages - 1
    st.session_state["stocks_page"] = page

start = page * PER_PAGE
end = min(start + PER_PAGE, len(filtered))
page_stocks = filtered[start:end]

# ── Clickable HTML table ──
GRID = "grid-template-columns: 100px 80px 1fr 70px 120px 100px 90px"
HS = ("padding:12px 16px;font-size:11px;font-weight:600;color:#aeaeb2;"
      "text-transform:uppercase;letter-spacing:0.8px;text-align:left")
CS = "padding:14px 16px;font-size:14px;display:flex;align-items:center"

header = f"""<div style="display:grid;{GRID};border-bottom:1px solid #e8e8ed;padding:0 4px">
    <div style="{HS}">Ticker</div>
    <div style="{HS}">Market</div>
    <div style="{HS}">Company</div>
    <div style="{HS}">Grade</div>
    <div style="{HS}">Rating</div>
    <div style="{HS}">Score</div>
    <div style="{HS}">Price</div>
</div>"""

rows_html = ""
for s in page_stocks:
    sym = s["symbol"]
    name = s["name"] or sym
    grade = s["grade"]
    rating = s["rating"]
    rating_color = s["rating_color"]
    price = s["price"]
    score = s["score"]

    # Grade color coding
    if grade >= 75:
        grade_color = "#2e7d32"
    elif grade >= 55:
        grade_color = "#007aff"
    elif grade >= 45:
        grade_color = "#ff9500"
    else:
        grade_color = "#ff3b30"

    market_badge = (
        '<span style="font-size:11px;font-weight:600;padding:3px 8px;border-radius:6px;'
        f'background:{"#eef4ff" if s["market"] == "US" else "#f5eefa"};'
        f'color:{"#1565c0" if s["market"] == "US" else "#7b1fa2"}">{s["market"]}</span>'
    )

    # Truncate long names
    display_name = name if len(name) <= 35 else name[:32] + "..."

    rows_html += f"""<a href="/Analysis?ticker={sym}" target="_self"
        style="display:grid;{GRID};text-decoration:none;color:inherit;
               border-bottom:1px solid #f0f0f5;padding:0 4px;
               transition:background 0.15s"
        onmouseover="this.style.background='#f8f9fa'"
        onmouseout="this.style.background='transparent'">
        <div style="{CS};font-weight:600;color:#1d1d1f">{sym}</div>
        <div style="{CS}">{market_badge}</div>
        <div style="{CS};font-size:13px;color:#86868b">{display_name}</div>
        <div style="{CS};font-weight:700;color:{grade_color}">{grade}</div>
        <div style="{CS};font-size:12px;font-weight:600;color:{rating_color}">{rating}</div>
        <div style="{CS};font-size:13px;color:#86868b">{score:.0f}</div>
        <div style="{CS};font-weight:600;color:#1d1d1f">${price:.2f}</div>
    </a>"""

st.markdown(f"""
<div style="background:white;border:1px solid #f0f0f5;border-radius:16px;overflow:hidden;
            box-shadow:0 1px 3px rgba(0,0,0,0.04)">
    {header}
    {rows_html}
</div>
""", unsafe_allow_html=True)

# ── Pagination controls ──
if total_pages > 1:
    st.markdown(f"""<div style="display:flex;justify-content:center;align-items:center;gap:16px;
                    padding:24px 0;font-size:14px;color:#86868b">
        Page {page + 1} of {total_pages}
    </div>""", unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        if st.button("Previous", disabled=(page == 0), key="stocks_prev", use_container_width=True):
            st.session_state["stocks_page"] = max(0, page - 1)
            st.rerun()
    with p2:
        if st.button("Next", disabled=(page >= total_pages - 1), key="stocks_next", use_container_width=True):
            st.session_state["stocks_page"] = min(total_pages - 1, page + 1)
            st.rerun()
