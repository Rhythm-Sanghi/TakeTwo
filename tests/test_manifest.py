import copy

import numpy as np
import pytest
import soundfile as sf
from pydantic import ValidationError

from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import Annotation, ImportSpec, canonical_json
from taketwo.dataset.storage import load, managed_path, manifest_text, save, workspace_lock
from taketwo.dataset.validation import validate
from taketwo.dataset.workspace import add_annotations, import_recording, initialize


def make_human(imported, metadata, tmp_path, signal):
    root, reference = imported
    mirror_metadata = copy.deepcopy(metadata)
    mirror_metadata["origin"] = "self_recorded"
    mirror_metadata["speaker_id"] = "test-mirror"
    mirror_metadata["provenance"]["source_id"] = "mirror-source"
    mirror_metadata["provenance"]["consent_evidence"] = "test-only consent marker"
    path = tmp_path / "human-fixture.wav"
    sf.write(path, signal * 0.8, 16000, subtype="FLOAT")
    spec = ImportSpec.model_validate_json(canonical_json(mirror_metadata))
    recording = import_recording(
        root, path, spec, reference_id=reference.id, category="pacing", severity=2
    )
    return recording, load(root).pairs[0]


def human_annotation(recording, pair):
    return Annotation(
        id="test-label",
        pair_id=pair.id,
        recording_id=recording.id,
        transcript_sha256=recording.transcript_sha256,
        category="pacing",
        start_s=0.2,
        end_s=0.8,
        severity=2,
        source="human",
        review_status="reviewed",
        reviewer_id="test-reviewer",
        rationale="Software test only, not a real review",
        uncertainty_s=0.1,
        token_span=(0, 2),
        transformation_sha256=None,
    )


def test_import_human_and_annotation(imported, metadata, tmp_path, signal):
    root, _ = imported
    recording, pair = make_human(imported, metadata, tmp_path, signal)
    assert pair.identity_status == "needs_review"
    assert load(root).annotations == []  # Human flaws never get invented timestamps.
    annotation = human_annotation(recording, pair)
    add_annotations(root, [annotation])
    state = load(root)
    assert state.annotations == [annotation]
    assert validate(state, root)["valid"]
    assert not validate(state, root, publication=True)["valid"]


def test_wrong_human_transcript_rejected(imported, metadata, audio_path):
    root, reference = imported
    metadata["transcript"]["text"] = "These are different words."
    spec = ImportSpec.model_validate_json(canonical_json(metadata))
    with pytest.raises(DatasetError, match="transcript/family"):
        import_recording(
            root, audio_path, spec, reference_id=reference.id, category="pacing", severity=1
        )


@pytest.mark.parametrize("field", ["speaker_id", "provenance", "transcript", "family_id"])
def test_missing_metadata(metadata, field):
    del metadata[field]
    with pytest.raises(ValidationError):
        ImportSpec.model_validate_json(canonical_json(metadata))


def test_verified_requires_two_reviewers(metadata):
    metadata["transcript"]["status"] = "verified"
    with pytest.raises(ValidationError):
        ImportSpec.model_validate_json(canonical_json(metadata))


@pytest.mark.parametrize("field", ["holder", "license_name", "evidence", "attribution", "status"])
def test_missing_rights_fields(metadata, field):
    del metadata["provenance"]["rights"][field]
    with pytest.raises(ValidationError):
        ImportSpec.model_validate_json(canonical_json(metadata))


def test_clearance_requires_permissions(metadata):
    metadata["provenance"]["rights"]["status"] = "cleared"
    with pytest.raises(ValidationError, match="permit"):
        ImportSpec.model_validate_json(canonical_json(metadata))


@pytest.mark.parametrize(
    "changes",
    [
        {"end_s": 0.1},
        {"category": "imagined_flaw"},
        {"severity": 4},
        {"severity": 0},
        {"reviewer_id": None},
        {"source": "synthetic_recipe", "transformation_sha256": "a" * 64},
        {"uncertainty_s": float("nan")},
    ],
)
def test_invalid_annotation_schema(imported, metadata, tmp_path, signal, changes):
    recording, pair = make_human(imported, metadata, tmp_path, signal)
    data = human_annotation(recording, pair).model_dump()
    data.update(changes)
    with pytest.raises(ValidationError):
        Annotation.model_validate(data)


