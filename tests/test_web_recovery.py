"""Hard process termination tests: real service/CPU workers, generated software signals."""

import json
import os
import socket
import subprocess
import sys
import time

import httpx
import pytest

from taketwo.web.processes import ProcessTree, lease

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows kernel supervision")


def eventually(probe, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            value = probe()
            if value:
                return value
        except (OSError, ValueError, httpx.HTTPError):
            pass
        time.sleep(0.05)
    raise AssertionError("Real process test deadline exceeded.")


def launch(root):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import os,sys; from pathlib import Path; "
            "Path(sys.argv[1]).write_text(str(os.getpid())); "
            "sys.argv=sys.argv[1:]; from taketwo.web.cli import main; main()",
            str(root / "service.pid"),
            "--workspace",
            str(root),
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    client = httpx.Client(base_url=f"http://127.0.0.1:{port}/api/v1", timeout=3)
    eventually(lambda: client.get("/health").status_code == 200)
    process.service_pid = int((root / "service.pid").read_text())
    return process, client


def worker(root):
    files = list((root / ".runtime").glob("taketwo-job-*/worker.json"))
    return json.loads(files[0].read_text())["pid"] if files else None


def kill(pid):
    # Terminate exactly this process; tree cleanup must be done by the application/kernel.

    from taketwo.web.processes import checked, kernel, w

    kernel.OpenProcess.argtypes, kernel.OpenProcess.restype = [w.DWORD, w.BOOL, w.DWORD], w.HANDLE
    kernel.TerminateProcess.argtypes, kernel.TerminateProcess.restype = [w.HANDLE, w.UINT], w.BOOL
    handle = checked(kernel.OpenProcess(1, False, pid))
    try:
        checked(kernel.TerminateProcess(handle, 99))
    finally:
        kernel.CloseHandle(handle)


def alive(pid):
    import ctypes

    from taketwo.web.processes import kernel, w

    kernel.OpenProcess.argtypes, kernel.OpenProcess.restype = [w.DWORD, w.BOOL, w.DWORD], w.HANDLE
    kernel.GetExitCodeProcess.argtypes, kernel.GetExitCodeProcess.restype = (
        [w.HANDLE, w.LPVOID],
        w.BOOL,
    )
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return False
    try:
        code = w.DWORD()
        assert kernel.GetExitCodeProcess(handle, ctypes.byref(code))
        return code.value == 259
    finally:
        kernel.CloseHandle(handle)


def test_hard_service_crash_restart_marks_failure_and_removes_only_owned_temp(imported):
    root, recording = imported
    process, client = launch(root)
    restarted = None
    try:
        request = {"reference_id": recording.id, "align": False}
        job = client.post("/analyses", json=request).json()
        pid = eventually(lambda: worker(root))
        assert alive(pid)
        # A second service cannot acquire the live kernel lease.
        with pytest.raises(RuntimeError, match="lease"):
            with lease(root, ".service.lock"):
                pass
        untouched = root / ".runtime" / "operator-notes"
        untouched.mkdir()
        (untouched / "keep.txt").write_text("not job-owned")
        kill(process.service_pid)
        process.wait(timeout=15)
        eventually(lambda: not alive(pid))
        assert list((root / ".runtime").glob("taketwo-job-*"))
        client.close()
        restarted, client = launch(root)
        old = client.get(f"/analyses/{job['id']}").json()
        assert old["state"] == "failed" and old["error"]["code"] == "interrupted"
        assert not list((root / ".runtime").glob("taketwo-job-*"))
        assert (untouched / "keep.txt").read_text() == "not job-owned"
        assert len(client.get("/analyses").json()) == 1  # Never automatically requeue.
        retry = client.post("/analyses", json=request).json()
        assert retry["id"] != job["id"]
        assert client.post("/analyses", json=request).json()["id"] == retry["id"]
        final = eventually(lambda: terminal(client, retry["id"]), timeout=60)
        assert final["state"] == "completed", final
        assert client.get(f"/analyses/{retry['id']}/report").json()["overall_score"] is None
        assert final["peak_commit_bytes"] > 0 and final["stage_elapsed_s"]
        # A digest-invalid complete artifact remains untrusted after another hard restart.
        kill(restarted.service_pid)
        restarted.wait(timeout=15)
        path = root / final["artifacts"][recording.id]["features"]
        payload = json.loads(path.read_text())
        payload["result"]["quality"]["peak"] += 1
        path.write_text(json.dumps(payload))
        client.close()
        restarted, client = launch(root)
        invalid = client.post("/analyses", json=request).json()
        rejected = eventually(lambda: terminal(client, invalid["id"]), timeout=60)
        # Re-extraction cannot silently overwrite a corrupt content-addressed destination.
        assert rejected["state"] == "failed" and rejected["report_path"] is None
        assert rejected["error"]["code"] == "processing_failed"
        assert json.loads(path.read_text()) == payload
        assert client.get(f"/analyses/{retry['id']}/report").status_code == 422
    finally:
        client.close()
        for service in (process, restarted):
            if service and service.poll() is None:
                kill(service.service_pid)
                service.wait(timeout=15)


def terminal(client, identifier):
    job = client.get(f"/analyses/{identifier}").json()
    return job if job["state"] not in {"queued", "running"} else None


def test_hard_worker_crash_preserves_service_and_allows_retry(imported):
    root, recording = imported
    service, client = launch(root)
    try:
        request = {"reference_id": recording.id, "align": False}
        job = client.post("/analyses", json=request).json()
        kill(eventually(lambda: worker(root)))
        final = eventually(lambda: terminal(client, job["id"]))
        assert final["state"] == "failed" and final["error"]["code"] == "worker_failed"
        assert not (root / ".dataset.lock").exists()
        assert not list((root / ".runtime").glob("taketwo-job-*"))
        assert client.get("/health").json()["ready"] is True
        retry = client.post("/analyses", json=request).json()
        assert eventually(lambda: terminal(client, retry["id"]), 60)["state"] == "completed"
    finally:
        client.close()
        kill(service.service_pid)
        service.wait(timeout=15)


def test_real_descendant_dies_when_supervisor_handle_is_lost(tmp_path):
    script = tmp_path / "supervisor.py"
    child_code = """import os,time,subprocess,sys
from pathlib import Path
gate=Path(os.environ['TAKETWO_WORKER_GATE'])
while not gate.exists(): time.sleep(.01)
p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])
Path(sys.argv[1]).write_text(str(p.pid))
time.sleep(60)
"""
    script.write_text(
        "import os,sys,time\nfrom pathlib import Path\n"
        "from taketwo.web.processes import ProcessTree\n"
        "root=Path(sys.argv[1])\n"
        "(root/'supervisor.pid').write_text(str(os.getpid()))\n"
        "tree=ProcessTree(root,'test-descendants')\n"
        f"code={child_code!r}\n"
        "p=tree.spawn([sys.executable,'-c',code,str(root/'child.pid')],os.environ.copy(),root)\n"
        "(root/'worker.pid').write_text(str(p.pid))\ntime.sleep(60)\n"
    )
    process = subprocess.Popen([sys.executable, str(script), str(tmp_path)])
    try:
        child = eventually(lambda: int((tmp_path / "child.pid").read_text()))
        parent = int((tmp_path / "worker.pid").read_text())
        assert alive(parent) and alive(child)
        kill(int((tmp_path / "supervisor.pid").read_text()))
        process.wait(timeout=15)
        eventually(lambda: not alive(parent) and not alive(child))
    finally:
        if process.poll() is None:
            kill(int((tmp_path / "supervisor.pid").read_text()))
            process.wait(timeout=15)


def test_kernel_enforces_commit_memory_limit(tmp_path):
    with ProcessTree(tmp_path, "test-memory", memory_limit=128 * 1024**2) as tree:
        output = tmp_path / "memory.txt"
        code = """from pathlib import Path
import sys,os,time
while not Path(os.environ['TAKETWO_WORKER_GATE']).exists(): time.sleep(.01)
try: b=bytearray(256*1024**2)
except MemoryError: Path(sys.argv[1]).write_text('bounded')
"""
        process = tree.spawn([sys.executable, "-c", code, str(output)], os.environ.copy(), tmp_path)
        assert process.wait(timeout=15) == 0
        assert output.read_text() == "bounded"
        # Windows can charge an attempted allocation to the peak counter before rejection.
        # The actual allocation must fail; verify the configured kernel limit independently.
        import ctypes

        from taketwo.web.processes import ExtendedLimits, checked, kernel

        limits = ExtendedLimits()
        checked(
            kernel.QueryInformationJobObject(
                tree.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits), None
            )
        )
        assert limits.job_memory == 128 * 1024**2 and limits.basic.flags & 0x200
        assert tree.peak_commit_bytes() > 0


def test_unknown_legacy_or_cli_lock_is_not_deleted(imported):
    root, _ = imported
    lock = root / ".dataset.lock"
    lock.write_text("unknown owner; preserve")
    with pytest.raises(RuntimeError, match="lease"):
        with lease(root, ".dataset.lock"):
            pass
    assert lock.read_text() == "unknown owner; preserve"
