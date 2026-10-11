# TakeTwo architecture

Speech analysis workspace. Status: Phase 1 dataset tooling and Phase 2 alignment/acoustic modules are implemented. Native Windows CPU MFA and real-audio extraction have run; independent timing/transcript review remains open. See [analysis engine](analysis-engine.md) and [actual validation](phase2-validation.md). API, database, comparison/scoring and UI remain planned. Target: Windows 11, Intel Core i7-1365U, 16 GB RAM, integrated graphics, local CPU processing. Start with single-speaker English excerpts; other languages, overlapping speech and unverified transcripts receive an explicit unsupported/review state.

## Technology decisions

| Layer | Selection and purpose | Tradeoff / verification gate |
| --- | --- | --- |
| API | Python 3.11 baseline, FastAPI, Pydantic, Uvicorn | Typed request/response contracts; resolve compatible versions on Windows in Phase 1 |
| Audio I/O | soundfile | Decode WAV/FLAC, inspect actual format; no mandatory FFmpeg or MP3 support initially |
| Numerics | NumPy and SciPy | Arrays, FFT, resampling and signal/statistical calculations |
| Acoustic features | librosa | MFCCs and pitch estimation; benchmark pYIN CPU cost before committing to clip limits |
| Evaluation | NumPy/SciPy; defer scikit-learn | Deterministic metrics need no learned model; add scikit-learn only if grouped calibration/classification later needs it |
| Alignment | Montreal Forced Aligner (MFA), separate Conda/Miniforge environment | CPU-first dictionary/acoustic alignment; native execution verified, independent timing gate remains open |
| UI | React, TypeScript, Vite | Local interactive workspace needs no SSR; CSS tokens, native audio, canvas waveform with accessible DOM controls |
| Metadata | Python sqlite3, SQL migrations | Local single-user persistence with no server or ORM requirement |
| Storage | Managed local files under `%LOCALAPPDATA%/TakeTwo` | Original audio immutable; derived artifacts removable/rebuildable |
| Verification | pytest; Vitest + Testing Library; Playwright | Signal/contract tests, accessible interaction tests and real browser workflows |

Phase 1 locks the Python dataset runtime in `pyproject.toml`/`uv.lock`; its purpose and license inventory is in [dependencies](dependencies.md). No API/frontend/database packages are installed yet. Librosa's transitive scikit-learn dependency is present but unused for learning. Phase 2 locks the aligner environment and model artifacts separately in `environments/`; frontend versions are resolved when that phase starts. No paid API, CUDA, cloud inference, message broker or external database is required. Avoid introducing a waveform library until native audio/canvas interaction is shown to be insufficient.

## Boundaries and data model

Implement cohesive modules only when their phase starts: ingestion, normalization, alignment, features, comparison, region detection, scoring, evaluation, persistence, API and UI. Engine functions accept explicit arrays/artifacts/configuration and do not depend on HTTP or UI state. Evaluation invokes the same engine through a CLI, without a browser.

Phase 1 implements `src/taketwo/dataset/`: schema, errors, safe storage, audio ingestion/normalization, controlled transformations, connected-group splitting, validation, workspace operations and CLI. Tests are in `tests/`. It uses one atomically replaced versioned JSONL manifest and managed local audio directories; SQLite is deferred until application sessions need it. The executable contracts and commands are in [dataset engineering](dataset-engineering.md).

SQLite entities: `recordings` (hash, managed path, origin, quality, transcript ID), `transcripts` (original/normalized text and hash), `pairs` (reference/participant IDs), `alignments` (recording, model/config hash, status, artifact path), `analyses` (pair, rubric/config hash, job state), `rubrics` (immutable versioned JSON), `evaluation_runs` (split/config/report hashes). Dataset manifests additionally contain provenance and annotation records defined in the [dataset plan](dataset-plan.md). Foreign keys enforced, schema migrations numbered, writes short and transactional; enable WAL for local readers with a bounded busy timeout. Do not use a network share for the database.

Store originals, normalized audio, per-recording alignment JSON, feature arrays (`.npz`, no pickle), waveform peaks and report JSON separately. Paths are server-generated IDs, never user-provided filesystem paths. Use atomic file publication followed by the DB transaction; recover orphan temporary files on startup. A canonical analysis identity hashes input bytes, transcript, configuration, code version, rubric and model checksums. Reports include artifact versions and validity, not merely a cached score.

## Recording-to-report workflow

