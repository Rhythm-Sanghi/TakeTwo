"""Read-only preflight of an actual exported reviewer file; never imports or approves."""

import argparse
import json
from pathlib import Path

from pydantic import ValidationError

from taketwo.analysis.contracts import AlignmentResult
from taketwo.analysis.storage import read_artifact, recording_input, validate_identity
from taketwo.comparison.contracts import Review
from taketwo.comparison.reviews import validate_review
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import canonical_json
from taketwo.dataset.storage import load, read_json


def check(root, review_path, alignment_path=None):
    review = Review.model_validate_json(canonical_json(read_json(review_path)))
    recording, _, provenance = recording_input(root, review.provenance.recording_id)
    if review.provenance != provenance:
        raise ValueError("Review provenance differs from current recording and implementation.")
    alignment = read_artifact(alignment_path) if alignment_path else None
    if alignment is not None:
        if not isinstance(alignment, AlignmentResult):
            raise ValueError("Expected an original alignment artifact.")
        validate_identity(root, alignment)
    validate_review(review, recording, alignment)
    if review.scope == "flaws" and not any(
        pair.id == review.pair_id and pair.participant_id == recording.id
        for pair in load(root).pairs
    ):
        raise ValueError("Review pair does not identify this participant.")
    return {
        "valid_structure_and_identity": True,
        "scope": review.scope,
        "recording_id": recording.id,
        "dataset_version": review.provenance.dataset_version,
        "imported": False,
        "notice": "Does not authenticate a reviewer, certify independence, approve evidence "
        "or establish scientific eligibility. Import uses the existing validators again.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--alignment", type=Path)
    args = parser.parse_args()
    try:
        result = check(args.workspace, args.review, args.alignment)
    except (ValidationError, DatasetError, ValueError, OSError):
        # Do not echo private reviewer content or filesystem paths in errors.
        print(
            json.dumps(
                {
                    "error": "Review preflight failed. Check the strict Review contract, "
                    "current source identity and original alignment. Nothing was imported."
                }
            )
        )
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
