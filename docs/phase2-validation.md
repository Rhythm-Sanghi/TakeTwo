# Phase 1B / Phase 2 validation evidence

Historical evidence: limits and measurements below describe that recorded release. Current duration policy and measurements are in [duration validation](duration-validation.md).

Executed 2026-10-11 from `cb0dbd7`. Product: TakeTwo — Speech analysis workspace. Phase 2's alignment/acoustic implementation has actual execution evidence; **acceptance remains partially complete** because independent transcript/timing evidence and the human contrastive pilot are absent. No Phase 3 scoring or frontend work was started.

Implementation commit: `717f856` (`Implement native CPU alignment and reproducible acoustic evidence CLI`). Acquisition/status documentation follows in a separate local commit.

## Environment and scientific evidence

Native Microsoft Windows 11 Pro Insider Preview, build 10.0.26220; Intel Core i7-1365U (10 cores, 12 logical processors), approximately 16 GB visible RAM; CPU execution. TakeTwo: CPython 3.11.9 and uv lock (38 packages including development/transitive dependencies). Isolated MFA: 3.3.9, CPython 3.11.17, Kaldi 5.5.1172 CPU, kalpy 0.10.5, OpenFst 1.8.4, Pynini 2.1.7. The exported environment locks 198 package URLs/builds/MD5 hashes; installed file-size sum was 2,458,176,993 bytes, excluding package/download cache and separate models. No GPU framework was installed.

English US ARPA model and dictionary release **v3.0.0**, both **CC BY 4.0**, are checksummed in `environments/mfa-models.json`. Actual `mfa version`, `align --help`, `model download --help` and downloads were executed. Native binaries loaded and aligned genuine audio; no substitute backend was necessary. The offline-path run succeeded with existing local resources, unavailable HTTP/HTTPS proxies, `HF_HUB_OFFLINE=1` and `uv --offline`; this checks this invocation's local-resource behavior, not a packet-level network audit.

Genuine acquisitions and exact master hashes are in [pilot collection](pilot-collection.md). Two public-domain JFK masters were downloaded; one draft inaugural reference candidate was imported using the unchanged Phase 1 CLI. The final candidate is a 17.3 s salutation, recording `r-478a9405c1b10a75fda31972`, workspace `local-data/pilot-v2`. Canonical WAV SHA-256: `a342f051ea3b4ae23a40d293264bdee3946be235cb73c77e7e582c65dc873bc8`; sample SHA-256: `4f1b711de84e0b9a87a1e4d8cec7759560e12092031559ae127e052c491a2879`. Source masters, private/local metadata and generated artifacts are ignored and unpublished.

The archive-based 19-token transcript remains **unverified**, with no reviewer IDs/date. MFA produced 19 word intervals and 115 phone intervals. Two consecutive same-input native runs produced identical word/phone intervals (maximum word-boundary difference 0.0 s); their diagnostic log paths/artifact hashes differed. This is repeatability of automatic output, **not accuracy**. No independent human boundary set exists, so median/p90 timing error is unavailable. The initial 24 s exploratory clip contains a longer tail than the draft salutation and is not an exact-text corpus inclusion claim. Its automatic boundaries guided the shorter draft cut; human listening must confirm it.

On the 17.3 s clip, extraction produced 1,728 spectral/MFCC frames and 1,724 pitch frames. No pYIN frame met the configured probability >=0.8 (maximum approximately 0.548525), so pitch and relative pitch are unavailable and `pitch_unavailable` is explicit. Energy/FFT/MFCC measurements are available. Speaking/articulation rates and inter-word pauses are withheld because transcript review is missing. A successful tool exit never overrides these evidence gates.

## Executed checks

| Check | Actual result |
| --- | --- |
| `uv run pytest -q` final complete run | **155 passed**, zero failures/skips, 81.75 s; original 114 tests retained plus 41 analysis tests |
| `uv run ruff check src tests scripts` | Passed |
| `uv run ruff format --check src tests scripts` | Passed; 26 Python files |
| `uv lock`, `uv sync --locked`, `uv lock --check` | Passed; threadpoolctl 3.7.0 promoted from existing transitive dependency to explicit pin/use |
| `uv build --no-sources` | Source distribution and wheel built |
| Dataset and analysis JSON Schema comparison | Checked against runtime Pydantic contracts; dataset schema v1 unchanged |
| PDF SHA-256 | Unchanged: `0e621d35e6bfdbb9d9e169b259ebf9d3d923d1efcbab38ba2a4331f6958fb280` |

