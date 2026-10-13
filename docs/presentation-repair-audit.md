# Dataset, evidence, chart and print repair - 13 October 2026

TakeTwo - Speech analysis workspace. Started clean on `master` at
`e071ce943c886f0d7c25f5c63f22ae591fad0514`. Local commits only; no push, external
publication or submission. Root AGENTS.md remains unchanged and authoritative.

## Baseline and evidence

Executed baseline: **316 Python passed**, zero failed/skipped, one existing
Starlette/httpx warning, **156.91 s**; **21 frontend passed**, **17.09 s**.
Inspected the supplied comparison JSON and all five rendered pages of the browser
printout found in Downloads. No separate screenshot attachment was available;
the populated Dataset screen was reproduced read-only. Existing frontend/API/CSS,
review/scoring/accessibility documentation and tests were inspected before changes.

The actual private inventory has **five recordings, four participant takes, one
controlled reference, one declared speaker ID and one connected family**. Verified
transcripts, independent submitted assertions, timing/flaw reviews, public-source
candidates and synthetic derivatives are zero. Machine alignment/processing exist;
overall score is null with no eligible regions. Those conditions were preserved.

## Confirmed findings

| Finding | Cause and correction | Verification |
| --- | --- | --- |
| P2: takes labeled participants | Frontend filtered recordings but implied people. Backend summary now separates takes, IDs and existing connected groups. | Failing-before regressions for four takes/one ID, linked/unrelated speakers/families and empty inventory pass. |
| P2: disconnected readiness guidance | Static CLI-only text ignored browser review and progress. Backend derives recording actions from manifest, existing review consensus/binding and processing; navigation preselects operator preparation. | Rights, partial transcript, reviewed version, processing, timing/flaws/disagreement tests; missing capability stays 403; active handoff still blocks dataset/peer APIs. |
| P2: sparse pitch appeared representative | Non-null baseline lacked reliability context. It is now diagnostic accepted-F0 median with actual percent coverage, stored mask, per-phrase minimum, backend eligibility and score availability. | High/low/zero coverage, missing baseline/input/gate and independent available dimension tests. |
| P2: repeated blockers | Four dimension sections repeated shared reasons. Unique shared messages appear once; disclosures retain dimension restrictions, coverage/counts/minimums and technical codes. | Deduplication/disclosure, null overall score and zero-region abstention regressions. |
| P2: paper canvas clipping | Paper layout narrowed while uPlot retained screen pixels. Print hooks synchronously snapshot the existing plot at readable paper width; screen resize respects the actual container without the former 260px floor. | Five real generated durations across five widths; supplied native charts complete in the printed PDF. |
| P2: poor browser print layout | No print system. A4 styles hide controls/raw tables, preserve identity/eligibility, avoid small-panel splits and provide compact print-only input measurements. | Real Chromium PDF with all disclosures open; three A4 pages rendered and visually inspected. Live tables remain after printing. |
| P3: loading mistaken for empty readiness | A visual capture briefly showed import guidance before inventory arrived. Readiness now separates loading, unavailable and genuinely empty states; populated captures await actual counts. | Focused loading-versus-empty component regression and final browser integration checks. |
| P2: unnecessary cold readiness I/O | Summary parsed large completed feature histories even when unverified text made processing irrelevant to the next action. It now defers those reads until text is verified. | Failing-before no-artifact-read regression; final six focused backend cases and complete suite pass. No processing or scientific gate changed. |

Changed modules: dataset/workspace.py; web/contracts.py, app.py, readiness.py;
additive OpenAPI/TypeScript adapters; frontend DatasetReadiness, App, ReviewWorkspace,
Evidence, Timeline, TokenOverlay, plotPrint and CSS; focused Python/component/E2E
tests and documentation. No acoustic/comparison implementation files changed.

## Timeline diagnosis and scientific integrity

Supplied durations: **30.224375 s / 29.370 s**. Existing downsampled RMS responses
reach frame centers **30.1925 s / 29.3525 s** with 999/1000 plotted points. The
roughly 22-second visible print cutoff is not truncated extraction. Frame centers,
incomplete terminal supports and extrema downsampling differ from recording bounds.
Chart domains explicitly retain each native viewing window, with full recording or
selected window stated beside identity. Unequal tracks retain separate seconds.
Empty and all-null series remain unavailable rather than receiving invented values.

Actual pitch baselines **186.7 / 198.3 Hz** remain diagnostic. Accepted coverage is
**0.60% / 0.51%**, converted from stored fractions. Confidence 0.8, the per-phrase
50% requirement, acoustic-v1, delivery-v0, independent-review requirements and null
scoring are unchanged. No React scores, interpolation, invented contours/metrics,
approvals or identity claims were added.

