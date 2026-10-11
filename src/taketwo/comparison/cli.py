"""TakeTwo scientific CLI: operational failures and evidence abstention are distinct."""

import json
import sys
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from taketwo.analysis.contracts import AlignmentResult
from taketwo.analysis.storage import read_artifact as read_analysis
from taketwo.analysis.storage import recording_input, validate_identity
from taketwo.dataset.cli import Parser
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import canonical_json, content_hash
from taketwo.dataset.storage import load, read_json, safe_path, workspace_lock, write_new
from taketwo.dataset.workspace import check_dataset, find_recording

from .contracts import Evaluation, EvaluationConfig, Policy, Report, Review
from .engine import compare
from .evaluation import evaluate
from .reviews import validate_review
from .storage import implementation_hash, load_evidence, publish, read_artifact, reproduce


def parser():
    result = Parser(description="TakeTwo - Speech analysis workspace comparison and review tools")
    commands = result.add_subparsers(dest="command", required=True, parser_class=Parser)
    commands.add_parser("schema")
    for name in (
        "compare",
        "detect",
        "score",
        "evidence",
        "import-review",
        "inspect",
        "validate",
        "evaluate",
        "export",
    ):
        command = commands.add_parser(name)
        command.add_argument("workspace", type=Path)
        if name in {"compare", "detect", "score", "evidence"}:
            command.add_argument("--reference-features", type=Path, required=True)
            command.add_argument("--reference-alignment", type=Path)
            command.add_argument("--participant-features", type=Path)
            command.add_argument("--participant-alignment", type=Path)
            command.add_argument("--pair")
            command.add_argument("--review", type=Path, action="append", default=[])
            command.add_argument("--policy", type=Path)
        elif name == "import-review":
            command.add_argument("--review", type=Path, required=True)
            command.add_argument("--alignment", type=Path)
        elif name == "evaluate":
            command.add_argument("--report", type=Path, action="append", default=[])
            command.add_argument("--review", type=Path, action="append", default=[])
            command.add_argument("--config", type=Path)
        else:
            command.add_argument("--artifact", type=Path, required=True)
            if name == "validate":
                command.add_argument("--reproduce", action="store_true")
            if name == "export":
                command.add_argument("--output", type=Path, required=True)
    return result


def schema():
    return TypeAdapter(Report | Review | Evaluation).json_schema()


def model_file(path, contract):
    return contract.model_validate_json(canonical_json(read_json(path)))


