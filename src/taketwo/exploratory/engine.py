"""Summarize existing native artifacts; never detect or score delivery flaws."""

import math
from dataclasses import dataclass

import numpy as np

from taketwo.analysis.alignment import validate_alignment
from taketwo.analysis.contracts import AlignmentResult, FeatureResult
from taketwo.analysis.storage import validate_features
from taketwo.comparison.contracts import ArtifactRef
from taketwo.dataset.audio import sha256
from taketwo.dataset.schema import Dataset, Recording, canonical_json, content_hash

from .contracts import (
    AcousticCandidate,
    AcousticSummary,
    AutomaticAlignment,
    AutomaticCorrespondence,
    DescriptiveComparison,
    ExploratoryConfig,
    ExploratoryReport,
)


@dataclass
class Source:
    recording: Recording
    features: FeatureResult
    feature_ref: ArtifactRef
    alignment: AlignmentResult | None = None
    alignment_ref: ArtifactRef | None = None


def quantiles(values):
    values = [v for v in values if v is not None]
    return np.quantile(values, [0.1, 0.5, 0.9], method="linear").tolist() if values else []


def summarize(source: Source, config: ExploratoryConfig):
    r, f, alignment = source.recording, source.features, source.alignment
    # Validate even callers that constructed a model with unchecked model_copy updates.
    FeatureResult.model_validate_json(canonical_json(f.model_dump(mode="json")))
    validate_features(f)
    if (
        r.id != f.provenance.recording_id
        or r.dataset_version != f.provenance.dataset_version
        or sha256(r.transcript.text.encode("utf-8")) != f.provenance.original_text_sha256
        or r.normalized_sha256 != f.provenance.audio_sha256
        or r.sample_sha256 != f.provenance.sample_sha256
        or r.transcript_sha256 != f.provenance.transcript_sha256
        or r.normalized_info.frames != f.quality.sample_count
        or source.feature_ref.sha256 != content_hash(f.model_dump(mode="json"))
    ):
        raise ValueError("Exploratory source recording/feature identity differs.")
    aligned = None
    if alignment:
        validate_alignment(alignment)
        digest = content_hash(alignment.model_dump(mode="json"))
        if (
            alignment.provenance != f.provenance
            or f.alignment_sha256 != digest
            or source.alignment_ref is None
            or source.alignment_ref.sha256 != digest
        ):
            raise ValueError("Exploratory alignment identity differs.")
        span = alignment.words[-1].end_s - alignment.words[0].start_s if alignment.words else None
        usable = alignment.status == "succeeded" and len(alignment.words) >= 2 and not alignment.oov
        aligned = AutomaticAlignment(
            status=alignment.status,
            transcript_sha256=f.provenance.transcript_sha256,
            original_text_sha256=f.provenance.original_text_sha256,
            words=alignment.words,
            token_count=len(alignment.normalized_tokens),
            word_span_s=span,
            estimated_words_per_minute=60 * len(alignment.words) / span
            if usable and span
            else None,
            rate_unavailable_reason=None
            if usable
            else "Complete unambiguous machine word coverage is required.",
            diagnostics=[d.message for d in alignment.diagnostics],
        )
    energy, activity = f.series["energy"], f.series["activity"]
    starts = np.asarray(energy.start_samples, dtype=float) / 16000
    observed_end = (energy.start_samples[-1] + energy.frame_length) / 16000 if len(starts) else 0.0
    # Partition observed support into nonoverlapping hop cells. Original full-window
    # activity/quiet unions can overlap at transitions; they are not silence durations.
    ends = np.r_[starts[1:], observed_end] if len(starts) else np.array([])
    active = np.asarray(activity.values, dtype=bool)
    widths = ends - starts
    candidates = []

    def candidate(
        kind, start, end, values, delta=None, method="acoustic-v1 activity mask, hop-cell partition"
    ):
        identifier = content_hash(
            {
                "recording": r.id,
                "features": source.feature_ref.sha256,
                "kind": kind,
                "start": start,
                "end": end,
                "config": config.model_dump(mode="json"),
            }
        )
        candidates.append(
            AcousticCandidate(
                id="c-" + identifier[:24],
                recording_id=r.id,
                feature_sha256=source.feature_ref.sha256,
                kind=kind,
                start_s=float(start),
                end_s=float(end),
                duration_s=float(end - start),
                median_energy_dbfs=float(np.median(values)),
                energy_delta_db=delta,
                method=method,
                threshold_dbfs=f.energy_baseline_dbfs - f.config.activity_drop_db
                if delta is None and f.energy_baseline_dbfs is not None
                else None,
                threshold_delta_db=config.energy_step_db if delta is not None else None,
                frame_window_s=energy.frame_length / 16000,
                boundary_resolution_s=energy.hop_length / 16000,
                explanation=(
                    (
                        f"Observed low-energy support for {end - start:.2f} s; "
                        f"median frame level {np.median(values):.1f} dBFS."
                    )
                    if delta is None
                    else (
                        f"Adjacent {config.energy_window_s:g} s windows differ by "
                        f"{delta:+.1f} dB in median digital energy."
                    )
                ),
                limitation=(
                    "Automatic, unverified acoustic event. Noise, breath, intentional pause "
                    "and dropout cannot be distinguished. Boundaries follow frame hops, "
                    "not exact speech onsets."
                ),
            )
        )

    i = 0
    while i < len(starts):
        if active[i]:
            i += 1
            continue
        j = i + 1
        while j < len(starts) and not active[j]:
            j += 1
        start, end = float(starts[i]), float(ends[j - 1])
        if end - start + 1e-12 >= config.minimum_quiet_s:
            kind = (
                "recording_low_energy"
                if i == 0 and j == len(starts)
                else "leading_low_energy"
                if i == 0
                else "trailing_low_energy"
                if j == len(starts)
                else "internal_low_energy"
            )
            candidate(kind, start, end, energy.values[i:j])
        i = j
    bins = []
    for index in range(int(observed_end / config.energy_window_s)):
        left, right = index * config.energy_window_s, (index + 1) * config.energy_window_s
        indices = [
            i
            for i, start in enumerate(starts)
            if start >= left and (energy.start_samples[i] + energy.frame_length) / 16000 <= right
        ]
        if len(indices) >= 2:
            bins.append((index, left, right, [energy.values[i] for i in indices]))
    for before, after in zip(bins, bins[1:], strict=False):
        if after[0] != before[0] + 1:
            continue
        delta = float(np.median(after[3]) - np.median(before[3]))
        if abs(delta) + 1e-12 >= config.energy_step_db:
            candidate(
                "energy_change",
                before[1],
                after[2],
                before[3] + after[3],
                delta,
                "exploratory-v1 adjacent-window median energy difference",
            )
    pitch = f.series["f0"].values
    accepted = sum(v is not None for v in pitch)
    summary = AcousticSummary(
        recording_id=r.id,
        filename=r.original_filename,
        role=r.role,
        origin=r.origin,
        provenance=f.provenance,
        feature_artifact=source.feature_ref,
        alignment_artifact=source.alignment_ref,
        feature_config=f.config,
        duration_s=f.quality.duration_s,
        source_sample_rate_hz=r.original_info.sample_rate_hz,
        rms=f.quality.rms,
        peak=f.quality.peak,
        clipping_fraction=f.quality.clipping_fraction,
        energy_baseline_dbfs=f.energy_baseline_dbfs,
        energy_quantiles_dbfs=quantiles(energy.values),
        active_energy_range_db=f.energy_range_db,
        activity_support_s=float(widths[active].sum()),
        low_energy_support_s=float(widths[~active].sum()),
        observed_support_s=observed_end,
        unobserved_tail_s=f.quality.duration_s - observed_end,
        accepted_pitch_frames=accepted,
        pitch_frames=len(pitch),
        accepted_pitch_fraction=accepted / len(pitch) if pitch else None,
        pitch_baseline_hz=f.pitch_baseline_hz,
        voicing_probability_quantiles=quantiles(f.series["voicing_probability"].values),
        quality_flags=f.quality.flags,
        automatic_alignment=aligned,
    )
    return summary, candidates


