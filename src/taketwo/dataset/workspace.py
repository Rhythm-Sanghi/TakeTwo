"""Transactional dataset operations; originals are immutable managed copies."""

from collections import Counter
from pathlib import Path

from .audio import (
    RATE,
    decode,
    inspect_samples,
    normalize,
    quality,
    read_audio,
    sample_hash,
    sha256,
    versions,
    wav_bytes,
)
from .errors import DatasetError
from .schema import (
    Annotation,
    Dataset,
    ImportSpec,
    Pair,
    Processing,
    Recipe,
    Recording,
    Transformation,
    content_hash,
    tokenize,
)
from .splits import make_split
from .storage import load, managed_path, safe_path, save, workspace_lock, write_new
from .transform import CATEGORIES, apply_recipe
from .validation import validate


def initialize(root: Path, dataset_version: str) -> Dataset:
    dataset = Dataset(dataset_version=dataset_version)
    safe_path(root)
    if root.exists():
        raise DatasetError(
            "workspace_exists",
            "Initialization requires a new directory.",
            "Choose a new workspace; existing files were not changed.",
            str(root),
        )
    root.mkdir(parents=True)
    (root / "originals").mkdir()
    (root / "normalized").mkdir()
    save(root, dataset)
    return dataset


def find_recording(dataset: Dataset, recording_id: str) -> Recording:
    for recording in dataset.recordings:
        if recording.id == recording_id:
            return recording
    raise DatasetError(
        "recording_missing",
        "Recording ID does not exist.",
        "List/export the workspace and use a recording ID.",
        recording_id,
    )


def check_dataset(dataset: Dataset, root: Path) -> None:
    report = validate(dataset, root)
    if not report["valid"]:
        first = report["errors"][0]
        raise DatasetError(
            "dataset_invalid",
            first["message"],
            "Run validate and repair the workspace before modifying it.",
            first["affected"],
        )


def persist_recording(
    root: Path,
    dataset: Dataset,
    recording: Recording,
    original: bytes,
    normalized: bytes,
    pair: Pair | None,
    annotations: list[Annotation],
) -> None:
    for existing in dataset.recordings:
        if (
            existing.original_sha256 == recording.original_sha256
            or existing.sample_sha256 == recording.sample_sha256
        ):
            raise DatasetError(
                "duplicate_audio",
                "Audio content already exists in the workspace.",
                "Reuse the existing recording; no duplicate was written.",
                existing.id,
            )
    if dataset.split and recording.origin != "synthetic":
        raise DatasetError(
            "split_frozen",
            "Workspace already has a split report.",
            "Create/branch a new dataset version before adding recordings.",
        )
    original_path = managed_path(root, recording.original_path)
    normalized_path = managed_path(root, recording.normalized_path)
    created: list[Path] = []
    try:
        write_new(original_path, original)
        created.append(original_path)
        write_new(normalized_path, normalized)
        created.append(normalized_path)
        dataset.recordings.append(recording)
        if pair:
            dataset.pairs.append(pair)
        dataset.annotations.extend(annotations)
        if dataset.split:
            previous = dataset.split.assignments
            dataset.split = make_split(dataset, dataset.split.seed, dataset.split.ratios)
            if any(dataset.split.assignments[key] != value for key, value in previous.items()):
                raise DatasetError(
                    "split_changed",
                    "New derivative would change frozen assignments.",
                    "Use a new dataset version.",
                )
        check_dataset(dataset, root)
        save(root, dataset)
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise


def import_recording(
    root: Path,
    audio_path: Path,
    spec: ImportSpec,
    *,
    reference_id: str | None = None,
    category: str = "acceptable",
    severity: int | None = 0,
) -> Recording:
    with workspace_lock(root):
        dataset = load(root)
        check_dataset(dataset, root)
        reference = find_recording(dataset, reference_id) if reference_id else None
        if reference and reference.role != "reference":
            raise DatasetError(
                "reference_role",
                "Pair target must be a reference.",
                "Select a reference recording.",
            )
        tokens, offsets = tokenize(spec.transcript.text)
        transcript_hash = content_hash(tokens)
        if reference and (
            reference.transcript_sha256 != transcript_hash or reference.family_id != spec.family_id
        ):
            raise DatasetError(
                "transcript_relationship",
                "Mirror transcript/family differs from reference.",
                "Use the same canonical word sequence and speech family.",
            )
        original, samples, original_info = read_audio(audio_path)
        mono = normalize(samples, original_info.sample_rate_hz, spec.channel)
        normalized = wav_bytes(mono)
        normalized_info = inspect_samples(mono, RATE, "WAV", "FLOAT")
        if "near_silent" in quality(original_info) + quality(normalized_info):
            raise DatasetError(
                "near_silent",
                "Recording is silent or below -60 dBFS RMS.",
                "Review/re-record the source rather than amplifying silently.",
            )
        rid = (
            "r-"
            + content_hash(
                {
                    "input": sha256(original),
                    "spec": spec.model_dump(mode="json"),
                    "filename": audio_path.name,
                    "reference": reference_id,
                    "version": dataset.dataset_version,
                }
            )[:24]
        )
        recording = Recording(
            id=rid,
            dataset_version=dataset.dataset_version,
            family_id=spec.family_id,
            speaker_id=spec.speaker_id,
            origin=spec.origin,
            role="participant" if reference else "reference",
            original_filename=audio_path.name,
            original_path=f"originals/{rid}.{original_info.format.lower()}",
            normalized_path=f"normalized/{rid}.wav",
            original_sha256=sha256(original),
            normalized_sha256=sha256(normalized),
            sample_sha256=sample_hash(mono),
            transcript=spec.transcript,
            transcript_sha256=transcript_hash,
            tokens=tokens,
            token_offsets=offsets,
            provenance=spec.provenance,
            original_info=original_info,
            normalized_info=normalized_info,
            processing=Processing(channel=spec.channel, versions=versions()),
            transformation=None,
            quality_flags=sorted(set(quality(original_info) + quality(normalized_info))),
        )
        pair = None
        if reference:
            pair = Pair(
                id="p-" + content_hash([reference.id, rid])[:24],
                reference_id=reference.id,
                participant_id=rid,
                transcript_sha256=transcript_hash,
                intended_flaw=category,
                intended_severity=severity,
                identity_status="verified"
                if (reference.transcript.status == spec.transcript.status == "verified")
                else "needs_review",
            )
        persist_recording(root, dataset, recording, original, normalized, pair, [])
        return recording


