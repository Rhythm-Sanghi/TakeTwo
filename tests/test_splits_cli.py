import copy
import json
import subprocess
import sys
import time

import numpy as np
import pytest
from test_transform import recipe

from taketwo.dataset.audio import wav_bytes
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import ImportSpec, canonical_json
from taketwo.dataset.splits import connected_groups, make_split
from taketwo.dataset.storage import load, manifest_text
from taketwo.dataset.validation import validate
from taketwo.dataset.workspace import assign_splits, generate, import_recording, initialize


def independent_dataset(tmp_path, metadata):
    root = tmp_path / "split-workspace"
    initialize(root, "v1")
    for i in range(6):
        spec = copy.deepcopy(metadata)
        spec["family_id"] = f"family-{i}"
        spec["speaker_id"] = f"speaker-{i}"
        spec["transcript"]["text"] = f"Independent test words number {i}."
        spec["provenance"]["source_id"] = f"source-{i}"
        spec["provenance"]["work_id"] = f"work-{i}"
        path = tmp_path / f"fixture-{i}.wav"
        x = (0.2 * np.sin(2 * np.pi * (220 + 10 * i) * np.arange(32000) / 16000)).astype(np.float32)
        path.write_bytes(wav_bytes(x))
        import_recording(root, path, ImportSpec.model_validate_json(canonical_json(spec)))
    return root, load(root)


def test_deterministic_split_and_derivative_inheritance(tmp_path, metadata):
    root, state = independent_dataset(tmp_path, metadata)
    split = assign_splits(root, 17, (0.5, 0.25, 0.25))
    assert split == assign_splits(root, 17, (0.5, 0.25, 0.25))
    assert set(split["assignments"].values()) == {"train", "validation", "test"}
    parent = state.recordings[0]
    derivative = generate(root, parent.id, recipe("gain", 0.2, 0.8, 0.5))
    updated = load(root)
    assert updated.split.assignments[derivative.id] == split["assignments"][parent.id]
    assert all(
        updated.split.assignments[key] == value for key, value in split["assignments"].items()
    )
    assert validate(updated, root)["valid"]
    assert make_split(updated, 17, (0.5, 0.25, 0.25)) == updated.split
    with pytest.raises(DatasetError, match="silently reassigned"):
        assign_splits(root, 23, (1.0, 0.0, 0.0))


@pytest.mark.parametrize("field", ["family", "speaker", "work", "source", "transcript"])
def test_stricter_group_links(tmp_path, metadata, field):
    _, state = independent_dataset(tmp_path, metadata)
    left, right = state.recordings[:2]
    if field == "family":
        right.family_id = left.family_id
    elif field == "speaker":
        right.speaker_id = left.speaker_id
    elif field in {"work", "source"}:
        setattr(right.provenance, field + "_id", getattr(left.provenance, field + "_id"))
    else:
        right.transcript_sha256 = left.transcript_sha256
    groups = connected_groups(state)
    assert len(groups) == 5
    assert any(left.id in members and right.id in members for members in groups.values())


def test_detect_leakage(imported):
    root, reference = imported
    derivative = generate(root, reference.id, recipe("gain", 0.2, 0.8, 0.5))
    assign_splits(root, 1, (0.5, 0.25, 0.25))
    state = load(root)
    state.split.assignments[derivative.id] = "test"
    codes = {e["code"] for e in validate(state, root)["errors"]}
    assert "split_leakage" in codes and "split_hash" in codes and "split_replay" in codes


@pytest.mark.parametrize("ratios", [(1.0, 1.0, 1.0), (-0.1, 0.5, 0.6), (float("nan"), 0.0, 1.0)])
def test_invalid_split_ratios(imported, ratios):
    root, _ = imported
    with pytest.raises(DatasetError):
        assign_splits(root, 0, ratios)


def command(*args):
    return subprocess.run(
        [sys.executable, "-m", "taketwo.dataset.cli", *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_cli_workflow(tmp_path, audio_path, metadata):
    root = tmp_path / "cli-workspace"
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(canonical_json(metadata), encoding="utf-8")
    assert command("init", root, "--version", "v1").returncode == 0
    imported = command("import-reference", root, "--audio", audio_path, "--metadata", metadata_path)
    assert imported.returncode == 0, imported.stderr
    reference_id = json.loads(imported.stdout)["recording_id"]
    recipe_path = tmp_path / "recipe.json"
    recipe_path.write_text(
        canonical_json(recipe("gain", 0.2, 0.8, 0.5).model_dump(mode="json")), encoding="utf-8"
    )
    generated = command("generate", root, "--reference", reference_id, "--recipe", recipe_path)
    assert generated.returncode == 0, generated.stderr
    assert command("split", root, "--seed", "17").returncode == 0
    checked = command("validate", root, "--reproduce")
    assert checked.returncode == 0 and json.loads(checked.stdout)["valid"]
    assert command("validate", root, "--publication").returncode == 1
    output = tmp_path / "export.json"
    assert command("export", root, "--output", output).returncode == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["origins"]["synthetic"] == 1
    assert command("export", root, "--output", output).returncode == 2
    assert json.loads(command("schema").stdout)["properties"]["schema_version"]["const"] == 1


@pytest.mark.parametrize(
    "arguments",
    [
        ["init"],
        ["not-a-command"],
        ["validate", "missing-workspace"],
        ["init", "invalid-root", "--version", "../unsafe"],
    ],
)
def test_cli_errors_are_structured(arguments):
    result = command(*arguments)
    assert result.returncode == 2
    assert json.loads(result.stderr)["error"]["recovery"]


def test_cli_rejects_bad_schema_and_duplicate_json(tmp_path):
    root = tmp_path / "bad-json"
    command("init", root, "--version", "v1")
    metadata = tmp_path / "bad.json"
    for text in ["{}", '{"family_id":"a","family_id":"b"}']:
        metadata.write_text(text, encoding="utf-8")
        result = command("import-reference", root, "--audio", "missing.wav", "--metadata", metadata)
        assert result.returncode == 2 and json.loads(result.stderr)["error"]


def test_repeat_builds_have_identical_semantic_metadata(tmp_path, audio_path, spec, signal):
    first = tmp_path / "build-one"
    second = tmp_path / "build-two"
    configuration = recipe("gain", 0.2, 0.8, 0.5)
    initialize(first, "v1")
    reference = import_recording(first, audio_path, spec)
    generate(first, reference.id, configuration)
    # Catch libsndfile FLOAT PEAK timestamps changing encoded file hashes.
    time.sleep(1.1)
    initialize(second, "v1")
    reference2 = import_recording(second, audio_path, spec)
    generate(second, reference2.id, configuration)
    assert manifest_text(load(first)) == manifest_text(load(second))
    for relative in [r.normalized_path for r in load(first).recordings]:
        assert (first / relative).read_bytes() == (second / relative).read_bytes()
    assert wav_bytes(signal) == wav_bytes(signal.copy())
