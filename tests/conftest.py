"""Short generated signals are test fixtures, never competition dataset recordings."""

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from taketwo.dataset.schema import ImportSpec, canonical_json
from taketwo.dataset.workspace import import_recording, initialize


@pytest.fixture
def signal() -> np.ndarray:
    rate = 16000
    x = (0.2 * np.sin(2 * np.pi * 220 * np.arange(rate * 2) / rate)).astype(np.float32)
    x[8000:12000] = 0
    return x


@pytest.fixture
def audio_path(tmp_path: Path, signal: np.ndarray) -> Path:
    path = tmp_path / "test-signal.wav"
    sf.write(path, signal, 16000, subtype="FLOAT")
    return path


@pytest.fixture
def metadata() -> dict:
    return {
        "family_id": "test-family",
        "speaker_id": "test-oscillator",
        "origin": "source",
        "transcript": {
            "text": "Generated signal fixture only.",
            "language": "en",
            "status": "unverified",
            "reviewers": [],
            "verification_date": None,
            "revision": "v1",
        },
        "provenance": {
            "source_id": "test-source",
            "work_id": "test-work",
            "source": "pytest generated tone",
            "source_url": None,
            "collection_method": "NumPy oscillator; not speech",
            "access_date": "2026-10-11",
            "excerpt_offset_s": 0.0,
            "baseline_rationale": "Software fixture only; not an effective public speech",
            "consent_evidence": None,
            "rights": {
                "status": "pending",
                "holder": "test fixture generator",
                "license_name": "not a released dataset",
                "evidence": "tests/conftest.py",
                "attribution": "generated test signal",
                "permits_adaptation": False,
                "permits_redistribution": False,
            },
        },
    }


@pytest.fixture
def spec(metadata: dict) -> ImportSpec:
    return ImportSpec.model_validate_json(canonical_json(metadata))


@pytest.fixture
def imported(tmp_path: Path, audio_path: Path, spec: ImportSpec):
    root = tmp_path / "workspace"
    initialize(root, "test-v1")
    recording = import_recording(root, audio_path, spec)
    return root, recording