def generate(root: Path, parent_id: str, recipe: Recipe) -> Recording:
    with workspace_lock(root):
        dataset = load(root)
        check_dataset(dataset, root)
        parent = find_recording(dataset, parent_id)
        if parent.role != "reference":
            raise DatasetError(
                "parent_role",
                "Generate from a source reference in v1.",
                "Use combined operations in one recipe instead of chained variants.",
            )
        source, _ = decode(managed_path(root, parent.normalized_path).read_bytes())
        output, time_map, affected = apply_recipe(source[:, 0], recipe)
        normalized = wav_bytes(output)
        recipe_hash = content_hash(recipe.model_dump(mode="json"))
        rid = (
            "r-"
            + content_hash(
                {
                    "parent": parent.id,
                    "recipe": recipe_hash,
                    "versions": versions(),
                    "version": dataset.dataset_version,
                }
            )[:24]
        )
        info = inspect_samples(output, RATE, "WAV", "FLOAT")
        transformation = Transformation(
            parent_id=parent.id,
            source_sha256=parent.normalized_sha256,
            recipe=recipe,
            recipe_sha256=recipe_hash,
            time_map=time_map,
            versions=versions(),
        )
        recording = parent.model_copy(
            update={
                "id": rid,
                "origin": "synthetic",
                "role": "participant",
                "original_filename": f"{rid}.wav",
                "original_path": f"originals/{rid}.wav",
                "normalized_path": f"normalized/{rid}.wav",
                "original_sha256": sha256(normalized),
                "normalized_sha256": sha256(normalized),
                "sample_sha256": sample_hash(output),
                "original_info": info,
                "normalized_info": info,
                "processing": Processing(channel=None, versions=versions()),
                "transformation": transformation,
                "quality_flags": quality(info),
            }
        )
        highest = max(recipe.operations, key=lambda operation: operation.severity)
        pair = Pair(
            id="p-" + content_hash([parent.id, rid])[:24],
            reference_id=parent.id,
            participant_id=rid,
            transcript_sha256=parent.transcript_sha256,
            intended_flaw=CATEGORIES[highest.kind],
            intended_severity=highest.severity,
            identity_status="derived",
        )
        annotations = [
            Annotation(
                id="a-" + content_hash([rid, index])[:24],
                pair_id=pair.id,
                recording_id=rid,
                transcript_sha256=recording.transcript_sha256,
                category=CATEGORIES[operation.kind],
                start_s=start / RATE,
                end_s=end / RATE,
                severity=operation.severity,
                source="synthetic_recipe",
                review_status="unreviewed",
                reviewer_id=None,
                rationale=(
                    f"Recipe operation {index}: {operation.kind}; "
                    "edit support, not perceptual ground truth."
                ),
                uncertainty_s=None,
                token_span=None,
                transformation_sha256=recipe_hash,
            )
            for index, (operation, (start, end)) in enumerate(
                zip(recipe.operations, affected, strict=False)
            )
        ]
        persist_recording(root, dataset, recording, normalized, normalized, pair, annotations)
        return recording


def add_annotations(root: Path, annotations: list[Annotation]) -> None:
    with workspace_lock(root):
        dataset = load(root)
        check_dataset(dataset, root)
        dataset.annotations.extend(annotations)
        check_dataset(dataset, root)
        save(root, dataset)


def assign_splits(root: Path, seed: int, ratios: tuple[float, float, float]) -> dict:
    with workspace_lock(root):
        dataset = load(root)
        check_dataset(dataset, root)
        report = make_split(dataset, seed, ratios)
        if dataset.split and dataset.split != report:
            raise DatasetError(
                "split_frozen",
                "Existing split cannot be silently reassigned.",
                "Use a separately versioned workspace for revised splits.",
            )
        dataset.split = report
        save(root, dataset)
        return report.model_dump(mode="json")


def summary(dataset: Dataset) -> dict:
    return {
        "schema_version": dataset.schema_version,
        "dataset_version": dataset.dataset_version,
        "recordings": len(dataset.recordings),
        "pairs": len(dataset.pairs),
        "annotations": len(dataset.annotations),
        "origins": dict(Counter(r.origin for r in dataset.recordings)),
        "annotation_review": dict(Counter(a.review_status for a in dataset.annotations)),
        "severity": dict(
            Counter(
                str(p.intended_severity) if p.intended_severity is not None else "unlabeled"
                for p in dataset.pairs
            )
        ),
        "split": dataset.split.model_dump(mode="json") if dataset.split else None,
        "competition_dataset_complete": False,
    }
