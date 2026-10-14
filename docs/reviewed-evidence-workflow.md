# From private recordings to legitimately reviewed evaluation

TakeTwo — Speech analysis workspace. This is an owner/reviewer procedure, not evidence
that review occurred. The five private takes currently have pending rights, unverified
text, no independent timing/flaw evidence and no valid evaluation. Actual listening
acceptance also remains pending. Never import this checklist as a scientific review.

1. **Prepare the source.** Export the current inventory with
   `uv run taketwo-dataset export $sourceWorkspace --output $inventoryFile`.
   Check source/original/normalized hashes, recording/pair IDs, dataset version and
   actual supplied text. Use originals for a new import, not a cropped listening clip.
2. **Record genuine permission.** Preserve actual holder/license, attribution,
   adaptation/redistribution scope, evidence reference and consent where applicable.
   Existing ImportSpec fields are `provenance.rights` and `provenance.consent_evidence`;
   record intended uses/scope in the real permission evidence and collection ledger.
   Keep unknown fields unknown. Local upload permission and self-recorded origin do
   not automatically clear rights. The existing `cleared` policy requires all rights
   fields plus adaptation and redistribution permission; do not assert that broader
   permission when only local processing is permitted. A software declaration cannot
   grant legal rights. Metadata corrections use a new version, preserving the old one.
3. **Two independent transcript reviews.** Use the existing supervised Review Workspace
   ([operator/reviewer procedure](review-workspace.md)). Two different real people
   listen to the source and independently check spoken text. Save actual notes,
   evidence reference and an explicit decision. A unique reviewer ID is not proof
   of a person's identity or independence. MFA suggestions never count as approval.
4. **Resolve discrepancies.** Retain initial submissions. Use separate adjudication
   notes and explicit same-author superseding reviews; a note does not override
   consensus. Reconciled work is adjudicated evidence, not new blind-independent work.
   Keep source approvals and the ledger connecting them to the revised version.
5. **Create the reviewed version.** Prepare actual ImportSpec JSON files with agreed
   text, two actual reviewer IDs, real verification date/revision and legitimate rights
   evidence. Do not copy old Review payloads under new identities. Run:

   ```powershell
   uv run taketwo-dataset init $newWorkspace --version $newVersion
   $ref = uv run taketwo-dataset import-reference $newWorkspace --audio $referenceAudio --metadata $referenceMetadata | ConvertFrom-Json
   # Check $LASTEXITCODE after each native command; stop on failure.
   $member = uv run taketwo-dataset import-flawed $newWorkspace --reference $ref.recording_id --audio $participantAudio --metadata $participantMetadata --category $declaredCategory --severity $declaredSeverity | ConvertFrom-Json
   uv run taketwo-dataset validate $newWorkspace --reproduce
   uv run taketwo-dataset export $newWorkspace --output $newInventoryFile
   ```

   Category/severity describe genuine acquisition intent, not automatic ground truth.
   `acceptable` uses intended severity 0; do not infer it from a filename. Review the
   actual pair ID in the exported `dataset.pairs` and bind it to `$pairId`.
6. **Regenerate and independently review timing.** Run the pinned configured aligner
   and extractor on the new version; bind review to their actual payload hashes:

   ```powershell
   $aRef = uv run taketwo-analysis align $newWorkspace --recording $ref.recording_id --config $alignmentConfig | ConvertFrom-Json
   $fRef = uv run taketwo-analysis extract $newWorkspace --recording $ref.recording_id --alignment $aRef.artifact | ConvertFrom-Json
   $aMember = uv run taketwo-analysis align $newWorkspace --recording $member.recording_id --config $alignmentConfig | ConvertFrom-Json
   $fMember = uv run taketwo-analysis extract $newWorkspace --recording $member.recording_id --alignment $aMember.artifact | ConvertFrom-Json
   ```

   Two real reviewers inspect every word and a complete phrase partition in native
   audio. Loading MFA boundaries is not approving them. Resolve uncertainty and
   disagreement; preserve original alignment and all review history. Changed source,
   text, version, code or alignment requires new dependent evidence.
7. **Collect blinded flaws and export real evidence.** Two independent reviewers
   listen to the whole participant recording with assigned reference context, without
   predictions. Record actual category/severity, native interval or valid boundary
   anchor, uncertainty and audible rationale. Empty labels are legitimate only after
   actual full coverage. A person exposed to predictions must not claim a blind review.
   Export scientific **Review JSON** from submitted sessions. Draft/session summaries
   are not importable scientific Review files. Manifest Annotation records are a
   separate dataset/publication contract; prepare them from actual reviewers as
   described in [reproducibility](reproducibility.md), never from predicted windows.
