"""Deterministic maximum-cardinality, then maximum-quality bipartite assignment."""

import numpy as np
from scipy.optimize import linear_sum_assignment


def assign(left_ids, right_ids, qualities):
    """ID-sorted rows/columns resolve solver ties reproducibly; no quality perturbation.

    qualities maps eligible (left ID, right ID) edges to finite quality in [0, 1].
    Each row has a zero-reward unmatched column. A cardinality bonus greater than
    the maximum possible total quality makes losing a valid match suboptimal.
    """
    left, right = sorted(left_ids), sorted(right_ids)
    if len(set(left)) != len(left) or len(set(right)) != len(right):
        raise ValueError("Matching IDs must be unique.")
    if not left or not right:
        return []
    li, ri = {v: i for i, v in enumerate(left)}, {v: i for i, v in enumerate(right)}
    bonus = min(len(left), len(right)) + 1
    reward = np.zeros((len(left), len(right) + len(left)))
    reward[:, : len(right)] = -bonus
    for (a, b), quality in qualities.items():
        if not np.isfinite(quality) or not 0 <= quality <= 1:
            raise ValueError("Matching quality must be finite and between zero and one.")
        reward[li[a], ri[b]] = bonus + quality
    rows, columns = linear_sum_assignment(reward, maximize=True)
    return sorted(
        (left[a], right[b])
        for a, b in zip(rows, columns, strict=True)
        if b < len(right) and (left[a], right[b]) in qualities
    )
