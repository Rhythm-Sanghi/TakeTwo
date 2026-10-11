"""One-to-one temporal matching, provenance gates and family-level uncertainty."""

import numpy as np
from scipy.stats import spearmanr

from taketwo.dataset.schema import Dataset, content_hash
from taketwo.dataset.splits import connected_groups, make_split

from .contracts import Evaluation, EvaluationConfig, Label, Match, Metrics, Region, Report, Review
from .eligibility import DIMENSIONS, decision, reason
from .reviews import consensus, validate_review


def iou(left, right):
    intersection = max(0.0, min(left.end_s, right.end_s) - max(left.start_s, right.start_s))
    union = max(left.end_s, right.end_s) - min(left.start_s, right.start_s)
    return intersection / union


def match_regions(predictions: list[Region], labels: list[Label], config: EvaluationConfig):
    """Descending IoU, stable-ID ties; boundary events never count as intervals."""
    if len({p.id for p in predictions}) != len(predictions) or len(
        {label.id for label in labels}
    ) != len(labels):
        raise ValueError("Matching IDs must be unique.")
    candidates = []
    for p in predictions:
        for label in labels:
            if p.category != label.category:
                continue
            if p.participant_interval and label.interval:
                overlap = iou(p.participant_interval, label.interval)
                if overlap >= config.iou_threshold:
                    candidates.append((-overlap, p.id, label.id, overlap))
            elif p.participant_interval is None and label.interval is None:
                error = abs(p.participant_anchor_s - label.anchor_s)
                if error <= config.boundary_tolerance_s:
                    # Event candidates are independent of intervals; closest anchors win.
                    candidates.append((error, p.id, label.id, None))
    by_pred, by_label = {p.id: p for p in predictions}, {label.id: label for label in labels}
    used_pred, used_label, matches = set(), set(), []
    for _, pid, lid, overlap in sorted(candidates):
        if pid in used_pred or lid in used_label:
            continue
        p, label = by_pred[pid], by_label[lid]
        start = (
            abs(p.participant_interval.start_s - label.interval.start_s)
            if overlap is not None
            else abs(p.participant_anchor_s - label.anchor_s)
        )
        end = (
            abs(p.participant_interval.end_s - label.interval.end_s)
            if overlap is not None
            else None
        )
        matches.append(
            Match(
                prediction_id=pid, label_id=lid, iou=overlap, start_error_s=start, end_error_s=end
            )
        )
        used_pred.add(pid)
        used_label.add(lid)
    return matches, sorted(set(by_pred) - used_pred), sorted(set(by_label) - used_label)


def metrics(predictions, labels, matches):
    pids, lids = {p.id for p in predictions}, {label.id for label in labels}
    selected = [m for m in matches if m.prediction_id in pids and m.label_id in lids]
    tp, fp, fn = len(selected), len(predictions) - len(selected), len(labels) - len(selected)
    errors = [
        error
        for match in selected
        for error in (match.start_error_s, match.end_error_s)
        if error is not None
    ]
    return Metrics(
        true_positive=tp,
        false_positive=fp,
        false_negative=fn,
        precision=tp / (tp + fp) if tp + fp else None,
        recall=tp / (tp + fn) if tp + fn else None,
        f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        median_boundary_error_s=float(np.median(errors)) if errors else None,
        p90_boundary_error_s=float(np.quantile(errors, 0.9, method="linear")) if errors else None,
    )


def clean_spans(duration, labels, event_tolerance):
    """Exclude every reviewed positive, including event neighborhoods, from clean time."""
    positive = sorted(
        (label.interval.start_s, label.interval.end_s)
        if label.interval
        else (
            max(0.0, label.anchor_s - event_tolerance),
            min(duration, label.anchor_s + event_tolerance),
        )
        for label in labels
    )
    clean, cursor = [], 0.0
    for start, end in positive:
        if start > cursor:
            clean.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < duration:
        clean.append((cursor, duration))
    return clean


