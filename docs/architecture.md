# TakeTwo architecture

Speech analysis workspace. Status: Phase 1 dataset tooling and Phase 2 alignment/acoustic modules are implemented. Native Windows CPU MFA and real-audio extraction have run; independent timing/transcript review remains open. See [analysis engine](analysis-engine.md) and [actual validation](phase2-validation.md). Phase 3 comparison/scoring, review evidence and evaluation are implemented; [contracts and workflow](comparison-engine.md) and [validation](phase3-validation.md) are the current authority. Phase 4 now provides the FastAPI service, SQLite job history and React workspace; see [HTTP/lifecycle contracts](backend-api.md), [frontend guide](frontend-workspace.md) and [validation](phase4-validation.md). Target: Windows 11, Intel Core i7-1365U, 16 GB RAM, integrated graphics, local CPU processing. Start with single-speaker English excerpts; other languages, overlapping speech and unverified transcripts receive an explicit unsupported/review state.

## Technology decisions

Product stabilization retains this architecture and scientific formulas. A compact upload adapter now derives internal collection IDs and preserves unknown metadata in explicit dataset schema v2, with a backed-up opt-in v1 upgrade. Controlled references remain distinct from official public-speaker baselines. Report-bound dataset snapshots preserve history after unrelated imports while retaining exact input/review/code checks. Excerpts and pairing corrections create new recordings/versions rather than altering originals; see [current API contracts](backend-api.md) and [recording guide](recording-import-guide.md).

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

Phase 1 locks the Python dataset runtime in `pyproject.toml`/`uv.lock`; its purpose and license inventory is in [dependencies](dependencies.md). Phase 4 locks FastAPI/Uvicorn/multipart and the React/Vite/TypeScript/uPlot workspace; SQLite uses the Python standard library. Librosa's transitive scikit-learn dependency is present but unused for learning. Phase 2 locks the aligner environment and model artifacts separately in `environments/`; frontend versions are resolved when that phase starts. No paid API, CUDA, cloud inference, message broker or external database is required. Avoid introducing a waveform library until native audio/canvas interaction is shown to be insufficient.

## Boundaries and data model

The [Human Review Workspace](review-workspace.md) adds a dedicated SQLite lifecycle database for scoped reviewer drafts, sequential handoff and separate adjudication. Existing dataset/analysis/comparison artifacts remain scientific authority. Final exports are unchanged Phase 3 Review v1 records. A fail-closed handoff middleware isolates recording-scoped media/edit APIs from all analysis/peer APIs; the frontend mounts only the reviewer application during handoff. Capabilities and an OS-held operator key provide proportionate supervised local access control, not person authentication. No worker, acoustic algorithm, scoring rule or runtime dependency changes are introduced.

Implement cohesive modules only when their phase starts: ingestion, normalization, alignment, features, comparison, region detection, scoring, evaluation, persistence, API and UI. Engine functions accept explicit arrays/artifacts/configuration and do not depend on HTTP or UI state. Evaluation invokes the same engine through a CLI, without a browser.

Phase 1 implements `src/taketwo/dataset/`: schema, errors, safe storage, audio ingestion/normalization, controlled transformations, connected-group splitting, validation, workspace operations and CLI. Tests are in `tests/`. It uses one atomically replaced versioned JSONL manifest and managed local audio directories; SQLite is deferred until application sessions need it. The executable contracts and commands are in [dataset engineering](dataset-engineering.md).

Phase 4 SQLite persists job requests, states, stages, errors and immutable artifact references in schema version 1, with WAL and a five-second busy timeout. The existing dataset manifest remains authoritative for recordings/transcripts/pairs; comparison/analysis artifacts remain authoritative for science. Avoid duplicate mutable recording tables. See [implemented API/storage decisions](backend-api.md).

Store originals, normalized audio, per-recording alignment JSON, versioned feature JSON (current CLI authority; consider non-pickle array sidecars only if measured size requires them), waveform peaks and report JSON separately. Paths are server-generated IDs, never user-provided filesystem paths. Use atomic file publication followed by the DB transaction; recover orphan temporary files on startup. A canonical analysis identity hashes input bytes, transcript, configuration, code version, rubric and model checksums. Reports include artifact versions and validity, not merely a cached score.

## Phase 3 implementation boundary

`src/taketwo/comparison/` adds typed policy/report/review/evaluation contracts, centralized eligibility, reviewed canonical-token correspondence, native-frame aggregation, detectors, deterministic explanations, rubric aggregation and one-to-one temporal evaluation. It consumes Phase 2 feature/alignment artifacts without re-extraction or MFA. No dataset or Phase 2 code/schema was changed. Separate content-addressed `derived/comparison-v1/` artifacts bind upstream hashes, complete policy/configuration and comparison implementation hash. Rubric changes invalidate comparison reports while preserving cached acoustic evidence.

Manual timing/phrase reviews are separate immutable assertions bound to original automatic alignments. Two independent agreeing reviews are required for grounded comparison; manual boundaries never overwrite the machine artifact. The existing verified-transcript gate remains intact. Full support coverage, local clipping and pitch masks operate per region/dimension. Missing mirrors/reviews yield a valid abstention artifact with null scores, not a simulated report. Numeric evidence can still be inspected independently.

