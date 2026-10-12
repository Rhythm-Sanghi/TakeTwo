"""Cross-record and artifact validation, with a stricter publication gate."""

import math
from pathlib import Path

import numpy as np

from .audio import RATE, decode, normalize, quality, sample_hash, sha256, versions
from .errors import DatasetError
from .schema import Dataset, content_hash, tokenize
from .splits import connected_groups, make_split
from .storage import managed_path
from .transform import CATEGORIES, apply_recipe


def validate(
    dataset: Dataset, root: Path, *, publication: bool = False, reproduce: bool = False
) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []

    def issue(code: str, message: str, affected: str, *, warning: bool = False) -> None:
        target = warnings if warning else errors
        target.append(
            DatasetError(
                code, message, "Repair/review the identified manifest record or artifact.", affected
            ).as_dict()
        )

    for collection in (dataset.recordings, dataset.pairs, dataset.annotations):
        seen: set[str] = set()
        for item in collection:
            if item.id in seen:
                issue("duplicate_id", "Duplicate identifier.", item.id)
            seen.add(item.id)
    recordings = {r.id: r for r in dataset.recordings}
    pairs = {p.id: p for p in dataset.pairs}
    annotations = {a.id: a for a in dataset.annotations}
    hashes: dict[str, str] = {}
    for recording in dataset.recordings:
        rid = recording.id
        if recording.dataset_version != dataset.dataset_version:
            issue("dataset_version", "Recording dataset version differs from header.", rid)
        tokens, offsets = tokenize(recording.transcript.text)
        if (
            tokens != recording.tokens
            or offsets != recording.token_offsets
            or content_hash(tokens) != recording.transcript_sha256
        ):
            issue("transcript_hash", "Transcript tokens/hash/offsets disagree.", rid)
        if recording.transcript.status != "verified":
            issue(
                "transcript_review",
                "Transcript has not been verified by two reviewers.",
                rid,
                warning=not publication,
            )
        if recording.provenance.rights.status != "cleared":
            issue(
                "rights_pending",
                "Adaptation/publication rights are pending.",
                rid,
                warning=not publication,
            )
        if recording.origin == "self_recorded" and not recording.provenance.consent_evidence:
            issue("consent", "Human recording requires a consent evidence reference.", rid)
        if recording.role == "reference":
            if (
                recording.origin not in {"source", "self_recorded"}
                or not recording.provenance.baseline_rationale
            ):
                issue(
                    "reference_provenance",
                    "Reference needs genuine source/self-recorded origin and selection rationale.",
                    rid,
                )
        if recording.origin == "synthetic" and not recording.transformation:
            issue(
                "transformation_missing",
                "Synthetic recording requires a transformation record.",
                rid,
            )
        if recording.origin != "synthetic" and recording.transformation:
            issue("origin", "Only synthetic recordings may contain transformations.", rid)
        if (
            recording.processing.channel is not None
            and recording.processing.channel >= recording.original_info.channels
        ):
            issue("processing_channel", "Selected channel does not exist in original audio.", rid)
        if recording.role == "participant" and not any(
            p.participant_id == rid for p in dataset.pairs
        ):
            issue("pair_missing", "Participant has no reference pair.", rid)
        required_versions = set(versions())
        if not required_versions <= recording.processing.versions.keys():
            issue("processing_versions", "Missing processing software versions.", rid)
        elif recording.processing.versions != versions():
            issue(
                "environment_drift",
                "Processing environment differs from this runtime.",
                rid,
                warning=not reproduce,
            )
        try:
            expected_original = f"originals/{rid}." + recording.original_info.format.lower()
            if (
                recording.original_path != expected_original
                or recording.normalized_path != f"normalized/{rid}.wav"
            ):
                issue(
                    "artifact_path",
                    "Managed artifact path does not match recording ID/container.",
                    rid,
                )
            original_path = managed_path(root, recording.original_path)
            normalized_path = managed_path(root, recording.normalized_path)
            original_data = original_path.read_bytes()
            normalized_data = normalized_path.read_bytes()
            if sha256(original_data) != recording.original_sha256:
                issue("original_hash", "Original audio hash mismatch.", rid)
            if sha256(normalized_data) != recording.normalized_sha256:
                issue("normalized_hash", "Normalized audio hash mismatch.", rid)
            original, original_info = decode(original_data)
            normalized_2d, normalized_info = decode(normalized_data)
            for label, actual, stored in (
                ("original", original_info, recording.original_info),
                ("normalized", normalized_info, recording.normalized_info),
            ):
                for field, value in actual.model_dump().items():
                    saved = getattr(stored, field)
                    equal = (
                        math.isclose(value, saved, abs_tol=1e-7)
                        if isinstance(value, float)
                        else value == saved
                    )
                    if not equal:
                        issue(
                            "audio_metadata", f"{label} {field} does not match decoded audio.", rid
                        )
            if (
                normalized_info.sample_rate_hz != RATE
                or normalized_info.channels != 1
                or normalized_info.subtype != "FLOAT"
                or normalized_info.format != "WAV"
            ):
                issue("canonical_audio", "Expected mono 16 kHz float32 WAV derivative.", rid)
            actual_sample_hash = sample_hash(normalized_2d[:, 0])
            if actual_sample_hash != recording.sample_sha256:
                issue("sample_hash", "Canonical sample hash mismatch.", rid)
            if actual_sample_hash in hashes:
                issue(
                    "duplicate_audio",
                    f"Same canonical samples as {hashes[actual_sample_hash]}.",
                    rid,
                )
            hashes[actual_sample_hash] = rid
            flags = sorted(set(quality(original_info) + quality(normalized_info)))
            if flags != sorted(recording.quality_flags):
                issue("quality_metadata", "Quality flags differ from decoded audio.", rid)
            if flags:
                issue(
                    "audio_quality", f"Audio needs review: {flags}.", rid, warning=not publication
                )
            if reproduce:
                rebuilt = normalize(
                    original, original_info.sample_rate_hz, recording.processing.channel
                )
                if rebuilt.shape != normalized_2d[:, 0].shape or not np.allclose(
                    rebuilt, normalized_2d[:, 0], rtol=0, atol=1e-6
                ):
                    issue(
                        "normalization_replay",
                        "Normalization does not reproduce saved samples.",
                        rid,
                    )
        except (OSError, DatasetError) as exc:
            issue("artifact_error", str(exc), rid)
        if recording.transformation:
            transformation = recording.transformation
            parent = recordings.get(transformation.parent_id)
            if not parent:
                issue("parent_missing", "Transformation parent is missing.", rid)
                continue
            if parent.origin == "synthetic":
                issue("synthetic_chain", "Nested synthetic parents are not supported in v1.", rid)
            if (
                transformation.source_sha256 != parent.normalized_sha256
                or transformation.recipe_sha256
                != content_hash(transformation.recipe.model_dump(mode="json"))
                or recording.transcript_sha256 != parent.transcript_sha256
                or recording.family_id != parent.family_id
                or recording.speaker_id != parent.speaker_id
                or recording.provenance != parent.provenance
            ):
                issue(
                    "transformation_provenance",
                    "Parent, recipe, transcript or inherited provenance differs.",
                    rid,
                )
            if transformation.versions != recording.processing.versions:
                issue(
                    "transformation_versions",
                    "Transformation and processing environments differ.",
                    rid,
                )
            if parent.role != "reference" or recording.role != "participant":
                issue("transformation_role", "Recipe must link a reference to a participant.", rid)
            source_cursor = output_cursor = 0
            for segment in transformation.time_map:
                if (
                    segment.source_start != source_cursor
                    or segment.output_start != output_cursor
                    or segment.source_end < segment.source_start
                    or segment.output_end <= segment.output_start
                    or (segment.kind == "inserted") != (segment.source_start == segment.source_end)
                ):
                    issue("time_map", "Noncontiguous or invalid sample time map.", rid)
                if segment.kind == "unchanged" and (
                    segment.source_end - segment.source_start
                    != segment.output_end - segment.output_start
                ):
                    issue("time_map", "Unchanged segment changes duration.", rid)
                source_cursor, output_cursor = segment.source_end, segment.output_end
            if (
                source_cursor != parent.normalized_info.frames
                or output_cursor != recording.normalized_info.frames
            ):
                issue("time_map", "Time map does not cover parent and derivative.", rid)
            if reproduce:
                try:
                    parent_audio, _ = decode(
                        managed_path(root, parent.normalized_path).read_bytes()
                    )
                    rebuilt, time_map, _ = apply_recipe(parent_audio[:, 0], transformation.recipe)
                    actual, _ = decode(managed_path(root, recording.normalized_path).read_bytes())
                    if (
                        time_map != transformation.time_map
                        or rebuilt.shape != actual[:, 0].shape
                        or not np.allclose(rebuilt, actual[:, 0], atol=1e-6, rtol=0)
                    ):
                        issue(
                            "transform_replay",
                            "Recipe does not reproduce saved audio/time map.",
                            rid,
                        )
                except (OSError, DatasetError) as exc:
                    issue("transform_replay", str(exc), rid)
    for pair in dataset.pairs:
        reference, participant = (
            recordings.get(pair.reference_id),
            recordings.get(pair.participant_id),
        )
        if not reference or not participant:
            issue("pair_missing", "Reference/participant recording does not exist.", pair.id)
            continue
        if (
            reference.role != "reference"
            or participant.role != "participant"
            or reference.id == participant.id
            or reference.family_id != participant.family_id
            or pair.transcript_sha256 != reference.transcript_sha256
            or pair.transcript_sha256 != participant.transcript_sha256
        ):
            issue(
                "pair_relationship", "Pair role, family or transcript identity mismatch.", pair.id
            )
        expected_identity = (
            "derived"
            if participant.origin == "synthetic"
            else (
                "verified"
                if reference.transcript.status == participant.transcript.status == "verified"
                else "needs_review"
            )
        )
        if pair.identity_status != expected_identity:
            issue(
                "identity_status",
                "Pair identity status contradicts transcript/origin evidence.",
                pair.id,
            )
        if pair.identity_status == "needs_review":
            issue(
                "identity_review",
                "Human transcript identity needs review.",
                pair.id,
                warning=not publication,
            )
        if pair.intended_flaw != "unspecified" and (pair.intended_flaw == "acceptable") != (
            pair.intended_severity == 0
        ):
            issue("severity", "Only acceptable pairs use intended severity zero.", pair.id)
        reviewed = [
            a
            for a in dataset.annotations
            if a.pair_id == pair.id
            and a.source == "human"
            and a.review_status in {"reviewed", "adjudicated"}
        ]
        if pair.reviewed_severity is not None and (
            not reviewed or pair.reviewed_severity != max(a.severity for a in reviewed)
        ):
            issue(
                "reviewed_severity",
                "Pair reviewed severity lacks matching reviewed labels.",
                pair.id,
            )
        if publication:
            reviewers = {a.reviewer_id for a in reviewed}
            if len(reviewers) < 2:
                issue(
                    "annotation_review",
                    "Publication needs independent reviewed annotation by two reviewers.",
                    pair.id,
                )
        if participant.transformation:
            recipe = participant.transformation.recipe
            kinds = {CATEGORIES[operation.kind] for operation in recipe.operations}
            if pair.intended_flaw not in kinds or pair.intended_severity != max(
                o.severity for o in recipe.operations
            ):
                issue(
                    "recipe_severity",
                    "Pair severity/category contradicts transformation recipe.",
                    pair.id,
                )
    for annotation in dataset.annotations:
        recording, pair = recordings.get(annotation.recording_id), pairs.get(annotation.pair_id)
        if not recording or not pair or pair.participant_id != annotation.recording_id:
            issue(
                "annotation_relationship",
                "Annotation must refer to a pair's participant.",
                annotation.id,
            )
            continue
        if annotation.transcript_sha256 != recording.transcript_sha256:
            issue("annotation_transcript", "Annotation transcript hash differs.", annotation.id)
        if annotation.end_s > recording.normalized_info.duration_s + 1e-8:
            issue("annotation_interval", "Annotation exceeds participant duration.", annotation.id)
        if annotation.token_span and not (
            0 <= annotation.token_span[0] < annotation.token_span[1] <= len(recording.tokens)
        ):
            issue("annotation_tokens", "Invalid half-open token span.", annotation.id)
        if annotation.supersedes:
            old = annotations.get(annotation.supersedes)
            if not old or old.pair_id != annotation.pair_id or old.id == annotation.id:
                issue("annotation_history", "Invalid superseded annotation link.", annotation.id)
        if annotation.source == "synthetic_recipe" and (
            not recording.transformation
            or annotation.transformation_sha256 != recording.transformation.recipe_sha256
        ):
            issue(
                "annotation_recipe",
                "Generated label lacks matching recipe provenance.",
                annotation.id,
            )
        if annotation.source == "synthetic_recipe" and recording.transformation:
            operations = recording.transformation.recipe.operations
            expected_labels = {
                "a-" + content_hash([recording.id, i])[:24]: operation
                for i, operation in enumerate(operations)
            }
            operation = expected_labels.get(annotation.id)
            if (
                not operation
                or annotation.category != CATEGORIES[operation.kind]
                or (annotation.severity != operation.severity)
            ):
                issue(
                    "annotation_recipe",
                    "Generated label category/severity/ID differs from recipe.",
                    annotation.id,
                )
            elif recording.transformation.time_map:
                start, end = round(operation.start_s * RATE), round(operation.end_s * RATE)
                segments = [
                    s
                    for s in recording.transformation.time_map
                    if s.source_start >= start and s.source_end <= end and s.kind != "unchanged"
                ]
                if not segments or not (
                    math.isclose(annotation.start_s, segments[0].output_start / RATE, abs_tol=1e-8)
                    and math.isclose(annotation.end_s, segments[-1].output_end / RATE, abs_tol=1e-8)
                ):
                    issue(
                        "annotation_recipe",
                        "Generated interval differs from mapped edit support.",
                        annotation.id,
                    )
        if (
            annotation.source == "human"
            and annotation.transformation_sha256 is not None
            and (
                not recording.transformation
                or annotation.transformation_sha256 != recording.transformation.recipe_sha256
            )
        ):
            issue(
                "annotation_recipe",
                "Human annotation's supplied recipe hash does not match.",
                annotation.id,
            )
    for recording in dataset.recordings:
        if recording.transformation:
            expected_ids = {
                "a-" + content_hash([recording.id, i])[:24]
                for i in range(len(recording.transformation.recipe.operations))
            }
            actual_ids = {
                a.id
                for a in dataset.annotations
                if a.recording_id == recording.id and a.source == "synthetic_recipe"
            }
            if actual_ids != expected_ids:
                issue(
                    "recipe_labels_missing",
                    "Recipe edit-support labels are missing or unexpected.",
                    recording.id,
                )
    if dataset.split:
        split = dataset.split
        groups = connected_groups(dataset)
        if split.groups != groups or set(split.assignments) != set(recordings):
            issue("split_membership", "Split members/groups do not cover current dataset.", "split")
        if split.membership_sha256 != content_hash(split.assignments):
            issue("split_hash", "Split membership checksum differs.", "split")
        for group, members in groups.items():
            if len({split.assignments.get(member) for member in members}) > 1:
                issue(
                    "split_leakage",
                    "Connected family/source/work/transcript/speaker crosses splits.",
                    group,
                )
        try:
            expected = make_split(dataset, split.seed, split.ratios)
            if split != expected:
                issue(
                    "split_replay", "Split report differs from deterministic assignment.", "split"
                )
        except DatasetError as exc:
            issue(exc.code, str(exc), "split")
    elif publication:
        issue("split_missing", "Publication requires an audited split report.", "split")
    if publication:
        references = [
            r for r in dataset.recordings if r.role == "reference" and r.origin == "source"
        ]
        if len({r.family_id for r in references}) < 2:
            issue("pilot_missing", "At least two reviewed source families are required.", "dataset")
        human_pairs = [
            p
            for p in dataset.pairs
            if recordings.get(p.participant_id)
            and recordings[p.participant_id].origin == "self_recorded"
        ]
        if not {0, 1, 2, 3} <= {p.intended_severity for p in dataset.pairs}:
            issue(
                "severity_coverage", "Dataset lacks the near-perfect to severe spectrum.", "dataset"
            )
        if not {0, 3} <= {p.intended_severity for p in human_pairs}:
            issue(
                "human_mirrors_missing",
                "Human near-perfect and severe mirrors are required.",
                "dataset",
            )
        if dataset.split:
            counts = {
                name: sum(
                    1
                    for members in dataset.split.groups.values()
                    if dataset.split.assignments.get(members[0]) == name
                )
                for name in ("train", "validation", "test")
            }
            if counts["train"] < 1 or counts["validation"] < 1 or counts["test"] < 3:
                issue(
                    "split_coverage",
                    "Publication evaluation needs train/validation and three test groups.",
                    "split",
                )
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "recordings": len(dataset.recordings),
        "pairs": len(dataset.pairs),
        "annotations": len(dataset.annotations),
    }
