"""Generated signals test descriptive observations, never real speech accuracy."""

import json

import numpy as np
import pytest

from taketwo.analysis.contracts import (
    AlignmentConfig,
    AlignmentResult,
    FeatureConfig,
    Interval,
    Resource,
)
from taketwo.analysis.features import extract
from taketwo.analysis.storage import recording_input
from taketwo.comparison.contracts import ArtifactRef
from taketwo.dataset.audio import inspect_samples, sample_hash, sha256, wav_bytes
from taketwo.dataset.schema import Dataset, Pair, content_hash
from taketwo.exploratory.contracts import ExploratoryConfig
from taketwo.exploratory.engine import Source, build, summarize
from taketwo.exploratory.storage import implementation_hash, publish, read_artifact


@pytest.fixture
def source(imported):
    root, recording = imported
    _, samples, provenance = recording_input(root, recording.id)
    features = extract(samples, provenance, FeatureConfig())
    return root, Source(
        recording,
        features,
        ArtifactRef(
            path="derived/fixture.json", sha256=content_hash(features.model_dump(mode="json"))
        ),
    )


def report(source, **changes):
    _, item = source
    arguments = dict(
        reference_id=item.recording.id,
        pair_id=None,
        job_id="j-fixture",
        processing_state="succeeded",
        implementation_sha256=implementation_hash(),
    )
    arguments.update(changes)
    return build(
        Dataset(dataset_version="test-v1", recordings=[item.recording]), [item], **arguments
    )


def test_native_support_and_candidate_evidence(source):
    _, item = source
    summary, candidates = summarize(item, ExploratoryConfig())
    assert summary.duration_s == 2
    assert summary.activity_support_s + summary.low_energy_support_s == pytest.approx(
        summary.observed_support_s
    )
    assert summary.observed_support_s + summary.unobserved_tail_s == pytest.approx(2)
    quiet = [c for c in candidates if c.kind == "internal_low_energy"]
    assert len(quiet) == 1
    assert quiet[0].start_s == pytest.approx(0.5)
    assert quiet[0].end_s <= 0.75
    for c in candidates:
        assert 0 <= c.start_s < c.end_s <= summary.duration_s
        assert c.duration_s == pytest.approx(c.end_s - c.start_s)
        assert c.feature_sha256 == item.feature_ref.sha256
        assert c.status == "automatic_unverified"
        assert c.boundary_resolution_s == 0.01
        assert c.threshold_delta_db == (6 if c.kind == "energy_change" else None)
        assert (c.threshold_dbfs is None) == (c.kind == "energy_change")
        if c.kind != "energy_change":
            levels = np.asarray(item.features.series["energy"].values)
            audible = (
                np.asarray(item.features.series["rms"].values) > item.features.config.energy_floor
            )
            seed = np.quantile(levels[audible], 0.75, method="linear")
            initial = audible & (levels >= seed - item.features.config.activity_drop_db)
            assert c.threshold_dbfs == pytest.approx(
                np.median(levels[initial]) - item.features.config.activity_drop_db
            )
    assert summary.automatic_alignment is None


@pytest.mark.parametrize(
    "signal_kind,size",
    [
        ("silence", 32000),
        ("quiet", 32000),
        ("short", 200),
        ("noise", 16000),
        ("clipped", 16000),
        ("step", 32000),
    ],
)
def test_signal_edge_cases(imported, signal_kind, size):
    root, recording = imported
    _, _, provenance = recording_input(root, recording.id)
    values = np.zeros(size, dtype=np.float32)
    if signal_kind == "quiet":
        values[:] = 1e-7
    if signal_kind == "noise":
        values = np.random.default_rng(42).normal(0, 0.02, size).astype(np.float32)
    if signal_kind == "clipped":
        values[:] = 1
    if signal_kind == "step":
        values = (0.2 * np.sin(2 * np.pi * 220 * np.arange(size) / 16000)).astype(np.float32)
        values[:16000] *= 0.1
    # Bypass acquisition only inside this extractor test: production imports reject
    # near-silence. Keep every generated signal's metadata and hashes truthful.
    info = inspect_samples(values, 16000, "WAV", "FLOAT")
    digest = sha256(wav_bytes(values))
    recording = recording.model_copy(
        update={
            "normalized_info": info,
            "original_info": info,
            "sample_sha256": sample_hash(values),
            "normalized_sha256": digest,
        }
    )
    provenance = provenance.model_copy(
        update={"sample_sha256": sample_hash(values), "audio_sha256": digest}
    )
    f = extract(values, provenance, FeatureConfig())
    item = Source(
        recording,
        f,
        ArtifactRef(path="fixture.json", sha256=content_hash(f.model_dump(mode="json"))),
    )
    summary, candidates = summarize(item, ExploratoryConfig())
    assert summary.duration_s == size / 16000
    assert all(c.end_s <= summary.duration_s for c in candidates)
    if signal_kind in {"silence", "quiet"}:
        assert summary.accepted_pitch_frames == 0
        assert any(c.kind == "recording_low_energy" for c in candidates)
    if signal_kind == "short":
        assert candidates == []
        assert summary.accepted_pitch_fraction is None
        assert summary.unobserved_tail_s == summary.duration_s
    if signal_kind == "clipped":
        assert summary.clipping_fraction == 1
    if signal_kind == "step":
        changes = [c for c in candidates if c.kind == "energy_change"]
        assert len(changes) == 1
        assert changes[0].energy_delta_db == pytest.approx(20, abs=0.1)


