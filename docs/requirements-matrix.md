# TakeTwo requirements matrix

Speech analysis workspace. Requirement IDs and acceptance criteria below map the
unchanged official statement to implementation and evidence. Software checks and
genuine processing have executed; independent scientific validation and the
full required public paired corpus remain incomplete. A preliminary five-recording
single-speaker pilot is now public, with four automatic, unreviewed alignments;
public availability does not supply independent ground truth. See [verification](verification.md)
and [submission readiness](submission.md#deliverables-and-current-evidence) for results and deliverables.

Authority: [official Track C specification](../requirments/Track%20C.pdf), all three pages, reviewed on 2026-10-11. Keep its existing path and bytes. SHA-256: `0e621d35e6bfdbb9d9e169b259ebf9d3d923d1efcbab38ba2a4331f6958fb280`.

## Official judging weights

| Criterion (page 3) | Weight | Primary phases |
| --- | --- | --- |
| Data Engineering & Stress Testing | 30% | 1, 2, 3, 5 |
| Causal Explainability & Temporal Grounding | 25% | 2, 3, 5 |
| Feature Extraction | 20% | 2, 3, 5 |
| Visualization & Dashboard | 15% | 4 |
| Reproducibility & Code Quality | 10% | All; release verification in 6 |

These weights total 100%. They determine delivery priorities, not the acoustic rubric's dimension weights.

## Required behavior and evidence

Status **Planned** means specified here, not implemented or verified. IDs R1a-R4b follow the PDF's numbered requirements. C rows cover the challenge; T rows cover technical considerations. Numeric gates elsewhere are proposed TakeTwo gates, not official thresholds. See the [requirements below](#required-behavior-and-evidence) for evidence ownership and the [risk register](verification.md#evidence-boundaries-and-open-requirements) for blockers.

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
| D1 | GitHub codebase and documentation | Repository / 6 | Public repository contains runnable code, setup and documentation | Pilot code tag uses `6c35e65`, passed [Windows CI](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38683403376); later documentation commits need their own CI | Public code/documentation available |
| D2 | Public custom paired dataset, transcripts and alignment labels | Dataset release / 6 | Files in GitHub or public Google Drive linked from README; rights permit release | [TakeTwo Pilot Dataset v1](https://github.com/Rhythm-Sanghi/TakeTwo/releases/tag/pilot-dataset-v1); [anonymous download/checksum evidence](dataset-publication.md#published-pilot-dataset-v1) | Partial: five genuine takes, author-approved CC BY 4.0 intended passage and four automatic alignments public. No independently reviewed transcript/flaw truth or public-speaker baseline; full requirement incomplete |
| D3 | Functional interactive dashboard prototype | Workspace / 4 | Demonstrates real upload, extraction and visual/text results | Recorded browser run and end-to-end tests | Local prototype implemented; genuine-reference and generated-pair runs verified, eligible human-pair demonstration open |
| D4 | Technical documentation, maximum 6 pages | Submission report / 6 | Covers dataset construction, rubric, architecture and scoring within six rendered pages | [Current report](../output/pdf/taketwo-technical-report-2026-10-15.pdf), page/content checks | Six-page historical snapshot retained; dataset-publication status superseded by D2 and submission documentation |
| D5 | 3-10 minute YouTube demonstration | Submission video / 6 | Shows collection, spectrum stress tests and specific caught deviations | [Owner-supplied demonstration](https://youtu.be/DfFTmNTAB6E) | Prior access/duration check; full narration/permissions require owner review |

These engineering documents are working specifications, not the six-page submission report. Implementation alone does not establish scientific or public-deliverable acceptance.

## Acceptance evidence

The [verification record](verification.md) consolidates actual engineering results,
failed attempts and historical sources. [Submission readiness](submission.md#deliverables-and-current-evidence)
tracks public links and remaining owner actions. The [review workflow](review-workspace.md)
and [human pilot kit](review-protocol.md#recording-preparation-and-participant-permissions) support independent evidence collection.
Software execution does not close scientific or publication gates.
