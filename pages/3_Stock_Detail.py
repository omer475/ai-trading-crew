"""
AI Trading Crew — Stock Browser
Browse all 1,003 stocks. Click any stock to open its analysis page.
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

st.markdown('<div style="max-width:800px;margin:0 auto 32px">', unsafe_allow_html=True)
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
st.markdown('</div>', unsafe_allow_html=True)

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

# ─── Results count ───────────────────────────────────────────────────

st.markdown(f'<div style="text-align:center;color:#86868b;font-size:13px;margin-bottom:24px">{len(df):,} results</div>', unsafe_allow_html=True)

# ─── Stock Grid ──────────────────────────────────────────────────────

PAGE_SIZE = 30
if "sd_page" not in st.session_state:
    st.session_state["sd_page"] = 0

total_pages = max(1, (len(df) + PAGE_SIZE - 1) // PAGE_SIZE)
page = min(st.session_state["sd_page"], total_pages - 1)
start = page * PAGE_SIZE
end = min(start + PAGE_SIZE, len(df))
page_df = df.iloc[start:end]

# Render stocks as clean cards in a grid
cols_per_row = 3
rows_needed = (len(page_df) + cols_per_row - 1) // cols_per_row

for row_idx in range(rows_needed):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        item_idx = row_idx * cols_per_row + col_idx
        if item_idx >= len(page_df):
            break

        row = page_df.iloc[item_idx]
        tk = row["Ticker"]
        grade = row["_grade"]
        rating = row["_rating"]
        is_pick = tk in picks_map

        # Grade color
        if grade >= 75: gc = "#2e7d32"
        elif grade >= 55: gc = "#007aff"
        elif grade >= 45: gc = "#ff9500"
        elif grade >= 0: gc = "#ff3b30"
        else: gc = "#aeaeb2"

        grade_str = f"{grade:.0f}" if grade >= 0 else "—"

        with cols[col_idx]:
            # Card content
            pick_badge = ""
            if is_pick:
                tgt = picks_map[tk]["pick"].get("target", 0)
                pick_badge = f'<div style="margin-top:8px"><span style="background:#eef4ff;color:#1565c0;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600">AI Pick</span>{f" <span style=color:#86868b;font-size:12px>Target ${tgt:.0f}</span>" if tgt else ""}</div>'

            st.markdown(f"""<div style="background:white;border:1px solid #f0f0f5;border-radius:14px;padding:20px;margin-bottom:8px;
                box-shadow:0 1px 3px rgba(0,0,0,0.03);transition:all 0.2s">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <div style="font-size:17px;font-weight:600;color:#1d1d1f">{tk}</div>
                        <div style="font-size:12px;color:#86868b;margin-top:2px">{row['Sector']}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:22px;font-weight:700;color:{gc}">{grade_str}</div>
                        <div style="font-size:10px;color:#aeaeb2">/100</div>
                    </div>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px">
                    <div style="font-size:12px;color:{gc};font-weight:500">{rating}</div>
                    <div style="font-size:11px;color:#aeaeb2">{row['Market']}</div>
                </div>
                {pick_badge}
            </div>""", unsafe_allow_html=True)

            if st.button("View Analysis", key=f"v_{tk}", use_container_width=True):
                st.session_state["selected_stock"] = tk
                st.switch_page("pages/5_Analysis.py")

# ─── Pagination ──────────────────────────────────────────────────────

st.markdown("")
pc1, pc2, pc3 = st.columns([1, 2, 1])
with pc1:
    if page > 0 and st.button("Previous", key="prev"):
        st.session_state["sd_page"] = page - 1
        st.rerun()
with pc2:
    st.markdown(f'<div style="text-align:center;padding:8px;color:#86868b;font-size:13px">{start+1}–{end} of {len(df):,}</div>', unsafe_allow_html=True)
with pc3:
    if end < len(df) and st.button("Next", key="next"):
        st.session_state["sd_page"] = page + 1
        st.rerun()