Authoritative flaw evaluation additionally uses `exact-inventory-v1`, described in
[comparison tools](comparison-engine.md). Semantic listening tolerance is not a
canonical boundary-selection rule. Exact numerical inventories must agree before
content-derived evaluation labels can be used; otherwise metrics are withheld
until explicit same-author revisions. Review inventory and separate adjudication
display the same unresolved state. Original reviews and historical evaluations
remain immutable; schema v1 and all acoustic/delivery rules are preserved.

The [comparison schema](comparison-schema-v1.json) defines `Report`, `Review` and `Evaluation`; Phase 4 API/UI adapters must use these contracts. Keep proposed HTTP lifecycle errors separate from scientific abstention and display boundary events without invented intervals. API/database/frontend remained outside Phase 3; Phase 4 adapts these contracts without modifying the engines. Full details and commands are in [the technical guide](comparison-engine.md).

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

Phase 4 runs one API process, one supervisor thread and at most one disposable CPU worker, with three additional queued jobs. States are `queued | running | completed | failed | cancelled`; interruption is a failed job with an explicit interrupted diagnostic. The parent owns the dataset lock, supervises timeout/cancellation and kills the Windows worker/MFA process tree. Validated completed stages publish atomically and survive later failures. Native-time envelopes and windowed features keep browser payloads bounded. Null scientific scores are valid completed reports.

## Implemented API v1

[Backend API](backend-api.md) and generated [OpenAPI](api-v1.json) supersede the Phase 0 proposed endpoint outline. Metadata and exact text arrive with multipart recording import; participant import creates a validated pair. HTTP serves actual original dataset/analysis/comparison models, job lifecycle, byte-range WAV, sample-coordinate waveform windows, bounded feature windows, reviewed-word overlays, policy, persisted evaluations/reviews and safe report downloads. TypeScript contracts are generated from these Python schemas; frontend calculations only format units and navigate time.

The launcher binds loopback, restricts browser origins/hosts, validates media using actual content and existing managed-path safeguards, limits resource use and exposes no arbitrary filesystem/model/command/URL API. No private audio/transcript telemetry is added. Phase 4B uses Windows kernel delete-on-close leases and named kill-on-close Job Objects for automatic process-crash recovery, a 4 GiB worker-tree commit limit and safe abandoned temporary cleanup. Authenticated human review, OS power-loss recovery and non-Windows web supervision remain unverified. See [Windows operation/recovery](windows-setup.md).

## Evaluation and reproducibility

The evaluation CLI reads a frozen split manifest and uses exactly the production engine/config. Save per-recording outputs, failures, aggregate metrics, seed, environment lock hashes, CPU/OS and code commit. Compare independent annotations, not transformation recipes, to detections. Keep calibration/train data separate from validation and sealed test data. See [dataset](dataset-plan.md), [scoring](scoring-policy.md) and [requirements](requirements-matrix.md) for gates. Fixed CPU operations, seeds and thread settings support repeatability; exact hashes cover inputs, while cross-environment floats use a documented numeric tolerance and unchanged decision checks.

## Primary technical references

Reviewed 2026-10-11. These inform the design; actual installed versions and limited CPU measurements are recorded separately in the Phase 2 evidence.

- [FastAPI background-task guidance](https://fastapi.tiangolo.com/tutorial/background-tasks/): heavy computation motivates a separate worker.
- [MFA installation](https://montreal-forced-aligner.readthedocs.io/en/stable/installation.html) and [alignment workflow](https://montreal-forced-aligner.readthedocs.io/en/stable/user_guide/workflows/alignment.html): isolated Conda environment, model inputs and version-sensitive CLI.
- [TorchAudio alignment lifecycle warning](https://docs.pytorch.org/audio/master/tutorials/ctc_forced_alignment_api_tutorial.html): do not build on removed alignment APIs.
- [React build-tool guidance](https://react.dev/learn/build-a-react-app-from-scratch): Vite fits the bounded local UI, with framework needs reconsidered if scope expands.
- [SQLite intended uses](https://www.sqlite.org/whentouse.html): embedded local persistence fits the single-user workstation.
- [SciPy polyphase resampling](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.signal.resample_poly.html) and [librosa pYIN implementation](https://librosa.org/doc/main/_modules/librosa/core/pitch.html): processing choices to verify against the versions eventually locked.

## Operational duration budget

`analysis/limits.py` owns the default and supported ceiling of 45 seconds. `TAKETWO_MAX_ANALYSIS_DURATION_S` accepts integer seconds 1–45; invalid configuration fails service startup. Restart after changing it. CLI alignment/extraction, API admission, native sample excerpt creation and disposable workers enforce it. Feature configuration may impose a smaller reproducible budget; it cannot bypass the deployment limit. API health supplies frontend controls/copy, with no independent frontend default. Dataset storage remains 600 seconds and 100 MiB. Native playback and waveform windows still cover complete originals. The serial worker, three queued jobs, 4 GiB Job Object, 32 MiB artifact bound, cancellation, atomic publication and identity checks remain intact. Job timeout remains 600 seconds; alignment default remains 120 seconds and existing local setup remains 180 seconds.

The shared `TAKETWO_MAX_ANALYSIS_DURATION_S` setting accepts integer seconds 1–45, default 45. Restart after changing it. See [duration configuration and verification](duration-validation.md).
