"""HTTP/lifecycle tests use generated signals, never real-speech accuracy claims."""

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from fastapi.testclient import TestClient

from taketwo.dataset.schema import canonical_json
from taketwo.web.app import create_app, window
from taketwo.web.contracts import AnalysisRequest
from taketwo.web.jobs import Jobs


def test_concurrent_cold_validation_reads_once_and_retries_changed_or_failed_inputs(monkeypatch):
    import taketwo.web.app as web

    calls = []
    sentinel = object()

    def read(path):
        calls.append(path)
        time.sleep(0.05)  # Hold a cache miss while the other requests arrive.
        return sentinel

    monkeypatch.setattr(web, "read_analysis", read)
    barrier = Barrier(6)

    def request(_):
        barrier.wait()
        return web.validated_analysis("software-concurrent-cache-probe", 1, 100)

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(request, range(6)))
    assert all(result is sentinel for result in results)
    assert len(calls) == 1
    assert web.validated_analysis("software-concurrent-cache-probe", 2, 101) is sentinel
    assert len(calls) == 2  # The existing stat key still invalidates changed artifacts.

    def failed(path):
        calls.append(path)
        raise ValueError("Software corruption probe")

    monkeypatch.setattr(web, "read_analysis", failed)
    for _ in range(2):
        with pytest.raises(ValueError, match="corruption probe"):
            web.validated_analysis("software-concurrent-cache-probe", 3, 102)
    assert len(calls) == 4  # Failure is never cached as successful evidence.


@pytest.fixture
def client(imported):
    root, recording = imported
    with TestClient(create_app(root)) as client:
        yield client, root, recording


def wait_job(client, identifier, timeout=60):
    begin = time.monotonic()
    while time.monotonic() - begin < timeout:
        job = client.get(f"/api/v1/analyses/{identifier}").json()
        if job["state"] not in {"running", "queued"}:
            return job
        time.sleep(0.1)
    raise AssertionError("Job failed to finish within test deadline.")


def test_health_metadata_pairs_and_private_errors(client):
    client, _, recording = client
    health = client.get("/api/v1/health").json()
    assert health["product"] == "TakeTwo" and health["worker_concurrency"] == 1
    assert not health["alignment_configured"]
    assert client.get("/api/v1/recordings").json()[0]["id"] == recording.id
    assert (
        client.get(f"/api/v1/recordings/{recording.id}/transcript").json()["status"] == "unverified"
    )
    assert client.get("/api/v1/pairs").json() == []
    assert client.get("/api/v1/dataset").json()["competition_dataset_complete"] is False
    assert client.get("/api/v1/recordings/missing").status_code == 404
    response = client.post("/api/v1/analyses", json={"reference_id": "private secret transcript!"})
    assert response.status_code == 422
    assert "private secret" not in response.text


def test_audio_range_and_waveform_sample_coordinates(client):
    client, _, recording = client
    response = client.get(
        f"/api/v1/recordings/{recording.id}/audio", headers={"Range": "bytes=0-43"}
    )
    assert response.status_code == 206 and len(response.content) == 44
    assert response.content[:4] == b"RIFF"
    waveform = client.get(
        f"/api/v1/recordings/{recording.id}/waveform?start_s=0.5&end_s=0.75&bins=10"
    ).json()
    assert waveform["bins"][0][0] == 8000 and waveform["bins"][-1][1] == 12000
    assert all(low == high == 0 for _, _, low, high in waveform["bins"])
    assert client.get(f"/api/v1/recordings/{recording.id}/waveform?bins=5001").status_code == 422
    assert client.get(f"/api/v1/recordings/{recording.id}/waveform?start_s=inf").status_code == 422
    assert (
        client.get(f"/api/v1/recordings/{recording.id}/waveform?start_s=4&end_s=5").status_code
        == 422
    )


@pytest.mark.parametrize(
    "mime,data,expected", [("text/html", b"<html/>", 415), ("audio/wav", b"not audio", 422)]
)
def test_reject_upload_content(client, metadata, mime, data, expected):
    client, _, _ = client
    response = client.post(
        "/api/v1/recordings",
        files={"audio": ("recording.wav", data, mime)},
        data={"metadata": canonical_json({"metadata": metadata})},
    )
    assert response.status_code == expected


