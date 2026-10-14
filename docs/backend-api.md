# Local backend API v1

## Exploratory result additions

`GET /api/v1/analyses/{job_id}/exploratory` returns the separately versioned
[Exploratory Speech Analysis contract](exploratory-schema-v1.json). At least one
completed acoustic feature stage is required (otherwise HTTP 409). Missing members
produce a partial result; integrity/provenance failures do not produce replacement
measurements. `/exploratory/export?format=json|csv` exports checksum-bound reports
or native automatic-event rows. General-API handoff restrictions apply unchanged.
See [methods and cache boundaries](exploratory-analysis.md).

## Dataset presentation additions

`GET /api/v1/dataset` retains existing fields and adds default-empty `inventory_counts`
and `review_readiness`. The generated [contract](api-v1.json) and TypeScript adapter
include these additive fields; scientific schemas are unchanged. The CLI summary
supplies recording counts too; refresh after upgrade to load review readiness.

Inventory separates takes from declared speaker IDs. Connected families reuse
`connected_groups`, including shared speaker/source/work/text/pair/derivative links.
Stored independent/timing/flaw assertion counts include preserved revisions; neither
those assertions nor distinct IDs authenticate people or certify scientific readiness.

Recording workflow hints use manifest rights/consent/text, existing review consensus
and binding validation, and valid successful alignment/features. Other member,
original alignment, pair, coverage, acoustic and split gates remain authoritative
at comparison/evaluation. Active-handoff middleware still denies this endpoint;
navigation preselects operator preparation only and grants no session or capability.

## Human review lifecycle additions

The [review workflow](review-workspace.md) defines sequential operator/reviewer handoff and its local security limits. Prefix below is `/api/v1/review-workspace`. All lifecycle payloads are in the generated [OpenAPI contract](api-v1.json); final scientific evidence remains unchanged `Review` v1. Requests are capped at 1 MiB. Operator routes require `X-Review-Operator`, except unlock which takes an explicit key body. Reviewer routes use the active capability in a scoped HttpOnly/SameSite cookie; a session ID alone grants no access.

| Method / suffix | Behavior |
| --- | --- |
| `GET /mode` | Active handoff ID only; no capability, recording or peer evidence |
| `POST /sessions` | Operator `ReviewAssignment`; one-time `ReviewGrant`, atomic active handoff, blank unresolved draft; timing needs current successful MFA job, flaws need assigned participant pair |
| `POST /{sid}/activate` | `ActivateReview`; validate active capability, set scoped cookie, return only own `ReviewSession` |
| `GET /{sid}` | Own current session, original/machine text, suggestions when permitted, draft, provenance, integrity, listening/inspection state |
| `POST /{sid}/draft` | `DraftSave {revision,draft}`; revision is the session's **edit_revision**, independently of playback-event revision; transactional optimistic save, validate bounds/scope/current identities, invalidate changed-word inspection |
| `POST /{sid}/listen` | `ListeningEvent {start_s,end_s}`; positive <=2.5 s native playback increment bounded against server wall time; no seek-jump coverage or gap filling |
| `POST /{sid}/inspect` | `WordInspection {token_index}`; explicit saved boundary inspection after observed listening |
| `GET /{sid}/validation` | `ReviewValidation`; missing actions, exact full listening, notes/declarations, every timing word/phrase, current binding, changed-text regeneration warning; no scientific approval |
| `POST /{sid}/submit` | Saved `DraftSave`; immutable publication through existing Phase 3 validation/storage, auditable submitted lifecycle state. Never defaults decision to approved |
| `GET /{sid}/export` | Submitted `Review` JSON compatible with current importer; drafts return 409 |
| `GET /{sid}/summary` | Own lifecycle/provenance/annotations plus validation; explicitly not a scientific Review import |
| `GET /{sid}/audio` / `/waveform` | Assigned validated native media/ranges and bounded real envelope; no general inventory, predictions or recipes |
| `GET /{sid}/reference-audio` | Blinded-flaw activity only: paired reference audio context, no reference metadata/scores/reviews |
| `GET /inventory` | Operator only, unavailable during handoff: sessions, original review inventories, existing consensus differences and decision history |
| `POST /{sid}/resume` | Operator rotates capability, reopens saved own evidence without modifying submitted records; no active competing handoff allowed |
| `POST /unlock` | `OperatorKey`; explicit operator-controlled handoff end and cookie removal; close reviewer window before peer work |
| `POST /adjudications` | Operator `Adjudication`; distinct original reviews, all active evidence of subject/scope, binding validation, timestamped explained decision stored separately. Disagreements require explicit author revisions; no eligibility override |