def evaluate(
    dataset: Dataset,
    reports: list[Report],
    reviews: list[Review],
    config: EvaluationConfig,
    implementation_sha256: str,
) -> Evaluation:
    issues = []
    dataset_hash = content_hash(dataset.model_dump(mode="json"))
    kwargs = dict(
        config=config,
        implementation_sha256=implementation_sha256,
        dataset_sha256=dataset_hash,
        report_sha256=[content_hash(r.model_dump(mode="json")) for r in reports],
        review_sha256=sorted(content_hash(r.model_dump(mode="json")) for r in reviews),
        origin="unavailable",
        independent_real_validation=False,
        policy_sha256=None,
        metrics=None,
        interval_metrics=None,
        boundary_event_metrics=None,
        by_category={},
        by_severity={},
        matches=[],
        false_positive_ids=[],
        false_negative_ids=[],
        family_ids=[],
        clean_reviewed_duration_s=None,
        false_flags_in_clean_spans=None,
        false_flags_per_clean_minute=None,
        severity_spearman=None,
        severity_matched_count=0,
        uncertainty={},
        limitations=[
            "Temporal/category agreement does not establish rhetorical quality "
            "or causal human explanations.",
            "Small-family bootstrap intervals are descriptive, not population guarantees.",
            "Severity agreement is ordinal association; detector bins "
            "are not validated human severity.",
        ],
    )
    if not reports:
        issues.append(reason("reports_missing", "No comparison reports are available."))
    if len({r.pair_id for r in reports}) != len(reports):
        raise ValueError("Supply each pair once; repeated reports would double-count detections.")
    pair_map = {p.id: p for p in dataset.pairs}
    recording_map = {r.id: r for r in dataset.recordings}
    if reports and len({r.policy_sha256 for r in reports}) != 1:
        raise ValueError("One evaluation requires one frozen policy/configuration.")
    groups = connected_groups(dataset)
    group_for = {rid: group for group, members in groups.items() for rid in members}
    if config.mode != "software_fixture":
        split = dataset.split
        if split is None:
            issues.append(
                reason("split_missing", "Evaluation requires frozen connected-group splits.")
            )
        elif split != make_split(dataset, split.seed, split.ratios):
            raise ValueError("Split membership/group/leakage audit failed.")
    predictions, labels, all_matches, fps, fns, family_metrics = [], [], [], [], [], []
    clean_duration, clean_flags = 0.0, 0
    origins, families = set(), set()
    for report in reports:
        pair = pair_map.get(report.pair_id)
        if report.dataset_sha256 != dataset_hash or pair is None or len(report.inputs) != 2:
            raise ValueError("Evaluation report dataset/pair identity differs.")
        if [i.provenance.recording_id for i in report.inputs] != [
            pair.reference_id,
            pair.participant_id,
        ]:
            raise ValueError("Evaluation report pair members differ.")
        if report.overall_score is None or report.eligibility.state != "ELIGIBLE":
            # Still evaluate eligible regional categories; report abstention separately.
            kwargs["limitations"].append(f"Pair {pair.id} has withheld dimensions/overall score.")
        participant = recording_map[pair.participant_id]
        origin = "synthetic" if participant.origin == "synthetic" else "human"
        origins.add(origin)
        group = group_for[participant.id]
        families.add(group)
        policy = report.policy
        if config.mode != "software_fixture" and dataset.split:
            if dataset.split.assignments[participant.id] != config.split:
                raise ValueError("Pair is outside the requested evaluation split.")
            if group in set(policy.calibration_group_ids + policy.validation_group_ids):
                raise ValueError("Evaluation family leaks into policy calibration/validation.")
        if config.mode == "held_out":
            if config.split != "test" or not policy.frozen:
                issues.append(
                    reason(
                        "policy_not_frozen",
                        "Held-out evaluation requires frozen policy and test split.",
                    )
                )
            elif dataset.split:
                for gid, expected in [(g, "train") for g in policy.calibration_group_ids] + [
                    (g, "validation") for g in policy.validation_group_ids
                ]:
                    if gid not in groups or any(
                        dataset.split.assignments[rid] != expected for rid in groups[gid]
                    ):
                        raise ValueError(
                            "Calibration/validation policy group provenance is invalid."
                        )
        selected = [r for r in reviews if r.scope == "flaws" and r.pair_id == pair.id]
        accepted, review_reason = consensus(selected, "flaws")
        if review_reason:
            issues.append(reason("human_labels_unavailable", f"{pair.id}: {review_reason}"))
            continue
        for review in accepted:
            validate_review(review, participant, None)
            if (
                review.provenance.recording_id != participant.id
                or review.provenance != report.inputs[1].provenance
            ):
                raise ValueError("Flaw review input identity differs from report.")
        spans = sorted(accepted[0].reviewed_spans, key=lambda s: s.start_s)
        if (
            spans[0].start_s != 0
            or spans[-1].end_s != participant.normalized_info.duration_s
            or any(a.end_s != b.start_s for a, b in zip(spans, spans[1:], strict=False))
        ):
            issues.append(
                reason(
                    "review_coverage",
                    "Full recording listening coverage is required; "
                    "uninspected spans cannot be treated as clean negatives.",
                )
            )
            continue
        local_predictions = report.regions
        local_labels = accepted[0].labels
        if any(
            report.feature_eligibility[label.category].state != "ELIGIBLE" for label in local_labels
        ):
            issues.append(
                reason(
                    "category_unavailable",
                    "Reviewed positive category is withheld by evidence gates.",
                )
            )
            continue
        local_matches, local_fp, local_fn = match_regions(local_predictions, local_labels, config)
        clean = clean_spans(
            participant.normalized_info.duration_s, local_labels, config.boundary_tolerance_s
        )
        clean_duration += sum(end - start for start, end in clean)
        for prediction in local_predictions:
            if prediction.id not in local_fp:
                continue
            interval, anchor = prediction.participant_interval, prediction.participant_anchor_s
            if any(
                (start <= interval.start_s < interval.end_s <= end)
                if interval
                else (start <= anchor < end)
                for start, end in clean
            ):
                clean_flags += 1
        predictions.extend(local_predictions)
        labels.extend(local_labels)
        all_matches.extend(local_matches)
        fps.extend(local_fp)
        fns.extend(local_fn)
        family_metrics.append((group, metrics(local_predictions, local_labels, local_matches)))
    if len(origins) > 1:
        raise ValueError("Evaluate human and synthetic origins separately.")
    if len({p.id for p in predictions}) != len(predictions) or len(
        {label.id for label in labels}
    ) != len(labels):
        raise ValueError("Prediction and ground-truth IDs must be unique across evaluated pairs.")
    kwargs["origin"] = next(iter(origins)) if origins else "unavailable"
    kwargs["family_ids"] = sorted(families)
    kwargs["policy_sha256"] = reports[0].policy_sha256 if reports else None
    if issues:
        return Evaluation(eligibility=decision(issues, review=True), **kwargs)
    if config.mode == "software_fixture":
        kwargs["limitations"].append(
            "Software-fixture metrics exercise numerical matching only; no human validation claim."
        )
    kwargs.update(
        metrics=metrics(predictions, labels, all_matches),
        interval_metrics=metrics(
            [p for p in predictions if p.participant_interval],
            [label for label in labels if label.interval],
            all_matches,
        ),
        boundary_event_metrics=metrics(
            [p for p in predictions if p.participant_interval is None],
            [label for label in labels if label.interval is None],
            all_matches,
        ),
        by_category={
            d: metrics(
                [p for p in predictions if p.category == d],
                [label for label in labels if label.category == d],
                all_matches,
            )
            for d in DIMENSIONS
        },
        by_severity={
            str(s): metrics(
                [p for p in predictions if p.severity == s],
                [label for label in labels if label.severity == s],
                all_matches,
            )
            for s in (1, 2, 3)
        },
        matches=all_matches,
        false_positive_ids=sorted(fps),
        false_negative_ids=sorted(fns),
        clean_reviewed_duration_s=clean_duration,
        false_flags_in_clean_spans=clean_flags,
        false_flags_per_clean_minute=60 * clean_flags / clean_duration if clean_duration else None,
        severity_matched_count=len(all_matches),
    )
    pred_by_id, label_by_id = {p.id: p for p in predictions}, {label.id: label for label in labels}
    predicted_severity = [pred_by_id[m.prediction_id].severity for m in all_matches]
    reviewed_severity = [label_by_id[m.label_id].severity for m in all_matches]
    if len(all_matches) >= 2 and np.ptp(predicted_severity) > 0 and np.ptp(reviewed_severity) > 0:
        kwargs["severity_spearman"] = float(
            spearmanr(predicted_severity, reviewed_severity).statistic
        )
    grouped = {}
    for group, result in family_metrics:
        totals = grouped.setdefault(group, np.zeros(3, dtype=int))
        totals += [result.true_positive, result.false_positive, result.false_negative]
    rng = np.random.default_rng(config.seed)
    samples = {name: [] for name in ("precision", "recall", "f1")}
    values = np.array([grouped[g] for g in sorted(grouped)])
    for _ in range(config.bootstrap_resamples):
        tp, fp, fn = values[rng.integers(0, len(values), size=len(values))].sum(axis=0)
        for name, numerator, denominator in (
            ("precision", tp, tp + fp),
            ("recall", tp, tp + fn),
            ("f1", 2 * tp, 2 * tp + fp + fn),
        ):
            if denominator:
                samples[name].append(float(numerator / denominator))
    kwargs["uncertainty"] = {
        name: {
            "percentile_95": np.quantile(v, [0.025, 0.975], method="linear").tolist()
            if v
            else None,
            "undefined_resamples": config.bootstrap_resamples - len(v),
        }
        for name, v in samples.items()
    }
    kwargs["independent_real_validation"] = (
        config.mode == "held_out" and origins == {"human"} and len(families) >= 3
    )
    if len(families) < 3:
        kwargs["limitations"].append("Fewer than three independent groups; pilot-only evidence.")
    return Evaluation(eligibility=decision([]), **kwargs)
