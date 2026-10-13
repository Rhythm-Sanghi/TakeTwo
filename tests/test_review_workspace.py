"""Review lifecycle software fixtures; never genuine reviewer evidence."""

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from taketwo.analysis.contracts import AlignmentConfig, AlignmentResult, Interval, Resource
from taketwo.analysis.storage import publish as publish_alignment
from taketwo.analysis.storage import recording_input
from taketwo.comparison.contracts import Review
from taketwo.comparison.reviews import consensus
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import Pair, canonical_json, content_hash
from taketwo.dataset.storage import load, save
from taketwo.web.app import create_app
from taketwo.web.review_contracts import DraftSave, ListeningEvent, ReviewAssignment, ReviewDraft
from taketwo.web.review_workspace import ReviewWorkspace


@pytest.fixture
def workspace(imported):
    root, recording = imported
    jobs = SimpleNamespace(list=lambda: [], get=lambda _: SimpleNamespace(artifacts={}))
    return ReviewWorkspace(root, jobs), recording


def draft(session, **updates):
    return session.draft.model_copy(
        update={
            "notes": "Software fixture ONLY; not human review.",
            "evidence_reference": "pytest:test_review_workspace.py",
            "independent": True,
            **updates,
        }
    )


def save_draft(workspace, session, value):
    return workspace.save(session.id, DraftSave(revision=session.edit_revision, draft=value))


def listen_fixture(workspace, sid, monkeypatch):
    # Simulated clock and listening are ONLY permitted in isolated software tests.
    with workspace.db() as db:
        last = db.execute("SELECT heartbeat FROM sessions WHERE id=?", (sid,)).fetchone()[0]
    monkeypatch.setattr("taketwo.web.review_workspace.time.time", lambda: last + 2)
    return workspace.listen(sid, ListeningEvent(start_s=0.0, end_s=2.0))


def test_transcript_draft_restart_edit_conflict_and_no_auto_approval(workspace):
    ws, recording = workspace
    grant = ws.create(
        ReviewAssignment(recording_id=recording.id, reviewer_id="test-a", scope="transcript")
    )
    session = ws.get(grant.session_id)
    assert not ws.validation(session).can_submit
    value = draft(session, corrected_text="Generated corrected signal fixture only.")
    edited = save_draft(ws, session, value)
    restarted = ReviewWorkspace(ws.root, ws.jobs)
    assert restarted.active() == session.id
    assert restarted.get(session.id).draft == edited.draft
    assert restarted.validation(edited).alignment_needs_regeneration
    assert restarted.reviews() == []
    with pytest.raises(Exception, match="another tab"):
        save_draft(ws, session, value)


def test_submission_immutability_export_contract_and_revision(workspace, monkeypatch):
    ws, recording = workspace
    grant = ws.create(
        ReviewAssignment(recording_id=recording.id, reviewer_id="test-a", scope="transcript")
    )
    session = listen_fixture(ws, grant.session_id, monkeypatch)
    session = save_draft(ws, session, draft(session, decision="approved"))
    assert ws.validation(session).can_submit
    submitted = ws.submit(session.id, session.edit_revision)
    assert submitted.review.decision == "approved"
    assert Review.model_validate_json(submitted.review.model_dump_json()) == submitted.review
    with pytest.raises(Exception, match="immutable"):
        save_draft(ws, submitted, submitted.draft)
    assert ws.submit(submitted.id, submitted.edit_revision) == submitted
    ws.unlock()
    revised = ws.create(
        ReviewAssignment(
            recording_id=recording.id,
            reviewer_id="test-a",
            scope="transcript",
            supersedes=submitted.id,
        )
    )
    session = ws.get(revised.session_id)
    assert session.draft.decision == "unresolved" and not session.draft.independent
    assert ws.reviews()[0] == submitted.review
    assert not ws.validation(session).can_submit


def timing_fixture(ws, recording):
    _, _, provenance = recording_input(ws.root, recording.id)
    resource = Resource(
        path="software-fixture",
        sha256="0" * 64,
        version="fixture",
        license="fixture",
        source_url="https://example.invalid",
    )
    alignment = AlignmentResult(
        provenance=provenance,
        config=AlignmentConfig(
            command=["fixture"], expected_version="fixture", model=resource, dictionary=resource
        ),
        duration_s=2.0,
        original_text=recording.transcript.text,
        normalized_tokens=recording.tokens,
        token_offsets=recording.token_offsets,
        status="succeeded",
        words=[
            Interval(start_s=i * 0.4, end_s=i * 0.4 + 0.3, label=t, token_index=i)
            for i, t in enumerate(recording.tokens)
        ],
        phones=[],
        diagnostics=[],
        oov=[],
    )
    path = publish_alignment(ws.root, alignment)
    ws.jobs.get = lambda _: SimpleNamespace(
        artifacts={recording.id: {"alignment": path.relative_to(ws.root).as_posix()}}
    )
    grant = ws.create(
        ReviewAssignment(
            recording_id=recording.id, reviewer_id="test-a", scope="timing", job_id="test-job"
        )
    )
    return ws.get(grant.session_id), alignment, path


