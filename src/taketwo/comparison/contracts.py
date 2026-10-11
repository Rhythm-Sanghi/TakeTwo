"""Versioned scientific outputs for CLI consumers and the future workspace."""

import math
from datetime import date
from typing import Annotated, Literal

from pydantic import Field, model_validator

from taketwo.analysis.contracts import FeatureConfig, Interval, Provenance, QualityReport
from taketwo.dataset.schema import Digest, Identifier, Model, Text

Dimension = Literal["pacing", "pause_behavior", "energy_variation", "pitch_dynamics"]
State = Literal["ELIGIBLE", "PARTIALLY_ELIGIBLE", "INELIGIBLE", "REVIEW_REQUIRED"]
Fraction = Annotated[float, Field(ge=0, le=1)]
Nonnegative = Annotated[float, Field(ge=0)]


class Span(Model):
    start_s: Nonnegative
    end_s: Annotated[float, Field(gt=0)]

    @model_validator(mode="after")
    def width(self):
        if self.end_s <= self.start_s:
            raise ValueError("Expected positive-width native-time interval.")
        return self


class Reason(Model):
    code: Text
    message: Text


class Eligibility(Model):
    state: State
    reasons: list[Reason] = Field(default_factory=list)


class Policy(Model):
    version: Identifier = "delivery-v0"
    algorithm: Literal["contrastive-v1"] = "contrastive-v1"
    numerical_epsilon: Literal[1e-12] = 1e-12
    pacing_tolerance: Annotated[float, Field(ge=math.log(1.15))] = math.log(1.15)
    pacing_width: Literal[0.4054651081081644] = math.log(1.5)
    pause_floor_s: Literal[0.15] = 0.15
    pause_relative: Literal[0.25] = 0.25
    pause_width_s: Literal[0.75] = 0.75
    pause_calibrated_tolerance_s: Nonnegative = 0.0
    energy_tolerance_db: Annotated[float, Field(ge=3)] = 3.0
    energy_width_db: Literal[6.0] = 6.0
    pitch_tolerance_st: Annotated[float, Field(ge=2)] = 2.0
    pitch_width_st: Literal[4.0] = 4.0
    contour_energy_tolerance_db: Annotated[float, Field(gt=0)] = 6.0
    contour_pitch_tolerance_st: Annotated[float, Field(gt=0)] = 3.0
    minimum_coverage: Literal[0.8] = 0.8
    minimum_pitch_fraction: Literal[0.5] = 0.5
    minimum_phrase_s: Literal[0.5] = 0.5
    minimum_phrase_words: Literal[3] = 3
    minimum_phrases: Literal[2] = 2
    minimum_gaps: Literal[5] = 5
    weights: dict[Dimension, float] = Field(
        default_factory=lambda: {
            "pacing": 0.25,
            "pause_behavior": 0.25,
            "energy_variation": 0.25,
            "pitch_dynamics": 0.25,
        }
    )
    frozen: bool = False
    calibration_group_ids: list[Identifier] = Field(default_factory=list)
    validation_group_ids: list[Identifier] = Field(default_factory=list)
    calibration_evidence: Text | None = None

    @model_validator(mode="after")
    def policy(self):
        if self.weights != dict.fromkeys(
            ("pacing", "pause_behavior", "energy_variation", "pitch_dynamics"), 0.25
        ):
            raise ValueError("delivery rubric uses four fixed equal weights; no redistribution.")
        if set(self.calibration_group_ids) & set(self.validation_group_ids):
            raise ValueError("Calibration and validation groups overlap.")
        if self.frozen and (
            not self.calibration_evidence
            or not self.calibration_group_ids
            or not self.validation_group_ids
        ):
            raise ValueError("Frozen policy requires traceable calibration/validation evidence.")
        initial = {
            "pacing_tolerance": math.log(1.15),
            "pacing_width": math.log(1.5),
            "pause_floor_s": 0.15,
            "pause_relative": 0.25,
            "pause_width_s": 0.75,
            "pause_calibrated_tolerance_s": 0.0,
            "energy_tolerance_db": 3.0,
            "energy_width_db": 6.0,
            "pitch_tolerance_st": 2.0,
            "pitch_width_st": 4.0,
            "contour_energy_tolerance_db": 6.0,
            "contour_pitch_tolerance_st": 3.0,
        }
        if self.version == "delivery-v0" and any(getattr(self, k) != v for k, v in initial.items()):
            raise ValueError("Changed thresholds require a new policy version.")
        return self


