# TakeTwo architecture

Speech analysis workspace. A local Python/FastAPI service and serial supervised
workers process immutable recording and scientific artifacts; React presents
analysis, native playback, review and dataset/evaluation workflows. SQLite stores
job and review lifecycle state. [HTTP contracts](backend-api.md),
[browser interaction contracts](#browser-interaction-contracts), [acoustic extraction](analysis-engine.md)
and [comparison methods](comparison-engine.md) describe the component interfaces.

The measured target is Windows 11, Intel Core i7-1365U, 16 GB RAM and local CPU
processing. Start with single-speaker English excerpts. Other languages,
overlapping speech and unverified transcripts receive explicit unsupported/review
states. Native processing and software checks have executed; independent speech
accuracy and broader hardware compatibility remain open. See [verification](verification.md).


## Technology decisions

A compact upload adapter derives internal collection IDs and preserves unknown metadata in explicit dataset schema v2, with a backed-up opt-in v1 upgrade. Controlled references remain distinct from official public-speaker baselines. Report-bound dataset snapshots preserve history after unrelated imports while retaining exact input/review/code checks. Excerpts and pairing corrections create new recordings/versions rather than altering originals; see [current API contracts](backend-api.md) and [recording guide](user-guide.md#import-recordings).

| Layer | Selection and purpose | Tradeoff / verification gate |
| --- | --- | --- |
| API | Python 3.11 baseline, FastAPI, Pydantic, Uvicorn | Typed request/response contracts; versions pinned in pyproject.toml and uv.lock |
| Audio I/O | soundfile | Decode WAV/FLAC, inspect actual format; no mandatory FFmpeg; direct import supports WAV/FLAC |
| Numerics | NumPy and SciPy | Arrays, FFT, resampling and signal/statistical calculations |
| Acoustic features | librosa | MFCCs and pitch estimation; pitch abstains when confidence/support is insufficient; measured limits are explicit |
| Evaluation | NumPy/SciPy | Deterministic metrics need no learned model; scikit-learn is transitive through librosa, with no trained classifier |
| Alignment | Montreal Forced Aligner (MFA), separate Conda/Miniforge environment | CPU-first dictionary/acoustic alignment; native execution verified, independent timing gate remains open |
| UI | React, TypeScript, Vite | Local interactive workspace needs no SSR; CSS tokens, native audio, canvas waveform with accessible DOM controls |
| Metadata | Python sqlite3, SQL migrations | Local single-user persistence with no server or ORM requirement |
| Storage | Managed local files under `%LOCALAPPDATA%/TakeTwo` | Original audio immutable; retained content-addressed artifacts and integrity-checked replay |
| Verification | pytest; Vitest + Testing Library; Playwright | Signal/contract tests, accessible interaction tests and real browser workflows |

Python runtime/development pins are in `pyproject.toml`/`uv.lock`; frontend resolution
is in `frontend/package-lock.json`. Native MFA/model resources are locked separately
in `environments/`. SQLite uses the standard library and librosa's transitive
scikit-learn dependency is unused for learning. See [dependency purposes and notices](attributions.md#dependency-inventory).
Local installation needs no paid API, CUDA, cloud inference, message broker or external database.

## Boundaries and data model

The [Human Review Workspace](review-workspace.md) adds a dedicated SQLite lifecycle database for scoped reviewer drafts, sequential handoff and separate adjudication. Existing dataset/analysis/comparison artifacts remain scientific authority. Final exports are unchanged Phase 3 Review v1 records. A fail-closed handoff middleware isolates recording-scoped media/edit APIs from all analysis/peer APIs; the frontend mounts only the reviewer application during handoff. Capabilities and an OS-held operator key provide proportionate supervised local access control, not person authentication. No worker, acoustic algorithm, scoring rule or runtime dependency changes are introduced.

Engine modules accept explicit arrays/artifacts/configuration and do not depend on
HTTP or UI state. CLI evaluation invokes the same production methods without a browser.

`src/taketwo/dataset/` contains schema, errors, safe storage, audio ingestion/normalization, controlled transformations, connected-group splitting, validation, workspace operations and CLI. Tests are in `tests/`. It uses one atomically replaced versioned JSONL manifest and managed local audio directories; SQLite stores application lifecycle state separately. The executable contracts and commands are in [dataset engineering](dataset-engineering.md).

SQLite persists job requests, states, stages, errors and immutable artifact references in schema version 1, with WAL and a five-second busy timeout. The existing dataset manifest remains authoritative for recordings/transcripts/pairs; comparison/analysis artifacts remain authoritative for science. Avoid duplicate mutable recording tables. See [implemented API/storage decisions](backend-api.md).

Store originals, normalized audio, per-recording alignment JSON, versioned feature JSON, waveform peaks and report JSON separately. Paths are server-generated IDs, never user-provided filesystem paths. Publish complete artifacts atomically and persist lifecycle references. Review evidence uses a journaled publication intent with restart reconciliation; recover only owned managed temporary files on startup, without replacing corrupt evidence. A canonical analysis identity hashes input bytes, transcript, configuration, code version, rubric and model checksums. Reports include artifact versions and validity, not merely a cached score.

## Comparison and review boundary

`src/taketwo/comparison/` adds typed policy/report/review/evaluation contracts, centralized eligibility, reviewed canonical-token correspondence, native-frame aggregation, detectors, deterministic explanations, rubric aggregation and one-to-one temporal evaluation. It consumes immutable feature/alignment artifacts without re-extraction or MFA. Separate content-addressed `derived/comparison-v1/` artifacts bind upstream hashes, complete policy/configuration and comparison implementation hash. Rubric changes invalidate comparison reports while preserving cached acoustic evidence.

Manual timing/phrase reviews are separate immutable assertions bound to original automatic alignments. Two independent agreeing reviews are required for grounded comparison; manual boundaries never overwrite the machine artifact. The existing verified-transcript gate remains intact. Full support coverage, local clipping and pitch masks operate per region/dimension. Missing mirrors/reviews yield a valid abstention artifact with null scores, not a simulated report. Numeric evidence can still be inspected independently.

Authoritative flaw evaluation additionally uses `exact-inventory-v1`, described in
[comparison tools](comparison-engine.md). Semantic listening tolerance is not a
canonical boundary-selection rule. Exact numerical inventories must agree before
content-derived evaluation labels can be used; otherwise metrics are withheld
until explicit same-author revisions. Review inventory and separate adjudication
display the same unresolved state. Original reviews and historical evaluations
remain immutable; schema v1 and all acoustic/delivery rules are preserved.

The [comparison schema](comparison-schema-v1.json) defines `Report`, `Review` and `Evaluation`; API/UI adapters use these contracts. Keep operational HTTP lifecycle errors separate from scientific abstention and display boundary events without invented intervals. The service and UI adapt these contracts without inventing scientific results. Full details and commands are in [the technical guide](comparison-engine.md).

## Recording-to-report workflow

1. Upload each recording and a UTF-8 transcript; enforce 100 MiB/file, 10 minutes/recording, one or two channels and 8-96 kHz as import limits. The UI accepts a `.txt` upload or pasted text and sends its content to the transcript endpoint, with a 100,000-character limit. Validate decoded headers, finite samples and actual duration before expensive work. Supported import containers are WAV/FLAC; analysis has a separate measured duration budget below.
2. Preserve original bytes/hash. Inspect channel cancellation before downmixing; ask for channel selection if averaging would destroy speech. Create a 16 kHz mono analysis derivative with SciPy polyphase resampling. Keep raw level/clipping evidence; no automatic loudness normalization, denoising, silence trimming or time stretching. Source and derivative time origins remain identical; cropped dataset excerpts record their source offset.
3. Flag silence, poor signal quality and clipping (clipping warning: more than 0.1% of decoded samples at magnitude >=0.999; quality indicators are heuristic). Reject corrupt/empty files, all-silence and incompatible text. Ask the user to review suspected omissions rather than forcing arbitrary matches.
4. Pair the recordings against one canonical transcript; punctuation normalization never silently removes spoken words. Align each independently with MFA. Preflight pronunciation coverage, model presence and language; retain original token-to-normalized-token correspondence.
5. Parse word/phone intervals and validate ordering, bounds and word coverage. Save alignment diagnostics; suspected mismatch or missing model produces `needs_review` or `failed`, never evenly spaced substitute timestamps. Manual reviewed alignment import is a recovery path with provenance, not an automatic equivalent to forced alignment.
6. Compute frame features on each native time axis; aggregate per shared word/phrase and inter-word pause. Use token correspondence for comparison; do not warp away duration or pause differences. Features and masks are specified in the [scoring policy](scoring-policy.md).
7. Compute deltas, threshold crossings and participant-time regions. Attach corresponding reference intervals, feature evidence and uncertainty. Aggregate dimension scores only where evidence is valid; report unavailable dimensions explicitly.
8. Persist report/artifacts atomically. UI displays waveform, correspondence, evidence and rubric. Export versioned JSON/CSV and deliberate searchable summary/full reports; exports do not approve scientific evidence.

## Alignment and Windows execution

MFA 3.3.9 is pinned with English US ARPA model/dictionary release v3.0.0 (CC BY 4.0), verified in native Windows smoke runs. Independent manual timing evaluation remains open. Invoke the locked CLI via argument arrays, never a shell-interpolated command. Use one isolated job directory; capture command/version, logs, timeout and output hashes. Run alignment serially under the supervised worker tree and its explicit process/commit limits. Pin the command signature as well as artifacts because upstream model formats/CLI are changing. No automatic model downloads during analysis.

If installation, licensing or accuracy blocks MFA, stop the alignment gate and evaluate another maintained CPU aligner on the same manually timed pilot. Do not silently switch engines or rely on removed TorchAudio alignment APIs. A manually annotated pilot enables independent timing evaluation but does not satisfy the automatic alignment requirement by itself.

The application runs one API process, one supervisor thread and at most one disposable CPU worker, with three additional queued jobs. States are `queued | running | completed | failed | cancelled`; interruption is a failed job with an explicit interrupted diagnostic. The parent owns the dataset lock, supervises timeout/cancellation and kills the Windows worker/MFA process tree. Validated completed stages publish atomically and survive later failures. Native-time envelopes and windowed features keep browser payloads bounded. Null scientific scores are valid completed reports.

## Implemented API v1

[Backend API](backend-api.md) and generated [OpenAPI](api-v1.json) are the implemented API authority. Metadata and exact text arrive with multipart recording import; participant import creates a validated pair. HTTP serves actual original dataset/analysis/comparison models, job lifecycle, byte-range WAV, sample-coordinate waveform windows, bounded feature windows, reviewed-word overlays, policy, persisted evaluations/reviews and safe report downloads. TypeScript contracts are generated from these Python schemas; frontend calculations only format units and navigate time.

The launcher binds loopback, restricts browser origins/hosts, validates media using actual content and existing managed-path safeguards, limits resource use and exposes no arbitrary filesystem/model/command/URL API. No private audio/transcript telemetry is added. The Windows supervisor uses kernel delete-on-close leases and named kill-on-close Job Objects for automatic process-crash recovery, a 4 GiB worker-tree commit limit and safe abandoned temporary cleanup. Authenticated human review, OS power-loss recovery and non-Windows web supervision remain unverified. See [Windows operation/recovery](windows-setup.md).

## Evaluation and reproducibility

The evaluation CLI reads a frozen split manifest and uses exactly the production engine/config. Save per-recording outputs, failures, aggregate metrics, seed, environment lock hashes, CPU/OS and code commit. Compare independent annotations, not transformation recipes, to detections. Keep calibration/train data separate from validation and sealed test data. See [dataset](dataset-engineering.md#collection-and-evaluation-design), [scoring](scoring-policy.md) and [requirements](requirements-matrix.md) for gates. Fixed CPU operations, seeds and thread settings support repeatability; exact hashes cover inputs, while cross-environment floats use a documented numeric tolerance and unchanged decision checks.

## Primary technical references

Reviewed 2026-10-11. These inform the design; actual installed versions and CPU measurements are in [verification](verification.md).

- [FastAPI background-task guidance](https://fastapi.tiangolo.com/tutorial/background-tasks/): heavy computation motivates a separate worker.
- [MFA installation](https://montreal-forced-aligner.readthedocs.io/en/stable/installation.html) and [alignment workflow](https://montreal-forced-aligner.readthedocs.io/en/stable/user_guide/workflows/alignment.html): isolated Conda environment, model inputs and version-sensitive CLI.
- [TorchAudio alignment lifecycle warning](https://docs.pytorch.org/audio/master/tutorials/ctc_forced_alignment_api_tutorial.html): do not build on removed alignment APIs.
- [React build-tool guidance](https://react.dev/learn/build-a-react-app-from-scratch): Vite fits the bounded local UI, with framework needs reconsidered if scope expands.
- [SQLite intended uses](https://www.sqlite.org/whentouse.html): embedded local persistence fits the single-user workstation.
- [SciPy polyphase resampling](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.signal.resample_poly.html) and [librosa pYIN implementation](https://librosa.org/doc/main/_modules/librosa/core/pitch.html): processing references; actual versions are recorded in the locks.

## Operational duration budget

`analysis/limits.py` owns the default and supported ceiling of 45 seconds. `TAKETWO_MAX_ANALYSIS_DURATION_S` accepts integer seconds 1–45; invalid configuration fails service startup. Restart after changing it. CLI alignment/extraction, API admission, native sample excerpt creation and disposable workers enforce it. Feature configuration may impose a smaller reproducible budget; it cannot bypass the deployment limit. API health supplies frontend controls/copy, with no independent frontend default. Dataset storage remains 600 seconds and 100 MiB. Native playback and waveform windows still cover complete originals. The serial worker, three queued jobs, 4 GiB Job Object, 32 MiB artifact bound, cancellation, atomic publication and identity checks remain intact. Job timeout remains 600 seconds; alignment default remains 120 seconds and existing local setup remains 180 seconds.

See [duration measurements and limits](verification.md#analysis-duration-and-capacity).


## Browser interaction contracts

The React/strict TypeScript/Vite workspace has five areas: Recording Library,
Analysis Workspace, Rubric and Evidence, Review Workspace, and Dataset and Evaluation.
The complete collection/history lives only in Library. History reopens the actual
stored request and artifacts with readable names and converted UTC timestamps.
Successful import waits for inventory refresh and selects the returned pair;
exact-request retries preserve failed/cancelled request identity.

`App` coordinates inventory, selection and request state. Focused modules include
`AnalysisResult`, `ComparativeInsights`, `ExploratoryResult`, `DatasetReadiness`,
`ReviewWorkspace`, `ReviewJourney`, `ImportForm`, `Timeline`, `TokenOverlay` and
`Evidence`. Client types come from the checked-in OpenAPI schema. No frontend formula
detects or scores flaws; render backend eligibility, observations, nulls and reasons.
No aggregate eligible-pair count or authenticated reviewer identity is inferred.

Bind displayed reports to job ID/path, request/pair and actual recording IDs.
Selection/history changes synchronously clear obsolete results. Bound dataset
snapshots preserve history after unrelated imports; changed used inputs, reviews,
configuration/code or corrupt snapshots still fail identity checks. Reference-only
processing uses inspection terminology; its lack of a participant is not a failure.

Native HTML audio elements keep independent clocks. Only one track plays at once.
At 800 px and below the track switch pauses audio while preserving each mounted
cursor and interval. Numeric seek/selection uses 16 kHz sample-resolution steps;
waveform dragging has numeric keyboard alternatives. Replay stops at its own end;
a new seek clears the previous bound. Region/boundary actions use each contract
location, never an invented silence interval or wall-time warp. Word overlays require
backend correspondence/review gates and use canonical word index plus native seeking.

A small canvas renderer draws actual min/max sample envelopes. uPlot renders backend
RMS, energy, supported F0, activity and centroid, with explicit clocks, units,
frame/hop and aggregation. Null pitch stays a gap. Synchronous print hooks snapshot
existing plots at paper width; no second acoustic renderer or PDF service is added.
Dedicated reports retain complete inventories; workspace print retains current native
charts and selected findings. See [user operations](user-guide.md) for export/QA steps.

During reviewer handoff the operator application is not mounted. Scope navigation
preserves the capability URL fragment and mounted editors, without saving or granting
access. Save indicators require server acknowledgement; completion requires actual
backend validation/submission. Unsaved edits remain on conflicts. Shared scientific
blockers appear once, with unique counts/coverage/minimums and reason codes in details.
Pitch baselines are diagnostic accepted-F0 medians; the 50% support requirement is per
scored phrase. Independent evaluation requires an actual bound eligible human run,
not a route fixture or software-only metric. [Review Workspace](review-workspace.md)
documents capability, privacy and identity boundaries.
