"""Local filesystem safety and atomic JSONL manifest persistence."""

import json
import os
import stat
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from pydantic import ValidationError

from .errors import DatasetError
from .schema import Annotation, Dataset, Pair, Recording, SplitReport, canonical_json


def safe_path(path: Path, *, root: Path | None = None) -> Path:
    if ".." in path.parts or path.drive.startswith("\\\\"):
        raise DatasetError(
            "unsafe_path",
            "Traversal/UNC paths are not accepted.",
            "Use an explicit local path without '..'.",
            str(path),
        )
    absolute = path.absolute()
    for component in [absolute, *absolute.parents]:
        if component.is_reserved() or component.name.endswith((".", " ")):
            raise DatasetError(
                "unsafe_path",
                "Reserved or ambiguous Windows path component.",
                "Use a regular filename without trailing dots/spaces.",
                str(path),
            )
        if component.name and ":" in component.name:
            raise DatasetError(
                "unsafe_path",
                "Alternate data streams are not accepted.",
                "Use an ordinary filename.",
                str(path),
            )
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 1024:
            raise DatasetError(
                "unsafe_path",
                "Symlinks and reparse points are not accepted.",
                "Use a real local directory/file.",
                str(component),
            )
    if root is not None and not absolute.is_relative_to(root.absolute()):
        raise DatasetError(
            "unsafe_path",
            "Artifact escapes the dataset workspace.",
            "Restore the manifest's managed relative path.",
            str(path),
        )
    return absolute


def managed_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or path.drive or "\\" in relative:
        raise DatasetError(
            "unsafe_path",
            "Manifest paths must be relative POSIX paths.",
            "Use originals/<id>.<ext> or normalized/<id>.wav.",
            relative,
        )
    return safe_path(root / path, root=root)


def unique_json(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> object:
    safe_path(path)
    if path.stat().st_size > 32 * 1024 * 1024:
        raise DatasetError("size_limit", "Metadata exceeds 32 MiB.", "Split the input.", str(path))
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_json)


def manifest_text(dataset: Dataset) -> str:
    data = dataset.model_dump(mode="json")
    rows = [
        {
            "kind": "header",
            "data": {
                "schema_version": dataset.schema_version,
                "dataset_version": dataset.dataset_version,
            },
        }
    ]
    for kind, key in [
        ("recording", "recordings"),
        ("pair", "pairs"),
        ("annotation", "annotations"),
    ]:
        rows.extend(
            {"kind": kind, "data": item} for item in sorted(data[key], key=lambda item: item["id"])
        )
    if data["split"] is not None:
        rows.append({"kind": "split", "data": data["split"]})
    return "".join(canonical_json(row) + "\n" for row in rows)


def load(root: Path) -> Dataset:
    path = managed_path(root, "manifest.jsonl")
    if not path.is_file():
        raise DatasetError(
            "missing_workspace",
            "Dataset manifest does not exist.",
            "Run init or restore manifest.jsonl.",
            str(path),
        )
    if path.stat().st_size > 32 * 1024 * 1024:
        raise DatasetError("size_limit", "Manifest exceeds 32 MiB.", "Partition the dataset.")
    data: dict = {"recordings": [], "pairs": [], "annotations": [], "split": None}
    header = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line, object_pairs_hook=unique_json)
            if set(row) != {"kind", "data"}:
                raise ValueError("row requires exactly kind and data")
            kind = row["kind"]
            if kind == "header" and not header and number == 1:
                if set(row["data"]) != {"schema_version", "dataset_version"}:
                    raise ValueError("invalid header fields")
                data.update(row["data"])
                header = True
            elif kind in {"recording", "pair", "annotation"} and header:
                contract = {"recording": Recording, "pair": Pair, "annotation": Annotation}[kind]
                try:
                    contract.model_validate_json(canonical_json(row["data"]))
                except ValidationError as exc:
                    affected = (
                        row["data"].get("id", f"line-{number}")
                        if isinstance(row["data"], dict)
                        else f"line-{number}"
                    )
                    details = "; ".join(
                        f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()
                    )
                    raise DatasetError(
                        "manifest_schema",
                        f"Line {number}: {details}",
                        "Correct the indicated manifest fields.",
                        str(affected),
                    ) from exc
                data[
                    {"recording": "recordings", "pair": "pairs", "annotation": "annotations"}[kind]
                ].append(row["data"])
            elif kind == "split" and header and data["split"] is None:
                SplitReport.model_validate_json(canonical_json(row["data"]))
                data["split"] = row["data"]
            else:
                raise ValueError("unknown, duplicate or out-of-order manifest row")
        except (ValueError, TypeError, KeyError) as exc:
            raise DatasetError(
                "manifest_schema",
                f"Line {number}: {exc}",
                "Repair the indicated JSONL row.",
                "manifest.jsonl",
            ) from exc
    return Dataset.model_validate_json(canonical_json(data))


def write_new(path: Path, content: bytes) -> None:
    safe_path(path)
    created = False
    try:
        with path.open("xb") as stream:
            created = True
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise DatasetError(
            "overwrite",
            "Output already exists.",
            "Choose a new output path; no overwrite was performed.",
            str(path),
        ) from exc
    except Exception:
        if created:
            path.unlink(missing_ok=True)
        raise


def save(root: Path, dataset: Dataset) -> None:
    temporary = managed_path(root, f".manifest-{uuid.uuid4().hex}.tmp")
    target = managed_path(root, "manifest.jsonl")
    try:
        write_new(temporary, manifest_text(dataset).encode("utf-8"))
        safe_path(target)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def workspace_lock(root: Path) -> Iterator[None]:
    safe_path(root)
    lock = managed_path(root, ".dataset.lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise DatasetError(
            "workspace_busy",
            "Workspace is already locked.",
            "Finish the other command. After a crash, inspect/remove the stale lock.",
        ) from exc
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()
