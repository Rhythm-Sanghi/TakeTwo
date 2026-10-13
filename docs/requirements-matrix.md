# TakeTwo requirements matrix

Speech analysis workspace. Dataset tooling and Phase 2 alignment/acoustic tooling are implemented. Genuine source acquisition and native CPU execution are documented in [pilot collection](pilot-collection.md) and [validation](phase2-validation.md). Independent human dataset/timing evidence and official deliverables remain incomplete. Phase 3 software evidence is in [validation](phase3-validation.md); independent detection accuracy remains unavailable. Phase numbers follow the current [roadmap](implementation-roadmap.md).

Authority: [official Track C specification](../requirments/Track%20C.pdf), all three pages, reviewed on 2026-10-11. Keep its existing path and bytes. SHA-256: `0e621d35e6bfdbb9d9e169b259ebf9d3d923d1efcbab38ba2a4331f6958fb280`.

## Official judging weights

Current product stabilization and newly supplied private practice takes are tracked in [the issue audit](product-audit.md), [validation](product-validation.md) and [recording guide](recording-import-guide.md). Controlled-reference software support does not close R1a or independent scientific/publication gates. Prior reports retain their historical acquisition/evaluation status.

| Criterion (page 3) | Weight | Primary phases |
| --- | --- | --- |
| Data Engineering & Stress Testing | 30% | 1, 2, 3, 5 |
| Causal Explainability & Temporal Grounding | 25% | 2, 3, 5 |
| Feature Extraction | 20% | 2, 3, 5 |
| Visualization & Dashboard | 15% | 4 |
| Reproducibility & Code Quality | 10% | All; release verification in 6 |

These weights total 100%. They determine delivery priorities, not the acoustic rubric's dimension weights.

## Required behavior and evidence

Status **Planned** means specified here, not implemented or verified. IDs R1a-R4b follow the PDF's numbered requirements. C rows cover the challenge; T rows cover technical considerations. Numeric gates elsewhere are proposed TakeTwo gates, not official thresholds. See the [roadmap](implementation-roadmap.md) for evidence ownership and the [risk register](risk-register.md) for blockers.

| ID / source | Requirement | Component / phase | Acceptance criterion | Required evaluation evidence | Status |
| --- | --- | --- | --- | --- | --- |
| C1 / p1 challenge | Reproducible custom rubric scores | Scoring policy, report / 3 | Versioned formulas yield repeatable scores from fixed inputs; unavailable evidence yields unavailable scores | Repeat-run report and hand-calculated fixtures | Implemented; numerical/replay tests, real scores withheld |
| C2 / p1 challenge | Actionable delivery feedback | Region explanations, UI / 3, 4 | Each flag states measured delta, interval, context and a review action | Explanation audit against report values and audio | Deterministic numeric templates implemented; independent audio audit pending |
| R1a / p1 | Source and transcribe effective public speakers | Acquisition manifest / 1 | Real public-speech references have verified transcripts, rights and baseline-selection rationale | Source/license ledger and transcript review log | Partial: one imported draft candidate; reviews pending |
| R1b / p1 | Same-text flawed spectrum from severe to near-perfect | Paired recordings, transformations / 1 | Exact canonical transcript shared across pairs; mild, moderate, severe and near-perfect examples; synthetic origin explicit | Listening QA, recipe hashes, severity coverage table | Tooling implemented; human spectrum missing |
| R1c / p1 | Accurate paired labels and temporal bounds for training/testing | Annotation schema, split manifest / 1, 2 | Every annotated interval is in range, reviewed and linked to a pair; families cannot cross splits | Schema validation, adjudication log and leakage audit | Schema/split checks implemented; independent labels missing |
| R2a / p2 | Forced transcript-to-audio alignment | MFA pipeline / 2 | Word intervals monotonic and checked against independent manual boundaries; failures exposed | Boundary-error distribution, coverage and failure log | Native automatic execution verified; accuracy unmeasured |
| R2b / p2 | Acoustic footprint extraction | FFT, MFCC, F0, energy, rate, pauses / 2 | Actual samples produce documented, unit-bearing features; clarity limitations explicit | Signal fixtures and inspected real contours | Implemented; signal tests and real-audio extraction executed |
| R3a / p2 | Exact start/end times of significant delivery deviations | Region detector / 3 | Region bounds remain in participant time and link to corresponding reference words | Held-out region IoU and boundary-error results | Detectors/matching implemented; reviewed real accuracy unavailable |
| R3b / p2 | Structured mathematical rationale for each region | Evidence records / 3 | Explanation identifies feature, reference, participant, signed delta and threshold | Independently recomputed evidence audit | Hand-calculated fixtures pass; independent human audit pending |
| R4a / p2 | Interactive audio and transcript uploads | API, upload workflow / 4 | Valid pair runs through real engine; invalid files/transcripts return recovery guidance | Browser test with real licensed audio plus error cases | Real source import/processing/browser export verified; legitimate reviewed pair remains open |
| R4b / p2 | Time-series overlay, highlights and explanations | Comparison workspace / 4 | Reference/participant features share explicit correspondence; clicking a region seeks correct audio | Browser seek tests and manual timeline review | Native waveform/play/seek and feature plots verified; eligible real-pair overlays/regions await human evidence |
| T1 / p2 | Quality before quantity | Dataset QA / 1 | Exclude ambiguous or unlicensed pairs; publish coverage gaps | Inclusion/exclusion ledger and dataset card | Planned |
| T2 / p2 | Speaker-agnostic pitch/energy normalization | Comparison engine / 2, 3, 5 | Relative pitch/energy retain dynamics while reducing register/gain dependence | Cross-speaker and gain/register stress tests | Implemented; gain/register fixtures pass; cross-speaker evaluation pending |
| T3 / p2 | Temporal precision sufficient for explanation | Alignment and detector / 2, 3, 5 | Report timing error and abstain when correspondence is unreliable | Manual boundary audit and uncertainty examples | Eligibility/abstention implemented; manual benchmark pending |
| T4 / p2 | Reproducibility across runs/environments | Config, locks, manifests / all | Fixed hashes/config reproduce decisions; numeric differences bounded and documented | Clean Windows rerun and second-environment comparison | Same-Windows feature replay verified; other environments pending |

