"""Preflight negative controls use generated strings/files, never actual private data."""

import io
import json
import runpy
import tarfile
import zipfile
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "name", ["private.wav", "workspace.sqlite", ".review-operator-key", ".env", "models/model.onnx"]
)
def test_release_rejects_private_candidates(tmp_path, monkeypatch, capsys, name):
    module = runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit_release.py"))
    main = module["main"]
    main.__globals__["ROOT"] = tmp_path
    (tmp_path / "LICENSE").write_text("MIT License fixture", encoding="utf-8")
    candidate = tmp_path / name
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(b"generated software fixture")

    def git(args, **_):
        if args[1] == "ls-files":
            return (name + "\0").encode()
        if args[1] == "rev-list":
            return b""
        raise AssertionError(args)

    monkeypatch.setattr(main.__globals__["subprocess"], "check_output", git)
    assert main() == 1
    assert json.loads(capsys.readouterr().out)["blocking_findings"]


def test_release_missing_license_is_blocking(tmp_path, monkeypatch, capsys):
    main = runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit_release.py"))["main"]
    main.__globals__["ROOT"] = tmp_path
    monkeypatch.setattr(main.__globals__["subprocess"], "check_output", lambda *_a, **_k: b"")
    assert main() == 1
    result = json.loads(capsys.readouterr().out)
    assert not result["code_license_present"]
    assert result["blocking_findings"][0]["path"] == "LICENSE"


def test_release_deleted_history_secret_remains_blocking(tmp_path, monkeypatch, capsys):
    main = runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit_release.py"))["main"]
    main.__globals__["ROOT"] = tmp_path
    (tmp_path / "LICENSE").write_text("MIT License fixture", encoding="utf-8")

    def git(args, **_):
        if args[1] == "ls-files":
            return b""
        if args[1] == "rev-list":
            return b"fixture-object deleted.txt\n"
        if args[2] == "-t":
            return b"blob"
        return b"gh" + b"p_" + b"A" * 40  # Generated token-shaped negative control.

    monkeypatch.setattr(main.__globals__["subprocess"], "check_output", git)
    assert main() == 1
    result = json.loads(capsys.readouterr().out)
    assert result["reachable_history_blobs"] == 1
    assert result["history_blocking_findings"][0]["path"] == "deleted.txt"


@pytest.mark.parametrize("format", ["whl", "tar.gz"])
def test_package_preflight_rejects_dependency_cache_and_preserves_source(tmp_path, format):
    inspect = runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit_release.py"))[
        "audit_packages"
    ]
    for root, unsafe in [(tmp_path / "bad", True), (tmp_path / "clean", False)]:
        (root / "dist").mkdir(parents=True)
        members = {"taketwo/LICENSE": b"MIT License fixture", "taketwo/src/app.py": b"pass\n"}
        if unsafe:
            members["taketwo/frontend/node_modules/generated.node"] = b"generated negative control"
        path = root / "dist" / ("fixture." + format)
        if format == "whl":
            with zipfile.ZipFile(path, "w") as archive:
                for name, content in members.items():
                    archive.writestr(name, content)
        else:
            with tarfile.open(path, "w:gz") as archive:
                for name, content in members.items():
                    info = tarfile.TarInfo(name)
                    info.size = len(content)
                    archive.addfile(info, io.BytesIO(content))
        findings = inspect(root)
        assert bool(findings) == unsafe
        if unsafe:
            assert findings[0]["path"].endswith("generated.node")