@pytest.mark.parametrize(
    "changes,code",
    [
        ({"end_s": 10.0}, "annotation_interval"),
        ({"transcript_sha256": "0" * 64}, "annotation_transcript"),
        ({"token_span": (0, 1000)}, "annotation_tokens"),
        ({"pair_id": "missing"}, "annotation_relationship"),
        ({"supersedes": "missing"}, "annotation_history"),
    ],
)
def test_annotation_semantics_and_atomicity(imported, metadata, tmp_path, signal, changes, code):
    root, _ = imported
    recording, pair = make_human(imported, metadata, tmp_path, signal)
    before = (root / "manifest.jsonl").read_bytes()
    annotation = human_annotation(recording, pair).model_copy(update=changes)
    state = load(root)
    state.annotations.append(annotation)
    assert code in {e["code"] for e in validate(state, root)["errors"]}
    with pytest.raises(DatasetError):
        add_annotations(root, [annotation])
    assert (root / "manifest.jsonl").read_bytes() == before


@pytest.mark.parametrize(
    "mutation,code",
    [
        ("duplicate_id", "duplicate_id"),
        ("transcript", "transcript_hash"),
        ("version", "dataset_version"),
        ("audio_info", "audio_metadata"),
        ("hash", "original_hash"),
        ("versions", "processing_versions"),
    ],
)
def test_manifest_inconsistency(imported, mutation, code):
    root, _ = imported
    state = load(root)
    recording = state.recordings[0]
    if mutation == "duplicate_id":
        state.recordings.append(recording)
    elif mutation == "transcript":
        recording.tokens = ["wrong"]
    elif mutation == "version":
        recording.dataset_version = "wrong-version"
    elif mutation == "audio_info":
        recording.original_info.frames += 1
    elif mutation == "hash":
        recording.original_sha256 = "0" * 64
    else:
        recording.processing.versions = {}
    assert code in {e["code"] for e in validate(state, root)["errors"]}


@pytest.mark.parametrize("damage", ["missing", "corrupt", "samples"])
def test_artifact_damage(imported, damage):
    root, recording = imported
    path = root / recording.normalized_path
    if damage == "missing":
        path.unlink()
    elif damage == "corrupt":
        path.write_bytes(b"broken")
    else:
        sf.write(path, np.full(32000, 0.1), 16000, subtype="FLOAT")
    assert not validate(load(root), root)["valid"]


def test_manifest_roundtrip_and_unknown_rows(imported):
    root, _ = imported
    state = load(root)
    before = manifest_text(state)
    save(root, state)
    assert manifest_text(load(root)) == before
    path = root / "manifest.jsonl"
    path.write_text(before + '{"kind":"future","data":{}}\n', encoding="utf-8")
    with pytest.raises(DatasetError, match="unknown"):
        load(root)


@pytest.mark.parametrize(
    "path", ["../escape.wav", "C:/escape.wav", "originals\\escape.wav", "originals/a.wav:stream"]
)
def test_managed_path_safety(tmp_path, path):
    with pytest.raises(DatasetError):
        managed_path(tmp_path, path)


def test_workspace_collision_and_lock(imported):
    root, _ = imported
    with pytest.raises(DatasetError, match="new directory"):
        initialize(root, "v2")
    with workspace_lock(root):
        with pytest.raises(DatasetError, match="locked"):
            with workspace_lock(root):
                pass
    assert not (root / ".dataset.lock").exists()


def test_symlink_rejected(imported, tmp_path):
    root, recording = imported
    original = root / recording.original_path
    alias = tmp_path / "alias.wav"
    try:
        alias.symlink_to(original)
    except OSError:
        pytest.skip("Windows symlink creation privilege is unavailable")
    from taketwo.dataset.audio import read_audio

    with pytest.raises(DatasetError, match="Symlinks"):
        read_audio(alias)


def test_no_partial_artifacts_on_existing_output(imported, metadata, tmp_path, signal, monkeypatch):
    import taketwo.dataset.workspace as workspace

    root, _ = imported
    before = (root / "manifest.jsonl").read_bytes()
    files = sorted(p.name for p in (root / "originals").iterdir())

    def failed_save(*_):
        raise OSError("simulated disk failure")

    monkeypatch.setattr(workspace, "save", failed_save)
    with pytest.raises(OSError, match="disk failure"):
        make_human(imported, metadata, tmp_path, signal)
    assert sorted(p.name for p in (root / "originals").iterdir()) == files
    assert (root / "manifest.jsonl").read_bytes() == before
