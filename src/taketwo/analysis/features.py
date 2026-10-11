"""CPU acoustic measurements on complete, unpadded native-time windows."""

import numpy as np
from scipy.fft import dct
from scipy.signal import windows
from threadpoolctl import threadpool_limits

from taketwo.dataset.audio import sample_hash
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import content_hash

from .contracts import (
    AlignmentResult,
    Diagnostic,
    FeatureConfig,
    FeatureResult,
    Interval,
    Provenance,
    QualityReport,
    Series,
)


def runs(mask: np.ndarray, starts: np.ndarray, length: int, label: str) -> list[Interval]:
    """Union selected observed supports, including overlap across an unselected frame."""
    result = []
    for start in starts[mask]:
        begin, end = float(start / 16000), float((start + length) / 16000)
        if result and begin <= result[-1].end_s:
            result[-1].end_s = end
        else:
            result.append(Interval(start_s=begin, end_s=end, label=label))
    return result


@threadpool_limits.wrap(limits=1, user_api="blas")
def extract(
    samples: np.ndarray,
    provenance: Provenance,
    config: FeatureConfig,
    alignment: AlignmentResult | None = None,
) -> FeatureResult:
    if samples.ndim != 1 or not len(samples) or not np.isfinite(samples).all():
        raise DatasetError(
            "invalid_signal", "Expected finite nonempty mono audio.", "Review audio."
        )
    if len(samples) / 16000 > config.maximum_duration_s:
        raise DatasetError(
            "analysis_limit", "Phase 2 supports at most 30 seconds.", "Use an excerpt."
        )
    samples = samples.astype(np.float32)
    if not np.isfinite(samples).all() or sample_hash(samples) != provenance.sample_sha256:
        raise DatasetError(
            "sample_identity",
            "Samples differ from declared provenance.",
            "Use the matching canonical recording.",
        )
    if alignment is not None:
        from .alignment import validate_alignment

        validate_alignment(alignment)
        if alignment.provenance != provenance:
            raise DatasetError(
                "alignment_identity", "Alignment inputs differ.", "Realign this audio."
            )
    import librosa

    x = samples.astype(np.float64)
    length, hop = config.frame_length, config.hop_length
    starts = np.arange(0, max(0, len(x) - length + 1), hop, dtype=np.int64)
    frames = (
        np.lib.stride_tricks.sliding_window_view(x, length)[::hop]
        if len(x) >= length
        else np.empty((0, length))
    )
    rms = np.sqrt(np.mean(frames**2, axis=1))
    energy = 20 * np.log10(np.maximum(rms, config.energy_floor))
    window = windows.hann(length, sym=False)
    stft = np.fft.rfft(frames * window, n=config.n_fft, axis=1)
    power = abs(stft) ** 2 / np.sum(window**2)
    frequencies = np.fft.rfftfreq(config.n_fft, 1 / 16000)
    factors = np.full(len(frequencies), 2.0)
    factors[[0, -1]] = 1
    total_power = np.sum(power * factors, axis=1) / config.n_fft
    denominator = np.sum(power, axis=1)
    centroid = np.divide(
        power @ frequencies, denominator, out=np.zeros_like(denominator), where=denominator > 0
    )
    mel = librosa.filters.mel(
        sr=16000,
        n_fft=512,
        n_mels=40,
        fmin=0,
        fmax=8000,
        htk=False,
        norm="slaney",
        dtype=np.float64,
    )
    mfcc = dct(np.log(np.maximum(power @ mel.T, 1e-10)), type=2, norm="ortho", axis=1)[:, :13]
    # Upper-energy quartile is a gain-equivariant candidate speech baseline. It is not a VAD.
    audible = rms > config.energy_floor
    seed = float(np.quantile(energy[audible], 0.75, method="linear")) if audible.any() else None
    active = audible & (energy >= seed - config.activity_drop_db) if seed is not None else audible
    baseline = float(np.median(energy[active])) if active.any() else None
    if baseline is not None:
        active = audible & (energy >= baseline - config.activity_drop_db)
        baseline = float(np.median(energy[active]))
    relative = energy - baseline if baseline is not None else np.full(len(starts), np.nan)
    pitch_starts = np.arange(0, max(0, len(x) - 1024 + 1), hop, dtype=np.int64)
    f0 = np.full(len(pitch_starts), np.nan)
    probability = np.zeros(len(pitch_starts))
    voiced = np.zeros(len(pitch_starts), dtype=bool)
    if len(pitch_starts) and np.max(np.abs(x)) > config.energy_floor:
        raw_f0, raw_voiced, probability = librosa.pyin(
            x,
            sr=16000,
            fmin=config.fmin_hz,
            fmax=config.fmax_hz,
            frame_length=1024,
            hop_length=hop,
            center=False,
            fill_na=np.nan,
        )
        voiced = raw_voiced & (probability >= config.voicing_threshold) & np.isfinite(raw_f0)
        f0[voiced] = raw_f0[voiced]
    pitch_base = float(np.median(f0[voiced])) if voiced.any() else None
    semitones = 12 * np.log2(f0 / pitch_base) if pitch_base is not None else f0.copy()
    series = {}

    def add(name: str, values: np.ndarray, unit: str, positions=starts, size=length) -> None:
        series[name] = Series(
            unit=unit,
            frame_length=size,
            hop_length=hop,
            start_samples=positions.tolist(),
            times_s=((positions + size / 2) / 16000).tolist(),
            values=[float(v) if np.isfinite(v) else None for v in values],
        )

    add("rms", rms, "full_scale")
    add("energy", energy, "dBFS")
    add("relative_energy", relative, "dB")
    add("spectral_power", total_power, "full_scale_squared")
    add("spectral_centroid", centroid, "Hz")
    add("activity", active.astype(float), "binary_energy_estimate")
    add("f0", f0, "Hz", pitch_starts, 1024)
    add("relative_pitch", semitones, "semitones", pitch_starts, 1024)
    add("voicing_probability", probability, "pYIN_model_probability", pitch_starts, 1024)
    add("voiced", voiced.astype(float), "binary", pitch_starts, 1024)
    low_energy = runs(~active, starts, length, "low_energy_candidate")
    pauses = []
    rate = articulation = None
    reason = "A complete successful alignment and independently verified transcript are required."
    if (
        alignment is not None
        and alignment.status == "succeeded"
        and alignment.words
        and provenance.transcript_verified
    ):
        # Transcript verification is checked by the workspace layer; automatic alignment
        # remains unreviewed timing evidence even when structurally complete.
        words = alignment.words
        for left, right in zip(words, words[1:], strict=False):
            start, end = left.end_s, right.start_s
            inside = (starts >= start * 16000) & (starts + length <= end * 16000)
            if end - start >= config.minimum_pause_s and inside.any() and (~active[inside]).all():
                pauses.append(Interval(start_s=start, end_s=end, label="aligned_low_energy_gap"))
        span = words[-1].end_s - words[0].start_s
        rate = 60 * len(words) / span
        speaking = span - sum(p.end_s - p.start_s for p in pauses)
        articulation = 60 * len(words) / speaking if speaking > 0 else None
        reason = None
    flags = []
    peak = float(np.max(np.abs(x)))
    clipping = float(np.mean(np.abs(x) >= 0.999))
    if clipping > 0.001 or peak > 1:
        flags.append("clipping")
    if np.sqrt(np.mean(x**2)) < 1e-3:
        flags.append("near_silent")
    if not len(starts):
        flags.append("too_short_for_spectrum")
    if not voiced.any():
        flags.append("pitch_unavailable")
    if voiced.any() and np.any(
        (f0[voiced] < config.fmin_hz * 1.02) | (f0[voiced] > config.fmax_hz / 1.02)
    ):
        flags.append("pitch_range_edge")
    adjacent = np.isfinite(semitones[:-1]) & np.isfinite(semitones[1:])
    if np.any(np.abs(np.diff(semitones)[adjacent]) > 7):
        flags.append("pitch_jump_review")
    waveform = [
        (i, min(i + hop, len(x)), float(x[i : i + hop].min()), float(x[i : i + hop].max()))
        for i in range(0, len(x), hop)
    ]

    def excursion(values: np.ndarray) -> float | None:
        values = values[np.isfinite(values)]
        return (
            float(np.diff(np.quantile(values, [0.1, 0.9], method="linear"))[0])
            if len(values)
            else None
        )

    return FeatureResult(
        provenance=provenance,
        config=config,
        quality=QualityReport(
            sample_count=len(x),
            duration_s=len(x) / 16000,
            mean=float(x.mean()),
            rms=float(np.sqrt(np.mean(x**2))),
            peak=peak,
            clipping_fraction=clipping,
            flags=flags,
            spectral_covered_until_s=float((starts[-1] + length) / 16000) if len(starts) else 0.0,
            pitch_covered_until_s=float((pitch_starts[-1] + 1024) / 16000)
            if len(pitch_starts)
            else 0.0,
        ),
        series=series,
        frequencies_hz=frequencies.tolist(),
        spectrum_power=power.tolist(),
        mfcc=mfcc.tolist(),
        waveform=waveform,
        activity=runs(active, starts, length, "energy_activity"),
        low_energy=low_energy,
        voiced_regions=runs(voiced, pitch_starts, 1024, "pyin_voiced_support"),
        unvoiced_regions=runs(~voiced, pitch_starts, 1024, "pyin_unvoiced_support"),
        pauses=pauses,
        alignment_sha256=content_hash(alignment.model_dump(mode="json")) if alignment else None,
        speaking_rate_wpm=rate,
        articulation_rate_wpm=articulation,
        rate_unavailable_reason=reason,
        energy_baseline_dbfs=baseline,
        pitch_baseline_hz=pitch_base,
        energy_range_db=excursion(relative[active]),
        pitch_range_semitones=excursion(semitones),
        diagnostics=[
            Diagnostic(
                code="energy_activity_heuristic",
                message="Energy activity may include noise and omit quiet speech; "
                "silence is not a flaw.",
                recovery="Inspect contours and alignment against the recording.",
            )
        ],
    )
