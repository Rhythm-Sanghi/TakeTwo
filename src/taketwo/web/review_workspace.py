"""Local sequential reviewer handoff, isolated drafts and immutable evidence publication.

Capabilities protect browser/API access, not the trusted OS account. No scientific
approval, identity verification or consent is inferred from interaction telemetry.
"""

import hashlib
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import UTC, datetime

from fastapi import HTTPException

from taketwo.analysis.contracts import AlignmentResult
from taketwo.analysis.storage import read_artifact, recording_input, validate_identity
from taketwo.comparison.contracts import Review, Span
from taketwo.comparison.reviews import active_reviews, consensus, resolved_flaws, validate_review
from taketwo.comparison.storage import publish
from taketwo.comparison.storage import read_artifact as read_review
from taketwo.dataset.schema import canonical_json, content_hash, tokenize
from taketwo.dataset.storage import load, managed_path, write_new

from .review_contracts import ReviewDraft, ReviewGrant, ReviewSession, ReviewValidation


def now():
    return datetime.now(UTC).isoformat()


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def merged(spans):
    result = []
    for span in sorted(spans, key=lambda s: s.start_s):
        if result and span.start_s <= result[-1].end_s:
            result[-1] = Span(start_s=result[-1].start_s, end_s=max(result[-1].end_s, span.end_s))
        else:
            result.append(span)
    return result


