"""Token-corresponding native-time aggregates, detectors, templates and delivery-v0."""

import math
from dataclasses import dataclass, field

import numpy as np

from taketwo.analysis.contracts import AlignmentResult, FeatureResult, Interval
from taketwo.dataset.schema import Pair, Recording, content_hash

from .contracts import (
    ArtifactRef,
    DimensionScore,
    Eligibility,
    Explanation,
    InputEvidence,
    Observation,
    Policy,
    Region,
    Report,
    Review,
    Span,
)
from .eligibility import DIMENSIONS, combine, decision, pair_gate, reason, recording_gates


@dataclass
class Evidence:
    recording: Recording
    features: FeatureResult
    feature_ref: ArtifactRef
    alignment: AlignmentResult | None = None
    alignment_ref: ArtifactRef | None = None
    reviews: list[Review] = field(default_factory=list)
    review_refs: list[ArtifactRef] = field(default_factory=list)

    def summary(self):
        return InputEvidence(
            provenance=self.features.provenance,
            origin=self.recording.origin,
            family_id=self.recording.family_id,
            speaker_id=self.recording.speaker_id,
            duration_s=self.features.quality.duration_s,
            features=self.feature_ref,
            alignment=self.alignment_ref,
            reviews=sorted(self.review_refs, key=lambda r: r.sha256),
            feature_config=self.features.config,
            quality=self.features.quality,
            energy_baseline_dbfs=self.features.energy_baseline_dbfs,
            pitch_baseline_hz=self.features.pitch_baseline_hz,
            spectral_frame_count=len(self.features.series["energy"].values),
            pitch_valid_fraction=(
                sum(v is not None for v in self.features.series["f0"].values)
                / len(self.features.series["f0"].values)
            )
            if self.features.series["f0"].values
            else 0.0,
            speaking_rate_wpm=self.features.speaking_rate_wpm,
            articulation_rate_wpm=self.features.articulation_rate_wpm,
        )


def span(words: list[Interval], start: int, end: int) -> Span:
    return Span(start_s=words[start].start_s, end_s=words[end - 1].end_s)


def frame_values(features: FeatureResult, interval: Span, name: str):
    """Use full observed supports, independently for each native frame clock."""
    series = features.series[name]
    indices = [
        i
        for i, sample in enumerate(series.start_samples)
        if sample / 16000 >= interval.start_s
        and (sample + series.frame_length) / 16000 <= interval.end_s
    ]
    supports = [
        (series.start_samples[i] / 16000, (series.start_samples[i] + series.frame_length) / 16000)
        for i in indices
    ]
    covered, last = 0.0, interval.start_s
    for start, end in supports:
        covered += max(0.0, end - max(last, start))
        last = max(last, end)
    coverage = min(1.0, covered / (interval.end_s - interval.start_s))
    valid = []
    for i in indices:
        value = series.values[i]
        if value is None:
            continue
        if name == "relative_energy" and features.series["activity"].values[i] != 1:
            continue
        if name == "relative_pitch" and (
            features.series["voiced"].values[i] != 1
            or features.series["voicing_probability"].values[i] < 0.8
        ):
            continue
        valid.append(value)
    fraction = len(valid) / len(indices) if indices else 0.0
    return valid, coverage, fraction


def clipped(features: FeatureResult, interval: Span) -> bool:
    return any(
        start / 16000 < interval.end_s
        and end / 16000 > interval.start_s
        and max(abs(low), abs(high)) >= 0.999
        for start, end, low, high in features.waveform
    )


def acoustic_gate(features: FeatureResult, interval: Span, name: str, base: Eligibility):
    if base.state != "ELIGIBLE":
        return [], base, 0.0
    values, coverage, fraction = frame_values(features, interval, name)
    issues = []
    if clipped(features, interval):
        issues.append(
            reason("local_clipping", "Observed waveform clipping contaminates this span.")
        )
    if coverage + 1e-12 < 0.8 or not values:
        issues.append(
            reason("frame_coverage", "Insufficient complete observed frames in this span.")
        )
    if name == "relative_pitch" and fraction < 0.5:
        issues.append(
            reason("pitch_coverage", "Fewer than 50% of observed pitch frames are reliable.")
        )
    return values, decision(issues), fraction


