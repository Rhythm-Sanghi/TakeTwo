"""Strict manifest v1 contracts; acoustic truth is never inferred from metadata."""

import hashlib
import json
import re
import unicodedata
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Identifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")]
Digest = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100000)]
Severity = Literal[0, 1, 2, 3]
Category = Literal[
    "pacing",
    "pause_behavior",
    "energy_variation",
    "pitch_dynamics",
    "acceptable",
    "recording_quality",
    "alignment_uncertainty",
]


def canonical_json(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    )


def content_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def tokenize(text: str) -> tuple[list[str], list[tuple[int, int]]]:
    # Normalize tokens, not the original text, so offsets remain faithful to the input.
    matches = list(re.finditer(r"\w+(?:['\u2019]\w+)*", text, re.UNICODE))
    return (
        [
            unicodedata.normalize("NFKC", m.group()).casefold().replace("\u2019", "'")
            for m in matches
        ],
        [(m.start(), m.end()) for m in matches],
    )


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Transcript(Model):
    text: Text
    language: Literal["en"]
    status: Literal["unverified", "verified"]
    reviewers: list[Identifier]
    verification_date: str | None
    revision: Identifier

    @model_validator(mode="after")
    def check_verification(self) -> "Transcript":
        if not tokenize(self.text)[0]:
            raise ValueError("transcript must contain spoken words")
        if len(set(self.reviewers)) != len(self.reviewers):
            raise ValueError("reviewer IDs must be unique")
        if self.status == "verified":
            if len(self.reviewers) < 2 or self.verification_date is None:
                raise ValueError("verified transcripts need two reviewers and a verification date")
            date.fromisoformat(self.verification_date)
        elif self.reviewers or self.verification_date:
            raise ValueError("unverified transcripts cannot assert verification reviewers/date")
        return self


class Rights(Model):
    status: Literal["pending", "cleared"]
    holder: Text | None
    license_name: Text | None
    evidence: Text | None
    attribution: Text | None
    permits_adaptation: bool
    permits_redistribution: bool

    @model_validator(mode="after")
    def check_clearance(self) -> "Rights":
        if self.status == "cleared" and not (
            self.permits_adaptation
            and self.permits_redistribution
            and self.holder
            and self.license_name
            and self.evidence
            and self.attribution
        ):
            raise ValueError("cleared rights must permit adaptation and redistribution")
        return self


class Provenance(Model):
    source_id: Identifier
    work_id: Identifier
    source: Text
    source_url: Text | None
    collection_method: Text
    access_date: str
    excerpt_offset_s: Annotated[float, Field(ge=0)]
    baseline_rationale: Text | None
    consent_evidence: Text | None
    rights: Rights

    @model_validator(mode="after")
    def check_date(self) -> "Provenance":
        date.fromisoformat(self.access_date)
        if self.source_url and not self.source_url.startswith(("https://", "http://")):
            raise ValueError("source_url must be HTTP(S)")
        return self


class AudioInfo(Model):
    format: Literal["WAV", "FLAC"]
    subtype: Text
    sample_rate_hz: Annotated[int, Field(ge=8000, le=96000)]
    channels: Literal[1, 2]
    frames: Annotated[int, Field(gt=0)]
    duration_s: Annotated[float, Field(gt=0, le=600)]
    rms_dbfs: float
    peak: Annotated[float, Field(ge=0)]
    clipping_fraction: Annotated[float, Field(ge=0, le=1)]


class Processing(Model):
    algorithm: Literal["mono-polyphase-v1"] = "mono-polyphase-v1"
    sample_rate_hz: Literal[16000] = 16000
    subtype: Literal["FLOAT"] = "FLOAT"
    channel: Literal[0, 1] | None
    versions: dict[str, Text]


class Operation(Model):
    kind: Literal["insert_pause", "shorten_pause", "tempo", "gain", "pitch_shift"]
    start_s: Annotated[float, Field(ge=0)]
    end_s: Annotated[float, Field(gt=0)]
    value: float
    severity: Literal[1, 2, 3]

    @model_validator(mode="after")
    def check_operation(self) -> "Operation":
        if self.end_s <= self.start_s:
            raise ValueError("operation end must exceed start")
        bounds = {
            "insert_pause": (0.05, 5),
            "shorten_pause": (0.05, 0.95),
            "tempo": (0.5, 2),
            "gain": (0.1, 3),
            "pitch_shift": (-4, 4),
        }
        low, high = bounds[self.kind]
        if not low <= self.value <= high:
            raise ValueError(f"{self.kind} value must be between {low} and {high}")
        if self.kind in {"tempo", "gain"} and self.value == 1:
            raise ValueError("identity operation is not a flaw")
        if self.kind == "pitch_shift" and self.value == 0:
            raise ValueError("zero pitch shift is not a flaw")
        return self


