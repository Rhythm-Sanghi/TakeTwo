"""Independent acoustic checks; generated fixtures are not real speech accuracy evidence."""

import copy
import json
import subprocess
import sys
import threading
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError
from scipy.signal import windows

from taketwo.analysis.alignment import align, execute, parse_textgrid, preflight, validate_alignment
from taketwo.analysis.contracts import (
    AlignmentConfig,
    AlignmentResult,
    FeatureConfig,
    Interval,
    Resource,
)
from taketwo.analysis.features import extract as extract_engine
from taketwo.analysis.storage import (
    publish,
    read_artifact,
    recording_input,
    validate_features,
    validate_identity,
)
from taketwo.dataset.audio import sample_hash, sha256
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import canonical_json, content_hash


def extract(samples, provenance, config, alignment=None):
    # Each generated signal is a distinct test input; preserve truthful sample identity.
    provenance = provenance.model_copy(update={"sample_sha256": sample_hash(samples)})
    return extract_engine(samples, provenance, config, alignment)


@pytest.fixture
def inputs(imported):
    root, recording = imported
    _, samples, provenance = recording_input(root, recording.id)
    return root, recording, samples, provenance


@pytest.fixture
def backend(tmp_path):
    dictionary = tmp_path / "test.dict"
    dictionary.write_text(
        "generated JH EH N\nsignal S IH G\nfixture F IH K\nonly OW N\n"
        "i AY\na AH\nmister M IH S T ER\n",
        encoding="utf-8",
    )
    model = tmp_path / "test-model.zip"
    model.write_bytes(b"fixture-not-a-real-model")

    def resource(path):
        return Resource(
            path=str(path),
            sha256=sha256(path.read_bytes()),
            version="test-fixture",
            license="test-only",
            source_url="https://example.invalid/test",
        )

    return AlignmentConfig(
        command=[sys.executable],
        expected_version="fixture-version",
        dictionary=resource(dictionary),
        model=resource(model),
        timeout_s=1.0,
    )


def test_signal_physics(inputs):
    _, _, _, provenance = inputs
    t = np.arange(16000) / 16000
    x = 0.2 * np.sin(2 * np.pi * 400 * t)
    result = extract(x, provenance, FeatureConfig())
    validate_features(result)
    assert result.quality.rms == pytest.approx(0.2 / np.sqrt(2), abs=1e-8)
    assert np.median(result.series["rms"].values) == pytest.approx(0.2 / np.sqrt(2), abs=1e-8)
    assert np.median(result.series["energy"].values) == pytest.approx(
        20 * np.log10(0.2 / np.sqrt(2))
    )
    power = np.array(result.spectrum_power)
    assert abs(result.frequencies_hz[int(np.argmax(power[10]))] - 400) <= 16000 / 512 / 2
    window = windows.hann(400, sym=False)
    expected = np.sum((x[1600:2000] * window) ** 2) / np.sum(window**2)
    assert result.series["spectral_power"].values[10] == pytest.approx(expected, abs=1e-8)
    assert np.array(result.mfcc).shape == (98, 13)
    assert np.isfinite(result.mfcc).all()
    assert result.series["energy"].times_s[:2] == [0.0125, 0.0225]
    assert result.series["f0"].times_s[:2] == [0.032, 0.042]
    measured = np.array([v for v in result.series["f0"].values if v is not None])
    assert len(measured) > 80
    assert np.median(measured) == pytest.approx(400, rel=0.015)
    assert result.quality.spectral_covered_until_s == 0.995
    assert result.quality.pitch_covered_until_s == 0.994


def test_pause_support_and_gain_invariance(inputs):
    _, _, x, provenance = inputs
    a = extract(x, provenance, FeatureConfig())
    b = extract(x * 0.5, provenance, FeatureConfig())
    assert any(abs(p.start_s - 0.5) <= 0.03 and abs(p.end_s - 0.75) <= 0.03 for p in a.low_energy)
    assert a.pauses == [] and a.speaking_rate_wpm is None
    assert a.energy_baseline_dbfs - b.energy_baseline_dbfs == pytest.approx(
        20 * np.log10(2), abs=1e-6
    )
    av = np.array(a.series["relative_energy"].values)
    bv = np.array(b.series["relative_energy"].values)
    active = np.array(a.series["activity"].values) == 1
    np.testing.assert_allclose(av[active], bv[active], atol=1e-6)
    assert a.energy_range_db == pytest.approx(b.energy_range_db, abs=1e-6)