def gap(features: FeatureResult, left: Interval, right: Interval, base: Eligibility):
    width = right.start_s - left.end_s
    if base.state != "ELIGIBLE":
        return None, base
    # A sub-150 ms gap is zero in delivery-v0, not an inferred silence interval.
    if width < 0.15:
        return 0.0, base
    interval = Span(start_s=left.end_s, end_s=right.start_s)
    values, coverage, _ = frame_values(features, interval, "activity")
    if coverage + 1e-12 < 0.8 or not values or any(v != 0 for v in values):
        return None, decision(
            [
                reason(
                    "pause_not_corroborated",
                    "The aligned gap lacks sufficient "
                    "low-energy frame support; noise/breath/mismatch needs review.",
                )
            ]
        )
    if clipped(features, interval):
        return None, decision([reason("local_clipping", "Clipping contaminates this gap.")])
    return width, base


def excursion(values):
    return float(np.diff(np.quantile(values, [0.1, 0.9], method="linear"))[0])


def observation(
    identity,
    dimension,
    detector,
    tokens,
    ref_span,
    part_span,
    unit,
    reference,
    participant,
    tolerance,
    width,
    weight,
    gate,
    *,
    scored=True,
    log_ratio=False,
    ref_anchor=None,
    part_anchor=None,
    fractions=(None, None),
):
    eligible = gate.state == "ELIGIBLE" and reference is not None and participant is not None
    delta = (
        (math.log(participant / reference) if log_ratio else participant - reference)
        if eligible
        else None
    )
    excess = max(0.0, abs(delta) - tolerance) if delta is not None else None
    if delta is not None and math.isclose(abs(delta), tolerance, rel_tol=0, abs_tol=1e-12):
        excess = 0.0
    result = Observation(
        id="o-pending",
        dimension=dimension,
        detector=detector,
        token_span=tokens,
        participant_interval=part_span,
        participant_anchor_s=part_anchor,
        reference_interval=ref_span,
        reference_anchor_s=ref_anchor,
        unit=unit,
        reference=reference if eligible else None,
        participant=participant if eligible else None,
        delta=delta,
        tolerance=tolerance,
        saturation_width=width,
        normalized_deviation=delta / tolerance if delta is not None else None,
        excess=excess,
        penalty=min(1.0, excess / width) if excess is not None else None,
        weight=weight,
        scored=scored,
        eligibility=gate,
        reference_valid_fraction=fractions[0],
        participant_valid_fraction=fractions[1],
    )
    result.id = "o-" + content_hash([identity, result.model_dump(mode="json")])[:24]
    return result


def scores(observations: list[Observation], policy: Policy):
    results = []
    for dimension in DIMENSIONS:
        expected = [o for o in observations if o.dimension == dimension and o.scored]
        eligible = [
            o for o in expected if o.eligibility.state == "ELIGIBLE" and o.penalty is not None
        ]
        total = sum(o.weight for o in expected)
        usable = sum(o.weight for o in eligible)
        coverage = usable / total if total else 0.0
        minimum = policy.minimum_gaps if dimension == "pause_behavior" else policy.minimum_phrases
        issues = []
        if coverage + policy.numerical_epsilon < policy.minimum_coverage:
            issues.append(reason("score_coverage", "Eligible observation weight is below 80%."))
        if len(eligible) < minimum:
            issues.append(
                reason("score_count", f"At least {minimum} eligible observations are required.")
            )
        penalty = sum(o.weight * o.penalty for o in eligible)
        results.append(
            DimensionScore(
                dimension=dimension,
                score=100 * (1 - penalty / usable) if not issues else None,
                eligible_count=len(eligible),
                expected_count=len(expected),
                coverage=coverage,
                eligible_weight=usable,
                expected_weight=total,
                weighted_penalty=penalty,
                reasons=issues,
            )
        )
    return results


