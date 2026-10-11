# TakeTwo

Speech analysis workspace

TakeTwo is a professional speech-analysis workstation for comparing reference and participant recordings of the same transcript, inspecting temporally grounded acoustic evidence, and scoring delivery with an explainable rubric.

The interface follows the Workshop + Gridline + Studio Utility design language. Engineering, design and scientific integrity standards are defined in [AGENTS.md](AGENTS.md).

## Project status

Phase 0 planning and Phase 1 dataset tooling are implemented. Phase 2 now provides native Windows CPU MFA alignment, transcript/OOV preflight, numerical acoustic features, typed derived artifacts and an analysis CLI. Real public-domain audio has been processed. **Phase 1B and Phase 2 acceptance remain partially complete**: human mirrors, independent transcript/timing review and alignment accuracy evidence are missing. Phase 3 now implements evidence-gated comparison, temporal detectors, rubric scoring, review imports and evaluation tooling. Independent real detection accuracy remains unmeasured; there is no frontend.

Development must preserve the Track C requirements for contrastive datasets, forced alignment, acoustic feature extraction, temporal grounding, explainable rubric-based scoring, reproducibility, a dashboard and deliverables.

## Phase 0 documentation

- [Requirements matrix and official judging weights](docs/requirements-matrix.md)
- [Architecture, API contracts and recording-to-report workflow](docs/architecture.md)
- [Dataset acquisition, annotations and evaluation splits](docs/dataset-plan.md)
- [Scoring formulas, uncertainty and evaluation methodology](docs/scoring-policy.md)
- [Design system and accessibility](docs/design-system.md)
- [Implementation phases, evidence gates and next step](docs/implementation-roadmap.md)
- [Risks, mitigations and blockers](docs/risk-register.md)

Selected design: local Python/FastAPI processing, NumPy/SciPy/librosa/soundfile, CPU forced alignment with MFA, SQLite and managed audio storage, and React/TypeScript/Vite. Phase 1 uses manifests instead of a database; its Python dependencies are pinned and locked. scikit-learn is present only as a librosa transitive dependency, with no learned scoring or training. The application service/UI remain future work; Phase 2 records the reviewed MFA model/dictionary licenses.

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

Next, close the human pilot/review gates and independently evaluate alignment/detection. Phase 4 will expose the real typed contracts through the local service and React workspace, preserving Workshop + Gridline + Studio Utility. No Phase 4 implementation belongs in this run. The public paired dataset, dashboard, maximum six-page technical report and 3-10 minute YouTube demonstration remain future deliverables.

## AI assistance

Codex assisted with the product rename, specification review, Phase 0 technical planning and Phase 1, Phase 2 and Phase 3 implementation/tests, rights-source research and actual CPU runs. Generated signal fixtures verify software behavior and are not the competition dataset. Rubric selections remain proposals awaiting real held-out evaluation. AI assistance must continue to be disclosed honestly as the project develops.
