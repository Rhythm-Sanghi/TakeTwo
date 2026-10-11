"""Measure an actual analysis CLI run; Windows memory is sampled for the process tree."""

import argparse
import ctypes
import json
import os
import platform
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path


def windows_tree_bytes(root: int) -> int | None:
    if os.name != "nt":
        return None

    class Entry(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD),
            ("usage", wintypes.DWORD),
            ("pid", wintypes.DWORD),
            ("heap", ctypes.c_size_t),
            ("module", wintypes.DWORD),
            ("threads", wintypes.DWORD),
            ("parent", wintypes.DWORD),
            ("priority", wintypes.LONG),
            ("flags", wintypes.DWORD),
            ("exe", wintypes.WCHAR * 260),
        ]

    class Memory(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD),
            ("faults", wintypes.DWORD),
            ("peak", ctypes.c_size_t),
            ("working", ctypes.c_size_t),
            ("paged_peak", ctypes.c_size_t),
            ("paged", ctypes.c_size_t),
            ("nonpaged_peak", ctypes.c_size_t),
            ("nonpaged", ctypes.c_size_t),
            ("pagefile", ctypes.c_size_t),
            ("pagefile_peak", ctypes.c_size_t),
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    parents = {}
    entry = Entry()
    entry.size = ctypes.sizeof(entry)
    try:
        more = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while more:
            parents[entry.pid] = entry.parent
            more = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    members = {root}
    while True:
        children = {pid for pid, parent in parents.items() if parent in members}
        if children <= members:
            break
        members |= children
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Memory), wintypes.DWORD]
    total = 0
    measured = False
    for pid in members:
        handle = kernel.OpenProcess(0x410, False, pid)
        if handle:
            memory = Memory()
            memory.size = ctypes.sizeof(memory)
            if psapi.GetProcessMemoryInfo(handle, ctypes.byref(memory), memory.size):
                total += memory.working
                measured = True
            kernel.CloseHandle(handle)
    return total if measured else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    arguments = args.arguments[1:] if args.arguments[:1] == ["--"] else args.arguments
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    # Invoke real CPython so a Windows virtualenv launcher is not the measured root.
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(Path(sys.prefix) / "Lib/site-packages"),
            str(Path(__file__).resolve().parents[1] / "src"),
        ]
    )
    start = time.perf_counter()
    process = subprocess.Popen(
        [sys._base_executable, "-m", "taketwo.analysis.cli", *arguments],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    peak = None
    while process.poll() is None:
        measured = windows_tree_bytes(process.pid)
        if measured is not None:
            peak = max(peak or 0, measured)
        time.sleep(0.1)
    stdout, stderr = process.communicate()
    cpu = platform.processor()
    if os.name == "nt":
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
        ) as key:
            cpu = winreg.QueryValueEx(key, "ProcessorNameString")[0]
    payload = {
        "arguments": arguments,
        "exit_code": process.returncode,
        "elapsed_s": time.perf_counter() - start,
        "sampled_peak_tree_working_set_bytes": peak,
        "memory_sampling_s": 0.1,
        "cpu": cpu,
        "os": platform.platform(),
        "python": platform.python_version(),
        "stdout": stdout.decode("utf-8", errors="replace"),
        "stderr": stderr.decode("utf-8", errors="replace"),
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, allow_nan=False)
    print(json.dumps(payload, ensure_ascii=True))
    return process.returncode


if __name__ == "__main__":
    sys.exit(main())
