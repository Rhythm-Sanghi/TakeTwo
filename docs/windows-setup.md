# Windows local workspace

Requires Windows 11, Python 3.11 with uv, and Node.js 24 LTS / npm (the executed environment used Node 24.15.0). CPU processing requires no CUDA. The backend and frontend use committed locks. Existing MFA/environment/model setup remains in [analysis engine](analysis-engine.md); it is installed separately and never downloaded by an analysis request.

From the repository root in PowerShell:

```powershell
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
uv run taketwo-web
```

Open `http://127.0.0.1:8765`. This single local process serves the built UI and API; it launches a separate CPU worker only during analysis. The default managed workspace is `%LOCALAPPDATA%/TakeTwo/workspace`. Source checkout launch expects `frontend/dist`; the Python wheel provides the API/CLI, not prebuilt frontend assets. Launch from the repository root or pass `--frontend` explicitly.

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

The Vite UI at `http://127.0.0.1:5173` proxies `/api` to port 8765. `scripts/start-local.ps1` provides the build-and-launch convenience command. The backend does not hot-reload scientific source while jobs run.

## Verification

```powershell
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
npm --prefix frontend exec playwright install chromium
npm --prefix frontend run e2e
uv run python scripts/check_repository.py
git diff --check
```

Generated oscillator fixtures are software tests only. E2E creates a fresh ignored workspace and performs actual HTTP imports and CPU extraction; no scientific route is mocked. The optional `TAKETWO_REAL_SMOKE=1` test requires the previously acquired, rights-documented `local-data/acquisition/inaugural-salutation.wav` and `final-alignment-config.json`; these private/local assets are intentionally not shipped. See [pilot collection](pilot-collection.md) for provenance. `scripts/measure_browser_smoke.py` runs that available genuine-reference workflow and samples its full process tree, writing exclusive ignored evidence files.

Graceful stop: Ctrl+C in the service terminal. After an abrupt crash, first stop/check all old TakeTwo worker/MFA processes, preserve workspace files, then inspect/remove `.service.lock` and `.dataset.lock` inside that specific workspace before restarting. Inspect abandoned `.runtime/taketwo-job-*` temporary directories only after confirming their processes have stopped. Never remove a live CLI/service lock. Persisted unfinished jobs become failed/interrupted on startup; rerun analysis to retry. Originals/completed artifacts are retained. Crash-orphan automation and a packaged desktop installer remain open.
