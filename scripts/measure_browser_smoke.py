"""Measure genuine browser smoke process tree; includes Node, Chromium and backend."""

import argparse
import json
import os
import runpy
import subprocess
import time
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    measure = runpy.run_path(str(root / "scripts/benchmark_analysis.py"))["windows_tree_bytes"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "local-data/acquisition/phase4-browser-measurement.json",
    )
    output = parser.parse_args().output
    if output.exists():
        raise ValueError("Choose a fresh measurement output; existing evidence is preserved.")
    env = {**os.environ, "TAKETWO_REAL_SMOKE": "1"}
    started = time.perf_counter()
    peak = None
    log = output.with_suffix(".log")
    with log.open("xb") as stream:
        process = subprocess.Popen(
            ["cmd.exe", "/d", "/c", "npm", "run", "e2e"],
            cwd=root / "frontend",
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        while process.poll() is None:
            measured = measure(process.pid)
            if measured is not None:
                peak = max(peak or 0, measured)
            time.sleep(0.1)
    result = {
        "workflow": "genuine public-domain reference import, MFA, acoustic extraction, "
        "abstention, playback, export and axe browser checks",
        "exit_code": process.returncode,
        "elapsed_workflow_s": time.perf_counter() - started,
        "sampled_peak_tree_working_set_bytes": peak,
        "sample_period_s": 0.1,
        "scope": "Entire browser test process tree including Node, Chromium, API, CPU worker "
        "and MFA; sampled lower bound, shared pages may be counted repeatedly. "
        "Not an eligible real-pair benchmark.",
    }
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
