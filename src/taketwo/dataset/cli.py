"""PowerShell-friendly CLI. Success is JSON on stdout; errors are JSON on stderr."""

import argparse
import json
import sys
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from .errors import DatasetError
from .schema import Annotation, Dataset, ImportSpec, Recipe, canonical_json
from .storage import load, read_json, safe_path, write_new
from .validation import validate
from .workspace import (
    add_annotations,
    assign_splits,
    generate,
    import_recording,
    initialize,
    summary,
)


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise DatasetError("arguments", message, "Run the command with --help.")


def parser() -> argparse.ArgumentParser:
    result = Parser(description="TakeTwo — Speech analysis workspace dataset tools")
    commands = result.add_subparsers(dest="command", required=True, parser_class=Parser)
    init = commands.add_parser("init", help="Create a new versioned workspace")
    init.add_argument("workspace", type=Path)
    init.add_argument("--version", required=True)
    for name in ("import-reference", "import-flawed"):
        command = commands.add_parser(name)
        command.add_argument("workspace", type=Path)
        command.add_argument("--audio", type=Path, required=True)
        command.add_argument("--metadata", type=Path, required=True)
        if name == "import-flawed":
            command.add_argument("--reference", required=True)
            command.add_argument("--category", required=True)
            command.add_argument("--severity", type=int, choices=range(4), required=True)
    generated = commands.add_parser("generate")
    generated.add_argument("workspace", type=Path)
    generated.add_argument("--reference", required=True)
    generated.add_argument("--recipe", type=Path, required=True)
    annotated = commands.add_parser("annotate")
    annotated.add_argument("workspace", type=Path)
    annotated.add_argument("--annotations", type=Path, required=True)
    split = commands.add_parser("split")
    split.add_argument("workspace", type=Path)
    split.add_argument("--seed", type=int, required=True)
    split.add_argument("--ratios", nargs=3, type=float, default=[0.5, 0.25, 0.25])
    checked = commands.add_parser("validate")
    checked.add_argument("workspace", type=Path)
    checked.add_argument("--publication", action="store_true")
    checked.add_argument("--reproduce", action="store_true")
    exported = commands.add_parser("export")
    exported.add_argument("workspace", type=Path)
    exported.add_argument("--output", type=Path, required=True)
    commands.add_parser("schema", help="Print the version 1 dataset JSON Schema")
    return result


def run(args: argparse.Namespace) -> tuple[dict, int]:
    if args.command == "schema":
        return Dataset.model_json_schema(), 0
    root = safe_path(args.workspace)
    if args.command == "init":
        return summary(initialize(root, args.version)), 0
    if args.command in {"import-reference", "import-flawed"}:
        spec = ImportSpec.model_validate_json(canonical_json(read_json(args.metadata)))
        recording = import_recording(
            root,
            args.audio,
            spec,
            reference_id=getattr(args, "reference", None),
            category=getattr(args, "category", "acceptable"),
            severity=getattr(args, "severity", 0),
        )
        return {
            "recording_id": recording.id,
            "quality_flags": recording.quality_flags,
            "transcript_status": recording.transcript.status,
        }, 0
    if args.command == "generate":
        recipe = Recipe.model_validate_json(canonical_json(read_json(args.recipe)))
        recording = generate(root, args.reference, recipe)
        return {
            "recording_id": recording.id,
            "origin": recording.origin,
            "labels": "synthetic_recipe; unreviewed",
        }, 0
    if args.command == "annotate":
        annotations = TypeAdapter(list[Annotation]).validate_json(
            canonical_json(read_json(args.annotations))
        )
        if not annotations:
            raise DatasetError(
                "empty_annotations", "No annotations supplied.", "Provide a nonempty JSON list."
            )
        add_annotations(root, annotations)
        return {"added": len(annotations)}, 0
    if args.command == "split":
        return assign_splits(root, args.seed, tuple(args.ratios)), 0
    dataset = load(root)
    report = validate(
        dataset,
        root,
        publication=getattr(args, "publication", False),
        reproduce=getattr(args, "reproduce", False),
    )
    if args.command == "validate":
        return report, 0 if report["valid"] else 1
    if not report["valid"]:
        return report, 1
    payload = {
        "dataset": dataset.model_dump(mode="json"),
        "summary": summary(dataset),
        "validation": report,
    }
    write_new(safe_path(args.output), (canonical_json(payload) + "\n").encode("utf-8"))
    return {"exported": args.output.name, "summary": summary(dataset)}, 0


def main(argv: list[str] | None = None) -> int:
    try:
        payload, status = run(parser().parse_args(argv))
        print(json.dumps(payload, sort_keys=True, ensure_ascii=True, allow_nan=False))
        return status
    except DatasetError as exc:
        error = exc.as_dict()
    except ValidationError as exc:
        error = DatasetError(
            "schema", "Metadata does not match dataset schema.", "Correct the listed fields."
        ).as_dict()
        error["fields"] = [
            {"location": list(item["loc"]), "message": item["msg"]} for item in exc.errors()
        ]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        error = DatasetError(
            "input_io", str(exc), "Check file paths, permissions and JSON syntax."
        ).as_dict()
    print(json.dumps({"error": error}, sort_keys=True, ensure_ascii=True), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
