# TakeTwo

Speech analysis workspace

TakeTwo is a professional speech-analysis workstation for comparing reference and participant recordings of the same transcript, inspecting temporally grounded acoustic evidence, and scoring delivery with an explainable rubric.

The interface follows the Workshop + Gridline + Studio Utility design language. Engineering, design and scientific integrity standards are defined in [AGENTS.md](AGENTS.md).

## Project status

Phase 0–4 software is implemented: dataset tools, native CPU alignment/acoustics, evidence-gated comparison/evaluation and a local FastAPI/SQLite + React/TypeScript/Vite workspace. Phase 4B adds Windows crash-contained workers, automatic interrupted-job recovery, bounded worker memory, exact-request retry and accessibility fixes. Genuine archival audio has passed browser import-to-MFA-to-report/playback/export and cache reuse. **Acceptance remains partial:** no participant recordings or independent reviews are available; human-pair accuracy, calibration, screen-reader speech and 200% browser zoom remain unverified. See [Phase 4B evidence](docs/phase4b-validation.md) and the [human recording/review kit](docs/human-pilot-kit.md).

Development must preserve the Track C requirements for contrastive datasets, forced alignment, acoustic feature extraction, temporal grounding, explainable rubric-based scoring, reproducibility, a dashboard and deliverables.

## Phase 0 documentation

- [Requirements matrix and official judging weights](docs/requirements-matrix.md)
- [Architecture, API contracts and recording-to-report workflow](docs/architecture.md)
- [Dataset acquisition, annotations and evaluation splits](docs/dataset-plan.md)
- [Scoring formulas, uncertainty and evaluation methodology](docs/scoring-policy.md)
- [Design system and accessibility](docs/design-system.md)
- [Implementation phases, evidence gates and next step](docs/implementation-roadmap.md)
- [Risks, mitigations and blockers](docs/risk-register.md)

Selected stack: local Python/FastAPI/Uvicorn, NumPy/SciPy/librosa/soundfile, CPU MFA, SQLite job history, managed audio files and React/TypeScript/Vite with uPlot. The Phase 1 manifest remains the metadata authority; scientific engines are unchanged. Dependencies are pinned in `uv.lock` and `frontend/package-lock.json`. scikit-learn remains a librosa transitive dependency, with no learned scoring/training. MFA model/dictionary hashes and licenses remain separately recorded.

## Open the local application

```powershell
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
uv run taketwo-web
```

Open `http://127.0.0.1:8765`. Python 3.11 and Node 24 are required. The default workspace is `%LOCALAPPDATA%/TakeTwo/workspace`; no recordings are seeded. Set `TAKETWO_ALIGNMENT_CONFIG` to a reviewed local MFA configuration to enable alignment. Without it, actual acoustic inspection remains available with explicit abstention. WAV/FLAC imports support up to 100 MiB/600 s; analysis remains bounded to 30 s.

Read [Windows setup and verification commands](docs/windows-setup.md), [backend API/lifecycle](docs/backend-api.md), [frontend interactions](docs/frontend-workspace.md) and [Phase 4 evidence](docs/phase4-validation.md). `scripts/start-local.ps1` builds and launches locally. Two-terminal development uses `uv run taketwo-web` and `npm --prefix frontend run dev`. No cloud account, CUDA or broker is required.

## Dataset tools

```powershell
uv sync --locked
uv run taketwo-dataset --help
uv run pytest -q
uv run ruff check src tests
```

Use Python 3.11. Read the [dataset-engineering guide](docs/dataset-engineering.md) for schema, PowerShell commands, annotation workflow and release checks, and the [dependency inventory](docs/dependencies.md) for purpose/license notes. [Phase 1 validation evidence](docs/phase1-validation.md) separates software tests from actual dataset readiness. Keep local recordings under ignored `local-data/` or outside the checkout.

## Analysis tools

Read the [analysis engine guide](docs/analysis-engine.md), [Phase 2 validation evidence](docs/phase2-validation.md), and [genuine pilot / human collection procedure](docs/pilot-collection.md). MFA runs in a separately locked environment; model and dictionary hashes/licenses are recorded in `environments/`. threadpoolctl 3.7.0, already present transitively, is now explicitly pinned to enforce one BLAS thread for reproducible MFCC calculations.

