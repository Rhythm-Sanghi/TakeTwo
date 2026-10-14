# Track C submission compliance

Current release pass: 15 October 2026. Application code is public at `9938bd8`;
local and fetched remote HEAD matched. Its [Windows Actions run 38615636707](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38615636707)
was still running at preparation. See [current release evidence](publication-readiness.md).

## Current official deliverables

| Deliverable | Status | Evidence / remaining action |
| --- | --- | --- |
| Public GitHub code/documentation | Application public; new release documents await approval | `master` 9938bd8; verify final exact-SHA CI after authorized publication |
| Public paired audio/text/alignment labels | Unresolved mandatory requirement | No approved, independently reviewed corpus or public URL; five private takes remain excluded |
| Interactive prototype | Local software verified; human acceptance partial | Five workspace areas, genuine processing, native replay and exports; listening and spoken accessibility remain pending |
| Technical document <=6 pages | Current source/PDF prepared for owner review | [Current report](../output/pdf/taketwo-technical-report-2026-10-15.pdf); historical PDF retained; publication awaits approval |
| YouTube demonstration 3-10 minutes | Unresolved mandatory requirement | Script exists; no supplied video/URL or verified public playback |
| Devpost submission | Manual owner action | [Fields and checklist](submission-draft.md); no receipt |

The deadline and portal must be checked by the owner against current organizer rules.
No software-fixture metric closes scientific acceptance. The matrix below is retained
as dated historical evidence; its old publication statuses do not describe this release.

This is the historical Phase 5 readiness snapshot. Current product repairs and the later user-supplied private practice takes are recorded in [product validation](product-validation.md) and [the recording guide](recording-import-guide.md). No newly supplied take is automatically a verified/public competition example; official scientific/public deliverable gates remain open.

TakeTwo — Speech analysis workspace. Audit date: 2026-10-12; baseline `9551d73`. Authority: all three pages of the unchanged [official statement](../requirments/Track%20C.pdf). The October 15 deadline comes from the project owner's instruction, not this PDF. This is a local preparation audit, not submission certification.

Statuses: **implemented** = working code exists; **validated** = stated scope has executed evidence; **incomplete** = some required work remains; **blocked** = missing external inputs prevent acceptance; **not applicable** = outside the stated requirement. Software and scientific acceptance are separate. No mandatory requirement is dismissed as not applicable.

| Official requirement | Software / component | Scientific or deliverable acceptance | Evidence and remaining gate |
| --- | --- | --- | --- |
| Challenge: reproducible custom rubric | Validated: comparison engine, fixed delivery-v0, replay | Blocked: perceptual calibration/valid human scores | [Scoring policy](scoring-policy.md), [Phase 3 tests](phase3-validation.md); no calibrated confidence |
| Challenge: actionable feedback | Implemented: numeric explanations and replay guidance | Blocked: independent listening/explanation audit | Every region binds measurements; no genuine eligible regions available |
| R1a: effective public speakers, transcribed | Validated: import/provenance tools; genuine source ingestion | Incomplete: two JFK masters, one unverified 17.3 s salutation; no substantive verified baseline | [Acquisition ledger](pilot-collection.md); both masters share one speaker group |
| R1b: exact-text severe-to-near-perfect mirrors | Validated: canonical identity, human import, synthetic transformations | Blocked: no consented participant recordings or reviewed spectrum | Intention/recipe strength never substitutes for listening severity |
| R1c: accurate temporal labels, training/testing | Validated: annotation/review contracts, connected-group splits | Blocked: zero independent human labels; no valid held-out corpus | [Recording kit](human-pilot-kit.md), [worksheet](annotation-worksheet.md) |
| R2a: forced alignment | Validated: native CPU MFA word/phone output | Blocked: independent boundary accuracy | 19 words/115 phones on genuine source; automatic repeatability is not accuracy |
| R2b: acoustic footprint | Validated: FFT/MFCC/RMS/energy/pYIN/activity extraction | Incomplete: cross-speaker/noisy/flawed-speech validation | Genuine frames measured; accepted F0 fraction 0. Rates/pauses withheld with unverified text. Vocal clarity is not independently scored |
| R3a: exact flaw start/end | Validated: native-time region/event software and matching fixtures | Blocked: human region IoU/boundary benchmark | Phrase/word/gap resolution is declared; missing pauses are anchors |
| R3b: structured mathematical rationale | Validated: hand calculations, evidence templates | Blocked: independent genuine explanation audit | Explains the trigger, not a proven psychological cause |
| R4a: audio/transcript uploads | Validated: actual local HTTP/browser workflow | Incomplete: eligible human-pair acceptance | Real import/MFA/features/playback/export; error/recovery tests |
| R4b: overlay, highlights, explanations | Validated: generated-signal correspondence/evidence tests; genuine native tracks | Blocked: genuine reviewed pair overlay/flag demonstration | Numeric alternatives, keyboard seeking; no hardcoded regions |
| T1: quality before quantity | Implemented: provenance/QA/publication gates | Incomplete: release-worthy corpus | Strict gates retained rather than declaring draft sources complete |
| T2: speaker-agnostic comparison | Validated: median-centered dB, relative semitones, invariance fixtures | Blocked: independent cross-speaker results | No per-recording variance normalization; speaker fairness unmeasured |
| T3: sufficient temporal precision | Implemented: correspondence/coverage/uncertainty gates | Blocked: independent timing/region evaluation | Human annotations and engine uncertainty remain distinct |
| T4: repeatable runs/environments | Validated: same-Windows replay, locks/hashes | Incomplete: clean second-environment replay | No cross-platform equivalence claim |
| D1: GitHub code and documentation | Incomplete: local package/commits prepared | Blocked: owner review and public release verification | Existing remote URL alone does not verify publication of this work |
| D2: public paired audio/transcripts/alignment labels, README link | Implemented: release preflight/export tools | Blocked: missing real corpus, release and public download audit | [Publication guide](dataset-publication.md); no public dataset claimed |
| D3: functional prototype | Validated: local Windows prototype, real reference workflow | Incomplete: valid human-pair demonstration/accessibility review | Four workspaces use actual backend contracts |
| D4: technical document, maximum six pages | Validated: six-page PDF rendered and visually inspected | Incomplete: final evidence reconciliation/owner approval; current document is a draft | [Editable report](technical-report.md), [Phase 5 evidence](phase5-validation.md) |
| D5: 3–10 minute YouTube demonstration | Incomplete: five-minute script/checklist prepared | Blocked: genuine caught-deviation evidence, recording/upload/public verification | [Script](demo-script.md); no uploaded video |

Official judging weights: **Data Engineering & Stress Testing 30%; Causal Explainability & Temporal Grounding 25%; Feature Extraction 20%; Visualization & Dashboard 15%; Reproducibility & Code Quality 10%**. They sum to 100% and are unrelated to the four equal rubric weights.

Stress testing has executed known-signal, gain/register, malformed media, clipping/silence, timing, cancellation/crash/cache and resource-limit checks. These validate software. Human severity ordering, acceptable alternatives, difficult alignment and speaker generalization remain blocked. Prior evidence: [Phase 4B](phase4b-validation.md); current executed checks: [Phase 5](phase5-validation.md).

The original [requirements matrix](requirements-matrix.md) retains requirement IDs and acceptance criteria. This final audit governs current readiness. Prior phase reports are dated historical evidence, not claims about today's complete corpus. Human and public-artifact actions are consolidated in [ACTION-REQUIRED](ACTION-REQUIRED.md).