def test_timing_inspection_edit_invalidation_and_phrase_partition(workspace, monkeypatch):
    ws, recording = workspace
    session, alignment, _ = timing_fixture(ws, recording)
    assert session.draft.words == []  # No silent machine-to-human transfer.
    session = listen_fixture(ws, session.id, monkeypatch)
    session = save_draft(
        ws, session, draft(session, words=alignment.words, phrase_spans=[(0, 2), (2, 4)])
    )
    for index in range(4):
        session = ws.inspect(session.id, index)
    assert ws.validation(session).can_submit
    words = list(session.draft.words)
    words[1] = words[1].model_copy(update={"start_s": 0.41})
    session = save_draft(ws, session, session.draft.model_copy(update={"words": words}))
    assert session.inspected_words == [0, 2, 3]
    assert not ws.validation(session).can_submit
    assert ws.alignment(session.assignment) == alignment


@pytest.mark.parametrize("start,end", [(-0.1, 0.2), (0.4, 0.4), (0.1, 0.5), (1.5, 2.1)])
def test_invalid_timing(workspace, start, end):
    ws, recording = workspace
    session, alignment, _ = timing_fixture(ws, recording)
    payload = draft(session, words=alignment.words, phrase_spans=[(0, 4)]).model_dump(mode="json")
    payload["words"][1].update(start_s=start, end_s=end)
    with pytest.raises(ValueError):
        request = DraftSave.model_validate_json(
            canonical_json({"revision": session.edit_revision, "draft": payload})
        )
        ws.save(session.id, request)


def test_stale_alignment_and_changed_recording_fail_closed(workspace):
    ws, recording = workspace
    session, alignment, path = timing_fixture(ws, recording)
    envelope = json.loads(path.read_text(encoding="utf-8"))
    envelope["result"]["words"][0]["end_s"] = 0.31
    path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(ValueError, match="hash"):
        ws.check_current(session)
    path.write_text(
        canonical_json(
            {
                "sha256": content_hash(alignment.model_dump(mode="json")),
                "result": alignment.model_dump(mode="json"),
            }
        ),
        encoding="utf-8",
    )
    dataset = load(ws.root)
    dataset.recordings[0].transcript.text += " Edited."
    save(ws.root, dataset)
    with pytest.raises((ValueError, DatasetError)):
        ws.check_current(session)


def test_flaw_crud_blinding_coverage_and_uncertainty(workspace, monkeypatch):
    ws, recording = workspace
    dataset = load(ws.root)
    dataset.recordings[0].role = "participant"
    dataset.pairs.append(
        Pair(
            id="test-pair",
            reference_id="test-other-reference",
            participant_id=recording.id,
            transcript_sha256=recording.transcript_sha256,
            intended_flaw="pacing",
            intended_severity=3,
            identity_status="needs_review",
        )
    )
    save(ws.root, dataset)
    grant = ws.create(
        ReviewAssignment(
            recording_id=recording.id, reviewer_id="test-a", scope="flaws", pair_id="test-pair"
        )
    )
    session = ws.get(grant.session_id)
    assert session.machine_text is None and session.suggestions == []
    assert session.recording_name == "Assigned recording"
    payload = draft(session, blinded_to_predictions=True).model_dump(mode="json")
    payload["labels"] = [
        {
            "id": "test-label",
            "category": "pause_behavior",
            "severity": 1,
            "interval": None,
            "anchor_s": 1.0,
            "rationale": "software fixture missing pause",
            "uncertainty_s": 0.1,
        }
    ]
    session = save_draft(ws, session, ReviewDraft.model_validate_json(canonical_json(payload)))
    assert not ws.validation(session).can_submit
    payload["labels"][0]["severity"] = 2
    session = save_draft(ws, session, ReviewDraft.model_validate_json(canonical_json(payload)))
    assert session.draft.labels[0].severity == 2
    session = save_draft(ws, session, session.draft.model_copy(update={"labels": []}))
    session = listen_fixture(ws, session.id, monkeypatch)
    assert ws.validation(session).can_submit


