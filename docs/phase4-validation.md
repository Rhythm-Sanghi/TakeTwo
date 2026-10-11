# Phase 4 validation evidence

TakeTwo — Speech analysis workspace. Developed from `4cd1f37` on native Windows 11, Intel Core i7-1365U / approximately 16 GB RAM, CPython 3.11.9, Node 24.15.0. **The local web application is implemented; acceptance remains partially complete** because a legitimate independently reviewed human pair, manual screen-reader/200% zoom audit and abrupt-crash orphan recovery remain open. No final submission/publication phase was started.

## Implemented workflows

FastAPI/Uvicorn wraps the unchanged Phase 1–3 engines. React/strict TypeScript/Vite/uPlot implements Recording Library, Analysis Workspace, Rubric and Evidence, Dataset and Evaluation. Real multipart audio/text/provenance import creates immutable recordings and same-text participant pairs. Metadata/quality, native waveform/audio transport, zoom/pan/interval selection, automatic word markers, windowed RMS/energy/F0/activity features, reviewed-word overlays, grounded event seeking, numeric evidence, eligibility, history and JSON/CSV export use actual backend contracts. There is no seeded production dataset or mocked scientific route.

SQLite persists lifecycle/history, with one isolated CPU worker and three waiting slots. Named stages, active-request deduplication, cancellation, whole-job/MFA deadlines, process-tree cleanup, retained completed artifacts and explicit failed/interrupted states are implemented. Atomic complete-file publication avoids exposing partial artifacts during cancellation. The manifest and scientific artifacts remain authoritative; they were not rewritten into mutable database copies. See [API/lifecycle](backend-api.md), [interaction design](frontend-workspace.md) and [Windows launch/recovery](windows-setup.md).

The original dataset/analysis/comparison source and original 197 tests remain unchanged. Their original schemas, AGENTS.md and Track C PDF remain unchanged. Acoustic implementation digest remains `4007b3faa56ff95771eace60f501820c9567720b77172afac13e3d49dfc672f0`; comparison digest remains `74ab0877f26480a936da95927d9876e7a377cdebf5d0597d1b20eb829b4b5a90`. Python scientific pins are unchanged; the service/UI additions are purpose/license documented in [dependencies](dependencies.md).

## Executed verification

| Check | Actual evidence |
| --- | --- |
| Complete Python regression | **212 passed**, zero failures/skips, 122.52 s: all 197 foundation tests plus 15 HTTP/lifecycle tests; one dependency deprecation warning |
| Additional lifecycle coverage | Windows atomic-stage sharing retry and stopped-supervisor readiness rejection passed in the complete regression |
| Frontend component/interaction tests | **7 passed**; coordinate/sample mapping, differing native durations, null scores/fixed weights, boundary-event inspector values, unverified import and playback/selection interactions |
| TypeScript strict check / ESLint / frontend production build | All passed on final source/contracts; 319.38 kB JS / 104.38 kB gzip, 8.13 kB CSS / 2.61 kB gzip |
| Chromium generated-pair browser workflow | Final rerun: one passed in 17.3 s (14.1 s test body). Passed through actual HTTP imports, real CPU extraction/comparison, native audio seek/play, waveform zoom, evidence/abstention, JSON download, policy/evaluation navigation and axe. Generated tones are explicitly software fixtures, not speeches or human approvals |
| Genuine-reference Chromium workflow | Passed fresh real import, native MFA, acoustic extraction, persisted report, waveform seek/play/zoom, actual input evidence, JSON download, unavailable scoring and axe |
| Accessibility | Axe found zero violations on both exercised analysis views. Browser navigation heading focus, native controls and numeric/table alternatives were exercised; screenshots inspected at desktop and 800 px responsive width. Manual screen-reader listening and full 200% browser-zoom review remain unperformed |

HTTP tests additionally cover MIME/actual-content rejection, strict private-value-free request errors, duplicate rollback, origin/host/size restrictions, byte-range streaming, exact waveform sample bounds, bounded gap-preserving feature windows, job member isolation, caching/replay, corrupted-artifact rejection, queued dedup/cancel/full queue, interrupted history, running cancel/timeout lock cleanup, symlink refusal and Python/OpenAPI snapshot equality. These generated signals establish software behavior only.

During development, checks exposed a parent-folder PostCSS configuration, an unavailable test-helper import, optional generated response fields and component fixture defaults; these were corrected and rerun. Browser repeats exposed a Windows `PermissionError` when replacing a stage file while the supervisor briefly held it open. Bounded sharing-violation retry was added and deterministically regression-tested; subsequent generated-pair and genuine-reference browser runs passed. Worker errors preserve exception category without private transcript/log contents. The final genuine run also logged a Windows asyncio connection-reset callback during browser transport shutdown; the workflow still passed, and this log is retained rather than hidden. No arbitrary-input robustness is claimed. Final documentation checking caught a stale HTTP schema after request-bound changes; the schema and TypeScript types were regenerated and equality checking passed.

## Genuine archival audio