During handoff, middleware denies **every general API** plus OpenAPI/docs, including peer reviews, recording metadata/audio, reports, scores, features, recipes and operator inventory. Scoped routes still require the correct active capability. Static assets and mode do not contain evidence. An operator key cannot read peer inventory while locked. This is supervised localhost access control, not proof of reviewer identity or protection from the OS/filesystem owner. All already-downloaded evidence and old tabs remain the operator's responsibility.

Additive `review-workspace.sqlite3` schema 1 uses WAL/transactions and internal/envelope digests; job database version 1, dataset schemas and immutable scientific contracts remain unchanged. See [storage/recovery limits](review-workspace.md). Final evidence becomes an ordinary existing content-addressed Review artifact consumed by unchanged worker/evaluation logic. Transcript correction/approval never mutates source text or provenance; reviewed new versions and regenerated artifacts remain required.

TakeTwo — Speech analysis workspace. The executable HTTP contract is [api-v1.json](api-v1.json), generated from FastAPI/Pydantic by `scripts/export_api.py`. Scientific report, alignment, feature and dataset contracts remain unchanged; [comparison contracts](comparison-schema-v1.json) remain authoritative for calculations. HTTP lifecycle completion is separate from scientific eligibility.

| Endpoint | Contract and behavior |
| --- | --- |
| `GET /api/v1/health` | Product/version, acoustic readiness, local alignment configuration diagnostics, configured analysis duration (default 45 s) / 100 MiB upload limits, one worker |
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

## Product stabilization additions

`POST /recordings` also accepts multipart metadata matching generated `LocalImportRequest`: `recording_type=public_reference|controlled_reference|human_participant`, exact draft transcript, local permission assertion, optional title/reference/speaker/rights/channel/intent. The original nested `ImportRequest` remains supported. Internal collection IDs and actual import time are generated on the server; selected reference supplies family/work. Unknown ownership/license/evidence/attribution stay null in schema v2. Missing intended labels stay `unspecified` with null severity. Explicit clearance still needs all actual rights fields and adaptation/redistribution permissions. Local permission never grants public release or verifies text. Unassigned speakers conservatively share an ID; same-speaker association requires an explicit choice.

| New endpoint | Contract / safeguards |
| --- | --- |
| `POST /api/v1/dataset/upgrade` | Explicit schema-v1-to-v2 metadata upgrade under workspace lock. Exact previous manifest backup retained; audio/IDs/artifacts and frozen membership preserved. No silent startup migration |
| `POST /api/v1/recordings/{id}/excerpt` | `ExcerptRequest {start_s,end_s,transcript,reference_id?}`; explicit native cut within the configured analysis duration (default 45 s) from original canonical samples, new unverified recording, parent hash/cut provenance, no original overwrite. Participant needs the matching excerpt reference |
| `POST /api/v1/pairs/{id}/correction` | `CorrectionRequest {reference_id}`; same canonical words, genuine participant; creates a separate two-recording version with copied immutable originals and reset text/review/intent state. Returns restart location/guidance; old workspace/history remains |
| `POST /api/v1/reviews/import` | `ReviewImportRequest {job_id,review}`; actual review contract bound to selected job member and original alignment. Reuses existing CLI validation/publication; never authenticates independence or changes transcript verification |

The dataset summary now identifies schema version. New web reports atomically retain content-addressed dataset snapshots beside immutable reports. Current API reads and CLI replay use the original snapshot when only unrelated data was added, verifying its digest and exact used recording/pair identity. Upstream content, policy/code and current review checks remain. Legacy artifacts without a needed snapshot require a fresh comparison; no historical context is guessed. SQLite remains lifecycle schema 1; no database migration or duplicate metadata authority is introduced.

## Worker execution

One service owns a workspace lease. One supervisor thread launches one disposable CPython process, with at most three queued requests. Exact duplicate active requests reuse their ID; other work runs serially. The parent owns the existing dataset lock, so imports and CLI mutations cannot race processing. Windows process-tree termination cancels CPU extraction and descendant MFA processes; the parent releases its lock and temporary directory. The whole-job deadline is 600 s; MFA retains its separately configured deadline. Queued cancellation is immediate. Running cancellation is a request until process termination completes.

