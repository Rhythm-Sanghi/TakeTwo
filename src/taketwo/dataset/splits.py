"""Deterministic connected-group splits, including source and mirror speakers."""

import math
import random
from collections import defaultdict

from .errors import DatasetError
from .schema import Dataset, SplitReport, content_hash


def connected_groups(dataset: Dataset) -> dict[str, list[str]]:
    parents = {recording.id: recording.id for recording in dataset.recordings}

    def find(item: str) -> str:
        while parents[item] != item:
            parents[item] = parents[parents[item]]
            item = parents[item]
        return item

    def union(left: str, right: str) -> None:
        if left in parents and right in parents:
            a, b = sorted((find(left), find(right)))
            parents[b] = a

    owners: dict[tuple[str, str], str] = {}
    for recording in sorted(dataset.recordings, key=lambda r: r.id):
        keys = {
            "family": recording.family_id,
            "speaker": recording.speaker_id,
            "source": recording.provenance.source_id,
            "work": recording.provenance.work_id,
            "transcript": recording.transcript_sha256,
            "original": recording.original_sha256,
            "samples": recording.sample_sha256,
        }
        for category, value in keys.items():
            key = (category, value)
            if key in owners:
                union(recording.id, owners[key])
            owners[key] = recording.id
        if recording.transformation:
            union(recording.id, recording.transformation.parent_id)
    for pair in dataset.pairs:
        union(pair.reference_id, pair.participant_id)
    groups: dict[str, list[str]] = defaultdict(list)
    for recording_id in sorted(parents):
        groups[find(recording_id)].append(recording_id)
    real_ids = {r.id for r in dataset.recordings if r.origin != "synthetic"}
    # Synthetic additions must not change the ordering/identity of frozen source groups.
    stable = {
        "g-" + content_hash(sorted(set(members) & real_ids))[:24]: members
        for members in groups.values()
    }
    return dict(sorted(stable.items()))


def make_split(dataset: Dataset, seed: int, ratios: tuple[float, float, float]) -> SplitReport:
    if not all(math.isfinite(r) and r >= 0 for r in ratios) or not math.isclose(sum(ratios), 1):
        raise DatasetError(
            "split_ratios",
            "Split ratios must be finite, nonnegative and sum to one.",
            "Use, for example, 0.5 0.25 0.25.",
        )
    groups = connected_groups(dataset)
    if not groups:
        raise DatasetError(
            "empty_dataset", "Cannot split an empty dataset.", "Import recordings first."
        )
    ordered = list(groups)
    random.Random(seed).shuffle(ordered)
    targets = [len(groups) * ratio for ratio in ratios]
    counts = [math.floor(target) for target in targets]
    for index in sorted(range(3), key=lambda i: (targets[i] - counts[i], -i), reverse=True)[
        : len(groups) - sum(counts)
    ]:
        counts[index] += 1
    assignments: dict[str, str] = {}
    cursor = 0
    for name, count in zip(("train", "validation", "test"), counts, strict=False):
        for group_id in ordered[cursor : cursor + count]:
            for recording_id in groups[group_id]:
                assignments[recording_id] = name
        cursor += count
    warnings = []
    if any(count == 0 and ratio > 0 for count, ratio in zip(counts, ratios, strict=False)):
        warnings.append("Too few independent groups to populate every requested split.")
    if counts[2] < 3:
        warnings.append("Fewer than three independent test groups: evaluation remains pilot-only.")
    return SplitReport(
        seed=seed,
        ratios=ratios,
        assignments=assignments,
        groups=groups,
        membership_sha256=content_hash(assignments),
        warnings=warnings,
    )
