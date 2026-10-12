# Local backend API v1

TakeTwo — Speech analysis workspace. The executable HTTP contract is [api-v1.json](api-v1.json), generated from FastAPI/Pydantic by `scripts/export_api.py`. Scientific report, alignment, feature and dataset contracts remain unchanged; [comparison contracts](comparison-schema-v1.json) remain authoritative for calculations. HTTP lifecycle completion is separate from scientific eligibility.

| Endpoint | Contract and behavior |
| --- | --- |
| `GET /api/v1/health` | Product/version, acoustic readiness, local alignment configuration diagnostics, 30 s analysis / 100 MiB upload limits, one worker |
| `POST /api/v1/recordings` | Multipart `audio` and UTF-8 JSON `metadata` conforming to `ImportRequest`; 201 immutable `Recording`. Metadata includes `ImportSpec`, optional existing `reference_id`, intended category/severity. Participant import creates the dataset `Pair` transactionally |
| `GET /api/v1/recordings` / `/{id}` | Actual manifest `Recording` inventory / detail; original and derivative hashes, provenance, quality, text verification |
| `GET /api/v1/recordings/{id}/transcript` | Original `Transcript`; no automatic verification |
| `GET /api/v1/pairs` | Existing `Pair` records, including identity review state |
| `GET /api/v1/recordings/{id}/audio` | Validated 16 kHz mono WAV; HTTP byte ranges supported |
| `GET /api/v1/recordings/{id}/waveform` | Native `start_s`, `end_s`, `bins<=5000`; actual sample min/max envelopes with half-open sample bounds |
| `POST /api/v1/analyses` | `AnalysisRequest {reference_id,pair_id:null|string,align:bool}`; 202 `Job`. A missing pair permits genuine reference inspection and an abstention report |
| `GET /api/v1/analyses` / `/{id}` | Persistent job history / state; stages and structured error, retained artifact paths, no invented percentage |
| `POST /api/v1/analyses/{id}/cancel` | 202 cancellation request; terminal jobs return 409. Retry uses a fresh analysis request; history and completed artifacts remain |
| `GET /api/v1/analyses/{id}/alignments/{recording_id}` | Validated original `AlignmentResult`; failed attempts retain diagnostics; no substitute words |
| `GET /api/v1/analyses/{id}/features/{recording_id}` | `name`, native `start_s/end_s`, `max_points<=5000`; unit/frame/hop, bounded samples, quality, eligible pauses and rate/reason |
| `GET /api/v1/analyses/{id}/overlay` | `name=relative_energy|relative_pitch`; reviewed canonical word medians, independently native word intervals and null gaps. Unavailable correspondence returns a reason and empty arrays |
| `GET /api/v1/analyses/{id}/report` | Unmodified comparison `Report`; null scores remain null. Missing report or stale dataset/code identity returns 409 |
| `GET /api/v1/analyses/{id}/export` | `format=json|csv`; validated report JSON or region CSV with independent reference/participant intervals or boundary anchors; download only, no user-supplied output path |
| `GET /api/v1/rubrics/delivery-v0` | Actual immutable `Policy`, fixed four equal weights and original gates |
| `GET /api/v1/dataset` | Actual Phase 1 inventory summary; does not certify competition completion |
| `GET /api/v1/reviews` | Stored review assertions; no automatic approval or authentication claim |
| `GET /api/v1/evaluations` | Actual validated persisted `Evaluation` artifacts; software-fixture origins/modes remain explicit |

List responses intentionally cover the compact local workspace. No pagination contract or large-corpus scaling is claimed. SQLite stores lifecycle/history only; the immutable Phase 1 manifest remains the recording/transcript/pair authority. Duplicating its metadata into parallel mutable tables would create unnecessary consistency risks. `PRAGMA user_version=1`, WAL and a five-second busy timeout define the first application database version.

## Execution and publication

One service owns a workspace lease. One supervisor thread launches one disposable CPython process, with at most three queued requests. Exact duplicate active requests reuse their ID; other work runs serially. The parent owns the existing dataset lock, so imports and CLI mutations cannot race processing. Windows process-tree termination cancels CPU extraction and descendant MFA processes; the parent releases its lock and temporary directory. The whole-job deadline is 600 s; MFA retains its separately configured deadline. Queued cancellation is immediate. Running cancellation is a request until process termination completes.

