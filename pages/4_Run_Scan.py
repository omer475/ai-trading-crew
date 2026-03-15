"""
AI Trading Crew — Run Scan Page
Execute a full pipeline scan with progress tracking.
"""

import streamlit as st
import os, sys, glob

st.set_page_config(page_title="Run Scan | AI Trading Crew", page_icon="", layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import inject_css, page_header

inject_css()
page_header()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown('<div class="section-title" style="margin-top:0">Run Scan</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Scan 1,003 stocks across LSE and US markets. AI agents find the best long-term investments.</div>', unsafe_allow_html=True)

# ─── Scan Configuration ─────────────────────────────────────────────

st.markdown('<div class="section-title" style="font-size:20px;margin-top:0">Configuration</div>', unsafe_allow_html=True)

sc1, sc2 = st.columns(2)
with sc1:
    scan_market = st.selectbox(
        "Market",
        ["All (LSE + US)", "London Stock Exchange", "US Stocks"],
        key="scan_market",
    )
with sc2:
    scan_top = st.selectbox(
        "Top N picks",
        [5, 10, 15, 20],
        index=1,
        key="scan_top",
    )

skip_ai = st.checkbox("Quick scan (skip AI analysis \u2014 faster)", value=False, key="scan_skip_ai")

st.markdown("")

# ─── Run Button ──────────────────────────────────────────────────────

if st.button("Start Scan", use_container_width=True, key="scan_run_btn"):
    mm = {
        "All (LSE + US)": "all",
        "London Stock Exchange": "lse",
        "US Stocks": "us",
    }
    with st.status("Scanning...", expanded=True) as status:
        try:
            import subprocess

            cmd = [
                "python3", "pipeline.py",
                "--market", mm[scan_market],
                "--top", str(scan_top),
            ]
            if skip_ai:
                cmd.append("--skip-ai")

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=PROJECT_ROOT,
            )

            out_area = st.empty()
            lines = []
            for line in iter(proc.stdout.readline, ""):
                lines.append(line.rstrip())
                out_area.code("\n".join(lines[-25:]))

            proc.wait()

            if proc.returncode == 0:
                status.update(label="Scan complete!", state="complete")
                st.success("Scan finished successfully. Navigate to **Overview** or **Top Picks** to see results.")
                st.cache_data.clear()
            else:
                status.update(label="Scan failed", state="error")
                st.error("The scan encountered an error. Check the output above.")
        except Exception as e:
            st.error(f"Error running scan: {str(e)}")

# ─── Past Scans ──────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="section-title">Past Scans</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Previous scan results stored in the reports directory.</div>', unsafe_allow_html=True)

rd = os.path.join(PROJECT_ROOT, "reports")
if os.path.exists(rd):
    jf = sorted(glob.glob(os.path.join(rd, "*_scan.json")), reverse=True)
    if jf:
        for i, f in enumerate(jf[:15]):
            fname = os.path.basename(f).replace("_scan.json", "")
            fsize = os.path.getsize(f)
            size_str = f"{fsize / 1024:.1f} KB" if fsize < 1024 * 1024 else f"{fsize / (1024*1024):.1f} MB"

            st.markdown(f"""<div class="card-sm" style="margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
                <div>
                    <div class="value-sm">{fname}</div>
                </div>
                <div class="caption">{size_str}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="caption">No scan reports found yet.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="caption">Reports directory not found. Run your first scan to create it.</div>', unsafe_allow_html=True)

# ─── Help Section ────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="section-title" style="font-size:20px">Scan Options</div>', unsafe_allow_html=True)

st.markdown("""<div class="card" style="margin-top:8px">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
        <div>
            <div class="label">Full Scan</div>
            <div style="font-size:14px;color:#424245;line-height:1.6;margin-top:4px">
                Runs the complete pipeline: market regime detection, universe scan
                (filters to top 30), AI deep analysis with 5 agents, final ranking,
                and report generation. Takes 10-30 minutes depending on market size.
            </div>
        </div>
        <div>
            <div class="label">Quick Scan (Skip AI)</div>
            <div style="font-size:14px;color:#424245;line-height:1.6;margin-top:4px">
                Runs only the scanner phase: technical and fundamental screening
                of all stocks, without the AI agent analysis. Much faster (2-5 minutes)
                but no AI reasoning or agent verdicts.
            </div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)
