# Product completion audit

TakeTwo — Speech analysis workspace. Started 14 October 2026 on clean `master`
at `01203ff386dfda6f8d4c1f45f18b255402c2dcc9`. Root AGENTS.md is the only
applicable repository instruction file. Official Track C's three pages were
read; its six-page technical-documentation limit and separate human dataset,
labeling, accuracy and publication obligations remain in force.

## Stage A: baseline and reproduction

Fresh baseline: 322 Python tests, 43 frontend tests and 8 browser cases passed.
One existing Starlette/httpx deprecation warning and nonfatal Windows Proactor
socket-reset diagnostics occurred. TypeScript, ESLint, Prettier, Ruff lint/format,
production/package builds, schemas/local links, npm/pip dependency audits and
release/private-data preflight passed. Baseline evidence is ignored under
`local-data/completion-baseline-*`; no historical test count substitutes for this run.

An authorized isolated copy of the genuine workspace returns five recordings,
four human-recorded participants, one controlled reference, one declared speaker
ID, one connected family, zero verified transcripts and zero submitted reviews.
Fifteen original/private/report files have a fresh SHA-256 preservation baseline.

Controlled browser failures reproduce all-or-nothing refresh: `/reviews` returning
503 hides the five successful recordings and `/dataset` response. A structurally
incomplete summary (`inventory_counts={}`, `review_readiness=[]`) reproduces five
takes with indefinite unavailable counts and no response-shape diagnosis. This
establishes code defects, not the exact cause of an earlier unseen server response.
Current healthy backend counts are correct; no missing human review is called a bug.

Before images: ignored `local-data/completion-before-analysis-390.png`,
`completion-before-readiness-390.png`, `completion-before-unrelated-failure.png`
and `completion-before-incomplete-readiness.png`. Network/reproduction evidence:
`completion-readiness-reproduction.json`.

## Severity and category inventory

| ID | Priority/category | Evidence and required action |
| --- | --- | --- |
| PC1 | P1 confirmed defect | Refresh uses one Promise.all for eight independent APIs; one rejection suppresses successful updates. Separate result/error state and reject obsolete requests. |
| PC2 | P1 confirmed defect | Readiness accepts incomplete dictionaries/default empty readiness; missing data gets generic text without diagnosis/retry. Distinguish zero, unknown, restricted, unavailable and server failure. |
| PC3 | P1 confirmed partial-failure weakness | Dataset inventory, immutable review parsing and review DB lookup share one failure path. Preserve authoritative recording inventory if review evidence cannot load; never invent zero review counts. |
| PC4 | P1 missing useful capability | Completed acoustic artifacts contain energy/activity/quality information, but the primary result largely reports formal abstention. Add a separate versioned exploratory artifact and interpretation. |
| PC5 | P1 missing useful capability | Stored low-energy supports lack an end-user observation list/replay/export distinct from formal flaw regions. Add explicit unverified acoustic candidates with method/config/native timing. |
| PC6 | P2 product weakness | Automatic word timestamps are buried in disclosures and there is no clearly separate provisional pair correspondence/rate explanation. Expose only structurally supported automatic evidence. |
| PC7 | Scientific limitation | Genuine accepted F0 coverage is about 0.3–0.6%; previous controls implicate confidence/window interaction. Repeat diagnostic study; no threshold relaxation or score unlock without independent F0 evidence. |
| PC8 | Performance investigation | Each validated HTTP artifact can re-decode source audio; worker startup/MFA/pYIN costs dominate. Measure caches, stages, memory and summary overhead before claiming optimization. |
| PC9 | Platform investigation | Nonfatal WinError 10054 recurs; prior atomic state sharing already has bounded retry. Retain reproducible evidence and test operational failures; no universal fix claimed from a later pass. |
| PC10 | Human/external dependency | Independent transcripts/timings/flaws, rights, cross-speaker collection, calibration, held-out accuracy, spoken accessibility and publication approval remain absent. Do not bypass gates. |

## Architecture and preservation boundaries

Dataset schema/storage/audio/workspace/splits/transform modules own immutable
originals, canonical 16 kHz mono derivatives, provenance, pairing and versions.
Analysis contracts/alignment/features/storage own actual MFA outputs, complete
native frame supports, pYIN masks, activity/energy, FFT/MFCC, quality and hashed
artifacts. Their implementation digests cover their own package; preserve these
files and `acoustic-v1` so historical acoustic artifacts remain valid.

Comparison eligibility/engine/reviews/matching/evaluation/storage own scientific
gates, native correspondence, deterministic rubric/regions, exact-inventory ground
truth, matching and metrics. Their package digest is independent of a new
exploratory package. Preserve `delivery-v0`, consensus, thresholds and historical
reports. Automatic candidates must never become Review/Label/Region records.

Web imports/contracts/app/readiness adapt these engines. SQLite Jobs uses WAL,
five-second busy timeout and bounded queue; disposable workers preserve valid
stages and atomic publication. Kernel supervision owns cancellation, crash recovery,
600 s timeout and 4 GiB worker-tree commit. ReviewWorkspace uses a separate lifecycle
database, scoped capability, immutable submissions, revisions and adjudication.
Its middleware denies every general API during handoff, including future endpoints.

Frontend API/generated schemas, App selection/report state, imports/tools,
timelines/plots, outcomes/findings/rubric, readiness and reviewer/editor consumers
were traced against backend contracts and historical defect audits. Keep the five
areas, compact phone selector, mounted native track switching, reference-inspection
states and validated report identity protection. Baseline suites cover imports,
native playback, interval replay, history, printing, review/draft/immutability,
five-width accessibility and real Chromium 200% tab zoom.

## Staged implementation plan

1. Repair independent readiness state and partial backend evidence failures.
2. Add `exploratory-v1` outside acoustic/comparison packages: compact summaries,
   explicit frame-derived acoustic candidates, provisional alignment and provenance.
3. Integrate useful results, native replay and separate verified assessment.
4. Add JSON/interval CSV and native searchable print reports; retain historical PDFs.
5. Repeat pitch/practical scoring studies and real-copy checks without inventing labels.
6. Measure performance/reliability; fix demonstrated defects only.
7. Execute the complete regression/security/visual checks, update guides/report,
   and commit verified stages locally. No push, release or private publication.

Stage outcomes, measurements, actual counts and remaining acceptance gates will
be appended as execution completes. This initial audit does not mark later work done.