def regions(observations: list[Observation], policy: Policy) -> list[Region]:
    results = []
    for o in observations:
        if o.eligibility.state != "ELIGIBLE" or o.excess is None or o.excess <= 0:
            continue
        severity = (
            1
            if o.penalty <= 1 / 3 + policy.numerical_epsilon
            else 2
            if o.penalty <= 2 / 3 + policy.numerical_epsilon
            else 3
        )
        location = (
            f"{o.participant_interval.start_s:.3f}-{o.participant_interval.end_s:.3f} s"
            if o.participant_interval
            else f"boundary at {o.participant_anchor_s:.3f} s"
        )
        delta_unit = "natural-log rate ratio" if o.dimension == "pacing" else o.unit
        action = {
            "pacing": "Replay these words in both recordings; compare phrase duration "
            "and try a slower "
            "delivery."
            if o.delta > 0
            else "Replay these words; compare phrase duration and try a faster delivery.",
            "pause_behavior": "Replay this word boundary and try a shorter gap."
            if o.delta > 0
            else "Replay this word boundary and try retaining the reference pause.",
            "energy_variation": "Replay the marked words and compare relative energy emphasis; "
            "try a more even or more varied envelope as the context warrants.",
            "pitch_dynamics": "Replay the marked words and compare relative pitch movement; "
            "try the reference contour only if it fits the intended delivery.",
        }[o.dimension]
        technical = (
            f"{o.detector}; tokens [{o.token_span[0]},{o.token_span[1]}), {location}. "
            f"Reference={o.reference:.6g}, participant={o.participant:.6g} {o.unit}; "
            f"signed delta={o.delta:.6g} {delta_unit}; tolerance={o.tolerance:.6g}, "
            f"excess={o.excess:.6g}, saturation width={o.saturation_width:.6g}, "
            f"penalty={o.penalty:.6g}. {policy.version}; "
            f"{'rubric observation' if o.scored else 'evidence only; no extra score penalty'}. "
            "Timing is reviewed; statistical detection confidence and timing error are unmeasured."
        )
        plain = (
            f"At {location}, the measured {o.dimension.replace('_', ' ')} differs from "
            f"the selected reference beyond this policy's tolerance "
            f"({o.reference:.4g} versus {o.participant:.4g} {o.unit}). "
            "This flags an acoustic difference for listening, not proof of poor speaking."
        )
        results.append(
            Region(
                id="f-" + content_hash([policy.model_dump(mode="json"), o.id])[:24],
                category=o.dimension,
                detector=o.detector,
                participant_interval=o.participant_interval,
                participant_anchor_s=o.participant_anchor_s,
                reference_interval=o.reference_interval,
                reference_anchor_s=o.reference_anchor_s,
                token_span=o.token_span,
                observation_ids=[o.id],
                severity=severity,
                eligibility=o.eligibility,
                explanation=Explanation(technical=technical, plain=plain, suggested_review=action),
            )
        )
    # Adjacent rubric phrase flags merge for display only. Preserve observation calculations.
    merged = []
    for region in sorted(results, key=lambda r: (r.category, r.detector, r.token_span)):
        previous = merged[-1] if merged else None
        if (
            previous
            and region.detector == previous.detector == "rubric"
            and region.category == previous.category != "pause_behavior"
            and previous.token_span[1] == region.token_span[0]
            and region.participant_interval.start_s - previous.participant_interval.end_s <= 0.2
        ):
            previous.participant_interval.end_s = region.participant_interval.end_s
            previous.reference_interval.end_s = region.reference_interval.end_s
            previous.token_span = (previous.token_span[0], region.token_span[1])
            previous.observation_ids.extend(region.observation_ids)
            previous.severity = max(previous.severity, region.severity)
            previous.explanation.technical += " " + region.explanation.technical
            previous.explanation.plain += " " + region.explanation.plain
            previous.id = "f-" + content_hash(previous.observation_ids)[:24]
        else:
            merged.append(region)
    return sorted(
        merged,
        key=lambda r: (
            r.participant_interval.start_s if r.participant_interval else r.participant_anchor_s,
            r.id,
        ),
    )