class Label(Model):
    id: Identifier
    category: Dimension
    severity: Literal[1, 2, 3]
    interval: Span | None
    anchor_s: Nonnegative | None = None
    rationale: Text
    uncertainty_s: Nonnegative | None = None

    @model_validator(mode="after")
    def location(self):
        if (self.interval is None) == (self.anchor_s is None):
            raise ValueError("Provide an interval or a boundary anchor, exclusively.")
        if self.anchor_s is not None and self.category != "pause_behavior":
            raise ValueError("Only missing/short pause labels may be boundary events.")
        return self


class Review(Model):
    kind: Literal["review"] = "review"
    schema_version: Literal[1] = 1
    id: Identifier
    scope: Literal["transcript", "timing", "flaws"]
    provenance: Provenance
    alignment_sha256: Digest | None = None
    pair_id: Identifier | None = None
    reviewer_id: Identifier
    reviewed_on: str
    evidence_reference: Text
    independent: bool
    blinded_to_predictions: bool
    decision: Literal["approved", "rejected", "unresolved"]
    notes: Text
    corrected_text: Text | None = None
    words: list[Interval] = Field(default_factory=list)
    phrase_spans: list[tuple[int, int]] = Field(default_factory=list)
    labels: list[Label] = Field(default_factory=list)
    reviewed_spans: list[Span] = Field(default_factory=list)
    supersedes: Identifier | None = None

    @model_validator(mode="after")
    def scope_fields(self):
        date.fromisoformat(self.reviewed_on)
        if self.scope == "transcript":
            if not self.corrected_text or self.words or self.labels or self.phrase_spans:
                raise ValueError("Transcript review requires checked text, no timing/flaw labels.")
        elif self.scope == "timing":
            if not self.alignment_sha256 or not self.words or not self.phrase_spans:
                raise ValueError("Timing review needs original alignment hash, words and phrases.")
            if self.corrected_text or self.labels:
                raise ValueError("Keep transcript/flaw reviews separate from timing.")
        elif (
            not self.pair_id
            or not self.reviewed_spans
            or self.words
            or self.corrected_text
            or self.phrase_spans
        ):
            raise ValueError(
                "Flaw review needs pair and inspected spans, with no transcript/timing."
            )
        if len({label.id for label in self.labels}) != len(self.labels):
            raise ValueError("Duplicate review label IDs.")
        return self


class ArtifactRef(Model):
    path: Text
    sha256: Digest


class InputEvidence(Model):
    provenance: Provenance
    origin: Literal["source", "self_recorded", "synthetic"]
    family_id: Identifier
    speaker_id: Identifier
    duration_s: Annotated[float, Field(gt=0)]
    features: ArtifactRef
    alignment: ArtifactRef | None
    reviews: list[ArtifactRef]
    feature_config: FeatureConfig
    quality: QualityReport
    energy_baseline_dbfs: float | None
    pitch_baseline_hz: float | None
    spectral_frame_count: Annotated[int, Field(ge=0)]
    pitch_valid_fraction: Fraction
    speaking_rate_wpm: float | None
    articulation_rate_wpm: float | None


class Observation(Model):
    id: Identifier
    dimension: Dimension
    detector: Literal["rubric", "sustained_energy", "energy_step", "pitch_contour"]
    token_span: tuple[int, int]
    participant_interval: Span | None
    participant_anchor_s: Nonnegative | None = None
    reference_interval: Span | None
    reference_anchor_s: Nonnegative | None = None
    unit: Text
    reference: float | None
    participant: float | None
    delta: float | None
    tolerance: Annotated[float, Field(gt=0)]
    saturation_width: Annotated[float, Field(gt=0)]
    normalized_deviation: float | None
    excess: Nonnegative | None
    penalty: Fraction | None
    weight: Nonnegative
    scored: bool
    eligibility: Eligibility
    reference_valid_fraction: Fraction | None = None
    participant_valid_fraction: Fraction | None = None

    @model_validator(mode="after")
    def evidence(self):
        if not 0 <= self.token_span[0] < self.token_span[1]:
            raise ValueError("Observation requires a nonempty canonical token span.")
        for interval, anchor in (
            (self.participant_interval, self.participant_anchor_s),
            (self.reference_interval, self.reference_anchor_s),
        ):
            if (interval is None) == (anchor is None):
                raise ValueError("Each observation needs an interval or boundary anchor.")
        measurements = (
            self.reference,
            self.participant,
            self.delta,
            self.excess,
            self.normalized_deviation,
            self.penalty,
        )
        if self.eligibility.state == "ELIGIBLE":
            if any(v is None for v in measurements):
                raise ValueError("Eligible observations need all calculation evidence.")
        elif any(v is not None for v in measurements):
            raise ValueError("Withheld observations cannot contain a calculated penalty.")
        return self


class Explanation(Model):
    technical: Text
    plain: Text
    suggested_review: Text
    causal_scope: Literal["calculation_only"] = "calculation_only"