def test_blind_api_isolation_and_owner_recovery(imported):
    root, recording = imported
    app = create_app(root)
    with TestClient(app) as client:
        operator = (root / ".review-operator-key").read_text()
        assert (
            client.post(
                "/api/v1/review-workspace/sessions",
                json={"recording_id": recording.id, "reviewer_id": "test-a", "scope": "transcript"},
            ).status_code
            == 403
        )
        grant = client.post(
            "/api/v1/review-workspace/sessions",
            headers={"X-Review-Operator": operator},
            json={"recording_id": recording.id, "reviewer_id": "test-a", "scope": "transcript"},
        ).json()
        sid, token = grant["session_id"], grant["access_token"]
        for path in [
            "reviews",
            "dataset",
            "recordings",
            "pairs",
            "analyses",
            "evaluations",
            "rubrics/delivery-v0",
            "review-workspace/inventory",
            f"recordings/{recording.id}/audio",
            "analyses/other/report",
        ]:
            assert (
                client.get(f"/api/v1/{path}", headers={"X-Review-Operator": operator}).status_code
                == 403
            ), path
        assert client.get("/openapi.json").status_code == 403
        assert client.get(f"/api/v1/review-workspace/{sid}").status_code == 403
        assert (
            client.post(
                f"/api/v1/review-workspace/{sid}/activate", json={"access_token": "wrong"}
            ).status_code
            == 403
        )
        activated = client.post(
            f"/api/v1/review-workspace/{sid}/activate", json={"access_token": token}
        )
        assert activated.status_code == 200
        assert "HttpOnly" in activated.headers["set-cookie"]
        assert token not in activated.text
        assert (
            client.get(
                f"/api/v1/review-workspace/{sid}/audio", headers={"Range": "bytes=0-43"}
            ).status_code
            == 206
        )
        assert client.get(f"/api/v1/review-workspace/{sid}/export").status_code == 409
        assert client.get("/api/v1/review-workspace/other").status_code == 403
        assert (
            client.post(
                "/api/v1/review-workspace/unlock", json={"operator_key": "wrong"}
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/v1/review-workspace/unlock", json={"operator_key": operator}
            ).status_code
            == 200
        )
        assert client.get(f"/api/v1/review-workspace/{sid}").status_code == 403
        assert client.get("/api/v1/reviews").json() == []
        resumed = client.post(
            f"/api/v1/review-workspace/{sid}/resume", headers={"X-Review-Operator": operator}
        ).json()
        assert resumed["access_token"] != token
        assert (
            client.post(
                f"/api/v1/review-workspace/{sid}/activate", json={"access_token": token}
            ).status_code
            == 403
        )


def test_adjudication_preserves_disagreement_and_eligibility(workspace, monkeypatch):
    ws, recording = workspace
    reviews = []
    for reviewer, text in [
        ("test-a", recording.transcript.text),
        ("test-b", "Different fixture words."),
    ]:
        grant = ws.create(
            ReviewAssignment(recording_id=recording.id, reviewer_id=reviewer, scope="transcript")
        )
        s = listen_fixture(ws, grant.session_id, monkeypatch)
        s = save_draft(ws, s, draft(s, decision="approved", corrected_text=text))
        reviews.append(ws.submit(s.id, s.edit_revision).review)
        ws.unlock()
    from taketwo.web.review_contracts import Adjudication

    decision = ws.adjudicate(
        Adjudication(
            recording_id=recording.id,
            scope="transcript",
            review_ids=[r.id for r in reviews],
            adjudicator_id="test-adjudicator",
            explanation="Software test: token disagreement",
            resolution="Reviewers must independently revisit the text.",
        )
    )
    assert decision["status"] == "awaiting_reviewer_revisions"
    assert consensus(ws.reviews(), "transcript")[1]
    assert load(ws.root).recordings[0].transcript.status == "unverified"
    assert ws.inventory()["decisions"][0] == decision


