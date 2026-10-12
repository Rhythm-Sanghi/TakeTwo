"""Measure an actual Windows supervised job; never supplies speech or reviewer evidence.

Requires an already imported local workspace. Writes a new evidence file exclusively.
CPU seconds include terminated descendants through Windows Job Object accounting.
"""

import argparse
import ctypes
import json
import platform
import statistics
import time
from pathlib import Path

from fastapi.testclient import TestClient

from taketwo.web.app import create_app
from taketwo.web.processes import Accounting, ProcessTree, checked, kernel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--pair")
    parser.add_argument("--alignment-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Choose a fresh evidence output.")
    cpu_seconds = None
    original = ProcessTree.peak_commit_bytes

    def measure(tree):
        nonlocal cpu_seconds
        accounting = Accounting()
        checked(
            kernel.QueryInformationJobObject(
                tree.handle, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None
            )
        )
        cpu_seconds = (accounting.times[0] + accounting.times[1]) / 10_000_000
        return original(tree)

    ProcessTree.peak_commit_bytes = measure
    timings = []
    stages = []
    started = time.perf_counter()
    try:
        with TestClient(create_app(args.workspace, args.alignment_config)) as client:
            request = {"reference_id": args.reference, "pair_id": args.pair, "align": True}
            response = client.post("/api/v1/analyses", json=request)
            response.raise_for_status()
            job = response.json()
            while job["state"] in {"queued", "running"}:
                begin = time.perf_counter()
                health = client.get("/api/v1/health")
                health.raise_for_status()
                timings.append(time.perf_counter() - begin)
                job = client.get(f"/api/v1/analyses/{job['id']}").json()
                if not stages or stages[-1] != job["stage"]:
                    stages.append(job["stage"])
                    print(job["stage"], flush=True)
                time.sleep(0.5)
                if time.perf_counter() - started > 630:
                    raise TimeoutError("Supervisor did not terminate within its bounded budget.")
            report = client.get(f"/api/v1/analyses/{job['id']}/report")
            payload = {
                "os": platform.platform(),
                "python": platform.python_version(),
                "elapsed_s": time.perf_counter() - started,
                "job": job,
                "job_tree_cpu_seconds": cpu_seconds,
                "observed_stages": stages,
                "health_requests": len(timings),
                "health_latency_median_s": statistics.median(timings),
                "health_latency_p95_s": sorted(timings)[int((len(timings) - 1) * 0.95)],
                "health_latency_max_s": max(timings),
                "report_status": report.status_code,
                "report": report.json(),
            }
            with args.output.open("x", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2, allow_nan=False)
            print(json.dumps({k: v for k, v in payload.items() if k != "report"}))
            return 0 if job["state"] == "completed" and report.is_success else 1
    finally:
        ProcessTree.peak_commit_bytes = original


if __name__ == "__main__":
    raise SystemExit(main())