def test_deterministic_artifact_and_tamper(source):
    root, _ = source
    first = report(source)
    assert first == report(source)
    assert first.comparison is None and first.automatic_correspondence == []
    path = publish(root, first)
    before = path.stat().st_mtime_ns
    assert publish(root, first) == path
    assert path.stat().st_mtime_ns == before
    assert read_artifact(path) == first
    envelope = json.loads(path.read_text())
    envelope["result"]["job_id"] = "tampered"
    path.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="checksum"):
        read_artifact(path)
    with pytest.raises(ValueError, match="preserved"):
        publish(root, first)


def test_selection_and_provenance_rejection(source):
    _, item = source
    with pytest.raises(ValueError, match="pair"):
        report(source, pair_id="missing-pair")
    bad = Source(
        item.recording, item.features, item.feature_ref.model_copy(update={"sha256": "0" * 64})
    )
    with pytest.raises(ValueError, match="identity"):
        summarize(bad, ExploratoryConfig())
    bad = Source(
        item.recording.model_copy(update={"original_filename": "other.wav"}),
        item.features,
        item.feature_ref,
    )
    dataset = Dataset(dataset_version="test-v1", recordings=[item.recording])
    with pytest.raises(ValueError, match="current dataset"):
        build(
            dataset,
            [bad],
            reference_id=item.recording.id,
            pair_id=None,
            job_id="j-fixture",
            processing_state="succeeded",
            implementation_sha256=implementation_hash(),
        )


def test_rejects_a_structurally_valid_but_incorrect_activity_mask(source):
    _, item = source
    features = item.features.model_copy(deep=True)
    features.series["activity"].values[0] = 1 - features.series["activity"].values[0]
    changed = Source(
        item.recording,
        features,
        ArtifactRef(path="fixture.json", sha256=content_hash(features.model_dump(mode="json"))),
    )
    with pytest.raises(ValueError, match="activity mask"):
        summarize(changed, ExploratoryConfig())


@pytest.mark.parametrize(
    "status,oov", [("succeeded", []), ("partial", []), ("succeeded", ["only"])]
)
def test_automatic_rate_is_separate_and_abstains_for_incomplete_alignment(imported, status, oov):
    root, recording = imported
    _, samples, provenance = recording_input(root, recording.id)
    resource = Resource(
        path="fixture-only",
        sha256="0" * 64,
        version="fixture",
        license="fixture",
        source_url="https://example.invalid/software",
    )
    alignment = AlignmentResult(
        provenance=provenance,
        config=AlignmentConfig(
            command=["fixture-only"],
            expected_version="fixture",
            model=resource,
            dictionary=resource,
        ),
        duration_s=2.0,
        original_text=recording.transcript.text,
        normalized_tokens=recording.tokens,
        token_offsets=recording.token_offsets,
        status=status,
        oov=oov,
        words=[
            Interval(start_s=0.1 + i * 0.4, end_s=0.3 + i * 0.4, label=token, token_index=i)
            for i, token in enumerate(
                recording.tokens[:3] if status == "partial" else recording.tokens
            )
        ],
    )
    features = extract(samples, provenance, FeatureConfig(), alignment)
    item = Source(
        recording,
        features,
        ArtifactRef(path="features.json", sha256=content_hash(features.model_dump(mode="json"))),
        alignment,
        ArtifactRef(path="alignment.json", sha256=content_hash(alignment.model_dump(mode="json"))),
    )
    summary, _ = summarize(item, ExploratoryConfig())
    automatic = summary.automatic_alignment
    assert automatic.independently_verified is False
    assert recording.transcript.status == "unverified"
    if status == "succeeded" and not oov:
        assert automatic.estimated_words_per_minute == pytest.approx(60 * 4 / 1.4)
    else:
        assert automatic.estimated_words_per_minute is None
        assert automatic.rate_unavailable_reason


def test_pair_deltas_and_partial_input(source):
    _, item = source
    participant = item.recording.model_copy(update={"id": "participant", "role": "participant"})
    f = item.features.model_copy(
        update={
            "provenance": item.features.provenance.model_copy(
                update={"recording_id": participant.id}
            )
        }
    )
    second = Source(
        participant,
        f,
        ArtifactRef(path="participant.json", sha256=content_hash(f.model_dump(mode="json"))),
    )
    pair = Pair(
        id="pair-fixture",
        reference_id=item.recording.id,
        participant_id=participant.id,
        transcript_sha256=item.recording.transcript_sha256,
        intended_flaw="unspecified",
        intended_severity=None,
        identity_status="needs_review",
    )
    dataset = Dataset(
        dataset_version="test-v1", recordings=[item.recording, participant], pairs=[pair]
    )
    arguments = dict(
        reference_id=item.recording.id,
        pair_id=pair.id,
        job_id="j-fixture",
        processing_state="succeeded",
        implementation_sha256=implementation_hash(),
    )
    result = build(dataset, [second, item], **arguments)
    assert result.recordings[0].recording_id == item.recording.id
    assert result.comparison.duration_delta_s == 0
    assert result.comparison.relative_duration_delta_percent == 0
    assert result.comparison.rms_level_delta_db == 0
    assert "equal duration" in result.comparison.interpretation
    assert "speech rate" in result.comparison.interpretation
    assert "scores" not in result.model_dump()
    partial = build(dataset, [item], unavailable={participant.id: "features failed"}, **arguments)
    assert partial.state == "partial" and partial.comparison is None
    assert partial.unavailable_recordings == {participant.id: "features failed"}
