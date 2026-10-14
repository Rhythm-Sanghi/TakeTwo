"""Readiness failures cannot invent approvals or erase authoritative inventory."""

import sqlite3

from fastapi.testclient import TestClient

from taketwo.dataset.storage import load
from taketwo.web.app import create_app
from taketwo.web.readiness import review_readiness


def test_review_database_failure_preserves_recording_inventory(imported, monkeypatch):
    root, _ = imported
    with TestClient(create_app(root)) as client:

        def fail():
            raise sqlite3.OperationalError("software lock fixture")

        monkeypatch.setattr(client.app.state.review_workspace, "inventory", fail)
        response = client.get("/api/v1/dataset")
        assert response.status_code == 200
        result = response.json()
        assert result["recordings"] == 1
        assert result["inventory_counts"]["reference_takes"] == 1
        assert "submitted_independent_assertions" not in result["inventory_counts"]
        assert result["review_readiness"] == []
        assert result["readiness_diagnostic"]["code"] == "review_evidence_unavailable"
        assert "software lock" not in response.text


def test_corrupt_review_does_not_become_zero_reviews(imported):
    root, _ = imported
    directory = root / "derived/comparison-v1"
    with TestClient(create_app(root)) as client:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "review-software-corrupt.json").write_text("{}", encoding="utf-8")
        result = client.get("/api/v1/dataset").json()
        assert result["recordings"] == 1
        assert result["inventory_counts"]["verified_transcripts"] == 0
        assert "timing_reviews" not in result["inventory_counts"]
        assert result["readiness_diagnostic"]


def test_empty_readiness_has_authoritative_zeros_and_no_failure(tmp_path):
    with TestClient(create_app(tmp_path / "empty")) as client:
        result = client.get("/api/v1/dataset").json()
        assert result["recordings"] == 0
        assert result["inventory_counts"]["submitted_independent_assertions"] == 0
        assert result["readiness_diagnostic"] is None


def test_readiness_agreement_is_structured_and_does_not_clear_rights(imported):
    root, recording = imported
    dataset = load(root)
    inventory = {
        "disagreements": [{"recording_id": recording.id, "scope": "transcript", "issue": None}]
    }
    hint = review_readiness(dataset, inventory, {})[0]
    assert hint.review_agreement == {"transcript": True, "timing": False, "flaws": False}
    assert hint.next_action == "rights"
    assert recording.provenance.rights.status == "pending"
    assert recording.transcript.status == "unverified"


def test_insufficient_review_agreement_cannot_promote_a_version(imported):
    root, recording = imported
    dataset = load(root)
    # Isolated generated-signal metadata, never an actual permission declaration.
    rights = recording.provenance.rights.model_copy(
        update={"status": "cleared", "permits_adaptation": True, "permits_redistribution": True}
    )
    member = recording.model_copy(
        update={"provenance": recording.provenance.model_copy(update={"rights": rights})}
    )
    dataset = dataset.model_copy(update={"recordings": [member]})
    inventory = {
        "disagreements": [
            {
                "recording_id": recording.id,
                "scope": "transcript",
                "issue": "At least two independent reviewers required",
            }
        ]
    }
    hint = review_readiness(dataset, inventory, {})[0]
    assert hint.review_agreement["transcript"] is False
    assert hint.next_action == "transcript"
    inventory["disagreements"][0]["issue"] = None
    hint = review_readiness(dataset, inventory, {})[0]
    assert hint.next_action == "reviewed_version"
    assert member.transcript.status == "unverified"