def build(
    dataset: Dataset,
    sources: list[Source],
    *,
    reference_id,
    pair_id,
    job_id,
    processing_state,
    implementation_sha256,
    unavailable=None,
):
    config = ExploratoryConfig()
    pair = next((p for p in dataset.pairs if p.id == pair_id), None)
    if pair_id and (pair is None or pair.reference_id != reference_id):
        raise ValueError("Exploratory pair does not belong to reference.")
    expected = [reference_id] + ([pair.participant_id] if pair else [])
    identifiers = [s.recording.id for s in sources]
    if (
        not sources
        or len(set(identifiers)) != len(identifiers)
        or any(i not in expected for i in identifiers)
    ):
        raise ValueError("Exploratory sources must be distinct selected job members.")
    records = {r.id: r for r in dataset.recordings}
    if reference_id not in records or records[reference_id].role != "reference":
        raise ValueError("Exploratory reference must be a dataset reference recording.")
    if pair and (
        pair.participant_id not in records or records[pair.participant_id].role != "participant"
    ):
        raise ValueError("Exploratory pair member must be a participant recording.")
    if any(records.get(s.recording.id) != s.recording for s in sources):
        raise ValueError("Exploratory source differs from the current dataset recording.")
    summaries, candidates = [], []
    for source in sources:
        summary, items = summarize(source, config)
        summaries.append(summary)
        candidates.extend(items)
    summaries.sort(key=lambda item: expected.index(item.recording_id))
    comparison, correspondence = None, []
    if pair and len(summaries) == 2:
        reference, participant = summaries
        delta = participant.duration_s - reference.duration_s
        rms_delta = (
            20 * math.log10(participant.rms / reference.rms)
            if min(reference.rms, participant.rms) >= 0.001
            else None
        )
        energy_delta = (
            participant.active_energy_range_db - reference.active_energy_range_db
            if participant.active_energy_range_db is not None
            and reference.active_energy_range_db is not None
            else None
        )
        comparison = DescriptiveComparison(
            duration_delta_s=delta,
            absolute_duration_difference_s=abs(delta),
            relative_duration_delta_percent=100 * delta / reference.duration_s,
            rms_level_delta_db=rms_delta,
            active_energy_range_delta_db=energy_delta,
            interpretation=(
                (
                    f"The participant recording is {abs(delta):.3f} s "
                    f"{'shorter' if delta < 0 else 'longer'} "
                    f"({abs(100 * delta / reference.duration_s):.2f}% of reference duration). "
                    if delta
                    else "The recordings have equal duration. "
                )
                + "This whole-recording difference does not establish speech rate or a pacing flaw."
            ),
            evidence_keys=[
                "comparison.duration_delta_s",
                "comparison.relative_duration_delta_percent",
                "recordings.duration_s",
            ],
            notes=[
                (
                    "RMS/energy depend on microphone, gain and noise; digital amplitude "
                    "is not perceived loudness, calibrated SPL or vocal effort."
                ),
                "RMS level difference is withheld if either recording is near-silent.",
                "Energy activity is a heuristic, not verified speech duration.",
                "Same intended text does not verify the words actually spoken.",
            ],
        )
        a, b = [s.alignment for s in sorted(sources, key=lambda s: expected.index(s.recording.id))]
        if (
            a
            and b
            and a.status == b.status == "succeeded"
            and a.normalized_tokens == b.normalized_tokens
        ):
            correspondence = [
                AutomaticCorrespondence(
                    token_index=i, token=a.normalized_tokens[i], reference=left, participant=right
                )
                for i, (left, right) in enumerate(zip(a.words, b.words, strict=True))
            ]
    return ExploratoryReport(
        config=config,
        implementation_sha256=implementation_sha256,
        dataset_version=dataset.dataset_version,
        dataset_sha256=content_hash(dataset.model_dump(mode="json")),
        job_id=job_id,
        processing_state=processing_state,
        reference_id=reference_id,
        pair_id=pair_id,
        state="available" if len(summaries) == len(expected) else "partial",
        recordings=summaries,
        unavailable_recordings=unavailable or {},
        comparison=comparison,
        candidates=candidates,
        automatic_correspondence=correspondence,
        limitations=[
            (
                "Automatic acoustic observations are unverified, not "
                "delivery flaws or human review labels."
            ),
            "Energy activity can include noise and omit quiet speech. Silence is not a mistake.",
            (
                "RMS/dBFS are digital levels, not "
                "calibrated SPL or microphone-independent perceived loudness."
            ),
            (
                "Frame-hop candidate boundaries have 10 ms resolution with "
                "25 ms window smearing; unobserved tails remain unknown."
            ),
            (
                "Machine word times align supplied text; they "
                "do not verify it or establish timing accuracy."
            ),
            (
                "Automatic word-span rate includes internal gaps and "
                "uses unverified transcript words, not verified spoken-word counts."
            ),
            "No confidence, speaking-quality score or causal diagnosis is produced.",
        ],
    )
