"""Diagnose raw pYIN confidence without changing extraction or scientific policy."""

import argparse
import json
import time
import warnings
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from taketwo.analysis.contracts import FeatureConfig
from taketwo.dataset.storage import load, managed_path


def inspect(samples, config, *, frame_length=None, fmin=None, fmax=None):
    started = time.perf_counter()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        f0, voiced, probability = librosa.pyin(
            samples.astype(np.float64),
            sr=16000,
            fmin=config.fmin_hz if fmin is None else fmin,
            fmax=config.fmax_hz if fmax is None else fmax,
            frame_length=config.pitch_frame_length if frame_length is None else frame_length,
            hop_length=config.hop_length,
            center=False,
            fill_na=np.nan,
        )
    accepted = voiced & np.isfinite(f0) & (probability >= config.voicing_threshold)
    finite = f0[np.isfinite(f0)]
    adjacent = np.isfinite(f0[:-1]) & np.isfinite(f0[1:])
    jumps = np.abs(12 * np.log2(f0[1:][adjacent] / f0[:-1][adjacent]))
    frames = np.lib.stride_tricks.sliding_window_view(samples, config.frame_length)[
        :: config.hop_length
    ]
    rms = np.sqrt(np.mean(frames.astype(np.float64) ** 2, axis=1))
    return {
        "seconds": len(samples) / 16000,
        "frames": len(f0),
        "raw_finite_fraction": float(np.mean(np.isfinite(f0))),
        "raw_voiced_fraction": float(np.mean(voiced)),
        "accepted_fraction": float(np.mean(accepted)),
        "probability_quantiles_0_25_50_75_95_100": np.quantile(
            probability, [0, 0.25, 0.5, 0.75, 0.95, 1]
        ).tolist(),
        "raw_f0_quantiles_0_50_100": np.quantile(finite, [0, 0.5, 1]).tolist()
        if len(finite)
        else None,
        "nan_f0_frames": int(np.isnan(f0).sum()),
        "nonfinite_probability_frames": int((~np.isfinite(probability)).sum()),
        "adjacent_octave_jumps_over_10_semitones": int((jumps > 10).sum()),
        "peak": float(np.max(np.abs(samples))),
        "clipped_fraction": float(np.mean(abs(samples) >= 0.999)),
        "rms_dbfs_quantiles_5_50_95": (
            20 * np.log10(np.maximum(np.quantile(rms, [0.05, 0.5, 0.95]), 1e-12))
        ).tolist(),
        "warnings": [str(w.message) for w in captured],
        "elapsed_s": time.perf_counter() - started,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--probes",
        action="store_true",
        help="Diagnostic-only frame/range probes; never publishes features",
    )
    args = parser.parse_args()
    config = FeatureConfig()
    result = {"config": config.model_dump(mode="json"), "controls": {}, "recordings": {}}
    t = np.arange(48000) / 16000
    for frequency in (80, 120, 200, 400):
        tone = 0.2 * np.sin(2 * np.pi * frequency * t)
        result["controls"][str(frequency)] = inspect(tone, config)
    for recording in load(args.workspace).recordings:
        samples, sr = sf.read(
            managed_path(args.workspace, recording.normalized_path), dtype="float32"
        )
        if sr != 16000 or samples.ndim != 1:
            raise ValueError("Expected canonical mono 16 kHz audio")
        result["recordings"][recording.id] = inspect(samples, config)
        if recording.role == "reference":
            result["recordings"][recording.id + "-gain-0.1-control"] = inspect(
                samples * 0.1, config
            )
    if args.probes:
        probes = {}
        reference = next(
            (r for r in load(args.workspace).recordings if r.role == "reference"), None
        )
        inputs = [(f"tone{f}", 0.2 * np.sin(2 * np.pi * f * t)) for f in (80, 120)]
        if reference:
            samples, _ = sf.read(
                managed_path(args.workspace, reference.normalized_path), dtype="float32"
            )
            inputs.append(("reference", samples))
        for name, samples in inputs:
            for frame, low, high in [
                (1024, 60, 500),
                (2048, 60, 500),
                (1024, 40, 500),
                (1024, 60, 800),
            ]:
                probes[f"{name}-frame{frame}-range{low}-{high}"] = inspect(
                    samples, config, frame_length=frame, fmin=low, fmax=high
                )
        result["diagnostic_only_probes"] = probes
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
