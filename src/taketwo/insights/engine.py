"""Deterministic native-time comparisons. No review decisions or flaw scores."""

import math
import statistics

import numpy as np

from taketwo.analysis.alignment import validate_alignment
from taketwo.analysis.contracts import Interval
from taketwo.analysis.storage import validate_features
from taketwo.dataset.schema import canonical_json, content_hash
from taketwo.exploratory.contracts import ExploratoryReport

from .contracts import (
    AlignmentAnomaly,
    ComparativeReport,
    InsightConfig,
    InspectionItem,
    LocalMeasurements,
    ObservationGroup,
    PairedSegment,
)


def identifier(prefix, value):
    return prefix + content_hash(value)[:24]


def group_candidates(report):
    """Connected temporal components, with immutable raw evidence membership."""
    summaries = {r.recording_id: r for r in report.recordings}
    buckets = {}
    seen = set()
    for candidate in report.candidates:
        c = type(candidate).model_validate_json(canonical_json(candidate.model_dump(mode="json")))
        r = summaries.get(c.recording_id)
        numbers = [
            c.start_s,
            c.end_s,
            c.duration_s,
            c.median_energy_dbfs,
            c.frame_window_s,
            c.boundary_resolution_s,
        ]
        numbers += [
            v for v in (c.energy_delta_db, c.threshold_dbfs, c.threshold_delta_db) if v is not None
        ]
        if (
            c.id in seen
            or not r
            or c.feature_sha256 != r.feature_artifact.sha256
            or not all(math.isfinite(v) for v in numbers)
            or not 0 <= c.start_s < c.end_s <= r.duration_s
            or not math.isclose(c.duration_s, c.end_s - c.start_s, abs_tol=1e-9)
            or min(c.frame_window_s, c.boundary_resolution_s) <= 0
        ):
            raise ValueError("Invalid, duplicate or foreign candidate evidence.")
        if c.kind == "energy_change" and (c.energy_delta_db is None or c.energy_delta_db == 0):
            raise ValueError("Energy grouping requires a nonzero measured direction.")
        if c.kind != "energy_change" and c.energy_delta_db is not None:
            raise ValueError("Low-energy evidence cannot carry a change direction.")
        seen.add(c.id)
        direction = (
            "low_energy"
            if c.energy_delta_db is None
            else ("increase" if c.energy_delta_db > 0 else "decrease")
        )
        key = (
            c.recording_id,
            c.kind,
            direction,
            c.feature_sha256,
            c.method,
            c.threshold_dbfs,
            c.threshold_delta_db,
            c.frame_window_s,
            c.boundary_resolution_s,
        )
        buckets.setdefault(key, []).append(c)
    groups = []
    for key, values in sorted(buckets.items(), key=lambda item: str(item[0])):
        components = []
        for c in sorted(values, key=lambda c: (c.start_s, c.end_s, c.id)):
            # Touching intervals can join; no positive temporal gap is bridged.
            if components and c.start_s <= max(v.end_s for v in components[-1]) + 1e-9:
                components[-1].append(c)
            else:
                components.append([c])
        for items in components:
            deltas = [c.energy_delta_db for c in items if c.energy_delta_db is not None]
            levels = [c.median_energy_dbfs for c in items]
            start, end = min(c.start_s for c in items), max(c.end_s for c in items)
            groups.append(
                ObservationGroup(
                    id=identifier("g-", [c.id for c in items]),
                    recording_id=key[0],
                    kind=key[1],
                    direction=key[2],
                    start_s=start,
                    end_s=end,
                    duration_s=end - start,
                    candidate_ids=[c.id for c in items],
                    detection=items[0],
                    representative_delta_db=statistics.median(deltas) if deltas else None,
                    delta_range_db=[min(deltas), max(deltas)] if deltas else [],
                    median_energy_range_dbfs=[min(levels), max(levels)],
                    limitation="Connected same-direction windows are not independent events; "
                    "overlap can include another directional group. "
                    "No cause or flaw is established.",
                )
            )
    return sorted(groups, key=lambda g: (g.recording_id, g.start_s, g.end_s, g.id))


