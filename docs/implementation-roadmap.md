# TakeTwo implementation roadmap

Status on 2026-10-11: Phase 0 planning complete, with documentation checks recorded below; Phases 1-7 unstarted. Nothing below is a claim of implemented behavior or achieved analysis performance. Follow [AGENTS.md](../AGENTS.md) and the [requirements matrix](requirements-matrix.md).

Prioritize dataset engineering (official 30%), temporal grounding/explainability (25%) and features (20%). Build the dashboard (15%) around verified artifacts. Reproducibility/code quality (10%) is a gate in every phase, not final cleanup. Implement one complete vertical slice at a time; commit working changes and update status/evidence before proceeding.

| Phase | Scope and dependencies | Completion gate | Required test/evaluation evidence | Status |
| --- | --- | --- | --- | --- |
| 0: Plan | Requirements, contracts, dataset, rubric, visual standards, risks | All seven documents cover the full PDF; weights total 100%; links valid; source unchanged; no application code | Full PDF reading/visual review, documentation checks, diff review and commit | Complete |
| 1: Dataset foundation | Provenance/schema validator, acquisition pilot, canonical transcripts, split grouping; resolve minimal Python test environment | Two cleared real public-speech families plus human near-perfect/severe mirrors; exact text, reviewed temporal labels; no fabricated or unlicensed release items | pytest manifest/interval/hash/split cases; actual pilot QA and permission log; locked environment/license inventory | Not started |
| 2: Alignment | CPU MFA environment/model lock, transcript preflight, aligner invocation and alignment artifact validation; depends on 1 | Native Windows smoke test on real pilot; no fabricated fallback; manual timing comparison published; missing models/OOV/mismatch recoverable | pytest ordering/coverage/failure tests; manual boundary audit; target median <=100 ms and p90 <=250 ms, otherwise investigate and revise scope transparently | Not started |
| 3: Acoustic engine | Ingestion/quality validation, normalization, FFT/MFCC/F0/energy/rate/pause features; depends on 2 | Actual features with native timestamps, units/masks and documented normalization; CPU/memory budget measured | Known-signal tests, real contour audit, silence/clipping/channel cases; waveform/derivative timing checks; gain/register invariance; resource log on target PC | Not started |
| 4: Temporal comparison and rubric | Token/phrase correspondence, evidence-backed flags and scores, exportable report; depends on 3 | Every flag is recomputable from real evidence; missing evidence abstains; scores match hand calculations; no psychological causal claims | Unit/contract fixtures, independent explanation audit, boundary/pause tests and repeat-run reports | Not started |
| 5: Dataset completion and held-out evaluation | Expand reviewed corpus, freeze validation-tuned config, independent evaluator; depends on 1-4 | Rights/QA/group-split checks pass; full spectrum and coverage gaps documented; sealed test results and failure inventory published | Per-origin/dimension/severity metrics, IoU/F1, boundary error, false flags/min, rank agreement, bootstrap uncertainty, abstentions and performance logs | Not started |
| 6: Functional workspace | FastAPI/SQLite worker lifecycle and React interface; depends on real report artifacts from 4; evaluation view consumes 5 | Import pair -> actual engine -> grounded evidence -> export works; keyboard/error/retry flows verified | API persistence/restart/cancellation tests; frontend interaction tests; Playwright with real pilot recordings; manual accessibility and timeline review | Not started |
| 7: Reproducible submission | Clean setup, public release dataset and docs, report/video; depends on 5-6 | Official D1-D5 satisfied; report <=6 pages; public YouTube video 3-10 minutes; README links resolve | Fresh Windows install/rerun, second-environment output comparison, dataset checksum/public-access audit, rendered report review and video duration check | Not started |

## Proposed performance gates and limits

Numeric gates are TakeTwo targets, not official minima or reported results. For the first pilot, target alignment errors above, peak application memory <6 GB, and end-to-end processing within 5 minutes for a pair of 60-second excerpts on the target CPU (record first-run and warm-run separately). If missed, profile and reduce concurrency/feature workload; do not hide quality loss with invented output or remove required functionality. Reassess the ten-minute input ceiling after benchmarking.

Before final test, choose validation-supported detector tolerances and record them. Initial utility targets: region precision >=0.75 and recall >=0.60 at IoU 0.5 on human labels, and <=1 false flag/minute on reviewed near-perfect spans; report all results even if these targets fail. Few families and annotator disagreement limit what these metrics establish. Do not tune thresholds on the sealed test to pass a gate. A missed utility gate leaves analysis experimental and requires an explicit limitation or a new independent test set after revision.

Exact decisions and repeat-run tolerances follow the [scoring policy](scoring-policy.md). For every phase retain failing cases, commands, environment hashes and evidence paths in a dated validation log. Required tests grow with implementation; do not add empty module scaffolds or tests that simply restate constants to create apparent progress.

## Scope control and critical path

Critical path: rights-cleared pilot -> reviewed labels -> working CPU alignment -> native-time features -> grounded reports -> frozen evaluation -> usable workspace -> submission. Dataset acquisition and labeling effort starts before frontend polishing. Maintain a small working corpus and avoid model training unless pilot evidence proves it necessary. Defer multilingual support, cloud deployment, live recording, authentication, ASR transcription, learned scoring and visual customization.

Block rather than pretend completion when rights are unresolved, no aligner meets the pilot gate, held-out labels are unreviewed or the public dataset/video/report is missing. Phases may overlap documentation/annotation work, but their evidence gates cannot be skipped. The maximum six-page technical report is a final condensed artifact, not a restriction on these internal engineering documents.

## Exact next implementation step

After the user's next development instruction, start Phase 1 with a versioned JSONL dataset manifest and a small Python validator plus pytest checks for provenance, hashes, interval bounds and connected-group split leakage. Resolve a minimal locked Python environment for this work, then acquire and review two rights-cleared public-speech pilot families. Do not build the API, frontend or scoring engine until their dependency gates are met. Phase 0 stops before any of this implementation.

## Phase 0 verification record

Executed on 2026-10-11 using the bundled Python runtime and Git, without installing dependencies:

- Read AGENTS.md and README.md completely; extracted all three PDF pages with pypdf and inspected all three Poppler-rendered page images.
- Checked the seven required documents, all 22 local Markdown links, balanced code fences, absence of unresolved planning placeholders and absence of the former product name in project Markdown.
- Checked all 20 matrix behavior/consideration/deliverable IDs and their Planned status, plus the exact official weights 30/25/20/15/10 summing to 100%.
- Verified the PDF SHA-256 against the initial value recorded in the requirements matrix and verified AGENTS.md against commit `8c9b813` after line-ending normalization.
- Reviewed the documentation diff and ran `git diff --cached --check`; verified local runtime/cache/model paths are ignored and no application/package files were introduced.

These are documentation/repository checks. Application tests, alignment runs, dataset evaluation, CPU benchmarks and scoring validation have not been executed because implementation has not started.
