"""Readiness failures cannot invent approvals or erase authoritative inventory."""

import sqlite3

from fastapi.testclient import TestClient

from taketwo.web.app import create_app


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