def compare(
    reference: Evidence,
    participant: Evidence | None,
    pair: Pair | None,
    policy: Policy,
    dataset_sha256: str,
    implementation_sha256: str,
) -> Report:
    members = [reference] + ([participant] if participant else [])
    gates, words, phrases = [], [], []
    for evidence in members:
        if evidence.feature_ref.sha256 != content_hash(evidence.features.model_dump(mode="json")):
            raise ValueError("Feature artifact reference hash differs from numerical input.")
        if evidence.alignment is not None and (
            evidence.alignment_ref is None
            or evidence.alignment_ref.sha256
            != content_hash(evidence.alignment.model_dump(mode="json"))
        ):
            raise ValueError("Alignment artifact reference hash differs from input.")
        if sorted(ref.sha256 for ref in evidence.review_refs) != sorted(
            content_hash(review.model_dump(mode="json")) for review in evidence.reviews
        ):
            raise ValueError("Review artifact references differ from supplied evidence.")
        if any(review.scope == "flaws" for review in evidence.reviews):
            raise ValueError(
                "Flaw reviews are ground truth for evaluation only; "
                "do not supply them to the detector."
            )
        gate, timing, partition = recording_gates(
            evidence.recording, evidence.features, evidence.alignment, evidence.reviews, policy
        )
        gates.append(gate)
        words.append(timing)
        phrases.append(partition)
    pair_decision = pair_gate(
        pair, reference.recording, participant.recording if participant else None
    )
    if participant and phrases[0] != phrases[1]:
        pair_decision = decision(
            [reason("phrase_disagreement", "Reviewed phrase partitions differ.")], review=True
        )
    feature_gates = {d: combine([pair_decision, *[g[d] for g in gates]]) for d in DIMENSIONS}
    # PARTIALLY_ELIGIBLE means some dimensions/regions are available, never permission
    # to bypass a failed common gate on an individual observation.
    for d in DIMENSIONS:
        failed = [g for g in [pair_decision, *[x[d] for x in gates]] if g.state != "ELIGIBLE"]
        if failed:
            feature_gates[d] = decision(
                [r for g in failed for r in g.reasons],
                review=all(g.state == "REVIEW_REQUIRED" for g in failed),
            )
    identity = [
        policy.model_dump(mode="json"),
        [e.summary().model_dump(mode="json") for e in members],
    ]
    observations = []
    if (
        participant
        and pair_decision.state == "ELIGIBLE"
        and all(words)
        and phrases[0] == phrases[1]
    ):
        rf, pf = reference.features, participant.features
        rw, pw = words
        for start, end in phrases[0]:
            rs, ps = span(rw, start, end), span(pw, start, end)
            weight = rs.end_s - rs.start_s
            size_gate = (
                decision([])
                if (
                    end - start >= policy.minimum_phrase_words
                    and min(weight, ps.end_s - ps.start_s) >= policy.minimum_phrase_s
                )
                else decision(
                    [
                        reason(
                            "phrase_size",
                            "Phrase needs at least three words and 0.5 s in both recordings.",
                        )
                    ]
                )
            )
            for dimension in ("pacing", "energy_variation", "pitch_dynamics"):
                base = feature_gates[dimension]
                if base.state == "ELIGIBLE" and size_gate.state != "ELIGIBLE":
                    base = size_gate
                if dimension == "pacing":
                    issues = (
                        [reason("local_clipping", "Clipping contaminates this phrase.")]
                        if (clipped(rf, rs) or clipped(pf, ps))
                        else []
                    )
                    gate = base if base.state != "ELIGIBLE" else decision(issues)
                    rv, pv = (
                        60 * (end - start) / weight,
                        60 * (end - start) / (ps.end_s - ps.start_s),
                    )
                    tau, width, unit, fractions = (
                        policy.pacing_tolerance,
                        policy.pacing_width,
                        "words/min",
                        (None, None),
                    )
                else:
                    name = (
                        "relative_energy" if dimension == "energy_variation" else "relative_pitch"
                    )
                    a, ga, fa = acoustic_gate(rf, rs, name, base)
                    b, gb, fb = acoustic_gate(pf, ps, name, base)
                    gate = ga if ga.state != "ELIGIBLE" else gb
                    rv, pv = (excursion(a), excursion(b)) if a and b else (None, None)
                    tau, width, unit = (
                        (policy.energy_tolerance_db, policy.energy_width_db, "dB")
                        if dimension == "energy_variation"
                        else (policy.pitch_tolerance_st, policy.pitch_width_st, "semitones")
                    )
                    fractions = (fa, fb)
                observations.append(
                    observation(
                        identity,
                        dimension,
                        "rubric",
                        (start, end),
                        rs,
                        ps,
                        unit,
                        rv,
                        pv,
                        tau,
                        width,
                        weight,
                        gate,
                        log_ratio=dimension == "pacing",
                        fractions=fractions,
                    )
                )
        for index in range(len(rw) - 1):
            rv, ga = gap(rf, rw[index], rw[index + 1], feature_gates["pause_behavior"])
            pv, gb = gap(pf, pw[index], pw[index + 1], feature_gates["pause_behavior"])
            gate = ga if ga.state != "ELIGIBLE" else gb
            rs = Span(start_s=rw[index].end_s, end_s=rw[index + 1].start_s) if rv else None
            # Short/missing pauses are boundary events even if a tiny acoustic gap exists.
            ps = (
                Span(start_s=pw[index].end_s, end_s=pw[index + 1].start_s)
                if pv and rv is not None and pv >= rv
                else None
            )
            observations.append(
                observation(
                    identity,
                    "pause_behavior",
                    "rubric",
                    (index, index + 2),
                    rs,
                    ps,
                    "s",
                    rv,
                    pv,
                    max(
                        policy.pause_floor_s,
                        policy.pause_relative * (rv or 0),
                        policy.pause_calibrated_tolerance_s,
                    ),
                    policy.pause_width_s,
                    1.0,
                    gate,
                    ref_anchor=rw[index].end_s if rs is None else None,
                    part_anchor=pw[index].end_s if ps is None else None,
                )
            )
        # Corresponding word medians are contour context; clocks and lengths remain independent.
        contours = {}
        for dimension, name in (
            ("energy_variation", "relative_energy"),
            ("pitch_dynamics", "relative_pitch"),
        ):
            values = []
            for index in range(len(rw)):
                rs, ps = span(rw, index, index + 1), span(pw, index, index + 1)
                a, ga, fa = acoustic_gate(rf, rs, name, feature_gates[dimension])
                b, gb, fb = acoustic_gate(pf, ps, name, feature_gates[dimension])
                gate = ga if ga.state != "ELIGIBLE" else gb
                rv, pv = (float(np.median(a)), float(np.median(b))) if a and b else (None, None)
                values.append((rv, pv, gate, fa, fb))
                if dimension == "pitch_dynamics":
                    observations.append(
                        observation(
                            identity,
                            dimension,
                            "pitch_contour",
                            (index, index + 1),
                            rs,
                            ps,
                            "semitones",
                            rv,
                            pv,
                            policy.contour_pitch_tolerance_st,
                            policy.pitch_width_st,
                            0.0,
                            gate,
                            scored=False,
                            fractions=(fa, fb),
                        )
                    )
            contours[dimension] = values
        energy = contours["energy_variation"]
        for start, end in phrases[0]:
            values = energy[start:end]
            if not all(v[2].state == "ELIGIBLE" for v in values):
                continue
            residuals = [v[1] - v[0] for v in values]
            direction = np.sign(np.median(residuals))
            # Sustained means >=80% corresponding word medians cross in the same direction,
            # at least two words, and >=0.5 s observed span in each recording.
            if (
                end - start >= 2
                and min(
                    span(rw, start, end).end_s - span(rw, start, end).start_s,
                    span(pw, start, end).end_s - span(pw, start, end).start_s,
                )
                >= 0.5
                and sum(direction * d > policy.contour_energy_tolerance_db for d in residuals)
                / len(values)
                >= 0.8
            ):
                # Mean preserves the exact mean paired difference.
                observations.append(
                    observation(
                        identity,
                        "energy_variation",
                        "sustained_energy",
                        (start, end),
                        span(rw, start, end),
                        span(pw, start, end),
                        "dB",
                        float(np.mean([v[0] for v in values])),
                        float(np.mean([v[1] for v in values])),
                        policy.contour_energy_tolerance_db,
                        policy.energy_width_db,
                        0.0,
                        decision([]),
                        scored=False,
                    )
                )
        for index in range(len(energy) - 1):
            left, right = energy[index : index + 2]
            if left[2].state != "ELIGIBLE" or right[2].state != "ELIGIBLE":
                continue
            observations.append(
                observation(
                    identity,
                    "energy_variation",
                    "energy_step",
                    (index, index + 2),
                    span(rw, index, index + 2),
                    span(pw, index, index + 2),
                    "dB",
                    right[0] - left[0],
                    right[1] - left[1],
                    policy.contour_energy_tolerance_db,
                    policy.energy_width_db,
                    0.0,
                    decision([]),
                    scored=False,
                )
            )
    dimension_scores = scores(observations, policy)
    for dimension in DIMENSIONS:
        local = [o.eligibility for o in observations if o.dimension == dimension and o.scored]
        if local:
            feature_gates[dimension] = combine(local)
    overall = (
        sum(policy.weights[d.dimension] * d.score for d in dimension_scores)
        if all(d.score is not None for d in dimension_scores)
        else None
    )
    abstentions = [
        reason(
            "dimension_unavailable", f"{d.dimension}: " + "; ".join(r.message for r in d.reasons)
        )
        for d in dimension_scores
        if d.score is None
    ]
    return Report(
        pair_id=pair.id if pair else None,
        dataset_version=reference.recording.dataset_version,
        dataset_sha256=dataset_sha256,
        implementation_sha256=implementation_sha256,
        policy=policy,
        policy_sha256=content_hash(policy.model_dump(mode="json")),
        inputs=[e.summary() for e in members],
        eligibility=combine(list(feature_gates.values())),
        feature_eligibility=feature_gates,
        observations=observations,
        regions=regions(observations, policy),
        dimensions=dimension_scores,
        overall_score=overall,
        abstention_reasons=abstentions,
        limitations=[
            "Scores measure agreement with the selected reference, "
            "not overall public-speaking quality.",
            "Engineering thresholds and severity bins are uncalibrated perceptual hypotheses.",
            "Phrase/word spans are detector resolution, not measured frame-exact flaw onsets.",
            "No statistical detection confidence or independent timing-error bound is available.",
            "Energy activity is heuristic; noise, microphone and speaker effects can remain.",
            "Synthetic input results are controlled probes, never independent human validation.",
        ],
    )