def local_measurements(features, start, end):
    """Clip disjoint hop cells to native interval; gaps remain unknown, never quiet."""
    energy, activity = features.series["energy"], features.series["activity"]
    starts = np.asarray(energy.start_samples, dtype=float) / 16000
    if not len(starts):
        return LocalMeasurements(
            observed_s=0,
            interval_s=end - start,
            complete=False,
            low_energy_s=None,
            median_energy_dbfs=None,
            energy_range_db=None,
            relative_energy_db=None,
        )
    # A hop cell ends at the next hop or its complete frame support, whichever is earlier.
    ends = np.minimum(
        np.r_[starts[1:], starts[-1] + energy.frame_length / 16000],
        starts + energy.frame_length / 16000,
    )
    widths = np.maximum(0, np.minimum(end, ends) - np.maximum(start, starts))
    selected = widths > 0
    observed = float(widths.sum())
    complete = math.isclose(observed, end - start, abs_tol=1e-8)
    levels = np.asarray(energy.values, dtype=float)[selected]
    quiet = float(widths[~np.asarray(activity.values, dtype=bool)].sum())
    median = float(np.median(levels)) if len(levels) else None
    return LocalMeasurements(
        observed_s=observed,
        interval_s=end - start,
        complete=complete,
        low_energy_s=quiet if observed else None,
        median_energy_dbfs=median,
        energy_range_db=float(np.quantile(levels, 0.9) - np.quantile(levels, 0.1))
        if len(levels)
        else None,
        relative_energy_db=median - features.energy_baseline_dbfs
        if median is not None and features.energy_baseline_dbfs is not None
        else None,
    )


def matching_reason(sources):
    if len(sources) != 2:
        return "A completed alignment for both selected recordings is required."
    a, b = [s.alignment for s in sources]
    if not a or not b or a.status != "succeeded" or b.status != "succeeded" or a.oov or b.oov:
        return "Partial, missing, failed or OOV alignment cannot establish complete correspondence."
    if (
        a.normalized_tokens != b.normalized_tokens
        or a.original_text != b.original_text
        or a.token_offsets != b.token_offsets
        or a.provenance.original_text_sha256 != b.provenance.original_text_sha256
    ):
        return "Canonical transcript identity and token offsets differ; matching is withheld."
    # Complete indices disambiguate supplied-text positions, never observed speech.
    for alignment in (a, b):
        if [w.token_index for w in alignment.words] != list(range(len(a.normalized_tokens))):
            return "Missing or ambiguous token-index coverage; matching is withheld."
    return None


