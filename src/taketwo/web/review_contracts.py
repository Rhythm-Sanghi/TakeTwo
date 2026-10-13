"""Draft lifecycle around the existing Phase 3 scientific Review contract."""

from typing import Annotated, Literal

from pydantic import Field, field_validator

from taketwo.analysis.contracts import Interval, Provenance
from taketwo.comparison.contracts import Label, Review, Span
from taketwo.dataset.schema import Digest, Identifier, Model, Text, canonical_json


class ReviewAssignment(Model):
    recording_id: Identifier
    reviewer_id: Identifier
    scope: Literal["transcript", "timing", "flaws"]
    job_id: Identifier | None = None
    pair_id: Identifier | None = None
    supersedes: Identifier | None = None


class ReviewDraft(Model):
    corrected_text: Annotated[str, Field(max_length=100000)] = ""
    words: list[Interval] = Field(default_factory=list, max_length=3000)
    phrase_spans: list[tuple[int, int]] = Field(default_factory=list, max_length=3000)
    labels: list[Label] = Field(default_factory=list, max_length=1000)
    unclear_spans: list[Span] = Field(default_factory=list, max_length=1000)
    uncertain_words: list[int] = Field(default_factory=list, max_length=3000)
    decision: Literal["approved", "rejected", "unresolved"] = "unresolved"
    independent: bool = False
    blinded_to_predictions: bool = False
    evidence_reference: Annotated[str, Field(max_length=100000)] = ""
    notes: Annotated[str, Field(max_length=100000)] = ""


class DraftSave(Model):
    revision: Annotated[int, Field(ge=0)]
    draft: ReviewDraft

    @field_validator("draft", mode="before")
    @classmethod
    def json_draft(cls, value):
        # FastAPI decodes the HTTP body first. Preserve strict JSON semantics for tuples.
        return (
            ReviewDraft.model_validate_json(canonical_json(value))
            if isinstance(value, dict)
            else value
        )


class ListeningEvent(Model):
    start_s: Annotated[float, Field(ge=0)]
    end_s: Annotated[float, Field(gt=0)]


class WordInspection(Model):
    token_index: Annotated[int, Field(ge=0)]


class ReviewSession(Model):
    schema_version: Literal[1] = 1
    id: Identifier
    assignment: ReviewAssignment
    state: Literal["draft", "submitted"] = "draft"
    created_at: Text
    updated_at: Text
    submitted_at: Text | None = None
    revision: int = 0
    edit_revision: int = 0
    recording_name: Text
    duration_s: float
    provenance: Provenance
    recording_sha256: Digest
    alignment_sha256: Digest | None
    pair_sha256: Digest | None = None
    original_text: Text
    machine_text: str | None
    suggestions: list[Interval]
    assisted_alignment: bool
    draft: ReviewDraft
    listened_spans: list[Span] = Field(default_factory=list)
    inspected_words: list[int] = Field(default_factory=list)
    review: Review | None = None
    integrity_sha256: Digest | None = None


class ReviewGrant(Model):
    session_id: Identifier
    access_token: Text


class ActivateReview(Model):
    access_token: Text


class OperatorKey(Model):
    operator_key: Text


class Adjudication(Model):
    recording_id: Identifier
    scope: Literal["transcript", "timing", "flaws"]
    review_ids: Annotated[list[Identifier], Field(min_length=2)]
    adjudicator_id: Identifier
    explanation: Text
    resolution: Text


class ReviewValidation(Model):
    can_submit: bool
    issues: list[str]
    alignment_needs_regeneration: bool
    listened_s: float
    scientific_notice: str = (
        "Submission stores a reviewer assertion, not authenticated identity or scientific "
        "eligibility. Verified dataset text, agreement, rights and all existing gates still apply."
    )


class ReviewMode(Model):
    active_session: Identifier | None


class AdjudicationRecord(Adjudication):
    id: Identifier
    created_at: Text
    status: Literal["awaiting_reviewer_revisions", "agreement_recorded"]
    consensus_issue: str | None


class ReviewDisagreement(Model):
    recording_id: Identifier
    scope: Literal["transcript", "timing", "flaws"]
    issue: str | None
    reviews: list[Review]


class ReviewInventory(Model):
    sessions: list[ReviewSession]
    disagreements: list[ReviewDisagreement]
    decisions: list[AdjudicationRecord]


class ReviewSummary(Model):
    session: ReviewSession
    validation: ReviewValidation