The PDF calls R3b "causal" explainability. TakeTwo will explain the calculation that triggered a flag and its delivery context. It will not infer anxiety, intent, health or a proven human cause from acoustic association.

## Official deliverables

| ID / source p2 | Deliverable | Component / phase | Acceptance criterion | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | GitHub codebase and documentation | Repository / 6 | Public repository contains runnable code, setup and documentation | Public master verified at 35a1486; repair CI pending authorized push | Published code; CI verification incomplete |
| D2 | Public custom paired dataset, transcripts and alignment labels | Dataset release / 6 | Files in GitHub or public Google Drive linked from README; rights permit release | Public download check, manifest checksums and dataset card | Planned |
| D3 | Functional interactive dashboard prototype | Workspace / 4 | Demonstrates real upload, extraction and visual/text results | Recorded browser run and end-to-end tests | Local prototype implemented; genuine-reference and generated-pair runs verified, eligible human-pair demonstration open |
| D4 | Technical documentation, maximum 6 pages | Submission report / 6 | Covers dataset construction, rubric, architecture and scoring within six rendered pages | PDF page count and visual/content review | Planned |
| D5 | 3-10 minute YouTube demonstration | Submission video / 6 | Shows collection, spectrum stress tests and specific caught deviations | Public video link, duration and chapter checklist | Planned |

These engineering documents are working specifications, not the six-page submission report. No official deliverable is marked complete merely because Phase 0 is complete.

## Phase 4 integration evidence

The [Human Review Workspace](review-workspace.md) adds real browser authoring of the existing hash-bound transcript, timing/phrase and blinded-flaw evidence contracts, with separate adjudication history and existing consensus/eligibility. This supports R1 labeling, R2 timing validation, R3 temporal evidence, R4 interaction and reproducibility; it does not itself complete any human dataset/accuracy gate. Acceptance evidence and remaining human/manual accessibility actions are in [review validation](review-workspace-validation.md). Official judging weights and all original acceptance criteria remain unchanged.

Current submission readiness is reconciled requirement by requirement in the [Phase 5 final compliance audit](submission-compliance.md). It supersedes historical readiness labels below without changing official criteria or weights. The six-page report draft and manual/public release gates are tracked there; no complete dataset or submission is claimed.

[Phase 4 validation](phase4-validation.md) records the real local service/workspace, actual browser audio import/alignment/extraction/playback/export, typed contracts, software tests and remaining acceptance gates. Local success does not complete public dataset/report/video deliverables or establish independent detection accuracy.

[Phase 4B validation](phase4b-validation.md) adds verified Windows process-crash recovery, bounded workers, retry, cache reuse and all-workspace narrow/accessibility checks. The [human pilot kit](human-pilot-kit.md) supplies recording and review procedures. R1/R2 accuracy/R3 real detection and D2 remain blocked by absent participant recordings and independent annotations; no metric or calibration claim closes those gates.

Current repair status (2026-10-13): five genuine private practice recordings remain outside Git and lack independent ground truth/public consent. Structured semantic flaw agreement, maximum-cardinality evaluation and journaled review publication are covered by software regressions; they do not close R1–R3 human-data gates. MIT licenses original code/documentation only. See [final repair audit](final-repair-audit.md).

Current hosted-verification and deliverable status is in [CI/submission verification](ci-submission-validation.md). The three audited repair commits are public; new changes remain local. Historical phase readiness is not current remote status.
