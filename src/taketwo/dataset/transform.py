"""Controlled edits on explicitly supplied intervals, never inferred flaw detections."""

import numpy as np
from numpy.typing import NDArray

from .audio import RATE, inspect_samples, quality
from .errors import DatasetError
from .schema import Recipe, TimeSegment

CATEGORIES = {
    "insert_pause": "pause_behavior",
    "shorten_pause": "pause_behavior",
    "tempo": "pacing",
    "gain": "energy_variation",
    "pitch_shift": "pitch_dynamics",
}


def apply_recipe(
    samples: NDArray[np.float32], recipe: Recipe
) -> tuple[NDArray[np.float32], list[TimeSegment], list[tuple[int, int]]]:
    chunks: list[NDArray[np.float32]] = []
    mapping: list[TimeSegment] = []
    affected: list[tuple[int, int]] = []
    cursor = output_cursor = 0

    def append(chunk: NDArray, start: int, end: int, kind: str) -> None:
        nonlocal output_cursor
        if not len(chunk):
            return
        chunk = chunk.astype(np.float32)
        chunks.append(chunk)
        mapping.append(
            TimeSegment(
                source_start=start,
                source_end=end,
                output_start=output_cursor,
                output_end=output_cursor + len(chunk),
                kind=kind,
            )
        )
        output_cursor += len(chunk)

    for operation in recipe.operations:
        start, end = round(operation.start_s * RATE), round(operation.end_s * RATE)
        if start < cursor or end > len(samples) or end <= start:
            raise DatasetError(
                "transform_interval",
                "Transformation interval exceeds source bounds.",
                "Use ordered nonoverlapping intervals in parent recording time.",
            )
        append(samples[cursor:start], cursor, start, "unchanged")
        segment = samples[start:end].copy()
        changed_start = output_cursor
        if operation.kind in {"insert_pause", "shorten_pause"}:
            if float(np.sqrt(np.mean(segment.astype(np.float64) ** 2))) > 0.0031623:
                raise DatasetError(
                    "not_pause",
                    "Selected pause interval exceeds -50 dBFS RMS.",
                    "Select a reviewed quiet gap; speech will not be deleted.",
                )
            if operation.kind == "insert_pause":
                append(
                    np.zeros(round(operation.value * RATE), np.float32), start, start, "inserted"
                )
            else:
                new_length = max(1, round(len(segment) * operation.value))
                if len(segment) / RATE < 0.15:
                    raise DatasetError(
                        "not_pause",
                        "Shortening requires at least a 150 ms gap.",
                        "Select a longer reviewed pause.",
                    )
                segment = np.interp(
                    np.linspace(0, len(segment) - 1, new_length), np.arange(len(segment)), segment
                ).astype(np.float32)
        elif operation.kind == "gain":
            if len(segment) < 320:
                raise DatasetError(
                    "short_transform",
                    "Gain interval is shorter than 20 ms.",
                    "Choose an interval long enough for the boundary ramps.",
                )
            if start == 0 and end == len(samples):
                raise DatasetError(
                    "global_gain",
                    "Global gain is an invariance probe, not a flaw.",
                    "Select a local interval for energy inconsistency.",
                )
            # 10 ms ramp preserves samples at the edit boundary.
            ramp = min(160, len(segment) // 2)
            envelope = np.full(len(segment), operation.value)
            envelope[:ramp] = np.linspace(1, operation.value, ramp)
            envelope[-ramp:] = np.linspace(operation.value, 1, ramp)
            segment *= envelope.astype(np.float32)
        else:
            if len(segment) < 2048:
                raise DatasetError(
                    "short_transform",
                    "Tempo/pitch interval is shorter than 128 ms.",
                    "Choose a longer reviewed speech interval.",
                )
            import librosa

            if operation.kind == "tempo":
                segment = librosa.effects.time_stretch(
                    segment, rate=operation.value, n_fft=1024, hop_length=256
                )
            else:
                if start == 0 and end == len(samples):
                    raise DatasetError(
                        "global_pitch",
                        "Global register shift is not a delivery flaw.",
                        "Use a local pitch-dynamics alteration.",
                    )
                segment = librosa.effects.pitch_shift(
                    segment, sr=RATE, n_steps=operation.value, n_fft=1024, hop_length=256
                )
            # Fade only inside the edited region; timestamps and outside samples are unchanged.
            ramp = min(80, len(segment) // 2)
            segment[:ramp] *= np.linspace(0, 1, ramp)
            segment[-ramp:] *= np.linspace(1, 0, ramp)
        append(segment, start, end, "modified")
        affected.append((changed_start, output_cursor))
        cursor = end
    append(samples[cursor:], cursor, len(samples), "unchanged")
    output = np.concatenate(chunks).astype(np.float32)
    if len(output) > 600 * RATE:
        raise DatasetError(
            "audio_duration",
            "Transformation exceeds ten minutes.",
            "Reduce edit duration or use a shorter excerpt.",
        )
    if quality(inspect_samples(output, RATE, "WAV", "FLOAT")):
        raise DatasetError(
            "transform_quality",
            "Transformation creates clipping or near-silence.",
            "Reduce gain or revise the transformation; no output was written.",
        )
    return output, mapping, affected


def remap_interval(start_s: float, end_s: float, mapping: list[TimeSegment]) -> tuple[float, float]:
    """Map a parent interval, including inserted pauses within it, into a derivative."""
    if not np.isfinite([start_s, end_s]).all() or not 0 <= start_s < end_s:
        raise DatasetError(
            "time_map",
            "Expected a finite positive-width source interval.",
            "Use 0 <= start < end within the parent recording.",
        )

    def point(sample: float, right: bool) -> float:
        candidates = []
        for segment in mapping:
            if segment.source_start <= sample <= segment.source_end:
                width = segment.source_end - segment.source_start
                if width:
                    ratio = (sample - segment.source_start) / width
                    candidates.append(
                        segment.output_start + ratio * (segment.output_end - segment.output_start)
                    )
                else:
                    candidates.extend([segment.output_start, segment.output_end])
        if not candidates:
            raise DatasetError(
                "time_map",
                "Interval lies outside the source time map.",
                "Use an interval within the parent recording.",
            )
        return max(candidates) if right else min(candidates)

    return point(start_s * RATE, False) / RATE, point(end_s * RATE, True) / RATE
