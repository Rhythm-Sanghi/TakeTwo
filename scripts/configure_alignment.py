"""Write local MFA configuration only after checking downloaded model/dictionary hashes."""

import argparse
import json
from pathlib import Path

from taketwo.analysis.contracts import AlignmentConfig, Resource
from taketwo.dataset.audio import sha256
from taketwo.dataset.schema import canonical_json
from taketwo.dataset.storage import read_json, safe_path, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    lock = read_json(Path(__file__).resolve().parents[1] / "environments/mfa-models.json")
    resources = {}
    for kind, folder in [("model", "acoustic"), ("dictionary", "dictionary")]:
        item = dict(lock[kind])
        path = safe_path(args.models / folder / item.pop("filename"))
        if sha256(path.read_bytes()) != item["sha256"]:
            raise ValueError(f"{kind} does not match the reviewed artifact lock")
        resources[kind] = Resource(path=str(path), **item)
    config = AlignmentConfig(
        command=[str(safe_path(args.prefix / "Scripts/mfa.exe"))],
        expected_version=lock["backend_version"],
        timeout_s=180.0,
        replacements={"mr": "mister"},
        **resources,
    )
    write_new(
        safe_path(args.output), (canonical_json(config.model_dump(mode="json")) + "\n").encode()
    )
    print(json.dumps({"configured": str(args.output)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
