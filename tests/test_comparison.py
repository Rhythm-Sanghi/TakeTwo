"""Analytic feature/reviewer fixtures ONLY; no claims about real human speech or review."""

import copy
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

from taketwo.analysis.contracts import (
    AlignmentConfig,
    AlignmentResult,
    FeatureConfig,
    FeatureResult,
    Interval,
    Provenance,
    QualityReport,
    Resource,
    Series,
)
from taketwo.analysis.features import extract
from taketwo.analysis.storage import publish as publish_analysis
from taketwo.analysis.storage import recording_input
from taketwo.comparison.cli import main, schema
from taketwo.comparison.contracts import (
    ArtifactRef,
    EvaluationConfig,
    Label,
    Policy,
    Review,
    Span,
)
from taketwo.comparison.engine import Evidence, compare, frame_values
from taketwo.comparison.evaluation import evaluate, iou, match_regions, metrics
from taketwo.comparison.reviews import active_reviews, consensus, validate_review
from taketwo.comparison.storage import implementation_hash, publish, read_artifact, reproduce
from taketwo.dataset.audio import sha256
from taketwo.dataset.schema import (
    Dataset,
    ImportSpec,
    Pair,
    Recipe,
    Transformation,
    canonical_json,
    content_hash,
    tokenize,
)
from taketwo.dataset.splits import connected_groups, make_split
from taketwo.dataset.storage import load
from taketwo.dataset.workspace import import_recording, initialize

HASH = "0" * 64


def typed(contract, payload):
    return contract.model_validate_json(canonical_json(payload))


def analytic_evidence(recording, factor=1.0, pause_s=0.1):
    """Known frame arrays isolate Phase 3 math; Phase 2 independently tests signal physics."""
    text = "One two three. Four five six."
    tokens, offsets = tokenize(text)
    duration = 4.0 * factor + pause_s
    count = round(duration * 16000)
    duration = count / 16000
    transcript = recording.transcript.model_copy(
        update={
            "text": text,
            "status": "verified",
            "reviewers": ["fixture-a", "fixture-b"],
            "verification_date": "2026-10-11",
        }
    )
    provenance = recording.provenance.model_copy(deep=True)
    provenance.rights.status = "cleared"
    provenance.rights.permits_adaptation = True
    provenance.rights.permits_redistribution = True
    provenance.consent_evidence = "software-fixture-only"
    info = recording.normalized_info.model_copy(update={"frames": count, "duration_s": duration})
    recording = recording.model_copy(
        update={
            "transcript": transcript,
            "tokens": tokens,
            "token_offsets": offsets,
            "transcript_sha256": content_hash(tokens),
            "provenance": provenance,
            "normalized_info": info,
        }
    )
    p = Provenance(
        recording_id=recording.id,
        dataset_version=recording.dataset_version,
        audio_sha256=recording.normalized_sha256,
        sample_sha256=recording.sample_sha256,
        transcript_sha256=recording.transcript_sha256,
        original_text_sha256=sha256(text.encode()),
        transcript_verified=True,
        versions={"test": "analytic-fixture"},
        implementation_sha256=HASH,
    )
    resource = Resource(
        path="fixture",
        sha256=HASH,
        version="fixture",
        license="fixture",
        source_url="https://example.invalid",
    )
    config = AlignmentConfig(
        command=["fixture"], expected_version="fixture", model=resource, dictionary=resource
    )
    words = []
    for i, token in enumerate(tokens):
        start = (0.2 + i * 0.6) * factor + (pause_s - 0.1 if i >= 3 else 0)
        words.append(
            Interval(start_s=start, end_s=start + 0.5 * factor, label=token, token_index=i)
        )
    alignment = AlignmentResult(
        provenance=p,
        config=config,
        duration_s=duration,
        original_text=text,
        normalized_tokens=tokens,
        token_offsets=offsets,
        status="succeeded",
        words=words,
    )
    series = {}
    names = {
        "rms": ("full_scale", 0.1),
        "energy": ("dBFS", -20.0),
        "relative_energy": ("dB", 0.0),
        "spectral_power": ("full_scale_squared", 0.01),
        "spectral_centroid": ("Hz", 220.0),
        "activity": ("binary_energy_estimate", 1.0),
        "f0": ("Hz", 220.0),
        "relative_pitch": ("semitones", 0.0),
        "voicing_probability": ("pYIN_model_probability", 0.99),
        "voiced": ("binary", 1.0),
    }
    for name, (unit, value) in names.items():
        length = 1024 if name in {"f0", "relative_pitch", "voicing_probability", "voiced"} else 400
        starts = list(range(0, count - length + 1, 160))
        vals = [value] * len(starts)
        if name == "activity":
            vals = [
                float(any(w.start_s <= (s + 200) / 16000 <= w.end_s for w in words)) for s in starts
            ]
        series[name] = Series(
            unit=unit,
            frame_length=length,
            hop_length=160,
            start_samples=starts,
            times_s=[(s + length / 2) / 16000 for s in starts],
            values=vals,
        )
    n = len(series["rms"].values)
    f = FeatureResult(
        provenance=p,
        config=FeatureConfig(),
        quality=QualityReport(
            sample_count=count,
            duration_s=duration,
            mean=0.0,
            rms=0.1,
            peak=0.2,
            clipping_fraction=0.0,
            flags=[],
            spectral_covered_until_s=(series["rms"].start_samples[-1] + 400) / 16000,
            pitch_covered_until_s=(series["f0"].start_samples[-1] + 1024) / 16000,
        ),
        series=series,
        frequencies_hz=np.fft.rfftfreq(512, 1 / 16000).tolist(),
        spectrum_power=[[0.0] * 257 for _ in range(n)],
        mfcc=[[0.0] * 13 for _ in range(n)],
        waveform=[(i, min(count, i + 160), -0.2, 0.2) for i in range(0, count, 160)],
        activity=[],
        low_energy=[],
        voiced_regions=[],
        unvoiced_regions=[],
        pauses=[],
        alignment_sha256=content_hash(alignment.model_dump(mode="json")),
        speaking_rate_wpm=100.0,
        articulation_rate_wpm=100.0,
        rate_unavailable_reason=None,
        energy_baseline_dbfs=-20.0,
        pitch_baseline_hz=220.0,
        energy_range_db=0.0,
        pitch_range_semitones=0.0,
        diagnostics=[],
    )
    reviews = [
        Review(
            id=f"timing-{recording.id}-{reviewer}",
            scope="timing",
            provenance=p,
            alignment_sha256=f.alignment_sha256,
            reviewer_id=f"fixture-{reviewer}",
            reviewed_on="2026-10-11",
            evidence_reference="analytic fixture; never a human review",
            independent=True,
            blinded_to_predictions=True,
            decision="approved",
            notes="test-only",
            words=words,
            phrase_spans=[(0, 3), (3, 6)],
        )
        for reviewer in ("a", "b")
    ]
    return Evidence(
        recording,
        f,
        ArtifactRef(path="fixture-features.json", sha256=content_hash(f.model_dump(mode="json"))),
        alignment,
        ArtifactRef(path="fixture-alignment.json", sha256=f.alignment_sha256),
        reviews,
        [
            ArtifactRef(
                path=f"{review.id}.json", sha256=content_hash(review.model_dump(mode="json"))
            )
            for review in reviews
        ],
    )


