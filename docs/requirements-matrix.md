# TakeTwo requirements matrix

Speech analysis workspace. Phase 1 now provides dataset tooling, documented in [dataset engineering](dataset-engineering.md). No competition dataset, speech-analysis engine, dashboard or evaluation result exists yet. The Planned statuses below refer to complete official behavior/deliverables, not an absence of partial tooling.

Authority: [official Track C specification](../requirments/Track%20C.pdf), all three pages, reviewed on 2026-10-11. Keep its existing path and bytes. SHA-256: `0e621d35e6bfdbb9d9e169b259ebf9d3d923d1efcbab38ba2a4331f6958fb280`.

## Official judging weights

| Criterion (page 3) | Weight | Primary phases |
| --- | --- | --- |
| Data Engineering & Stress Testing | 30% | 1, 2, 5 |
| Causal Explainability & Temporal Grounding | 25% | 2, 4, 5 |
| Feature Extraction | 20% | 3, 5 |
| Visualization & Dashboard | 15% | 6 |
| Reproducibility & Code Quality | 10% | All; release verification in 7 |

These weights total 100%. They determine delivery priorities, not the acoustic rubric's dimension weights.

## Required behavior and evidence

Status **Planned** means specified here, not implemented or verified. IDs R1a-R4b follow the PDF's numbered requirements. C rows cover the challenge; T rows cover technical considerations. Numeric gates elsewhere are proposed TakeTwo gates, not official thresholds. See the [roadmap](implementation-roadmap.md) for evidence ownership and the [risk register](risk-register.md) for blockers.

| ID / source | Requirement | Component / phase | Acceptance criterion | Required evaluation evidence | Status |
| --- | --- | --- | --- | --- | --- |
| C1 / p1 challenge | Reproducible custom rubric scores | Scoring policy, report / 4 | Versioned formulas yield repeatable scores from fixed inputs; unavailable evidence yields unavailable scores | Repeat-run report and hand-calculated fixtures | Planned |
| C2 / p1 challenge | Actionable delivery feedback | Region explanations, UI / 4, 6 | Each flag states measured delta, interval, context and a review action | Explanation audit against report values and audio | Planned |
| R1a / p1 | Source and transcribe effective public speakers | Acquisition manifest / 1 | Real public-speech references have verified transcripts, rights and baseline-selection rationale | Source/license ledger and transcript review log | Planned |
| R1b / p1 | Same-text flawed spectrum from severe to near-perfect | Paired recordings, transformations / 1 | Exact canonical transcript shared across pairs; mild, moderate, severe and near-perfect examples; synthetic origin explicit | Listening QA, recipe hashes, severity coverage table | Planned |
| R1c / p1 | Accurate paired labels and temporal bounds for training/testing | Annotation schema, split manifest / 1, 2 | Every annotated interval is in range, reviewed and linked to a pair; families cannot cross splits | Schema validation, adjudication log and leakage audit | Planned |
| R2a / p2 | Forced transcript-to-audio alignment | MFA pipeline / 2 | Word intervals monotonic and checked against independent manual boundaries; failures exposed | Boundary-error distribution, coverage and failure log | Planned |
| R2b / p2 | Acoustic footprint extraction | FFT, MFCC, F0, energy, rate, pauses / 3 | Actual samples produce documented, unit-bearing features; clarity limitations explicit | Signal fixtures and inspected real contours | Planned |
| R3a / p2 | Exact start/end times of significant delivery deviations | Region detector / 4 | Region bounds remain in participant time and link to corresponding reference words | Held-out region IoU and boundary-error results | Planned |
| R3b / p2 | Structured mathematical rationale for each region | Evidence records / 4 | Explanation identifies feature, reference, participant, signed delta and threshold | Independently recomputed evidence audit | Planned |
| R4a / p2 | Interactive audio and transcript uploads | API, upload workflow / 6 | Valid pair runs through real engine; invalid files/transcripts return recovery guidance | Browser test with real licensed audio plus error cases | Planned |
| R4b / p2 | Time-series overlay, highlights and explanations | Comparison workspace / 6 | Reference/participant features share explicit correspondence; clicking a region seeks correct audio | Browser seek tests and manual timeline review | Planned |
| T1 / p2 | Quality before quantity | Dataset QA / 1 | Exclude ambiguous or unlicensed pairs; publish coverage gaps | Inclusion/exclusion ledger and dataset card | Planned |
| T2 / p2 | Speaker-agnostic pitch/energy normalization | Comparison engine / 3, 5 | Relative pitch/energy retain dynamics while reducing register/gain dependence | Cross-speaker and gain/register stress tests | Planned |
| T3 / p2 | Temporal precision sufficient for explanation | Alignment and detector / 2, 4, 5 | Report timing error and abstain when correspondence is unreliable | Manual boundary audit and uncertainty examples | Planned |
| T4 / p2 | Reproducibility across runs/environments | Config, locks, manifests / all | Fixed hashes/config reproduce decisions; numeric differences bounded and documented | Clean Windows rerun and second-environment comparison | Planned |

The PDF calls R3b "causal" explainability. TakeTwo will explain the calculation that triggered a flag and its delivery context. It will not infer anxiety, intent, health or a proven human cause from acoustic association.

## Official deliverables

| ID / source p2 | Deliverable | Component / phase | Acceptance criterion | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | GitHub codebase and documentation | Repository / 7 | Public repository contains runnable code, setup and documentation | Reviewed release commit and public link | Planned |
| D2 | Public custom paired dataset, transcripts and alignment labels | Dataset release / 7 | Files in GitHub or public Google Drive linked from README; rights permit release | Public download check, manifest checksums and dataset card | Planned |
| D3 | Functional interactive dashboard prototype | Workspace / 6 | Demonstrates real upload, extraction and visual/text results | Recorded browser run and end-to-end tests | Planned |
| D4 | Technical documentation, maximum 6 pages | Submission report / 7 | Covers dataset construction, rubric, architecture and scoring within six rendered pages | PDF page count and visual/content review | Planned |
| D5 | 3-10 minute YouTube demonstration | Submission video / 7 | Shows collection, spectrum stress tests and specific caught deviations | Public video link, duration and chapter checklist | Planned |

These engineering documents are working specifications, not the six-page submission report. No official deliverable is marked complete merely because Phase 0 is complete.
