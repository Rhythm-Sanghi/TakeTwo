# Track C submission compliance

TakeTwo — Speech analysis workspace.

The unchanged [official Track C statement](../requirments/Track%20C.pdf) defines the
requirements and judging criteria. The [requirements matrix](requirements-matrix.md)
preserves every requirement ID, acceptance criterion and required evidence. Use
[submission readiness](publication-readiness.md) for current deliverable links and
owner actions, and [verification](verification.md) for executed results and failures.

## Acceptance boundaries

| Requirement | Current evidence / remaining gate |
| --- | --- |
| Contrastive dataset | Provenance-aware import, synthetic lineage and connected-group split tooling exist. The required public paired audio/text/alignment-label dataset remains unmet: rights, independent labels and public-download verification are missing. |
| Forced alignment and acoustic features | Native CPU MFA and real FFT/MFCC/RMS/energy/pYIN processing executed. Automatic repeatability is not independent boundary accuracy; supported pitch can be unavailable. |
| Temporal grounding and explainable rubric | Native regions/anchors, measured deltas, formulas and fixed eligibility are implemented. Delivery-v0 is uncalibrated; real detection metrics and cross-speaker validation remain unavailable. |
| Interactive prototype | Import, processing, native playback, review, exports and five workspace areas have software evidence. Genuine listening usefulness and spoken accessibility remain pending. |
| Reproducibility | Locked software/native resources, immutable artifacts, fixed configuration and same-host replay are documented. Independent second-machine replay remains open. |
| Public deliverables | Public code, current six-page report and owner-supplied YouTube link exist. This cleanup requires authorized push and exact-commit CI. Dataset and submission receipt remain missing. |

Official weights are **Data Engineering & Stress Testing 30%; Causal Explainability
& Temporal Grounding 25%; Feature Extraction 20%; Visualization & Dashboard 15%;
Reproducibility & Code Quality 10%**. These are distinct from the four equal rubric
weights. Explanations describe acoustic associations, not psychological causes.

Software fixtures, intended severity, successful processing and green tests cannot
substitute for permissions or independent ground truth. A one-family pilot does
not establish held-out generalization. No mandatory requirement is waived.

Rhythm Sanghi created and directed TakeTwo. Disclose **OpenAI Codex** for
implementation/testing/documentation and **ChatGPT** for planning/review in README
and Devpost Built With. Verify live organizer rules and portal state before final
submission; prepared repository files are not a submission receipt.