```powershell
uv run taketwo-analysis --help
uv run taketwo-analysis check --config .\local-data\alignment-config.json
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
```

Commands: `check`, `align`, `extract`, `inspect`, `validate`, `export`. Features operate on short imported clips even if alignment is unavailable; rates and inter-word pauses require complete alignment and verified transcripts. Stable [analysis schema v1](docs/analysis-schema-v1.json) is separate from unchanged dataset schema v1. Local audio and generated artifacts remain ignored and unpublished.

## Comparison and review tools

Read the [comparison engine and PowerShell guide](docs/comparison-engine.md), [schema v1](docs/comparison-schema-v1.json) and [Phase 3 validation](docs/phase3-validation.md). Phase 3 uses cached Phase 2 features; no additional dependencies, service or frontend was introduced.

```powershell
uv run taketwo-comparison --help
uv run taketwo-comparison schema
uv run python scripts/check_repository.py
```

Commands: `compare`, `detect`, `score`, `evidence`, `import-review`, `inspect`, `validate`, `evaluate`, `export`, `schema`. Exit 3 explicitly marks scientific abstention. Unavailable dimensions never receive perfect scores or redistributed weights. Real input remains blocked by absent human mirrors/reviews; generated fixtures establish software behavior only.

Next, collect consented human mirrors and independent transcript/timing/flaw reviews, then verify a legitimate eligible pair and held-out evaluation. The local dashboard is implemented; complete real-pair acceptance remains unverified. Phase 5 prepares the local submission package below. Public dataset/code release, video upload and submission remain owner actions; no public dataset or YouTube URL is available.

## Submission package

- [Actions requiring people, expected filenames and handoff](docs/ACTION-REQUIRED.md)
- [Final official compliance audit and judging weights](docs/submission-compliance.md)
- [Technical report editable source](docs/technical-report.md) and [rendered draft PDF](output/pdf/taketwo-technical-report.pdf)
- [Five-minute demonstration script and recording checklist](docs/demo-script.md)
- [Dataset publication and public download verification](docs/dataset-publication.md)
- [Locked setup, review import and evaluation reproduction](docs/reproducibility.md)
- [Attributions, licensing status and tool disclosure](docs/attributions.md)
- [Devpost description draft and final artifact checklist](docs/submission-draft.md)
- [Phase 5 checks actually executed](docs/phase5-validation.md)

The human package includes [recording directions and explicitly unverified draft words](docs/recording-session.md), a [blank private consent/provenance form](docs/consent-provenance-form.md), and the existing independent annotation worksheet. No exact verified source transcript can be supplied until two humans check it. Both acquired masters share JFK; no participant or review evidence exists. Keep delivery-v0 unchanged and do not tune held-out labels. Missing real metrics, scores and confidence remain unavailable.

Regenerate the report on Windows with `python scripts/build_submission_report.py` in a separate document-tool environment containing ReportLab; inspect it with pypdf/Poppler and confirm at most six pages. These authoring tools are not application dependencies. Source-code license selection and final public release review remain owner decisions. Existing dependencies/resources retain their own terms. No audio, model, consent record or runtime workspace is committed.

## Known limitations

Independent alignment/detection accuracy, rubric calibration, cross-speaker generalization and cross-environment equivalence remain unmeasured. The genuine draft salutation has no accepted pYIN frames under the current threshold; pitch, rates and scores can be unavailable. Comparison requires verified words and two independent timing/phrase reviews per member. Current web process supervision requires Windows; analysis is capped at 30 s. Actual 200% browser zoom and heard screen-reader output remain unverified. Automated tests do not establish production readiness or scientific validity.

## AI assistance and attributions

Codex assisted with the product rename, specification review, Phase 0 planning and Phase 1–4B implementation/tests, rights-source research, actual CPU runs, crash/restart and browser verification, blank human collection materials and Phase 5 submission preparation. Generated signal fixtures verify software behavior and are not the competition dataset. Rubric selections remain proposals awaiting real held-out evaluation. AI assistance must continue to be disclosed honestly as the project develops.