def test_upload_duplicate_and_metadata_validation(client, audio_path, metadata):
    client, root, _ = client
    before = (root / "manifest.jsonl").read_bytes()
    response = client.post(
        "/api/v1/recordings",
        files={"audio": ("../../unsafe name.wav", audio_path.read_bytes(), "audio/wav")},
        data={"metadata": canonical_json({"metadata": metadata})},
    )
    assert response.status_code == 409 and response.json()["error"]["code"] == "duplicate_audio"
    assert (root / "manifest.jsonl").read_bytes() == before
    response = client.post(
        "/api/v1/recordings",
        files={"audio": ("recording.wav", audio_path.read_bytes(), "audio/wav")},
        data={"metadata": "{}"},
    )
    assert response.status_code == 422 and "metadata" in response.text


def test_origin_host_length_limits(client):
    client, _, recording = client
    assert (
        client.post(
            "/api/v1/analyses",
            json={"reference_id": recording.id},
            headers={"origin": "https://untrusted.invalid"},
        ).status_code
        == 403
    )
    assert client.get("/api/v1/health", headers={"host": "untrusted.invalid"}).status_code == 400
    assert (
        client.post(
            "/api/v1/analyses", content=b"{}", headers={"content-length": str(102 * 1024 * 1024)}
        ).status_code
        == 413
    )


def test_real_generated_signal_job_report_export_and_cache(client):
    client, root, recording = client
    response = client.post("/api/v1/analyses", json={"reference_id": recording.id, "align": False})
    assert response.status_code == 202
    job = wait_job(client, response.json()["id"])
    assert job["state"] == "completed", job
    report = client.get(f"/api/v1/analyses/{job['id']}/report").json()
    assert report["overall_score"] is None and report["regions"] == []
    assert report["inputs"][0]["spectral_frame_count"] == 198
    overlay = client.get(f"/api/v1/analyses/{job['id']}/overlay").json()
    assert overlay["reference_values"] == [] and overlay["unavailable_reason"]
    assert any(r["code"] == "pair_missing" for r in report["eligibility"]["reasons"])
    features = client.get(
        f"/api/v1/analyses/{job['id']}/features/{recording.id}?max_points=12"
    ).json()
    assert len(features["values"]) <= 12 and features["unit"] == "full_scale"
    assert client.get(f"/api/v1/analyses/{job['id']}/features/not-a-member").status_code == 409
    assert client.get(f"/api/v1/analyses/{job['id']}/export").json() == report
    csv = client.get(f"/api/v1/analyses/{job['id']}/export?format=csv")
    assert csv.status_code == 200 and csv.text.startswith("region_id,")
    assert client.post(f"/api/v1/analyses/{job['id']}/cancel", json={}).status_code == 409
    second = client.post(
        "/api/v1/analyses", json={"reference_id": recording.id, "align": False}
    ).json()
    replay = wait_job(client, second["id"])
    assert replay["report_path"] == job["report_path"] and replay["artifacts"] == job["artifacts"]
    path = root / job["artifacts"][recording.id]["features"]
    payload = json.loads(path.read_text())
    payload["result"]["quality"]["peak"] += 1
    path.write_text(json.dumps(payload))
    assert client.get(f"/api/v1/analyses/{job['id']}/features/{recording.id}").status_code == 422


def test_queue_dedup_bounded_cancel_restart(imported):
    root, recording = imported
    jobs = Jobs(root, None)
    request = AnalysisRequest(reference_id=recording.id, align=False)
    first = jobs.submit(request)
    assert jobs.submit(request).id == first.id
    assert jobs.cancel(first.id).state == "cancelled"
    for i in range(4):
        jobs.submit(AnalysisRequest(reference_id=f"test-{i}"))
    with pytest.raises(ValueError, match="full"):
        jobs.submit(AnalysisRequest(reference_id="test-5"))
    restarted = Jobs(root, None)
    restarted.recover()
    assert all(j.state not in {"running", "queued"} for j in restarted.list())
    assert sum(j.error is not None and j.error.code == "interrupted" for j in restarted.list()) == 4


