"""Local import acceptance uses identified software signals, not human evidence."""

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from taketwo.dataset.schema import canonical_json
from taketwo.dataset.storage import load
from taketwo.dataset.validation import validate
from taketwo.web.app import create_app


@pytest.fixture
def local_client(tmp_path):
    with TestClient(create_app(tmp_path / "workspace")) as client:
        yield client


def signal_bytes(tmp_path, frequency=220, seconds=2):
    path = tmp_path / f"tone-{frequency}.wav"
    samples = 0.2 * np.sin(2 * np.pi * frequency * np.arange(int(16000 * seconds)) / 16000)
    sf.write(path, samples, 16000, subtype="PCM_16")
    return path.read_bytes()


def upload(client, data, recording_type="controlled_reference", **extra):
    return client.post(
        "/api/v1/recordings",
        files={"audio": ("fixture.wav", data, "audio/wav")},
        data={
            "metadata": canonical_json(
                {
                    "recording_type": recording_type,
                    "transcript": "Generated signal fixture only.",
                    "local_permission": True,
                    **extra,
                }
            )
        },
    )


@pytest.mark.parametrize(
    "kind,origin", [("public_reference", "source"), ("controlled_reference", "self_recorded")]
)
def test_minimal_reference_unknown_rights_and_real_derivation(local_client, tmp_path, kind, origin):
    response = upload(local_client, signal_bytes(tmp_path), kind)
    assert response.status_code == 201, response.text
    item = response.json()
    assert item["role"] == "reference" and item["origin"] == origin
    assert item["transcript"]["status"] == "unverified"
    assert item["speaker_id"] == "speaker-unassigned"
    assert item["original_info"]["duration_s"] == 2
    rights = item["provenance"]["rights"]
    assert rights["status"] == "pending" and rights["holder"] is None
    assert rights["license_name"] is None and rights["evidence"] is None
    assert not rights["permits_redistribution"]
    assert "Capture date unknown" in item["provenance"]["collection_method"]
    root = local_client.app.state.root
    report = validate(load(root), root, publication=True)
    assert not report["valid"]
    assert any(e["code"] == "rights_pending" for e in report["errors"])
    if origin == "self_recorded":
        assert "local storage/processing" in item["provenance"]["consent_evidence"]
        assert any(e["code"] == "pilot_missing" for e in report["errors"])


def test_human_participant_pair_and_identity_stay_unverified(local_client, tmp_path):
    reference = upload(
        local_client, signal_bytes(tmp_path), speaker_label="Fixture only voice"
    ).json()
    response = upload(
        local_client,
        signal_bytes(tmp_path, 270),
        "human_participant",
        reference_id=reference["id"],
        same_speaker_as_reference=True,
    )
    assert response.status_code == 201, response.text
    item = response.json()
    assert item["role"] == "participant" and item["origin"] == "self_recorded"
    assert item["speaker_id"] == reference["speaker_id"]
    assert item["family_id"] == reference["family_id"]
    assert item["provenance"]["work_id"] == reference["provenance"]["work_id"]
    pair = local_client.get("/api/v1/pairs").json()[0]
    assert pair["participant_id"] == item["id"] and pair["identity_status"] == "needs_review"


@pytest.mark.parametrize(
    "extra",
    [
        {"local_permission": False},
        {"recording_type": "synthetic"},
        {"recording_type": "human_participant"},
        {"same_speaker_as_reference": True},
        {
            "rights": {
                "status": "cleared",
                "holder": None,
                "license_name": None,
                "evidence": None,
                "attribution": None,
                "permits_adaptation": True,
                "permits_redistribution": True,
            }
        },
        {"source_url": "file:///private"},
        {"category": "pacing", "severity": 0},
    ],
)
def test_invalid_local_assertions_do_not_write(local_client, tmp_path, extra):
    response = upload(local_client, signal_bytes(tmp_path), **extra)
    assert response.status_code == 422, response.text
    assert not local_client.get("/api/v1/recordings").json()


