"""Local draft adapters; unknown facts stay null, never presumed clearance/review."""

import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from taketwo.analysis.limits import maximum_analysis_duration_s
from taketwo.dataset.audio import RATE, decode, wav_bytes
from taketwo.dataset.schema import ImportSpec, Provenance, Rights, Transcript, content_hash
from taketwo.dataset.storage import load, managed_path, safe_path, save, workspace_lock, write_new
from taketwo.dataset.workspace import find_recording, import_recording, initialize

from .contracts import ExcerptRequest, LocalImportRequest, WorkspaceRevision


def local_spec(root: Path, request: LocalImportRequest, filename: str) -> ImportSpec:
    if load(root).schema_version != 2:
        raise ValueError(
            "Enable private draft imports to upgrade this v1 manifest with a retained backup."
        )
    if not request.local_permission:
        raise ValueError("Confirm permission to store and process this audio locally.")
    participant = request.recording_type == "human_participant"
    if participant != bool(request.reference_id):
        raise ValueError("Select an existing reference for a human participant only.")
    reference = find_recording(load(root), request.reference_id) if participant else None
    if reference and reference.role != "reference":
        raise ValueError("Pair target must be a reference recording.")
    if request.same_speaker_as_reference and not reference:
        raise ValueError("Same-speaker choice requires an existing reference.")
    stamp = datetime.now(UTC).isoformat()
    source_id = "upload-" + uuid4().hex[:24]
    # Unassigned voices conservatively share an ID, preventing invented independent groups.
    speaker = (
        reference.speaker_id
        if request.same_speaker_as_reference
        else "speaker-" + content_hash(request.speaker_label.casefold())[:24]
        if request.speaker_label
        else "speaker-unassigned"
    )
    return ImportSpec(
        family_id=reference.family_id if reference else "family-" + source_id,
        speaker_id=speaker,
        origin="source" if request.recording_type == "public_reference" else "self_recorded",
        channel=request.channel,
        transcript=Transcript(
            text=request.transcript,
            language="en",
            status="unverified",
            reviewers=[],
            verification_date=None,
            revision="v1",
        ),
        provenance=Provenance(
            source_id=source_id,
            work_id=reference.provenance.work_id if reference else "work-" + source_id,
            source=request.title or filename,
            source_url=request.source_url,
            collection_method=(
                f"Local upload at {stamp}; importer type: "
                f"{request.recording_type}. Capture date unknown."
            ),
            access_date=stamp[:10],
            excerpt_offset_s=0.0,
            baseline_rationale=None
            if participant
            else request.rationale
            or "Importer-selected comparison reference; effectiveness unreviewed.",
            consent_evidence=request.consent_evidence
            or (
                f"Importer asserted local storage/processing permission at {stamp}; "
                "public release not granted by this assertion."
                if request.recording_type != "public_reference"
                else None
            ),
            rights=request.rights
            or Rights(
                status="pending",
                holder=None,
                license_name=None,
                evidence=None,
                attribution=None,
                permits_adaptation=False,
                permits_redistribution=False,
            ),
        ),
    )


