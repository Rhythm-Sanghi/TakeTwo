# Submission readiness

TakeTwo — Speech analysis workspace. Repository cleanup reviewed 15 October 2026.

## Deliverables

| Deliverable | Evidence and remaining requirement |
| --- | --- |
| Code | [Public repository](https://github.com/Rhythm-Sanghi/TakeTwo). Cleanup started from fetched `master` / `origin/master` at `0cdb837522de2957b147c48ce8d83f9b0b2c032a`. Local cleanup requires owner authorization before push and its own exact-commit Actions result. |
| Technical report | [Current six-page PDF](../output/pdf/taketwo-technical-report-2026-10-15.pdf) and [editable source](technical-report.md), retained unchanged. Older report/source remain traceable in Git history through [verification](verification.md). |
| Demonstration | [Owner-supplied YouTube demonstration](https://youtu.be/DfFTmNTAB6E). The previous publication pass recorded signed-out playback, 6:23 duration and the correct repository description link. This cleanup does not repeat that access check or establish narration quality/recording rights. |
| Public paired dataset | **Unmet.** No approved redistribution-ready independently annotated corpus or verified download URL exists. Five private practice takes are not ground truth. Follow [publication requirements](dataset-publication.md). |
| Submission | [Prepared Devpost fields](submission-draft.md); no submission receipt supplied. Verify the live organizer portal and rules before submitting. |

The previous publication record links successful [Windows run 38617800894](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38617800894) to `faebbc9`. That historical result does not certify this cleanup or later commits. Current local checks and historical failure evidence are in [verification](verification.md).

## Run and reproduce

Use `.\scripts\start-local.ps1 -Setup` once, then `.\scripts\start-local.ps1`.
Open `http://127.0.0.1:8765`; stop with Ctrl+C. Follow [Windows setup](windows-setup.md) and the separate [MFA/model configuration](analysis-engine.md). Without MFA, acoustic inspection/playback work and alignment explicitly abstains. Use [reproduction commands](reproducibility.md) for verification and dataset processing.

## Owner checklist

1. Review the concrete local cleanup, authorize push when satisfied, then verify remote HEAD and the Actions run for that exact commit.
2. Review the complete video for narration, claims, permissions and private information. Video permission does not grant dataset redistribution rights.
3. Obtain item-specific rights clearance and two actual independent transcript/timing/flaw reviews before a corpus release. Follow [reviewed version/import/evaluation](reviewed-evidence-workflow.md) and [publication validation/checksums](dataset-publication.md). Retain unresolved or unavailable results honestly.
4. Complete actual [listening acceptance](comparative-listening-acceptance.md), [spoken screen-reader acceptance](spoken-accessibility-acceptance.md) and clean second-machine setup/replay.
5. Verify the actual portal deadline/state, enter real deliverable links, include **OpenAI Codex** and **ChatGPT** in Built With and retain the actual submission receipt. Prepared files are not a submitted entry.

Rhythm Sanghi created and directed TakeTwo. Codex assisted implementation/testing/documentation; ChatGPT assisted planning/review. Private recordings, consent signatures, identity mappings, operator keys and reviewer records stay outside public releases. MIT covers original code/documentation and grants no recording or model redistribution permission.