New verification covers finite-window sine RMS/energy, known FFT/F0 frequency, one-sided Parseval scaling, MFCC finite shape, distinct frame clocks/coverage, silence/short/noise/clipping, gain/register normalization, pause corroboration, verified-transcript rate gate, input/artifact hashes, original text mapping, dictionary/OOV/abbreviation behavior, missing prerequisites, backend failure/timeout/cancellation, interval bounds/order/coverage, safe temporary cleanup, immutable derived storage, schema versions and real CLI subprocess paths. Alignment parser/adapter fixtures are explicitly software tests, not evidence of real-speech timing accuracy.

A real replay found MFCC differences up to `1.4210854715202004e-14` between default BLAS and a single-thread benchmark, while spectra were identical. Extraction now explicitly limits BLAS to one thread with threadpoolctl; a regression checks identical results under externally configured one- and two-thread pools. No numeric tolerance was loosened to hide the issue. Models/audio/data schema were not changed by this fix.

## Executed CPU measurements

Measurements use actual CLI commands and include imports, validation, processing and JSON publication. Windows process-tree working set is sampled every 100 ms, so values are **sampled lower bounds**, count shared pages across processes and are not guaranteed true peaks. These short-clip results do not establish capacity for ten-minute ingestion or a 60-second pair.

| Run | Audio | Elapsed | Sampled peak tree working set | Context |
| --- | --- | --- | --- | --- |
| First real feature run | 24 s | 13.369 s | 289,812,480 bytes | Exploratory draft; before BLAS replay fix, benchmark already limited to one thread |
| Offline-path alignment | 17.3 s | 134.412 s | 1,941,450,752 bytes | Concurrent regression tests caused CPU contention; before BLAS extraction fix |
| Serial repeat alignment | 17.3 s | 79.098 s | 1,939,640,320 bytes | Same intervals as preceding run; before BLAS extraction fix |
| Serial feature run | 17.3 s | 12.287 s | 271,933,440 bytes | Original alignment supplied, pitch/rates unavailable as described; before BLAS replay fix |

The first 24 s MFA run's own log reported 111.976 s; no external peak-memory measurement was collected for that run. Use serial measurements, not the contended one, as the limited current CPU baseline.

## Final post-fix workflow

- Final native alignment of the 17.3 s candidate: **86.943 s**, sampled peak tree working set **1,944,772,608 bytes**; exit 0, 19 words / 115 phones. Current implementation digest: `4007b3faa56ff95771eace60f501820c9567720b77172afac13e3d49dfc672f0`.
- Final feature extraction with that alignment: **10.788 s**, sampled peak **269,778,944 bytes**; exit 0. Feature payload SHA-256: `690c8285c5e6b421f4bbdb92a977c8fcb3557b56ced3c0d6bcb15021ef36111a`.
- Normal-CLI `validate --reproduce --alignment` passed against the benchmark artifact after the BLAS fix. A subsequent `extract` reused the identical content-addressed feature file; inspection and fresh machine-readable export succeeded. No tolerance was introduced.
- Actual CLI smoke exercised all six commands: `check`, `align`, `extract`, `inspect`, `validate`, `export`. Dataset `validate --reproduce` returned exit 0, zero errors and one honest unverified-transcript warning. `--publication --reproduce` returned exit 1 with five missing-review/corpus/split/spectrum/human-mirror errors, as required.
- Wheel inspection confirmed the analysis CLI is included and no WAV/FLAC/MP3/Ogg assets are packaged. Documentation link/fence/branding/weight checks and Git whitespace checks were executed. Official PDF, AGENTS.md, dataset schema and all existing dataset code/tests remain unchanged from baseline.
- Documentation audit covered 15 Markdown documents and 56 local links; code fences, product identity and official weights passed. Staged Git whitespace checks also passed.

Benchmark JSON, source metadata and full artifacts remain under ignored `local-data/acquisition/` and `local-data/pilot-v2/`. Exact successful commands are in [the engine guide](analysis-engine.md). No remote branch or push was created.

## Remaining gates

Phase 1B remains incomplete: obtain a second source speaker, substantive independently verified excerpts, consented near-perfect/severe human mirrors and two-reviewer temporal annotations. Both acquired masters share JFK and therefore one leakage group. No fictional human performance, approval, label, dataset metric or publication was created. A collection script/procedure is ready, but no microphone/human review work was performed.

Phase 2 real automatic execution is verified; independent timing accuracy, difficult/noisy/flawed speech generalization, broader speaker/pitch coverage, cross-environment equivalence and full hardware profiling remain open. Keep the 30-second feature limit until evidence supports raising it. Review clipping/PCM16 quantization and alignment mismatch before later scoring. Record failures and abstentions instead of assigning perfect scores.

Recommended separate Phase 3: first validate alignment/quality eligibility and canonical-token/phrase correspondence; then native-time deltas, explainable evidence/regions and hand-checked versioned rubric calculations. Obtain independent timing labels before reporting detection accuracy. No frontend or learned quality model is required for that step.