@pytest.mark.parametrize("action", ["cancel", "timeout"])
def test_running_cancel_timeout_releases_lock_and_cleanup(imported, action):
    root, recording = imported
    app = create_app(root, timeout_s=0.15 if action == "timeout" else 60)
    with TestClient(app) as client:
        job = client.post(
            "/api/v1/analyses", json={"reference_id": recording.id, "align": False}
        ).json()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            running = client.get(f"/api/v1/analyses/{job['id']}").json()
            if running["state"] == "running":
                break
            time.sleep(0.01)
        if action == "cancel":
            assert client.post(f"/api/v1/analyses/{job['id']}/cancel", json={}).status_code == 202
        final = wait_job(client, job["id"])
        assert final["state"] == ("cancelled" if action == "cancel" else "failed")
        if action == "timeout":
            assert final["error"]["code"] == "timeout"
        assert not (root / ".dataset.lock").exists()
        assert not list((root / ".runtime").iterdir())
    assert not (root / ".service.lock").exists()


def test_gap_preserving_bounded_plot_downsampling():
    from taketwo.analysis.contracts import Series

    series = Series(
        unit="Hz",
        frame_length=1024,
        hop_length=160,
        start_samples=list(range(100)),
        times_s=[float(i) for i in range(100)],
        values=[None if i % 7 == 0 else float(i) for i in range(100)],
    )
    times, values, aggregation = window(series, 0, 100, 12)
    assert len(values) <= 12 and None in values
    assert aggregation == "min_max_with_gap_markers" and times == sorted(times)


def test_openapi_contract_snapshot():
    import runpy

    contract = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/export_api.py"))[
        "contract"
    ]

    saved = json.loads((Path(__file__).resolve().parents[1] / "docs/api-v1.json").read_text())
    assert saved == contract()


