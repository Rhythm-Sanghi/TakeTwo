# Phase 4B validation

TakeTwo — Speech analysis workspace. Continued from `901eec1` on Windows 11 / Intel Core i7-1365U / approximately 16 GB RAM, CPython 3.11.9, Node 24.15.0. Official Track C PDF, AGENTS.md, scientific engines, scientific schemas, rubric and dependency locks are unchanged. No push, public release, submission or Phase 5 implementation was performed. Codex implemented and verified these changes under human direction.

## Separate acceptance outcomes

| Gate | Actual status |
| --- | --- |
| Software readiness | Core Windows reliability, regression, real-reference workflow and accessibility fixes verified. Actual screen-reader speech and 200% browser zoom remain unverified; full accessibility acceptance is incomplete |
| Dataset readiness | **Open:** user confirmed no participant recordings or independent reviews. Two previously acquired masters share JFK; one draft salutation is an integration candidate, not a complete contrastive corpus |
| Scientific validation | **Open:** zero reviewed human pairs or independent evaluation groups. Detection metrics, boundary accuracy, speaker fairness and calibration are unavailable |

## Changes

Windows kernel delete-on-close leases replace web-owned empty lock files. Named kill-on-close Job Objects contain the actual CPU worker and MFA descendants, prevent child breakaway, cap aggregate commit at 4 GiB and process count at 16. Workers wait for containment before importing engines or spawning children. Startup stops surviving named trees, marks unfinished history failed/interrupted without requeueing, and removes only checked managed job temporary directories under the dataset lease. Unknown CLI/legacy locks remain untouched. Original audio and complete artifacts remain immutable. No distributed infrastructure or dependency was added.

Exact-request retry is available for failed/cancelled history. Timeline controls have distinct track labels, status regions remain mounted, changing waveform windows hide stale samples, and the continuously moving playhead is not announced. Narrow scrollable tables and nonvisual measurement regions accept keyboard focus. Workshop + Gridline + Studio Utility layout, colors and typography are retained; no decorative dashboard feature was added.

Additive API job observations report elapsed wall time, stage durations, peak kernel commit and actual cache hits. Old persisted job payloads load with defaults. Runtime OpenAPI and generated TypeScript contracts agree. Scientific artifact formulas/provenance and deterministic content remain unchanged. [API lifecycle](backend-api.md) and [Windows operation](windows-setup.md) describe boundaries and legacy migration.

## Executed verification

| Check | Evidence |
| --- | --- |
| Full Python regression | Final run: 217 passed in 162.08 s, including all original 197 foundation tests, 15 web tests and five real Windows process-recovery tests; one existing Starlette/httpx deprecation warning |
| Recovery tests | Hard service kill, hard worker kill, descendant termination after supervisor loss, enforced allocation failure under a 128 MiB test cap, live lease exclusion, preserved unknown locks, restart failure marking, no requeue, active deduplication, retry, selective temp cleanup and corrupt-cache refusal |
| Frontend | Seven unit/interaction tests passed, including pending-window stale-waveform removal; strict TypeScript, ESLint and production build passed |
| Generated-pair browser | Passed in 41.2 s total / 36.4 s test body: actual imports/CPU extraction, abstention, playback/seek/export, cancellation/retry/cache, skip link and heading focus; no mocked scientific routes |
| Genuine-reference browser | Passed in 226.542 s total: actual archival import, MFA, extraction, report, playback/seek/zoom/export, cancellation/retry/cache; 17.3 s real source, no participant substitute |
| Automated accessibility | Zero axe violations across library/analysis/rubric/evaluation desktop checks and all four areas at 320 px, in both browser runs. Root horizontal-overflow assertions passed; 800 px screenshot also inspected |
| CLI / reproducibility | Genuine extraction, exact feature replay, comparison replay, dataset normalization replay and native alignment prerequisite/version check passed. Comparison/evaluation returned expected scientific-abstention exit 3 |
| Repository / packaging | Ruff check and formatting, locked dependency check, source/wheel build, wheel inventory, runtime scientific/API schema equality, Markdown links/fences/branding/weights, unchanged PDF digest, generated frontend contracts, launcher syntax and Git whitespace checks passed |

