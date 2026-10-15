# Verification, measured evidence and limitations

TakeTwo — Speech analysis workspace. Results below distinguish software regression,
real-sample processing, human acceptance and scientific validation. None establishes
production readiness. Reproduction commands and fixture setup are in
[reproducibility](reproducibility.md); blank human review/acceptance forms are in
[review protocol](review-protocol.md).

## Evidence boundaries and open requirements

| Evidence class | Established scope | Remaining gate |
| --- | --- | --- |
| Automated software | Signal/analytic fixtures, schemas, native clocks, hand calculations, identity, review lifecycle, crash/cache behavior and UI workflows | Does not supply permissions, people, independent labels or speech accuracy |
| Genuine processing | Five private mono 48 kHz PCM16 practice takes, declared same speaker/family; archival JFK inputs processed locally | Text/timing/flaws remain independently unverified; no public-release consent or paired dataset |
| Human product acceptance | Procedures and blank forms exist | Actual listening, manual native-zoom visual review and heard Narrator/NVDA remain pending |
| Scientific validation | Evidence-gated tools, nulls and explicit abstention are implemented | Independent F0/boundary/flaw truth, calibration, held-out metrics and cross-speaker generalization unavailable |
| Reproducibility | Locked same-host execution/replay, manifests and bound hashes | Clean second-machine equivalence and power-loss durability unverified |

Delivery-v0 is uncalibrated; no missing score becomes zero and unavailable weights
are not redistributed. Automatic alignment can fit incorrect words. Supplied text,
performer intention, pYIN probability, playback telemetry and reviewer pseudonyms
do not prove correctness, severity, comprehension or independence. Capabilities do
not authenticate people or defeat the trusted OS owner. Acoustic association does
not establish persuasion, emotion, ability or psychological cause.

The practice durations are reference **30.224375 s**, natural **30.590 s**, slow
**40.590 s**, uneven **29.370 s**, near-perfect **31.760 s**. Titles reflect intended
acquisition, not reviewed quality. Their 71-word supplied passage and all four
participant pairs form one connected family, unsuitable for held-out generalization.
Rights/consents and exact source attribution remain in private evidence and the
[acquisition ledger](pilot-collection.md). The mandatory public dataset is unmet.

## Pitch coverage and scientific abstention

These are actual local measurements on the five genuine private same-person practice takes, not independent pitch accuracy or detection evaluation. No recordings, identities or raw private diagnostic artifacts are released. `acoustic-v1` and `delivery-v0` remain unchanged: pYIN range 60–500 Hz, 1,024 samples (64 ms), 160-sample hop (10 ms), center=False, no padding, confidence >=0.8 and finite voiced F0. Unaccepted F0 remains null; relative pitch never supplies fabricated scores.

| Take | Duration s | Raw voiced % | Accepted % | Probability median | Probability p95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| reference | 30.224375 | 72.091 | 0.597 | 0.01185 | 0.54853 |
| natural | 30.590 | 76.351 | 0.295 | 0.01185 | 0.48499 |
| slow | 40.590 | 69.331 | 0.617 | 0.01082 | 0.54853 |
| uneven | 29.370 | 75.162 | 0.512 | 0.01310 | 0.54853 |
| near-perfect | 31.760 | 75.678 | 0.284 | 0.01185 | 0.42606 |

Raw voiced medians are 119.3–123.5 Hz; raw estimates include the 60 Hz floor and reach 231.8–249.9 Hz. All probability frames are finite; unvoiced NaNs are expected and masked before JSON serialization. No adjacent finite-frame jump exceeds 10 semitones in these runs; no pYIN warning was emitted. Canonical peaks are 0.297–0.400 and clipping fraction is zero. Median frame levels are -31.1 to -32.4 dBFS; fifth-percentile levels -43.3 to -44.7 dBFS. Those lower levels combine pauses and noise: no isolated noise reference/calibrated SNR or microphone response is available. These observations cannot establish the cause of each low-confidence frame.

### Controls and hypotheses

Three-second clean known-F0 sine controls at 80/120/200/400 Hz all produce 100% raw voiced estimates with median frequency within 0.7% of the known fundamental. Accepted fractions are respectively 0/0/100/100%; median probabilities 0.426/0.686/0.891/0.985. Thus even a clean low-frequency signal can be withheld with this window/confidence combination; input noise alone does not explain the limitation.

