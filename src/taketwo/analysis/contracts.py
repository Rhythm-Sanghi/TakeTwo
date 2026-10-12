"""Versioned derived contracts, independent of the immutable dataset v1 schema."""

from typing import Annotated, Literal

from pydantic import Field, model_validator

from taketwo.dataset.schema import Digest, Identifier, Model, Text

from .limits import DEFAULT_MAX_ANALYSIS_DURATION_S, maximum_analysis_duration_s

Positive = Annotated[float, Field(gt=0)]


class FeatureConfig(Model):
    algorithm: Literal["acoustic-v1"] = "acoustic-v1"
    sample_rate_hz: Literal[16000] = 16000
    frame_length: Literal[400] = 400
    hop_length: Literal[160] = 160
    n_fft: Literal[512] = 512
    pitch_frame_length: Literal[1024] = 1024
    fmin_hz: Annotated[float, Field(ge=60, le=250)] = 60.0
    fmax_hz: Annotated[float, Field(ge=300, le=800)] = 500.0
    voicing_threshold: Annotated[float, Field(ge=0, le=1)] = 0.8
    energy_floor: Literal[1e-6] = 1e-6
    activity_drop_db: Annotated[float, Field(gt=0, le=60)] = 25.0
    minimum_pause_s: Annotated[float, Field(ge=0.05, le=1)] = 0.15
    maximum_duration_s: Annotated[float, Field(gt=0, le=DEFAULT_MAX_ANALYSIS_DURATION_S)] = Field(
        default_factory=maximum_analysis_duration_s
    )


class Diagnostic(Model):
    code: Text
    message: Text
    recovery: Text


class Resource(Model):
    path: Text
    sha256: Digest
    version: Text
    license: Text
    source_url: Text


class AlignmentConfig(Model):
    backend: Literal["mfa"] = "mfa"
    command: Annotated[list[Text], Field(min_length=1)]
    expected_version: Text
    model: Resource
    dictionary: Resource
    timeout_s: Annotated[float, Field(gt=0, le=1800)] = 120.0
    # Explicit one-token spoken forms. Multiword expansions require corrected transcript.
    replacements: dict[str, Text] = Field(default_factory=dict)


class Interval(Model):
    start_s: Annotated[float, Field(ge=0)]
    end_s: Positive
    label: Text
    token_index: Annotated[int, Field(ge=0)] | None = None

    @model_validator(mode="after")
    def width(self) -> "Interval":
        if self.start_s >= self.end_s:
            raise ValueError("interval must have positive width")
        return self


class Provenance(Model):
    recording_id: Identifier
    dataset_version: Identifier
    audio_sha256: Digest
    sample_sha256: Digest
    transcript_sha256: Digest
    original_text_sha256: Digest
    transcript_verified: bool
    versions: dict[str, Text]
    implementation_sha256: Digest


class AlignmentResult(Model):
    kind: Literal["alignment"] = "alignment"
    schema_version: Literal[1] = 1
    provenance: Provenance
    config: AlignmentConfig
    duration_s: Positive
    original_text: Text
    normalized_tokens: list[Text]
    token_offsets: list[tuple[int, int]]
    status: Literal["succeeded", "partial", "failed", "cancelled", "timeout"]
    words: list[Interval] = Field(default_factory=list)
    phones: list[Interval] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    oov: list[Text] = Field(default_factory=list)
    backend_version: str | None = None
    output_sha256: Digest | None = None
    prepared_audio_sha256: Digest | None = None
    log: str = ""
    timing_uncertainty_s: None = None
    independently_reviewed: Literal[False] = False


class Series(Model):
    unit: Text
    frame_length: Annotated[int, Field(gt=0)]
    hop_length: Annotated[int, Field(gt=0)]
    start_samples: list[int]
    times_s: list[float]
    values: list[float | None]


class QualityReport(Model):
    sample_count: Annotated[int, Field(gt=0)]
    duration_s: Positive
    mean: float
    rms: Annotated[float, Field(ge=0)]
    peak: Annotated[float, Field(ge=0)]
    clipping_fraction: Annotated[float, Field(ge=0, le=1)]
    flags: list[Text]
    spectral_covered_until_s: Annotated[float, Field(ge=0)]
    pitch_covered_until_s: Annotated[float, Field(ge=0)]


class FeatureResult(Model):
    kind: Literal["features"] = "features"
    schema_version: Literal[1] = 1
    provenance: Provenance
    config: FeatureConfig
    quality: QualityReport
    series: dict[str, Series]
    frequencies_hz: list[float]
    spectrum_power: list[list[float]]
    mfcc: list[list[float]]
    waveform: list[tuple[int, int, float, float]]
    activity: list[Interval]
    low_energy: list[Interval]
    voiced_regions: list[Interval]
    unvoiced_regions: list[Interval]
    pauses: list[Interval]
    alignment_sha256: Digest | None
    speaking_rate_wpm: float | None
    articulation_rate_wpm: float | None
    rate_unavailable_reason: str | None
    energy_baseline_dbfs: float | None
    pitch_baseline_hz: float | None
    energy_range_db: float | None
    pitch_range_semitones: float | None
    diagnostics: list[Diagnostic]