class ReviewWorkspace:
    def __init__(self, root, jobs):
        self.root, self.jobs = root, jobs
        self.path = managed_path(root, "review-workspace.sqlite3")
        self.key_path = managed_path(root, ".review-operator-key")
        if not self.key_path.exists():
            if self.path.exists():
                raise ValueError(
                    "Operator key missing; restore the private key backup before reopening reviews."
                )
            write_new(self.key_path, secrets.token_urlsafe(32).encode("ascii"))
        self.operator_hash = digest(self.key_path.read_text(encoding="ascii"))
        with self.db() as db:
            if db.execute("PRAGMA user_version").fetchone()[0] not in {0, 1, 2}:
                raise ValueError(
                    "Unsupported review lifecycle database version; restore compatible software."
                )
            db.executescript(
                "PRAGMA journal_mode=WAL; PRAGMA user_version=2;"
                "CREATE TABLE IF NOT EXISTS sessions ("
                "id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, payload TEXT NOT NULL, "
                "sha TEXT NOT NULL, heartbeat REAL NOT NULL);"
                "CREATE TABLE IF NOT EXISTS handoff (id INTEGER PRIMARY KEY CHECK(id=1), "
                "session_id TEXT); INSERT OR IGNORE INTO handoff VALUES(1,NULL);"
                "CREATE TABLE IF NOT EXISTS decisions (id TEXT PRIMARY KEY, payload TEXT NOT NULL);"
                "CREATE TABLE IF NOT EXISTS publications (id TEXT PRIMARY KEY, "
                "payload TEXT NOT NULL, sha TEXT NOT NULL, base_sha TEXT NOT NULL, "
                "completed INTEGER NOT NULL DEFAULT 0);"
            )

        self.recover_publications()

    @contextmanager
    def db(self, *, write=False):
        managed_path(self.root, "review-workspace.sqlite3")
        with sqlite3.connect(self.path, timeout=5) as db:
            if write:
                db.execute("BEGIN IMMEDIATE")
            yield db

    def operator(self, key):
        if not key or not secrets.compare_digest(digest(key), self.operator_hash):
            raise HTTPException(403, "The local operator key is required.")

    def active(self):
        with self.db() as db:
            return db.execute("SELECT session_id FROM handoff WHERE id=1").fetchone()[0]

    def authorize(self, sid, token):
        with self.db() as db:
            row = db.execute("SELECT token_hash FROM sessions WHERE id=?", (sid,)).fetchone()
        if (
            self.active() != sid
            or not row
            or not token
            or not secrets.compare_digest(digest(token), row[0])
        ):
            raise HTTPException(403, "This reviewer capability is not active for this recording.")

    def get(self, sid, db=None):
        if db is None:
            with self.db() as connection:
                return self.get(sid, connection)
        row = db.execute("SELECT payload,sha FROM sessions WHERE id=?", (sid,)).fetchone()
        if not row:
            raise KeyError(sid)
        if digest(row[0]) != row[1]:
            raise ValueError("Review session integrity mismatch; restore from backup.")
        session = ReviewSession.model_validate_json(row[0])
        claimed = session.integrity_sha256
        session.integrity_sha256 = None
        if claimed != content_hash(session.model_dump(mode="json")):
            raise ValueError("Review session payload integrity differs.")
        session.integrity_sha256 = claimed
        return session

    def store(self, session, db):
        session.updated_at = now()
        session.revision += 1
        session.integrity_sha256 = None
        session.integrity_sha256 = content_hash(session.model_dump(mode="json"))
        payload = session.model_dump_json()
        db.execute(
            "UPDATE sessions SET payload=?,sha=? WHERE id=?",
            (payload, digest(payload), session.id),
        )

    def alignment(self, assignment):
        if not assignment.job_id:
            return None
        job = self.jobs.get(assignment.job_id)
        path = job.artifacts.get(assignment.recording_id, {}).get("alignment")
        if not path:
            raise ValueError("Selected job has no alignment for this recording.")
        result = read_artifact(managed_path(self.root, path))
        if not isinstance(result, AlignmentResult) or result.status != "succeeded":
            raise ValueError("Timing suggestions require a successful alignment.")
        validate_identity(self.root, result)
        return result

    def create(self, assignment):
        if any(j.state in {"running", "queued"} for j in self.jobs.list()):
            raise HTTPException(409, "Finish or cancel processing before reviewer handoff.")
        recording, _, provenance = recording_input(self.root, assignment.recording_id)
        alignment = self.alignment(assignment) if assignment.scope != "flaws" else None
        if assignment.scope == "timing" and alignment is None:
            raise ValueError("Timing review requires an actual original MFA artifact.")
        if assignment.scope == "flaws" and not any(
            p.id == assignment.pair_id and p.participant_id == recording.id
            for p in load(self.root).pairs
        ):
            raise ValueError("Blinded flaws must bind the selected participant pair.")
        previous = None
        pair = next((p for p in load(self.root).pairs if p.id == assignment.pair_id), None)
        if assignment.supersedes:
            previous = next((r for r in self.reviews() if r.id == assignment.supersedes), None)
            if not previous or (
                previous.reviewer_id != assignment.reviewer_id
                or previous.scope != assignment.scope
                or previous.provenance != provenance
                or previous.pair_id != assignment.pair_id
            ):
                raise ValueError("Revision must preserve reviewer, scope, pair and provenance.")
        sid, token = "rs-" + secrets.token_hex(12), secrets.token_urlsafe(32)
        session = ReviewSession(
            id=sid,
            assignment=assignment,
            created_at=now(),
            updated_at=now(),
            recording_name="Assigned recording",  # Intent-bearing filenames stay hidden.
            duration_s=recording.normalized_info.duration_s,
            provenance=provenance,
            recording_sha256=content_hash(recording.model_dump(mode="json")),
            alignment_sha256=content_hash(alignment.model_dump(mode="json")) if alignment else None,
            pair_sha256=content_hash(pair.model_dump(mode="json")) if pair else None,
            original_text=recording.transcript.text,
            machine_text=" ".join(alignment.normalized_tokens) if alignment else None,
            suggestions=alignment.words if alignment else [],
            assisted_alignment=alignment is not None,
            draft=ReviewDraft(corrected_text=recording.transcript.text)
            if assignment.scope == "transcript"
            else ReviewDraft(),
        )
        if previous:
            session.draft = ReviewDraft(
                corrected_text=previous.corrected_text or "",
                words=previous.words,
                phrase_spans=previous.phrase_spans,
                labels=previous.labels,
                notes=previous.notes,
            )
        with self.db(write=True) as db:
            if db.execute("SELECT session_id FROM handoff WHERE id=1").fetchone()[0]:
                raise HTTPException(
                    409, "End the current handoff before assigning another reviewer."
                )
            db.execute(
                "INSERT INTO sessions VALUES(?,?,?,?,?)",
                (
                    sid,
                    digest(token),
                    session.model_dump_json(),
                    digest(session.model_dump_json()),
                    time.time(),
                ),
            )
            self.store(session, db)
            db.execute("UPDATE handoff SET session_id=? WHERE id=1", (sid,))
        return ReviewGrant(session_id=sid, access_token=token)

    def check_current(self, session):
        recording, _, provenance = recording_input(self.root, session.assignment.recording_id)
        if (
            provenance != session.provenance
            or content_hash(recording.model_dump(mode="json")) != session.recording_sha256
        ):
            raise ValueError(
                "Recording, text or processing provenance changed; create a new session."
            )
        if session.pair_sha256:
            pair = next(
                (p for p in load(self.root).pairs if p.id == session.assignment.pair_id), None
            )
            if pair is None or content_hash(pair.model_dump(mode="json")) != session.pair_sha256:
                raise ValueError("Assigned pair changed; this session is stale.")
        alignment = self.alignment(session.assignment) if session.alignment_sha256 else None
        if (
            alignment
            and content_hash(alignment.model_dump(mode="json")) != session.alignment_sha256
        ):
            raise ValueError("Original alignment changed; this session is stale.")
        return recording, alignment

    def validate_draft(self, session, draft):
        duration = session.duration_s
        for span in draft.unclear_spans:
            if span.end_s > duration:
                raise ValueError("Unclear speech span exceeds recording.")
        if any(i < 0 or i >= len(session.suggestions) for i in draft.uncertain_words):
            raise ValueError("Unknown uncertain word.")
        if session.assignment.scope == "timing" and draft.words:
            temporary = self.make_review(
                session,
                draft.model_copy(
                    update={"phrase_spans": draft.phrase_spans or [(0, len(draft.words))]}
                ),
            )
            recording, alignment = self.check_current(session)
            validate_review(temporary, recording, alignment)
        if session.assignment.scope != "timing" and (
            draft.words or draft.phrase_spans or draft.uncertain_words
        ):
            raise ValueError("Timing fields belong to a timing activity.")
        if session.assignment.scope != "flaws" and draft.labels:
            raise ValueError("Flaw labels belong to a blinded flaw activity.")
        if session.assignment.scope != "transcript" and draft.corrected_text:
            raise ValueError("Transcript corrections belong to a transcript activity.")
        for label in draft.labels:
            if (label.interval and label.interval.end_s > duration) or (
                label.anchor_s is not None and label.anchor_s > duration
            ):
                raise ValueError("Annotation exceeds native audio.")
        if len({label.id for label in draft.labels}) != len(draft.labels):
            raise ValueError("Duplicate annotation identifiers.")

    def save(self, sid, request):
        with self.db(write=True) as db:
            session = self.get(sid, db)
            self.editable(session)
            if request.revision != session.edit_revision:
                raise HTTPException(409, "Draft changed in another tab. Reload before editing.")
            self.check_current(session)
            self.validate_draft(session, request.draft)
            for index, word in enumerate(request.draft.words):
                if index >= len(session.draft.words) or word != session.draft.words[index]:
                    session.inspected_words = [i for i in session.inspected_words if i != index]
            session.draft = request.draft
            session.edit_revision += 1
            self.store(session, db)
            return session

    def editable(self, session):
        with self.db() as db:
            pending = db.execute(
                "SELECT completed FROM publications WHERE id=?", (session.id,)
            ).fetchone()
        if pending and not pending[0]:
            raise HTTPException(
                409, "Submission is pending recovery; restart the local service before editing."
            )
        if session.state != "draft":
            raise HTTPException(
                409, "Submitted evidence is immutable; request a superseding session."
            )

    def listen(self, sid, event):
        with self.db(write=True) as db:
            session = self.get(sid, db)
            self.editable(session)
            last = db.execute("SELECT heartbeat FROM sessions WHERE id=?", (sid,)).fetchone()[0]
            wall = time.time()
            width = event.end_s - event.start_s
            if (
                not 0 < width <= min(2.5, (wall - last) * 1.3 + 0.1)
                or event.end_s > session.duration_s
            ):
                raise ValueError(
                    "Listening event must follow real-time playback, without seek jumps."
                )
            session.listened_spans = merged([*session.listened_spans, Span(**event.model_dump())])
            db.execute("UPDATE sessions SET heartbeat=? WHERE id=?", (wall, sid))
            self.store(session, db)
            return session

    def inspect(self, sid, index):
        with self.db(write=True) as db:
            session = self.get(sid, db)
            self.editable(session)
            if index >= len(session.draft.words):
                raise ValueError("Set a valid word boundary before inspecting it.")
            word = session.draft.words[index]
            if not any(
                s.start_s <= word.start_s + 0.025 and s.end_s >= word.end_s - 0.025
                for s in session.listened_spans
            ):
                raise ValueError("Listen to this word before marking its boundary inspected.")
            session.inspected_words = sorted({*session.inspected_words, index})
            self.store(session, db)
            return session

    def make_review(self, session, draft=None):
        draft = draft or session.draft
        scope = session.assignment.scope
        return Review(
            id=session.id,
            scope=scope,
            provenance=session.provenance,
            alignment_sha256=session.alignment_sha256 if scope == "timing" else None,
            pair_id=session.assignment.pair_id if scope == "flaws" else None,
            reviewer_id=session.assignment.reviewer_id,
            reviewed_on=(session.submitted_at or now())[:10],
            evidence_reference=draft.evidence_reference or "Draft: evidence reference required",
            independent=draft.independent,
            blinded_to_predictions=draft.blinded_to_predictions,
            decision=draft.decision,
            notes=draft.notes or "Draft: listening notes required",
            corrected_text=draft.corrected_text if scope == "transcript" else None,
            words=draft.words,
            phrase_spans=draft.phrase_spans,
            labels=draft.labels,
            reviewed_spans=session.listened_spans if scope == "flaws" else [],
            supersedes=session.assignment.supersedes,
        )

    def validation(self, session):
        issues = []
        d = session.draft
        listened = sum(s.end_s - s.start_s for s in session.listened_spans)
        if not (
            len(session.listened_spans) == 1
            and session.listened_spans[0].start_s == 0
            and session.listened_spans[0].end_s == session.duration_s
        ):
            issues.append("Listen to the entire recording; seeking does not count as listening.")
        if not d.evidence_reference.strip() or not d.notes.strip():
            issues.append("Supply an evidence reference and actual listening notes.")
        if not d.independent:
            issues.append("Declare your independence, or retain this as a draft.")
        if session.assignment.scope == "flaws" and not d.blinded_to_predictions:
            issues.append("Declare blindness to predictions, scores, intended labels and recipes.")
        if session.assignment.scope == "timing" and len(session.inspected_words) != len(
            session.suggestions
        ):
            issues.append(
                "Explicitly inspect every word boundary after listening; "
                "edited words need reinspection."
            )
        if d.decision == "approved" and (d.unclear_spans or d.uncertain_words):
            issues.append(
                "Unclear speech or uncertain boundaries require an unresolved/rejected decision."
            )
        try:
            self.validate_draft(session, d)
            review = self.make_review(session)
            recording, alignment = self.check_current(session)
            validate_review(review, recording, alignment)
            if not review.supersedes and any(
                r.reviewer_id == review.reviewer_id
                and r.scope == review.scope
                and r.provenance.recording_id == review.provenance.recording_id
                and r.id != review.id
                for r in active_reviews(self.reviews())
            ):
                raise ValueError(
                    "This reviewer already submitted; use an explicit superseding session."
                )
            active_reviews([*[r for r in self.reviews() if r.id != review.id], review])
        except (ValueError, KeyError) as exc:
            issues.append(str(exc))
        changed = (
            session.assignment.scope == "transcript"
            and tokenize(d.corrected_text)[0] != tokenize(session.original_text)[0]
        )
        return ReviewValidation(
            can_submit=not issues,
            issues=issues,
            alignment_needs_regeneration=changed,
            listened_s=listened,
        )

    def submit(self, sid, revision):
        # Durable intent precedes filesystem publication. The journal preserves
        # the exact identity/date/draft even when the process dies before commit.
        with self.db(write=True) as db:
            session = self.get(sid, db)
            if session.edit_revision != revision:
                raise HTTPException(409, "Save and reload the current draft before submission.")
            if session.state == "submitted":
                self.verify_publication(session)
                return session  # Same logical request, not a second submission.
            pending = db.execute("SELECT id FROM publications WHERE id=?", (sid,)).fetchone()
            if not pending:
                self.editable(session)
                validation = self.validation(session)
                if not validation.can_submit:
                    raise ValueError(" ".join(validation.issues))
                session.submitted_at = now()
                session.review = self.make_review(session)
                payload = session.model_dump_json()
                base = db.execute("SELECT sha FROM sessions WHERE id=?", (sid,)).fetchone()[0]
                db.execute(
                    "INSERT INTO publications VALUES(?,?,?,?,0)",
                    (sid, payload, digest(payload), base),
                )
        self.recover_publications(sid)
        return self.get(sid)

    def verify_publication(self, session):
        if session.review is None:
            raise ValueError("Submitted review is missing; restore evidence from backup.")
        path = managed_path(
            self.root,
            f"derived/comparison-v1/review-{content_hash(session.review.model_dump(mode='json'))}.json",
        )
        if not path.is_file() or read_review(path) != session.review:
            raise ValueError("Submitted artifact missing or corrupt; restore evidence from backup.")

    def recover_publications(self, sid=None):
        # SQLite serializes publishers/recovery. No draft can change after intent.
        # A completed journal is also checked on startup: corruption is not repair.
        with self.db(write=True) as db:
            known = {}
            for review in self.reviews():
                if review.id in known:
                    raise ValueError(
                        "Conflicting review ID artifacts; retain evidence and restore backup."
                    )
                known[review.id] = review
            if sid is None:
                rows = db.execute(
                    "SELECT id,payload,sha,base_sha,completed FROM publications"
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT id,payload,sha,base_sha,completed FROM publications WHERE id=?", (sid,)
                ).fetchall()
            for identity, payload, claimed, base_sha, completed in rows:
                if digest(payload) != claimed:
                    raise ValueError(
                        "Publication journal hash differs; restore from backup "
                        "without deleting evidence."
                    )
                prepared = ReviewSession.model_validate_json(payload)
                current = self.get(identity, db)
                if identity in known and known[identity] != prepared.review:
                    raise ValueError(
                        "Published review contradicts submission intent; restore backup."
                    )
                if prepared.id != identity or prepared.review != self.make_review(prepared):
                    raise ValueError(
                        "Contradictory publication identity; retain evidence and restore backup."
                    )
                if completed:
                    if (
                        current.state != "submitted"
                        or current.review != prepared.review
                        or current.submitted_at != prepared.submitted_at
                    ):
                        raise ValueError(
                            "Contradictory submitted lifecycle; retain evidence and restore backup."
                        )
                    self.verify_publication(current)
                    continue
                actual = db.execute("SELECT sha FROM sessions WHERE id=?", (identity,)).fetchone()[
                    0
                ]
                if current.state != "draft" or actual != base_sha:
                    raise ValueError(
                        "Draft changed after submission intent; retain evidence and restore backup."
                    )
                path = publish(self.root, prepared.review)
                if read_review(path) != prepared.review:
                    raise ValueError("Published artifact hash/identity differs; restore backup.")
                prepared.state = "submitted"
                self.store(prepared, db)
                db.execute("UPDATE publications SET completed=1 WHERE id=?", (identity,))
            # Old schema-1 interruption had no intent. Do not guess its date or
            # overwrite conflicting draft edits; surface an operator recovery gate.
            if sid is None:
                published = {r.id: r for r in self.reviews()}
                for (identity,) in db.execute("SELECT id FROM sessions").fetchall():
                    current = self.get(identity, db)
                    if current.state == "draft" and identity in published:
                        raise ValueError(
                            "Legacy orphan review detected; preserve artifact/draft "
                            "and reconcile from backup before startup."
                        )
                    if current.state == "submitted":
                        self.verify_publication(current)

    def reviews(self):
        return [
            read_review(p)
            for p in managed_path(self.root, "derived/comparison-v1").glob("review-*.json")
        ]

    def unlock(self):
        with self.db(write=True) as db:
            db.execute("UPDATE handoff SET session_id=NULL WHERE id=1")

    def resume(self, sid):
        token = secrets.token_urlsafe(32)
        with self.db(write=True) as db:
            self.get(sid, db)
            if db.execute("SELECT session_id FROM handoff WHERE id=1").fetchone()[0]:
                raise HTTPException(409, "End the active handoff first.")
            db.execute(
                "UPDATE sessions SET token_hash=?,heartbeat=? WHERE id=?",
                (digest(token), time.time(), sid),
            )
            db.execute("UPDATE handoff SET session_id=? WHERE id=1", (sid,))
        return ReviewGrant(session_id=sid, access_token=token)

    def inventory(self):
        with self.db() as db:
            sessions = [
                self.get(row[0], db)
                for row in db.execute("SELECT id FROM sessions ORDER BY rowid DESC")
            ]
            decisions = [
                json.loads(row[0])
                for row in db.execute("SELECT payload FROM decisions ORDER BY rowid")
            ]
        groups = {}
        for review in self.reviews():
            key = (review.provenance.recording_id, review.scope)
            groups.setdefault(key, []).append(review)
        disagreements = []
        for (rid, scope), reviews in groups.items():
            _, reason = consensus(reviews, scope)
            if scope == "flaws" and reason is None:
                _, reason = resolved_flaws(reviews)
            for review in reviews:
                try:
                    self.review_binding(review)
                except (ValueError, KeyError, OSError) as exc:
                    reason = f"Stale/invalid evidence: {exc}"
            disagreements.append(
                {
                    "recording_id": rid,
                    "scope": scope,
                    "issue": reason,
                    "reviews": [r.model_dump(mode="json") for r in reviews],
                }
            )
        return {"sessions": sessions, "disagreements": disagreements, "decisions": decisions}

    def review_binding(self, review):
        recording, _, provenance = recording_input(self.root, review.provenance.recording_id)
        if provenance != review.provenance:
            raise ValueError("Review processing/audio/text provenance is stale.")
        alignment = None
        if review.scope == "timing":
            path = managed_path(
                self.root,
                f"derived/v1/{recording.id}/alignment-{review.alignment_sha256}.json",
            )
            alignment = read_artifact(path)
            validate_identity(self.root, alignment)
        validate_review(review, recording, alignment)

    def adjudicate(self, decision):
        known = {r.id: r for r in self.reviews()}
        selected = [known[i] for i in decision.review_ids]
        required = {
            r.id
            for r in active_reviews(list(known.values()))
            if r.provenance.recording_id == decision.recording_id and r.scope == decision.scope
        }
        if not required <= set(decision.review_ids):
            raise ValueError("Adjudication cannot omit another active review of this subject.")
        for review in selected:
            self.review_binding(review)
        if len(set(decision.review_ids)) != len(selected) or any(
            r.provenance.recording_id != decision.recording_id or r.scope != decision.scope
            for r in selected
        ):
            raise ValueError(
                "Adjudication must name distinct submitted reviews of one subject/scope."
            )
        _, issue = consensus(selected, decision.scope)
        if decision.scope == "flaws" and issue is None:
            _, issue = resolved_flaws(selected)
        payload = {
            "id": "ad-" + secrets.token_hex(12),
            "created_at": now(),
            **decision.model_dump(mode="json"),
            "status": "awaiting_reviewer_revisions" if issue else "agreement_recorded",
            "consensus_issue": issue,
        }
        with self.db(write=True) as db:
            db.execute(
                "INSERT INTO decisions VALUES(?,?)", (payload["id"], canonical_json(payload))
            )
        return payload
