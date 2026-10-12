# Analysis duration validation

TakeTwo — Speech analysis workspace. Current implementation raises the default analysis duration from 30 to 45 seconds, without changing acoustic definitions, scoring, scientific eligibility or independent review requirements.

## Configuration and inventory

`src/taketwo/analysis/limits.py` is authoritative: `TAKETWO_MAX_ANALYSIS_DURATION_S` accepts integer seconds 1–45, default 45. Restart the service after changing it. Larger/unparseable values fail startup; no unmeasured larger workload is admitted. `FeatureConfig` records the processing budget and may narrow it; extraction also enforces the deployment budget. Previous artifacts retain their configuration and code identity safeguards; changed implementation hashes cause recomputation, never edits to evidence.

Previously independent 30-second checks/copy were found in analysis contracts/extraction, API submission/health, excerpt creation, worker admission, frontend App/ImportForm/ExcerptForm, generated TypeScript, pilot acceptance, invalid-signal fixtures and current README/analysis/API/frontend/dataset/session/import/roadmap guides. These now use the central setting, runtime schema bounds or API health. CLI alignment now checks the same duration before expensive processing. Timeline passes health metadata to excerpt controls; entire original playback/selection axes remain intact.

Unrelated limits are preserved: import schema/decoder/transform storage 600 seconds; file limit 100 MiB; waveform/feature query windows 600 seconds; one worker, three queued jobs; 4 GiB aggregate worker commit; 32 MiB artifact bound; 600-second job timeout; MFA default 120 seconds and existing local config 180 seconds; 30-second version probe and browser report-delivery assertion; 30 displayed history rows. Historical release reports retain dated limits and measurements with a current-policy notice. Official and submission PDFs are unchanged.

## Boundary evidence

Generated tone fixtures test native 16 kHz excerpts at 44.9999375, 45.0000000 and 45.0000625 seconds: below/exact accepted with exact frame counts, above rejected; oversized originals still import and remain unchanged. The same path is tested with a configured 12-second budget. Invalid settings fail startup and explicit FeatureConfig cannot bypass a smaller deployment limit. These are software tests, not human speech evaluation.

## Windows workload evidence

Executed 2026-10-12. Measured on Windows 11 (build 26220), Intel Core i7-1365U, 16 GB RAM, Python 3.11.9, CPU only, one worker and one-thread numerical pools. The application/API benchmark uses the unchanged Windows Job Object; CPU seconds include descendant processes through kernel accounting. Health latencies use actual in-process HTTP TestClient requests and include alignment prerequisite/hash checks. They are not browser interaction latency measurements.