def build(report, sources, implementation_sha256, phrase_spans=None, phrase_review_sha256=None):
    report = ExploratoryReport.model_validate_json(canonical_json(report.model_dump(mode="json")))
    summaries = {r.recording_id: r for r in report.recordings}
    if len(sources) != len(summaries) or {s.recording.id for s in sources} != set(summaries):
        raise ValueError("Comparative sources differ from exploratory members.")
    sources = sorted(sources, key=lambda s: s.recording.id != report.reference_id)
    for s in sources:
        r = summaries[s.recording.id]
        validate_features(s.features)
        if (
            s.features.provenance != r.provenance
            or s.feature_ref != r.feature_artifact
            or s.features.quality.duration_s != r.duration_s
            or content_hash(s.features.model_dump(mode="json")) != s.feature_ref.sha256
        ):
            raise ValueError("Comparative feature identity differs.")
        if s.alignment:
            validate_alignment(s.alignment)
            if (
                s.alignment.provenance != r.provenance
                or s.alignment_ref != r.alignment_artifact
                or not s.alignment_ref
                or content_hash(s.alignment.model_dump(mode="json")) != s.alignment_ref.sha256
                or s.features.alignment_sha256 != s.alignment_ref.sha256
            ):
                raise ValueError("Comparative alignment identity differs.")
        elif r.alignment_artifact:
            raise ValueError("Comparative alignment source is absent.")
    config = InsightConfig()
    groups = group_candidates(report)
    reason = (
        matching_reason(sources)
        if report.pair_id
        else "Reference-only inspection has no paired correspondence."
    )
    segments, anomalies = [], []

    def segment(first, last, kind):
        a, b = sources
        left = Interval(
            start_s=a.alignment.words[first].start_s,
            end_s=a.alignment.words[last - 1].end_s,
            label="reference",
        )
        right = Interval(
            start_s=b.alignment.words[first].start_s,
            end_s=b.alignment.words[last - 1].end_s,
            label="participant",
        )
        lm = local_measurements(a.features, left.start_s, left.end_s)
        rm = local_measurements(b.features, right.start_s, right.end_s)
        lg = left.start_s - a.alignment.words[first - 1].end_s if first else None
        rg = right.start_s - b.alignment.words[first - 1].end_s if first else None
        delta = (right.end_s - right.start_s) - (left.end_s - left.start_s)
        return PairedSegment(
            id=identifier("s-", [report.job_id, kind, first, last, report.dataset_sha256]),
            kind=kind,
            token_start=first,
            token_end=last,
            text=" ".join(a.alignment.normalized_tokens[first:last]),
            reference=left,
            participant=right,
            reference_measurements=lm,
            participant_measurements=rm,
            duration_delta_s=delta,
            relative_duration_delta_percent=100 * delta / (left.end_s - left.start_s),
            reference_gap_before_s=lg,
            participant_gap_before_s=rg,
            gap_delta_s=rg - lg if lg is not None and rg is not None else None,
            relative_energy_delta_db=rm.relative_energy_db - lm.relative_energy_db
            if lm.complete
            and rm.complete
            and lm.relative_energy_db is not None
            and rm.relative_energy_db is not None
            else None,
            limitation="Provisional supplied-text correspondence. Spoken text and timing accuracy "
            "are unverified; word length is not pronunciation or delivery quality. "
            "Relative digital energy depends on recording conditions.",
        )

    if reason is None:
        segments = [segment(i, i + 1, "word") for i in range(len(sources[0].alignment.words))]
    phrase_reason = (
        "No common independently reviewed phrase partition is available; "
        "phrase comparison is withheld."
    )
    if phrase_spans is not None and reason is None:
        position = 0
        for start, end in phrase_spans:
            if start != position or not start < end <= len(segments):
                raise ValueError("Phrase partition must cover canonical tokens in order.")
            position = end
        if position != len(segments):
            raise ValueError("Phrase partition omits canonical tokens.")
        segments.extend(segment(start, end, "phrase") for start, end in phrase_spans)
        phrase_reason = None
    for source in sources:
        alignment = source.alignment
        if not alignment or alignment.status not in {"succeeded", "partial"}:
            continue
        words = alignment.words
        for before, after in zip(words, words[1:], strict=False):
            if after.token_index != before.token_index + 1:
                continue
            gap = after.start_s - before.end_s
            paired = next(
                (s for s in segments if s.kind == "word" and s.token_start == after.token_index),
                None,
            )
            other_gap = None
            if paired:
                other_gap = (
                    paired.participant_gap_before_s
                    if source.recording.id == report.reference_id
                    else paired.reference_gap_before_s
                )
            if gap < config.anomaly_gap_s or (
                other_gap is not None and gap - other_gap < config.anomaly_relative_gap_s
            ):
                continue
            interval = Interval(start_s=before.end_s, end_s=after.start_s, label="alignment gap")
            anomalies.append(
                AlignmentAnomaly(
                    id=identifier("a-", [source.alignment_ref.sha256, before.token_index]),
                    recording_id=source.recording.id,
                    before_token_index=before.token_index,
                    before_word=before,
                    after_word=after,
                    gap=interval,
                    context=Interval(
                        start_s=before.start_s, end_s=after.end_s, label="gap context"
                    ),
                    measurement=local_measurements(
                        source.features, interval.start_s, interval.end_s
                    ),
                    reason=f"Consecutive text tokens have a {gap:.3f} s machine gap (rule >=1 s)"
                    + (
                        f", {gap - other_gap:+.3f} s relative to the other take (rule >=0.5 s)."
                        if other_gap is not None
                        else "."
                    )
                    + " Acoustic activity is checked separately; a gap is not proof of silence. "
                    "Pause, misalignment or repeated/omitted speech require listening; "
                    "alignment confidence is unavailable.",
                )
            )
    items = []

    def add(category, evidence, magnitude, ids, complete=True):
        limited = not complete or any(
            summaries[r].quality_flags
            or summaries[r].clipping_fraction > 0
            or summaries[r].rms < 0.001
            for r in ids
        )
        tier = {"alignment_anomaly": 0, "gap_difference": 1, "word_duration": 2, "group": 3}[
            category
        ]
        native = (
            evidence.start_s
            if category == "group"
            else evidence.gap.start_s
            if category == "alignment_anomaly"
            else evidence.reference.start_s
        )
        if category == "alignment_anomaly":
            selected_reason = (
                f"Automatic alignment leaves a {magnitude:.3f} s gap between "
                f"{evidence.before_word.label!r} and {evidence.after_word.label!r}, "
                f"meeting the {config.anomaly_gap_s:.3f} s inspection threshold. "
                f"Acoustic coverage is {evidence.measurement.observed_s:.3f} s; "
                + (
                    f"low-energy support is {evidence.measurement.low_energy_s:.3f} s. "
                    if evidence.measurement.low_energy_s is not None
                    else "low-energy support is unavailable. "
                )
                + "Check supplied text and automatic timing against the recording; "
                "this establishes neither a pause nor an alignment error. "
            )
        elif category == "gap_difference":
            selected_reason = (
                f"The absolute provisional gap difference {magnitude:.3f} s "
                "meets the 0.150 s inspection threshold. "
                f"Reference gap {evidence.reference_gap_before_s:.3f} s; "
                f"participant gap {evidence.participant_gap_before_s:.3f} s. "
                "Check the interval before the supplied-text word; "
                "a machine gap does not prove hesitation. "
            )
        elif category == "word_duration":
            selected_reason = (
                f"The absolute provisional word-duration difference {magnitude:.3f} s "
                "meets the 0.100 s inspection threshold. "
                "Check the assigned word boundaries; this is not a pronunciation judgment. "
            )
        else:
            rule = (
                f"absolute energy change at least {evidence.detection.threshold_delta_db:g} dB"
                if evidence.detection.threshold_delta_db is not None
                else "the configured low-energy activity rule"
            )
            selected_reason = (
                f"{len(evidence.candidate_ids)} source window(s) meet {rule}; "
                f"the compatible connected interval spans {magnitude:.3f} s. "
                "Longer grouped intervals appear first within this category; "
                "this is a presentation policy, not validated importance. "
            )
        item = InspectionItem(
            id=identifier("i-", [category, evidence.id]),
            category=category,
            evidence_id=evidence.id,
            quality_limited=limited,
            order_reason=selected_reason
            + (
                "Quality/support limited; shown after complete evidence. "
                if limited
                else "Complete native support without recording quality warnings. "
            )
            + f"Category order: anomaly, gap delta, word-duration delta, acoustic groups; "
            "within category larger measured duration "
            f"first ({magnitude:.3f} s); ties use native start then evidence ID. "
            "Inspection order is not severity, accuracy or confidence.",
        )
        items.append(((limited, tier, -magnitude, native, evidence.id), item))

    for a in anomalies:
        add(
            "alignment_anomaly",
            a,
            a.gap.end_s - a.gap.start_s,
            [a.recording_id],
            a.measurement.complete,
        )
    for s in segments:
        if s.kind != "word":
            continue
        # A gap anomaly already presents this following word's paired context.
        # Keep its full segment in the appendix without a second highlight.
        if any(a.before_token_index + 1 == s.token_start for a in anomalies):
            continue
        ids = [source.recording.id for source in sources]
        complete = s.reference_measurements.complete and s.participant_measurements.complete
        if s.gap_delta_s is not None and abs(s.gap_delta_s) >= 0.15:
            add("gap_difference", s, abs(s.gap_delta_s), ids, complete)
        elif abs(s.duration_delta_s) >= 0.1:
            add("word_duration", s, abs(s.duration_delta_s), ids, complete)
    for g in groups:
        add("group", g, g.duration_s, [g.recording_id])
    return ComparativeReport(
        config=config,
        implementation_sha256=implementation_sha256,
        exploratory_sha256=content_hash(report.model_dump(mode="json")),
        exploratory=report,
        groups=groups,
        segments=segments,
        anomalies=anomalies,
        inspection_order=[item for _, item in sorted(items, key=lambda item: item[0])],
        activity_delta_s=report.recordings[1].activity_support_s
        - report.recordings[0].activity_support_s
        if len(sources) == 2
        else None,
        low_energy_delta_s=report.recordings[1].low_energy_support_s
        - report.recordings[0].low_energy_support_s
        if len(sources) == 2
        else None,
        correspondence_unavailable_reason=reason,
        phrase_unavailable_reason=phrase_reason,
        phrase_review_sha256=phrase_review_sha256 or [],
        limitations=[
            "All comparisons are automatic and unverified. They never approve independent review.",
            "Digital energy cannot establish vocal effort or perceived loudness; "
            "no significance is asserted.",
            "Complete token indices disambiguate supplied text, not words actually spoken.",
            "No isolated noise reference is available; absence of a warning "
            "does not establish clean speech.",
            "Hop-cell measurements have 10 ms resolution and 25 ms window smearing; "
            "partial support stays unknown.",
        ],
    )
