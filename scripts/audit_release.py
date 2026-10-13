"""Inspect tracked release candidates without printing possible secret values."""

import json
import re
import subprocess
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


def main():
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
    result = {
        "candidate_files": len(files),
        "blocking_findings": findings,
        "personal_absolute_path_files": absolute_paths,
        "binary_files_for_review": binary_files,
        "code_license_present": license_present,
        "reachable_history_blobs": len(checked),
        "history_blocking_findings": history_findings,
        "scope": "Pattern/inventory preflight; review staged diff, history, rights and public "
        "artifacts separately. Not proof of absence of every secret or rights issue.",
    }
    print(json.dumps(result, indent=2))
    return int(bool(findings or absolute_paths or history_findings))


if __name__ == "__main__":
    raise SystemExit(main())
