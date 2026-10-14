# Workspace design and interaction

Dataset and Evaluation now separates takes, declared speaker IDs and connected
families using backend counts. A recording selector exposes its next rights/review/
version/processing/evaluation step. **Open Review Workspace** preselects recording,
available job and scope without creating a session or granting access. Rights and
reviewed-version changes still require real evidence and the CLI procedure in the
[human pilot kit](human-pilot-kit.md).

Shared comparison blockers appear once above a dimension table. Native disclosures
retain specific restrictions, counts, coverage, minimums, recovery and reason codes.
Pitch baselines are diagnostic medians of accepted F0 frames; percent coverage,
stored confidence mask, backend eligibility and score availability remain separate.
The policy's 50% requirement applies per scored phrase, not to a new React score.

**Print analysis summary** uses standard browser printing. Choose the browser's Save as PDF destination for searchable text; an external system printer may rasterize. Reference inspection prints identity, processing status, relevant use requirements, native waveform/plot and compact actual measurements, without comparison scores. Paired output retains the agreement/evidence tables. A4 styles retain native
windows, recording/job/version identity, summaries, blockers and unavailable scores;
controls, raw chart tables and unavailable correspondence help are omitted. Live
tables and exports remain available. Synchronous print hooks snapshot the existing
uPlot at readable paper width without a second acoustic renderer or PDF service.
This private summary is separate from the hackathon report. See [executed repair
evidence](presentation-repair-audit.md).

Current addition: **Review Workspace** is the fifth navigation area. It prepares recording-scoped sequential handoffs and operator adjudication. Handoff reloads into an isolated editor with actual playback/waveform, separate original/MFA/corrected text, millisecond word-boundary dragging and numeric alternatives, phrase partitions, unclear speech, flaw intervals/pause anchors, draft persistence/completion checks and immutable submission/export. The analysis application is not mounted during handoff. Read [review workflow](review-workspace.md) for instructions and identity/blinding limits, and [verification](review-workspace-validation.md) for actual browser/accessibility evidence. Existing four-area workflows remain available outside handoff.

TakeTwo — Speech analysis workspace. React/strict TypeScript/Vite implement the [Workshop + Gridline + Studio Utility tokens](design-system.md). System fonts, 4 px spacing, restrained teal/reference and brown/dashed participant signals, 1 px rules and compact native controls remain consistent. The focused feature modules include `AnalysisResult`, `RubricGuide`, `Rubric`, `ReviewJourney`, `ImportForm`, `Timeline`, `TokenOverlay` and `Evidence`; there is no UI framework, icon pack, animation dependency or dashboard generator.

The five connected areas are Recording Library, Analysis Workspace, Rubric and Evidence, Review Workspace, and Dataset and Evaluation. The full collection/history lives only in Recording Library; existing navigation keeps it accessible from every task. Phones use a labeled native workspace selector. Collection entries form a vertical mobile list with wrapping filenames and secondary job details. Recording type requires an explicit choice, independent of the readable reference selector: public source, self-recorded controlled reference, or human participant. The initial form asks for file/text, optional title and actual local processing permission. Source/speaker, rights and recording details are disclosures; no internal IDs are requested. Unknown public rights remain null/pending. Intended labels default to unspecified/null. Imported UI text is always unverified. A participant inherits the explicitly chosen reference's family/work, with canonical-word mismatch rejected; this is an intended relationship, not proof of spoken identity. See [the first-time recording guide](recording-import-guide.md).

History uses readable recording names and correctly converted UTC timestamps, reopening the original reference/pair and saved artifacts. **Retry this analysis** submits the failed/cancelled attempt's exact request. Successful import waits for inventory refresh and selects the actual new pair. **Correct this pairing safely** prepares a separate two-recording version and restart guidance, preserving old data and resetting review/intent assertions. Explicit excerpt saving within the API-advertised duration (default 45 s) uses the selected track's native samples and requires its actual cut transcript. Transcript/rights corrections still need a reviewed new version; there is no unsafe artifact editing/deletion. Evaluation inventory separates controlled references from human participants and supports actual review-file import without granting approval. New web reports retain bound dataset snapshots; unrelated imports preserve history, while changed used inputs/reviews/code are refused.

## Audio and acoustic tools

Native HTML audio supplies accessible play/pause/volume and supported WAV playback; only one track plays at once. At 800 px and below, Reference audio / Participant audio buttons switch between mounted tracks; switching pauses playback while preserving each native cursor and interval. Replay is directly accessible; precision fields remain in a disclosure. Actual sample min/max envelopes are drawn with a small canvas renderer. Zoom/pan operates on native seconds; seek inputs use sample-resolution steps at 16 kHz. Dragging the waveform selects an interval; numeric start/end fields provide the keyboard alternative. Native audio controls show current time/duration. Precision playhead samples and numeric selection controls remain in the interval disclosure. Replay stops at the selected end; a new seek clears that bound. Word buttons seek actual automatic alignment intervals and explicitly label them unreviewed.