def test_flaw_adjudication_cannot_resolve_boundary_sensitive_truth(workspace):
    from taketwo.comparison.contracts import Label, Span
    from taketwo.comparison.storage import publish
    from taketwo.web.review_contracts import Adjudication

    ws, recording = workspace
    _, _, provenance = recording_input(ws.root, recording.id)
    reviews = [
        Review(
            id=f"fixture-review-{i}",
            reviewer_id=f"fixture-reviewer-{i}",
            scope="flaws",
            provenance=provenance,
            pair_id="fixture-pair",
            reviewed_on="2026-10-13",
            independent=True,
            blinded_to_predictions=True,
            decision="approved",
            notes="Software fixture only",
            evidence_reference="pytest generated signal",
            reviewed_spans=[Span(start_s=0, end_s=2)],
            labels=[
                Label(
                    id=f"fixture-label-{i}",
                    category="pacing",
                    severity=1,
                    interval=Span(start_s=0.2 * i, end_s=1 + 0.2 * i),
                    rationale="Fixture only",
                )
            ],
        )
        for i in range(2)
    ]
    for review in reviews:
        publish(ws.root, review)
    assert consensus(reviews, "flaws")[1] is None
    assert "boundaries differ" in ws.inventory()["disagreements"][0]["issue"]
    decision = ws.adjudicate(
        Adjudication(
            recording_id=recording.id,
            scope="flaws",
            review_ids=[r.id for r in reviews],
            adjudicator_id="fixture-operator",
            explanation="Fixture boundary discussion",
            resolution="Operator prefers first interval; this cannot create independent agreement.",
        )
    )
    assert decision["status"] == "awaiting_reviewer_revisions"
    assert sorted(ws.reviews(), key=lambda r: r.id) == reviews
    revised = reviews[1].model_copy(
        deep=True, update={"id": "revision", "supersedes": reviews[1].id}
    )
    revised.labels = [reviews[0].labels[0].model_copy(update={"id": "fixture-revised-label"})]
    publish(ws.root, revised)
    restarted = ReviewWorkspace(ws.root, ws.jobs)
    assert restarted.inventory()["disagreements"][0]["issue"] is None
    assert restarted.inventory()["decisions"][0] == decision
    assert len(restarted.reviews()) == 3


def test_seek_jumps_and_integrity_rejected(workspace):
    ws, recording = workspace
    grant = ws.create(
        ReviewAssignment(recording_id=recording.id, reviewer_id="test-a", scope="transcript")
    )
    with pytest.raises(ValueError, match="real-time"):
        ws.listen(grant.session_id, ListeningEvent(start_s=0.0, end_s=2.0))
    with ws.db() as db:
        db.execute("UPDATE sessions SET payload='{}' WHERE id=?", (grant.session_id,))
    with pytest.raises(ValueError, match="integrity"):
        ws.get(grant.session_id)


def test_export_import_existing_pipeline_and_contracts(imported, monkeypatch):
    root, recording = imported
    app = create_app(root)
    with TestClient(app) as client:
        ws = app.state.review_workspace
        grant = ws.create(
            ReviewAssignment(recording_id=recording.id, reviewer_id="test-only", scope="transcript")
        )
        session = listen_fixture(ws, grant.session_id, monkeypatch)
        session = save_draft(ws, session, draft(session))
        ws.submit(session.id, session.edit_revision)
        client.post(
            f"/api/v1/review-workspace/{session.id}/activate",
            json={"access_token": grant.access_token},
        )
        exported = client.get(f"/api/v1/review-workspace/{session.id}/export")
        assert exported.status_code == 200
        review = Review.model_validate_json(exported.content)
        assert review.decision == "unresolved"  # No approval generated by submission.
        ws.unlock()
        app.state.jobs.get = lambda _: SimpleNamespace(artifacts={recording.id: {}})
        imported_review = client.post(
            "/api/v1/reviews/import",
            json={"job_id": "software-job", "review": review.model_dump(mode="json")},
        )
        assert imported_review.status_code == 200, imported_review.text
        assert imported_review.json()["decision"] == "unresolved"
        assert len(ws.reviews()) == 1
        schema = client.get("/openapi.json").json()
        for name in (
            "ReviewSession",
            "ReviewValidation",
            "ReviewInventory",
            "ReviewSummary",
            "AdjudicationRecord",
        ):
            assert name in schema["components"]["schemas"]
        wrong = review.model_dump(mode="json")
        wrong["provenance"]["audio_sha256"] = "0" * 64
        assert (
            client.post(
                "/api/v1/reviews/import", json={"job_id": "software-job", "review": wrong}
            ).status_code
            == 422
        )


def test_http_timing_phrase_arrays_use_existing_json_contract(imported):
    root, recording = imported
    app = create_app(root)
    with TestClient(app) as client:
        ws = app.state.review_workspace
        session, alignment, _ = timing_fixture(ws, recording)
        ws.unlock()
        grant = ws.resume(session.id)
        client.post(
            f"/api/v1/review-workspace/{session.id}/activate",
            json={"access_token": grant.access_token},
        )
        payload = draft(session, words=alignment.words, phrase_spans=[(0, 2), (2, 4)]).model_dump(
            mode="json"
        )
        response = client.post(
            f"/api/v1/review-workspace/{session.id}/draft",
            json={"revision": session.edit_revision, "draft": payload},
        )
        assert response.status_code == 200, response.text
        assert response.json()["draft"]["phrase_spans"] == [[0, 2], [2, 4]]
        payload["phrase_spans"] = [[0, "4"]]
        assert (
            client.post(
                f"/api/v1/review-workspace/{session.id}/draft",
                json={"revision": 1, "draft": payload},
            ).status_code
            == 422
        )
        updated = ws.get(session.id)
        review = ws.make_review(updated)
        ws.unlock()
        response = client.post(
            "/api/v1/reviews/import",
            json={"job_id": "test-job", "review": review.model_dump(mode="json")},
        )
        assert response.status_code == 200, response.text
        assert load(root).recordings[0].transcript.status == "unverified"


