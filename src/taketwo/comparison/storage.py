"""Content-addressed evidence artifacts; Phase 1/2 schemas and code stay unchanged."""

import os
import uuid
from pathlib import Path

from taketwo.analysis.contracts import AlignmentResult, FeatureResult
from taketwo.analysis.storage import read_artifact as read_analysis
from taketwo.analysis.storage import validate_identity
from taketwo.dataset.audio import sha256
from taketwo.dataset.schema import Dataset, canonical_json, content_hash
from taketwo.dataset.storage import managed_path, read_json, safe_path, write_new
from taketwo.dataset.workspace import find_recording

from .contracts import ArtifactRef, Evaluation, Report, Review
from .engine import Evidence, compare
from .reviews import validate_review


def implementation_hash():
    directory = Path(__file__).parent
    return content_hash({p.name: sha256(p.read_bytes()) for p in sorted(directory.glob("*.py"))})


def publish(root: Path, result: Report | Review | Evaluation):
    payload = result.model_dump(mode="json")
    digest = content_hash(payload)
    path = managed_path(root, f"derived/comparison-v1/{result.kind}-{digest}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (canonical_json({"sha256": digest, "result": payload}) + "\n").encode("utf-8")
    if len(content) > 32 * 1024 * 1024:
        raise ValueError("Evidence artifact exceeds 32 MiB; use a smaller evaluation batch.")
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError("Existing evidence artifact differs; no overwrite performed.")
    else:
        # Publish a fully fsynced inode atomically, with no replacement. A hard
        # interruption can leave a staging file, never a partial evidence target.
        temporary = managed_path(root, f"derived/comparison-v1/.publish-{uuid.uuid4().hex}.tmp")
        try:
            write_new(temporary, content)
            try:
                os.link(temporary, path)
            except FileExistsError:
                if path.read_bytes() != content:
                    raise ValueError(
                        "Existing evidence artifact differs; no overwrite performed."
                    ) from None
        finally:
            temporary.unlink(missing_ok=True)
    return path


def read_artifact(path: Path):
    envelope = read_json(path)
    if not isinstance(envelope, dict) or set(envelope) != {"sha256", "result"}:
        raise ValueError("Expected hashed evidence artifact envelope.")
    if content_hash(envelope["result"]) != envelope["sha256"]:
        raise ValueError("Evidence artifact content hash differs.")
    contract = {"comparison": Report, "review": Review, "evaluation": Evaluation}.get(
        envelope["result"].get("kind")
    )
    if contract is None:
        raise ValueError("Unknown evidence artifact kind.")
    result = contract.model_validate_json(canonical_json(envelope["result"]))
    if isinstance(result, Report) and result.policy_sha256 != content_hash(
        result.policy.model_dump(mode="json")
    ):
        raise ValueError("Report policy hash differs.")
    return result


def artifact_ref(root: Path, path: Path, result):
    path = safe_path(path, root=root)
    return ArtifactRef(
        path=path.relative_to(root.absolute()).as_posix(),
        sha256=content_hash(result.model_dump(mode="json")),
    )


def load_evidence(root, dataset, feature_path, alignment_path=None, review_paths=()):
    features = read_analysis(safe_path(feature_path, root=root))
    if not isinstance(features, FeatureResult):
        raise ValueError("Expected Phase 2 features.")
    validate_identity(root, features)
    recording = find_recording(dataset, features.provenance.recording_id)
    alignment = read_analysis(safe_path(alignment_path, root=root)) if alignment_path else None
    if alignment is not None and not isinstance(alignment, AlignmentResult):
        raise ValueError("Expected Phase 2 alignment.")
    if alignment:
        validate_identity(root, alignment)
    reviews, references = [], []
    for path in review_paths:
        review = read_artifact(safe_path(path, root=root))
        if not isinstance(review, Review):
            raise ValueError("Expected imported human review artifact.")
        if review.provenance.recording_id != recording.id:
            continue  # Shared CLI list can include both pair members.
        validate_review(review, recording, alignment)
        reviews.append(review)
        references.append(artifact_ref(root, path, review))
    return Evidence(
        recording,
        features,
        artifact_ref(root, feature_path, features),
        alignment,
        artifact_ref(root, alignment_path, alignment) if alignment else None,
        reviews,
        references,
    )


def bound_dataset(root, dataset, report: Report):
    if report.dataset_sha256 == content_hash(dataset.model_dump(mode="json")):
        return dataset
    path = managed_path(root, f"derived/comparison-v1/dataset-{report.dataset_sha256}.json")
    if not path.is_file():
        raise ValueError(
            "Dataset changed and the legacy report has no saved snapshot; compare again."
        )
    snapshot = Dataset.model_validate_json(canonical_json(read_json(path)))
    if content_hash(snapshot.model_dump(mode="json")) != report.dataset_sha256:
        raise ValueError("Dataset snapshot hash differs.")
    for member in report.inputs:
        rid = member.provenance.recording_id
        if find_recording(snapshot, rid) != find_recording(dataset, rid):
            raise ValueError("A report recording changed; compare again.")
    if report.pair_id and next((p for p in snapshot.pairs if p.id == report.pair_id), None) != next(
        (p for p in dataset.pairs if p.id == report.pair_id), None
    ):
        raise ValueError("Report pair changed; compare again.")
    return snapshot


def reproduce(root, dataset, report: Report):
    if report.implementation_sha256 != implementation_hash():
        raise ValueError(
            "Comparison implementation changed; compare again using cached Phase 2 artifacts."
        )
    dataset = bound_dataset(root, dataset, report)
    evidence = []
    for member in report.inputs:
        feature_path = managed_path(root, member.features.path)
        alignment_path = managed_path(root, member.alignment.path) if member.alignment else None
        loaded = load_evidence(
            root,
            dataset,
            feature_path,
            alignment_path,
            [managed_path(root, ref.path) for ref in member.reviews],
        )
        if loaded.summary() != member:
            raise ValueError("Upstream feature/alignment/review reference changed.")
        evidence.append(loaded)
    if not 1 <= len(evidence) <= 2:
        raise ValueError("Comparison needs one reference and optional participant.")
    pair = next((p for p in dataset.pairs if p.id == report.pair_id), None)
    rebuilt = compare(
        evidence[0],
        evidence[1] if len(evidence) == 2 else None,
        pair,
        report.policy,
        content_hash(dataset.model_dump(mode="json")),
        implementation_hash(),
    )
    if rebuilt != report:
        raise ValueError("Comparison replay differs.")
    return rebuilt