Reference and participant have separate native axes and cursors. Selecting a grounded region or boundary event seeks both using its independent contract locations, with no invented silence interval. Previous/next inspection uses real region records. When no reviewed correspondence exists, affected synchronization controls are disabled with an adjacent reason. The matched-word overlay appears only after backend eligibility/review gates pass; it plots backend-computed median normalized energy/pitch on canonical word index, with native word-start seeking and an accessible measurement table. It is not a wall-time overlay or a hidden time warp.

uPlot renders actual windowed RMS, dBFS/relative energy, F0/relative pitch, energy-based activity and spectral centroid. Legends, axes, units, native clocks, frame/hop and aggregation labels accompany charts. Pitch retains null gaps; empty pitch is explicitly unavailable. Aligned pause/rate evidence is shown only when returned by the engine; eligible pacing observations appear in the numeric region inspector. No frontend formula detects or scores flaws.

The inspector shows actual input quality/baselines/frame counts/provenance even during abstention. A selected region displays category, severity, both locations/anchors, original observations, deltas/tolerances/excess/penalty/coverage, normalization, eligibility and deterministic engine explanations. Confidence/timing uncertainty remain unavailable until measured. JSON/CSV exports use the validated backend report; null scores are never replaced with zero.

## Accessibility and limits

Semantic landmarks/headings, labeled forms, real table headers, a skip link, focus outlines, keyboard-native controls, navigation heading focus and polite stage announcements support keyboard and assistive use. Canvas/chart information has numeric seek/selection controls and real data tables. Signals use role names and solid/dashed strokes as well as color. Layout reflows below 1250/800 px; reduced-motion preferences disable optional motion. No pointer-only chart action is required for evidence inspection.

Stage/import/waveform/feature loading statuses use live regions; the moving playhead is not continuously announced. Each track's seek, pan, selection and feature controls has a distinct accessible name. A pending waveform replaces the previous recording/window rather than displaying stale samples. Scrollable tables and numeric chart alternatives accept keyboard focus. Automated axe, keyboard/focus/playback, desktop/800/320 px checks and visual review are recorded in [Phase 4B validation](phase4b-validation.md). Actual screen-reader speech remains unverified. Native 200% Chromium zoom has automated geometry, focus and axe coverage; headless screenshot capture has a known clipping limitation, so manual native-zoom visual acceptance remains separate. Genuine eligible paired-region inspection depends on human mirror/transcript/timing collection; software fixtures do not establish real speech accuracy.

The shared `TAKETWO_MAX_ANALYSIS_DURATION_S` setting accepts integer seconds 1–45, default 45. Restart after changing it. See [duration configuration and verification](duration-validation.md).


## Outcome-first journey

Import a reference and participant in Recording Library, then choose the pair and
Run analysis in Analysis Workspace. The first panel identifies both recordings and
separates processing from scientific assessment. A completed unverified comparison
says **Audio analysis complete. Delivery assessment awaiting verification.** Its
requirements explain unresolved transcripts, rights and independent timing reviews.
The next action opens Dataset and Evaluation for authoritative readiness guidance.
Duration, available artifacts and reliable pitch coverage are diagnostic evidence.

Findings appear before the audio tools. Eligible backend regions retain category,
severity, both native locations, explanation, supporting observation measurements
and uncertainty. Inspect and seek navigates both native positions; Replay participant
interval plays only the participant interval and stops at its end. A boundary event
has a seek action, never a fabricated positive interval. Eligible zero findings and
unavailable detection have different explanations. Partial dimensions remain visible
in Rubric and Evidence without producing an overall score.

The paired transports sit side by side on wide screens and stack below 1250 px.
Waveform navigation, sample-resolution seek and acoustic charts are supporting
exploration. Precision selection/replay, word alignment, score calculations,
provenance and scientific exports remain accessible in native disclosures. Print
uses the same compact evidence summaries even with technical disclosures closed.

Rubric and Evidence starts with what pacing, pauses, energy and pitch mean, required
evidence, backend eligibility and score availability. Shared blockers appear once;
dimension details retain unique requirements. Thresholds and math are secondary.
An independent-evaluation statement requires a stored eligible human run with real
validation, metrics and matching report/dataset/implementation/policy hashes.
Software-fixture evaluation never enables that statement.

Dataset and Evaluation opens with readiness and the next actual recording action.
Counts distinguish takes, recorded speaker IDs and connected families. The API does
not expose an aggregate eligible-pair count or authenticate independent people;
the UI says so and shows selected-report eligibility and recording-scoped review
status rather than estimating totals or completion percentages.

Assigned reviewers get four scope-specific navigation buttons: Listen, Check transcript /
Inspect timing / Annotate flaws, Notes and uncertainty, Validate and submit. Navigation does not modify the capability URL fragment. All
editors stay mounted; navigation does not save, approve or access peer evidence.
Save state reflects server acknowledgement and unsaved edits. Completion badges
appear only after backend validation of the saved draft or immutable submission.
Remaining requirements use backend validation issues without a second rules engine.
Operator key, revision and session provenance stay available in disclosures.

Reference inspection is separate from delivery comparison. Completed reference processing leads with **Reference audio analysis complete** and selects an existing participant or prepares an import. Applicable reference rights/transcript requirements are secondary. Reports are bound to job ID/path, request/pair and actual input recording IDs; selection/history changes clear obsolete results synchronously. See [reference and print verification](reference-inspection-audit.md).