def test_mismatch_duplicate_corruption_and_missing_provenance(local_client, tmp_path):
    data = signal_bytes(tmp_path)
    reference = upload(local_client, data).json()
    before = (local_client.app.state.root / "manifest.jsonl").read_bytes()
    mismatch = upload(
        local_client,
        signal_bytes(tmp_path, 300),
        "human_participant",
        reference_id=reference["id"],
        transcript="Different actual words.",
    )
    assert mismatch.status_code == 422 and "transcript_relationship" in mismatch.text
    assert upload(local_client, data).status_code == 409
    assert upload(local_client, b"damaged header").status_code == 422
    missing = local_client.post(
        "/api/v1/recordings",
        files={"audio": ("a.wav", data, "audio/wav")},
        data={"metadata": canonical_json({"metadata": {}})},
    )
    assert missing.status_code == 422
    duplicate_keys = local_client.post(
        "/api/v1/recordings",
        files={"audio": ("a.wav", data, "audio/wav")},
        data={"metadata": '{"local_permission":true,"local_permission":false}'},
    )
    assert duplicate_keys.status_code == 422
    assert (local_client.app.state.root / "manifest.jsonl").read_bytes() == before


def test_explicit_excerpt_preserves_original_and_native_sample_source(local_client, tmp_path):
    reference = upload(local_client, signal_bytes(tmp_path)).json()
    root = local_client.app.state.root
    original = (root / reference["original_path"]).read_bytes()
    request = {"start_s": 0.25, "end_s": 1.5, "transcript": "Generated fixture excerpt."}
    response = local_client.post(f"/api/v1/recordings/{reference['id']}/excerpt", json=request)
    assert response.status_code == 201, response.text
    result = response.json()
    assert result["origin"] == "self_recorded" and result["transcript"]["status"] == "unverified"
    assert result["normalized_info"]["frames"] == 20000
    assert "samples [4000,24000)" in result["provenance"]["collection_method"]
    a, _ = sf.read(root / reference["normalized_path"])
    b, _ = sf.read(root / result["normalized_path"])
    np.testing.assert_array_equal(a[4000:24000], b)
    assert (root / reference["original_path"]).read_bytes() == original
    assert (
        local_client.post(
            f"/api/v1/recordings/{reference['id']}/excerpt", json={**request, "end_s": 3}
        ).status_code
        == 422
    )


def test_pair_correction_new_version_preserves_old_manifest(local_client, tmp_path):
    a = upload(local_client, signal_bytes(tmp_path), title="First fixture reference").json()
    b = upload(local_client, signal_bytes(tmp_path, 330), title="Correct fixture reference").json()
    member = upload(
        local_client, signal_bytes(tmp_path, 280), "human_participant", reference_id=a["id"]
    ).json()
    pair = local_client.get("/api/v1/pairs").json()[0]
    root = local_client.app.state.root
    before = (root / "manifest.jsonl").read_bytes()
    response = local_client.post(
        f"/api/v1/pairs/{pair['id']}/correction", json={"reference_id": b["id"]}
    )
    assert response.status_code == 201, response.text
    target = Path(response.json()["workspace"])
    target.resolve().relative_to(root.resolve())
    dataset = load(target)
    assert dataset.dataset_version != load(root).dataset_version
    assert len(dataset.recordings) == 2 and len(dataset.pairs) == 1
    assert dataset.pairs[0].identity_status == "needs_review"
    assert {r.original_sha256 for r in dataset.recordings} == {
        b["original_sha256"],
        member["original_sha256"],
    }
    assert (root / "manifest.jsonl").read_bytes() == before


def test_old_manifest_serialization_is_unchanged(imported):
    root, _ = imported
    manifest = root / "manifest.jsonl"
    manifest.write_bytes(
        manifest.read_bytes().replace(b'"schema_version":2', b'"schema_version":1', 1)
    )
    before = (root / "manifest.jsonl").read_bytes()
    from taketwo.dataset.storage import manifest_text

    assert manifest_text(load(root)).encode() == before


