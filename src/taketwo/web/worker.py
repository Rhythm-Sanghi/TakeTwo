"""One disposable process invokes unchanged engines; no HTTP or fake results."""

import os
import sys
import time
from pathlib import Path

# No engine import or descendant process may precede kernel job assignment.
# If the parent dies before assignment/gate publication, exit without doing any work.
if __name__ == "__main__" and os.environ.get("TAKETWO_WORKER_GATE"):
    deadline = time.monotonic() + 5
    while not Path(os.environ["TAKETWO_WORKER_GATE"]).exists():
        if time.monotonic() >= deadline:
            sys.exit(130)
        time.sleep(0.01)

from taketwo.analysis.alignment import align
from taketwo.analysis.contracts import (
    AlignmentConfig,
    AlignmentResult,
    FeatureConfig,
    FeatureResult,
)
from taketwo.analysis.features import extract
from taketwo.analysis.limits import maximum_analysis_duration_s
from taketwo.analysis.storage import publish as publish_analysis
from taketwo.analysis.storage import read_artifact as read_analysis
from taketwo.analysis.storage import recording_input, validate_identity
from taketwo.comparison.contracts import Policy, Review
from taketwo.comparison.engine import compare
from taketwo.comparison.storage import implementation_hash, load_evidence, publish, read_artifact
from taketwo.dataset.schema import canonical_json, content_hash
from taketwo.dataset.storage import load, managed_path, read_json, write_new
from taketwo.dataset.workspace import check_dataset

from .contracts import AnalysisRequest


def atomic_json(path: Path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(canonical_json(value), encoding="utf-8")
    # Windows readers may hold the destination without FILE_SHARE_DELETE briefly.
    # Retry only this transient sharing violation; never expose a partial state file.
    for attempt in range(20):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.05)


def publish_complete(root, temporary, result):
    """Link only a completely written artifact; interruption cannot expose partial JSON."""
    writer = publish_analysis if isinstance(result, FeatureResult | AlignmentResult) else publish
    staged = writer(temporary, result)
    target = managed_path(root, staged.relative_to(temporary).as_posix())
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(staged, target)
    except FileExistsError:
        if target.read_bytes() != staged.read_bytes():
            raise ValueError("Existing content-addressed artifact differs.") from None
    return target


def cached(root, recording_id, contract, config, alignment_hash=None):
    directory = managed_path(root, f"derived/v1/{recording_id}")
    for path in sorted(directory.glob("*.json")):
        try:
            result = read_analysis(path)
            if not isinstance(result, contract) or result.config != config:
                continue
            validate_identity(root, result)
            if isinstance(result, AlignmentResult) and result.status != "succeeded":
                continue
            if isinstance(result, FeatureResult) and result.alignment_sha256 != alignment_hash:
                continue
            return path, result
        except (ValueError, OSError):
            continue
    return None, None


def run(root: Path, temporary: Path, request: AnalysisRequest, alignment_config: Path | None):
    previous, started = None, time.monotonic()
    timings, hits = {}, []

    def stage(name):
        nonlocal previous, started
        now = time.monotonic()
        if previous:
            timings[previous] = now - started
        previous, started = name, now
        atomic_json(temporary / "stage.json", {"stage": name})

    stage("validating")
    dataset = load(root)
    check_dataset(dataset, root)
    pair = next((p for p in dataset.pairs if p.id == request.pair_id), None)
    members = [request.reference_id] + ([pair.participant_id] if pair else [])
    config = (
        AlignmentConfig.model_validate_json(canonical_json(read_json(alignment_config)))
        if alignment_config
        else None
    )
    artifacts, evidence = {}, []
    review_paths = []
    for path in managed_path(root, "derived/comparison-v1").glob("review-*.json"):
        review = read_artifact(path)
        if isinstance(review, Review) and review.scope != "flaws":
            review_paths.append(path)
    for rid in members:
        recording, samples, provenance = recording_input(root, rid)
        if len(samples) > maximum_analysis_duration_s() * 16000:
            raise ValueError(
                f"Analysis supports excerpts up to {maximum_analysis_duration_s()} seconds; "
                "import a shorter excerpt."
            )
        alignment_path, alignment = None, None
        if request.align and config:
            stage(f"aligning {recording.role}")
            alignment_path, alignment = cached(root, rid, AlignmentResult, config)
            if alignment is not None:
                hits.append(f"alignment:{rid}")
            if alignment is None:
                alignment = align(
                    managed_path(root, recording.normalized_path),
                    recording.transcript.text,
                    provenance,
                    len(samples) / 16000,
                    config,
                )
                alignment_path = publish_complete(root, temporary, alignment)
        stage(f"extracting {recording.role}")
        alignment_hash = content_hash(alignment.model_dump(mode="json")) if alignment else None
        feature_path, features = cached(root, rid, FeatureResult, FeatureConfig(), alignment_hash)
        if features is not None:
            hits.append(f"features:{rid}")
        if features is None:
            features = extract(samples, provenance, FeatureConfig(), alignment)
            feature_path = publish_complete(root, temporary, features)
        artifacts[rid] = {"features": feature_path.relative_to(root).as_posix()}
        if alignment_path:
            artifacts[rid]["alignment"] = alignment_path.relative_to(root).as_posix()
        atomic_json(temporary / "artifacts.json", artifacts)
        evidence.append(load_evidence(root, dataset, feature_path, alignment_path, review_paths))
    stage("comparing and scoring")
    report = compare(
        evidence[0],
        evidence[1] if len(evidence) == 2 else None,
        pair,
        Policy(),
        content_hash(dataset.model_dump(mode="json")),
        implementation_hash(),
    )
    # Retain the exact dataset context without making unrelated future imports stale inputs.
    snapshot = (canonical_json(dataset.model_dump(mode="json")) + "\n").encode("utf-8")
    staged = temporary / "dataset-snapshot.json"
    write_new(staged, snapshot)
    target = managed_path(root, f"derived/comparison-v1/dataset-{report.dataset_sha256}.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(staged, target)
    except FileExistsError:
        if target.read_bytes() != snapshot:
            raise ValueError("Dataset snapshot differs; existing evidence was preserved.") from None
    path = publish_complete(root, temporary, report)
    stage("completed")
    atomic_json(
        temporary / "result.json",
        {
            "report_path": path.relative_to(root).as_posix(),
            "artifacts": artifacts,
            "stage_elapsed_s": timings,
            "cache_hits": hits,
        },
    )


if __name__ == "__main__":
    root, temporary = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        request = AnalysisRequest.model_validate_json((temporary / "request.json").read_text())
        run(root, temporary, request, Path(sys.argv[3]) if len(sys.argv) == 4 else None)
    except Exception as exc:
        # Keep private transcript/audio and backend log contents out of service logs.
        atomic_json(
            temporary / "error.json",
            {
                "code": "processing_failed",
                "message": f"CPU processing stopped ({type(exc).__name__}).",
                "recovery": "Validate dataset and alignment prerequisites with the CLI; "
                "completed artifacts are retained.",
            },
        )
        sys.exit(1)
