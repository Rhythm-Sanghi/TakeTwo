"""Explicit human assertions, retained separately from automatic alignment and labels."""

import numpy as np

from taketwo.analysis.contracts import AlignmentResult, Interval
from taketwo.dataset.schema import Recording, content_hash, tokenize

from .contracts import Review


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
    for label in review.labels:
        if label.interval:
            if label.interval.end_s > duration or not any(
                s.start_s <= label.interval.start_s < label.interval.end_s <= s.end_s
                for s in review.reviewed_spans
            ):
                raise ValueError("Flaw label must lie inside an explicitly inspected span.")
        elif label.anchor_s > duration or not any(
            s.start_s <= label.anchor_s <= s.end_s for s in review.reviewed_spans
        ):
            raise ValueError("Flaw anchor must lie inside an explicitly inspected span.")


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
    if scope == "timing":
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
        # Conservative: identical adjudicated inventories; preserve differing originals.
        inventory = lambda r: {  # noqa: E731
            "labels": [label.model_dump(mode="json") for label in r.labels],
            "spans": [span.model_dump(mode="json") for span in r.reviewed_spans],
        }
        if any(inventory(r) != inventory(selected[0]) for r in selected):
            return [], "Flaw inventories disagree; reconcile explicitly, never choose one silently."
    return selected, None


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