@pytest.fixture
def pair_evidence(imported):
    _, r = imported
    reference = analytic_evidence(r.model_copy(update={"id": "reference"}))
    participant = analytic_evidence(
        r.model_copy(update={"id": "participant", "role": "participant", "origin": "self_recorded"})
    )
    pair = Pair(
        id="pair",
        reference_id="reference",
        participant_id="participant",
        transcript_sha256=reference.recording.transcript_sha256,
        intended_flaw="acceptable",
        intended_severity=0,
        identity_status="verified",
    )
    return reference, participant, pair


def run_pair(inputs, policy=None):
    reference, participant, pair = inputs
    for member in (reference, participant):
        member.feature_ref.sha256 = content_hash(member.features.model_dump(mode="json"))
        if member.alignment:
            member.alignment_ref.sha256 = content_hash(member.alignment.model_dump(mode="json"))
        member.review_refs = [
            ArtifactRef(path=f"{r.id}.json", sha256=content_hash(r.model_dump(mode="json")))
            for r in member.reviews
        ]
    return compare(reference, participant, pair, policy or Policy(), HASH, implementation_hash())


def dimension(report, name):
    return next(d for d in report.dimensions if d.dimension == name)


def alter_contour(evidence, name, fn):
    series = evidence.features.series[name]
    series.values = [float(fn(t)) for t in series.times_s]


def test_identical_agreement_and_determinism(pair_evidence):
    report = run_pair(pair_evidence)
    assert report.overall_score == 100.0
    assert not report.regions
    assert all(d.coverage == 1 for d in report.dimensions)
    assert report == run_pair(pair_evidence)
    assert report.eligibility.state == "ELIGIBLE"


@pytest.mark.parametrize("factor", [0.75, 1.25, 1.5])
def test_tempo_native_time_and_hand_score(pair_evidence, factor):
    reference, participant, pair = pair_evidence
    participant = analytic_evidence(participant.recording, factor=factor)
    report = run_pair((reference, participant, pair))
    expected_delta = math.log(1 / factor)
    expected_penalty = min(1, max(0, abs(expected_delta) - math.log(1.15)) / math.log(1.5))
    assert dimension(report, "pacing").score == pytest.approx(100 * (1 - expected_penalty))
    obs = [o for o in report.observations if o.dimension == "pacing"]
    assert obs[0].delta == pytest.approx(expected_delta)
    assert obs[0].reference_interval.start_s == 0.2
    assert obs[0].participant_interval.start_s == pytest.approx(0.2 * factor)
    assert all(
        0
        <= r.participant_interval.start_s
        < r.participant_interval.end_s
        <= participant.features.quality.duration_s
        for r in report.regions
        if r.participant_interval
    )


@pytest.mark.parametrize("reference_pause,participant_pause", [(0.3, 0.8), (0.8, 0.3), (0.8, 0.1)])
def test_pause_duration_missing_boundary_and_math(
    pair_evidence, reference_pause, participant_pause
):
    r, p, pair = pair_evidence
    r, p = (
        analytic_evidence(r.recording, pause_s=reference_pause),
        analytic_evidence(p.recording, pause_s=participant_pause),
    )
    report = run_pair((r, p, pair))
    obs = next(
        o for o in report.observations if o.dimension == "pause_behavior" and o.token_span == (2, 4)
    )
    # Sub-150 ms gaps map to zero; longer gaps retain native duration.
    ref = reference_pause if reference_pause >= 0.15 else 0
    part = participant_pause if participant_pause >= 0.15 else 0
    assert obs.reference == pytest.approx(ref)
    assert obs.participant == pytest.approx(part)
    assert obs.delta == pytest.approx(part - ref)
    expected = min(1, max(0, abs(part - ref) - max(0.15, 0.25 * ref)) / 0.75)
    assert dimension(report, "pause_behavior").score == pytest.approx(100 * (1 - expected / 5))
    region = next(r for r in report.regions if r.category == "pause_behavior")
    if part < ref:
        assert region.participant_interval is None and region.participant_anchor_s is not None
    else:
        assert (
            region.participant_interval.end_s - region.participant_interval.start_s
            == pytest.approx(part)
        )
    assert "signed delta" in region.explanation.technical
    assert region.confidence is None


