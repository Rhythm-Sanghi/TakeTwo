"""Operational CPU duration budget; imports retain their independent storage limits."""

import os

DEFAULT_MAX_ANALYSIS_DURATION_S = 45


def maximum_analysis_duration_s() -> int:
    """Allow smaller deployment budgets; longer workloads require new verification."""
    value = os.environ.get("TAKETWO_MAX_ANALYSIS_DURATION_S", str(DEFAULT_MAX_ANALYSIS_DURATION_S))
    try:
        limit = int(value)
    except ValueError as error:
        raise ValueError(
            "TAKETWO_MAX_ANALYSIS_DURATION_S must be an integer from 1 to 45."
        ) from error
    if not 1 <= limit <= DEFAULT_MAX_ANALYSIS_DURATION_S:
        raise ValueError("TAKETWO_MAX_ANALYSIS_DURATION_S must be an integer from 1 to 45.")
    return limit
