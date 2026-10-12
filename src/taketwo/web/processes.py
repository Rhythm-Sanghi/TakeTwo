"""Windows kernel-owned leases and bounded, crash-contained CPU process trees."""

import ctypes
import os
import subprocess
import time
from contextlib import contextmanager
from ctypes import wintypes as w
from hashlib import sha256

from taketwo.dataset.storage import managed_path, workspace_lock

MAX_JOB_COMMIT_BYTES = 4 * 1024**3


if os.name == "nt":
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    for name, arguments, result in (
        (
            "CreateFileW",
            [w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE],
            w.HANDLE,
        ),
        ("CreateJobObjectW", [w.LPVOID, w.LPCWSTR], w.HANDLE),
        ("OpenJobObjectW", [w.DWORD, w.BOOL, w.LPCWSTR], w.HANDLE),
        ("CloseHandle", [w.HANDLE], w.BOOL),
        ("SetInformationJobObject", [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD], w.BOOL),
        (
            "QueryInformationJobObject",
            [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD, w.LPVOID],
            w.BOOL,
        ),
        ("AssignProcessToJobObject", [w.HANDLE, w.HANDLE], w.BOOL),
        ("TerminateJobObject", [w.HANDLE, w.UINT], w.BOOL),
    ):
        function = getattr(kernel, name)
        function.argtypes, function.restype = arguments, result


class Limits(ctypes.Structure):
    _fields_ = [
        ("process_time", ctypes.c_longlong),
        ("job_time", ctypes.c_longlong),
        ("flags", w.DWORD),
        ("minimum_ws", ctypes.c_size_t),
        ("maximum_ws", ctypes.c_size_t),
        ("processes", w.DWORD),
        ("affinity", ctypes.c_size_t),
        ("priority", w.DWORD),
        ("scheduling", w.DWORD),
    ]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("basic", Limits),
        ("io", ctypes.c_ulonglong * 6),
        ("process_memory", ctypes.c_size_t),
        ("job_memory", ctypes.c_size_t),
        ("peak_process_memory", ctypes.c_size_t),
        ("peak_job_memory", ctypes.c_size_t),
    ]


class Accounting(ctypes.Structure):
    _fields_ = [
        ("times", ctypes.c_longlong * 4),
        ("page_faults", w.DWORD),
        ("total_processes", w.DWORD),
        ("active_processes", w.DWORD),
        ("terminated", w.DWORD),
    ]


def checked(result):
    if not result:
        raise ctypes.WinError(ctypes.get_last_error())
    return result


@contextmanager
def lease(root, name):
    """CREATE_NEW preserves unknown CLI/legacy locks; kernel removes our lock on exit."""
    if os.name != "nt":
        if name != ".dataset.lock":
            raise RuntimeError("Crash-safe web supervision currently requires Windows.")
        with workspace_lock(root):
            yield
        return
    path = managed_path(root, name)
    handle = kernel.CreateFileW(str(path), 0xC0010000, 0, None, 1, 0x04000000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise RuntimeError(
            f"Workspace lease {name} is held or predates crash-safe supervision. "
            "Stop/check old TakeTwo and CLI processes before inspecting a legacy lock."
        )
    try:
        yield
    finally:
        checked(kernel.CloseHandle(handle))


def job_name(root, identifier):
    identity = sha256(str(root.absolute()).casefold().encode()).hexdigest()[:24]
    return f"Local\\TakeTwo-{identity}-{identifier}"


def stop_orphan(root, identifier):
    """A named job avoids PID reuse and closes the parent-death/startup race."""
    if os.name != "nt":
        return
    handle = kernel.OpenJobObjectW(0x0008 | 0x0004, False, job_name(root, identifier))
    if not handle:
        if ctypes.get_last_error() == 2:
            return
        checked(handle)
    try:
        checked(kernel.TerminateJobObject(handle, 130))
        deadline = time.monotonic() + 15
        while True:
            state = Accounting()
            checked(
                kernel.QueryInformationJobObject(
                    handle, 1, ctypes.byref(state), ctypes.sizeof(state), None
                )
            )
            if state.active_processes == 0:
                return
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Previous CPU process tree has not stopped; recovery is blocked."
                )
            time.sleep(0.05)
    finally:
        kernel.CloseHandle(handle)


class ProcessTree:
    """The sole service-owned handle kills worker/MFA descendants even on hard service exit."""

    def __init__(self, root, identifier, memory_limit=MAX_JOB_COMMIT_BYTES):
        if os.name != "nt":
            raise RuntimeError("Crash-safe CPU jobs currently require Windows.")
        self.handle = checked(kernel.CreateJobObjectW(None, job_name(root, identifier)))
        self.process = None
        try:
            limits = ExtendedLimits()
            # KILL_ON_JOB_CLOSE | JOB_MEMORY | ACTIVE_PROCESS; no child breakaway.
            limits.basic.flags, limits.basic.processes = 0x2000 | 0x200 | 0x8, 16
            limits.job_memory = memory_limit
            checked(
                kernel.SetInformationJobObject(
                    self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
                )
            )
        except BaseException:
            self.close()
            raise

    def spawn(self, command, env, temporary):
        gate = temporary / "worker-gate"
        process = subprocess.Popen(
            command,
            env={**env, "TAKETWO_WORKER_GATE": str(gate)},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        try:
            # Worker waits before importing engines or spawning any descendants.
            checked(kernel.AssignProcessToJobObject(self.handle, int(process._handle)))
            self.process = process
            gate.touch(exist_ok=False)
            return process
        except BaseException:
            process.kill()
            process.wait(timeout=15)
            raise

    def peak_commit_bytes(self):
        limits = ExtendedLimits()
        checked(
            kernel.QueryInformationJobObject(
                self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits), None
            )
        )
        return limits.peak_job_memory

    def stop(self):
        checked(kernel.TerminateJobObject(self.handle, 130))

    def close(self):
        if self.handle:
            checked(kernel.CloseHandle(self.handle))
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        try:
            self.stop()
            if self.process:
                self.process.wait(timeout=15)
        finally:
            self.close()