def test_energy_range_sustained_step_no_double_penalty(pair_evidence):
    r, p, _ = pair_evidence
    alter_contour(r, "relative_energy", lambda t: -4 if t < 1.9 else 4)
    alter_contour(p, "relative_energy", lambda t: 4 if t < 1.9 else -4)
    report = run_pair(pair_evidence)
    assert dimension(report, "energy_variation").score == 100
    detectors = {
        region.detector for region in report.regions if region.category == "energy_variation"
    }
    assert {"sustained_energy", "energy_step"} <= detectors
    assert all(not o.scored for o in report.observations if o.detector != "rubric")


def test_range_penalties_and_pitch_contour(pair_evidence):
    r, p, _ = pair_evidence
    alter_contour(r, "relative_energy", lambda t: 0)
    alter_contour(p, "relative_energy", lambda t: -5 if int(t * 10) % 2 else 5)
    alter_contour(p, "relative_pitch", lambda t: -4 if t < 1.9 else 4)
    report = run_pair(pair_evidence)
    assert dimension(report, "energy_variation").score == 0.0  # excursion 10; excess 7, saturated
    assert any(r.detector == "pitch_contour" for r in report.regions)
    assert all(
        o.unit == "semitones" for o in report.observations if o.dimension == "pitch_dynamics"
    )


@pytest.mark.parametrize(
    "failure",
    ["pitch", "probability", "timing", "transcript", "alignment", "rights", "pair", "clipping"],
)
def test_feature_specific_abstention(pair_evidence, failure):
    r, p, pair = pair_evidence
    if failure == "pitch":
        p.features.pitch_baseline_hz = None
        p.features.series["relative_pitch"].values = [None] * len(
            p.features.series["relative_pitch"].values
        )
    elif failure == "probability":
        p.features.series["voicing_probability"].values = [0.1] * len(
            p.features.series["voicing_probability"].values
        )
    elif failure == "timing":
        p.reviews = []
    elif failure == "transcript":
        p.recording.transcript = p.recording.transcript.model_copy(
            update={"status": "unverified", "reviewers": [], "verification_date": None}
        )
        prov = p.features.provenance.model_copy(update={"transcript_verified": False})
        p.features.provenance = p.alignment.provenance = prov
        p.features.speaking_rate_wpm = None
        p.features.alignment_sha256 = content_hash(p.alignment.model_dump(mode="json"))
        p.reviews = []
    elif failure == "alignment":
        p.alignment = None
        p.reviews = []
    elif failure == "rights":
        p.recording.provenance.rights.status = "pending"
    elif failure == "pair":
        pair.reference_id = "wrong-reference"
    else:
        p.features.waveform = [(a, b, -1.0, 1.0) for a, b, _, _ in p.features.waveform]
    report = run_pair(pair_evidence)
    assert report.overall_score is None
    assert report.abstention_reasons
    if failure in {"pitch", "probability"}:
        assert dimension(report, "pacing").score == 100.0
        assert dimension(report, "pause_behavior").score == 100.0
        assert dimension(report, "pitch_dynamics").score is None


def test_timestamp_units_and_integrity_rejection(pair_evidence):
    p = pair_evidence[1]
    p.features.series["relative_pitch"].unit = "Hz"
    with pytest.raises(ValueError, match="units"):
        run_pair(pair_evidence)
    p.features.series["relative_pitch"].unit = "semitones"
    p.features.series["f0"].times_s[0] = 0.0125  # FFT clock is incorrect for F0
    with pytest.raises(ValueError, match="coordinates"):
        run_pair(pair_evidence)


def test_frame_coverage_no_index_join(pair_evidence):
    features = pair_evidence[0].features
    values, coverage, fraction = frame_values(
        features, Span(start_s=0.2, end_s=0.7), "relative_pitch"
    )
    assert len(values) == 44
    assert coverage == pytest.approx(0.988)
    assert fraction == 1
    _, tiny_coverage, _ = frame_values(features, Span(start_s=0.2, end_s=0.21), "relative_pitch")
    assert tiny_coverage == 0


def test_review_disagreement_history_and_corrections(pair_evidence):
    evidence = pair_evidence[0]
    evidence.reviews[1].words = copy.deepcopy(evidence.reviews[1].words)
    evidence.reviews[1].words[0].start_s += 0.25
    assert consensus(evidence.reviews, "timing")[1]
    evidence.reviews[1].decision = "unresolved"
    assert consensus(evidence.reviews, "timing")[1]
    correction = evidence.reviews[1].model_copy(
        deep=True, update={"id": "replacement", "supersedes": evidence.reviews[1].id}
    )
    correction.words = copy.deepcopy(evidence.reviews[0].words)
    correction.decision = "approved"
    selected = evidence.reviews + [correction]
    assert consensus(selected, "timing")[1] is None
    assert len(active_reviews(selected)) == 2
    correction.supersedes = "nonexistent"
    with pytest.raises(ValueError, match="Superseded"):
        active_reviews(selected)
    transcript = evidence.reviews[0].model_copy(
        update={
            "scope": "transcript",
            "alignment_sha256": None,
            "words": [],
            "phrase_spans": [],
            "corrected_text": "Different checked words.",
        }
    )
    validate_review(transcript, evidence.recording, None)
    assert (
        transcript.corrected_text != evidence.recording.transcript.text
    )  # proposal retained; no mutation


@pytest.mark.parametrize(
    "field,value", [("energy_tolerance_db", 4.0), ("weights", {"pacing": 1.0}), ("frozen", True)]
)
def test_policy_invalidation(field, value):
    with pytest.raises(ValidationError):
        typed(Policy, Policy().model_dump(mode="json") | {field: value})


