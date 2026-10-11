# TakeTwo

Speech analysis workspace

TakeTwo is a professional speech-analysis workstation for comparing reference and participant recordings of the same transcript, inspecting temporally grounded acoustic evidence, and scoring delivery with an explainable rubric.

The interface follows the Workshop + Gridline + Studio Utility design language. Engineering, design and scientific integrity standards are defined in [AGENTS.md](AGENTS.md).

## Project status

Phase 0 defines the architecture and execution plan derived from all three pages of the official [Track C specification](requirments/Track%20C.pdf). Phase 1 implements a local, tested dataset-engineering CLI for audio import, provenance, controlled synthetic edits, annotations, leakage-resistant splits, validation and export. The real competition dataset and independently reviewed pilot have not been acquired. There is no frontend, forced aligner, model training or speech-scoring engine yet.

Development must preserve the Track C requirements for contrastive datasets, forced alignment, acoustic feature extraction, temporal grounding, explainable rubric-based scoring, reproducibility, a dashboard and deliverables.

## Phase 0 documentation

- [Requirements matrix and official judging weights](docs/requirements-matrix.md)
- [Architecture, API contracts and recording-to-report workflow](docs/architecture.md)
- [Dataset acquisition, annotations and evaluation splits](docs/dataset-plan.md)
- [Scoring formulas, uncertainty and evaluation methodology](docs/scoring-policy.md)
- [Design system and accessibility](docs/design-system.md)
- [Implementation phases, evidence gates and next step](docs/implementation-roadmap.md)
- [Risks, mitigations and blockers](docs/risk-register.md)

Selected design: local Python/FastAPI processing, NumPy/SciPy/librosa/soundfile, CPU forced alignment with MFA, SQLite and managed audio storage, and React/TypeScript/Vite. Phase 1 uses manifests instead of a database; its Python dependencies are pinned and locked. scikit-learn is present only as a librosa transitive dependency, with no learned scoring or training. The remaining application stack and model licenses are future gates.

## Dataset tools

```powershell
uv sync --locked
uv run taketwo-dataset --help
uv run pytest -q
uv run ruff check src tests
```

Use Python 3.11. Read the [dataset-engineering guide](docs/dataset-engineering.md) for schema, PowerShell commands, annotation workflow and release checks, and the [dependency inventory](docs/dependencies.md) for purpose/license notes. [Phase 1 validation evidence](docs/phase1-validation.md) separates software tests from actual dataset readiness. Keep local recordings under ignored `local-data/` or outside the checkout.

Next, acquire and independently review the rights-cleared pilot. Phase 2 should then implement the locked native Windows MFA alignment pipeline against that pilot. The public dataset, functional dashboard, maximum six-page technical report and 3-10 minute YouTube demonstration remain future deliverables; no placeholder release links or analysis results are provided.

## AI assistance

Codex assisted with the product rename, specification review, Phase 0 technical planning and Phase 1 implementation/tests. Generated signal fixtures verify software behavior and are not the competition dataset. Rubric selections remain proposals awaiting real held-out evaluation. AI assistance must continue to be disclosed honestly as the project develops.