def test_valid_but_replaced_alignment_and_pair_are_stale(workspace):
    ws, recording = workspace
    session, alignment, _ = timing_fixture(ws, recording)
    changed = alignment.model_copy(deep=True)
    changed.words[0].end_s = 0.31
    path = publish_alignment(ws.root, changed)
    ws.jobs.get = lambda _: SimpleNamespace(
        artifacts={recording.id: {"alignment": path.relative_to(ws.root).as_posix()}}
    )
    with pytest.raises(ValueError, match="alignment changed"):
        ws.check_current(session)
    ws.unlock()
    dataset = load(ws.root)
    dataset.recordings[0].role = "participant"
    pair = Pair(
        id="test-pair",
        reference_id="test-reference",
        participant_id=recording.id,
        transcript_sha256=recording.transcript_sha256,
        intended_flaw="unspecified",
        intended_severity=None,
        identity_status="needs_review",
    )
    dataset.pairs.append(pair)
    save(ws.root, dataset)
    grant = ws.create(
        ReviewAssignment(
            recording_id=recording.id, reviewer_id="test-a", scope="flaws", pair_id=pair.id
        )
    )
    session = ws.get(grant.session_id)
    dataset.pairs[0].reference_id = "test-other-reference"
    save(ws.root, dataset)
    with pytest.raises(ValueError, match="pair changed"):
        ws.check_current(session)


def test_unknown_lifecycle_version_is_not_silently_downgraded(workspace):
    ws, _ = workspace
    with ws.db() as db:
        db.execute("PRAGMA user_version=99")
    with pytest.raises(ValueError, match="Unsupported review"):
        ReviewWorkspace(ws.root, ws.jobs)


def test_missing_operator_key_requires_restore(workspace):
    ws, _ = workspace
    ws.key_path.unlink()  # Isolated temporary software fixture, never a user's key.
    with pytest.raises(ValueError, match="Operator key missing"):
        ReviewWorkspace(ws.root, ws.jobs)
    assert not ws.key_path.exists()


def test_uncertain_approval_duplicate_and_future_coverage_rejected(workspace, monkeypatch):
    ws, recording = workspace
    grant = ws.create(
        ReviewAssignment(recording_id=recording.id, reviewer_id="test-a", scope="transcript")
    )
    session = listen_fixture(ws, grant.session_id, monkeypatch)
    from taketwo.comparison.contracts import Span

    session = save_draft(
        ws,
        session,
        draft(session, decision="approved", unclear_spans=[Span(start_s=0.1, end_s=0.2)]),
    )
    assert not ws.validation(session).can_submit
    session = save_draft(ws, session, session.draft.model_copy(update={"unclear_spans": []}))
    assert ws.validation(session).can_submit
    ws.submit(session.id, session.edit_revision)
    ws.unlock()
    grant = ws.create(
        ReviewAssignment(recording_id=recording.id, reviewer_id="test-a", scope="transcript")
    )
    session = listen_fixture(ws, grant.session_id, monkeypatch)
    session = save_draft(ws, session, draft(session, decision="approved"))
    assert any("superseding" in issue for issue in ws.validation(session).issues)