class Region(Model):
    id: Identifier
    category: Dimension
    detector: Text
    participant_interval: Span | None
    participant_anchor_s: Nonnegative | None
    reference_interval: Span | None
    reference_anchor_s: Nonnegative | None
    token_span: tuple[int, int]
    observation_ids: list[Identifier]
    severity: Literal[1, 2, 3]
    confidence: None = None
    confidence_reason: Literal["not_calibrated"] = "not_calibrated"
    reliability: Literal["reviewed"] = "reviewed"
    timing_uncertainty_s: None = None
    eligibility: Eligibility
    explanation: Explanation


class DimensionScore(Model):
    dimension: Dimension
    score: Annotated[float, Field(ge=0, le=100)] | None
    eligible_count: Annotated[int, Field(ge=0)]
    expected_count: Annotated[int, Field(ge=0)]
    coverage: Fraction
    eligible_weight: Nonnegative
    expected_weight: Nonnegative
    weighted_penalty: Nonnegative
    reasons: list[Reason]


class Report(Model):
    kind: Literal["comparison"] = "comparison"
    schema_version: Literal[1] = 1
    pair_id: Identifier | None
    dataset_version: Identifier
    dataset_sha256: Digest
    implementation_sha256: Digest
    policy: Policy
    policy_sha256: Digest
    inputs: list[InputEvidence]
    eligibility: Eligibility
    feature_eligibility: dict[Dimension, Eligibility]
    observations: list[Observation]
    regions: list[Region]
    dimensions: list[DimensionScore]
    overall_score: Annotated[float, Field(ge=0, le=100)] | None
    abstention_reasons: list[Reason]
    limitations: list[Text]

    @model_validator(mode="after")
    def integrity(self):
        if not 1 <= len(self.inputs) <= 2:
            raise ValueError("Report needs a reference and optional participant.")
        if len({o.id for o in self.observations}) != len(self.observations):
            raise ValueError("Observation IDs must be unique.")
        known = {o.id for o in self.observations}
        if any(not set(r.observation_ids) <= known for r in self.regions):
            raise ValueError("Region refers to unknown measurements.")
        if self.overall_score is not None and (
            len(self.dimensions) != 4 or any(d.score is None for d in self.dimensions)
        ):
            raise ValueError("Overall score requires all four dimensions.")
        for o in self.observations:
            for interval, anchor, member in (
                (o.reference_interval, o.reference_anchor_s, self.inputs[0]),
                (o.participant_interval, o.participant_anchor_s, self.inputs[-1]),
            ):
                if (interval is not None and interval.end_s > member.duration_s) or (
                    anchor is not None and anchor > member.duration_s
                ):
                    raise ValueError("Evidence location exceeds native recording duration.")
        return self


class EvaluationConfig(Model):
    mode: Literal["pilot", "held_out", "software_fixture"] = "pilot"
    split: Literal["validation", "test"] = "test"
    iou_threshold: Annotated[float, Field(gt=0, le=1)] = 0.5
    boundary_tolerance_s: Annotated[float, Field(gt=0)] = 0.2
    bootstrap_resamples: Literal[1000] = 1000
    seed: int = 17


class Match(Model):
    prediction_id: Identifier
    label_id: Identifier
    iou: Fraction | None
    start_error_s: Nonnegative
    end_error_s: Nonnegative | None


class Metrics(Model):
    true_positive: int
    false_positive: int
    false_negative: int
    precision: Fraction | None
    recall: Fraction | None
    f1: Fraction | None
    median_boundary_error_s: Nonnegative | None
    p90_boundary_error_s: Nonnegative | None


class Evaluation(Model):
    kind: Literal["evaluation"] = "evaluation"
    schema_version: Literal[1] = 1
    config: EvaluationConfig
    implementation_sha256: Digest
    dataset_sha256: Digest
    report_sha256: list[Digest]
    review_sha256: list[Digest]
    eligibility: Eligibility
    origin: Literal["human", "synthetic", "unavailable"]
    independent_real_validation: bool
    policy_sha256: Digest | None
    metrics: Metrics | None
    interval_metrics: Metrics | None
    boundary_event_metrics: Metrics | None
    by_category: dict[Dimension, Metrics]
    by_severity: dict[str, Metrics]
    matches: list[Match]
    false_positive_ids: list[Identifier]
    false_negative_ids: list[Identifier]
    family_ids: list[Identifier]
    clean_reviewed_duration_s: Nonnegative | None
    false_flags_in_clean_spans: Annotated[int, Field(ge=0)] | None
    false_flags_per_clean_minute: Nonnegative | None
    severity_spearman: Annotated[float, Field(ge=-1, le=1)] | None
    severity_matched_count: Annotated[int, Field(ge=0)]
    uncertainty: dict[str, object]
    limitations: list[Text]
