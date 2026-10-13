"""Explicit human assertions, retained separately from automatic alignment and labels."""

import json
from itertools import combinations

import numpy as np

from taketwo.analysis.contracts import AlignmentResult, Interval
from taketwo.dataset.schema import Recording, canonical_json, content_hash, tokenize

from .contracts import Label, Review
from .matching import assign


def validate_review(review: Review, recording: Recording, alignment: AlignmentResult | None):
    p = review.provenance
    if (
        p.recording_id != recording.id
        or p.audio_sha256 != recording.normalized_sha256
        or p.sample_sha256 != recording.sample_sha256
        or p.transcript_sha256 != recording.transcript_sha256
        or p.dataset_version != recording.dataset_version
    ):
        raise ValueError("Review recording/audio/transcript identity differs.")
    from taketwo.dataset.audio import sha256

    if p.original_text_sha256 != sha256(recording.transcript.text.encode("utf-8")):
        raise ValueError("Review original text hash differs.")
    duration = recording.normalized_info.duration_s
    if review.scope == "timing":
        if (
            alignment is None
            or review.alignment_sha256 != content_hash(alignment.model_dump(mode="json"))
            or p != alignment.provenance
        ):
            raise ValueError("Timing review must bind the supplied original alignment.")
        if [w.token_index for w in review.words] != list(range(len(recording.tokens))):
            raise ValueError("Manual boundaries must cover every canonical token in order.")
        previous = 0.0
        for word in review.words:
            if not previous <= word.start_s < word.end_s <= duration:
                raise ValueError("Manual word boundaries overlap or exceed native audio.")
            if tokenize(word.label)[0] != [alignment.normalized_tokens[word.token_index]]:
                raise ValueError("Manual word label differs from original spoken-form policy.")
            previous = word.end_s
        cursor = 0
        for start, end in review.phrase_spans:
            if not cursor == start < end <= len(recording.tokens):
                raise ValueError("Reviewed phrases must partition canonical tokens exactly.")
            cursor = end
        if cursor != len(recording.tokens):
            raise ValueError("Reviewed phrases omit tokens.")
    for span in review.reviewed_spans:
        if span.end_s > duration:
            raise ValueError("Inspected span exceeds recording.")
    ordered = sorted(review.reviewed_spans, key=lambda s: s.start_s)
    if any(a.end_s > b.start_s for a, b in zip(ordered, ordered[1:], strict=False)):
        raise ValueError("Inspected spans must not overlap.")
    coverage = coverage_union(review.reviewed_spans)
    for label in review.labels:
        if label.interval:
            if label.interval.end_s > duration or not any(
                s.start_s <= label.interval.start_s < label.interval.end_s <= s.end_s
                for s in coverage
            ):
                raise ValueError("Flaw label must lie inside an explicitly inspected span.")
        elif label.anchor_s > duration or not any(
            s.start_s <= label.anchor_s <= s.end_s for s in coverage
        ):
            raise ValueError("Flaw anchor must lie inside an explicitly inspected span.")


def coverage_union(spans):
    """Merge touching inspected intervals without filling unreviewed gaps."""
    result = []
    for span in sorted(spans, key=lambda s: (s.start_s, s.end_s)):
        if result and span.start_s <= result[-1].end_s:
            result[-1] = result[-1].model_copy(update={"end_s": max(result[-1].end_s, span.end_s)})
        else:
            result.append(span)
    return result


def flaw_agreement(left, right):
    """semantic-v2: exact category/severity/uncertainty, <=200 ms and IoU >=0.5.

    Unstructured explanations remain original evidence for human adjudication.
    Their wording and random identifiers are not numerical agreement criteria.
    """
    if coverage_union(left.reviewed_spans) != coverage_union(right.reviewed_spans):
        return False
    if len(left.labels) != len(right.labels):
        return False
    edges = {}
    for a in left.labels:
        for b in right.labels:
            if (a.category, a.severity, a.uncertainty_s) != (
                b.category,
                b.severity,
                b.uncertainty_s,
            ):
                continue
            if a.interval is not None and b.interval is not None:
                x, y = a.interval, b.interval
                error = max(abs(x.start_s - y.start_s), abs(x.end_s - y.end_s))
                overlap = max(0.0, min(x.end_s, y.end_s) - max(x.start_s, y.start_s))
                quality = overlap / (max(x.end_s, y.end_s) - min(x.start_s, y.start_s))
                if error <= 0.2 + 1e-12 and quality >= 0.5:
                    edges[a.id, b.id] = quality
            elif a.interval is None and b.interval is None:
                error = abs(a.anchor_s - b.anchor_s)
                if error <= 0.2 + 1e-12:
                    edges[a.id, b.id] = max(0.0, 1 - error / 0.2)
    return len(assign([a.id for a in left.labels], [b.id for b in right.labels], edges)) == len(
        left.labels
    )


