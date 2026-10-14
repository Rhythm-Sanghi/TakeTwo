"""Operator workflow hints from existing review validation, never new score gates."""

from .contracts import RecordingReadiness


def review_readiness(dataset, inventory, processing):
    groups = {
        (group["recording_id"], group["scope"]): group for group in inventory["disagreements"]
    }
    result = []
    for recording in dataset.recordings:
        pair = next((p for p in dataset.pairs if p.participant_id == recording.id), None)
        status = {}
        for scope in ("transcript", "timing", "flaws"):
            group = groups.get((recording.id, scope))
            status[scope] = (
                "No submitted reviews"
                if group is None
                else group["issue"] or "Agreement recorded; existing evidence checks passed"
            )

        agreement = {
            scope: (recording.id, scope) in groups
            and groups[(recording.id, scope)]["issue"] is None
            for scope in ("transcript", "timing", "flaws")
        }

        job_id = processing.get(recording.id)
        scope = None
        if recording.provenance.rights.status != "cleared" or (
            recording.origin == "self_recorded" and not recording.provenance.consent_evidence
        ):
            action = "rights"
            message = (
                "Verify recording rights and genuine consent where applicable. "
                "The browser cannot grant rights; preserve evidence and use the documented "
                "reviewed-version CLI workflow for metadata corrections."
            )
        elif recording.transcript.status != "verified":
            if agreement["transcript"]:
                action = "reviewed_version"
                message = (
                    "Transcript reviews agree. Create a reviewed dataset version with the "
                    "documented CLI workflow, then regenerate alignment and features. "
                    "Submitted assertions alone do not change the manifest."
                )
            else:
                action, scope = "transcript", "transcript"
                message = (
                    "Complete two independent transcript reviews; resolve disagreements "
                    "with explicit same-author revisions. Machine alignment does not verify text."
                )
        elif not job_id:
            action = "processing"
            message = "Regenerate successful alignment and features against this reviewed version."
        elif not agreement["timing"]:
            action, scope = "timing", "timing"
            message = (
                "Complete independent word and phrase timing reviews of the current alignment; "
                "resolve disagreements with explicit revisions."
            )
        elif pair and not agreement["flaws"]:
            action, scope = "flaws", "flaws"
            message = (
                "Complete independent blinded flaw inventories for this pair and resolve "
                "numerical disagreements. Predictions must stay hidden from reviewers."
            )
        else:
            action = "comparison"
            message = (
                "Run comparison and the documented CLI evaluation checks. Other member, pair, "
                "coverage, split and acoustic gates still apply; "
                "this is not accuracy certification."
            )
        result.append(
            RecordingReadiness(
                recording_id=recording.id,
                next_action=action,
                message=message,
                review_scope=scope,
                job_id=job_id,
                pair_id=pair.id if pair else None,
                review_status=status,
                review_agreement=agreement,
            )
        )
    return result
