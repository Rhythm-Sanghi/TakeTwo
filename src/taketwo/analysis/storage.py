"""Immutable versioned JSON artifacts bound to dataset identifiers and input hashes."""

from pathlib import Path

import numpy as np

from taketwo.dataset.audio import RATE, read_audio, sample_hash, sha256, versions
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import canonical_json, content_hash, tokenize
from taketwo.dataset.storage import load, managed_path, read_json, write_new
from taketwo.dataset.workspace import find_recording

from .alignment import validate_alignment
from .contracts import AlignmentResult, FeatureResult, Provenance


def implementation_hash() -> str:
    directory = Path(__file__).parent
    return content_hash({p.name: sha256(p.read_bytes()) for p in sorted(directory.glob("*.py"))})


def recording_input(root: Path, recording_id: str):
    dataset = load(root)
    recording = find_recording(dataset, recording_id)
    data, samples, info = read_audio(managed_path(root, recording.normalized_path))
    tokens, offsets = tokenize(recording.transcript.text)
    if (
        sha256(data) != recording.normalized_sha256
        or sample_hash(samples[:, 0]) != recording.sample_sha256
        or info.sample_rate_hz != RATE
        or info.channels != 1
        or info.subtype != "FLOAT"
        or info.frames != recording.normalized_info.frames
        or tokens != recording.tokens
        or offsets != recording.token_offsets
        or content_hash(tokens) != recording.transcript_sha256
    ):
        raise DatasetError(
            "input_identity", "Audio/transcript differs from manifest.", "Validate dataset first."
        )
    provenance = Provenance(
        recording_id=recording.id,
        dataset_version=dataset.dataset_version,
        audio_sha256=sha256(data),
        sample_sha256=sample_hash(samples[:, 0]),
        transcript_sha256=recording.transcript_sha256,
        original_text_sha256=sha256(recording.transcript.text.encode("utf-8")),
        transcript_verified=recording.transcript.status == "verified",
        versions=versions(),
        implementation_sha256=implementation_hash(),
    )
    return recording, samples[:, 0], provenance


def publish(root: Path, result: AlignmentResult | FeatureResult) -> Path:
    payload = result.model_dump(mode="json")
    envelope = {"sha256": content_hash(payload), "result": payload}
    relative = (
        f"derived/v1/{result.provenance.recording_id}/{result.kind}-{envelope['sha256']}.json"
    )
    path = managed_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (canonical_json(envelope) + "\n").encode("utf-8")
    if len(content) > 32 * 1024 * 1024:
        raise DatasetError(
            "artifact_limit", "JSON artifact exceeds 32 MiB.", "Use a shorter excerpt."
        )
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError("Existing artifact content differs; no overwrite performed.")
    else:
        write_new(path, content)
    return path


def read_artifact(path: Path) -> AlignmentResult | FeatureResult:
    envelope = read_json(path)
    if not isinstance(envelope, dict) or set(envelope) != {"sha256", "result"}:
        raise ValueError("Expected analysis artifact envelope.")
    if content_hash(envelope["result"]) != envelope["sha256"]:
        raise ValueError("Artifact content hash mismatch.")
    contract = {"alignment": AlignmentResult, "features": FeatureResult}.get(
        envelope["result"].get("kind")
    )
    if contract is None:
        raise ValueError("Unknown artifact kind.")
    result = contract.model_validate_json(canonical_json(envelope["result"]))
    if isinstance(result, AlignmentResult):
        validate_alignment(result)
    else:
        validate_features(result)
    return result


def validate_features(result: FeatureResult) -> None:
    q, c = result.quality, result.config
    if q.duration_s != q.sample_count / 16000 or q.duration_s > c.maximum_duration_s:
        raise ValueError("Feature duration/sample coordinates differ.")
    expected_names = {
        "rms",
        "energy",
        "relative_energy",
        "spectral_power",
        "spectral_centroid",
        "activity",
        "f0",
        "relative_pitch",
        "voicing_probability",
        "voiced",
    }
    if set(result.series) != expected_names:
        raise ValueError("Feature series missing or unexpected.")
    for name, series in result.series.items():
        units = {
            "rms": "full_scale",
            "energy": "dBFS",
            "relative_energy": "dB",
            "spectral_power": "full_scale_squared",
            "spectral_centroid": "Hz",
            "activity": "binary_energy_estimate",
            "f0": "Hz",
            "relative_pitch": "semitones",
            "voicing_probability": "pYIN_model_probability",
            "voiced": "binary",
        }
        if series.unit != units[name]:
            raise ValueError("Feature units differ from algorithm contract.")
        for value in series.values:
            if value is None:
                if name not in {"relative_energy", "f0", "relative_pitch"}:
                    raise ValueError("Unexpected unavailable acoustic measurement.")
            elif (
                name in {"rms", "spectral_power", "spectral_centroid", "f0"}
                and value < 0
                or name in {"activity", "voiced"}
                and value not in {0, 1}
                or name == "voicing_probability"
                and not 0 <= value <= 1
            ):
                raise ValueError("Acoustic measurement outside physical/model bounds.")
        length = 1024 if name in {"f0", "relative_pitch", "voicing_probability", "voiced"} else 400
        starts = list(range(0, max(0, q.sample_count - length + 1), 160))
        if (
            series.frame_length != length
            or series.hop_length != 160
            or series.start_samples != starts
            or len(series.values) != len(starts)
            or series.times_s != [(s + length / 2) / 16000 for s in starts]
        ):
            raise ValueError("Invalid feature frame coordinates/shape.")
    count = len(result.series["rms"].values)
    if len(result.mfcc) != count or any(len(row) != 13 for row in result.mfcc):
        raise ValueError("Invalid MFCC shape.")
    if len(result.spectrum_power) != count or any(len(row) != 257 for row in result.spectrum_power):
        raise ValueError("Invalid spectrum shape.")
    if result.frequencies_hz != np.fft.rfftfreq(512, 1 / 16000).tolist():
        raise ValueError("Invalid spectrum frequency coordinates.")
    if any(v < 0 for row in result.spectrum_power for v in row):
        raise ValueError("Negative spectral power.")
    for intervals in (
        result.activity,
        result.low_energy,
        result.pauses,
        result.voiced_regions,
        result.unvoiced_regions,
    ):
        previous = 0.0
        for interval in intervals:
            if not previous <= interval.start_s < interval.end_s <= q.duration_s:
                raise ValueError("Invalid acoustic interval bounds/order.")
            previous = interval.end_s
    cursor = 0
    for start, end, low, high in result.waveform:
        if start != cursor or not start < end <= q.sample_count or low > high:
            raise ValueError("Invalid waveform envelope.")
        cursor = end
    if cursor != q.sample_count:
        raise ValueError("Waveform envelope does not cover samples.")
    if result.speaking_rate_wpm is not None and (
        result.alignment_sha256 is None or not result.provenance.transcript_verified
    ):
        raise ValueError("Rate requires alignment and verified transcript.")


def validate_identity(root: Path, result: AlignmentResult | FeatureResult) -> None:
    recording, _, provenance = recording_input(root, result.provenance.recording_id)
    if result.provenance != provenance:
        raise ValueError(
            "Artifact input/code/environment provenance differs from current workspace."
        )
    if isinstance(result, AlignmentResult) and (
        result.original_text != recording.transcript.text
        or result.duration_s != recording.normalized_info.duration_s
    ):
        raise ValueError("Alignment text/duration differs from manifest.")