@pytest.mark.parametrize("stage", ["before", "after"])
def test_actual_process_interruption_recovers_publication(workspace, monkeypatch, tmp_path, stage):
    import subprocess
    import sys
    import time

    ws, recording = workspace
    grant = ws.create(
        ReviewAssignment(recording_id=recording.id, reviewer_id="crash-fixture", scope="transcript")
    )
    session = listen_fixture(ws, grant.session_id, monkeypatch)
    session = save_draft(ws, session, draft(session, decision="approved"))
    barrier = tmp_path / "publication-barrier"
    script = r"""
import sys,time
from pathlib import Path
from types import SimpleNamespace
import taketwo.web.review_workspace as module
ws = module.ReviewWorkspace(Path(sys.argv[1]), SimpleNamespace(list=lambda: []))
original = module.publish
def interrupted(root,review):
    if sys.argv[5] == "after":
        original(root,review)
    Path(sys.argv[4]).write_text("ready")
    while True:
        time.sleep(.05)
module.publish = interrupted
ws.submit(sys.argv[2],int(sys.argv[3]))
"""
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            script,
            str(ws.root),
            session.id,
            str(session.edit_revision),
            str(barrier),
            stage,
        ]
    )
    try:
        deadline = time.monotonic() + 60
        while not barrier.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        assert barrier.exists(), "Child never reached publication interruption barrier"
    finally:
        process.kill()
        process.wait(timeout=10)
    assert ws.get(session.id).state == "draft"
    assert len(ws.reviews()) == (1 if stage == "after" else 0)
    restarted = ReviewWorkspace(ws.root, ws.jobs)
    recovered = restarted.get(session.id)
    assert recovered.state == "submitted"
    assert recovered.review.reviewer_id == "crash-fixture"
    assert recovered.review.notes == session.draft.notes
    assert len(restarted.reviews()) == 1
    assert restarted.submit(session.id, session.edit_revision) == recovered
    assert ReviewWorkspace(ws.root, ws.jobs).get(session.id) == recovered


def test_publication_corruption_fails_closed(workspace, monkeypatch):
    ws, recording = workspace
    grant = ws.create(
        ReviewAssignment(
            recording_id=recording.id, reviewer_id="corrupt-fixture", scope="transcript"
        )
    )
    session = listen_fixture(ws, grant.session_id, monkeypatch)
    session = save_draft(ws, session, draft(session, decision="approved"))
    ws.submit(session.id, session.edit_revision)
    artifact = next((ws.root / "derived/comparison-v1").glob("review-*.json"))
    artifact.write_text("corrupted", encoding="utf-8")
    with pytest.raises(ValueError):
        ReviewWorkspace(ws.root, ws.jobs)
    assert artifact.read_text(encoding="utf-8") == "corrupted"


@pytest.mark.parametrize("wrong_cookie", [False, True])
def test_every_reviewer_endpoint_rejects_missing_or_wrong_capability(imported, wrong_cookie):
    root, recording = imported
    app = create_app(root)
    with TestClient(app) as client:
        ws = app.state.review_workspace
        grant = ws.create(
            ReviewAssignment(
                recording_id=recording.id, reviewer_id="isolation-fixture", scope="transcript"
            )
        )
        prefix = f"/api/v1/review-workspace/{grant.session_id}"
        if wrong_cookie:
            client.cookies.set("taketwo_review", "wrong-capability")
        for suffix in (
            "",
            "/validation",
            "/export",
            "/summary",
            "/audio",
            "/reference-audio",
            "/waveform",
        ):
            assert client.get(prefix + suffix).status_code == 403, suffix
        payload = {"revision": 0, "draft": ws.get(grant.session_id).draft.model_dump(mode="json")}
        for suffix, value in [
            ("/draft", payload),
            ("/submit", payload),
            ("/listen", {"start_s": 0.0, "end_s": 0.1}),
            ("/inspect", {"token_index": 0}),
            ("/activate", {"access_token": "wrong"}),
            ("/resume", None),
        ]:
            assert client.post(prefix + suffix, json=value).status_code == 403, suffix
        assert ws.reviews() == []


def test_publication_journal_hash_and_conflicting_state_fail_closed(workspace, monkeypatch):
    ws, recording = workspace
    grant = ws.create(
        ReviewAssignment(
            recording_id=recording.id, reviewer_id="journal-fixture", scope="transcript"
        )
    )
    session = listen_fixture(ws, grant.session_id, monkeypatch)
    session = save_draft(ws, session, draft(session, decision="approved"))

    def interrupted(*_):
        raise RuntimeError("simulated interruption after durable intent")

    with monkeypatch.context() as patch:
        patch.setattr("taketwo.web.review_workspace.publish", interrupted)
        with pytest.raises(RuntimeError):
            ws.submit(session.id, session.edit_revision)
    with pytest.raises(Exception, match="pending recovery"):
        save_draft(ws, session, session.draft)
    with ws.db(write=True) as db:
        db.execute("UPDATE publications SET payload='{}' WHERE id=?", (session.id,))
    with pytest.raises(ValueError, match="journal hash"):
        ReviewWorkspace(ws.root, ws.jobs)
    assert ws.get(session.id).draft == session.draft


