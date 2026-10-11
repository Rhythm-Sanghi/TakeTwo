"""Analysis CLI: actual processing and explicit unavailable alignment states."""

import json
import sys
from pathlib import Path

from pydantic import ValidationError

from taketwo.dataset.cli import Parser
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import canonical_json
from taketwo.dataset.storage import managed_path, read_json, safe_path, workspace_lock, write_new

from .alignment import align, execute, prerequisites
from .contracts import AlignmentConfig, AlignmentResult, FeatureConfig, FeatureResult
from .features import extract
from .storage import publish, read_artifact, recording_input, validate_identity


def parser():
    result = Parser(description="TakeTwo - Speech analysis workspace acoustic tools")
    commands = result.add_subparsers(dest="command", required=True, parser_class=Parser)
    check = commands.add_parser("check")
    check.add_argument("--config", type=Path, required=True)
    for name in ("align", "extract", "inspect", "validate", "export"):
        command = commands.add_parser(name)
        command.add_argument("workspace", type=Path)
        if name in {"align", "extract"}:
            command.add_argument("--recording", required=True)
            command.add_argument("--config", type=Path, required=name == "align")
            if name == "extract":
                command.add_argument("--alignment", type=Path)
        else:
            command.add_argument("--artifact", type=Path, required=True)
        if name == "validate":
            command.add_argument("--reproduce", action="store_true")
            command.add_argument("--alignment", type=Path)
        if name == "export":
            command.add_argument("--output", type=Path, required=True)
    return result


def config_file(path, contract):
    return contract.model_validate_json(canonical_json(read_json(path)))


def run(args):
    if args.command == "check":
        import tempfile

        config = config_file(args.config, AlignmentConfig)
        issues = prerequisites(config)
        version = None
        if not issues:
            with tempfile.TemporaryDirectory(prefix="taketwo-check-") as directory:
                state, version, code = execute([*config.command, "version"], Path(directory), 30)
            if state != "succeeded" or code or config.expected_version != version.strip():
                return {
                    "ready": False,
                    "backend_version": version,
                    "reason": "Version/execution failed",
                }, 1
        return {
            "ready": not issues,
            "backend_version": version,
            "diagnostics": [d.model_dump(mode="json") for d in issues],
        }, 1 if issues else 0
    root = safe_path(args.workspace)
    if args.command in {"align", "extract"}:
        with workspace_lock(root):
            recording, samples, provenance = recording_input(root, args.recording)
            if args.command == "align":
                result = align(
                    managed_path(root, recording.normalized_path),
                    recording.transcript.text,
                    provenance,
                    len(samples) / 16000,
                    config_file(args.config, AlignmentConfig),
                )
            else:
                alignment = read_artifact(args.alignment) if args.alignment else None
                if alignment is not None and not isinstance(alignment, AlignmentResult):
                    raise ValueError("Expected an alignment artifact.")
                config = config_file(args.config, FeatureConfig) if args.config else FeatureConfig()
                result = extract(samples, provenance, config, alignment)
            path = publish(root, result)
        status = result.status if isinstance(result, AlignmentResult) else "extracted"
        return {"artifact": str(path), "status": status}, 0 if status in {
            "extracted",
            "succeeded",
        } else 1
    result = read_artifact(args.artifact)
    validate_identity(root, result)
    if args.command == "validate" and args.reproduce:
        if not isinstance(result, FeatureResult):
            raise ValueError(
                "Use align for a fresh backend run; exact alignment logs are not replay fixtures."
            )
        _, samples, provenance = recording_input(root, result.provenance.recording_id)
        alignment = read_artifact(args.alignment) if args.alignment else None
        if alignment is not None and not isinstance(alignment, AlignmentResult):
            raise ValueError("Expected alignment artifact.")
        rebuilt = extract(samples, provenance, result.config, alignment)
        if rebuilt != result:
            raise ValueError("Feature replay differs; include the original alignment if used.")
    if args.command == "export":
        write_new(
            safe_path(args.output),
            (canonical_json(result.model_dump(mode="json")) + "\n").encode("utf-8"),
        )
        return {"exported": str(args.output)}, 0
    return {
        "valid": True,
        "kind": result.kind,
        "schema_version": 1,
        "provenance": result.provenance.model_dump(mode="json"),
        "quality": result.quality.model_dump(mode="json")
        if isinstance(result, FeatureResult)
        else None,
        "status": result.status if isinstance(result, AlignmentResult) else "extracted",
    }, 0


def main(argv=None):
    try:
        payload, status = run(parser().parse_args(argv))
        print(json.dumps(payload, sort_keys=True, ensure_ascii=True, allow_nan=False))
        return status
    except KeyboardInterrupt:
        error = DatasetError(
            "cancelled", "Interrupted by user; subprocess cleaned up.", "Retry when ready."
        )
    except (DatasetError, ValidationError, OSError, ValueError, TypeError) as exc:
        error = (
            exc
            if isinstance(exc, DatasetError)
            else DatasetError("analysis_input", str(exc), "Review inputs and diagnostics.")
        )
    print(json.dumps({"error": error.as_dict()}, ensure_ascii=True), file=sys.stderr)
    return 130 if error.code == "cancelled" else 2


if __name__ == "__main__":
    sys.exit(main())
