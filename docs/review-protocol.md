# Recording and independent review protocol

TakeTwo — Speech analysis workspace. This document provides procedures and blank
forms, not consent, reviewer approval, listening acceptance or ground truth. The
five private practice takes have no independently verified text/timing/flaw inventory
or public release approval. Use permitted isolated copies and keep completed forms,
recordings, operator keys and identity mappings private.

## Recording preparation and participant permissions

Select a substantive rights-cleared 15–25 s pilot excerpt, within the active analysis
budget (45 s by default). Preserve its master hash, native excerpt offsets, exact
spoken words, source attribution and item-specific permitted uses. The existing JFK
salutation is an unverified integration candidate with limited rhetorical variation;
it is not a verified script. Its original draft, IDs, master/sample hashes and rights
remain in the [acquisition ledger](pilot-collection.md). Two JFK speeches are one
speaker/group, not two independent baselines.

Obtain actual adult participant permission for the intended recording, processing,
annotation, adaptation and publication scope. Declining public release must remain
possible. Local upload permission cannot satisfy the broader cleared-rights policy.
Use the blank consent form below; do not infer rights from `self_recorded` origin.

## Recording directions

Record with one fixed microphone/distance/gain in a quiet room. Mono PCM WAV or PCM FLAC at 16/44.1/48 kHz is preferred; record device/settings/room/date and unavoidable AGC/processing. Disable enhancement where possible. Keep short natural room tone, no clipping, music, voice synthesis, denoising or post-recording loudness edits. Target 15–25 s; default analysis cap is 45 s (operators can lower the configured budget). Listen before import; re-record added/missing words or clipped takes. Preserve raw originals.

| Take filename suffix | Instruction to performer | Interpretation |
| --- | --- | --- |
| `natural.wav` | Read the exact script comfortably in your own voice | Clean/acceptable alternative candidate, not certified ideal |
| `near-perfect.wav` | Listen to reference; preserve phrase pacing, pause locations and emphasis while using your own voice | Near-reference candidate; do not impersonate the speaker |
| `mild.wav` | Make one modest local change to rate, pause or emphasis without changing words | Intended mild departure, requiring listening confirmation |
| `moderate.wav` | Make a clear sustained/repeated change in one designated dimension | Intended moderate departure, not automatic ground truth |
| `severe.wav` | Make a strong departure in pacing, pauses or dynamics while keeping every word intelligible and identical | Intended severe departure; re-record text errors |

Rotate target dimensions across families; include mixed flaws and acceptable alternative delivery. Record performer intention separately, hidden from flaw labelers. Do not prescribe guessed timestamp windows as detection output. Synthetic stress edits may be made later with saved recipes/time maps and explicit `origin=synthetic`; they do not become human takes.

An operator assigns one real reviewer/activity at a time in a fresh private browser,
keeps the operator key and closes analysis/peer tabs. End the handoff and close the
window before assigning the second person independently. Reviewers submit only their
own completed work. Identifiers, playback telemetry and interaction cannot prove
identity, comprehension or independence; a performer cannot supply their own independent
ground truth. Timing review assisted by MFA is not an independent MFA accuracy benchmark.
The [Review Workspace](review-workspace.md) is the UI/lifecycle authority.

## Transcript, timing, flaw review and scientific eligibility

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
## Independent annotation worksheet