A genuine continuous 45-second archival excerpt uses source window `[6.36,51.36)` from the preserved Commons JFK inaugural Ogg master (SHA-256 `a257580da6eda796ed1c703e545865005753f7cb20cc042e0db3c44de82274fc`), decoded at native 44.1 kHz and exported PCM16 before normal import. No padding, repetition, speed change or synthesis. [JFK Library source/rights](https://www.jfklibrary.org/asset-viewer/archives/jfkwha-001) and [published speech](https://www.jfklibrary.org/learn/about-jfk/historic-speeches/inaugural-address) supply provenance. A separate synthetic control applies the existing seeded gain recipe (0.8 over native seconds 20–25); it is labeled synthetic, never human speech or independent ground truth. Both members remain 720,000 canonical samples. Recipe time-map segments cover `[0,320000)`, `[320000,400000)` and `[400000,720000)` with identical source/output coordinates.

The initial first-45-seconds candidate had an incomplete draft transcript: automatic alignment completed but omitted later spoken text. This is retained as a failed transcript-quality attempt, not successful alignment accuracy evidence. A native MFA research alignment of a longer source window was used only to locate candidate word gaps, outside the application capacity benchmark; no application duration guard was bypassed. The final 45-second subset's published draft text starts “President Eisenhower” and ends “three quarters.” Cut-edge/text correctness still needs independent human listening review. The full application was then rerun on a fresh dataset, with no cached stages.

| Actual paired workload | Measurement |
| --- | ---: |
| Supervised job wall time | 223.516 s |
| Job-tree CPU time (user + kernel) | 195.46875 CPU-s |
| Whole API workflow including validated report delivery | 231.566 s |
| Reference / synthetic alignment stages | 94.500 / 89.000 s |
| Reference / synthetic extraction stages | 19.078 / 17.516 s |
| Comparison/report construction stage | 2.047 s |
| Peak aggregate worker committed memory | 2,113,093,632 bytes (1.97 GiB) |
| Successful health probes while processing | 362 |
| Health latency median / p95 / maximum | 105.35 / 134.65 / 189.13 ms |
| Largest complete feature artifact | 28,377,392 bytes (27.06 MiB) |

Both automatic alignments succeeded with 60 ordered words / 265 phones, no OOV tokens, first word at 1.45 s and last ending at 43.639999 s. Native intervals, original-token mappings, sample identities and bound artifact hashes passed `read_artifact` / `validate_identity`. Each member produced 4,498 spectral frames; spectral coverage ends at 44.995 s and pitch coverage at 44.994 s because incomplete terminal windows are omitted. Waveform envelopes cover all 720,000 samples. Comparison/report retrieval returned HTTP 200 with explicit ineligibility and null overall score. No acoustic algorithms, scoring formulas, flaw detections or reviewer assertions were changed to obtain this outcome.

Peak worker commit stayed below the unchanged 4 GiB bound; artifacts stayed below 32 MiB. Each alignment stayed below both the 120-second default alignment budget and the existing local configuration's 180-second budget, and the paired job stayed below 600 seconds. No timeout or safety-budget increases are warranted by these measurements. One short archival family/control does not establish worst-case timing on other recordings or hardware. Independent transcript, boundary, phrase and blinded flaw reviews remain open; automatic coverage is not timing accuracy. No eligibility or human accuracy claims follow from this run.

Ignored local evidence: `local-data/acquisition/duration45-first.json` (incomplete draft attempt), `duration45-matched.json` (full supervised job), `duration45-integrity.json` (validated native mappings/artifacts), and `local-data/duration45-matched/` (immutable dataset/results). Original speaker files under `speech-01` remain untouched.

Re-run a supervised measurement on an already imported workspace using `python scripts/benchmark_duration.py WORKSPACE --reference RECORDING_ID --pair PAIR_ID --alignment-config CONFIG --output NEW.json`. Existing output files are never overwritten. The script measures actual processing and cannot supply reviews, text verification or fabricated results.

## Regression and browser verification

Executed checks:

- Genuine 45-second feature replay: `taketwo.analysis.cli validate --reproduce --alignment ...` passed against the saved reference artifact/configuration; no measurement arrays changed. Evidence: `local-data/acquisition/duration45-feature-replay.json`.
- Full Python suite: `pytest -q` — 246 passed, one existing Starlette/httpx deprecation warning, 111.61 s. This includes duration boundaries/configuration, worker admission, CLI rejection, cancellation/timeouts, crash containment, leases, artifact integrity, dataset transformations and comparison eligibility.
- Frontend suite: 17 passed. TypeScript, ESLint, Prettier, production Vite build passed. No dependency changes.
- Standard software browser workflow: passed in 26.0 s (29.0 s suite), including real HTTP imports, excerpts, CPU processing, cancellation/retry, history, playback, exports, accessibility and narrow layouts.
- Five genuine private WAV import workflow: passed in 10.6 s (13.5 s suite). All five fit the default budget; processing admission is enabled, without granting reviews, rights or intended severity.
- Initial 45-second browser workflow: passed, with saved automatic alignment/report inspection and actual uncached extraction of both 45-second members while navigating/seeking/exporting. Its extraction/comparison job took 41.282 s, peak commit 527,626,240 bytes, no cache hits. This separate run did not request alignment.
- Fresh-input full 45-second browser pipeline: passed, 221.233 s whole workflow; uncached supervised job 200.016 s, worker peak commit 2,118,840,320 bytes (1.97 GiB), entire browser/API/worker/MFA sampled working set 3,084,742,656 bytes (2.87 GiB). The latter is a sampled lower bound and can double-count shared pages; it is not isolated browser or worker memory. Both members again produced 60 words / 265 phones / 4,498 spectral frames, and null overall score. Native playback at 44 s, navigation/heading focus/seek during active processing, JSON export, no page JavaScript errors and axe passed. Immutable inputs are copied into a fresh ignored workspace, excluding caches/history/locks/reviews, so repeat runs cannot substitute cached stages.
- Failed browser harness attempts are retained: 5.864 s empty-history polling race, corrected with `[0]?.state`; and 246.682 s workflow whose CPU job and displayed report completed but a subsequent test GET hit stale keep-alive `ECONNRESET`. Idempotent test evidence GETs now retry that network failure once (`maxRetries: 1`), without relaxing HTTP failures, scientific assertions, processing timeouts or memory limits. Failed measurements/logs/traces remain under `duration45-browser-full.*`, `duration45-browser-final.*`, `duration45-browser-race-*` and `duration45-browser-connection-*`. Windows Proactor connection-reset warnings still appear on aborted/stale connections; no service crash or failed final workflow was observed. The successful final measurement is `duration45-browser-verified.json`, with job/report exports beside it.
- Native 200% zoom explicitly skipped in standard/pilot suites because full Chromium fails to launch on this host; spoken screen-reader checks remain unverified. No passing zoom claim.
- Ruff lint/format, locked dependency consistency (`uv lock --check`), wheel/sdist builds (`uv build --no-sources`), generated API/TypeScript contracts and all four runtime schema snapshots, Markdown links/judging weights/product identity, release inventory/secret-pattern preflight and `git diff --check` passed. Official PDF SHA-256 unchanged.

These checks establish duration admission and actual processing capacity on this host, not production readiness, calibrated scoring or independent human accuracy.


Codex assisted implementation, test scaffolding and documentation. All reported measurements derive from executed local jobs and checks, not estimated or generated performance results.

Final service restart on the existing five-take private workspace returned health limit 45 seconds, 100 MiB upload, one worker and 4 GiB commit budget. All five stored originals still match the original `speech-01` file hashes; every take fits the default duration.
