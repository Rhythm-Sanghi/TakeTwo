"""Inventory is recording metadata, never independently authenticated people."""

from taketwo.dataset.schema import Dataset, Pair
from taketwo.dataset.workspace import summary
from taketwo.web.readiness import review_readiness


def test_participant_takes_speakers_and_connected_families(imported):
    _, reference = imported
    reference = reference.model_copy(update={"origin": "self_recorded"})
    takes = [
        reference.model_copy(update={"id": f"take-{i}", "role": "participant"}) for i in range(4)
    ]
    dataset = Dataset(dataset_version="test-v1", recordings=[reference, *takes])
    counts = summary(dataset)["inventory_counts"]
    assert counts["human_participant_takes"] == counts["participant_takes"] == 4
    assert counts["reference_takes"] == counts["distinct_speaker_ids"] == 1
    assert counts["connected_families"] == 1
    assert counts["verified_transcripts"] == 0
    takes[0].speaker_id = "another-declared-speaker"
    counts = summary(dataset)["inventory_counts"]
    assert counts["distinct_speaker_ids"] == 2
    assert counts["connected_families"] == 1  # Shared family/source/text still connects.


def test_empty_inventory_counts():
    counts = summary(Dataset(dataset_version="empty"))["inventory_counts"]
    assert counts and all(value == 0 for value in counts.values())


def test_connected_groups_do_not_count_unrelated_declared_speakers_as_one(imported):
    _, recording = imported
    other = recording.model_copy(deep=True)
    other.id, other.speaker_id, other.family_id = "other", "another-speaker", "another-family"
    other.provenance.source_id, other.provenance.work_id = "another-source", "another-work"
    other.transcript_sha256 = other.original_sha256 = other.sample_sha256 = "1" * 64
    counts = summary(Dataset(dataset_version="test-v1", recordings=[recording, other]))[
        "inventory_counts"
    ]
    assert counts["distinct_speaker_ids"] == counts["connected_families"] == 2


def test_readiness_advances_only_from_existing_evidence_status(imported):
    # Synthetic status inputs exercise presentation only, never publish human assertions.
    _, recording = imported
    recording = recording.model_copy(deep=True)
    dataset = Dataset(dataset_version="test-v1", recordings=[recording])
    inventory = {"disagreements": []}

    def current(processing=None):
        return review_readiness(dataset, inventory, processing or {})[0]

    assert current().next_action == "rights"
    recording.provenance.rights.status = "cleared"
    assert current().next_action == "transcript"
    inventory["disagreements"] = [
        {"recording_id": recording.id, "scope": "transcript", "issue": "Two reviewers needed"}
    ]
    assert current().next_action == "transcript"
    inventory["disagreements"][0]["issue"] = None
    assert current().next_action == "reviewed_version"
    assert recording.transcript.status == "unverified"
    recording.transcript.status = "verified"
    assert current().next_action == "processing"
    assert current({recording.id: "job"}).next_action == "timing"
    inventory["disagreements"].append(
        {"recording_id": recording.id, "scope": "timing", "issue": None}
    )
    assert current({recording.id: "job"}).next_action == "comparison"
    inventory["disagreements"][-1]["issue"] = "Stale/invalid evidence"
    assert current({recording.id: "job"}).next_action == "timing"
    inventory["disagreements"][-1]["issue"] = None
    dataset.pairs = [
        Pair(
            id="fixture-pair",
            reference_id="fixture-reference",
            participant_id=recording.id,
            transcript_sha256=recording.transcript_sha256,
            intended_flaw="unspecified",
            intended_severity=None,
            identity_status="needs_review",
        )
    ]
    assert current({recording.id: "job"}).next_action == "flaws"
    inventory["disagreements"].append(
        {"recording_id": recording.id, "scope": "flaws", "issue": "Numerical inventory unresolved"}
    )
    assert current({recording.id: "job"}).review_scope == "flaws"
    inventory["disagreements"][-1]["issue"] = None
    assert current({recording.id: "job"}).next_action == "comparison"


def test_dataset_api_counts_and_navigation_do_not_create_sessions(imported):
    from fastapi.testclient import TestClient

    from taketwo.web.app import create_app

    root, recording = imported
    app = create_app(root)
    with TestClient(app) as client:
        response = client.get("/api/v1/dataset")
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_counts"]["submitted_independent_assertions"] == 0
        assert data["inventory_counts"]["verified_transcripts"] == 0
        assert data["review_readiness"][0]["next_action"] == "rights"
        assert app.state.review_workspace.inventory()["sessions"] == []
        assert (
            client.post(
                "/api/v1/review-workspace/sessions",
                json={
                    "recording_id": recording.id,
                    "reviewer_id": "fixture-only",
                    "scope": "transcript",
                },
            ).status_code
            == 403
        )


def test_unverified_inventory_does_not_parse_unneeded_processing_history(imported, monkeypatch):
    from types import SimpleNamespace

    from fastapi.testclient import TestClient

    from taketwo.web.app import create_app

    root, recording = imported
    app = create_app(root)
    with TestClient(app) as client:
        job = SimpleNamespace(id="software-only", state="completed", artifacts={recording.id: {}})
        monkeypatch.setattr(app.state.jobs, "list", lambda: [job])

        def unexpected_read(*_):
            raise AssertionError("Unverified inventory must not parse completed acoustic artifacts")

        monkeypatch.setattr(app.state.jobs, "get", unexpected_read)
        response = client.get("/api/v1/dataset")
        assert response.status_code == 200
        assert response.json()["review_readiness"][0]["next_action"] == "rights"
