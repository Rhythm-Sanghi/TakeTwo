# Mobile refinement audit — 14 October 2026

TakeTwo — Speech analysis workspace. Focused frontend refinement of local
`master`, starting at `be45b565cadd660951701d6f4d46c53958086f1d` with a clean tree.
Permanent root engineering/product standards remain in [AGENTS.md](../AGENTS.md).

## A. Reproduced issues and causes

| Visible issue | Confirmed cause | Correction |
| --- | --- | --- |
| Task below mobile history | Shared collection/history preceded every main page | Mount the complete collection only in Recording Library |
| Large phone navigation | Five desktop buttons wrapped across rows | Native labeled selector below 600 px; desktop row retained |
| Clipped cards | Horizontal mobile lists with minimum card widths | Vertical list, wrapping names/IDs and complete control width |
| Excessive analysis length | Both complete tracks stacked; correspondence/diagnostics primary | Explicit track switch below 801 px; secondary disclosures |
| Repeated rubric wording | Same unavailable explanation and direction repeated per dimension | Shared requirements once, four short summaries, details retained |
| Unclear review context | Analysis selection and assignment appeared related; key came too early | Separate comparison/assignment labels and ordered preparation |
| Repeated readiness warnings | Independence/rights caveats repeated around inventory and controls | Next action first, inventory second, shared caveats disclosure |
| Presumed provenance | Public reference selected without operator choice | Required placeholder; existing contract values preserved |
| Redundant history status | Job state and terminal stage printed together | One terminal state, actual participant when known, job details |

The fresh baseline executed 37 frontend tests and two relevant existing browser
checks successfully. Before screenshots measured the 320 px page heading at
615 px and assessment conclusion bottom at 861.56 px in a 740 px viewport.

## B. Information architecture

Recording Library retains imports, collection, metadata, pairing, correction and
history. Focusable shortcuts reach collection/history and import without paging
through the vertical list. Existing navigation reaches it from every workspace.
History restores the stored reference/pair; incomplete participant metadata is
explicitly unavailable. Full IDs, stage and original request remain in disclosures.

Analysis begins with actual pair, processing state, assessment and next action.
Measured durations/pitch coverage follow; feature/alignment diagnostics, reviewed
correspondence and scientific details remain accessible. No score is inferred.
Mobile track buttons pause playback explicitly and preserve mounted audio/selection
state. Wide displays retain paired native timelines. Replay remains directly
available; numerical fields, zoom, excerpt saving and chart tables are preserved.

Review shows current analysis context separately from the assignment recording.
Preparation follows recording, activity, reviewer declaration, original alignment
when required, operator authorization and start. Missing prerequisites explain
disabled start. Authorization help never displays the secret. Existing handoff,
draft, isolation and immutable submission protections remain in force.

Rubric uses one requirements list and four compact summaries. Observation counts,
coverage, score eligibility, reason codes, thresholds, weights and mathematical
policy remain in disclosures. Dataset readiness shows its backend next action
before real inventory counts, review/version/evaluation details and caveats.
Speaker IDs and review assertions remain declarations rather than authenticated
people. Import requires deliberate provenance type; participant-from-reference
continues to choose the actual existing participant contract value explicitly.

## C. Actual screenshots

Both first-viewport and full-page PNGs exist for all five areas at 320, 390, 800,
1366 and 1920 px, before and after: 100 images in ignored `local-data`.
Names follow `mobile-{before|after}-{width}-{area}-{viewport|full}.png`, with spaces
in area names replaced by hyphens. These contain private evidence and are not
committed or published. Geometry files are `mobile-before-geometry.json` and
`mobile-after-geometry.json`.

| Width | After heading top | After assessment conclusion bottom | Document overflow |
| --- | --- | --- | --- |
| 320 | 183 px | 425.56 px | None |
| 390 | 183 px | 382.88 px | None |
| 800 | 165 px | 344.19 px | None |
| 1366 | 128 px | 311.09 px | None |
| 1920 | 128 px | 311.09 px | None |

The 320/390 first viewport now contains the genuine pending-verification
conclusion and real next action. Inspected mobile Review, Dataset and Rubric
screens show their own tasks without shared history. The 1920 full screenshot
shows both waveform/acoustic panels side by side.

## D. Interaction verification

