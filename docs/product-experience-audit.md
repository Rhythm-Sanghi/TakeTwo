# TakeTwo product experience repair — 13 October 2026

Speech analysis workspace. Frontend redesign on the existing `master` branch,
starting at `47e9b38`. Workshop + Gridline + Studio Utility remains the design
language. Verification was executed on 13 October; local finalization is on
14 October 2026. No backend, acoustic-v1, delivery-v0, thresholds, contracts, resource
limits, source identities or review independence rules changed.

## Information architecture and completed workflows

| Area | Before | After |
| --- | --- | --- |
| Recording Library | Import and a long metadata/transcript panel | Import and real pair actions first; metadata and source transcript in a disclosure |
| Analysis Workspace | Configuration, two long tracks and inspector before the assessment | Selected pair, separate processing/assessment state, conclusion and next action; measured summary, findings, paired listening, then technical evidence |
| Rubric and Evidence | Formula/threshold table first | Meaning, required evidence and backend result for pacing, pauses, energy and pitch; shared requirements once; math and diagnostics secondary |
| Review Workspace | Continuous editor with submission controls at the bottom | Assigned-scope navigation, acknowledged save state, actual validation requirements and submitted/validated indicators; editors remain mounted |
| Dataset and Evaluation | Twelve-row count table first | Readiness and recording-specific next action; honest takes/IDs/families/transcript summary; inventory and instructions in Details |

The main journey is import reference → import participant → choose pair → run →
read assessment/findings → listen/explore → follow Dataset readiness → prepare an
authorized independent review → save/validate/submit → rebuild reviewed evidence
and rerun. Rights and reviewed dataset versions still require the documented CLI;
opening Review Workspace does not grant rights or reviewer access.

For the supplied reference/uneven comparison the primary conclusion is exactly
“Audio analysis complete. Delivery assessment awaiting verification.” Plain-language
requirements identify unverified spoken identity/transcripts, unresolved recording
rights and missing independent timing reviews. Duration, feature artifacts,
automatic alignment artifacts and reliable pitch coverage remain diagnostics.
Null scores remain null. There are no fabricated findings or success percentages.

Not processed, queued/running, failed, cancelled, report loading/unavailable,
processed pending, partial dimensions, eligible comparison and eligible-zero
findings have distinct presentation. Eligible findings retain actual severity,
native intervals or boundary anchors, explanation, observation measurements,
uncertainty and seek/replay actions. Replay plays only the participant interval;
both tracks seek to their own contract locations. Equal timestamps never imply
synchronization. Independent evaluation requires a bound stored eligible human
run with real-validation status, metrics and matching report, dataset,
implementation and policy hashes. Software-fixture metrics cannot enable it.

No aggregate workspace eligible-pair count or authenticated-person count exists
in the API. The interface states that limitation, presents selected-report
eligibility and retains recording-scoped backend review status. Stored independent
assertions are never promoted into verified human independence.

## Implementation and defects

`AnalysisResult`, `Findings`, `RubricGuide`, `Rubric` and `ReviewJourney` extract
cohesive presentation responsibilities from the large workspace components.
There is no new dependency, frontend detector or scoring/validation rules engine.
Native audio, real waveform/feature APIs, alignment, excerpt saving, pair correction,
review import, adjudication, JSON/CSV exports and immutable history remain available.

Repairs include selected-interval playback stopping at its actual end; a new seek
clears the old bound. Failed continuous playback heartbeats retain their unaccepted
span for the next actual playback update rather than silently losing coverage.
Seeking/stopping still clears continuity and backend real-time/listening gates are
unchanged. Step navigation uses buttons and focus/scroll, preserving the URL
fragment reserved for reviewer capability activation. Draft/save conflicts retain
unsaved edits. Completion comes exclusively from backend validation/submission,
never from visiting steps or changing a field.

Visual iteration removed repeated rubric blockers and an orphan third-column
layout. Technical evidence prints even when its disclosure is closed; raw values,
controls and unavailable/loading correspondence are omitted. The existing
three-page Analysis Summary and separate six-page technical report are preserved.

Intermediate browser runs exposed obsolete selectors for deliberately closed
disclosures. Tests now open the relevant details as users do. Windows also reset
a reused upload socket after long CPU/chart inspection. Generated import testing
uses a fresh request context per upload and never blindly retries a mutation.
Read-only dataset/mode checks may reconnect after the same idle-socket reset.
An observed rejected listening heartbeat left a true gap and correctly blocked
submission; the frontend continuity repair retains the backend requirement.

## Executed evidence

Fresh pre-edit baseline: **322 Python tests passed**, one existing Starlette/httpx
warning; **31 frontend tests passed**. Logs are `local-data/experience-baseline-*`.
Before screenshots of all five areas are `local-data/experience-before-*.png`.

Final execution on Windows with Chromium 156.0.8078.4:

| Check | Actual result |
| --- | --- |
| Python | 322 passed in 320.73 s; one existing Starlette/httpx warning |
| Frontend | 37 passed, including status distinctions, bound evaluation, scope navigation, interval stopping and rejected heartbeat continuity |
| TypeScript / ESLint / Prettier | Passed |
| Ruff check / format | Passed; 65 Python files already formatted |
| Lock / contracts / schemas | Lock check passed; regenerated frontend contract unchanged; four schema snapshots, official PDF hash and 310 local links passed |
| Production packages | Vite build and Python wheel/source distribution built successfully; frontend JS 382.51 kB, 121.34 kB gzip |
| Complete generated browser suite | 6 passed, none skipped, in 9.1 minutes; actual import/process/playback/export/cancel/retry/excerpts, five widths, native zoom, 15/29/30/40/45 s domains/printing, software UI states and immutable review/adjudication |
| Genuine-copy accessibility / responsiveness | 25 area/width audits, zero axe violations; no document overflow at 1920, 1366, 800, 390 and 320 px |
| Native 200% zoom | Factor 2.0, DPR 1 → 2, layout width 1600 → 800; completed chart loaded in 1436 ms; automated focus/geometry/axe passed |
| Genuine scientific export | Equal to the supplied report JSON; scores still unavailable; all 11 preserved input/manifest/database files unchanged |
| Print | New private A4 summary is 3 pages, 203432 bytes; all three rendered pages inspected; earlier summary and separate technical report retained |
| Release / private-data preflight | 167 candidates and 453 reachable history blobs checked before commits; no blocking candidate, history or package findings; no personal absolute paths |

The final successful browser run still logs nonfatal Windows Proactor connection-
reset diagnostics during navigation. This is retained as a platform limitation;
a green suite is not a claim that every platform issue is resolved. Spoken
screen-reader and manual native-zoom visual acceptance remain incomplete.

Private screenshots,
generated review exports, runtime logs and PDFs remain ignored local artifacts.
They are not submission data or release contents.

The genuine five-take verification uses `local-data/experience-private-copy`, a
separate copy with SQLite backups of the supplied workspace. No source recording,
original manifest/database, review draft or supplied report is edited. The genuine
report export is compared to the supplied JSON. Five-width all-area screenshots
and axe evidence are `local-data/experience-after-*` and
`local-data/experience-visual-checks.json`. The new private print artifact is
`output/pdf/taketwo-analysis-experience.pdf`; the earlier analysis PDF is retained.

The generated browser suite uses actual HTTP imports, extraction, playback,
cancellation/retry, excerpt saving, review isolation, immutable exports and
adjudication. The separate `zz-experience` test explicitly intercepts report
responses only to exercise software loading/partial/eligible/eligible-zero states.
Its regions and scores are UI fixtures, never saved scientific evidence or speech
accuracy. Its eligible-findings screenshots say software fixture in the evidence
explanation. The explicitly named software-fixture screenshots also cover report
loading, partial dimensions, eligible evidence without enough scores, and eligible
zero findings. Actual empty/import/processing/cancelled states, assigned drafts,
unsaved/validated reviews and immutable submission were captured and inspected.
Sixty final browser screenshots and associated JSON evidence are preserved under
`local-data/experience-browser-final`. Stable examples include
`local-data/experience-state-empty-workspace.png`,
`local-data/experience-state-processing.png`,
`local-data/experience-software-eligible-findings.png` and
`local-data/experience-review-guided-1366.png`. Assigned reviewer screenshots use
generated software tones and assertions, never genuine human approval.

Actual native zoom uses an isolated Chromium extension and `chrome.tabs.setZoom`
and `getZoom`, not CSS zoom, device-scale emulation or a changed user browser.
Automated focus, geometry and axe checks are separate from manual visual/spoken
acceptance. Headless native-zoom screenshot capture has a known blank/cropped
capture limitation. Narrator/NVDA speech has not been verified.

## Remaining scientific and submission limits

The five private takes are one person's practice recordings, not independent
participants or a public licensed corpus. Rights, transcript identity, independent
timing/flaw review, real validation, calibration, held-out accuracy and cross-speaker
generalization remain unresolved. Low reliable pitch coverage remains visible;
there is no policy relaxation or synthetic substitute. Genuine eligible speech
findings and independently validated accuracy cannot be visually accepted from
these inputs; software fixtures only check presentation and interaction.

Spoken screen-reader acceptance, manual native-zoom visual acceptance, clean
second-environment reproduction, public dataset/video/report approval and final
submission remain separate owner/human work. No push, dataset publication, release
upload or Devpost submission is performed. Codex assistance is disclosed in
[attributions](attributions.md); software tests do not conceal missing human work.


## Local handoff

Implementation and regression coverage: `92bff74` (outcomes, findings, guided
review and supporting workflow documentation). This audit and its entry-point
links are a separate documentation commit. Both remain local on `master`; no push
or publication was performed. Final post-commit status and release-history checks
are retained in `local-data/experience-final-git.txt` and
`local-data/experience-release-final.log`.