1. Upload each recording and a UTF-8 transcript; enforce 100 MiB/file, 10 minutes/recording, one or two channels and 8-96 kHz as initial configurable limits. The UI accepts a `.txt` upload or pasted text and sends its content to the transcript endpoint, with a 100,000-character limit. Validate decoded headers, finite samples and actual duration before expensive work. Initial supported containers: WAV/FLAC. Limits are design choices to benchmark, not measured capacity.
2. Preserve original bytes/hash. Inspect channel cancellation before downmixing; ask for channel selection if averaging would destroy speech. Create a 16 kHz mono analysis derivative with SciPy polyphase resampling. Keep raw level/clipping evidence; no automatic loudness normalization, denoising, silence trimming or time stretching. Source and derivative time origins remain identical; cropped dataset excerpts record their source offset.
3. Flag silence, poor signal quality and clipping (initial clipping warning: more than 0.1% of decoded samples at magnitude >=0.999; quality indicators are heuristic). Reject corrupt/empty files, all-silence and incompatible text. Ask the user to review suspected omissions rather than forcing arbitrary matches.
4. Pair the recordings against one canonical transcript; punctuation normalization never silently removes spoken words. Align each independently with MFA. Preflight pronunciation coverage, model presence and language; retain original token-to-normalized-token correspondence.
5. Parse word/phone intervals and validate ordering, bounds and word coverage. Save alignment diagnostics; suspected mismatch or missing model produces `needs_review` or `failed`, never evenly spaced substitute timestamps. Manual reviewed alignment import is a recovery path with provenance, not an automatic equivalent to forced alignment.
6. Compute frame features on each native time axis; aggregate per shared word/phrase and inter-word pause. Use token correspondence for comparison; do not warp away duration or pause differences. Features and masks are specified in the [scoring policy](scoring-policy.md).
7. Compute deltas, threshold crossings and participant-time regions. Attach corresponding reference intervals, feature evidence and uncertainty. Aggregate dimension scores only where evidence is valid; report unavailable dimensions explicitly.
8. Persist report/artifacts atomically. UI displays waveform, correspondence, evidence and rubric. Export versioned JSON and region CSV; human-readable report export follows after correctness is established.

## Alignment and Windows execution

Phase 2 selected MFA 3.3.9 with English US ARPA model/dictionary release v3.0.0 (CC BY 4.0), verified in native Windows smoke runs. Independent manual timing evaluation remains open. Invoke the locked CLI via argument arrays, never a shell-interpolated command. Use one isolated job directory; capture command/version, logs, timeout and output hashes. Start with one alignment job at a time and at most two CPU subprocesses. Pin the command signature as well as artifacts because upstream model formats/CLI are changing. No automatic model downloads during analysis.

If installation, licensing or accuracy blocks MFA, stop the alignment gate and evaluate another maintained CPU aligner on the same manually timed pilot. Do not silently switch engines or rely on removed TorchAudio alignment APIs. A manually annotated pilot enables independent timing evaluation but does not satisfy the automatic alignment requirement by itself.

Future application execution: run one API process plus one separate spawned engine worker. SQLite tracks queued jobs and stage transitions; the API remains responsive during CPU work. Worker stages are `validating -> aligning -> extracting -> comparing -> scoring`; job states are `queued | running | needs_review | succeeded | failed | cancelled | interrupted`. On restart mark unfinished work `interrupted`; retry creates a new attempt referencing the old one. Cancel at stage boundaries or terminate the isolated aligner subprocess; never publish partial artifacts as successful reports. Serialize heavy jobs, cap thread pools and load only one model at a time. Cache by artifact hashes, not filenames. Target peak total application memory below 6 GB; record peak RSS and real-time factor (wall seconds/audio seconds), with no speed claim before measurement.

## Proposed API v1 contracts

All IDs are opaque strings; timestamps are seconds from the decoded recording origin, intervals `[start_s,end_s)`. JSON is UTF-8; finite numbers only, missing evidence is `null` with a reason. Lists use cursor pagination. OpenAPI/Pydantic become the implementation authority; breaking schema changes increment the API/report version.

| Endpoint | Request | Success response |
| --- | --- | --- |
| `GET /api/v1/health` | None | 200: service/schema versions, worker and model availability |
| `POST /api/v1/transcripts` | JSON `{text, language:"en"}` | 201: `{id, sha256, normalized_text, token_count}` |
| `GET /api/v1/transcripts/{id}` | None | 200: original/normalized text, token mapping and hash |
| `POST /api/v1/recordings` | Multipart `audio`, `transcript_id`, `origin` (`source`, `self_recorded`, `synthetic`), optional `channel` | 201: `{id, sha256, duration_s, sample_rate_hz, quality_flags}` |
| `GET /api/v1/recordings` | Optional cursor | 200: `{items, next_cursor}` |
| `GET /api/v1/recordings/{id}/audio` | Optional HTTP Range | 200/206: local audio stream with correct media type |
| `GET /api/v1/recordings/{id}/waveform` | `start_s`, `end_s`, `bins` (max 5000) | 200: interval and min/max sample bins |
| `POST /api/v1/recordings/{id}/alignments` | Reviewed JSON word intervals, token indices and annotation provenance | 201: validated manual alignment ID; immutable original automatic attempt retained |
| `POST /api/v1/analyses` | JSON `{reference_id, participant_id, rubric_version, config_version}`; optional reviewed `reference_alignment_id` / `participant_alignment_id` and `Idempotency-Key` | 202: `{id, state, stage, report_id:null}`; identical key/body reuses job |
| `GET /api/v1/analyses/{id}` | None | 200: `{id, state, stage, error, report_id}` |
| `POST /api/v1/analyses/{id}/cancel` | None | 202: cancellation requested; terminal jobs return 409 |
| `POST /api/v1/analyses/{id}/retry` | None | 202: new attempt ID; preserves previous error/evidence |
| `GET /api/v1/analyses/{id}/report` | None | 200: report below; 409 if not ready |
| `GET /api/v1/analyses/{id}/features` | `recording_id`, `feature`, `start_s`, `end_s`, `max_points` (max 5000) | 200: `{unit, times_s, values, valid_mask, aggregation}`; only pair members allowed |
| `GET /api/v1/analyses/{id}/export` | `format=json` or `csv` | 200: downloadable report or region rows, with versions |
| `GET /api/v1/rubrics/{version}` | None | 200: immutable dimension definitions, weights, thresholds |
| `GET /api/v1/evaluations` | Optional cursor | 200: actual persisted evaluation summaries, empty until CLI runs |
| `GET /api/v1/evaluations/{id}` | None | 200: metrics, counts, uncertainty, config and failure inventory |
| `DELETE /api/v1/recordings/{id}` | None | 204 if unused; 409 with dependent IDs otherwise |

