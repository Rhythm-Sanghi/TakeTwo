# Human pilot collection kit

TakeTwo — Speech analysis workspace. No participant recordings, consent records or independent reviews were available for Phase 4B. This is a procedure for collecting evidence, not an assertion that collection occurred. Use the existing [acquisition ledger](pilot-collection.md), [dataset tools](dataset-engineering.md) and [review contracts](comparison-engine.md).

## Recording session

The earlier no-participant statement is historical to Phase 4B. The current user supplied five private same-speaker practice takes; follow [the five-file recording/import guide](recording-import-guide.md). They still require actual independent text/timing/flaw review and applicable public-release permission. Controlled local references do not replace the required public-speaker baseline. The new browser handoff imports actual review JSON; it never creates approval or silently changes verified transcript metadata.

1. Select a substantive, rights-cleared 15–25 second source excerpt. Retain the master, exact master-relative cut offsets, SHA-256, item-specific license evidence and required attribution. The existing JFK salutation is a useful integration candidate but lacks substantive delivery range. Obtain a second source speaker; two JFK speeches remain one connected group.
2. Have two people independently listen to the entire excerpt and check every spoken word, repetition and cut edge. Resolve differences before recording. Archive both original checks. Only then use `transcript.status=verified`, the actual two reviewer IDs and verification date in `ImportSpec`. Import corrected metadata into a new dataset version; never patch old feature artifacts.
3. Obtain actual adult participant permission covering recording, analysis, annotation, adaptation and the intended public release. Keep signed consent and identity mapping outside Git; put a stable private evidence reference in metadata. Declining public release must remain possible: do not mark redistribution permitted without permission. Record pseudonymous speaker ID, date, room, microphone, distance, gain and unavoidable AGC/noise processing.
4. Record the exact same verified script independently as a human. Use mono WAV/FLAC, fixed microphone/gain, a quiet room and short room tone. Disable enhancement where available. Do not imitate the source voice. Capture a comfortable faithful version and separate mild/moderate/severe intended changes to pace, pauses or emphasis. Intention is a collection instruction, not ground truth. Include acceptable alternative deliveries and mixed flaws. Listen for omissions/additions and clipping; re-record mismatches.
5. Import the reference and each participant with existing CLI metadata. Set participant `origin=self_recorded`, matching family/work/text, distinct speaker/source/session, and real consent/rights evidence. `import-flawed` is the existing pair-ingest command even for a near-perfect candidate; intended severity/category must remain distinct from reviewed labels. There is no automatic human capture or approval step.
6. Before derivatives/calibration, import all real members and freeze leakage-resistant groups with `split`. Shared speakers, source/work/family/text, hashes and lineage connect files. A tiny connected pilot cannot establish held-out accuracy; collect enough independent groups for train/validation and at least three test groups. Keep synthetic edits in separate lineage and evaluation runs.

```powershell
$workspace = '.\local-data\human-pilot-v1'
uv run taketwo-dataset init $workspace --version human-pilot-v1
$ref = uv run taketwo-dataset import-reference $workspace --audio $referenceWav --metadata $referenceMetadata | ConvertFrom-Json
# Check $LASTEXITCODE before using every returned ID/path.
uv run taketwo-dataset import-flawed $workspace --reference $ref.recording_id --audio $participantWav --metadata $participantMetadata --category pacing --severity 1
uv run taketwo-dataset validate $workspace --reproduce
uv run taketwo-dataset split $workspace --seed 17 --ratios 0.5 0.25 0.25
```

Variables refer to actual collected files; none are supplied or fabricated by this kit. The import form can also ingest recordings, but imports intentionally remain unverified there. Use a reviewed new CLI dataset version for score-eligible text.

## Review and comparison session

Reviewers can now perform checks in the [browser Review Workspace](review-workspace.md) and export existing-compatible Review JSON, rather than authoring files manually. An operator assigns one recording/activity at a time, keeps the private key, closes analysis/peer tabs, and supervises a fresh private browser handoff. The backend blocks peer/score/recipe APIs while locked. Recruit actual independent people; identifiers and interaction telemetry cannot prove identity or comprehension. Save drafts freely; approve/submit only real completed work. Use the checklist in that guide for all five private takes; automated draft browser checks do not supply human acceptance. Retain original blind inventories before adjudication/revisions.

Use a separate copy of the [annotation worksheet](annotation-worksheet.md) per reviewer/member. Preserve raw notes and disagreement history. A reviewer must not approve their own performance as independent ground truth. Both flaw reviewers listen without engine predictions or synthetic recipe windows. Timing reviewers may inspect original machine alignment, but manually check every boundary; this is assisted timing, not independent MFA accuracy evidence.

```powershell
$alignment = uv run taketwo-analysis align $workspace --recording $recordingId --config $alignmentConfig | ConvertFrom-Json
$features = uv run taketwo-analysis extract $workspace --recording $recordingId --alignment $alignment.artifact | ConvertFrom-Json
uv run taketwo-analysis inspect $workspace --artifact $alignment.artifact
uv run taketwo-analysis validate $workspace --artifact $features.artifact --alignment $alignment.artifact --reproduce
# Repeat alignment/extraction and two real timing reviews for each member.
$review = uv run taketwo-comparison import-review $workspace --review $reviewJson --alignment $alignment.artifact | ConvertFrom-Json
```

Copy exact `provenance` from the inspected alignment/features and the original alignment envelope `sha256` into each timing review. Follow `Review`/`Interval`/`Label` in [schema v1](comparison-schema-v1.json); do not substitute file-byte hashes for payload hashes. Timing reviews include every token and an agreed complete phrase partition. Two independent approved records must agree within 200 ms. Revisions use same-reviewer `supersedes`; retain originals. Transcript checks alone cannot approve timing.

For flaw reviews, record the actual pair, full native listening coverage, positive intervals or missing-pause anchors, severity, rationale and uncertainty. Empty labels assert no positives only over the inspected coverage. Store acceptable/quality/alignment-uncertain intervals separately using dataset `annotate`; comparison `Label` accepts the four flaw categories only. Evaluation needs two independent, blinded approved flaw reviews with identical reconciled label inventories, including IDs/rationales/uncertainty. Resolve inventories explicitly without inventing agreement or deleting the original disagreements.

```powershell
$paired = uv run taketwo-comparison compare $workspace --pair $pairId --reference-features $referenceFeatures --reference-alignment $referenceAlignment --participant-features $participantFeatures --participant-alignment $participantAlignment --review $referenceTimingA --review $referenceTimingB --review $participantTimingA --review $participantTimingB | ConvertFrom-Json
uv run taketwo-comparison validate $workspace --artifact $paired.artifact --reproduce
uv run taketwo-comparison evaluate $workspace --report $paired.artifact --review $flawReviewA --review $flawReviewB --config $evaluationConfig
uv run taketwo-dataset validate $workspace --publication --reproduce
```

Import both flaw reviews first with `import-review`; pass their published paths to evaluation, never to detection. Evaluation config specifies mode/origin/split. Freeze a separately versioned calibrated policy from reviewed train/validation groups before held-out testing; preserve `delivery-v0`. Exit 3 is honest abstention, not successful scientific validation. CLI review imports validate structure/binding, not reviewer identity or legal permission.

## Actions requiring people

The user must select substantive sources and retain rights evidence; recruit consenting independent speakers and two reviewers; record faithful/flawed takes; verify exact text; check native word boundaries/phrases; independently label the full performance; reconcile disagreements; and authorize any eventual release. Software can then run comparisons, show genuine regions, and compute evaluation. Until those actions happen, real-pair playback of detected regions, accuracy, calibration and dataset release remain open gates.