def test_browser_review_contracts_through_reviewed_revision_and_evaluation(
    workspace, audio_path, metadata, tmp_path, monkeypatch
):
    """Generated signals/assertions ONLY: exercise the complete evidence lifecycle."""
    from taketwo.analysis.contracts import FeatureConfig
    from taketwo.analysis.features import extract
    from taketwo.comparison.contracts import EvaluationConfig, Policy
    from taketwo.comparison.engine import compare
    from taketwo.comparison.evaluation import evaluate
    from taketwo.comparison.storage import implementation_hash, load_evidence
    from taketwo.dataset.schema import ImportSpec
    from taketwo.dataset.workspace import import_recording, initialize

    ws, recording = workspace
    _, original_alignment, _ = timing_fixture(ws, recording)
    ws.unlock()
    original_manifest = (ws.root / "manifest.jsonl").read_bytes()
    for author in ("fixture-a", "fixture-b"):
        grant = ws.create(
            ReviewAssignment(recording_id=recording.id, reviewer_id=author, scope="transcript")
        )
        session = listen_fixture(ws, grant.session_id, monkeypatch)
        session = save_draft(
            ws,
            session,
            draft(session, corrected_text="One two three. Four five six.", decision="approved"),
        )
        assert ws.validation(session).alignment_needs_regeneration
        ws.submit(session.id, session.edit_revision)
        ws.unlock()
    accepted, issue = consensus(ws.reviews(), "transcript")
    assert issue is None
    assert (ws.root / "manifest.jsonl").read_bytes() == original_manifest
    # Explicit operator re-import from consensus in a NEW version; no in-place
    # certification endpoint or old-review rebinding is implied by this fixture.
    root = tmp_path / "reviewed-fixture-v2"
    initialize(root, "reviewed-fixture-v2")
    metadata["transcript"].update(
        text=accepted[0].corrected_text,
        status="verified",
        reviewers=[r.reviewer_id for r in accepted],
        verification_date=accepted[0].reviewed_on,
        revision="reviewed-v2",
    )
    metadata["provenance"]["rights"].update(
        status="cleared", permits_adaptation=True, permits_redistribution=True
    )
    metadata["provenance"]["collection_method"] += (
        "; original transcript review hashes: "
        + ",".join(content_hash(r.model_dump(mode="json")) for r in accepted)
    )
    reference = import_recording(
        root, audio_path, ImportSpec.model_validate_json(canonical_json(metadata))
    )
    metadata["origin"] = "self_recorded"
    metadata["speaker_id"] = "fixture-participant"
    metadata["provenance"]["consent_evidence"] = (
        "Software generated signal only; not consent or a human recording"
    )
    import soundfile as sf

    fixture_samples, fixture_rate = sf.read(audio_path, dtype="float32")
    participant_path = tmp_path / "reviewed-participant-fixture.wav"
    sf.write(participant_path, fixture_samples * 0.7, fixture_rate, subtype="FLOAT")
    participant = import_recording(
        root,
        participant_path,
        ImportSpec.model_validate_json(canonical_json(metadata)),
        reference_id=reference.id,
    )
    jobs = SimpleNamespace(list=lambda: [])
    revised = ReviewWorkspace(root, jobs)
    paths = {}
    for member in (reference, participant):
        _, samples, provenance = recording_input(root, member.id)
        words = [
            Interval(start_s=0.05 + i * 0.3, end_s=0.3 + i * 0.3, label=token, token_index=i)
            for i, token in enumerate(member.tokens)
        ]
        alignment = original_alignment.model_copy(
            update={
                "provenance": provenance,
                "original_text": member.transcript.text,
                "normalized_tokens": member.tokens,
                "token_offsets": member.token_offsets,
                "words": words,
            }
        )
        assert alignment.provenance != original_alignment.provenance
        apath = publish_alignment(root, alignment)
        fpath = publish_alignment(root, extract(samples, provenance, FeatureConfig(), alignment))
        jobs.get = lambda _, rid=member.id, p=apath: SimpleNamespace(
            artifacts={rid: {"alignment": p.relative_to(root).as_posix()}}
        )
        for author in ("fixture-a", "fixture-b"):
            grant = revised.create(
                ReviewAssignment(
                    recording_id=member.id, reviewer_id=author, scope="timing", job_id="fixture-job"
                )
            )
            session = listen_fixture(revised, grant.session_id, monkeypatch)
            session = save_draft(
                revised,
                session,
                draft(session, decision="approved", words=words, phrase_spans=[(0, 3), (3, 6)]),
            )
            for index in range(len(words)):
                session = revised.inspect(session.id, index)
            revised.submit(session.id, session.edit_revision)
            revised.unlock()
        paths[member.id] = (fpath, apath)
    dataset = load(root)
    reviews = list((root / "derived/comparison-v1").glob("review-*.json"))
    evidence = [
        load_evidence(root, dataset, *paths[m.id], reviews) for m in (reference, participant)
    ]
    report = compare(
        *evidence,
        dataset.pairs[0],
        Policy(),
        content_hash(dataset.model_dump(mode="json")),
        implementation_hash(),
    )
    assert report.overall_score == 100.0
    assert all(g.state == "ELIGIBLE" for g in report.feature_eligibility.values())
    for author in ("fixture-a", "fixture-b"):
        grant = revised.create(
            ReviewAssignment(
                recording_id=participant.id,
                pair_id=dataset.pairs[0].id,
                reviewer_id=author,
                scope="flaws",
            )
        )
        session = listen_fixture(revised, grant.session_id, monkeypatch)
        session = save_draft(
            revised, session, draft(session, decision="approved", blinded_to_predictions=True)
        )
        revised.submit(session.id, session.edit_revision)
        revised.unlock()
    result = evaluate(
        dataset,
        [report],
        revised.reviews(),
        EvaluationConfig(mode="software_fixture"),
        implementation_hash(),
    )
    assert result.metrics.false_positive == 0
    assert not result.independent_real_validation
    assert load(ws.root).recordings[0].transcript.status == "unverified"