def test_configuration_changes_identity(pair_evidence):
    a = run_pair(pair_evidence)
    policy = Policy(version="delivery-v1-test", energy_tolerance_db=4.0)
    b = run_pair(pair_evidence, policy)
    assert a.policy_sha256 != b.policy_sha256
    assert a.observations[0].id != b.observations[0].id


def test_label_unsupported_bounds():
    base = dict(
        id="label",
        category="pacing",
        severity=1,
        interval={"start_s": 0.0, "end_s": 1.0},
        rationale="fixture",
    )
    for update in (
        {"category": "emotion"},
        {"interval": {"start_s": 1.0, "end_s": 1.0}},
        {"severity": 0},
    ):
        with pytest.raises(ValidationError):
            typed(Label, base | update)


def predicted_region(pair_evidence):
    r, p, pair = pair_evidence
    p = analytic_evidence(p.recording, factor=1.5)
    return run_pair((r, p, pair)).regions[0]


def test_iou_one_to_one_and_stable_ties(pair_evidence):
    p = predicted_region(pair_evidence)
    p.category = "pacing"
    p.participant_interval = Span(start_s=1.0, end_s=3.0)
    duplicate = p.model_copy(update={"id": "duplicate"})
    label = Label(
        id="truth",
        category="pacing",
        severity=1,
        interval=Span(start_s=2.0, end_s=4.0),
        rationale="fixture",
    )
    assert iou(p.participant_interval, label.interval) == pytest.approx(1 / 3)
    matches, fp, fn = match_regions([p, duplicate], [label], EvaluationConfig(iou_threshold=0.3))
    assert len(matches) == 1 and len(fp) == 1 and not fn
    result = metrics([p, duplicate], [label], matches)
    assert result.precision == 0.5 and result.recall == 1 and result.f1 == pytest.approx(2 / 3)
    assert result.median_boundary_error_s == 1
    assert match_regions([duplicate, p], [label], EvaluationConfig(iou_threshold=0.3)) == (
        matches,
        fp,
        fn,
    )
    assert len(match_regions([p], [label], EvaluationConfig(iou_threshold=0.7))[2]) == 1


def test_boundary_events_and_undefined_metrics(pair_evidence):
    p = predicted_region(pair_evidence)
    p.category, p.participant_interval, p.participant_anchor_s = "pause_behavior", None, 2.0
    label = Label(
        id="truth",
        category="pause_behavior",
        severity=1,
        interval=None,
        anchor_s=2.1,
        rationale="fixture",
    )
    matches, fp, fn = match_regions([p], [label], EvaluationConfig())
    assert len(matches) == 1 and matches[0].iou is None and matches[0].end_error_s is None
    assert metrics([], [], []).f1 is None
    assert metrics([], [label], []).recall == 0 and metrics([], [label], []).precision is None


def eval_inputs(pair_evidence):
    r, p, pair = pair_evidence
    dataset = Dataset(
        dataset_version=r.recording.dataset_version,
        recordings=[r.recording, p.recording],
        pairs=[pair],
    )
    report = compare(
        r, p, pair, Policy(), content_hash(dataset.model_dump(mode="json")), implementation_hash()
    )
    reviews = [
        Review(
            id=f"flaws-{reviewer}",
            scope="flaws",
            pair_id=pair.id,
            provenance=p.features.provenance,
            reviewer_id=f"test-{reviewer}",
            reviewed_on="2026-10-11",
            evidence_reference="software fixture only",
            independent=True,
            blinded_to_predictions=True,
            decision="approved",
            notes="fixture",
            labels=[],
            reviewed_spans=[Span(start_s=0.0, end_s=p.features.quality.duration_s)],
        )
        for reviewer in ("a", "b")
    ]
    return dataset, report, reviews


def test_evaluation_gates_and_fixture_origin(pair_evidence):
    dataset, report, reviews = eval_inputs(pair_evidence)
    cfg = EvaluationConfig(mode="software_fixture")
    missing = evaluate(dataset, [report], [], cfg, HASH)
    assert missing.metrics is None and not missing.independent_real_validation
    result = evaluate(dataset, [report], reviews, cfg, HASH)
    assert result.metrics.false_positive == 0 and result.metrics.f1 is None
    assert result.uncertainty["f1"]["undefined_resamples"] == 1000
    assert not result.independent_real_validation
    assert result == evaluate(dataset, [report], reviews, cfg, HASH)
    reviews[1].decision = "unresolved"
    assert evaluate(dataset, [report], reviews, cfg, HASH).metrics is None


def test_split_leakage_and_frozen_policy_gate(pair_evidence):
    dataset, report, reviews = eval_inputs(pair_evidence)
    dataset.split = make_split(dataset, 17, (0.0, 0.0, 1.0))
    report.dataset_sha256 = content_hash(dataset.model_dump(mode="json"))
    result = evaluate(dataset, [report], reviews, EvaluationConfig(mode="held_out"), HASH)
    assert result.metrics is None
    dataset.split.assignments["reference"] = "train"
    with pytest.raises(ValueError, match="leakage"):
        evaluate(dataset, [report], reviews, EvaluationConfig(), HASH)
    dataset.split = make_split(dataset, 17, (0.0, 0.0, 1.0))
    report.dataset_sha256 = content_hash(dataset.model_dump(mode="json"))
    report.policy.calibration_group_ids = list(connected_groups(dataset))
    with pytest.raises(ValueError, match="leaks"):
        evaluate(dataset, [report], reviews, EvaluationConfig(), HASH)


