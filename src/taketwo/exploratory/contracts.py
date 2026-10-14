"""Exploratory-v1: no scores, review approvals, calibrated confidence or flaw labels."""

from typing import Literal

from pydantic import Field

from taketwo.analysis.contracts import FeatureConfig, Interval, Provenance
from taketwo.comparison.contracts import ArtifactRef
from taketwo.dataset.schema import Digest, Identifier, Model


class ExploratoryConfig(Model):
    method: Literal["exploratory-v1"] = "exploratory-v1"
    minimum_quiet_s: Literal[0.15] = 0.15
    energy_window_s: Literal[0.5] = 0.5
    energy_step_db: Literal[6.0] = 6.0
    quantile_method: Literal["linear"] = "linear"


class AutomaticAlignment(Model):
    status: str
    transcript_sha256: Digest
    original_text_sha256: Digest
    independently_verified: Literal[False] = False
    words: list[Interval]
    token_count: int
    word_span_s: float | None
    estimated_words_per_minute: float | None
    rate_unavailable_reason: str | None
    diagnostics: list[str]


class AcousticSummary(Model):
    recording_id: Identifier
    filename: str
    role: Literal["reference", "participant"]
    origin: str
    provenance: Provenance
    feature_artifact: ArtifactRef
    alignment_artifact: ArtifactRef | None
    feature_config: FeatureConfig
    duration_s: float
    sample_rate_hz: Literal[16000] = 16000
    source_sample_rate_hz: int
    rms: float
    peak: float
    clipping_fraction: float
    energy_baseline_dbfs: float | None
    energy_quantiles_dbfs: list[float]
    active_energy_range_db: float | None
    activity_support_s: float
    low_energy_support_s: float
    observed_support_s: float
    unobserved_tail_s: float
    accepted_pitch_frames: int
    pitch_frames: int
    accepted_pitch_fraction: float | None
    pitch_baseline_hz: float | None
    voicing_probability_quantiles: list[float]
    quality_flags: list[str]
    automatic_alignment: AutomaticAlignment | None


class AcousticCandidate(Model):
    id: Identifier
    recording_id: Identifier
    feature_sha256: Digest
    kind: Literal[
        "leading_low_energy",
        "internal_low_energy",
        "trailing_low_energy",
        "recording_low_energy",
        "energy_change",
    ]
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    duration_s: float = Field(gt=0)
    median_energy_dbfs: float
    energy_delta_db: float | None = None
    status: Literal["automatic_unverified"] = "automatic_unverified"
    method: str
    threshold_dbfs: float | None
    threshold_delta_db: float | None = None
    frame_window_s: float
    boundary_resolution_s: float
    explanation: str
    limitation: str


class DescriptiveComparison(Model):
    duration_delta_s: float
    absolute_duration_difference_s: float
    relative_duration_delta_percent: float
    rms_level_delta_db: float | None
    active_energy_range_delta_db: float | None
    interpretation: str
    evidence_keys: list[str]
    notes: list[str]


class AutomaticCorrespondence(Model):
    token_index: int
    token: str
    reference: Interval
    participant: Interval
    status: Literal["automatic_unverified"] = "automatic_unverified"


class ExploratoryReport(Model):
    kind: Literal["exploratory_analysis"] = "exploratory_analysis"
    schema_version: Literal[1] = 1
    config: ExploratoryConfig
    implementation_sha256: Digest
    dataset_version: Identifier
    dataset_sha256: Digest
    job_id: str
    processing_state: str
    reference_id: Identifier
    pair_id: Identifier | None
    state: Literal["available", "partial"]
    recordings: list[AcousticSummary]
    unavailable_recordings: dict[str, str]
    comparison: DescriptiveComparison | None
    candidates: list[AcousticCandidate]
    automatic_correspondence: list[AutomaticCorrespondence]
    limitations: list[str]
