"""Generated-signal contract checks, not independently evaluated speech accuracy."""

import json

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
from taketwo.dataset.schema import Dataset, Pair, content_hash
from taketwo.exploratory.contracts import AcousticCandidate, ExploratoryConfig
from taketwo.exploratory.engine import Source, summarize
from taketwo.exploratory.engine import build as exploratory
from taketwo.insights.engine import build, group_candidates, local_measurements, matching_reason
from taketwo.insights.storage import implementation_hash, publish, read_artifact


@pytest.fixture
def paired(imported):
    root, recording = imported
    _, samples, provenance = recording_input(root, recording.id)
    resource = Resource(
        path="fixture",
        sha256="0" * 64,
        version="fixture",
        license="fixture",
        source_url="https://example.invalid/software",
    )
    sources = []
    for rid, role, shift in [(recording.id, "reference", 0), ("participant", "participant", 0.02)]:
        r = recording.model_copy(update={"id": rid, "role": role})
        p = provenance.model_copy(update={"recording_id": rid})
        alignment = AlignmentResult(
            provenance=p,
            config=AlignmentConfig(
                command=["fixture"], expected_version="fixture", model=resource, dictionary=resource
            ),
            duration_s=2,
            original_text=r.transcript.text,
            normalized_tokens=r.tokens,
            token_offsets=r.token_offsets,
            status="succeeded",
            words=[
                Interval(
                    start_s=0.1 + i * 0.4 + shift,
                    end_s=0.3 + i * 0.4 + shift,
                    label=token,
                    token_index=i,
                )
                for i, token in enumerate(r.tokens)
            ],
        )
        features = extract(samples, p, FeatureConfig(), alignment)
        sources.append(
            Source(
                r,
                features,
                ArtifactRef(
                    path=rid + "-f.json", sha256=content_hash(features.model_dump(mode="json"))
                ),
                alignment,
                ArtifactRef(
                    path=rid + "-a.json", sha256=content_hash(alignment.model_dump(mode="json"))
                ),
            )
        )
    pair = Pair(
        id="pair",
        reference_id=recording.id,
        participant_id="participant",
        transcript_sha256=recording.transcript_sha256,
        intended_flaw="unspecified",
        intended_severity=None,
        identity_status="needs_review",
    )
    report = exploratory(
        Dataset(dataset_version="test-v1", recordings=[s.recording for s in sources], pairs=[pair]),
        sources,
        reference_id=recording.id,
        pair_id=pair.id,
        job_id="fixture-job",
        processing_state="completed",
        implementation_sha256="0" * 64,
    )
    return root, report, sources


def windows(report, specifications):
    r = report.recordings[0]
    return report.model_copy(
        update={
            "candidates": [
                AcousticCandidate(
                    id=f"c-{i}",
                    recording_id=r.recording_id,
                    feature_sha256=r.feature_artifact.sha256,
                    kind=kind,
                    start_s=start,
                    end_s=end,
                    duration_s=end - start,
                    median_energy_dbfs=-30,
                    energy_delta_db=delta,
                    method="fixture",
                    threshold_dbfs=None,
                    threshold_delta_db=6 if kind == "energy_change" else None,
                    frame_window_s=0.025,
                    boundary_resolution_s=0.01,
                    explanation="Generated evidence",
                    limitation="Software fixture",
                )
                for i, (start, end, kind, delta) in enumerate(specifications)
            ]
        }
    )


@pytest.mark.parametrize(
    "bounds,count",
    [
        ([(0, 0.5), (0.25, 0.75), (0.5, 1)], 1),
        ([(0, 0.5), (0.5, 1), (1, 1.5)], 1),
        ([(0, 0.5), (0.51, 1)], 2),
        ([(0, 1), (0, 0.5)], 1),
    ],
)
def test_connected_overlap_touch_and_no_positive_gap(paired, bounds, count):
    _, report, _ = paired
    report = windows(report, [(a, b, "energy_change", 6) for a, b in bounds])
    groups = group_candidates(report)
    assert len(groups) == count
    assert sum(len(g.candidate_ids) for g in groups) == len(bounds)
    assert (
        group_candidates(report.model_copy(update={"candidates": report.candidates[::-1]}))
        == groups
    )