def test_annotations_cannot_drive_predictions(pair_evidence):
    dataset, report, reviews = eval_inputs(pair_evidence)
    before = run_pair(pair_evidence)
    # Detector signature never accepts annotations, transformation windows or intended severity.
    dataset.pairs[0].intended_flaw = "pacing"
    dataset.pairs[0].intended_severity = 3
    after = run_pair(pair_evidence)
    assert before.observations == after.observations and before.regions == after.regions


def test_new_artifact_hash_tamper_schema_and_old_contract(imported, pair_evidence, tmp_path):
    root, _ = imported
    report = run_pair(pair_evidence)
    path = publish(root, report)
    assert read_artifact(path) == report and publish(root, report) == path
    envelope = json.loads(path.read_text())
    envelope["result"]["overall_score"] = 17.0
    path.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="hash"):
        read_artifact(path)
    checked_schema = schema()
    assert {"Report", "Review", "Evaluation"} <= set(checked_schema["$defs"])


def test_real_cli_paths_on_generated_signal(imported, tmp_path, capsys):
    root, recording = imported
    _, samples, provenance = recording_input(root, recording.id)
    features = extract(samples, provenance, FeatureConfig())
    phase2_path = publish_analysis(root, features)
    args = [str(root), "--reference-features", str(phase2_path)]
    for command in ("compare", "detect", "score", "evidence"):
        assert main([command, *args]) == 3
        payload = json.loads(capsys.readouterr().out)
        assert payload["overall_score"] is None
    report_path = payload["artifact"]
    assert main(["validate", str(root), "--artifact", report_path, "--reproduce"]) == 0
    capsys.readouterr()
    report = read_artifact(Path(report_path))
    report.implementation_sha256 = HASH
    with pytest.raises(ValueError, match="implementation"):
        reproduce(root, load(root), report)
    assert main(["inspect", str(root), "--artifact", report_path]) == 0
    capsys.readouterr()
    exported = tmp_path / "export.json"
    assert main(["export", str(root), "--artifact", report_path, "--output", str(exported)]) == 0
    capsys.readouterr()
    assert main(["export", str(root), "--artifact", report_path, "--output", str(exported)]) == 2
    capsys.readouterr()
    assert main(["evaluate", str(root)]) == 3
    capsys.readouterr()
    assert (
        main(["compare", *args, "--pair", "unknown", "--participant-features", str(phase2_path)])
        == 2
    )
    capsys.readouterr()
    result = subprocess.run(
        [sys.executable, "-m", "taketwo.comparison.cli", "schema"], capture_output=True, text=True
    )
    assert result.returncode == 0 and json.loads(result.stdout) == schema()


def test_review_cli_transcript_traceability(imported, tmp_path, capsys):
    root, recording = imported
    _, _, provenance = recording_input(root, recording.id)
    review = Review(
        id="fixture-review",
        scope="transcript",
        provenance=provenance,
        reviewer_id="fixture-human-assertion",
        reviewed_on="2026-10-11",
        evidence_reference="test-only",
        independent=False,
        blinded_to_predictions=False,
        decision="unresolved",
        notes="test-only",
        corrected_text="Proposed correction, not a verified transcript.",
    )
    path = tmp_path / "review.json"
    path.write_text(canonical_json(review.model_dump(mode="json")))
    before = (root / "manifest.jsonl").read_bytes()
    assert main(["import-review", str(root), "--review", str(path)]) == 0
    assert "does not certify" in capsys.readouterr().out
    assert (root / "manifest.jsonl").read_bytes() == before