The final fresh generated-workspace suite passed all seven browser cases:
import/processing/native playback/export; five-width controls; native 200% zoom;
15/29/30/40/45 s chart domains/counts/review navigation/print; loading/partial/
eligible finding/eligible zero-region presentation; mobile independent audio state;
and review handoff/playback/immutable export/adjudication. No cases were skipped.

Mobile switching paused playback and retained each track's native cursor and
numeric interval. Selected replay stopped at its endpoint. Waveform dragging,
zoom, excerpt saving, history request restoration and pair selection passed.
Review checks retained capability denials, isolation, draft preservation,
completion/validation and immutable submission behavior. Technical disclosures
expanded; software findings sought/replayed their independent native intervals.
Software eligibility fixtures test presentation only; they do not create genuine
speech findings or independent human approvals.

## E. Accessibility

The genuine copied workspace passed axe with zero violations for all 25
area/width combinations and zero document overflow. Navigation uses native
keyboard controls, labeled options, page heading focus and visible focus outlines.
Mobile buttons/selects have at least 44 px control height. Numeric interval fields
and accessible measurement tables remain alternatives to canvas interaction.

Actual Chromium 200% tab zoom passed using an isolated extension's native
`chrome.tabs.setZoom/getZoom`, doubled DPR and halved layout viewport, with
geometry/focus/axe coverage. CSS scaling is not substituted. Headless zoom
screenshots retain a known blank/cropped capture limitation; manual native-zoom
visual acceptance and Narrator/NVDA spoken acceptance remain open.

## F. Regression and print evidence

Fresh full Python execution: 322 passed, one existing Starlette/httpx dependency
deprecation warning. Frontend: 39 passed, two files. TypeScript, ESLint, Prettier,
Ruff lint/format, lock check and production build passed. Four saved schemas match
runtime; generated frontend API contract is unchanged. Official Track C PDF hash
is unchanged. Built wheel/sdist and release/private-data preflight passed without
blocking findings; this is a pattern/inventory check, not proof of all rights.

Final browser run: 7 passed, 0 failed, 0 skipped. The initial full run had 5 passes
and 2 failures: the new responsive helper inspected navigation before mount,
and reviewer help text changed the field's accessible name. The helper now waits
for the navigation landmark; the field has its original explicit name and help
via `aria-describedby`, with unit coverage. Both targeted cases then passed,
followed by the complete fresh successful run. The initial run also logged a
nonfatal Windows Proactor socket-reset diagnostic. Browser `NO_COLOR` warnings
are runner-environment notices.

Executed logs: `local-data/mobile-{python,frontend-final,types-final,lint,
format-final,build-final,schema-final,e2e-final,precommit}.log`. Final browser
artifacts are in `local-data/mobile-final-results`; the private screenshot index
is `local-data/mobile-screenshots.md`. No existing tests were removed.

The private `output/pdf/taketwo-mobile-analysis-summary.pdf` has three A4 pages
and 204173 bytes. Generated from the actual copied pair at 320 px with participant
active, after both audio plots finished loading. Poppler rendered all three pages;
visual inspection confirmed reference waveform/plot, participant waveform/plot,
unavailable-score table, provenance and original measured evidence. The hidden
track's waveform is synchronously redrawn for print. No raw table dump, blank
chart or clipped axis appeared. Existing print/JSON contracts are preserved.

## G. Scientific integrity and limits

No changes to Python backend, scientific tests, scripts, environments or lockfile.
`acoustic-v1`, `delivery-v0`, consensus, ground truth, rights, independence,
thresholds, abstention, resource limits, contracts and artifact identities remain
unchanged. The copied genuine report exactly equals the user-supplied JSON;
overall and dimension scores remain null and delivery assessment awaits
verification. All 11 checked private source hashes (five WAVs and source workspace
manifests/databases) match the fresh pre-change baseline.

Private screenshot/PDF evidence is ignored. No push, publication, Devpost
submission, genuine approval, source-recording mutation or capability bypass was
performed. Genuine independent review, rights resolution, held-out accuracy and
human accessibility acceptance remain external work. AI assistance is disclosed
in [attributions](attributions.md).

## H. Local handoff

Implementation and regression coverage: `9178961`. This audit and related workflow
documentation are committed separately. Both commits remain local on `master`.
Final commit identity, clean status and post-commit release evidence are reported
at handoff and retained in `local-data/mobile-final-git.txt` and
`local-data/mobile-release-final.log`.