The existing rights-documented JFK inaugural salutation was uploaded through the actual browser form into a fresh ignored `local-data/browser-real-1791738073397` workspace. It is a real public-source candidate, not a participant or synthetic speech. Source selection/transcript/excerpt remain independently unreviewed; browser import retains unverified status and zero reviewers. Provenance remains linked to the [original acquisition evidence](pilot-collection.md).

- Recording: `r-6b1f4ec4bda45c614ef1e738`; job `j-b2f3ee654fc54a66b930ee1f41b6c41d` completed.
- Canonical audio SHA-256: `a342f051ea3b4ae23a40d293264bdee3946be235cb73c77e7e582c65dc873bc8`; 276,800 samples / 17.3 s.
- Native MFA succeeded: 19 words and 115 phones. Alignment payload: `9522824803227c069eda5fc0cfe982cb370b2d08566fc67394d6e1b4fb21b5c9`.
- Actual feature payload: `751d62331ae0ee9dbd6701b3bb538d183f630497a6bb310d362efec4659acb1e`; 1,728 spectral frames and 1,724 pitch frames. Accepted pitch fraction 0; F0 is unavailable under the unchanged threshold.
- RMS approximately 0.0772197731 full scale; peak approximately 0.6856004596; energy baseline approximately -34.46671585 dBFS. These are measurements, not speaking-quality results.
- Report payload: `f223782ce052bf6806077aa9ae12188f9f846b94868cfe43d246064ab2f68e18`. All four dimension scores and overall score are null, no regions are claimed, and pair/transcript/timing/pitch reasons remain explicit. Zero regions means comparison unavailable.
- Screenshots were rendered and inspected. Actual screenshots, exported report and measurement/log JSON remain ignored under `local-data/phase4-evidence` and `local-data/acquisition`; no recordings/models/private artifacts are committed.

The complete legitimate real-pair workflow, meaningful real paired overlays/flag inspection and eligible real scoring remain **unverified**. No human mirror, reviewer approval or flaw inventory was invented to close that gate. Component/generated-engine tests are separate from independent speech accuracy.

## CPU and memory scope

The genuine browser workflow took **142.265 s** including service/browser launch, form import, MFA, extraction, comparison, playback/export and axe. The persisted processing job took **124.573 s**. Sampled peak process-tree working set was **2,748,141,568 bytes (approximately 2.56 GiB)** at 100 ms intervals, including Node, Chromium, API, CPU worker and MFA. This is a sampled lower bound that can count shared pages repeatedly; it is not true peak or an eligible real-pair capacity benchmark. Measurement is preserved in `local-data/acquisition/phase4-browser-final.json` with exit 0 and its separate log. No GPU, paid API or model download occurred during analysis.

The executed production UI build is approximately 319.38 kB JavaScript / 104.38 kB gzip and 8.13 kB CSS / 2.61 kB gzip. These are actual Vite outputs, not estimated library sizes. One worker, thread limits, short-clip caps, immutable caches and bounded visualization windows protect the target workstation. Long-clip/large-library/eligible-pair profiling and browser-memory isolation remain open.

## Remaining gates

Collect a second independent source speaker, consented human near-perfect/flawed mirrors, independently verified text, two agreeing timing/phrase reviews and blinded flaw labels. The two acquired masters share JFK and do not provide independent groups. Freeze/calibrate the rubric only using reviewed train/validation families before sealed evaluation. Initial tolerances/severity bins remain unvalidated; automatic alignment success is not measured boundary accuracy. Pitch reliability, clipping/noise effects, short-word coverage and reference-style bias remain scientific limitations.

Abrupt process/host crashes require inspecting old worker/MFA processes and stale workspace locks before restart; cleanup is verified for supervised cancellation/timeouts/graceful shutdown. Automatic crash-orphan recovery is not implemented. Reopening the final smoke workspace reproduced a stale `.service.lock` after Playwright forced server teardown. Process inspection confirmed no live TakeTwo worker/MFA and an empty `.runtime`; removing only that stale lease allowed restart. The reopened service returned readiness true with alignment configured. Current Starlette TestClient emits one deprecation warning for httpx; tests pass, and a future explicit dev-client migration should be evaluated separately. No authenticated reviewer independence, cross-environment equivalence, installer, public dataset release, six-page submission report or YouTube demonstration is claimed.

Final verification also passed Ruff check/format (46 Python files), locked Python dependency resolution (49 packages), wheel/source build, wheel inspection (six web modules, CLI entry point, no audio/database assets), PowerShell launcher syntax, regenerated Python/TypeScript contracts, documentation consistency (21 Markdown files, 106 local links, four schemas, unchanged PDF hash) and Git whitespace checking. The original scientific engine diff against `4cd1f37` is empty. Final source/lock review includes no recordings, models, secrets, caches or unrelated files. Codex implemented and verified this integration under the user's direction; human scientific review remains separate. Integration source commit: `60e2dab5d899f24a4a3fb3695e51526cecd5f0df`; the documentation commit hash is reported in the completion message. Phase 4 ends here; no Phase 5/6 work or remote push was performed.