Worker stages are validation, alignment/extraction per role, then comparison/scoring. Failed alignment can still yield measured acoustic evidence and an honest abstention report. Operational failures become failed jobs; null scientific scores are valid completed jobs. Engine failures report their exception category without recording private transcripts or aligner log contents. Use the analysis CLI for detailed prerequisite diagnostics.

Completed artifacts are first fully written under the workspace's managed `.runtime` directory, then published using exclusive atomic hard links into content-addressed managed storage on the same volume. Cancellation cannot publish truncated JSON. Completed earlier stages survive a later failure/cancellation. Atomic stage updates retry brief Windows sharing violations for at most one second. Cache lookup validates schema, payload digest, exact recording/text/environment/code provenance, feature configuration and original alignment hash; changed inputs never silently reuse old measurements. Reports bind dataset/comparison/policy hashes and are checked against current feature, alignment and relevant non-flaw review hashes. Eight parsed analysis objects are cached by managed path/mtime/size; request identity checks remain active.

Graceful shutdown cancels active processing. On Windows, kernel-owned exclusive delete-on-close service/dataset leases release after hard termination. Each worker and its MFA descendants belong to a named Job Object with kill-on-last-handle-close, no breakaway, a 16-process limit and a 4 GiB aggregate committed-memory limit. The worker waits for assignment before importing engines or creating children. Startup terminates any surviving named job tree, marks nonterminal history failed/interrupted without requeueing, then removes only validated managed `.runtime/taketwo-job-*` directories under the dataset lease. Originals and complete artifacts remain. Unknown CLI/legacy locks are preserved and block startup; see [Windows migration](windows-setup.md). This web supervisor currently requires Windows; scientific CLI behavior is unchanged. Readiness checks the supervisor thread; new jobs return 503 if it has stopped.

Job responses add nullable `elapsed_s`, nullable `peak_commit_bytes`, `stage_elapsed_s` and `cache_hits`. Old SQLite payloads load with defaults. Wall timings include startup, cache validation and artifact publication; they are operational observations outside deterministic scientific artifacts. Peak commit is the Windows Job Object accounting counter, not resident RAM, and may include attempted rejected allocations. Health exposes `maximum_worker_commit_bytes=4294967296`. One serial worker and one-thread numerical pools bound concurrency; this does not impose a hard CPU-percent quota on the service/browser.

## Security and resource boundaries

The launcher binds `127.0.0.1`; trusted hosts and a local origin allowlist restrict browser mutations. No URL downloader, shell command, model/configuration path, filesystem browsing or arbitrary export destination is accepted from HTTP. Configure the workspace and reviewed MFA configuration only at local startup. No authentication/cloud/storage account is added.

Uploads require bounded Content-Length, at most 100 MiB audio plus 1 MiB multipart metadata. Uploaded names are reduced to sanitized basenames; reserved/ambiguous Windows names are rejected. Declared MIME is restricted to WAV/FLAC/binary, then actual headers/samples are decoded by the unchanged Phase 1 validator. Existing sample/duration/channel/finite-value/truncation/downmix/path/symlink safeguards apply. Analysis remains limited to 30 seconds; increasing it requires CPU evidence. Whole-file originals remain immutable and private by default.

Errors use `{error:{code,message,recovery}}`. Request/metadata validation lists field locations without echoing private input values. Statuses include 403 origin, 404 unknown ID, 409 conflict/unavailable evidence, 411 missing length, 413 size, 415 MIME and 422 validation. Media uses `nosniff`; bundled UI uses same-origin content policy and no-store responses. The local filesystem owner remains trusted; hostile same-user filesystem replacement is outside the service threat model.

Visualization windows retain real sample/frame coordinates. Waveforms are actual min/max bins. Feature windows return original frames when small; otherwise grouped extrema with conservative null gap markers. Any group containing missing measurements becomes a gap, sacrificing detail rather than bridging unobserved pitch. Full spectra/MFCCs and raw series remain in immutable artifacts, not repeated navigation responses.