Report schema: `{schema_version, analysis_id, input_hashes, transcript_id, transcript_hash, config_hash, model_hashes, rubric_version, recording_quality, alignment_quality, dimensions, overall_score, regions, limitations, reproducibility}`. Each dimension contains `{id, score, coverage, reliability, unavailable_reason}`. Each region contains `{id, kind, dimension, participant_interval, participant_anchor_s, reference_interval, token_range, observation_ids, measurements:[{feature, unit, reference, participant, delta, tolerance, excess}], explanation, suggested_review, reliability, timing_uncertainty_s}`. `kind` is `interval` or `boundary_event`; boundary events have a null participant interval and a valid anchor, rather than a fabricated nonzero silence. Numeric timing uncertainty is null until measured on reviewed data. No example numbers here represent analysis results.

Errors: `{error:{code,message,recovery,field,retryable},request_id}` with 400 malformed input, 404 unknown ID, 409 incompatible state/pair/key, 413 size limit, 415 unsupported format, 422 invalid audio/text/config and 503 unavailable worker/model. Background failures use the same structure in job status. Frontend polls job state; progress is a named stage, not a fabricated percentage. Validate origin metadata independently before public dataset inclusion.

Optional imported alignment IDs must match the current recording/transcript hashes and pass interval validation. Without them, the job runs automatic alignment. Any manually recovered report records that origin; evaluation separates automatic and manually assisted runs. Retry can reference corrected transcript/recording IDs through a new analysis request, preserving the failed attempt.

Bind to loopback by default, restrict CORS to the local UI origin, require same-origin mutation requests in the bundled app, reject arbitrary file paths/URLs and escape transcript text. No telemetry or uploaded audio leaves the device. Public hosting/authentication is outside the initial architecture.

## Evaluation and reproducibility

The evaluation CLI reads a frozen split manifest and uses exactly the production engine/config. Save per-recording outputs, failures, aggregate metrics, seed, environment lock hashes, CPU/OS and code commit. Compare independent annotations, not transformation recipes, to detections. Keep calibration/train data separate from validation and sealed test data. See [dataset](dataset-plan.md), [scoring](scoring-policy.md) and [roadmap](implementation-roadmap.md) for gates. Fixed CPU operations, seeds and thread settings support repeatability; exact hashes cover inputs, while cross-environment floats use a documented numeric tolerance and unchanged decision checks.

## Primary technical references

Reviewed 2026-10-11. These inform the design; actual installed versions and limited CPU measurements are recorded separately in the Phase 2 evidence.

- [FastAPI background-task guidance](https://fastapi.tiangolo.com/tutorial/background-tasks/): heavy computation motivates a separate worker.
- [MFA installation](https://montreal-forced-aligner.readthedocs.io/en/stable/installation.html) and [alignment workflow](https://montreal-forced-aligner.readthedocs.io/en/stable/user_guide/workflows/alignment.html): isolated Conda environment, model inputs and version-sensitive CLI.
- [TorchAudio alignment lifecycle warning](https://docs.pytorch.org/audio/master/tutorials/ctc_forced_alignment_api_tutorial.html): do not build on removed alignment APIs.
- [React build-tool guidance](https://react.dev/learn/build-a-react-app-from-scratch): Vite fits the bounded local UI, with framework needs reconsidered if scope expands.
- [SQLite intended uses](https://www.sqlite.org/whentouse.html): embedded local persistence fits the single-user workstation.
- [SciPy polyphase resampling](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.signal.resample_poly.html) and [librosa pYIN implementation](https://librosa.org/doc/main/_modules/librosa/core/pitch.html): processing choices to verify against the versions eventually locked.