def test_eligible_cli_review_compare_evaluate_replay(metadata, audio_path, tmp_path, capsys):
    """End-to-end CLI software fixture. Reviewer assertions are deliberately test-only."""
    import soundfile as sf

    metadata = copy.deepcopy(metadata)
    metadata["transcript"].update(
        text="One two three. Four five six.",
        status="verified",
        reviewers=["fixture-a", "fixture-b"],
        verification_date="2026-10-11",
    )
    metadata["provenance"]["rights"].update(
        status="cleared", permits_adaptation=True, permits_redistribution=True
    )
    root = tmp_path / "eligible-fixture"
    initialize(root, "fixture-v1")
    reference = import_recording(root, audio_path, typed(ImportSpec, metadata))
    metadata["origin"] = "self_recorded"
    metadata["speaker_id"] = "fixture-mirror"
    metadata["provenance"]["consent_evidence"] = "test-only assertion; no actual human recording"
    samples, fs = sf.read(audio_path, dtype="float32")
    mirror_path = tmp_path / "mirror.wav"
    sf.write(mirror_path, samples * 0.7, fs, subtype="FLOAT")
    participant = import_recording(
        root, mirror_path, typed(ImportSpec, metadata), reference_id=reference.id
    )
    paths, review_paths = [], []
    for recording in (reference, participant):
        _, x, provenance = recording_input(root, recording.id)
        analytic = analytic_evidence(recording)
        words = [
            Interval(start_s=0.05 + i * 0.3, end_s=0.3 + i * 0.3, label=token, token_index=i)
            for i, token in enumerate(recording.tokens)
        ]
        alignment = analytic.alignment.model_copy(
            update={"provenance": provenance, "duration_s": len(x) / 16000, "words": words}
        )
        alignment_path = publish_analysis(root, alignment)
        features = extract(x, provenance, FeatureConfig(), alignment)
        feature_path = publish_analysis(root, features)
        paths.append((feature_path, alignment_path))
        for reviewer in ("a", "b"):
            review = Review(
                id=f"fixture-{recording.id}-{reviewer}",
                scope="timing",
                provenance=provenance,
                alignment_sha256=content_hash(alignment.model_dump(mode="json")),
                reviewer_id=f"fixture-{reviewer}",
                reviewed_on="2026-10-11",
                evidence_reference="pytest generated signal",
                independent=True,
                blinded_to_predictions=True,
                decision="approved",
                notes="No human review claimed",
                words=words,
                phrase_spans=[(0, 3), (3, 6)],
            )
            review_path = tmp_path / f"{review.id}.json"
            review_path.write_text(canonical_json(review.model_dump(mode="json")))
            assert (
                main(
                    [
                        "import-review",
                        str(root),
                        "--review",
                        str(review_path),
                        "--alignment",
                        str(alignment_path),
                    ]
                )
                == 0
            )
            review_paths.append(json.loads(capsys.readouterr().out)["artifact"])
    dataset = load(root)
    args = [
        str(root),
        "--reference-features",
        str(paths[0][0]),
        "--reference-alignment",
        str(paths[0][1]),
        "--participant-features",
        str(paths[1][0]),
        "--participant-alignment",
        str(paths[1][1]),
        "--pair",
        dataset.pairs[0].id,
    ]
    for path in review_paths:
        args.extend(["--review", path])
    assert main(["score", *args]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["overall_score"] == 100.0
    assert main(["validate", str(root), "--artifact", payload["artifact"], "--reproduce"]) == 0
    capsys.readouterr()
    flaws = []
    for reviewer in ("a", "b"):
        review = Review(
            id=f"fixture-flaw-{reviewer}",
            scope="flaws",
            pair_id=dataset.pairs[0].id,
            provenance=features.provenance,
            reviewer_id=f"fixture-{reviewer}",
            reviewed_on="2026-10-11",
            evidence_reference="fixture only",
            independent=True,
            blinded_to_predictions=True,
            decision="approved",
            notes="No actual human review",
            labels=[],
            reviewed_spans=[Span(start_s=0.0, end_s=2.0)],
        )
        flaws.append(publish(root, review))
    cfg = tmp_path / "evaluation-config.json"
    cfg.write_text(
        canonical_json(EvaluationConfig(mode="software_fixture").model_dump(mode="json"))
    )
    assert (
        main(
            [
                "evaluate",
                str(root),
                "--report",
                payload["artifact"],
                "--review",
                str(flaws[0]),
                "--review",
                str(flaws[1]),
                "--config",
                str(cfg),
            ]
        )
        == 0
    )
    evaluation = json.loads(capsys.readouterr().out)["evaluation"]
    assert evaluation["metrics"]["false_positive"] == 0
    assert evaluation["config"]["mode"] == "software_fixture"
    assert not evaluation["independent_real_validation"]


def test_pitch_range_score_and_coverage_weight_no_redistribution(pair_evidence):
    r, p, _ = pair_evidence
    alter_contour(p, "relative_pitch", lambda t: -3 if int(t * 10) % 2 else 3)
    report = run_pair(pair_evidence)
    assert dimension(report, "pitch_dynamics").score == 0.0  # (6-2)/4 saturates
    assert report.overall_score == 75.0
    # Withhold the second phrase's pitch rather than granting its missing weight a perfect score.
    p.features.series["relative_pitch"].values = [
        v if t < 1.9 else None
        for t, v in zip(
            p.features.series["relative_pitch"].times_s,
            p.features.series["relative_pitch"].values,
            strict=True,
        )
    ]
    report = run_pair(pair_evidence)
    assert dimension(report, "pitch_dynamics").coverage == pytest.approx(0.5)
    assert report.overall_score is None and dimension(report, "pacing").score == 100.0


def test_review_bounds_identity_and_blindness(pair_evidence):
    r, p, _ = pair_evidence
    review = copy.deepcopy(r.reviews[0])
    review.words[-1].end_s = 50.0
    with pytest.raises(ValueError, match="exceed"):
        validate_review(review, r.recording, r.alignment)
    review = copy.deepcopy(r.reviews[0])
    review.provenance.audio_sha256 = "f" * 64
    with pytest.raises(ValueError, match="identity"):
        validate_review(review, r.recording, r.alignment)
    dataset, report, reviews = eval_inputs(pair_evidence)
    reviews[0].blinded_to_predictions = False
    assert (
        evaluate(
            dataset, [report], reviews, EvaluationConfig(mode="software_fixture"), HASH
        ).metrics
        is None
    )


def test_evaluation_positive_counts_fp_fn_category_severity(pair_evidence):
    dataset, report, reviews = eval_inputs(pair_evidence)
    predicted = predicted_region(pair_evidence)
    predicted.participant_interval = Span(start_s=1.0, end_s=2.0)
    predicted.category = "pacing"
    predicted.severity = 2
    report.regions = [predicted, predicted.model_copy(update={"id": "duplicate"})]
    label = Label(
        id="positive",
        category="pacing",
        severity=1,
        interval=Span(start_s=1.0, end_s=2.0),
        rationale="test-only analytic matching",
    )
    for review in reviews:
        review.labels = [label]
    result = evaluate(dataset, [report], reviews, EvaluationConfig(mode="software_fixture"), HASH)
    assert result.metrics.precision == 0.5 and result.metrics.recall == 1.0
    assert result.metrics.f1 == pytest.approx(2 / 3)
    assert result.by_severity["1"].false_negative == 1
    assert result.by_severity["2"].false_positive == 2
    assert len(result.false_positive_ids) == 1 and not result.false_negative_ids
    assert result.metrics.median_boundary_error_s == 0
    assert result.clean_reviewed_duration_s == pytest.approx(3.1)
    assert result.false_flags_in_clean_spans == 0


def test_synthetic_origin_and_recipe_labels_are_not_predictions(pair_evidence):
    r, p, pair = pair_evidence
    # Deliberately incongruent metadata is a test of label isolation, not real generated speech.
    recipe = typed(
        Recipe,
        {
            "seed": 17,
            "operations": [
                {"kind": "gain", "start_s": 0.2, "end_s": 0.6, "value": 2.0, "severity": 3}
            ],
        },
    )
    p.recording.origin = "synthetic"
    p.recording.transformation = Transformation(
        parent_id=r.recording.id,
        source_sha256=r.recording.normalized_sha256,
        recipe=recipe,
        recipe_sha256=content_hash(recipe.model_dump(mode="json")),
        time_map=[],
        versions={"test": "fixture"},
    )
    pair.identity_status = "derived"
    pair.intended_flaw, pair.intended_severity = "energy_variation", 3
    report = run_pair(pair_evidence)
    assert report.overall_score == 100.0 and not report.regions
    dataset, report, reviews = eval_inputs(pair_evidence)
    result = evaluate(dataset, [report], reviews, EvaluationConfig(mode="software_fixture"), HASH)
    assert result.origin == "synthetic" and not result.independent_real_validation
    assert (
        evaluate(dataset, [report], [], EvaluationConfig(mode="software_fixture"), HASH).metrics
        is None
    )


def test_flaw_reviews_rejected_by_detector(pair_evidence):
    _, _, reviews = eval_inputs(pair_evidence)
    pair_evidence[1].reviews.extend(reviews)
    with pytest.raises(ValueError, match="evaluation only"):
        run_pair(pair_evidence)


def test_wrong_reference_hash_rejected(pair_evidence):
    r, p, pair = pair_evidence
    p.feature_ref.sha256 = "f" * 64
    with pytest.raises(ValueError, match="reference hash"):
        compare(r, p, pair, Policy(), HASH, implementation_hash())


def test_checked_in_comparison_schema():
    path = Path(__file__).resolve().parents[1] / "docs/comparison-schema-v1.json"
    assert json.loads(path.read_text(encoding="utf-8")) == schema()


def test_threshold_equality_does_not_flag_roundoff(pair_evidence):
    r, p, pair = pair_evidence
    p = analytic_evidence(p.recording, factor=1.15)
    report = run_pair((r, p, pair))
    assert dimension(report, "pacing").score == 100.0
    assert not any(region.category == "pacing" for region in report.regions)


def test_semantic_flaws_distinct_ids_and_coverage_segments(pair_evidence):
    dataset, _, reviews = eval_inputs(pair_evidence)
    recording = next(r for r in dataset.recordings if r.id == reviews[0].provenance.recording_id)
    duration = recording.normalized_info.duration_s
    reviews[0].labels = [
        Label(
            id="independent-a",
            category="pacing",
            severity=1,
            interval=Span(start_s=0.1, end_s=0.9),
            rationale="Listener A: pacing deviation",
        )
    ]
    reviews[1].labels = [
        reviews[0]
        .labels[0]
        .model_copy(
            update={
                "id": "independent-b",
                "rationale": "Listener B: independently heard pacing",
                "interval": Span(start_s=0.15, end_s=0.95),
            }
        )
    ]
    reviews[1].reviewed_spans = [Span(start_s=0.0, end_s=1.0), Span(start_s=1.0, end_s=duration)]
    for review in reviews:
        validate_review(review, recording, None)
    accepted, reason = consensus(reviews, "flaws")
    assert reason is None and len(accepted) == 2
    assert reviews[0].labels[0].id == "independent-a"
    assert reviews[1].labels[0].id == "independent-b"
    assert consensus(list(reversed(reviews)), "flaws") == (accepted, None)


def test_maximum_cardinality_beats_highest_overlap(pair_evidence):
    base = predicted_region(pair_evidence)
    predictions = [
        base.model_copy(
            update={
                "id": "p1",
                "category": "pacing",
                "participant_interval": Span(start_s=0.0, end_s=3.0),
            }
        ),
        base.model_copy(
            update={
                "id": "p2",
                "category": "pacing",
                "participant_interval": Span(start_s=0.0, end_s=1.5),
            }
        ),
    ]
    labels = [
        Label(
            id="a",
            category="pacing",
            severity=1,
            interval=Span(start_s=0.0, end_s=2.5),
            rationale="software fixture",
        ),
        Label(
            id="b",
            category="pacing",
            severity=1,
            interval=Span(start_s=1.0, end_s=3.0),
            rationale="software fixture",
        ),
    ]
    matches, fp, fn = match_regions(predictions, labels, EvaluationConfig())
    assert {(m.prediction_id, m.label_id) for m in matches} == {("p1", "b"), ("p2", "a")}
    assert not fp and not fn
    assert metrics(predictions, labels, matches).f1 == 1


@pytest.mark.parametrize(
    "difference",
    [
        "time",
        "category",
        "severity",
        "omitted",
        "short",
        "gap",
        "uncertainty",
        "identity",
        "reviewer",
    ],
)
def test_semantic_consensus_rejects_substantive_disagreement(pair_evidence, difference):
    dataset, _, reviews = eval_inputs(pair_evidence)
    reviews[0].labels = [
        Label(
            id="a",
            category="pacing",
            severity=1,
            interval=Span(start_s=0.1, end_s=0.9),
            rationale="Fixture listener A",
        )
    ]
    reviews[1].labels = [reviews[0].labels[0].model_copy(update={"id": "b"})]
    label = reviews[1].labels[0]
    if difference == "time":
        label.interval = Span(start_s=0.4, end_s=1.2)
    elif difference == "category":
        label.category = "energy_variation"
    elif difference == "severity":
        label.severity = 2
    elif difference == "omitted":
        reviews[1].labels = []
    elif difference == "short":
        reviews[0].labels[0].interval = Span(start_s=0.1, end_s=0.2)
        label.interval = Span(start_s=0.19, end_s=0.29)
    elif difference == "gap":
        reviews[1].reviewed_spans = [Span(start_s=0.1, end_s=reviews[1].reviewed_spans[-1].end_s)]
    elif difference == "uncertainty":
        label.uncertainty_s = 0.1
    elif difference == "identity":
        reviews[1].pair_id = "another-pair"
    else:
        reviews[1].reviewer_id = reviews[0].reviewer_id
    accepted, reason = consensus(reviews, "flaws")
    assert not accepted and reason


def test_semantic_consensus_multiple_reviewers_and_supersession(pair_evidence):
    _, _, reviews = eval_inputs(pair_evidence)
    reviews[0].labels = [
        Label(
            id="a",
            category="pacing",
            severity=1,
            interval=Span(start_s=0.1, end_s=0.9),
            rationale="Fixture only",
        )
    ]
    reviews[1].labels = [reviews[0].labels[0].model_copy(update={"id": "b"})]
    third = reviews[1].model_copy(deep=True, update={"id": "third", "reviewer_id": "third"})
    third.labels[0].id = "c"
    assert consensus([third, *reversed(reviews)], "flaws") == consensus([*reviews, third], "flaws")
    old = reviews[1].model_copy(deep=True, update={"id": "old"})
    old.labels[0].severity = 3
    reviews[1].supersedes = old.id
    assert consensus([old, third, *reviews], "flaws")[1] is None
    third.labels[0].severity = 2
    assert consensus([old, third, *reviews], "flaws")[1]


def test_label_can_cross_adjacent_inspected_segments(pair_evidence):
    dataset, _, reviews = eval_inputs(pair_evidence)
    r = next(r for r in dataset.recordings if r.id == reviews[0].provenance.recording_id)
    reviews[0].reviewed_spans = [
        Span(start_s=0.0, end_s=0.5),
        Span(start_s=0.5, end_s=r.normalized_info.duration_s),
    ]
    reviews[0].labels = [
        Label(
            id="crossing",
            category="pacing",
            severity=1,
            interval=Span(start_s=0.2, end_s=0.9),
            rationale="Fixture across adjacent listening events",
        )
    ]
    validate_review(reviews[0], r, None)
    reviews[0].reviewed_spans[1].start_s = 0.6
    with pytest.raises(ValueError, match="inspected"):
        validate_review(reviews[0], r, None)


def test_assignment_matches_exhaustive_objective_and_permutations():
    from itertools import permutations

    from taketwo.comparison.matching import assign

    rng = np.random.default_rng(13)
    left, right = ["a", "b", "c"], ["x", "y", "z"]
    for _ in range(30):
        edges = {
            (a, b): float(rng.integers(0, 5)) / 4 for a in left for b in right if rng.random() < 0.6
        }
        candidates = [[]]
        for size in range(1, 4):
            for ls in permutations(left, size):
                for rs in permutations(right, size):
                    pairs = list(zip(ls, rs, strict=True))
                    if all(p in edges for p in pairs):
                        candidates.append(pairs)

        def objective(pairs, weights=edges):
            return len(pairs), sum(weights[p] for p in pairs)

        actual = assign(left, right, edges)
        assert objective(actual) == max(map(objective, candidates))
        assert actual == assign(
            list(reversed(left)), list(reversed(right)), dict(reversed(list(edges.items())))
        )
    with pytest.raises(ValueError, match="unique"):
        assign(["a", "a"], right, {})


def test_matching_threshold_types_and_duplicate_identifiers(pair_evidence):
    p = predicted_region(pair_evidence).model_copy(
        update={"category": "pacing", "participant_interval": Span(start_s=0.0, end_s=2.0)}
    )
    label = Label(
        id="equality",
        category="pacing",
        severity=1,
        interval=Span(start_s=0.0, end_s=1.0),
        rationale="Fixture threshold equality",
    )
    matches, fp, fn = match_regions([p], [label], EvaluationConfig())
    assert len(matches) == 1 and matches[0].iou == 0.5 and not fp and not fn
    assert metrics([p], [label], matches).median_boundary_error_s == 0.5
    with pytest.raises(ValueError, match="unique"):
        match_regions([p, p], [label], EvaluationConfig())
    with pytest.raises(ValueError, match="unique"):
        match_regions([p], [label, label], EvaluationConfig())
    label.category = "energy_variation"
    assert not match_regions([p], [label], EvaluationConfig())[0]
    p.category = "pause_behavior"
    label.category = "pause_behavior"
    label.interval = None
    label.anchor_s = 1.0
    assert not match_regions([p], [label], EvaluationConfig())[0]
    p.participant_interval = None
    p.participant_anchor_s = 1.0
    assert len(match_regions([p], [label], EvaluationConfig())[0]) == 1


def test_three_reviewers_cannot_form_transitive_timing_chain(pair_evidence):
    _, _, reviews = eval_inputs(pair_evidence)
    reviews.append(reviews[0].model_copy(deep=True, update={"id": "third", "reviewer_id": "third"}))
    for index, review in enumerate(reviews):
        review.labels = [
            Label(
                id=str(index),
                category="pacing",
                severity=1,
                interval=Span(start_s=index * 0.15, end_s=1 + index * 0.15),
                rationale="Fixture only",
            )
        ]
    assert consensus(reviews, "flaws")[1]


def test_equal_quality_assignment_ties_are_stable():
    from itertools import permutations

    from taketwo.comparison.matching import assign

    left, right = ["a", "b", "c"], ["x", "y", "z"]
    expected = list(zip(left, right, strict=True))
    for quality in (0.0, 0.5, 1.0):
        edges = {(a, b): quality for a in left for b in right}
        for _ in range(5):
            for ls in permutations(left):
                for rs in permutations(right):
                    assert assign(ls, rs, dict(reversed(list(edges.items())))) == expected