def test_register_normalization(inputs):
    _, _, _, provenance = inputs
    t = np.arange(16000) / 16000
    a = extract(0.2 * np.sin(2 * np.pi * 200 * t), provenance, FeatureConfig())
    b = extract(0.2 * np.sin(2 * np.pi * 300 * t), provenance, FeatureConfig())
    assert a.pitch_baseline_hz == pytest.approx(200, rel=0.015)
    assert b.pitch_baseline_hz == pytest.approx(300, rel=0.015)
    assert abs(np.nanmedian([v for v in a.series["relative_pitch"].values if v is not None])) < 0.01
    assert abs(np.nanmedian([v for v in b.series["relative_pitch"].values if v is not None])) < 0.01


@pytest.mark.parametrize("size", [1, 399, 400, 1023, 1024, 16000])
def test_silence_short_and_finite(inputs, size):
    result = extract(np.zeros(size), inputs[-1], FeatureConfig())
    validate_features(result)
    assert all(v is None for v in result.series["f0"].values)
    assert result.pitch_baseline_hz is None
    assert result.energy_baseline_dbfs is None
    assert np.isfinite(result.mfcc).all()
    assert all(v == -120 for v in result.series["energy"].values)


def test_unvoiced_noise_clipping(inputs):
    noise = np.random.default_rng(17).normal(0, 0.05, 16000)
    result = extract(noise, inputs[-1], FeatureConfig())
    assert sum(v == 1 for v in result.series["voiced"].values) < 10
    assert extract(np.ones(400), inputs[-1], FeatureConfig()).quality.flags.count("clipping") == 1


@pytest.mark.parametrize(
    "x", [np.array([]), np.array([np.nan]), np.array([np.inf]), np.zeros((5, 2)), np.zeros(480001)]
)
def test_invalid_signal(inputs, x):
    with pytest.raises(DatasetError):
        extract(x, inputs[-1], FeatureConfig())


def test_artifact_repeatability_hash_and_input(inputs):
    root, recording, x, provenance = inputs
    a = extract(x, provenance, FeatureConfig())
    b = extract(x.copy(), provenance, FeatureConfig())
    assert canonical_json(a.model_dump(mode="json")) == canonical_json(b.model_dump(mode="json"))
    before = (root / "manifest.jsonl").read_bytes()
    path = publish(root, a)
    assert publish(root, b) == path
    assert read_artifact(path) == a
    validate_identity(root, a)
    assert (root / "manifest.jsonl").read_bytes() == before
    payload = json.loads(path.read_text())
    payload["result"]["quality"]["peak"] += 0.1
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="hash"):
        read_artifact(path)
    (root / recording.normalized_path).write_bytes(b"corrupt")
    with pytest.raises(DatasetError):
        recording_input(root, recording.id)


@pytest.mark.parametrize(
    "change", ["frames", "time", "mfcc", "spectrum", "interval", "waveform", "rate"]
)
def test_invalid_feature_artifacts(inputs, change):
    result = extract(np.zeros(1600), inputs[-1], FeatureConfig())
    if change == "frames":
        result.series["rms"].start_samples[0] = 1
    elif change == "time":
        result.series["f0"].times_s[0] = 10
    elif change == "mfcc":
        result.mfcc[0].pop()
    elif change == "spectrum":
        result.spectrum_power[0][0] = -1
    elif change == "interval":
        result.low_energy[0].end_s = 10
    elif change == "waveform":
        result.waveform.pop()
    else:
        result.speaking_rate_wpm = 100.0
    with pytest.raises(ValueError):
        validate_features(result)


