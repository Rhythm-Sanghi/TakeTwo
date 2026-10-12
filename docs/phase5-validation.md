# Phase 5 submission preparation evidence

TakeTwo — Speech analysis workspace. Executed 2026-10-12 from `9551d73` on the existing Windows 11 / Intel Core i7-1365U / approximately 16 GB RAM environment, CPython 3.11.9 and Node 24.15.0. This phase prepares local submission materials only. No application feature, dependency, scientific formula, review approval, public release or submission is introduced.

The root instructions, unchanged official three-page PDF, all existing technical Markdown documents, Phase 4B evidence, human pilot kit and worksheet were read before changes. [Final compliance](submission-compliance.md) separates every mandatory software/scientific/public artifact gate and retains the official 30/25/20/15/10 weights. [ACTION-REQUIRED](ACTION-REQUIRED.md) consolidates actual external work.

## Executed checks

| Check | Actual result |
| --- | --- |
| Full Python suite | 217 passed in 181.29 s, including five real Windows process-recovery tests; one existing Starlette/httpx deprecation warning |
| Frontend tests | Seven passed in 1.90 s |
| TypeScript / ESLint / Prettier | Passed; formatting rerun from frontend directory after an initial wrong-directory glob matched no top-level TS files |
| Frontend production build | Passed; 320.72 kB JS / 104.71 kB gzip, 8.13 kB CSS / 2.61 kB gzip |
| Ruff lint / format | Passed on 50 files after shortening an overlong audit-script string; no rule suppressed |
| Python locked resolution / sdist / wheel | Passed, 49 resolved packages; no dependency change |
| Runtime API / generated TypeScript | Regenerated with existing scripts; no contract diff |
| Generated-signal browser E2E | Final updated-test run passed, 56.2 s total / 49.8 s test body (earlier run 45.3 s total); actual backend, not mocked scientific output |
| Genuine-source browser E2E | Final passed: 255.927 s measured whole workflow. Explicit successful-alignment, 19-word/nonempty-phone assertions, real playback/export, all-area desktop/narrow axe and retry/cache checks |
| Genuine CLI replay / dataset/evaluation | Extraction and exact feature replay exit 0; comparison exit 3; comparison replay exit 0; evaluation exit 3; dataset normalization replay and actual MFA prerequisite/version check exit 0. Publication preflight correctly rejects five missing-evidence/corpus gates |
| Documentation/schema/PDF integrity | 35 Markdown files / 197 local links; four schemas equal runtime, official PDF SHA-256 unchanged; launcher syntax and Git whitespace passed |
| Release inventory | No credential-pattern, personal absolute-path, runtime/private-media or oversized-asset findings in current candidate files. The unchanged official PDF and generated report are the only binary candidates; both deliberately retained. Source-code LICENSE absent, owner decision open |
| Report rendering | Six pages, all six PNG renders visually inspected: readable typography, intact formulas/hash, no clipped/overlapping text or missing glyphs |

The initial official PDF extraction hit the shell's cp1252 output encoding; UTF-8 extraction then read all pages successfully. Failures are recorded rather than treated as passing invocations. Generated report authoring uses external ReportLab, pypdf and Poppler without application dependency changes. The editable source is [technical report](technical-report.md); its historical Phase 4B timing/memory measurements are labeled as historical, separate from current test results.

The first genuine browser test reached successful alignment/extraction, playback/export and all-area narrow checks, then exceeded its 240 s whole-test budget during final cancellation/retry. Its measurement/log/trace/screenshots were preserved. The genuine-only test budget is now 360 s, allowing bounded CPU processing plus interaction/axe/retry; normal tests retain 240 s and application deadlines are unchanged. The strengthened test explicitly requires MFA `status=succeeded` rather than merely an artifact path. All four narrow screenshots are retained for inspection. The final passing run logged a Windows asyncio `ConnectionResetError` during browser transport teardown; it remains recorded and does not establish robustness for every disconnect.

## Current genuine observations

Final workspace: `local-data/browser-real-1791771456911`; source `r-6b1f4ec4bda45c614ef1e738`; job `j-8fbc15975bfe43c6a619e3e6267022ab`. MFA succeeded with 19 words and 115 phones. Job elapsed 200.469 s; alignment stage 178.219 s; extraction stage 18.360 s. Kernel worker-tree peak commit was 1,899,757,568 bytes; whole browser-tree sampled working set 2,665,791,488 bytes. The latter samples every 100 ms, can double-count shared pages and is a lower bound, not true peak. Cached retry completed in 6.141 s, peak commit 196,472,832 bytes, with both actual alignment/features cache hits. These are one-source operational observations, not human-pair capacity benchmarks. The first measured run overlapped CLI replay; the final run overlapped lightweight frontend lint/type checks, not another heavy audio run.

