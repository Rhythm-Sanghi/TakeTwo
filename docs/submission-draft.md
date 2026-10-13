# Submission description and final checklist

TakeTwo — Speech analysis workspace. Draft for owner review; not posted to Devpost or any third party. Official artifacts and current gates are in [compliance](submission-compliance.md); all manual actions are in [ACTION-REQUIRED](ACTION-REQUIRED.md).

## Devpost description draft

TakeTwo is a local speech-analysis workstation for comparing reference and participant performances of the same transcript. It preserves native audio timing and links delivery deviations to measured acoustic differences, explicit tolerances and reproducible rubric calculations. Its Workshop + Gridline + Studio Utility interface provides recording import, audio transport, waveform/feature inspection, evidence, history, dataset inventory and report export.

The implementation combines a provenance-aware contrastive dataset pipeline, native CPU Montreal Forced Aligner, FFT/MFCC/RMS/energy/pYIN extraction and reviewed word/phrase correspondence. Pacing, pause behavior, energy excursion and pitch excursion form the initial equal-weight delivery-agreement rubric. Scores and detection confidence are unavailable when evidence is insufficient. The software does not infer persuasion, emotion or a psychological cause from an acoustic difference.

Current evidence includes genuine archival reference processing and automated signal, contract, browser and Windows crash-recovery tests. The two acquired masters share JFK; the one imported excerpt is unverified. Five genuine private same-person practice takes and their intended transcript are now available; independent transcript/timing/flaw reviews and public-release consent remain absent, so genuine contrastive detection accuracy, rubric calibration and held-out results remain unavailable. Public dataset and video delivery are incomplete. Replace this status only with newly executed, inspectable evidence before submission.

Technology: Python 3.11, FastAPI/Uvicorn/Pydantic, NumPy/SciPy/librosa/soundfile, CPU MFA/Kaldi, SQLite, local managed files, React/TypeScript/Vite/uPlot; pytest, Vitest/Testing Library, Playwright/axe, Ruff/ESLint/Prettier. No CUDA or paid inference API. Exact versions/resources are locked. OpenAI Codex was extensively used for implementation, testing, integration and documentation. ChatGPT assisted architecture planning, problem interpretation, technical review and development instructions. Humans supplied the genuine recordings; human consent, recording, annotation and final judgments remain separate. See [full attribution/tool disclosure](attributions.md).

## Submission artifact checklist

| Artifact / action | Current state | Completion evidence required |
| --- | --- | --- |
| README/setup/architecture/contracts | Prepared locally | Owner-reviewed exact public release commit; signed-out setup/download check |
| Final compliance matrix | Prepared with open gates | Reconcile with actual submitted artifacts; retain incomplete rows |
| Code license and notices | Owner selected MIT, copyright (c) 2026 Rhythm Sanghi | Root LICENSE added; private data and third-party resources retain separate rights |
| Custom contrastive dataset | Blocked | Permitted audio, exact text, reviewed labels, spectrum, frozen groups, validation and public checksum audit |
| Independent scientific evaluation | Blocked | Real counts, replayable reports, independent labels, failures/abstentions and held-out prerequisites |
| Manual accessibility | Partial: automated native tab zoom verified | Actual heard screen-reader and independent keyboard acceptance log |
| Clean second-environment reproduction | Incomplete | Actual setup/replay hashes and decision comparison |
| Technical report, maximum six pages | Draft prepared; see Phase 5 validation for rendering | Final evidence reconciliation, page-count/content/visual audit |
| YouTube, 3–10 minutes | Script prepared; video absent | Actual recording, owner-approved upload, signed-out playback/duration |
| GitHub code/documentation link | Existing project remote; this work stays local | Public release commit verified after authorization |
| Public dataset link in README | Absent | Actual permitted public GitHub/Google Drive download and checksums |
| Devpost fields/attachments | Draft only | Owner verifies portal/rules/deadline/timezone and uploads actual artifacts |
| Submission receipt | Absent | Actual owner submission confirmation |

No placeholder URL, generated metric or software test result completes an external/scientific gate. Final owner review must compare the public README, PDF and video against the same actual release/data/config versions. This phase stops at local package preparation; it does not push, deploy, publish, create remote branches or submit.

Devpost Built With: Python, FastAPI, NumPy, SciPy, librosa, soundfile, Montreal Forced Aligner, Kaldi, SQLite, React, TypeScript, Vite, uPlot, OpenAI Codex, ChatGPT. Verification tools: pytest, Vitest, Playwright, axe, Ruff, ESLint, Prettier. These tool names do not imply independent human review.