Worker stages are validation, alignment/extraction per role, then comparison/scoring. Failed alignment can still yield measured acoustic evidence and an honest abstention report. Operational failures become failed jobs; null scientific scores are valid completed jobs. Engine failures report their exception category without recording private transcripts or aligner log contents. Use the analysis CLI for detailed prerequisite diagnostics.

Completed artifacts are first fully written under the workspace's managed `.runtime` directory, then published using exclusive atomic hard links into content-addressed managed storage on the same volume. Cancellation cannot publish truncated JSON. Completed earlier stages survive a later failure/cancellation. Atomic stage updates retry brief Windows sharing violations for at most one second. Cache lookup validates schema, payload digest, exact recording/text/environment/code provenance, feature configuration and original alignment hash; changed inputs never silently reuse old measurements. Reports bind dataset/comparison/policy hashes and are checked against current feature, alignment and relevant non-flaw review hashes. Eight parsed analysis objects are cached by managed path/mtime/size; request identity checks remain active.

Graceful shutdown cancels active processing. On Windows, kernel-owned exclusive delete-on-close service/dataset leases release after hard termination. Each worker and its MFA descendants belong to a named Job Object with kill-on-last-handle-close, no breakaway, a 16-process limit and a 4 GiB aggregate committed-memory limit. The worker waits for assignment before importing engines or creating children. Startup terminates any surviving named job tree, marks nonterminal history failed/interrupted without requeueing, then removes only validated managed `.runtime/taketwo-job-*` directories under the dataset lease. Originals and complete artifacts remain. Unknown CLI/legacy locks are preserved and block startup; see [Windows migration](windows-setup.md). This web supervisor currently requires Windows; scientific CLI behavior is unchanged. Readiness checks the supervisor thread; new jobs return 503 if it has stopped.

Job responses add nullable `elapsed_s`, nullable `peak_commit_bytes`, `stage_elapsed_s` and `cache_hits`. Old SQLite payloads load with defaults. Wall timings include startup, cache validation and artifact publication; they are operational observations outside deterministic scientific artifacts. Peak commit is the Windows Job Object accounting counter, not resident RAM, and may include attempted rejected allocations. Health exposes `maximum_worker_commit_bytes=4294967296`. One serial worker and one-thread numerical pools bound concurrency; this does not impose a hard CPU-percent quota on the service/browser.

## Security and resource boundaries

The launcher binds `127.0.0.1`; trusted hosts and a local origin allowlist restrict browser mutations. No URL downloader, shell command, model/configuration path, filesystem browsing or arbitrary export destination is accepted from HTTP. Configure the workspace and reviewed MFA configuration only at local startup. No authentication/cloud/storage account is added.

Uploads require bounded Content-Length, at most 100 MiB audio plus 1 MiB multipart metadata. Uploaded names are reduced to sanitized basenames; reserved/ambiguous Windows names are rejected. Declared MIME is restricted to WAV/FLAC/binary, then actual headers/samples are decoded by the unchanged Phase 1 validator. Existing sample/duration/channel/finite-value/truncation/downmix/path/symlink safeguards apply. Analysis uses the shared duration setting (default 45 seconds); the worker rechecks actual sample count. Whole-file originals remain immutable and private by default.

Errors use `{error:{code,message,recovery}}`. Request/metadata validation lists field locations without echoing private input values. Statuses include 403 origin, 404 unknown ID, 409 conflict/unavailable evidence, 411 missing length, 413 size, 415 MIME and 422 validation. Media uses `nosniff`; bundled UI uses same-origin content policy and no-store responses. The local filesystem owner remains trusted; hostile same-user filesystem replacement is outside the service threat model.

Visualization windows retain real sample/frame coordinates. Waveforms are actual min/max bins. Feature windows return original frames when small; otherwise grouped extrema with conservative null gap markers. Any group containing missing measurements becomes a gap, sacrificing detail rather than bridging unobserved pitch. Full spectra/MFCCs and raw series remain in immutable artifacts, not repeated navigation responses.

The shared `TAKETWO_MAX_ANALYSIS_DURATION_S` setting accepts integer seconds 1–45, default 45. Restart after changing it. See [duration configuration and verification](duration-validation.md).