def excerpt(root: Path, recording_id: str, request: ExcerptRequest):
    item = find_recording(load(root), recording_id)
    if item.origin == "synthetic":
        raise ValueError(
            "Synthetic edits retain their recipe/time map; create them with dataset tools."
        )
    limit = maximum_analysis_duration_s()
    if (
        not request.start_s < request.end_s <= item.normalized_info.duration_s
        or request.end_s - request.start_s > limit
    ):
        raise ValueError(
            f"Choose a positive excerpt of at most {limit} seconds inside this recording."
        )
    if (item.role == "participant") != bool(request.reference_id):
        raise ValueError("A participant excerpt needs the matching excerpt reference.")
    reference = find_recording(load(root), request.reference_id) if request.reference_id else None
    samples, _ = decode(managed_path(root, item.normalized_path).read_bytes())
    left, right = round(request.start_s * RATE), round(request.end_s * RATE)
    spec = ImportSpec(
        family_id=reference.family_id if reference else item.family_id,
        speaker_id=item.speaker_id,
        origin=item.origin,
        channel=None,
        transcript=item.transcript.model_copy(
            update={
                "text": request.transcript,
                "status": "unverified",
                "reviewers": [],
                "verification_date": None,
            }
        ),
        provenance=item.provenance.model_copy(
            update={
                "work_id": reference.provenance.work_id if reference else item.provenance.work_id,
                "excerpt_offset_s": item.provenance.excerpt_offset_s + left / RATE,
                "collection_method": (
                    f"Explicit excerpt of {item.id}, source SHA-256 "
                    f"{item.normalized_sha256}, samples [{left},{right}); prior: "
                    f"{item.provenance.collection_method}"
                ),
            }
        ),
    )
    with tempfile.TemporaryDirectory(prefix="taketwo-excerpt-") as directory:
        path = Path(directory) / (Path(item.original_filename).stem + "-excerpt.wav")
        path.write_bytes(wav_bytes(samples[left:right, 0]))
        return import_recording(
            root,
            path,
            spec,
            reference_id=request.reference_id,
            category="unspecified",
            severity=None,
        )


def upgrade_drafts(root: Path):
    with workspace_lock(root):
        dataset = load(root)
        if dataset.schema_version == 2:
            return dataset
        from taketwo.dataset.audio import sha256

        original = (root / "manifest.jsonl").read_bytes()
        backup = managed_path(root, f"history/schema-v1-{sha256(original)}.jsonl")
        backup.parent.mkdir(exist_ok=True)
        if backup.exists():
            if backup.read_bytes() != original:
                raise ValueError("Existing manifest backup differs; no upgrade performed.")
        else:
            write_new(backup, original)
        dataset.schema_version = 2
        save(root, dataset)
        return dataset


def corrected_pair(root: Path, pair_id: str, reference_id: str) -> WorkspaceRevision:
    dataset = load(root)
    pair = next((p for p in dataset.pairs if p.id == pair_id), None)
    if not pair:
        raise ValueError("Pair no longer exists.")
    participant = find_recording(dataset, pair.participant_id)
    reference = find_recording(dataset, reference_id)
    if reference.role != "reference" or reference.id == pair.reference_id:
        raise ValueError("Choose a different reference recording.")
    if reference.tokens != participant.tokens or participant.origin == "synthetic":
        raise ValueError(
            "Correction requires identical canonical words and a genuine human participant."
        )
    target = managed_path(root, "revisions/pair-" + uuid4().hex)
    target.parent.mkdir(exist_ok=True)
    try:
        initialize(target, "correction-" + uuid4().hex[:20])
        imported = []
        for item in (reference, participant):
            spec = ImportSpec(
                family_id=reference.family_id,
                speaker_id=item.speaker_id,
                origin=item.origin,
                channel=item.processing.channel,
                transcript=item.transcript.model_copy(
                    update={"status": "unverified", "reviewers": [], "verification_date": None}
                ),
                provenance=item.provenance.model_copy(
                    update={"work_id": reference.provenance.work_id}
                ),
            )
            with tempfile.TemporaryDirectory(prefix="taketwo-correction-") as directory:
                audio = Path(directory) / Path(item.original_filename).name
                audio.write_bytes(managed_path(root, item.original_path).read_bytes())
                result = import_recording(
                    target,
                    audio,
                    spec,
                    reference_id=imported[0].id if imported else None,
                    category="unspecified",
                    severity=None,
                )
            imported.append(result)
    except Exception:
        # Only the server-created revision is rolled back; user originals are never removed.
        safe_path(target)
        if target.exists():
            target.resolve().relative_to(root.resolve())
            shutil.rmtree(target)
        raise
    return WorkspaceRevision(
        workspace=str(target),
        reference_id=imported[0].id,
        participant_id=imported[1].id,
        notice=(
            "New two-recording dataset version prepared. Original workspace/history unchanged. "
            "Text and timing need fresh independent review. "
            "Restart the local launcher with the new workspace path."
        ),
    )