A diagnostic 2,048-sample window (not a production change) raises 80/120 Hz control acceptance to 60.069%/100%. Reference acceptance increases only from 0.597% to 1.362%, still far below the 50% local usable-pitch gate. Changing only bounds to 40–500 or 60–800 Hz leaves reference acceptance at 0.597%. Reducing reference gain by 20 dB leaves its raw voiced fraction, acceptance and probability quantiles unchanged. Gain normalization therefore does not solve this observed case. Window-dependent confidence is supported by controlled evidence; reliability on actual low-pitched speech is still unvalidated.

No swapped pYIN outputs, manufactured contour, NaN-to-score propagation or normalization defect was found. This is a verified configuration/model limitation, not evidence supporting a lower confidence threshold. Keep abstention. Any longer-window policy requires a separate version, native-time support checks, independent pitch labels, low/high-register/noise controls, benchmark and recalibration before adoption. No runtime acoustic/scoring code changed.

Reproduce diagnostics on authorized canonical input copies:

```powershell
uv run python scripts/inspect_pitch.py --workspace $privateWorkspace --output .\local-data\pitch-diagnostics.json --probes
```

The script reports raw/accepted coverage, quantiles, NaNs, jumps, levels, clipping, warnings and diagnostic runtime. It never publishes analysis features or modifies inputs. Initial diagnostic runtimes were 13.3–18.7 s per take under concurrent verification load (not isolated capacity benchmarks); the -20 dB control took 23.4 s. Raw diagnostic JSON is retained privately. Independent F0 accuracy, frame-wise confidence calibration and causal microphone/noise attribution remain open.