def test_explicit_legacy_upgrade_retains_exact_backup(local_client, tmp_path):
    root = local_client.app.state.root
    manifest = root / "manifest.jsonl"
    manifest.write_bytes(
        manifest.read_bytes().replace(b'"schema_version":2', b'"schema_version":1', 1)
    )
    before = manifest.read_bytes()
    assert upload(local_client, signal_bytes(tmp_path)).status_code == 422
    assert manifest.read_bytes() == before
    response = local_client.post("/api/v1/dataset/upgrade", json={})
    assert response.status_code == 200 and response.json()["schema_version"] == 2
    backups = list((root / "history").glob("schema-v1-*.jsonl"))
    assert len(backups) == 1 and backups[0].read_bytes() == before
    assert local_client.post("/api/v1/dataset/upgrade", json={}).status_code == 200
    assert upload(local_client, signal_bytes(tmp_path)).status_code == 201


def completed_job(client, recording):
    import time

    job = client.post(
        "/api/v1/analyses", json={"reference_id": recording["id"], "align": False}
    ).json()
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        result = client.get("/api/v1/analyses/" + job["id"]).json()
        if result["state"] not in {"queued", "running"}:
            assert result["state"] == "completed", result
            return result
        time.sleep(0.1)
    raise AssertionError("Generated-signal job did not complete")


def test_report_snapshot_survives_unrelated_import_and_replays(local_client, tmp_path):
    from taketwo.comparison.storage import read_artifact, reproduce

    reference = upload(local_client, signal_bytes(tmp_path)).json()
    job = completed_job(local_client, reference)
    endpoint = "/api/v1/analyses/" + job["id"] + "/report"
    original = local_client.get(endpoint).json()
    assert upload(local_client, signal_bytes(tmp_path, 390)).status_code == 201
    assert local_client.get(endpoint).json() == original
    assert local_client.get("/api/v1/analyses/" + job["id"] + "/export").json() == original
    root = local_client.app.state.root
    stored = read_artifact(root / job["report_path"])
    assert reproduce(root, load(root), stored) == stored
    snapshot = root / "derived/comparison-v1" / ("dataset-" + stored.dataset_sha256 + ".json")
    snapshot.write_text("{}")
    assert local_client.get(endpoint).status_code == 409


def test_review_handoff_never_verifies_or_approves_automatically(local_client, tmp_path):
    from taketwo.analysis.storage import recording_input
    from taketwo.comparison.contracts import Review

    reference = upload(local_client, signal_bytes(tmp_path)).json()
    job = completed_job(local_client, reference)
    _, _, provenance = recording_input(local_client.app.state.root, reference["id"])
    review = Review(
        id="test-review-unresolved",
        scope="transcript",
        provenance=provenance,
        reviewer_id="fixture-only-reviewer",
        reviewed_on="2026-10-12",
        evidence_reference="TEST ONLY; no person or real listening",
        independent=False,
        blinded_to_predictions=False,
        decision="unresolved",
        notes="Software fixture only.",
        corrected_text=reference["transcript"]["text"],
    )
    response = local_client.post(
        "/api/v1/reviews/import",
        json={"job_id": job["id"], "review": review.model_dump(mode="json")},
    )
    assert response.status_code == 200, response.text
    assert response.json()["decision"] == "unresolved"
    assert (
        local_client.get("/api/v1/recordings/" + reference["id"]).json()["transcript"]["status"]
        == "unverified"
    )
    assert local_client.get("/api/v1/reviews").json()[0]["decision"] == "unresolved"


def test_launcher_reports_missing_build_and_busy_port_before_creating_workspace(tmp_path):
    import socket
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    command = [
        sys.executable,
        "-m",
        "taketwo.web.cli",
        "--workspace",
        str(tmp_path / "not-created"),
    ]
    missing = subprocess.run(
        command + ["--frontend", str(tmp_path / "no-build")],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert missing.returncode == 2 and "Built interface missing" in missing.stderr
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        busy = subprocess.run(
            command + ["--port", str(listener.getsockname()[1])],
            cwd=root,
            capture_output=True,
            text=True,
        )
    assert busy.returncode == 2 and "already in use" in busy.stderr
    assert not (tmp_path / "not-created").exists()