def test_contradictory_publication_and_legacy_orphan_retained(workspace, monkeypatch):
    from taketwo.comparison.storage import publish

    ws, recording = workspace
    grant = ws.create(
        ReviewAssignment(
            recording_id=recording.id, reviewer_id="conflict-fixture", scope="transcript"
        )
    )
    session = listen_fixture(ws, grant.session_id, monkeypatch)
    session = save_draft(ws, session, draft(session, decision="approved"))
    original = ws.make_review(session)
    artifact = publish(ws.root, original)
    before = artifact.read_bytes()
    with pytest.raises(ValueError, match="Legacy orphan"):
        ReviewWorkspace(ws.root, ws.jobs)
    assert artifact.read_bytes() == before
    # A different approved payload for this logical ID cannot be reconciled by
    # publishing yet another hash-addressed file.
    with monkeypatch.context() as patch:
        patch.setattr(ws, "validation", lambda _: SimpleNamespace(can_submit=True))
        session = save_draft(
            ws, session, draft(session, decision="approved", notes="Contradictory fixture notes")
        )
        with pytest.raises(ValueError, match="contradicts"):
            ws.submit(session.id, session.edit_revision)
    assert artifact.read_bytes() == before and len(ws.reviews()) == 1
    assert ws.get(session.id).state == "draft"


def test_operator_endpoints_and_cross_origin_review_save_fail_closed(imported):
    root, recording = imported
    app = create_app(root)
    with TestClient(app) as client:
        ws = app.state.review_workspace
        grant = ws.create(
            ReviewAssignment(
                recording_id=recording.id, reviewer_id="operator-fixture", scope="transcript"
            )
        )
        ws.unlock()
        assignment = {
            "recording_id": recording.id,
            "reviewer_id": "other-fixture",
            "scope": "transcript",
        }
        adjudication = {
            "recording_id": recording.id,
            "scope": "transcript",
            "review_ids": ["fixture-a", "fixture-b"],
            "adjudicator_id": "fixture-owner",
            "explanation": "Test-only explanation",
            "resolution": "Test-only resolution",
        }
        prefix = "/api/v1/review-workspace"
        for headers in ({}, {"X-Review-Operator": "wrong"}):
            assert client.get(prefix + "/inventory", headers=headers).status_code == 403
            assert (
                client.post(prefix + "/sessions", headers=headers, json=assignment).status_code
                == 403
            )
            assert (
                client.post(prefix + f"/{grant.session_id}/resume", headers=headers).status_code
                == 403
            )
            assert (
                client.post(
                    prefix + "/adjudications", headers=headers, json=adjudication
                ).status_code
                == 403
            )
            assert (
                client.post(
                    prefix + "/unlock", headers=headers, json={"operator_key": "wrong"}
                ).status_code
                == 403
            )
        resumed = ws.resume(grant.session_id)
        assert (
            client.post(
                prefix + f"/{grant.session_id}/activate",
                json={"access_token": resumed.access_token},
            ).status_code
            == 200
        )
        session = ws.get(grant.session_id)
        response = client.post(
            prefix + f"/{grant.session_id}/draft",
            headers={"Origin": "https://untrusted.invalid"},
            json={
                "revision": session.edit_revision,
                "draft": session.draft.model_dump(mode="json"),
            },
        )
        assert response.status_code == 403
        assert ws.get(grant.session_id) == session