def active_reviews(reviews: list[Review]) -> list[Review]:
    by_id = {r.id: r for r in reviews}
    if len(by_id) != len(reviews):
        raise ValueError("Duplicate review ID; supply each artifact once.")
    replaced = set()
    for review in reviews:
        if review.supersedes:
            old = by_id.get(review.supersedes)
            if (
                old is None
                or old.scope != review.scope
                or old.reviewer_id != review.reviewer_id
                or old.provenance != review.provenance
                or old.pair_id != review.pair_id
            ):
                raise ValueError("Superseded review must be supplied and share reviewer/subject.")
            replaced.add(old.id)
            cursor = old
            seen = {review.id}
            while cursor:
                if cursor.id in seen:
                    raise ValueError("Cyclic review history.")
                seen.add(cursor.id)
                cursor = by_id.get(cursor.supersedes)
    return sorted((r for r in reviews if r.id not in replaced), key=lambda r: r.id)


def consensus(reviews: list[Review], scope: str) -> tuple[list[Review], str | None]:
    selected = [r for r in active_reviews(reviews) if r.scope == scope]
    if len(selected) < 2 or len({r.reviewer_id for r in selected}) != len(selected):
        return [], "Two distinct reviewer records are required."
    if any(not r.independent or r.decision != "approved" for r in selected):
        return [], "Review is nonindependent, rejected or unresolved."
    if any(
        (r.provenance, r.pair_id, r.alignment_sha256)
        != (selected[0].provenance, selected[0].pair_id, selected[0].alignment_sha256)
        for r in selected
    ):
        return [], "Reviewer recording, pair or alignment identity differs."
    if scope == "timing":
        if len({len(r.words) for r in selected}) != 1:
            return [], "Manual word boundary inventories differ."
        if any(r.phrase_spans != selected[0].phrase_spans for r in selected):
            return [], "Reviewers disagree on phrase partition; resolve with superseding reviews."
        boundaries = np.array([[(w.start_s, w.end_s) for w in r.words] for r in selected])
        if len({len(r.words) for r in selected}) != 1 or np.any(np.ptp(boundaries, axis=0) > 0.2):
            return [], "Manual word boundaries disagree by more than 200 ms."
    elif scope == "transcript":
        if any(
            tokenize(r.corrected_text)[0] != tokenize(selected[0].corrected_text)[0]
            for r in selected
        ):
            return [], "Reviewers disagree on the checked canonical transcript."
    else:
        if any(not r.blinded_to_predictions for r in selected):
            return [], "Evaluation reviewers must attest blindness to predictions and recipes."
        if any(not flaw_agreement(a, b) for a, b in combinations(selected, 2)):
            return [], "Flaw inventories or coverage disagree; revise or adjudicate explicitly."
    return selected, None


GROUND_TRUTH_POLICY = "exact-inventory-v1"


def resolved_flaws(reviews: list[Review]) -> tuple[list[Label], str | None]:
    """Resolve exact numerical agreement without choosing or averaging a reviewer.

    Semantic-v2 remains a listening-agreement screen. Even sub-tolerance temporal
    differences change boundary errors, clean time or threshold-sensitive matches.
    Require explicit same-author revisions until numerical multisets agree. IDs
    and prose remain in immutable source reviews, never matching tie breakers.
    The derived labels are reproducible from the evaluation's retained reviews.
    """
    accepted, issue = consensus(reviews, "flaws")
    if issue:
        return [], issue

    def inventory(review):
        return sorted(
            canonical_json(label.model_dump(mode="json", exclude={"id", "rationale"}))
            for label in review.labels
        )

    agreed = inventory(accepted[0])
    if any(inventory(review) != agreed for review in accepted[1:]):
        return [], (
            "Independent flaw reviews agree within listening tolerance but their exact "
            "boundaries differ. Evaluation is withheld until reviewers submit explicit "
            "superseding reviews with the same numerical labels. An adjudication note "
            "alone cannot resolve ground truth."
        )
    # Occurrence disambiguates repeated identical labels without depending on source IDs.
    labels = [
        Label.model_validate_json(
            canonical_json(
                {
                    **json.loads(value),
                    "id": "gt-"
                    + content_hash([GROUND_TRUTH_POLICY, accepted[0].pair_id, value, i]),
                    "rationale": "Exact numerical agreement; see independent review hashes.",
                }
            )
        )
        for i, value in enumerate(agreed)
    ]
    return labels, None


def reviewed_timing(
    reviews: list[Review],
) -> tuple[list[Interval], list[tuple[int, int]], str | None]:
    selected, reason = consensus(reviews, "timing")
    if reason:
        return [], [], reason
    boundaries = np.median(
        [[(w.start_s, w.end_s) for w in review.words] for review in selected], axis=0
    )
    words = [
        word.model_copy(update={"start_s": float(bounds[0]), "end_s": float(bounds[1])})
        for word, bounds in zip(selected[0].words, boundaries, strict=True)
    ]
    return words, selected[0].phrase_spans, None