def alignment_fixture(inputs, backend):
    _, recording, _, provenance = inputs
    return AlignmentResult(
        provenance=provenance,
        config=backend,
        duration_s=2.0,
        original_text=recording.transcript.text,
        normalized_tokens=recording.tokens,
        token_offsets=recording.token_offsets,
        status="succeeded",
        words=[
            Interval(start_s=s, end_s=e, label=label, token_index=i)
            for i, (s, e, label) in enumerate(
                [
                    (0.1, 0.3, "generated"),
                    (0.8, 1.0, "signal"),
                    (1.1, 1.3, "fixture"),
                    (1.4, 1.6, "only"),
                ]
            )
        ],
    )


def test_rate_requires_verified_transcript(inputs, backend):
    alignment = alignment_fixture(inputs, backend)
    result = extract(inputs[2], inputs[-1], FeatureConfig(), alignment)
    assert result.speaking_rate_wpm is None
    alignment.provenance.transcript_verified = True  # Explicit test assertion, not a real review.
    x = inputs[2].copy()
    x[4800:12800] = 0
    alignment.provenance = alignment.provenance.model_copy(update={"sample_sha256": sample_hash(x)})
    result = extract(x, alignment.provenance, FeatureConfig(), alignment)
    assert result.speaking_rate_wpm == pytest.approx(160.0)
    assert len(result.pauses) == 1
    assert result.articulation_rate_wpm == pytest.approx(240.0)
    alignment.provenance = alignment.provenance.model_copy(update={"audio_sha256": "0" * 64})
    with pytest.raises(DatasetError):
        extract(x, inputs[-1], FeatureConfig(), alignment)


@pytest.mark.parametrize(
    "change", ["zero", "outside", "overlap", "coverage", "index", "text", "failed"]
)
def test_alignment_bounds(inputs, backend, change):
    result = alignment_fixture(inputs, backend)
    if change == "zero":
        result.words[0].end_s = result.words[0].start_s
    elif change == "outside":
        result.words[-1].end_s = 3
    elif change == "overlap":
        result.words[1].start_s = 0.2
    elif change == "coverage":
        result.words.pop()
    elif change == "index":
        result.words[0].token_index = 100
    elif change == "text":
        result.words[0].label = "unexpected"
    else:
        result.status = "failed"
    with pytest.raises(ValueError):
        validate_alignment(result)


def test_dictionary_preflight(backend):
    original = "Generated, signal fixture only!"
    tokens, offsets, oov = preflight(original, backend)
    assert tokens == ["generated", "signal", "fixture", "only"] and not oov
    assert original[offsets[0][0] : offsets[0][1]] == "Generated"
    assert preflight("Mr. X 12 unknown", backend)[2] == ["12", "mr", "unknown", "x"]
    backend.replacements = {"mr": "mister"}
    assert preflight("Mr.", backend)[0] == ["mister"]
    backend.replacements = {"mr": "two words"}
    with pytest.raises(ValueError):
        preflight("Mr.", backend)


def test_missing_resources_and_backend_failure(inputs, backend):
    root, recording, _, provenance = inputs
    audio = root / recording.normalized_path
    for resource in ["model", "dictionary"]:
        config = copy.deepcopy(backend)
        getattr(config, resource).path += ".missing"
        result = align(audio, recording.transcript.text, provenance, 2.0, config)
        assert result.status == "failed" and result.words == []
        assert any(d.code == f"missing_{resource}" for d in result.diagnostics)
    result = align(audio, recording.transcript.text, provenance, 2.0, backend)
    assert result.status == "failed" and not result.words
    backend.command = ["missing-taketwo-aligner.exe"]
    assert align(audio, recording.transcript.text, provenance, 2.0, backend).status == "failed"


def test_timeout_cancellation_cleanup(tmp_path):
    script = tmp_path / "slow.py"
    script.write_text("import time\ntime.sleep(30)\n")
    state, _, code = execute([sys.executable, str(script)], tmp_path, 0.15)
    assert state == "timeout" and code is not None
    cancel = threading.Event()
    cancel.set()
    state, _, code = execute([sys.executable, str(script)], tmp_path, 5, cancel)
    assert state == "cancelled" and code is not None


