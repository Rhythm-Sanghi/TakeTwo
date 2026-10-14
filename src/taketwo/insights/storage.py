"""Immutable, bounded comparative envelopes; previous method artifacts are retained."""

import os
import uuid
from pathlib import Path

from taketwo.dataset.audio import sha256
from taketwo.dataset.schema import canonical_json, content_hash
from taketwo.dataset.storage import managed_path, read_json, write_new

from .contracts import ComparativeReport


def implementation_hash():
    return content_hash(
        {p.name: sha256(p.read_bytes()) for p in sorted(Path(__file__).parent.glob("*.py"))}
    )


def publish(root, result):
    payload = result.model_dump(mode="json")
    digest = content_hash(payload)
    path = managed_path(root, f"derived/comparative-insights-v1/insights-{digest}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (canonical_json({"sha256": digest, "result": payload}) + "\n").encode("utf-8")
    if len(content) > 4 * 1024 * 1024:
        raise ValueError("Comparative report exceeds 4 MiB; use a smaller excerpt.")
    temporary = path.parent / f".publish-{uuid.uuid4().hex}.tmp"
    try:
        write_new(temporary, content)
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != content:
                raise ValueError(
                    "Comparative artifact differs; existing evidence preserved."
                ) from None
    finally:
        temporary.unlink(missing_ok=True)
    return path


def read_artifact(path):
    envelope = read_json(path)
    if (
        not isinstance(envelope, dict)
        or set(envelope) != {"sha256", "result"}
        or content_hash(envelope["result"]) != envelope["sha256"]
    ):
        raise ValueError("Comparative artifact checksum differs.")
    return ComparativeReport.model_validate_json(canonical_json(envelope["result"]))
