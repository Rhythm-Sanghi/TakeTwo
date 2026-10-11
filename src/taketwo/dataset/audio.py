"""Bounded WAV/FLAC decoding and reproducible mono 16 kHz normalization."""

import hashlib
import io
import math
import platform
import struct
from importlib.metadata import version
from pathlib import Path

import numpy as np
import soundfile as sf
from numpy.typing import NDArray
from scipy.signal import resample_poly

from .errors import DatasetError
from .schema import AudioInfo
from .storage import safe_path

RATE = 16000
MAX_BYTES = 100 * 1024 * 1024


def versions() -> dict[str, str]:
    return {
        name: version(name) for name in ("taketwo", "numpy", "scipy", "soundfile", "librosa")
    } | {"python": platform.python_version(), "libsndfile": sf.__libsndfile_version__}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sample_hash(samples: NDArray[np.float32]) -> str:
    return sha256(np.asarray(samples, dtype="<f4").tobytes())


def inspect_samples(samples: NDArray, rate: int, container: str, subtype: str) -> AudioInfo:
    if not np.isfinite(samples).all():
        raise DatasetError(
            "nonfinite_audio", "Audio contains NaN or infinity.", "Re-export finite PCM samples."
        )
    rms = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))
    return AudioInfo(
        format=container,
        subtype=subtype,
        sample_rate_hz=rate,
        channels=1 if samples.ndim == 1 else samples.shape[1],
        frames=len(samples),
        duration_s=len(samples) / rate,
        rms_dbfs=20 * math.log10(max(rms, 1e-12)),
        peak=float(np.max(np.abs(samples))),
        clipping_fraction=float(np.mean(np.abs(samples) >= 0.999)),
    )


def decode(data: bytes) -> tuple[NDArray[np.float32], AudioInfo]:
    if len(data) > MAX_BYTES:
        raise DatasetError("size_limit", "Audio exceeds 100 MiB.", "Import a shorter excerpt.")
    if data[:4] == b"RIFF":
        validate_wav_chunks(data)
    try:
        with sf.SoundFile(io.BytesIO(data)) as stream:
            if stream.format not in {"WAV", "FLAC"} or stream.subtype not in {
                "PCM_16",
                "PCM_24",
                "PCM_32",
                "PCM_U8",
                "PCM_S8",
                "FLOAT",
                "DOUBLE",
            }:
                raise DatasetError(
                    "unsupported_encoding",
                    "Only PCM/float WAV and PCM FLAC are supported.",
                    "Export a PCM WAV or FLAC file.",
                )
            if not 8000 <= stream.samplerate <= 96000 or stream.channels not in (1, 2):
                raise DatasetError(
                    "audio_format",
                    "Expected 8-96 kHz, one or two channels.",
                    "Re-export within supported limits.",
                )
            if stream.frames < 1 or stream.frames / stream.samplerate > 600:
                raise DatasetError(
                    "audio_duration",
                    "Expected nonempty audio up to 600 seconds.",
                    "Import a nonempty excerpt of at most ten minutes.",
                )
            samples = stream.read(dtype="float32", always_2d=True)
            if len(samples) != stream.frames:
                raise DatasetError(
                    "truncated_audio",
                    "Decoded frame count differs from header.",
                    "Re-export the damaged file.",
                )
            info = inspect_samples(samples, stream.samplerate, stream.format, stream.subtype)
    except (sf.LibsndfileError, RuntimeError, ValueError) as exc:
        raise DatasetError(
            "audio_decode",
            "Audio is corrupt or unreadable.",
            "Check the input and re-export WAV/FLAC.",
        ) from exc
    return samples, info


def validate_wav_chunks(data: bytes) -> None:
    """Reject truncation that permissive audio decoders can otherwise conceal."""

    def malformed() -> None:
        raise DatasetError(
            "audio_decode",
            "WAV chunks are corrupt or truncated.",
            "Re-export the complete PCM/float WAV file.",
        )

    if (
        len(data) < 12
        or data[8:12] != b"WAVE"
        or struct.unpack_from("<I", data, 4)[0] + 8 != len(data)
    ):
        malformed()
    cursor = 12
    chunks: dict[bytes, bytes] = {}
    while cursor < len(data):
        if cursor + 8 > len(data):
            malformed()
        name, size = data[cursor : cursor + 4], struct.unpack_from("<I", data, cursor + 4)[0]
        start = cursor + 8
        end = start + size
        if end + size % 2 > len(data) or (name in {b"fmt ", b"data"} and name in chunks):
            malformed()
        chunks[name] = data[start:end]
        cursor = end + size % 2
    if b"fmt " not in chunks or b"data" not in chunks or len(chunks[b"fmt "]) < 16:
        malformed()
    block_align = struct.unpack_from("<H", chunks[b"fmt "], 12)[0]
    if not block_align or len(chunks[b"data"]) % block_align:
        malformed()


def read_audio(path: Path) -> tuple[bytes, NDArray[np.float32], AudioInfo]:
    safe_path(path)
    if path.suffix.lower() not in {".wav", ".flac"}:
        raise DatasetError(
            "unsupported_format",
            "Input extension must be .wav or .flac.",
            "Export WAV/FLAC.",
            str(path),
        )
    if not path.is_file():
        raise DatasetError(
            "missing_audio",
            "Input audio file does not exist.",
            "Check the local audio path.",
            str(path),
        )
    if path.stat().st_size > MAX_BYTES:
        raise DatasetError("size_limit", "Audio exceeds 100 MiB.", "Use a shorter excerpt.")
    data = path.read_bytes()
    samples, info = decode(data)
    expected_format = "WAV" if path.suffix.lower() == ".wav" else "FLAC"
    if info.format != expected_format:
        raise DatasetError(
            "format_mismatch",
            "Extension differs from decoded container.",
            "Use the correct extension.",
            str(path),
        )
    return data, samples, info


def normalize(samples: NDArray[np.float32], rate: int, channel: int | None) -> NDArray[np.float32]:
    if channel is not None:
        if channel >= samples.shape[1]:
            raise DatasetError(
                "channel",
                "Selected channel does not exist.",
                "Select channel 0 or an available channel 1.",
            )
        mono = samples[:, channel]
    else:
        mono = samples.mean(axis=1)
        if samples.shape[1] == 2 and np.mean(mono**2) < 0.01 * np.mean(samples**2):
            raise DatasetError(
                "channel_cancellation",
                "Stereo averaging cancels the signal.",
                "Review channels and specify channel 0 or 1.",
            )
    divisor = math.gcd(rate, RATE)
    normalized = resample_poly(
        mono.astype(np.float64),
        RATE // divisor,
        rate // divisor,
        window=("kaiser", 5.0),
        padtype="constant",
    ).astype(np.float32)
    return normalized


def quality(info: AudioInfo) -> list[str]:
    return (["near_silent"] if info.rms_dbfs < -60 else []) + (
        ["clipping"] if info.clipping_fraction > 0.001 or info.peak > 1 else []
    )


def wav_bytes(samples: NDArray[np.float32]) -> bytes:
    # libsndfile's FLOAT writer adds a volatile timestamp in its PEAK chunk.
    # Emit the minimal IEEE float WAV plus fact chunk, with no optional metadata.
    data = np.asarray(samples, dtype="<f4").tobytes()
    fmt = struct.pack("<HHIIHH", 3, 1, RATE, RATE * 4, 4, 32)
    chunks = (
        b"fmt "
        + struct.pack("<I", len(fmt))
        + fmt
        + b"fact"
        + struct.pack("<II", 4, len(samples))
        + b"data"
        + struct.pack("<I", len(data))
        + data
    )
    return b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks
