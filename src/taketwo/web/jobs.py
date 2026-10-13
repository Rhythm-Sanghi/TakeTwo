"""Bounded local queue, SQLite history, supervised CPU process and tree cancellation."""

import logging
import os
import shutil
import sqlite3
import sys
import tempfile
import threading
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from taketwo.analysis.contracts import Diagnostic
from taketwo.dataset.schema import canonical_json, content_hash
from taketwo.dataset.storage import managed_path, read_json, safe_path

from .contracts import AnalysisRequest, Job
from .processes import ProcessTree, lease, stop_orphan
from .worker import atomic_json


def now():
    return datetime.now(UTC).isoformat()


class Jobs:
    def __init__(self, root: Path, alignment_config: Path | None, timeout_s=600.0):
        self.root, self.config, self.timeout_s = root, alignment_config, timeout_s
        self.path = managed_path(root, "application.sqlite3")
        self.lock = threading.RLock()
        self.wake = threading.Event()
        self.closing = threading.Event()
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS jobs "
                "(id TEXT PRIMARY KEY, identity TEXT NOT NULL, payload TEXT NOT NULL)"
            )
            db.execute("PRAGMA user_version=1")
        self.thread = threading.Thread(target=self.loop, name="taketwo-jobs", daemon=True)

    def recover(self):
        for job in self.list():
            if job.state in {"running", "queued"}:
                stop_orphan(self.root, job.id)
                job.state, job.stage = "failed", "interrupted"
                job.error = Diagnostic(
                    code="interrupted",
                    message="Service stopped before completion.",
                    recovery="Start a new analysis; completed artifacts were preserved.",
                )
                self.save(job)

    def connect(self):
        managed_path(self.root, "application.sqlite3")
        connection = sqlite3.connect(self.path, timeout=5)
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def start(self):
        self.recover()
        # The service lease is already held; no other supervisor can own these trees.
        with lease(self.root, ".dataset.lock"):
            runtime = managed_path(self.root, ".runtime")
            for directory in runtime.glob("taketwo-job-*"):
                safe_path(directory, root=self.root)
                if not directory.is_dir():
                    continue
                # Verify every deletion target before recursively removing managed temp data.
                for path in directory.rglob("*"):
                    safe_path(path, root=self.root)
                shutil.rmtree(directory)
        self.thread.start()

    def close(self):
        self.closing.set()
        self.wake.set()
        if self.thread.is_alive():
            self.thread.join(timeout=25)

    def list(self):
        with self.connect() as db:
            return [
                Job.model_validate_json(row[0])
                for row in db.execute("SELECT payload FROM jobs ORDER BY rowid DESC")
            ]

    def get(self, job_id):
        with self.connect() as db:
            row = db.execute("SELECT payload FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return Job.model_validate_json(row[0])

    def save(self, job):
        job.updated_at = now()
        with self.connect() as db:
            db.execute("UPDATE jobs SET payload=? WHERE id=?", (job.model_dump_json(), job.id))

    def submit(self, request: AnalysisRequest):
        with self.lock:
            active = [job for job in self.list() if job.state in {"queued", "running"}]
            for job in active:
                if job.request == request:
                    return job
            if len(active) >= 4:
                raise ValueError("Queue is full (one running and at most three waiting).")
            job = Job(
                id="j-" + uuid.uuid4().hex,
                request=request,
                state="queued",
                stage="queued",
                created_at=now(),
                updated_at=now(),
            )
            with self.connect() as db:
                db.execute(
                    "INSERT INTO jobs VALUES (?,?,?)",
                    (job.id, content_hash(request.model_dump(mode="json")), job.model_dump_json()),
                )
            self.wake.set()
            return job

    def cancel(self, job_id):
        with self.lock:
            job = self.get(job_id)
            if job.state not in {"queued", "running"}:
                raise ValueError("Only queued or running analyses can be cancelled.")
            job.cancel_requested = True
            if job.state == "queued":
                job.state, job.stage = "cancelled", "cancelled"
            self.save(job)
            self.wake.set()
            return job

    def loop(self):
        while not self.closing.is_set():
            pending = [job for job in reversed(self.list()) if job.state == "queued"]
            if not pending:
                self.wake.wait(0.5)
                self.wake.clear()
                continue
            self.execute(pending[0])

    def execute(self, job):
        with self.lock:
            job = self.get(job.id)
            if job.cancel_requested:
                return
            job.state, job.stage = "running", "validating"
            self.save(job)
        process, tree = None, None
        begin = time.monotonic()
        try:
            runtime = managed_path(self.root, ".runtime")
            runtime.mkdir(exist_ok=True)
            # Parent owns the dataset lock: forced worker termination cannot leave it stale.
            with (
                lease(self.root, ".dataset.lock"),
                tempfile.TemporaryDirectory(prefix="taketwo-job-", dir=runtime) as directory,
                ProcessTree(self.root, job.id) as tree,
            ):
                temporary = Path(directory)
                atomic_json(temporary / "request.json", job.request.model_dump(mode="json"))
                env = os.environ.copy()
                env.update(
                    TMP=directory,
                    TEMP=directory,
                    OMP_NUM_THREADS="1",
                    OPENBLAS_NUM_THREADS="1",
                    MKL_NUM_THREADS="1",
                )
                command = [sys.executable, "-m", "taketwo.web.worker", str(self.root), directory]
                if self.config:
                    command.append(str(self.config))
                process = tree.spawn(command, env, temporary)
                atomic_json(temporary / "worker.json", {"pid": process.pid})
                while process.poll() is None:
                    with self.lock:
                        job = self.get(job.id)
                        if job.cancel_requested or self.closing.is_set():
                            job.state, job.stage = "cancelled", "cancelled"
                            break
                        if time.monotonic() - begin >= self.timeout_s:
                            job.state, job.stage = "failed", "timeout"
                            job.error = Diagnostic(
                                code="timeout",
                                message="Analysis exceeded the local job time limit.",
                                recovery="Use a shorter excerpt or check aligner configuration.",
                            )
                            break
                        if (temporary / "stage.json").exists():
                            job.stage = read_json(temporary / "stage.json")["stage"]
                        self.save(job)
                    time.sleep(0.1)
                tree.stop()
                process.wait(timeout=15)
                job.elapsed_s = time.monotonic() - begin
                job.peak_commit_bytes = tree.peak_commit_bytes()
                with self.lock:
                    if (temporary / "artifacts.json").exists():
                        job.artifacts = read_json(temporary / "artifacts.json")
                    if job.state not in {"cancelled", "failed"}:
                        if process.returncode == 0 and (temporary / "result.json").exists():
                            result = read_json(temporary / "result.json")
                            job.artifacts, job.report_path = (
                                result["artifacts"],
                                result["report_path"],
                            )
                            job.state, job.stage = "completed", "completed"
                            job.stage_elapsed_s = result["stage_elapsed_s"]
                            job.cache_hits = result["cache_hits"]
                        else:
                            job.state, job.stage = "failed", "failed"
                            job.error = (
                                Diagnostic.model_validate_json(
                                    canonical_json(read_json(temporary / "error.json"))
                                )
                                if (temporary / "error.json").exists()
                                else Diagnostic(
                                    code="worker_failed",
                                    message="CPU worker exited without a report.",
                                    recovery="Check dataset integrity and retry.",
                                )
                            )
                    self.save(job)
        except Exception:
            # Keep filesystem/process details in the local operator log, never
            # in the public API diagnostic. Preserve the original exception.
            logging.getLogger(__name__).exception("CPU supervision failed for job %s", job.id)
            if tree and tree.handle:
                tree.stop()
            if process:
                process.wait(timeout=15)
            job.state, job.stage = "failed", "failed"
            job.error = Diagnostic(
                code="workspace_unavailable",
                message="Workspace is busy or storage is unavailable.",
                recovery="Finish other CLI operations and check local storage before retrying.",
            )
            self.save(job)
        finally:
            if tree:
                tree.close()