A disposable private mirror used read-only SQLite backup and copied manifest/audio/
derived artifacts. Its served scientific report was deeply equal to the supplied
JSON. No private evidence was regenerated. Generated browser review fixtures stay
separate from genuine recordings. Historical PDFs, official statement and the
separate hackathon report were not edited or overwritten.

## Verification and retained failures

Final backend: **322 passed**, zero failed/skipped, one existing warning,
**186.14 s**. The preceding 321-test run passed in 207.87 s; runtime differences
are not controlled speed gains. Final frontend: **31 passed**, zero failed/skipped, **6.52 s**.
TypeScript, ESLint, Prettier, Ruff lint/format and production frontend build passed.

Initial inventory tests failed on absent fields. A new API regression caught nested
readiness models being serialized as plain JSON; explicit model dumping fixed it.
Component checks found missing-gate handling; absent pitch eligibility now leaves
other dimensions intact. Ambiguous test queries and incomplete fixture metadata
were corrected without weakening production validation.

One edit used Windows' default encoding, corrupting separator glyphs; browser import
failed its exact-count assertion. UTF-8 was restored. That initial browser attempt
had **one failed/four passed**, with the generated-duration case passing in **5.6
minutes**. Retained traces also contain a nonfatal Windows connection-reset callback.
The first full Python attempt had **320 passed/one failed** because a new Pair test
fixture omitted required intent/identity fields. The corrected fixture and subsequent
complete 321-test run passed. These attempts are retained, not represented as success.

Full generated browser suite: **five passed**, zero failed/skipped, **4.6 minutes**;
the five-duration case passed in 2.7 minutes. Final targeted workspace integration
passed **two tests in 1.0 minute**, zero failed/skipped, after the loading refinement.
The completed populated-chart native **200% zoom** rerun passed **one test in 24.5 s**,
zero failed/skipped, with focus/axe across all five areas. Chromium 156.0.8078.4
reported zoom 2.0, viewport 1600 to 800 and DPR 1 to 2. The actual chart loaded in
6,565 ms. DOM geometry and axe passed; native-zoom screenshots were blank or cropped
on this headless setup, including the nonblank full-document capture. They are not
accepted as complete visual evidence. **Human visual acceptance at 200% remains
INCOMPLETE**, separate from successful native zoom automation and normal-width
chart/print inspections. These scoped reruns are not another
complete five-test suite run.

The first enhanced zoom attempt passed before inventory loaded and did not enter
its optional populated branch; it is not populated-chart evidence. Waiting for
readiness exposed the unnecessary summary reads above. Subsequent cold-chart
attempts exceeded the default five-second visibility assertion (including an idle
attempt); their failures remain retained. The chart wait now uses the same explicit
30-second completed-report delivery budget as the existing workflow, with measured
load time recorded. No production timeout changed, and a universal latency repair
is not claimed. A nonfatal connection-reset callback also appeared in the successful
zoom run. Fresh populated private-copy captures separately verify the final UI.
Locked dependency validation passed; Python/npm audits found no known vulnerabilities.
Bandit scanned **7,565 lines**, zero medium/high findings and zero scan errors
(eight low-severity inventory findings). The final package/history preflight is
recorded at handoff. All **11 files in this task's private snapshot remain unchanged**;
original WAVs, manifests/databases and existing evidence were preserved.
Automated focus/axe/native zoom do not substitute for genuinely heard Narrator/NVDA
acceptance. Same-host checks do not establish a clean second-machine replay.

## Printed output and evidence locations

Owner-review PDF: `output/pdf/taketwo-analysis-summary.pdf`, explicitly Git-ignored
because it contains private recording evidence. This is a browser analysis summary,
not the six-page hackathon report. Three A4 pages preserve independent native charts,
job/dataset/recording identity, shared blockers, null scores, RMS/peak/energy, pitch
diagnostics and zero reviews. Poppler renders were inspected for width, labels,
legibility, margins, page breaks and unwanted controls. Raw disclosures are omitted
even when open; the live accessible tables remain available. Tagged/spoken PDF
accessibility is not claimed.

Private `local-data/presentation-*` contains baseline captures/PDF, populated
Dataset/Analysis captures at 1920/1366/800/390/320, browser traces, extraction/domain
measurements and print renders. Those artifacts are excluded from Git.

## Remaining human actions

Rights/consent, independent transcript/timing/blinded flaw review, explicit revisions,
reviewed dataset creation, valid family-disjoint evaluation and release permission
remain genuine human/external gates. One declared speaker and one connected family
cannot establish independent generalization. No accuracy result was manufactured.
Save open drafts and restart the original service when idle to load the additive
backend fields, then refresh. The original service was not restarted for this task;
old-server missing fields display unavailable rather than guessed counts. Scientific
comparison/evaluation and original alignment binding remain final authorities.

Engineering commit: `690cd7d`. The final verification/documentation commit, clean
tree, unchanged remote and final package/history preflight are identified in the
handoff. No additional branch or external publication was created.
