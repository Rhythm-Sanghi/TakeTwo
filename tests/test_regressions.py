import json
import struct
from pathlib import Path
from unittest.mock import patch

import pytest
from test_splits_cli import command
from test_transform import recipe

from taketwo.dataset.audio import decode, read_audio, wav_bytes
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import Dataset
from taketwo.dataset.storage import load, safe_path, write_new
from taketwo.dataset.validation import validate
from taketwo.dataset.workspace import generate


@pytest.mark.parametrize("change", ["truncated", "bad_size", "partial_frame"])
def test_wav_structural_corruption(signal, change):
    data = wav_bytes(signal)
    if change == "truncated":
        data = data[:-4]
    elif change == "bad_size":
        data = data[:4] + struct.pack("<I", 0) + data[8:]
    else:
        data = data[:-1]
        data = data[:4] + struct.pack("<I", len(data) - 8) + data[8:]
    with pytest.raises(DatasetError, match="corrupt|truncated"):
        decode(data)


@pytest.mark.parametrize("tamper", ["interval", "severity", "missing", "recipe", "time_map"])
def test_synthetic_annotation_integrity(imported, tamper):
    root, parent = imported
    generate(root, parent.id, recipe("gain", 0.2, 0.8, 0.5))
    state = load(root)
    synthetic = next(r for r in state.recordings if r.origin == "synthetic")
    if tamper == "interval":
        state.annotations[0].start_s += 0.01
    elif tamper == "severity":
        state.annotations[0].severity = 1
    elif tamper == "missing":
        state.annotations.clear()
    elif tamper == "recipe":
        synthetic.transformation.recipe_sha256 = "0" * 64
    else:
        synthetic.transformation.time_map[0].output_end += 1
    assert not validate(state, root)["valid"]


def test_processing_channel_mismatch(imported):
    root, _ = imported
    state = load(root)
    state.recordings[0].processing.channel = 1
    assert "processing_channel" in {e["code"] for e in validate(state, root)["errors"]}


def test_windows_reparse_point_rejected(tmp_path):
    original = type(tmp_path).lstat

    class ReparseInfo:
        st_mode = 0
        st_file_attributes = 1024

    def lstat(path):
        return ReparseInfo() if path == tmp_path else original(path)

    with patch.object(type(tmp_path), "lstat", lstat):
        with pytest.raises(DatasetError, match="reparse"):
            safe_path(tmp_path)


def test_sparse_input_size_limit(tmp_path):
    path = tmp_path / "too-big.wav"
    with path.open("wb") as stream:
        stream.truncate(100 * 1024 * 1024 + 1)
    with pytest.raises(DatasetError, match="100 MiB"):
        read_audio(path)


def test_invalid_cli_manifest_is_nonzero(imported):
    root, _ = imported
    with (root / "manifest.jsonl").open("a", encoding="utf-8") as stream:
        stream.write('{"kind":"annotation","data":{"id":"bad"}}\n')
    result = command("validate", root)
    assert result.returncode == 2
    assert json.loads(result.stderr)["error"]["code"] == "manifest_schema"
    assert json.loads(result.stderr)["error"]["affected"] == "bad"


def test_export_rejects_symlink_output(imported, tmp_path):
    root, _ = imported
    outside = tmp_path / "outside.json"
    outside.write_text("untouched", encoding="utf-8")
    link = tmp_path / "linked.json"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("Windows symlink creation privilege is unavailable")
    result = command("export", root, "--output", link)
    assert result.returncode == 2
    assert outside.read_text(encoding="utf-8") == "untouched"


def test_partial_file_removed_on_write_failure(tmp_path):
    path = tmp_path / "new.wav"
    with patch("taketwo.dataset.storage.os.fsync", side_effect=OSError("disk error")):
        with pytest.raises(OSError, match="disk error"):
            write_new(path, b"partial")
    assert not path.exists()


@pytest.mark.parametrize("name", ["CON", "NUL.wav", "trailing.", "trailing "])
def test_reserved_windows_paths(tmp_path, name):
    with pytest.raises(DatasetError, match="Reserved"):
        safe_path(tmp_path / name)


def test_documented_schema_matches_runtime():
    path = Path(__file__).resolve().parents[1] / "docs" / "dataset-schema-v1.json"
    assert json.loads(path.read_text(encoding="utf-8")) == Dataset.model_json_schema()