def test_opposing_categories_and_configuration_stay_separate(paired):
    _, report, _ = paired
    report = windows(
        report,
        [
            (0, 1, "energy_change", 6),
            (0.5, 1.5, "energy_change", -8),
            (0.5, 1.5, "internal_low_energy", None),
        ],
    )
    assert len(group_candidates(report)) == 3
    report.candidates.append(
        report.candidates[0].model_copy(update={"id": "changed", "threshold_delta_db": 7})
    )
    assert len(group_candidates(report)) == 4


@pytest.mark.parametrize(
    "changes",
    [
        {"start_s": -0.1},
        {"end_s": 3},
        {"duration_s": 0.1},
        {"median_energy_dbfs": float("nan")},
        {"energy_delta_db": None},
        {"energy_delta_db": 0},
        {"recording_id": "foreign"},
        {"feature_sha256": "0" * 64},
        {"boundary_resolution_s": 0},
    ],
)
def test_invalid_incomplete_foreign_candidates_rejected(paired, changes):
    _, report, _ = paired
    report = windows(report, [(0, 1, "energy_change", 6)])
    report.candidates[0] = report.candidates[0].model_copy(update=changes)
    with pytest.raises(ValueError):
        group_candidates(report)


def test_duplicate_id_rejected_without_losing_raw_inventory(paired):
    _, report, sources = paired
    result = build(report, sources, implementation_hash())
    assert result.exploratory.candidates == report.candidates
    assert sorted(i for g in result.groups for i in g.candidate_ids) == sorted(
        c.id for c in report.candidates
    )
    assert build(report, sources[::-1], implementation_hash()) == result
    report.candidates.append(report.candidates[0])
    with pytest.raises(ValueError, match="duplicate"):
        group_candidates(report)


def test_native_word_deltas_phrase_abstention_and_valid_partition(paired):
    _, report, sources = paired
    result = build(report, sources, implementation_hash())
    assert len(result.segments) == 4 and result.correspondence_unavailable_reason is None
    assert result.phrase_unavailable_reason
    word = result.segments[1]
    assert word.participant.start_s - word.reference.start_s == pytest.approx(0.02)
    assert word.duration_delta_s == pytest.approx(0)
    assert word.gap_delta_s == pytest.approx(0)
    assert word.status == "automatic_unverified"
    phrase = build(report, sources, implementation_hash(), [(0, 2), (2, 4)], ["1" * 64])
    assert len(phrase.segments) == 6 and phrase.phrase_unavailable_reason is None
    assert phrase.phrase_review_sha256 == ["1" * 64]
    with pytest.raises(ValueError, match="partition"):
        build(report, sources, implementation_hash(), [(0, 3), (2, 4)])


@pytest.mark.parametrize(
    "change", ["partial", "missing", "oov", "offsets", "text", "tokens", "indices"]
)
def test_correspondence_abstains_for_ambiguity(paired, change):
    _, _, sources = paired
    b = sources[1].alignment.model_copy(deep=True)
    if change == "partial":
        b.status = "partial"
    if change == "missing":
        sources[1].alignment = None
    if change == "oov":
        b.oov = ["fixture"]
    if change == "offsets":
        b.token_offsets[0] = (1, 2)
    if change == "text":
        b.original_text = "Different supplied text"
    if change == "tokens":
        b.normalized_tokens[0] = "different"
    if change == "indices":
        b.words[1].token_index = 0
    if change != "missing":
        sources[1].alignment = b
    assert matching_reason(sources)


