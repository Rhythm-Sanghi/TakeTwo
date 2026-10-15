# Windows local workspace

Human reviews use the [Review Workspace](review-workspace.md). With the service workspace path in `$workspace`, read its private operator capability using `Get-Content (Join-Path $workspace '.review-operator-key')`. Assign supervised reviewers in fresh private browser windows; stop analysis first. Handoff stays locked across service restarts. End it with the private operator key, close the reviewer window, then inspect peer/adjudication evidence. Keep the key and SQLite files private and backed up; typed reviewer IDs are not authenticated identities. No additional installation or dependency is required.

Requires Windows 11, Python 3.11 with uv, and Node.js 24 LTS / npm (the executed environment used Node 24.15.0). CPU processing requires no CUDA. The backend and frontend use committed locks. Existing MFA/environment/model setup remains in [analysis engine](analysis-engine.md); it is installed separately and never downloaded by an analysis request.

## Install prerequisites first

Install Python 3.11 from [Python's Windows downloads](https://www.python.org/downloads/windows/),
uv using [Astral's installation instructions](https://docs.astral.sh/uv/getting-started/installation/),
and Node.js 24 with npm from [Node.js downloads](https://nodejs.org/en/download).
Install Git if cloning with the README command, or download/extract the GitHub source archive.
Open a new PowerShell terminal after installation and check:

```powershell
uv --version
uv python install 3.11
node --version
npm --version
```

Node should report version 24; the project requires Python 3.11. Setup downloads locked
dependencies and builds the interface. If a command is missing, finish its installation
and reopen the terminal. If PowerShell blocks the launcher, use the manual commands
below rather than changing machine-wide execution policy. Model configuration remains
a separate step; the quick-start time estimate does not include those downloads.

## Launch and recover

From the repository root in PowerShell:

First-time setup: `./scripts/start-local.ps1 -Setup`. Normal startup: `./scripts/start-local.ps1`. The normal path reuses the installed locked environment and existing build; it does not reinstall packages. Use `-Workspace .\local-data\practice-v2`, `-AlignmentConfig .\local-data\alignment-config.json` and/or `-Port 8876` as needed. Missing uv/npm/build and occupied ports produce explicit recovery messages. The equivalent manual first-time commands remain below.

```powershell
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
uv run taketwo-web
```

Open `http://127.0.0.1:8765`. This single local process serves the built UI and API; it launches a separate CPU worker only during analysis. The default managed workspace is `%LOCALAPPDATA%/TakeTwo/workspace`. Source checkout launch expects `frontend/dist`; the Python wheel provides the API/CLI, not prebuilt frontend assets. Launch from the repository root or pass `--frontend` explicitly.

The default analysis budget is 45 seconds per recording. To lower it, set `$env:TAKETWO_MAX_ANALYSIS_DURATION_S = '30'` before launching and restart the service. Integer values 1–45 are supported; invalid or larger values fail startup. Remove that variable to restore the shared default. API health and the UI report the active value. Imports remain 600 seconds / 100 MiB. No timeout increase is implied.

Configure alignment using a real reviewed local config, then restart:

```powershell
$env:TAKETWO_ALIGNMENT_CONFIG = 'C:\path\to\alignment-config.json'
uv run taketwo-analysis check --config $env:TAKETWO_ALIGNMENT_CONFIG
uv run taketwo-web --workspace .\local-data\application-v1
```

Configuration paths are operator-controlled startup inputs. Missing configuration permits actual acoustic inspection with explicit unavailable alignment/scoring. Do not copy test reviewer assertions into real metadata. Keep recordings/config/private evidence under ignored local storage. Use short WAV/FLAC excerpts, exact spoken text and explicit rights/consent references.

For frontend development, use two terminals:

```powershell
uv run taketwo-web --workspace .\local-data\development-v1
```

```powershell
npm --prefix frontend run dev
```

The Vite UI at `http://127.0.0.1:5173` proxies `/api` to port 8765. `scripts/start-local.ps1 -Setup` installs/builds; its normal path only launches. The backend does not hot-reload scientific source while jobs run.

## Verification

The Windows launcher uses a Selector event loop after a reproduced Proactor
accept-socket failure during abrupt client resets. Worker processes retain kernel
supervision and synchronous thread-based launching. See
[measured Windows hardening evidence](verification.md#windows-restoration-transport-and-cold-load-failures) for cold/warm
timings, tested recovery, the bounded local-server tradeoff and remaining latency
and WinError 10054 limits.

Unexpected CPU-worker failures retain a bounded private traceback under
`.diagnostics/<job-id>.log` in the selected workspace (maximum 32 KiB per failure).
The API retains a redacted diagnostic; no HTTP route exposes the private trace.
Traces can contain private paths/input details, so keep them out of public releases
and issue attachments until reviewed. If storage prevents log retention, the
original processing error remains unchanged. Existing logs are not overwritten.

The stabilization native smoke passed in a fresh short temporary workspace with
the original 180-second alignment config; earlier longer-workspace attempts timed
out or raised a permission error. This is a reproducible test setup to try, not a
proven path-length fix. Preserve original data/drafts and their hashes; do not
migrate them silently. See [full execution evidence](verification.md).

The [recording guide](user-guide.md#import-recordings) covers public, controlled and participant imports, exact-text pairing, explicit excerpting and review handoff. New workspaces use schema v2; an existing v1 workspace needs **Enable private draft imports** before local compact imports. This retains an exact manifest backup and does not grant rights or verification. No clean-machine compatibility is inferred from same-host setup testing.

Optional private pilot acceptance uses the explicit private fixture kit and `TAKETWO_TEST_ALIGNMENT_CONFIG` described in [browser testing](reproducibility.md#browser-verification-and-fixture-configuration); set `TAKETWO_PILOT_SMOKE=1` only after preparing those authorized inputs. It performs no public release or human approval. Native zoom uses an isolated profile; a host launch failure is unverified. Spoken screen-reader testing remains separate.

```powershell
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
uv run pytest -q
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv lock --check
uv build --no-sources
uv run python scripts/export_api.py
npm --prefix frontend run contracts
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run test
npm --prefix frontend run build
uv run python scripts/make_browser_fixtures.py
npm --prefix frontend exec -- playwright install chromium
npm --prefix frontend run e2e
uv run python scripts/check_repository.py
git diff --check
```

Generated oscillator fixtures are software tests only. E2E creates a fresh ignored workspace and performs actual HTTP imports and CPU extraction; no scientific route is mocked. Optional genuine source and 45-second suites require the external fixture kit and actual native MFA configuration documented in [browser testing](reproducibility.md#browser-verification-and-fixture-configuration). No hardcoded private path is required in a fresh checkout. Missing inputs mean not configured; models/audio are not shipped. Historical capacity evidence remains in [duration validation](verification.md#analysis-duration-and-capacity).

Graceful stop: Ctrl+C in the service terminal. Phase 4B Windows kernel leases release even after hard termination, and kill-on-close Job Objects terminate CPU/MFA descendants. Restart marks unfinished history failed/interrupted and cleans only managed job temporary directories after stopping surviving named trees. It never requeues interrupted work or deletes originals/complete artifacts. Use **Retry this analysis** for a new job; active identical requests still deduplicate. Worker aggregate commit is limited to 4 GiB, with one serial worker and one-thread numerical pools.

Migration from older versions: unknown pre-Phase-4B or CLI lock files are deliberately not deleted automatically. If startup reports a legacy lease, verify all old service/worker/MFA and CLI processes for that exact workspace are stopped. Preserve the workspace, then inspect/remove only its stale `.service.lock` / `.dataset.lock`; never remove a live lock. New crash recovery does not change the scientific CLI lock convention. Windows hard-process interruption is tested; OS power-loss/filesystem recovery and a packaged installer remain unverified. See [Phase 4B evidence](verification.md).

The shared `TAKETWO_MAX_ANALYSIS_DURATION_S` setting accepts integer seconds 1–45, default 45. Restart after changing it. See [duration configuration and verification](verification.md#analysis-duration-and-capacity).