Failures found and corrected: the initial new recovery test helper had a quoting error; an initial test wrongly treated Windows peak commit as bounded resident memory (Windows may count rejected attempted allocations); broader narrow axe checks found a scrollable table without keyboard focus. Corrected tests verify real allocation rejection and configured kernel limit rather than asserting misleading peak semantics. The table defect was fixed without suppressing the axe rule. A documentation check temporarily failed while the new validation document was not yet created; final checking includes it. No unresolved automated regression failure is claimed passed.

## Genuine processing and process interruption

The fresh browser workspace is `local-data/browser-real-1791769283106`; recording `r-6b1f4ec4bda45c614ef1e738`, canonical sample digest `a342f051ea3b4ae23a40d293264bdee3946be235cb73c77e7e582c65dc873bc8`. Rights/acquisition evidence remains in [pilot collection](pilot-collection.md). Transcript/excerpt remain independently unreviewed. The completed job is `j-535dd5d11d844eed8a11dae213552e45`: native MFA produced 19 words/115 phones; extraction produced 1,728 spectral and 1,724 pitch frames. Accepted pitch fraction is 0, RMS approximately 0.0772197731, peak 0.6856004596, energy baseline -34.46671585 dBFS. All dimension/overall scores are null; zero regions means comparison unavailable.

A separate isolated copy without caches was interrupted while its **actual `mfa.exe align` process** was running. Terminating only the owning service PID stopped the observed MFA process within 0.049 s; the application/kernel performed tree termination. Startup marked `j-e33c012828114727bb82573df4ea627a` failed/interrupted, cleaned abandoned job temp data and did not requeue. Explicit retry `j-b668ffa255ef4648b37612ebc7f484f2` completed native alignment/features/abstention. Its report remained identical/readable after another hard service restart. A separate genuine-source running-MFA cancel completed in 0.334 s, left no report, removed its temporary directory/dataset lease and preserved service readiness.

Automated interruption/restart also verifies digest-invalid complete caches cannot become a successful report: recomputation refuses to overwrite a corrupt content-addressed destination, marks the new job failed and leaves suspect bytes for inspection. Existing completed artifacts are only reused after payload/schema/input/config/environment/code checks. This is explicit refusal, not automatic repair of corrupted evidence.

Real human-pair comparison, genuine detected-region seeking and eligible scores remain blocked. Generated tone pairs verify software only. No human recording, consent, transcript approval or flaw label was invented.

## Evaluation and calibration evidence

The actual existing evaluator was run on the genuine workspace without paired reports/reviews. It published a persisted pilot evaluation with **0 paired reports, 0 review artifacts, 0 families, 0 matched severities**, `independent_real_validation=false`, and `reports_missing` / `split_missing`. Precision, recall, F1, interval/event boundary metrics, false flags/minute, severity association and confidence intervals are **null**. Empty category/severity and FP/FN lists are empty inventories, not zero-error results. The UI displays the persisted abstention and reasons.

Phase 3 regression covers category/severity precision/recall/F1, one-to-one IoU/event matching, boundary errors, FP/FN IDs, full blinded human-review coverage, origin separation, frozen connected-group leakage checks and seeded family bootstrap. These are software tests, not accuracy on real speech. Defaults remain IoU 0.5, sensitivity 0.3/0.7 and event tolerance 200 ms. Held-out validation requires a frozen policy, disjoint calibration/validation groups and at least three independent test groups; thresholds must not be fit on test labels.

`delivery-v0` is retained unchanged and experimental. Its initial pacing/pause/energy/pitch tolerances and engineering severity bins lack independent validation. No valid reviewed sample supports changing penalties, claiming fairness or fitting calibration. Low pitch acceptance, short-word/frame coverage, assisted correspondence and reference-style bias remain explicit risks. Unavailable dimensions remain null, with no redistributed weights.

## Accessibility and actual UI review

All four running workspaces were inspected for layout, hierarchy, compact controls, actual inventory, loading/empty states and evidence wording. Manual keyboard actions verified workspace/history navigation with heading focus, sample-resolution seek, zoom-in and native audio Space play/pause; observed audio advanced to approximately 3.271 s before pause. Automated checks verify the skip link focuses `main`, all four narrow views remain within the root width and tables expose keyboard access. Measured charts retain numeric native-time alternatives and textual evidence. Canvas pixels themselves are not evaluated by axe.