def test_repeated_text_requires_complete_indexed_mapping(paired):
    _, _, sources = paired
    for source in sources:
        source.alignment.normalized_tokens = ["again"] * 4
        source.alignment.original_text = "again again again again"
        source.alignment.token_offsets = [(0, 5), (6, 11), (12, 17), (18, 23)]
        for word in source.alignment.words:
            word.label = "again"
    assert matching_reason(sources) is None
    sources[1].alignment.words.pop(1)
    assert matching_reason(sources)


def test_unknown_local_support_does_not_become_quiet(paired):
    _, _, sources = paired
    f = sources[0].features
    measurements = local_measurements(f, 1.99, 2)
    assert not measurements.complete and measurements.observed_s < 0.01
    empty = f.model_copy(deep=True)
    for name in ("energy", "activity"):
        empty.series[name].start_samples = []
        empty.series[name].values = []
    assert local_measurements(empty, 0, 1).low_energy_s is None


def test_immutable_storage_checksum_and_source_rejection(paired):
    root, report, sources = paired
    result = build(report, sources, implementation_hash())
    path = publish(root, result)
    assert publish(root, result) == path and read_artifact(path) == result
    envelope = json.loads(path.read_text())
    envelope["result"]["activity_delta_s"] = 100
    path.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="checksum"):
        read_artifact(path)
    with pytest.raises(ValueError, match="preserved"):
        publish(root, result)
    sources[0].feature_ref = sources[0].feature_ref.model_copy(update={"sha256": "0" * 64})
    with pytest.raises(ValueError, match="identity"):
        build(report, sources, implementation_hash())


def test_alignment_gap_has_separate_signal_evidence_and_deterministic_priority(paired):
    _, report, sources = paired
    b = sources[1]
    for word, (start, end) in zip(
        b.alignment.words, [(0.12, 0.32), (1.4, 1.5), (1.6, 1.7), (1.8, 1.9)], strict=True
    ):
        word.start_s = start
        word.end_s = end
    b.alignment_ref = b.alignment_ref.model_copy(
        update={"sha256": content_hash(b.alignment.model_dump(mode="json"))}
    )
    b.features.alignment_sha256 = b.alignment_ref.sha256
    b.feature_ref = b.feature_ref.model_copy(
        update={"sha256": content_hash(b.features.model_dump(mode="json"))}
    )
    report = report.model_copy(
        update={
            "recordings": [summarize(s, ExploratoryConfig())[0] for s in sources],
            "candidates": [],
        }
    )
    result = build(report, sources, implementation_hash())
    assert len(result.anomalies) == 1
    a = result.anomalies[0]
    assert a.gap.start_s == 0.32 and a.gap.end_s == 1.4
    assert a.measurement.low_energy_s < a.measurement.observed_s
    assert a.alignment_confidence is None and "not proof" in a.reason
    assert result.inspection_order[0].category == "alignment_anomaly"
    assert result == build(report, sources, implementation_hash())
    # A warning limits its ordering even when its measured gap is larger.
    report.recordings[1].quality_flags = ["fixture_noise_warning"]
    limited = build(report, sources, implementation_hash())
    assert all(i.quality_limited for i in limited.inspection_order)
    assert all("not severity" in i.order_reason for i in limited.inspection_order)


def test_large_quality_limited_change_does_not_outrank_complete_group(paired):
    _, report, sources = paired
    report = windows(report, [(0, 0.5, "energy_change", 6), (0, 2, "energy_change", 100)])
    report.candidates[1] = report.candidates[1].model_copy(
        update={
            "recording_id": sources[1].recording.id,
            "feature_sha256": sources[1].feature_ref.sha256,
        }
    )
    report.recordings[1].quality_flags = ["fixture_noise_warning"]
    result = build(report, sources, implementation_hash())
    assert result.inspection_order[0].quality_limited is False
    assert result.inspection_order[-1].quality_limited is True
    assert result.groups[0].representative_delta_db == 100
    assert result.inspection_order[0].evidence_id != result.groups[0].id