def run(args):
    if args.command == "schema":
        return schema(), 0
    root = safe_path(args.workspace)
    dataset = load(root)
    if args.command in {"compare", "detect", "score", "evidence"}:
        if bool(args.participant_features) != bool(args.pair) or (
            args.participant_alignment and not args.participant_features
        ):
            raise ValueError("Participant features and existing pair ID must be supplied together.")
        pair = next((p for p in dataset.pairs if p.id == args.pair), None)
        if args.pair and pair is None:
            raise ValueError("Pair ID does not exist.")
        with workspace_lock(root):
            check_dataset(dataset, root)
            reference = load_evidence(
                root, dataset, args.reference_features, args.reference_alignment, args.review
            )
            participant = (
                load_evidence(
                    root,
                    dataset,
                    args.participant_features,
                    args.participant_alignment,
                    args.review,
                )
                if args.participant_features
                else None
            )
            policy = model_file(args.policy, Policy) if args.policy else Policy()
            result = compare(
                reference,
                participant,
                pair,
                policy,
                content_hash(dataset.model_dump(mode="json")),
                implementation_hash(),
            )
            path = publish(root, result)
        payload = {
            "artifact": str(path),
            "eligibility": result.eligibility.model_dump(mode="json"),
            "overall_score": result.overall_score,
            "region_count": len(result.regions),
            "dimensions": [d.model_dump(mode="json") for d in result.dimensions],
        }
        if args.command == "detect":
            payload["regions"] = [r.model_dump(mode="json") for r in result.regions]
        if args.command == "evidence":
            payload["feature_eligibility"] = {
                k: v.model_dump(mode="json") for k, v in result.feature_eligibility.items()
            }
            payload["observations"] = [o.model_dump(mode="json") for o in result.observations]
            payload["inputs"] = [i.model_dump(mode="json") for i in result.inputs]
        return payload, 0 if result.overall_score is not None else 3
    if args.command == "import-review":
        review = model_file(args.review, Review)
        recording = find_recording(dataset, review.provenance.recording_id)
        _, _, provenance = recording_input(root, recording.id)
        if review.provenance != provenance:
            raise ValueError(
                "Review provenance differs from current recording/analysis implementation."
            )
        alignment = read_analysis(args.alignment) if args.alignment else None
        if alignment is not None:
            if not isinstance(alignment, AlignmentResult):
                raise ValueError("Expected alignment artifact.")
            validate_identity(root, alignment)
        validate_review(review, recording, alignment)
        if review.scope == "flaws" and not any(
            p.id == review.pair_id and p.participant_id == recording.id for p in dataset.pairs
        ):
            raise ValueError("Review pair does not identify this participant.")
        with workspace_lock(root):
            path = publish(root, review)
        return {
            "artifact": str(path),
            "decision": review.decision,
            "independent_assertion": review.independent,
            "notice": "Stored reviewer assertion; import does not certify independence "
            "or grant approval.",
        }, 0
    if args.command == "evaluate":
        reports = [read_artifact(path) for path in args.report]
        if any(not isinstance(r, Report) for r in reports):
            raise ValueError("Expected comparison reports.")
        reviews = [read_artifact(path) for path in args.review]
        if any(not isinstance(r, Review) for r in reviews):
            raise ValueError("Expected review artifacts.")
        with workspace_lock(root):
            check_dataset(dataset, root)
            for report in reports:
                reproduce(root, dataset, report)
            for review in reviews:
                validate_review(
                    review, find_recording(dataset, review.provenance.recording_id), None
                )
            config = (
                model_file(args.config, EvaluationConfig) if args.config else EvaluationConfig()
            )
            result = evaluate(dataset, reports, reviews, config, implementation_hash())
            path = publish(root, result)
        return {
            "artifact": str(path),
            "evaluation": result.model_dump(mode="json"),
        }, 0 if result.metrics else 3
    result = read_artifact(args.artifact)
    if args.command == "validate" and args.reproduce:
        if not isinstance(result, Report):
            raise ValueError(
                "Replay is available for comparison reports; evaluate again for evaluation replay."
            )
        reproduce(root, dataset, result)
    if args.command == "export":
        write_new(
            safe_path(args.output),
            (canonical_json(result.model_dump(mode="json")) + "\n").encode("utf-8"),
        )
        return {"exported": str(args.output)}, 0
    return {
        "valid_structure": True,
        "kind": result.kind,
        "result": result.model_dump(mode="json"),
        "notice": "Structural validity alone is not scientific eligibility "
        "or reviewer authentication.",
    }, 0


def main(argv=None):
    try:
        payload, status = run(parser().parse_args(argv))
        print(json.dumps(payload, sort_keys=True, ensure_ascii=True, allow_nan=False))
        return status
    except KeyboardInterrupt:
        error = DatasetError("cancelled", "Interrupted; no result claimed.", "Retry when ready.")
    except (DatasetError, ValidationError, OSError, ValueError, TypeError, KeyError) as exc:
        error = (
            exc
            if isinstance(exc, DatasetError)
            else DatasetError(
                "comparison_input", str(exc), "Review inputs, hashes and evidence diagnostics."
            )
        )
    print(json.dumps({"error": error.as_dict()}, ensure_ascii=True), file=sys.stderr)
    return 130 if error.code == "cancelled" else 2


if __name__ == "__main__":
    sys.exit(main())