Actual screen-reader verification remains **unverified**. Windows Narrator launched and exposed its updates dialog, but its main window reported a higher Windows integrity level than the automation helper; spoken output/announcements could not be verified. No elevation or accessibility-compliance claim was substituted. A native browser zoom shortcut in the in-app browser left viewport width/device-pixel ratio unchanged; **200% browser zoom remains unverified**. Responsive viewport checks do not substitute for that test. A person must test real Narrator/NVDA announcements, focus/error recovery and 200% browser zoom before accessibility acceptance.

## Measured resource scope

| Observation | Actual value / scope |
| --- | --- |
| Browser workflow / uncached job | 226.542 s / 187.422 s; browser workflow includes startup/import/playback/export/axe/retry |
| Alignment / extraction stages | 169.359 s / 14.235 s in browser job; include validation/publication overhead, not isolated numerical kernels |
| Worker-tree peak commit | 1,892,315,136 bytes (1.76 GiB), Windows Job Object counter; not resident RAM |
| Whole browser-tree sampled working set | 2,772,697,088 bytes (2.58 GiB), 100 ms sampling including Node/Chromium/API/worker/MFA; sampled lower bound, shared pages can be counted repeatedly |
| Cached job | 8.859 s, 196,341,760-byte peak commit; both exact alignment/features cache hits, same report path |
| Post-crash uncached retry | 118.204 s; alignment 104.516 s, extraction 11.109 s, peak commit 1,891,061,760 bytes |
| Alignment prerequisite/version CLI | 5.747 s including CLI imports, prerequisite/hash validation and MFA version startup; not isolated aligner initialization |
| 600 s / 38,400,080-byte oscillator ingest | 2.097 s; real final-ten-second waveform request 0.453 s / 1,500 bounded bins; analysis rejected with 422 before queueing, service remained ready. Explicit software fixture, not a speech benchmark |
| UI responsiveness observation | Keyboard area change plus accessibility snapshot 277 ms; includes automation overhead, single observation, not a rendering percentile benchmark |
| Production bundle | 320.72 kB JS / 104.71 kB gzip; 8.13 kB CSS / 2.61 kB gzip |

Measurements varied across runs; no general throughput guarantee is claimed. Browser measurement overlapped lightweight frontend checks/operator inspection. One serial CPU worker, one-thread numerical pools, 30 s analysis and 600 s/100 MiB ingestion bounds remain. No speculative optimization or GPU/cloud requirement was added. Eligible paired/large-corpus performance, isolated browser memory and other hardware remain unmeasured.

Ignored local evidence includes `local-data/acquisition/phase4b-{browser,jobs,real-recovery,real-cancel,cli,limits}.json` with logs, actual exports/screenshots in `local-data/phase4b-browser-evidence`, and isolated local workspaces. These files contain no invented human evidence and are not committed dataset assets. Repeat automated checks with [Windows commands](windows-setup.md); optional genuine browser smoke requires the documented local source/config. No recordings, models, database or temporary runtime artifacts are added to Git.

Final repository check covered 24 Markdown files, 125 local links, four runtime schemas and the unchanged official PDF digest. Ruff checked 48 Python files. Wheel inspection confirmed seven web modules, all four CLI entry points and no audio/database assets. Implementation commits: `198fa62` (Windows reliability/contracts) and `1eb1685` (retry/accessibility/browser verification); the subsequent documentation commit is reported in the completion message.

## Remaining submission blockers and next actions

Use the [recording kit](human-pilot-kit.md) and [blank annotation worksheet](annotation-worksheet.md) to collect rights-cleared substantive excerpts, a second source speaker, consented faithful/flawed participants, verified text, complete checked timing/phrase partitions and two independent blinded flaw inventories. Freeze leakage-resistant groups; calibrate a new version only with valid train/validation evidence; evaluate sealed test groups and inspect every FP/FN. Real human listening/release authorization cannot be supplied by software.

Finish real screen-reader/200% zoom testing. OS power-loss recovery, cross-environment equivalence, reviewer authentication and installer packaging remain unverified. The existing Starlette/httpx warning remains recorded; no unrelated upgrade was made. Public paired-data/code release, maximum six-page technical report and 3–10 minute YouTube demonstration remain future submission work. This run stops at Phase 4B; overall hackathon readiness is not claimed.
