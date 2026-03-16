"""
AI Trading Crew — Overview Page
Market regime card, top 3 picks as clickable HTML cards.
"""

import streamlit as st
import sys, os

st.set_page_config(
    page_title="Overview | AI Trading Crew",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    inject_css, page_header, get_latest_report, normalize_pick,
    regime_badge, metric_card, progress_bar,
)

inject_css()
page_header()

report = get_latest_report()

if not report:
    st.markdown("""<div style="text-align:center;padding:100px 0">
        <div style="font-size:24px;font-weight:600;color:#1d1d1f">No scan report found</div>
        <div style="font-size:14px;color:#86868b;margin-top:8px">Run a scan first from the Run Scan page.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

picks = report.get("picks", [])

# ── Title ──
st.markdown("""<div style="padding:24px 0 8px">
    <div class="hero-title" style="font-size:36px">Overview</div>
    <div class="hero-sub" style="font-size:15px">Market environment and top AI recommendations.</div>
</div>""", unsafe_allow_html=True)

# ── Market Regime Card ──
regime_data = report.get("regime", {})
if isinstance(regime_data, dict):
    regime_val = regime_data.get("regime", "Unknown")
    composite = regime_data.get("composite_score", 0)
    conf = regime_data.get("confidence", 0)
    if conf <= 1:
        conf *= 100

    st.markdown(f"""
    <div class="card" style="margin-bottom:32px">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px">
            <div>
                <div class="label">Market Regime</div>
                <div style="margin-top:8px">{regime_badge(regime_val)}</div>
            </div>
            <div style="display:flex;gap:32px">
                <div>
                    <div class="label">Composite Score</div>
                    <div class="value-lg" style="margin-top:4px">{composite:+.3f}</div>
                </div>
                <div>
                    <div class="label">Confidence</div>
                    <div class="value-lg" style="margin-top:4px">{conf:.0f}%</div>
                </div>
                <div>
                    <div class="label">Last Scan</div>
                    <div class="value-lg" style="margin-top:4px">{report.get("scan_date", "—")}</div>
                </div>
                <div>
                    <div class="label">Stocks Scanned</div>
                    <div class="value-lg" style="margin-top:4px">{report.get("stocks_scanned", 0):,}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Regime signals breakdown
    signals_list = regime_data.get("signals", [])
    if signals_list:
        sig_html = ""
        for sig in signals_list:
            s_name = sig.get("name", "").replace("_", " ").title()
            s_score = sig.get("score", 0)
            s_interp = sig.get("interpretation", "")
            if s_score > 0.2:
                dot_cls = "dot-green"
            elif s_score < -0.2:
                dot_cls = "dot-red"
            else:
                dot_cls = "dot-orange"
            sig_html += f"""<div class="card-sm" style="margin-bottom:8px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <span class="dot {dot_cls}"></span>
                        <span class="value-sm">{s_name}</span>
                    </div>
                    <span class="value-sm" style="color:{'#2e7d32' if s_score > 0 else '#c62828' if s_score < 0 else '#86868b'}">{s_score:+.3f}</span>
                </div>
                <div class="caption" style="margin-top:4px;margin-left:14px">{s_interp}</div>
            </div>"""
        st.markdown(sig_html, unsafe_allow_html=True)


# ── Top 3 Picks as clickable HTML cards ──
if picks:
    st.markdown("""<div class="section-title">Top Recommendations</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="section-sub">AI-selected from {report.get("stocks_scanned", 1003):,} stocks. Click any card to see full analysis.</div>""", unsafe_allow_html=True)

    cards_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">'

    for i, raw_pick in enumerate(picks[:3]):
        pick = normalize_pick(raw_pick)
        tk = pick["ticker"]
        conf = pick["confidence"]
        price = pick["price"]
        tgt = pick.get("target", 0)
        upside = ((tgt - price) / price * 100) if price > 0 and tgt > 0 else 0
        name = pick["name"] or tk

        if conf >= 75:
            conf_color = "#2e7d32"
        elif conf >= 60:
            conf_color = "#007aff"
        else:
            conf_color = "#ff9500"

        upside_html = f'<span style="font-size:13px;font-weight:600;color:#2e7d32">+{upside:.1f}%</span>' if upside > 0 else ""

        cards_html += f"""
        <a href="/Analysis?ticker={tk}" target="_self"
           style="display:block;text-decoration:none;color:inherit;
                  background:white;border:1px solid #f0f0f5;border-radius:16px;padding:24px;
                  box-shadow:0 1px 3px rgba(0,0,0,0.04);
                  transition:all 0.3s cubic-bezier(0.25,0.1,0.25,1);"
           onmouseover="this.style.boxShadow='0 8px 24px rgba(0,0,0,0.06)';this.style.borderColor='#e8e8ed';this.style.transform='translateY(-2px)'"
           onmouseout="this.style.boxShadow='0 1px 3px rgba(0,0,0,0.04)';this.style.borderColor='#f0f0f5';this.style.transform='none'">
            <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;color:#aeaeb2">#{i+1} Pick</div>
            <div style="font-size:20px;font-weight:600;color:#1d1d1f;margin:8px 0 2px;letter-spacing:-0.3px">{name}</div>
            <div style="font-size:12px;color:#86868b">{tk}</div>
            <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:20px">
                <div>
                    <div style="font-size:28px;font-weight:700;color:#1d1d1f;letter-spacing:-1px">${price:.2f}</div>
                    <div style="margin-top:2px">{upside_html}</div>
                </div>
                <div style="text-align:right">
                    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#aeaeb2">Confidence</div>
                    <div style="font-size:22px;font-weight:700;color:{conf_color}">{conf:.0f}%</div>
                </div>
            </div>
        </a>"""

    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)