8. **Preflight actual import files, read-only.** With existing dependencies:

   ```powershell
   uv run python scripts/check_review_file.py $newWorkspace --review $reviewJson --alignment $currentOriginalAlignment
   ```

   This checks strict raw Review structure, current source/text/code identity and
   scope-specific alignment/pair constraints using existing validators. Omit alignment
   only where the scope does not require it. Failure exits 2 and imports nothing;
   success establishes neither independence nor scientific eligibility. Review the
   actual content with its author before import; do not auto-approve uncertain data.
9. **Import legitimate assertions.** After operator handoff ends, use **Import an actual
   reviewer file** in Dataset & Evaluation with its matching job, or the supported CLI:

   ```powershell
   uv run taketwo-comparison import-review $newWorkspace --review $reviewJson --alignment $currentOriginalAlignment
   ```

   The importer validates again before immutable publication. Repeat with each actual
   reference/participant timing and participant flaw file. Preserve returned artifact
   paths. `validate --artifact` applies to imported envelopes, not raw reviewer exports.
10. **Check eligibility against the reviewed version.** Create comparison using actual
    imported reference/participant timing artifacts (repeat `--review` for each):

    ```powershell
    $comparison = uv run taketwo-comparison compare $newWorkspace --pair $pairId --reference-features $fRef.artifact --reference-alignment $aRef.artifact --participant-features $fMember.artifact --participant-alignment $aMember.artifact --review $referenceTimingA --review $referenceTimingB --review $participantTimingA --review $participantTimingB | ConvertFrom-Json
    uv run taketwo-comparison validate $newWorkspace --artifact $comparison.artifact --reproduce
    ```

    Missing rights, independent timing, text identity, support, acoustic quality or
    pitch eligibility withhold the affected scores; no weights are redistributed.
11. **Validate scientific splits and exact labels.** Use actual additional authorized
    speakers and connected families to support nonempty held-out groups. Keep every
    related take/derivative, speaker and connected source family together. One declared
    speaker/family cannot establish speaker-independent generalization. `split` is a
    deterministic grouping tool, not scientific validation:

    ```powershell
    uv run taketwo-dataset split $newWorkspace --seed 17 --ratios 0.5 0.25 0.25
    uv run taketwo-dataset validate $newWorkspace --reproduce
    ```

    Existing split warnings, missing test groups and disagreement must be resolved.
    Flaw agreement permits inspection tolerance; evaluation's `exact-inventory-v1`
    still requires exact active numerical inventories, full coverage and explicit
    revisions. Never split the five practice takes to manufacture held-out accuracy.
12. **Evaluate only eligible evidence.** Prepare the existing EvaluationConfig with
    actual reviewed dataset identity, held-out groups, annotation files and declared
    matching settings; the schema and examples are in [comparison tools](comparison-engine.md).

    ```powershell
    uv run taketwo-comparison evaluate $newWorkspace --report $comparison.artifact --review $flawReviewA --review $flawReviewB --config $evaluationConfig
    ```

    Precision/recall/F1, temporal agreement and eligible-zero are emitted only under
    their existing ground-truth gates. Exit 3/withheld metrics is not a successful
    accuracy result; operational input errors exit 2. Preserve configurations, native
    evidence, failed cases and hashes. Do not claim generalization from a pilot.

For acquisition, first write the intended claim and population (for example, held-out
speakers rather than repeated takes of this owner). Recruit authorized additional
speakers and independent speech families with documented processing/distribution scope;
keep a private consent ledger and avoid identifying public metadata. Collect matched
reference/participant speech with acceptable as well as potentially flawed examples,
including different recording conditions. Preserve originals and explicit transformations.
Have two actual independent reviewers follow the transcript, timing and flaw workflow
above, resolving disagreements transparently rather than promoting machine candidates.
Assign whole connected speaker/source-family groups to calibration and held-out sets
before tuning; exclude held-out groups from calibration and report actual split sizes,
label coverage, subgroup failures and uncertainty. Determine acquisition size from the
desired claims and precision of estimates before recruitment; five related practice
takes cannot supply that evidence. Report actual acquisition counts and missing labels;
this plan invents no participants, consent, temporal boundaries or accuracy.
Public data, demonstration/video and final report submission need separate owner and
rights approval. Everything above remains local unless explicitly authorized otherwise.