def test_textgrid_parser():
    grid = """item [1]:
      name = "words"
      intervals [1]:
        xmin = 0
        xmax = 0.1
        text = ""
      intervals [2]:
        xmin = 0.1
        xmax = 0.5
        text = "hello"
    item [2]:
      name = "phones"
      intervals [1]:
        xmin = 0.1
        xmax = 0.2
        text = "HH"
    """
    words, phones = parse_textgrid(grid)
    assert words[0].label == "hello" and phones[0].label == "HH"
    with pytest.raises(ValidationError):
        parse_textgrid(grid.replace("xmax = 0.5", "xmax = 0.1"))


def command(*args):
    return subprocess.run(
        [sys.executable, "-m", "taketwo.analysis.cli", *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_analysis_cli(inputs, backend, tmp_path):
    root, recording, _, _ = inputs
    extracted = command("extract", root, "--recording", recording.id)
    assert extracted.returncode == 0, extracted.stderr
    artifact = json.loads(extracted.stdout)["artifact"]
    assert command("inspect", root, "--artifact", artifact).returncode == 0
    assert command("validate", root, "--artifact", artifact, "--reproduce").returncode == 0
    export = tmp_path / "analysis-export.json"
    assert command("export", root, "--artifact", artifact, "--output", export).returncode == 0
    assert command("export", root, "--artifact", artifact, "--output", export).returncode == 2
    configuration = tmp_path / "backend.json"
    backend.command = ["missing-aligner.exe"]
    configuration.write_text(canonical_json(backend.model_dump(mode="json")))
    assert command("check", "--config", configuration).returncode == 1
    failed = command("align", root, "--recording", recording.id, "--config", configuration)
    assert failed.returncode == 1
    assert read_artifact(Path(json.loads(failed.stdout)["artifact"])).status == "failed"
    assert command("bad-command").returncode == 2
    assert command("extract", root, "--recording", "missing").returncode == 2


def test_contract_schema_and_unknown_version(inputs):
    result = extract(np.zeros(400), inputs[-1], FeatureConfig())
    data = result.model_dump(mode="json")
    data["schema_version"] = 99
    with pytest.raises(ValidationError):
        type(result).model_validate_json(canonical_json(data))
    assert content_hash(data) != content_hash(result.model_dump(mode="json"))


def test_sample_identity_and_overlapping_frame_support(inputs):
    from taketwo.analysis.features import runs

    with pytest.raises(DatasetError, match="provenance"):
        extract_engine(inputs[2] * 0.5, inputs[-1], FeatureConfig())
    regions = runs(np.array([True, False, True]), np.array([0, 160, 320]), 400, "test")
    assert len(regions) == 1 and regions[0].end_s == 720 / 16000


def test_adapter_execution_states(inputs, backend, monkeypatch):
    import taketwo.analysis.alignment as adapter

    root, recording, _, provenance = inputs
    calls = []

    def timeout(command, directory, timeout, cancel=None):
        calls.append(command)
        if len(calls) == 1:
            return "succeeded", "fixture-version", 0
        return "timeout", "fixture timeout", -1

    monkeypatch.setattr(adapter, "execute", timeout)
    result = align(
        root / recording.normalized_path, recording.transcript.text, provenance, 2.0, backend
    )
    assert result.status == "timeout" and result.words == []
    assert "--no_use_mp" in calls[-1]
    assert not Path(calls[-1][-1]).parent.exists()


def test_analysis_schema_snapshot():
    from taketwo.analysis.contracts import FeatureResult

    path = Path(__file__).resolve().parents[1] / "docs/analysis-schema-v1.json"
    assert json.loads(path.read_text()) == {
        "alignment": AlignmentResult.model_json_schema(),
        "features": FeatureResult.model_json_schema(),
    }


def test_mfcc_reproducible_across_external_blas_limits(inputs):
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1, user_api="blas"):
        first = extract(inputs[2], inputs[-1], FeatureConfig())
    with threadpool_limits(limits=2, user_api="blas"):
        second = extract(inputs[2], inputs[-1], FeatureConfig())
    assert first == second