The 13 October stabilization recheck and 14 October complete probe matrix reproduced
accepted fractions reference **0.596619%**, natural **0.294792%**, slow **0.616827%**,
uneven **0.511771%**, near-perfect **0.283912%**. The reference −20 dB control was
unchanged. The 2048-sample control accepted 60.069444%/100% at 80/120 Hz but only
1.362126% on the reference. All known-frequency controls had 294 frames. Recheck
runtimes 6.96–12.33 s were under mixed load, not a before/after speed benchmark.
Independent F0 truth, confidence calibration and causal noise/microphone attribution
remain unavailable. The original probe/recheck provenance is in [the immutable pitch record](https://github.com/Rhythm-Sanghi/TakeTwo/blob/cd9991866f57091fd5da4da1cd899bc2bc20ebc8/docs/pitch-investigation.md).

## Analysis duration and capacity

Measured 12 October 2026 on Windows 11 build 26220, Intel Core i7-1365U, 16 GB RAM,
Python 3.11.9, CPU only, one worker and one-thread numerical pools. Central
`TAKETWO_MAX_ANALYSIS_DURATION_S` accepts integer seconds 1–45, default 45; invalid
settings fail startup and FeatureConfig cannot bypass a lower deployment budget.
Imports remain 600 s/100 MiB; one worker/three queued jobs, 4 GiB aggregate worker
commit, 16 processes, 32 MiB feature artifacts and 600 s job deadline remain bounded.
MFA default stage budget is 120 s, the measured private config 180 s; version probe
remains 30 s. These limits are not inferred from the observations below.

Generated 16 kHz fixtures at 44.9999375/45.0000000/45.0000625 s accepted below/exact
and rejected above with exact frame counts, including a separate 12 s deployment.
Originals above analysis budget still imported without truncation. These are software
boundary tests. A real continuous archival excerpt used master window [6.36,51.36),
from the inaugural Ogg SHA-256
`a257580da6eda796ed1c703e545865005753f7cb20cc042e0db3c44de82274fc`, decoded at
44.1 kHz then PCM16 before canonical import. The other member is an explicitly
synthetic gain-0.8 control at native seconds 20–25, not a human take. Each has 720,000
canonical samples; identity time maps cover [0,320000), [320000,400000), [400000,720000).
The draft text starts “President Eisenhower” and ends “three quarters”; independent
cut-edge/text review is still absent. An initial longer-tail candidate omitted spoken
text and is retained as a failed transcript-quality attempt, not alignment accuracy.

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

Both automatic alignments returned 60 words/265 phones, no OOV, first start 1.45 s,
last end 43.639999 s; each had 4,498 spectral frames. Complete support ends at
44.995 s (spectral) / 44.994 s (pitch); omitted terminal windows are not silence.
Waveform envelopes cover every sample. Identity/replay checks passed and the report
returned HTTP 200 with explicit ineligibility/null overall score. Peak commit and
artifact size stayed within bounds; one family/host does not establish worst-case
capacity, timing accuracy or general throughput.

The independent fresh browser pipeline took 221.233 s, job 200.016 s, peak worker
commit 2,118,840,320 bytes; sampled whole browser/API/worker/MFA working set was
3,084,742,656 bytes. Sampling can double-count shared pages and is a lower bound,
not RSS or worker commit. An extraction-only run took 41.282 s / 527,626,240-byte
commit and did not request alignment. A 246.682 s attempt completed processing but
failed a stale keep-alive GET; a separate 5.864 s attempt hit an empty-history race.
The final run passed without changing production deadlines. Historical duration
verification had 246 Python/17 frontend tests; native zoom was skipped then, not
passed. Use the later native-zoom result only for its own scope. Full telemetry,
failed attempts, stage values, private evidence paths and replay commands remain in
[the immutable duration record](https://github.com/Rhythm-Sanghi/TakeTwo/blob/cd9991866f57091fd5da4da1cd899bc2bc20ebc8/docs/duration-validation.md).

## Windows restoration, transport and cold-load failures

Measured 14 October 2026 on Windows 11 Pro Insider Preview 10.0.26220, Python 3.11.9,
Uvicorn 0.42.0, i7-1365U (12 logical processors), 16,815,702,016 bytes installed RAM.
Six isolated genuine-workspace copies used SQLite backup and managed file copies.
Three Proactor trials lost their listener with WinError 64 after 14/30/19 abrupt
TCP resets. Three Selector trials survived 30 resets each with identical report,
exploratory and comparative payload hashes. Resets used Winsock SO_LINGER (1,0)
after a request and closed after 20 ms. The Windows launcher now selects Selector,
within its 512-socket/no-asyncio-subprocess-pipe constraints. Workers use synchronous
Popen in supervised threads. WinError 10054 was observed separately but not
reproduced by this experiment; no universal reset fix or event-loop speedup is claimed.

“Cold” below means a fresh process/cache, not cleared OS disk caches. Requests were
report → exploratory → insights; later endpoints may benefit from earlier validation.
Warm values summarize nine calls. Host contention included only 1.66 GiB free RAM.

| Loop / request | Initial seconds, three trials | Warm median (range), seconds |
| --- | --- | --- |
| Proactor startup to healthy | 8.231, 4.985, 12.719 | Not applicable |
| Selector startup to healthy | 6.831, 6.665, 8.823 | Not applicable |
| Proactor report | 15.233, 11.302, 20.850 | 0.661 (0.331–3.118) |
| Selector report | 10.244, 42.479, 19.934 | 0.701 (0.451–0.886) |
| Proactor exploratory | 7.912, 14.235, 9.260 | 0.709 (0.521–0.854) |
| Selector exploratory | 5.030, 11.248, 25.149 | 1.257 (0.268–2.216) |
| Proactor insights | 3.138, 9.978, 6.403 | 0.622 (0.310–1.064) |
| Selector insights | 4.241, 12.572, 14.294 | 1.364 (0.294–4.798) |

Six simultaneous cold requests redundantly validated one 25,592,607-byte feature
artifact six times (29.187 s); serializing lookup/validation reduced that experiment
to one validation (4.412 s) with identical models. The cache remains bounded to eight
entries with mtime/size keys, source/code/review checks and uncached failures.
This is a specific repair, not a defense against privileged metadata-preserving
tampering or a universal speedup. A fresh browser measured:

| Operation | Seconds |
| --- | --- |
| Backend startup to healthy | 4.370 |
| Cold frontend load to usable inventory/current health | 2.401 |
| Cold selection to comparative findings and both native charts | 29.431 |
| Backend restart to healthy | 4.254 |
| Open frontend reconnect to current inventory/health | 3.937 |
| Warm frontend reload plus stored comparison restoration | 5.991 |

The 29.431 s selection spans sequential evidence requests, each with the unchanged
15 s budget. A later genuine cold bootstrap still timed out after repair. Warm success
and safe GET retry do not close cold-latency risk. The API process grew from
146,518,016/862,019,584-byte working set/private memory to 244,994,048/962,580,480;
peak working set was 335,384,576 bytes. Selection used 17.96875 CPU-s; the restarted
process peak working set was 375,246,848 bytes. These are API measurements, separate
from worker-tree memory and whole-machine CPU.

Fresh genuine processing observations, with no cache hits:

| Run | Job seconds | MFA reference/participant (s) | Extraction reference/participant (s) | Comparison/validation (s) | Peak worker commit bytes |
| --- | ---: | --- | --- | --- | ---: |
| Baseline | 211.906 | 87.390 / 98.422 | 12.985 / 10.343 | 1.204 / 0.250 | 2,077,245,440 |
| Final | 237.640 | 116.671 / 91.219 | 15.297 / 11.375 | 1.328 / 0.266 | 2,081,546,240 |

Actual disconnect exposed a stale ready announcement; current health now drives the
status/reconnect action. A startup guard outage gained bounded failure/retry while
keeping operator views locked; failed inventory is unavailable, not false zero.
Six focused browser cases passed in 50.9 s. Earlier crash/retry attempts exceeded
unchanged 60 s job or 3 s report test budgets under load; the same case later passed
alone (104.04 s). Two reset/cache regressions passed in 9.13 s. Failed attempts remain
failures. Full trial traces, telemetry and configuration provenance remain in
[the immutable Windows record](https://github.com/Rhythm-Sanghi/TakeTwo/blob/cd9991866f57091fd5da4da1cd899bc2bc20ebc8/docs/windows-hardening-evidence.md).

## Regression findings and security boundaries

| Finding | Retained evidence / practical limit |
| --- | --- |
| Deterministic audio and features | Volatile libsndfile PEAK timestamps required deterministic headers; BLAS changed MFCCs up to 1.42e-14, motivating one-thread extraction. Same-input replay is not cross-machine equivalence. |
| Evaluation and reviewer order | Greedy matching missed a second match; maximum-cardinality/quality and exact-inventory-v1 now avoid reviewer-order-dependent ground truth. 0–1 s versus 0.2–1.2 s can change matching against 0–0.5 s. Numerical software fixtures are not speech accuracy. |
| Review publication | Journaled intent, immutable staging/publication and process-kill recovery retain one logical submission and reject corruption. This does not establish power-loss durability, authenticated identity or genuine independence. |
| Worker containment | Actual MFA descendant stopped 0.049 s after service kill; cancellation 0.334 s, explicit retry succeeded. Windows Job Objects enforce bounded commit/processes; unknown locks and corrupt content-addressed caches remain for inspection. |
| Searchable PDF | Supplied Microsoft printer outputs outlined text with zero fonts/extractable text; Chromium retained text/fonts/tags. Historical seven exports/33 rendered pages passed dual extraction and visual review. This does not certify PDF/UA or every driver. |
| Genuine comparison | Reference/uneven duration delta −0.854375 s (−2.826775%), RMS +0.0438473107 dB. 53 raw windows→44 groups, 71 provisional words, one anomaly/74 items. Reference 28→22. These are observations, not confirmed flaws. |
| Machine-gap diagnosis | technology→is machine gap 2.890 s had 0.000 s low-energy support. Context replay reference 10.93–11.88 s / participant 10.12–13.47 s. Gaps before helps/a differed +0.560/−0.510 s. Quiet pause, hesitation, pronunciation or alignment cause remain unknown without listening. |
| Privacy/security | Loopback/origin/path/upload/decoder limits, managed artifacts, redacted API errors and ≤32 KiB private traces are exercised. Pattern/dependency audits are not proof of absent secrets, rights clearance or every filesystem race. |

The complete prior phase/regression ledger, exact commands/hashes and intermediate
failure provenance are preserved in [the immutable pre-consolidation verification record](https://github.com/Rhythm-Sanghi/TakeTwo/blob/cd9991866f57091fd5da4da1cd899bc2bc20ebc8/docs/verification.md).
Its links retain the original experiments in ordinary Git history; no archive folder
or rewritten evidence replaces them. The risk register's recording rights, reference
bias, difficult alignment, timing/preprocessing, pitch, capacity, leakage, small-corpus,
drift, prioritization, causal wording, private-data and submission risks remain open
where the evidence above is absent. Original qualitative likelihood/impact judgments
are in [the immutable risk register](https://github.com/Rhythm-Sanghi/TakeTwo/blob/cd9991866f57091fd5da4da1cd899bc2bc20ebc8/docs/risk-register.md).

## Public baseline and current consolidation checks

Public baseline `cd9991866f57091fd5da4da1cd899bc2bc20ebc8` passed
[Windows Actions run 38680335494](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38680335494),
including browser E2E. The earlier interrupted local clean-clone browser run had
16 passes/two failures (missing-heading assertion and timeout); hosted success does
not rewrite those local results or establish their cause. Backend 376 and frontend
81 passed locally in that prior task. Those results describe that baseline; prior CI
does not certify the new consolidation commit.

The unchanged six-page [technical report](../output/pdf/taketwo-technical-report-2026-10-15.pdf)
and its [editable source](technical-report.md) are a dated submission snapshot.
Original reference [4] is the pinned pitch record above; reference [6] is the pinned
Windows record. Reference [5]'s hardening evidence remains linked from the historical
verification record. Snapshot citations identify their original versions; they are
not dependencies on deleted current paths. Reproduction and current methods use the
consolidated guides. No genuine audio, private review or completed consent is bundled.


## Consolidation verification, 15 October 2026

Docs Markdown decreased from **40 to 19**, removing 23 superseded files and adding
one review protocol and one submission document. All seven JSON schemas and the
official specification retain their bytes. No Python source, test, workflow, script,
lock or package manifest changed. The sole application edit updates the printed help
path to `docs/review-protocol.md`; Prettier adjusted its wrapping. The report/source,
screenshot, private originals and existing owner PDFs remain unchanged. Local-only
AGENTS instructions remain ignored and unchanged; no replacement file was published.

| Check actually executed | Result |
| --- | --- |
| `uv sync --locked`, npm ci, production build | Passed; no lock/dependency changes |
| Full backend `uv run pytest -q` | **376 passed**, 236.84 s; one existing Starlette/httpx warning |
| Frontend unit tests, one worker | **81 passed**, nine files, 14.80 s |
| TypeScript / ESLint / Prettier | Passed; initial help-path wrapping warning corrected with the existing formatter |
| Ruff check / format / uv lock check | Passed; 79 Python files, 49 locked packages |
| Relevant Playwright workspace + readiness suites | **7 passed**, 41.5 s; actual import/CPU processing/playback/export, five workspace layouts and readiness failure/recovery |
| Markdown file/fragment checks and repository validation | All local links and headings resolve; six current runtime contracts match and the seventh legacy schema remains valid/unchanged |
| Wheel/sdist builds and package inventory | Passed; all seven schemas/new guides included, all 23 removed documents and AGENTS absent |
| Release/history/package privacy preflight | 173 candidate files / 752 pre-commit reachable history blobs; zero blocking findings or personal absolute paths |
| Fresh source-clone setup smoke | Prospective staged tree applied to a fresh clone; locked setup/build/launcher served health + branded frontend HTTP 200 in 36.984 s without AGENTS |
| Current report/source and public link | Public PDF HTTP 200, 57,712 bytes identical to local, six pages; all 45 source blocks matched pypdf extraction |
| Demo URL | Resolved to the owner-supplied YouTube page; no fresh playback/narration/permission acceptance claimed |
| Source/data preservation | 178 protected files byte-identical; the one allowed frontend help-path/format change is separate from scientific code |
| Git whitespace | Passed |

A standalone readiness-only Playwright attempt had four passes/one failure because
its fresh workspace had zero recordings while one case expects the earlier import
journey's populated fixture. The error snapshot showed that empty inventory; running
the existing workspace prerequisites followed by all five readiness cases passed.
No test, timeout, assertion or application gate was changed. The full browser suite,
private genuine suites and human acceptance were not rerun for this documentation task.

The fresh-clone setup used the staged source tree at test time; later edits only
record these results and retained diagnostic commands. Package and repository checks
cover the final document tree. New hosted CI remains pending owner-authorized push.
The missing public corpus, independent scientific review/calibration and real human
acceptance remain blockers; green software checks do not close them.
