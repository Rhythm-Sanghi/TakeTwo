"""Inspect tracked release candidates without printing possible secret values."""

import argparse
import json
import re
import stat
import subprocess
import tarfile
import zipfile
from contextlib import ExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = (
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    rb"gh[pousr]_[A-Za-z0-9]{30,}",
    rb"github_pat_[A-Za-z0-9_]{50,}",
    rb"AKIA[0-9A-Z]{16}",
    rb"sk-(?:proj-)?[A-Za-z0-9_-]{40,}",
)
PRIVATE_PARTS = {
    ".diagnostics",
    "local-data",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "models",
    ".pytest_cache",
    ".ruff_cache",
    "test-results",
    "playwright-report",
    "tmp",
    "speech-01",
}
MEDIA_SUFFIXES = {
    ".wav",
    ".flac",
    ".mp3",
    ".ogg",
    ".mp4",
    ".sqlite3",
    ".zip",
    ".db",
    ".sqlite",
    ".pt",
    ".pth",
    ".onnx",
    ".safetensors",
    ".pkl",
    ".key",
    ".pem",
}


def audit_packages(root):
    """Inspect archive members without extracting or displaying secret values."""
    archives = [*sorted((root / "dist").glob("*.whl")), *sorted((root / "dist").glob("*.tar.gz"))]
    findings = []
    if not archives:
        return [{"archive": "dist", "issue": "Build wheel/sdist before package preflight"}]
    for path in archives:
        with ExitStack() as stack:
            if path.suffix == ".whl":
                archive = stack.enter_context(zipfile.ZipFile(path))
                members = [
                    (m.filename, m.file_size, m) for m in archive.infolist() if not m.is_dir()
                ]
                read = archive.read
            else:
                archive = stack.enter_context(tarfile.open(path))
                members = [(m.name, m.size, m) for m in archive if not m.isdir()]

                def read(member, source=archive):
                    if not member.isfile():
                        return b""
                    with source.extractfile(member) as stream:
                        return stream.read()

            if not any(name.endswith("/LICENSE") or name == "LICENSE" for name, _, _ in members):
                findings.append({"archive": path.name, "issue": "Packaged LICENSE missing"})
            for name, size, member in members:
                relative = Path(name)
                forbidden = bool(set(relative.parts) & (PRIVATE_PARTS | {"dist", "coverage"}))
                forbidden |= isinstance(member, tarfile.TarInfo) and not member.isfile()
                forbidden |= isinstance(member, zipfile.ZipInfo) and stat.S_ISLNK(
                    member.external_attr >> 16
                )
                forbidden |= relative.is_absolute() or ".." in relative.parts or "\\" in name
                forbidden |= relative.suffix.lower() in MEDIA_SUFFIXES | {".node", ".dll", ".exe"}
                forbidden |= relative.name.startswith(".env") and relative.name != ".env.example"
                forbidden |= relative.name == ".review-operator-key" or size > 5 * 1024 * 1024
                if not forbidden:
                    data = read(member)
                    forbidden = any(re.search(pattern, data) for pattern in SECRET_PATTERNS)
                    forbidden |= b"\0" not in data and bool(
                        re.search(rb"[A-Za-z]:[\\/]Users[\\/][^\s]+", data)
                    )
                if forbidden:
                    findings.append(
                        {"archive": path.name, "path": name, "issue": "Unsafe package member"}
                    )
    return findings


def main(*, packages=False):
    names = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
        )
        .decode()
        .split("\0")
    )
    findings = []
    absolute_paths = []
    binary_files = []
    files = [Path(name) for name in names if name and (ROOT / name).is_file()]
    for relative in files:
        path = ROOT / relative
        data = path.read_bytes()
        if (
            relative.name == ".review-operator-key"
            or set(relative.parts) & PRIVATE_PARTS
            or (relative.name.startswith(".env") and relative.name != ".env.example")
        ):
            findings.append({"path": relative.as_posix(), "issue": "private/runtime candidate"})
        if relative.suffix.lower() in MEDIA_SUFFIXES or len(data) > 5 * 1024 * 1024:
            findings.append({"path": relative.as_posix(), "issue": "media or large asset review"})
        if any(re.search(pattern, data) for pattern in SECRET_PATTERNS):
            findings.append({"path": relative.as_posix(), "issue": "possible credential"})
        if b"\0" in data:
            binary_files.append({"path": relative.as_posix(), "bytes": len(data)})
            continue
        text = data.decode("utf-8", errors="replace")
        if re.search(r"[A-Za-z]:[\\/]Users[\\/][^\s]+", text):
            absolute_paths.append(relative.as_posix())
    license_present = (ROOT / "LICENSE").is_file()
    if not license_present:
        findings.append({"path": "LICENSE", "issue": "owner-selected source license missing"})
    # Audit every blob reachable through local publication refs, including deleted
    # files. Ignore rules never remove previously committed content from history.
    objects = (
        subprocess.check_output(["git", "rev-list", "--objects", "--all"], cwd=ROOT)
        .decode()
        .splitlines()
    )
    history_findings, checked = [], set()
    for item in objects:
        oid, _, name = item.partition(" ")
        if not name or oid in checked:
            continue
        kind = subprocess.check_output(["git", "cat-file", "-t", oid], cwd=ROOT).strip()
        if kind != b"blob":
            continue
        checked.add(oid)
        data = subprocess.check_output(["git", "cat-file", "blob", oid], cwd=ROOT)
        relative = Path(name)
        private = bool(set(relative.parts) & (PRIVATE_PARTS | {"speech-01"}))
        private |= relative.suffix.lower() in MEDIA_SUFFIXES
        private |= relative.name == ".review-operator-key" or (
            relative.name.startswith(".env") and relative.name != ".env.example"
        )
        secret = any(re.search(pattern, data) for pattern in SECRET_PATTERNS)
        absolute = b"\0" not in data and bool(re.search(rb"[A-Za-z]:[\\/]Users[\\/][^\s]+", data))
        if private or secret or absolute or len(data) > 5 * 1024 * 1024:
            history_findings.append(
                {
                    "object": oid,
                    "path": name,
                    "issue": "private/secret/path/large history candidate",
                }
            )
    package_findings = audit_packages(ROOT) if packages else []
    result = {
        "candidate_files": len(files),
        "blocking_findings": findings,
        "personal_absolute_path_files": absolute_paths,
        "binary_files_for_review": binary_files,
        "code_license_present": license_present,
        "reachable_history_blobs": len(checked),
        "history_blocking_findings": history_findings,
        "package_blocking_findings": package_findings,
        "scope": "Pattern/inventory preflight; review staged diff, history, rights and public "
        "artifacts separately. Not proof of absence of every secret or rights issue.",
    }
    print(json.dumps(result, indent=2))
    return int(bool(findings or absolute_paths or history_findings or package_findings))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packages", action="store_true", help="Also inspect built wheel/sdist")
    raise SystemExit(main(packages=parser.parse_args().packages))