class Recipe(Model):
    seed: Annotated[int, Field(ge=0, le=2**32 - 1)]
    operations: Annotated[list[Operation], Field(min_length=1, max_length=12)]

    @model_validator(mode="after")
    def check_order(self) -> "Recipe":
        for previous, current in zip(self.operations, self.operations[1:], strict=False):
            if previous.end_s > current.start_s:
                raise ValueError("operations must be ordered and nonoverlapping in parent time")
        return self


class TimeSegment(Model):
    source_start: Annotated[int, Field(ge=0)]
    source_end: Annotated[int, Field(ge=0)]
    output_start: Annotated[int, Field(ge=0)]
    output_end: Annotated[int, Field(ge=0)]
    kind: Literal["unchanged", "modified", "inserted"]


class Transformation(Model):
    algorithm: Literal["controlled-flaws-v1"] = "controlled-flaws-v1"
    parent_id: Identifier
    source_sha256: Digest
    recipe: Recipe
    recipe_sha256: Digest
    time_map: list[TimeSegment]
    versions: dict[str, Text]


class Recording(Model):
    id: Identifier
    dataset_version: Identifier
    family_id: Identifier
    speaker_id: Identifier
    origin: Literal["source", "self_recorded", "synthetic"]
    role: Literal["reference", "participant"]
    original_filename: Text
    original_path: Text
    normalized_path: Text
    original_sha256: Digest
    normalized_sha256: Digest
    sample_sha256: Digest
    transcript: Transcript
    transcript_sha256: Digest
    tokens: list[str]
    token_offsets: list[tuple[int, int]]
    provenance: Provenance
    original_info: AudioInfo
    normalized_info: AudioInfo
    processing: Processing
    transformation: Transformation | None
    quality_flags: list[str]


class Pair(Model):
    id: Identifier
    reference_id: Identifier
    participant_id: Identifier
    transcript_sha256: Digest
    intended_flaw: Category | Literal["unspecified"]
    intended_severity: Severity | None
    reviewed_severity: Severity | None = None
    identity_status: Literal["needs_review", "verified", "derived"]

    @model_validator(mode="after")
    def intent(self):
        if self.intended_flaw == "unspecified":
            if self.intended_severity is not None:
                raise ValueError("Unspecified acquisition intent has no severity.")
        elif self.intended_severity is None:
            raise ValueError("An intended category requires its intended severity.")
        return self


class Annotation(Model):
    id: Identifier
    pair_id: Identifier
    recording_id: Identifier
    transcript_sha256: Digest
    category: Category
    start_s: Annotated[float, Field(ge=0)]
    end_s: Annotated[float, Field(gt=0)]
    severity: Severity
    source: Literal["human", "synthetic_recipe"]
    review_status: Literal["unreviewed", "reviewed", "adjudicated"]
    reviewer_id: Identifier | None
    rationale: Text
    uncertainty_s: Annotated[float, Field(ge=0)] | None
    token_span: tuple[int, int] | None
    transformation_sha256: Digest | None
    supersedes: Identifier | None = None

    @model_validator(mode="after")
    def check_annotation(self) -> "Annotation":
        if self.start_s >= self.end_s:
            raise ValueError("annotation end must exceed start")
        if (self.category == "acceptable") != (self.severity == 0):
            raise ValueError("only acceptable annotations use severity zero")
        if self.source == "synthetic_recipe":
            if (
                self.review_status != "unreviewed"
                or self.reviewer_id
                or not self.transformation_sha256
            ):
                raise ValueError(
                    "recipe labels are unreviewed and require transformation provenance"
                )
        elif self.review_status != "unreviewed" and not self.reviewer_id:
            raise ValueError("reviewed human annotations require a reviewer ID")
        return self


class SplitReport(Model):
    seed: int
    ratios: tuple[float, float, float]
    assignments: dict[str, Literal["train", "validation", "test"]]
    groups: dict[str, list[str]]
    membership_sha256: Digest
    warnings: list[str]


class Dataset(Model):
    schema_version: Literal[1, 2] = 2
    dataset_version: Identifier
    recordings: list[Recording] = Field(default_factory=list)
    pairs: list[Pair] = Field(default_factory=list)
    annotations: list[Annotation] = Field(default_factory=list)
    split: SplitReport | None = None

    @model_validator(mode="after")
    def legacy_fields(self):
        if self.schema_version == 1 and (
            any(
                r.provenance.access_date is None
                or any(
                    v is None
                    for v in (
                        r.provenance.rights.holder,
                        r.provenance.rights.license_name,
                        r.provenance.rights.evidence,
                        r.provenance.rights.attribution,
                    )
                )
                for r in self.recordings
            )
            or any(
                p.intended_flaw == "unspecified" or p.intended_severity is None for p in self.pairs
            )
        ):
            raise ValueError("Unknown draft facts require explicit dataset schema v2 upgrade.")
        return self


class ImportSpec(Model):
    family_id: Identifier
    speaker_id: Identifier
    origin: Literal["source", "self_recorded"]
    transcript: Transcript
    provenance: Provenance
    channel: Literal[0, 1] | None = None