def test_symlink_workspace_rejected(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Windows host cannot create symlinks.")
    with pytest.raises(Exception, match="Symlinks"):
        create_app(link)


def test_atomic_stage_publication_retries_windows_sharing_violation(tmp_path, monkeypatch):
    import taketwo.web.worker as worker

    path = tmp_path / "stage.json"
    path.write_text('{"stage":"old"}')
    replace = worker.os.replace
    attempts, delays = [], []

    def briefly_locked(source, target):
        attempts.append(target)
        if len(attempts) < 3:
            assert json.loads(path.read_text()) == {"stage": "old"}
            raise PermissionError("test-only sharing violation")
        replace(source, target)

    monkeypatch.setattr(worker.os, "replace", briefly_locked)
    monkeypatch.setattr(worker.time, "sleep", delays.append)
    worker.atomic_json(path, {"stage": "extracting"})
    assert len(attempts) == 3 and delays == [0.05, 0.05]
    assert json.loads(path.read_text()) == {"stage": "extracting"}
    assert not path.with_suffix(".tmp").exists()


def test_readiness_rejects_jobs_when_supervisor_stopped(client):
    client, _, recording = client
    client.app.state.jobs.close()
    assert client.get("/api/v1/health").json()["ready"] is False
    response = client.post("/api/v1/analyses", json={"reference_id": recording.id})
    assert response.status_code == 503


def test_exploratory_http_exports_preserve_formal_report(client, monkeypatch):
    import taketwo.web.app as module

    original_build = module.build_exploratory
    builds = []

    def counted_build(*args, **kwargs):
        builds.append(kwargs["job_id"])
        return original_build(*args, **kwargs)

    monkeypatch.setattr(module, "build_exploratory", counted_build)
    client, root, recording = client
    response = client.post("/api/v1/analyses", json={"reference_id": recording.id, "align": False})
    assert response.status_code == 202
    identifier = response.json()["id"]
    wait_job(client, identifier)
    base = f"/api/v1/analyses/{identifier}"
    before = client.get(base + "/report").json()
    original_publish = module.publish_exploratory

    def unavailable_publish(*args):
        raise OSError("test-only publication failure")

    monkeypatch.setattr(module, "publish_exploratory", unavailable_publish)
    assert client.get(base + "/exploratory").status_code == 503
    monkeypatch.setattr(module, "publish_exploratory", original_publish)
    response = client.get(base + "/exploratory")
    assert response.status_code == 200
    result = response.json()
    assert result["reference_id"] == recording.id and result["pair_id"] is None
    assert result["recordings"][0]["duration_s"] == 2
    assert result["comparison"] is None
    assert "scores" not in result
    exported = client.get(base + "/exploratory/export").json()
    from taketwo.dataset.schema import content_hash

    assert exported["sha256"] == content_hash(result)
    assert exported["result"] == result
    intervals = client.get(base + "/exploratory/export?format=csv")
    assert intervals.status_code == 200
    assert "recording_id,kind,start_s,end_s" in intervals.text
    assert "automatic_unverified" in intervals.text
    assert client.get(base + "/exploratory/export?format=html").status_code == 422
    assert client.get("/api/v1/analyses/missing/exploratory").status_code == 404
    assert client.get(base + "/report").json() == before
    assert len(list((root / "derived/exploratory-v1").glob("exploratory-*.json"))) == 1
    assert builds == [identifier, identifier]  # Failed publication did not enter the cache.
    restarted = TestClient(create_app(root))
    assert restarted.get(base + "/exploratory").json() == result
    assert builds == [identifier, identifier, identifier]
    # A cached summary never bypasses current source identity checks.
    audio = root / recording.normalized_path
    audio.write_bytes(b"corrupt test input")
    assert client.get(base + "/exploratory").status_code == 422


def test_comparative_cache_integrity_restoration_and_distinct_artifact_errors(client, monkeypatch):
    import csv
    import io

    import taketwo.web.app as module
    from taketwo.dataset.schema import content_hash

    client, root, recording = client
    job = client.post(
        "/api/v1/analyses", json={"reference_id": recording.id, "align": False}
    ).json()
    job = wait_job(client, job["id"])
    base = f"/api/v1/analyses/{job['id']}"
    formal = client.get(base + "/report").json()
    calls = []
    original = module.build_insights

    def counted(*args):
        calls.append(True)
        return original(*args)

    monkeypatch.setattr(module, "build_insights", counted)
    result = client.get(base + "/insights").json()
    assert result["exploratory"]["reference_id"] == recording.id
    assert result["segments"] == [] and result["correspondence_unavailable_reason"]
    assert client.get(base + "/insights").json() == result and len(calls) == 1
    exported = client.get(base + "/insights/export").json()
    assert exported == {"sha256": content_hash(result), "result": result}
    rows = list(
        csv.DictReader(io.StringIO(client.get(base + "/exploratory/export?format=csv").text))
    )
    assert [r["candidate_id"] for r in rows] == [
        c["id"] for c in result["exploratory"]["candidates"]
    ]
    assert client.get(base + "/report").json() == formal
    restarted = TestClient(create_app(root))
    assert restarted.get(base + "/insights").json() == result and len(calls) == 2
    stored = next((root / "derived/comparative-insights-v1").glob("insights-*.json"))
    original_bytes = stored.read_bytes()
    stored.write_bytes(b"corrupted fixture")
    corrupted = client.get(base + "/insights")
    assert corrupted.status_code == 422
    assert corrupted.json()["error"]["code"] == "artifact_corrupt"
    assert "Restore" in corrupted.json()["error"]["recovery"]
    stored.write_bytes(original_bytes)
    features = root / job["artifacts"][recording.id]["features"]
    original_bytes = features.read_bytes()
    features.unlink()
    missing = client.get(base + "/insights")
    assert missing.status_code == 404 and missing.json()["error"]["code"] == "artifact_missing"
    features.write_bytes(b"corrupted fixture")
    corrupt = client.get(base + "/insights")
    assert corrupt.status_code == 422 and corrupt.json()["error"]["code"] == "artifact_corrupt"
    features.write_bytes(original_bytes)
    assert client.get(base + "/insights").json() == result
    assert client.get("/api/v1/analyses/no-job/insights").json()["error"]["code"] == "not_found"
