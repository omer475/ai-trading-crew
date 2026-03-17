"""
AI Trading Crew — Run Scan Page
"""

import streamlit as st
import os, sys, glob, subprocess, time

st.set_page_config(page_title="Run Scan | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header
inject_css()
page_header()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown("""<div style="padding:24px 0 8px">
    <div class="hero-title" style="font-size:36px">Run Scan</div>
    <div class="hero-sub" style="font-size:15px">Scan 1,003 stocks. AI agents find the best investments.</div>
</div>""", unsafe_allow_html=True)

# Use a form to prevent reruns when changing options
with st.form("scan_form"):
    sc1, sc2 = st.columns(2)
    with sc1:
        scan_market = st.selectbox("Market", ["All (LSE + US)", "London Stock Exchange", "US Stocks"])
    with sc2:
        scan_top = st.selectbox("Top N picks", [5, 10, 15, 20], index=1)

    skip_ai = st.checkbox("Quick scan (skip AI — faster)", value=True)

    submitted = st.form_submit_button("Start Scan", use_container_width=True)

if submitted:
    mm = {"All (LSE + US)": "all", "London Stock Exchange": "lse", "US Stocks": "us"}

    cmd = ["python3", "pipeline.py", "--market", mm[scan_market], "--top", str(scan_top)]
    if skip_ai:
        cmd.append("--skip-ai")

    st.info("Scan is running. This takes 5-10 minutes (quick) or 30-90 minutes (with AI). Do not navigate away.")

    progress = st.empty()
    output = st.empty()

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=PROJECT_ROOT,
            env=env,
        )

        lines = []
        for line in iter(proc.stdout.readline, ""):
            stripped = line.rstrip()
            # Skip noisy delisted errors
            if "delisted" in stripped or "YFPricesMissing" in stripped:
                continue
            lines.append(stripped)
            # Update output every few lines to reduce Streamlit overhead
            if len(lines) % 3 == 0 or "Pipeline complete" in stripped or "STAGE" in stripped:
                output.code("\n".join(lines[-20:]))

        proc.wait()

        if proc.returncode == 0:
            st.success("Scan complete! Refresh the page or navigate to Overview / Top Picks to see results.")
            st.cache_data.clear()
            st.balloons()
        else:
            st.error(f"Scan exited with code {proc.returncode}")
            output.code("\n".join(lines[-30:]))

    except Exception as e:
        st.error(f"Error: {str(e)}")

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
    else:
        st.markdown('<div class="caption">No scans yet.</div>', unsafe_allow_html=True)