Existing real-source CLI extraction/replay returned the identical feature payload `e00bb7cae62042eee68a6a5b1b4e7f4862701fc7f9dc5a8fd3bfbf37fec23722` and comparison `66a82bb488c3f4ff5d9e76739be5eb426b13a47c39cc6a1221230b84b725b574`. Evaluation again returned zero paired reports/reviews/families, null metrics, `independent_real_validation=false`, `reports_missing` and `split_missing`. Publication preflight reported unverified transcript, missing split, insufficient source families, missing severity spectrum and missing human mirrors. Genuine master hashes were rechecked and match the [acquisition ledger](pilot-collection.md).

Current local evidence is ignored: `local-data/acquisition/phase5-{browser,browser-final,cli,jobs}.json`, browser logs, first-failure evidence in `local-data/phase5-first-browser-evidence`, and passing genuine screenshots/export in `local-data/phase5-final-browser-evidence`. These are not published dataset assets. The generated report is the only new committed binary. Wheel inspection found seven web modules, all four CLI entry points and no media/database assets.

## Scientific freeze and actual data status

The two original rights-documented masters and draft 17.3 s JFK salutation remain local/unpublished. Both masters share one speaker group. No participant recordings, consent or independent reviews were supplied or created. There is no verified transcript segment to offer; recording material preserves the existing archive draft and requires two-listener verification. The salutation lacks substantive rhetorical range.

Dataset, analysis and comparison source, their schemas, policy delivery-v0, dependency locks, AGENTS.md and official PDF remain unchanged. Existing connected-group/split, origin-separation, missing-evidence, scoring/uncertainty and held-out-calibration safeguards are exercised by the original tests. Initial thresholds are not scientifically frozen/calibrated: preservation of delivery-v0 is a code/policy freeze, not a false calibration claim. New valid audio/metadata/reviews can use existing documented CLI commands without code changes.

No genuine region accuracy, independent alignment error, severity agreement, clean-span false flags or confidence intervals are available. A valid real-source abstention report is not a successful paired evaluation. No fixture is promoted into human evidence.

## Accessibility and product audit scope

Current browser E2E traverses all four actual workspace areas at desktop and 320 px, checks heading/skip focus, real waveform seek/play/zoom, import/empty states, actual acoustic evidence, abstention/null scores, export, cancellation/retry/cache and axe. It also renders an 800 px evaluation view. Generated-signal and genuine-source origins remain separate. Existing HTTP/recovery tests exercise malformed input and operational errors. Genuine eligible paired overlays/flag selection remain unavailable without reviewed human pairs.

Current genuine desktop analysis, 800 px evaluation and all four 320 px workspace screenshots were visually inspected. Restrained surfaces, readable native controls, clear unavailable evidence and local table scrolling are retained; no verified layout regression required application changes. Axe reported zero violations across eight area/width scans per run (16 across the final generated/genuine runs). Numeric/table alternatives and keyboard focus are exercised; this does not establish spoken assistive-technology behavior. HTTP tests additionally verified real CSV export.

Manual Windows browser inspection was attempted with the installed Computer Use tooling. Its browser-state request was stopped because the helper could not determine the browser URL reliably enough to enforce policy. No further manual app input was issued. This prevented a new actual 200% zoom or screen-reader session. Prior Phase 4B Narrator launch was blocked by integrity-level access and the in-app zoom shortcut had no effect; those are historical attempts, not successful verification. Actual zoom and heard Narrator/NVDA output remain **unverified**. Automated axe/responsive checks cannot close these gates.

The current package is locally reviewable, not ready for an honest complete-submission claim. Public paired dataset, genuine caught-deviation video, verified GitHub release, owner-selected code license, clean second-environment run, manual accessibility and submission receipt remain open. No remote write, push, deployment, publication or Devpost submission was performed. Codex assisted this work under human direction; all collection/review/publication decisions remain explicit human actions.

Local verification commit: `8ffb11a` strengthens genuine alignment assertions, preserves all-area screenshots and adjusts only the genuine browser test budget. The submission-material commit follows it; its final hash is reported in the completion message. No further implementation phase is started.
