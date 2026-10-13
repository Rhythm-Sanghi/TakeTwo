"""HTTP lifecycle contracts, separate from scientific eligibility."""

from typing import Literal

from pydantic import Field, field_validator

from taketwo.analysis.contracts import Diagnostic, Interval, QualityReport
from taketwo.analysis.limits import DEFAULT_MAX_ANALYSIS_DURATION_S, maximum_analysis_duration_s
from taketwo.comparison.contracts import Review
from taketwo.dataset.schema import Identifier, ImportSpec, Model, Rights, SplitReport, Text


class ImportRequest(Model):
    metadata: ImportSpec
    reference_id: Identifier | None = None
    category: Literal[
        "unspecified",
        "acceptable",
        "pacing",
        "pause_behavior",
        "energy_variation",
        "pitch_dynamics",
    ] = "acceptable"
    severity: Literal[0, 1, 2, 3] | None = 0


class AnalysisRequest(Model):
    reference_id: Identifier
    pair_id: Identifier | None = None
    align: bool = True


class LocalImportRequest(Model):
    recording_type: Literal["public_reference", "controlled_reference", "human_participant"]
    transcript: Text
    title: Text | None = None
    reference_id: Identifier | None = None
    local_permission: bool
    speaker_label: Text | None = None
    same_speaker_as_reference: bool = False
    source_url: Text | None = None
    rationale: Text | None = None
    consent_evidence: Text | None = None
    rights: Rights | None = None
    channel: Literal[0, 1] | None = None
    category: Literal[
        "unspecified",
        "acceptable",
        "pacing",
        "pause_behavior",
        "energy_variation",
        "pitch_dynamics",
    ] = "unspecified"
    severity: Literal[0, 1, 2, 3] | None = None


class ExcerptRequest(Model):
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    transcript: Text
    reference_id: Identifier | None = None


class CorrectionRequest(Model):
    reference_id: Identifier


class WorkspaceRevision(Model):
    workspace: str
    reference_id: Identifier
    participant_id: Identifier
    notice: str


class ReviewImportRequest(Model):
    job_id: str
    review: Review

    @field_validator("review", mode="before")
    @classmethod
    def json_review(cls, value):
        # Review phrase tuples are JSON arrays at the HTTP boundary, as in CLI imports.
        from taketwo.dataset.schema import canonical_json

        return (
            Review.model_validate_json(canonical_json(value)) if isinstance(value, dict) else value
        )


class Job(Model):
    id: str
    request: AnalysisRequest
    state: Literal["queued", "running", "completed", "failed", "cancelled"]
    stage: str
    created_at: str
    updated_at: str
    error: Diagnostic | None = None
    report_path: str | None = None
    artifacts: dict[str, dict[str, str]] = Field(default_factory=dict)
    cancel_requested: bool = False
    elapsed_s: float | None = Field(default=None, ge=0)
    peak_commit_bytes: int | None = Field(default=None, ge=0)
    stage_elapsed_s: dict[str, float] = Field(default_factory=dict)
    cache_hits: list[str] = Field(default_factory=list)


class Health(Model):
    product: Literal["TakeTwo"] = "TakeTwo"
    description: Literal["Speech analysis workspace"] = "Speech analysis workspace"
    api_version: Literal[1] = 1
    ready: bool
    alignment_configured: bool
    alignment_diagnostics: list[Diagnostic]
    maximum_analysis_duration_s: int = Field(
        default_factory=maximum_analysis_duration_s, ge=1, le=DEFAULT_MAX_ANALYSIS_DURATION_S
    )
    maximum_upload_bytes: Literal[104857600] = 104857600
    worker_concurrency: Literal[1] = 1
    maximum_worker_commit_bytes: Literal[4294967296] = 4294967296


class Waveform(Model):
    sample_rate_hz: Literal[16000] = 16000
    start_s: float
    end_s: float
    aggregation: Literal["sample_min_max"] = "sample_min_max"
    bins: list[tuple[int, int, float, float]]


class FeatureWindow(Model):
    name: str
    unit: str
    frame_length: int
    hop_length: int
    sample_rate_hz: Literal[16000] = 16000
    aggregation: Literal["native_frames", "min_max_with_gap_markers"]
    times_s: list[float]
    values: list[float | None]
    quality: QualityReport
    pauses: list[Interval]
    speaking_rate_wpm: float | None
    rate_unavailable_reason: str | None


class Overlay(Model):
    name: str
    unit: str
    aggregation: Literal["reviewed_word_medians"] = "reviewed_word_medians"
    unavailable_reason: str | None
    tokens: list[str]
    reference_words: list[Interval]
    participant_words: list[Interval]
    reference_values: list[float | None]
    participant_values: list[float | None]


class DatasetSummary(Model):
    schema_version: Literal[1, 2]
    dataset_version: Identifier
    recordings: int
    pairs: int
    annotations: int
    origins: dict[str, int]
    annotation_review: dict[str, int]
    severity: dict[str, int]
    split: SplitReport | None
    competition_dataset_complete: Literal[False] = False
