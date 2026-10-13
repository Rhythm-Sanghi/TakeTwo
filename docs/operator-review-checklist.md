# Two-person review checklist

TakeTwo — Speech analysis workspace. This checklist collects human evidence; it
does not supply it. Use an isolated, permitted collection workspace. Keep operator
keys, consent records, recordings and reviewer identities private.

1. **Prepare the pair.** Import the actual reference and participant WAV/FLAC and
   intended words through Recording Library. Confirm source, local consent and
   same-text pairing. Preserve originals. Run actual alignment/features where
   configured; automatic success does not verify the words.
2. **Assign the first person.** In Review Workspace, enter the local operator key,
   recording, agreed reviewer pseudonym and transcript activity. Start handoff in
   a fresh private browser. The reviewer listens completely, corrects text, records
   uncertainty, saves and explicitly chooses a decision. Submit only their own
   completed work. Export the immutable Review JSON from the app.
3. **Assign the second person independently.** End handoff, close/clear the reviewer
   browser and use a fresh private window. Repeat without showing the first review.
   Inspect disagreements as operator after both submissions. Have each author
   independently revise disputed evidence in a superseding session; retain originals.
4. **Version checked text.** Use the explicit reviewed-version import workflow for
   two genuinely agreeing transcript checks. Regenerate alignment/features against
   that version. Old timing evidence never transfers to changed provenance. The
   [recording guide](recording-import-guide.md) and [reproduction guide](reproducibility.md)
   cover this operator step.
5. **Check timing for each member.** Assign two independent timing sessions against
   each regenerated alignment. Load suggestions, replay and correct every word,
   save each boundary and mark it inspected. Enter actual phrase end word numbers,
   including the final word. Resolve uncertain/overlapping boundaries explicitly.
6. **Collect blinded flaws for each pair.** Each reviewer independently listens to
   the participant and permitted reference context, covering the full recording.
   Mark actual intervals or missing-pause anchors, category, severity, rationale
   and uncertainty. Do not expose predictions, transformation recipes or intended
   severity. Empty labels are acceptable only after full listening. Save/submit/export
   separately; no automatic approval or fabricated positives.
7. **Resolve and validate.** Load sessions/adjudication as operator. Record the
   explanation separately, then request explicit same-author superseding sessions
   where needed. `exact-inventory-v1` requires equal numerical flaw inventories;
   different IDs/prose may remain, different boundaries cannot be selected silently.
   Export originals/revisions; validate and evaluate through the documented CLI.
   Keep null metrics when unresolved. A one-family result is pilot-only.

Completion evidence: actual two-person submissions, complete coverage, preserved
original/revision hashes, explicit dataset version, regenerated artifacts and a
replayable evaluation or honest abstention. Permission for local review does not
authorize public dataset/video release. See [review privacy and identity limits](review-workspace.md).
