# TakeTwo

Speech analysis workspace

TakeTwo is a professional speech-analysis workstation for comparing reference and participant recordings of the same transcript, inspecting temporally grounded acoustic evidence, and scoring delivery with an explainable rubric.

The interface follows the Workshop + Gridline + Studio Utility design language. Engineering, design and scientific integrity standards are defined in [AGENTS.md](AGENTS.md).

## Project status

Phase 0 contains the architecture and execution plan derived from all three pages of the official [Track C specification](requirments/Track%20C.pdf). Application features, datasets, model downloads, package dependencies and automated application tests have not been implemented. All later-phase acceptance gates and performance targets remain unverified.

Development must preserve the Track C requirements for contrastive datasets, forced alignment, acoustic feature extraction, temporal grounding, explainable rubric-based scoring, reproducibility, a dashboard and deliverables.

## Phase 0 documentation

- [Requirements matrix and official judging weights](docs/requirements-matrix.md)
- [Architecture, API contracts and recording-to-report workflow](docs/architecture.md)
- [Dataset acquisition, annotations and evaluation splits](docs/dataset-plan.md)
- [Scoring formulas, uncertainty and evaluation methodology](docs/scoring-policy.md)
- [Design system and accessibility](docs/design-system.md)
- [Implementation phases, evidence gates and next step](docs/implementation-roadmap.md)
- [Risks, mitigations and blockers](docs/risk-register.md)

Selected design: local Python/FastAPI processing, NumPy/SciPy/librosa/soundfile, CPU forced alignment with MFA, SQLite and managed audio storage, and React/TypeScript/Vite. Dependencies and model licenses will be resolved and locked when implementation begins; scikit-learn is deferred until a concrete need exists.

The next step is Phase 1 dataset manifests, validation and a rights-cleared pilot. The public dataset, functional dashboard, maximum six-page technical report and 3-10 minute YouTube demonstration remain future deliverables; no placeholder release links or results are provided.

## AI assistance

Codex assisted with the product rename, specification review and Phase 0 technical planning. Stack and rubric selections are documented proposals, not empirical validation. AI assistance must continue to be disclosed honestly as the project develops.