Blank collection material; **not an imported review or ground truth**. Copy per reviewer and per recording. Fill fields only from actual listening and source artifacts. Use [the pilot kit](review-protocol.md#recording-preparation-and-participant-permissions) for CLI steps.

| Session binding | Actual value |
| --- | --- |
| Dataset version / recording ID / pair ID | |
| Speaker pseudonym / origin (source, self_recorded, synthetic) | |
| Audio canonical sample hash / transcript hash / original text hash | |
| Analysis implementation hash / original alignment payload hash | |
| Reviewer pseudonym / date / private evidence reference | |
| Independence from performer/other reviewer and conflicts | |
| Predictions and edit recipes hidden during flaw review? | |
| Full duration / listened intervals / unjudgeable intervals | |
| Decision (unresolved until actually completed) / notes | |

### Transcript and native timing

Listen to the whole clip before checking machine boundaries. Record exact words/repetitions and audible start/end edges. Preserve the original transcript and checked correction separately. Index canonical tokens from zero; intervals are native seconds, not the other track's clock. Repeat rows for **every token**. Do not fill human boundaries by copying machine values without listening.

| Token index / canonical word / spoken form | Draft machine start/end (s) | Human checked start/end (s) | Uncertainty / mismatch / listening note |
| --- | --- | --- | --- |
| | | | |

| Phrase half-open token span [start,end) | Native phrase / pause observation | Reviewer reason / disputed boundary |
| --- | --- | --- |
| | | |

Phrase spans must partition all tokens without gaps/overlap. Review each member separately. More than 200 ms disagreement or unresolved review blocks correspondence; retain both original records and use explicit superseding revisions after reconciliation. Human timing uncertainty is not a measured detection-confidence probability.

### Independent flaw inventory

Listen without predictions, rubric scores or intended edit locations. Use the reference as acoustic context; allow effective alternatives. Mark measurable differences separately from your subjective appraisal. Label only the four evaluation categories: pacing, pause_behavior, energy_variation, pitch_dynamics. Use a positive-width native interval, or a boundary anchor only for a missing/short pause. Never invent silence for an absent pause.

| Stable label ID | Category | Native start/end or pause anchor (s) | Severity 1/2/3 | Uncertainty (s or unknown) | Audible evidence / acceptable alternative / rationale |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Severity guide for human review: **1 mild** = local noticeable difference with delivery largely maintained; **2 moderate** = clear sustained/repeated departure; **3 severe** = strong pervasive departure that materially disrupts the intended delivery. These are provisional annotation anchors, not validated engine thresholds or judgments of persuasion/ability. Record disagreements; do not infer severity from a transformation parameter or automatic score.

| Inspected native span (s) | Acceptable/no-positive coverage | Recording-quality or alignment uncertainty | Reason / re-listen required |
| --- | --- | --- | --- |
| | | | |

No-positive labels require actual full listening coverage. Null uncertainty means unknown. Use dataset annotations for acceptable (severity 0), quality and alignment uncertainty; keep these out of comparison flaw `Label` records. Keep original independent sheets before reconciliation. The current evaluator requires two approved full-coverage blinded inventories with exactly equal numerical labels (category, location, severity and uncertainty); IDs and rationale are excluded from numerical agreement and retained in original reviews. Agree a reconciled inventory only after both people have reviewed it; preserve original differences with `supersedes` history. Record exclusions and missing categories rather than choosing the more favorable reviewer.

### Handoff checklist

The [Review Workspace](review-workspace.md) provides these fields, native playback, explicit word inspection, draft saves and submitted JSON export. Use this sheet as the private evidence reference or take notes directly. Phrase end numbers are one-based word counts in the UI; exported phrase spans remain zero-based half-open token intervals. Machine suggestions are never human ground truth merely because they were loaded. Record unclear/uncertain spans honestly, preserve independent originals and retain the separate adjudicator's explanation. The operator must end handoff and close the reviewer window before showing peer evidence.

- Exact provenance copied from actual current analysis; transcript verification agrees with the reviewed dataset version.
- Actual identities/date/evidence references and independence declarations completed; consent stored privately.
- Every word and complete phrase partition checked; no guessed timestamps.
- Full flaw-review listening coverage recorded; positives, acceptable alternatives and uncertainty preserved.
- Two separate original reviews retained; any revised records identify what they supersede.
- Review JSON validates/imports with existing CLI; detector inputs contain timing reviews only.
- Evaluation split/group identities were frozen before tuning; no held-out labels used for calibration.

This checklist records reviewer work when completed; blank fields and unchecked external actions are not approvals.

## Consent and recording provenance template

Copy per participant/source into private collection storage. **Blank form: no permissions or decisions are asserted.** The owner must agree a specific release scope with the participant before capture/publication. Keep names, signatures and contact details out of Git and public datasets.

| Private session field | To be completed by the actual collector/participant |
| --- | --- |
| Record ID / date / collector | |
| Participant name / adult eligibility confirmation | |
| Public speaker pseudonym / private identity-map location | |
| Family/work/script revision and transcript hash | |
| Recorded filenames / recording date | |
| Microphone, recorder, sample rate, channel, distance, gain | |
| Room/noise / AGC, enhancements or conversion used | |
| Intended delivery changes (kept hidden from labelers) | |
| Project contact / retention period / withdrawal contact and cutoff agreed | |

Discuss each permission separately and record **yes/no/unresolved**, the exact scope and any restrictions. An unresolved/declined public permission blocks redistribution; it does not become assent by leaving the row blank.

| Permission to be discussed | Decision / agreed scope / restrictions |
| --- | --- |
| Voluntary audio recording for TakeTwo analysis | |
| Local acoustic processing and independent annotation | |
| Creating controlled altered derivatives | |
| Public distribution of original/excerpt audio and transcript | |
| Public distribution of synthetic derivatives and annotations | |
| Inclusion in a hackathon demonstration/YouTube video | |
| Exact proposed audio/dataset license and public hosting destination | |
| Public pseudonymous metadata; excluded identifying information | |
| Withdrawal procedure before release and limits after public copying explained | |
| Questions answered / opportunity to decline | |
| Participant confirmation/signature/date; collector confirmation/date | |

Publish only a redacted permission summary if actually permitted. Metadata `consent_evidence` references this private record by stable ID; do not expose its filesystem path or identity mapping. Reviewers separately record independence/conflicts and actual listening evidence.

For source audio, also record original archive URL/item, creator/rights-holder, source/work IDs, access date, master hash, master-relative excerpt start/end, transcript source, item-specific license evidence, adaptation/redistribution permissions, required attribution and human baseline-selection rationale. Archive the actual evidence. Public availability alone is not a release decision.

## Product listening acceptance

**Actual human listening: pending.**
Software checks verify routes, native clocks and cancellation; they do not establish
that a listener finds the passage useful. This workflow is a product acceptance
exercise, not scientific ground truth or flaw-detection accuracy.

### Prepare

Use authorized private copies of `reference.wav`, `uneven.wav`, `natural.wav`,
`slow.wav` and `near-perfect.wav`. Preserve originals. Select the reference and one
participant, run or restore a completed analysis, and keep the dataset version,
job ID, source hashes and comparative method/implementation hash with the review.
No rights, text, phrase or annotation approval is implied by this exercise.

### Review each selected insight

1. Read the observation, native timestamps, **Why inspect**, listening question
   and item-specific limit. Explain why it was selected in your own words.
2. Play the reference segment, then the participant segment. Each uses its own
   native clock; do not assume matching timestamps or time stretching.
   Confirm that each starts at its displayed native timestamp and stops at its
   displayed end boundary. Record either discrepancy rather than treating a play
   event as successful acceptance.
3. Replay either passage as needed. Confirm the bounding words or acoustic change
   are inspectable and that playback stops at the intended end.
4. Inspect provisional transcript boundaries and waveform/energy evidence.
   Distinguish a machine word gap from measured low-energy support.
5. Record whether the measurement is audible or inspectable, whether the
   explanation helped, any misleading wording and additional evidence needed.
6. Select one or more review categories below. Record the listener's name/date
   only with their permission. Keep the notes private unless cleared for release.

For the restored reference/uneven anomaly, check `technology` → `is`: reference
10.93–11.88 s; participant 10.12–13.47 s. The participant's provisional gap is
10.50–13.39 s (2.890 s), with 0.000 s low-energy support and complete frame
support. Check audible words and alignment/transcript correspondence. Activity
can include noise; do not assume a pause, speech, incorrect pronunciation or a
proven alignment error. Fresh runs must use their own actual reported intervals.

### Guided session order

Work through one test at a time with the facilitator. Before advancing, the listener
reports audible content, usefulness and transport problems in their own words. Keep
the actual wording; separate any facilitator interpretation from the observation.
An unanswered test remains pending. Preparation or automatic playback is not a result.

1. **Uneven alignment anomaly.** Replay the existing `technology` → `is` card in
   reference / participant / reference order at unchanged comfortable volume. Describe
   the words and sounds inside the participant interval before classifying it. Check
   each native start/end and whether a bounding word is clipped. The 2.890 s machine
   gap and zero low-energy support do not prescribe what the listener should hear.
2. **Gap before `helps`.** In the retained uneven comparison use reference
   13.23–13.64 s and participant 14.35–15.06 s (provisional gap difference +0.560 s).
   Fresh runs must use their own reported intervals. Compare the
   transition into the word; report an audible difference or uncertainty, and whether
   assigned boundaries make the comparison understandable. Timing alone is not hesitation.
3. **Gap before `a`.** In the retained comparison use reference 15.39–15.98 s and
   participant 16.25–16.32 s (provisional gap difference −0.510 s).
   Check both clips, including the very short participant interval.
   Report if the bounded replay is technically correct but too short to interpret.
   Inspect surrounding recording context separately; do not silently change the finding's bounds.
4. **Energy observations.** The retained uneven group `g-b807761964c99fe6fae32f69`
   covers participant 0.00–1.50 s with two measured windows. Open that actual
   grouped observation and replay its native
   interval. Describe any audible level change and whether the explanation is useful.
   These are within-recording changes; they do not establish cross-take emphasis or cause.
5. **Transport.** Switch tracks while one is playing, replay the same selection twice,
   then return to the complete recording. Report overlapping audio, missing sound,
   incorrect cursor/bounds, a lingering stop boundary or unexpected speed changes.
6. **Other participant takes.** Repeat on `natural.wav`, `slow.wav` and `near-perfect.wav`
   using each completed analysis's actual selected observations and native intervals.
   Recording titles do not establish performance quality. Missing analysis or absent
   categories must be recorded as such; never invent a corresponding finding.
7. **Reference-only playback.** Restore the completed reference inspection. Play
   an actual selected observation, then use Inspect waveform and the native audio
   control. Record whether its identity and boundaries are clear, and whether
   absent participant controls or comparison language cause confusion.
8. **Full recording playback.** Clear bounded replay by using the native complete
   recording controls. Play the reference and uneven recording individually from
   their beginning to their end (retained durations 30.224375 s and 29.370 s).
   Record truncated words, unexpected stops, overlap, silence or failures actually
   heard. Switch tracks mid-play and verify that the previous track stops.

For every case, collect exact heard words/sounds, start/end clipping, switching
and overlap behaviour, any missing sound, and explanation usefulness before
assigning an outcome. Use **Passed**, **Failed**, **Inconclusive**, **Not performed**
or **Blocked**, separate from the observation categories below. A useful explanation
alone cannot pass an unheard playback test. Record a blocker and recovery action;
an unperformed or blocked case keeps overall human acceptance pending.

The earlier Test 1 response explicitly said human listening was not performed;
audible content and playback were unassessed. Its text-only observation about
2.890 s versus zero low-energy support is retained privately. It is neither a
listening pass nor proof of an alignment error. No later audible observation is
available. Do not overwrite this historical response with facilitator conclusions.

Classify **after** collecting observations: useful comparison, possible machine-alignment
problem, technically correct but not useful, misleading explanation, playback problem,
or inconclusive. Multiple categories may apply. A usability report of an alignment
problem does not become independent reviewed timing or scientific ground truth.
For a suspected defect, retain the exact card/job, control sequence, expected/observed
behaviour and repeat outcome. Reproduce it before changing code; recheck the affected
journey and relevant regressions afterward. Keep private listener notes outside Git.

### Listener entries

Repeat for each selected item in all four participant comparisons. Leave fields
blank until an actual listener completes them; do not prefill a favourable result.

| Field | Listener entry |
| --- | --- |
| Date / listener (with permission) | |
| Reference / participant / source hashes | |
| Dataset version / job / implementation hash | |
| Stable evidence ID / observation category | |
| Reference native interval / participant native interval | |
| Selection reason understood? Explain in own words | |
| Reference played / participant played / replay needed | |
| Provisional text and waveform/energy inspected | |
| Audible or inspectable? Describe evidence | |
| Explanation useful? Why? | |
| Misleading wording or navigation problems | |
| Additional evidence needed | |
| Review category or categories | |
| Outcome / reason / reproducible steps / repeat outcome | |

Categories: **Useful comparison**; **Possible machine-alignment problem**;
**Technically correct but not useful**; **Misleading explanation**;
**Playback problem**; **Inconclusive**. Earlier worksheet categories remain valid
historical notes; do not rewrite a completed review to fit the new labels.

Store completed notes separately from independent annotations. Do not import these
notes into review approval, score eligibility, calibration or accuracy metrics.
Actual screen-reader listening acceptance (Narrator/NVDA) is also pending. Use the
[separate spoken-accessibility worksheet](review-protocol.md#spoken-accessibility-acceptance) to
record focus, announcements and transport failures separately from axe results.

## Spoken accessibility acceptance

**Narrator/NVDA spoken acceptance: pending.**
No completed actual-listener record is available. Axe, keyboard-routing, native zoom
and PDF tagging checks do not establish spoken comprehension. This coding environment
does not provide a genuine audible screen-reader acceptance session.

### Prepare an actual Windows session

Record Windows, browser and screen-reader versions, listener/date (with permission),
dataset/job identity and viewport/zoom. Restart the local TakeTwo backend with the
current code before testing. Use authorized private recording copies; preserve originals.
Start Narrator with **Windows + Ctrl + Enter**, following the
[official Microsoft commands](https://support.microsoft.com/en-us/accessibility/windows/narrator/appendix-b-narrator-keyboard-commands-and-touch-gestures).
Prefer a separate NVDA run when available; use its
[official user guide](https://download.nvaccess.org/documentation/userGuide.html).
In NVDA browse mode, `H` navigates headings and `B` buttons; `NVDA + Space` switches
browse/focus modes. Use Tab/Shift+Tab to test actual control focus as well as reading.
Keep speech output audible to the reviewer; reading a DOM snapshot is not this test.

### Test steps and expected understanding

| Step | What the listener must verify | Actual result / problem |
| --- | --- | --- |
| Workspace navigation | Names, current area and keyboard focus are understandable | |
| Recording selectors | Reference/participant identities and selected values are spoken | |
| Run/restore analysis | Loading, processing completion and failures are announced without repeated noise | |
| Opening result | Listener can identify recordings, measured differences and unverified status without a graph | |
| Selected heading | Finding category and supplied-text context are understandable | |
| Native timestamps | Each recording's independent start/end and units are understandable | |
| Why inspect / Listen for | Listener can explain the selection reason and uncertainty | |
| Replay reference / participant | Button names, audio switching and stopping bounds are understandable | |
| Inspect waveform | Focus moves to the intended recording's native audio control | |
| Expand evidence | Disclosure state and complete source measurements are reachable | |
| Export both reports | Summary/full purposes and controls are distinct; cancelling restores the workspace | |
| Safe failure/retry | Error and recovery are spoken; stale source results do not remain active | |
| Reference-only repeat | No nonexistent participant or paired differences are presented | |
| Native 200% repeat | Focus, reading and controls work without a visual-only workaround | |
| Dataset readiness | Selected recording/version and all six prerequisite statuses, missing evidence and next actions are spoken | |
| Evaluation unavailable/retry | A failed request is announced as unavailable; recovery distinguishes a successful zero inventory | |
| Dataset PDF export | Export name, print guidance, failure recovery and restored focus are understandable | |

Record inaccessible controls, missing/duplicate announcements, unexpected focus moves,
ambiguous wording and graph-dependent conclusions. Repeat failed steps after fixes.
Classify each step **Passed**, **Failed**, **Inconclusive**, **Not performed** or
**Blocked**, with exact
spoken observations; leave all fields blank until an actual reviewer performs them.
No automatic review, scientific approval, rights clearance or publication decision
results from completing this worksheet.
