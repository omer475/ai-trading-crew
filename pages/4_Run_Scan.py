"""
AI Trading Crew — Run Scan Page
Launches scan as a background process that survives page navigation.
"""

import streamlit as st
import os, sys, glob, subprocess, json

st.set_page_config(page_title="Run Scan | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header, _get_scan_status
inject_css()
page_header()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_FILE = os.path.join(PROJECT_ROOT, "reports", ".scan_status.json")
LOG_FILE = os.path.join(PROJECT_ROOT, "reports", ".scan_log.txt")

st.markdown("""<div style="padding:24px 0 8px">
    <div class="hero-title" style="font-size:36px">Run Scan</div>
    <div class="hero-sub" style="font-size:15px">Scan runs in the background — you can navigate to other pages.</div>
</div>""", unsafe_allow_html=True)

# Check current status
scan = _get_scan_status()
is_running = scan and scan.get("status") == "running"

if is_running:
    # Show live status
    st.markdown(f"""<div class="card" style="margin-bottom:24px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
            <div style="width:10px;height:10px;border-radius:50%;background:#34c759;animation:pulse 1.5s infinite"></div>
            <span style="font-size:16px;font-weight:600;color:#1d1d1f">Scan Running</span>
        </div>
        <div style="font-size:14px;color:#424245;margin-bottom:8px">{scan.get("stage","")}</div>
        <div style="background:#f0f0f5;border-radius:6px;height:8px;overflow:hidden;margin-bottom:8px">
            <div style="width:{scan.get("progress",0)}%;height:8px;background:#34c759;border-radius:6px;transition:width 0.5s"></div>
        </div>
        <div style="font-size:13px;color:#86868b">{scan.get("message","")}</div>
        <div style="font-size:11px;color:#aeaeb2;margin-top:8px">Started: {scan.get("started_at","")[:19]}</div>
    </div>
    <style>@keyframes pulse {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:0.3 }} }}</style>
    """, unsafe_allow_html=True)

    # Show live log
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            lines = f.readlines()
        if lines:
            # Filter noisy lines
            clean = [l.rstrip() for l in lines if "delisted" not in l and "YFPricesMissing" not in l]
            st.code("\n".join(clean[-25:]))

    if st.button("Refresh Status"):
        st.rerun()

else:
    # Show start form
    if scan and scan.get("status") == "complete":
        st.success(f"Last scan completed successfully. {scan.get('message','')}")
    elif scan and scan.get("status") == "failed":
        st.error(f"Last scan failed: {scan.get('error','')[:200]}")

    with st.form("scan_form"):
        sc1, sc2 = st.columns(2)
        with sc1:
            scan_market = st.selectbox("Market", ["US Stocks", "London Stock Exchange", "All (LSE + US)"])
        with sc2:
            scan_top = st.selectbox("Top N picks", [5, 10, 15, 20], index=1)

        skip_ai = st.checkbox("Quick scan (skip AI — faster)", value=True)

        submitted = st.form_submit_button("Start Scan", use_container_width=True)

    if submitted:
        mm = {"All (LSE + US)": "all", "London Stock Exchange": "lse", "US Stocks": "us"}

        cmd = [
            sys.executable, os.path.join(PROJECT_ROOT, "scan_runner.py"),
            "--market", mm[scan_market],
            "--top", str(scan_top),
        ]
        if skip_ai:
            cmd.append("--skip-ai")

        # Launch as detached background process
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # detach from Streamlit
            cwd=PROJECT_ROOT,
        )

        st.success("Scan started in the background! You can navigate to other pages — the status bar at the top will show progress.")
        st.rerun()

# ── Past Scans ──
st.markdown("---")
st.markdown('<div class="section-title">Past Scans</div>', unsafe_allow_html=True)

rd = os.path.join(PROJECT_ROOT, "reports")
if os.path.exists(rd):
    jf = sorted(glob.glob(os.path.join(rd, "*_scan.json")), reverse=True)
    if jf:
        for f in jf[:10]:
            fname = os.path.basename(f).replace("_scan.json", "")
            fsize = os.path.getsize(f)
            size_str = f"{fsize / 1024:.1f} KB" if fsize < 1024 * 1024 else f"{fsize / (1024*1024):.1f} MB"
            st.markdown(f"""<div class="card-sm" style="margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
                <div class="value-sm">{fname}</div>
                <div class="caption">{size_str}</div>
            </div>""", unsafe_allow_html=True)
