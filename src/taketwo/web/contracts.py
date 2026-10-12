"""HTTP lifecycle contracts, separate from scientific eligibility."""

from typing import Literal

from pydantic import Field

from taketwo.analysis.contracts import Diagnostic, Interval, QualityReport
from taketwo.dataset.schema import Identifier, ImportSpec, Model, SplitReport


class ImportRequest(Model):
    metadata: ImportSpec
    reference_id: Identifier | None = None
    category: Literal[
        "acceptable", "pacing", "pause_behavior", "energy_variation", "pitch_dynamics"
    ] = "acceptable"
    severity: Literal[0, 1, 2, 3] = 0


class AnalysisRequest(Model):
    reference_id: Identifier
    pair_id: Identifier | None = None
    align: bool = True


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
    maximum_analysis_duration_s: Literal[30] = 30
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
    dataset_version: Identifier
    recordings: int
    pairs: int
    annotations: int
    origins: dict[str, int]
    annotation_review: dict[str, int]
    severity: dict[str, int]
    split: SplitReport | None
    competition_dataset_complete: Literal[False] = False
