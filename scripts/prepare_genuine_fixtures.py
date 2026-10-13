"""Copy authorized private inputs to an explicitly selected private browser fixture kit."""

import argparse
import shutil
from pathlib import Path

from taketwo.dataset.storage import load, managed_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot", type=Path)
    parser.add_argument("--review-workspace", type=Path)
    parser.add_argument("--duration-workspace", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--transcript", type=Path)
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    try:
        relative = args.output.resolve().relative_to(repository)
    except ValueError:
        pass  # External private fixture kit.
    else:
        if not relative.parts or relative.parts[0] != "local-data":
            parser.error("In-repository private fixture kits must stay under ignored local-data")
    copies = []
    if args.pilot:
        copies.extend(
            (args.pilot / (name + ".wav"), Path("pilot") / (name + ".wav"))
            for name in ("reference", "natural", "slow", "uneven", "near-perfect")
        )
    for source, name in [
        (args.review_workspace, "review-workspace"),
        (args.duration_workspace, "duration-workspace"),
    ]:
        if source:
            dataset = load(source)
            if not dataset.recordings:
                parser.error(f"No recordings in fixture workspace: {source}")
            copies.append((source / "manifest.jsonl", Path(name) / "manifest.jsonl"))
            # Copy only manifest-bound audio, never incidental files in these
            # directories (databases, staging files or private review material).
            for relative in sorted(
                {p for r in dataset.recordings for p in (r.original_path, r.normalized_path)}
            ):
                copies.append((managed_path(source, relative), Path(name) / relative))
    if bool(args.archive) != bool(args.transcript):
        parser.error("--archive and --transcript must be supplied together")
    if args.archive:
        copies.extend(
            [(args.archive, Path("archive.wav")), (args.transcript, Path("transcript.txt"))]
        )
    if not copies:
        parser.error("Select at least one authorized fixture source")
    for source, _ in copies:
        if not source.exists():
            parser.error(f"Missing fixture input: {source}")
    # No overwrites. Keep this directory external or under ignored local-data.
    args.output.mkdir(parents=True, exist_ok=False)
    for source, relative in copies:
        target = args.output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    print("Prepared private input copies only; no reviews, history, databases or caches copied.")


if __name__ == "__main__":
    main()
