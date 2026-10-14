"""Comparative-insights-v1 contracts: inspection order is never confidence."""

from typing import Literal

from pydantic import Field, model_validator

from taketwo.analysis.contracts import Interval
from taketwo.dataset.schema import Digest, Identifier, Model, content_hash
from taketwo.exploratory.contracts import AcousticCandidate, ExploratoryReport


class InsightConfig(Model):
    method: Literal["comparative-insights-v1"] = "comparative-insights-v1"
    grouping: Literal["overlap-or-touch/same-kind/same-sign/same-config"] = (
        "overlap-or-touch/same-kind/same-sign/same-config"
    )
    matching: Literal["complete-identical-indexed-transcript"] = (
        "complete-identical-indexed-transcript"
    )
    anomaly_gap_s: Literal[1.0] = 1.0
    anomaly_relative_gap_s: Literal[0.5] = 0.5
    initial_items: Literal[6] = 6
    ordering: Literal["quality-first/anomaly/gap/duration/groups/native-id"] = (
        "quality-first/anomaly/gap/duration/groups/native-id"
    )


class ObservationGroup(Model):
    id: Identifier
    recording_id: Identifier
    kind: str
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    duration_s: float = Field(gt=0)
    direction: Literal["increase", "decrease", "low_energy"]
    candidate_ids: list[Identifier] = Field(min_length=1)
    representative_delta_db: float | None
    delta_range_db: list[float]
    median_energy_range_dbfs: list[float]
    detection: AcousticCandidate
    limitation: str


class LocalMeasurements(Model):
    observed_s: float = Field(ge=0)
    interval_s: float = Field(gt=0)
    complete: bool
    low_energy_s: float | None
    median_energy_dbfs: float | None
    energy_range_db: float | None
    relative_energy_db: float | None


class PairedSegment(Model):
    id: Identifier
    kind: Literal["word", "phrase"]
    token_start: int = Field(ge=0)
    token_end: int = Field(gt=0)
    text: str
    reference: Interval
    participant: Interval
    reference_measurements: LocalMeasurements
    participant_measurements: LocalMeasurements
    duration_delta_s: float
    relative_duration_delta_percent: float
    reference_gap_before_s: float | None
    participant_gap_before_s: float | None
    gap_delta_s: float | None
    relative_energy_delta_db: float | None
    status: Literal["automatic_unverified"] = "automatic_unverified"
    limitation: str


class AlignmentAnomaly(Model):
    id: Identifier
    recording_id: Identifier
    before_token_index: int
    before_word: Interval
    after_word: Interval
    gap: Interval
    context: Interval
    measurement: LocalMeasurements
    reason: str
    alignment_confidence: None = None
    status: Literal["automatic_unverified"] = "automatic_unverified"


class InspectionItem(Model):
    id: Identifier
    category: Literal["alignment_anomaly", "gap_difference", "word_duration", "group"]
    evidence_id: Identifier
    quality_limited: bool
    order_reason: str


class ComparativeReport(Model):
    kind: Literal["comparative_insights"] = "comparative_insights"
    schema_version: Literal[1] = 1
    config: InsightConfig
    implementation_sha256: Digest
    exploratory_sha256: Digest
    # Contains all original windows and provenance once; no duplicated feature arrays.
    exploratory: ExploratoryReport
    groups: list[ObservationGroup]
    segments: list[PairedSegment]
    anomalies: list[AlignmentAnomaly]
    inspection_order: list[InspectionItem]
    activity_delta_s: float | None
    low_energy_delta_s: float | None
    correspondence_unavailable_reason: str | None
    phrase_unavailable_reason: str | None
    phrase_review_sha256: list[Digest] = Field(default_factory=list)
    limitations: list[str]

    @model_validator(mode="after")
    def evidence_inventory(self):
        candidates = self.exploratory.candidates
        linked = [i for group in self.groups for i in group.candidate_ids]
        if sorted(linked) != sorted(c.id for c in candidates):
            raise ValueError("Every raw candidate must belong to exactly one group.")
        if self.exploratory_sha256 != content_hash(self.exploratory.model_dump(mode="json")):
            raise ValueError("Comparative exploratory identity differs.")
        return self
