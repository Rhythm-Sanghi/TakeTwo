"""Small immutable exploratory artifacts; no duplicate feature arrays or old rewrites."""

import os
import uuid
from pathlib import Path

from taketwo.dataset.audio import sha256
from taketwo.dataset.schema import canonical_json, content_hash
from taketwo.dataset.storage import managed_path, read_json, write_new

from .contracts import ExploratoryReport


def implementation_hash():
    return content_hash(
        {p.name: sha256(p.read_bytes()) for p in sorted(Path(__file__).parent.glob("*.py"))}
    )


def publish(root, result):
    payload = result.model_dump(mode="json")
    digest = content_hash(payload)
    path = managed_path(root, f"derived/exploratory-v1/exploratory-{digest}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (canonical_json({"sha256": digest, "result": payload}) + "\n").encode("utf-8")
    if len(content) > 4 * 1024 * 1024:
        raise ValueError("Exploratory report exceeds 4 MiB; use a smaller excerpt.")
    temporary = managed_path(root, f"derived/exploratory-v1/.publish-{uuid.uuid4().hex}.tmp")
    try:
        write_new(temporary, content)
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != content:
                raise ValueError(
                    "Exploratory artifact differs; existing evidence preserved."
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
        raise ValueError("Exploratory artifact checksum differs.")
    return ExploratoryReport.model_validate_json(canonical_json(envelope["result"]))
