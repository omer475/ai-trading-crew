"""
Background scan runner. Runs the pipeline as a detached process
and writes status to a file so the dashboard can show progress.

Usage: python3 scan_runner.py --market us --skip-ai --top 10
"""

import subprocess, sys, os, json, time, argparse
from datetime import datetime

STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", ".scan_status.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", ".scan_log.txt")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def write_status(status, stage="", progress=0, message="", error=""):
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    data = {
        "status": status,  # "running", "complete", "failed", "idle"
        "stage": stage,
        "progress": progress,  # 0-100
        "message": message,
        "error": error,
        "started_at": json.load(open(STATUS_FILE)).get("started_at", "") if os.path.exists(STATUS_FILE) and status != "running" else "",
        "updated_at": datetime.now().isoformat(),
    }
    if status == "running" and not data["started_at"]:
        data["started_at"] = datetime.now().isoformat()
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", default="us")
    parser.add_argument("--skip-ai", action="store_true")
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    cmd = ["python3", "pipeline.py", "--market", args.market, "--top", str(args.top)]
    if args.skip_ai:
        cmd.append("--skip-ai")

    write_status("running", stage="Starting", progress=5, message="Initializing pipeline...")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, cwd=PROJECT_ROOT, env=env,
        )

        log_lines = []
        with open(LOG_FILE, "w") as log:
            for line in iter(proc.stdout.readline, ""):
                stripped = line.rstrip()
                log.write(stripped + "\n")
                log.flush()
                log_lines.append(stripped)

                # Parse progress from output
                if "STAGE 1" in stripped:
                    write_status("running", "Stage 1: Market Regime", 10, "Detecting market regime...")
                elif "STAGE 2" in stripped:
                    write_status("running", "Stage 2: Scanning", 20, "Scanning all stocks...")
                elif "Scanned:" in stripped:
                    write_status("running", "Stage 2: Scanning", 40, stripped.strip())
                elif "STAGE 3" in stripped:
                    write_status("running", "Stage 3: AI Analysis", 50, "AI agents analyzing stocks...")
                elif "Analyzing" in stripped and "/" in stripped:
                    # Parse [5/20] style progress
                    try:
                        parts = stripped.split("[")[1].split("]")[0].split("/")
                        current, total = int(parts[0]), int(parts[1])
                        pct = 50 + int(current / total * 40)
                        write_status("running", f"Stage 3: AI Analysis ({current}/{total})", pct, stripped.strip())
                    except:
                        pass
                elif "STAGE 4" in stripped:
                    write_status("running", "Stage 4: Ranking", 92, "Ranking final picks...")
                elif "STAGE 5" in stripped:
                    write_status("running", "Stage 5: Reports", 95, "Generating reports...")
                elif "Pipeline complete" in stripped:
                    write_status("running", "Finishing", 99, "Almost done...")

        proc.wait()

        if proc.returncode == 0:
            write_status("complete", "Done", 100, "Scan finished successfully! Refresh to see results.")
        else:
            last_lines = "\n".join(log_lines[-5:])
            write_status("failed", "Error", 0, "Scan failed", error=last_lines)

    except Exception as e:
        write_status("failed", "Error", 0, str(e), error=str(e))


if __name__ == "__main__":
    run()
