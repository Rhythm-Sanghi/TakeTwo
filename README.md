# TakeTwo

Speech analysis workspace

TakeTwo compares reference and participant recordings of the same words, preserves native audio timing, and exposes measured acoustic evidence and an explainable delivery-agreement rubric. The Workshop + Gridline + Studio Utility interface uses restrained surfaces, precise grids, functional controls and explicit unavailable states. Permanent standards are in [AGENTS.md](AGENTS.md).

## Quick start on Windows

Requires Windows 11, Python 3.11 with uv, and Node.js 24/npm. From the repository root in PowerShell, install/build once:

```powershell
.\scripts\start-local.ps1 -Setup
```

Normal startup reuses installed dependencies and the built interface:

```powershell
.\scripts\start-local.ps1
```

Open `http://127.0.0.1:8765`. Stop with Ctrl+C. The default workspace is `%LOCALAPPDATA%/TakeTwo/workspace`; no recordings are seeded. Use `-Workspace .\local-data\practice-v2` for a separate private practice workspace or `-Port 8876` if another service owns the default port. Setup does not install MFA automatically. Missing prerequisites/builds and port conflicts have explicit messages. See [Windows setup](docs/windows-setup.md) for installation and manual commands.

For native CPU alignment, install the locked MFA environment and checksummed English US ARPA model/dictionary using [alignment setup](docs/analysis-engine.md). Then launch with `-AlignmentConfig .\local-data\alignment-config.json` or set `TAKETWO_ALIGNMENT_CONFIG`. Without configured resources, actual acoustic inspection works with alignment/scoring abstention. No CUDA, cloud account or paid inference API is required.

## First recording to report

1. In **Recording Library**, choose a public-source reference or a self-recorded controlled practice reference, select WAV/FLAC, and supply the actual spoken words.
2. Confirm local processing permission. Advanced source, speaker, rights and channel information stays available in disclosures; unknown rights are not filled with invented values.
3. Click **Add participant**, choose a separate take and confirm the intended same-text relationship. The app creates and selects its pair; text remains unverified.
4. Open **Analysis Workspace** and run analysis. Read the processing and assessment states first, then findings and the next required action. Listen to either native track and explore the supporting evidence.
5. Open **Technical details · scores, coverage and scientific exports** for the validated JSON/CSV report. Independent reviews are required for eligible scores; successful processing alone is not scientific validation.

Use **Review Workspace** for browser transcript checks, assisted word/phrase timing, blinded flaw annotation, saved drafts and immutable review exports. A local operator key controls sequential reviewer handoff and separate adjudication; general analysis/peer APIs close during handoff. Read [review workflow and privacy limits](docs/review-workspace.md) before assigning independent reviewers. Typed identities and playback events do not authenticate people or establish scientific eligibility. [Review implementation evidence](docs/review-workspace-validation.md) lists actual checks and outstanding human acceptance.

WAV/FLAC storage supports 100 MiB/600 s; analysis supports up to 45 s per member by default. Longer originals remain playable. Explicit selection-to-excerpt saving preserves originals and requires the exact excerpt text; each take has its own cut times. Read the concise [recording guide and five-WAV pilot steps](docs/recording-import-guide.md).

## Implemented scope and current status

Dataset ingestion/provenance, canonical audio/text, contrastive pairing, controlled transformations/time maps, connected-group splits, CPU MFA, FFT/MFCC/RMS/energy/pYIN extraction, reviewed correspondence, explainable detection/scoring, independent-label evaluation, SQLite history and the five-area web workspace are implemented. Supervised serial workers provide cancellation, timeout, Windows crash containment/recovery, exact-request retry, bounded memory and integrity-checked caches.

Product stabilization repairs recording-type selection, controlled references, progressive import, pair selection/correction, explicit metadata migration, reviewer-file handoff, excerpt recovery, history timestamps and bound-report persistence. [Issue inventory](docs/product-audit.md) and [executed verification](docs/product-validation.md) distinguish repaired software from remaining acceptance gates.

The user supplied five genuine private practice WAV takes and their intended transcript, all by one person. They are controlled local recordings, not public-speaker references, independently reviewed labels or a releasable corpus. Two previously acquired JFK masters and one draft archive excerpt remain documented separately. Independent transcript/timing/flaw reviews, public consent, calibration, real detection accuracy and held-out validation remain open. Prior [Phase 4B](docs/phase4b-validation.md) and [Phase 5](docs/phase5-validation.md) reports are historical evidence, including the absence of these newly supplied takes at that time.

## Architecture and engineering guides

Python 3.11/FastAPI/Uvicorn/Pydantic; NumPy/SciPy/librosa/soundfile; isolated CPU MFA/Kaldi; SQLite lifecycle history; immutable managed audio/JSON artifacts; React/strict TypeScript/Vite/uPlot. Python/npm/native environment/model resources are locked. scikit-learn is transitive through librosa; no classifier is trained. No broker, ORM, GPU framework or new runtime dependency is required.

- [Architecture and workflow](docs/architecture.md), [backend API](docs/backend-api.md), [frontend interaction guide](docs/frontend-workspace.md)
- [Dataset tools](docs/dataset-engineering.md), [dataset plan](docs/dataset-plan.md), [current schema v2](docs/dataset-schema-v2.json), [preserved legacy schema v1](docs/dataset-schema-v1.json)
- [Analysis engine](docs/analysis-engine.md), [comparison/review/evaluation CLI](docs/comparison-engine.md), [scoring formulas](docs/scoring-policy.md)
- [Design system](docs/design-system.md), [requirements and official weights](docs/requirements-matrix.md), [roadmap](docs/implementation-roadmap.md), [risks](docs/risk-register.md)
- [Source acquisition](docs/pilot-collection.md), [human review kit](docs/human-pilot-kit.md), [annotation worksheet](docs/annotation-worksheet.md), [Review Workspace](docs/review-workspace.md)
- [Dependency purpose/licenses](docs/dependencies.md), [reproduction commands](docs/reproducibility.md)

## Verification

```powershell
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
uv run pytest -q
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run test
npm --prefix frontend run build
uv run python scripts/make_browser_fixtures.py
npm --prefix frontend exec -- playwright install chromium
npm --prefix frontend run e2e
uv run python scripts/check_repository.py
uv run python scripts/audit_release.py
```

The browser suite uses actual local HTTP/audio processing; generated tones are explicit software fixtures. Optional `TAKETWO_REAL_SMOKE=1` requires the documented local archival source/config; `TAKETWO_PILOT_SMOKE=1` requires the user's private five files. The processing/review integration tests use actual backend routes. A separate explicitly labeled UI-state test intercepts report responses to exercise loading, partial, eligible findings and eligible-zero presentation; it never changes stored scientific artifacts or establishes speech accuracy. See the validation report for checks actually run, failed attempts and environment-blocked tests.

## Limitations and submission materials

Acoustic agreement is not persuasion, emotion or speaking ability. `delivery-v0` remains experimental and uncalibrated. Scores/regions/confidence stay unavailable when rights, text, timing, quality, pitch or coverage gates fail; no weights are redistributed. Automatic alignment can fit wrong words. Cross-speaker generalization and clean second-environment reproduction are unmeasured. Windows is required for current web supervision. Automated accessibility checks do not establish spoken screen-reader compatibility or production readiness.

The [submission package](docs/submission-draft.md) includes [compliance](docs/submission-compliance.md), the [six-page historical report draft](output/pdf/taketwo-technical-report.pdf), its [archived source](docs/technical-report-2026-10-12.md), and the [current editable report](docs/technical-report.md), [demo script](docs/demo-script.md), [dataset publication guide](docs/dataset-publication.md), [attributions](docs/attributions.md) and [manual action list](docs/ACTION-REQUIRED.md). Report regeneration uses external ReportLab tools via `scripts/build_submission_report.py`, without adding application dependencies. Reconcile drafts with current evidence before release.

Public code is verified on `master` at `cd2abe9`: [Windows Actions run 38357432224 passed](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38357432224). The earlier failed build-order run remains historical evidence. The subsequent [stabilization audit](docs/stabilization-audit.md) corrects ground-truth selection and narrow-screen controls locally; these changes have not been pushed. Public paired dataset, final report approval, video and submission remain owner actions. Private audio, models, consent records, databases and runtime evidence stay outside releases.

See the [product experience audit](docs/product-experience-audit.md) for the outcome-first redesign, verified user journeys, screenshots, accessibility evidence and remaining human acceptance limits.

## AI assistance

OpenAI Codex was extensively used for implementation, testing, integration and documentation under human direction. ChatGPT assisted architecture planning, problem interpretation, technical review and development instructions. Human participants supplied the genuine private recordings. Generated signals verify software only. Human consent, transcript/timing/flaw review, scientific judgments and final publication remain separate. Detailed third-party notices and honest tool disclosure are in [attributions](docs/attributions.md).

The shared `TAKETWO_MAX_ANALYSIS_DURATION_S` setting accepts integer seconds 1–45, default 45. Restart after changing it. See [duration configuration and verification](docs/duration-validation.md).

## License and data rights

Original TakeTwo code and project documentation use the [MIT License](LICENSE), copyright (c) 2026 Rhythm Sanghi. Private recordings, datasets, consent/reviewer records, external model files and third-party materials retain separate rights. See [attributions](docs/attributions.md); this license grants no private-data publication permission.

Current verification and owner actions are in the [stabilization audit](docs/stabilization-audit.md). The [earlier repair audit](docs/final-repair-audit.md) preserves historical evidence. Windows CI is configured in `.github/workflows/ci.yml`; [CI and submission verification](docs/ci-submission-validation.md) distinguishes the successful public baseline from subsequent local work.

Portable generated browser tests and opt-in private fixture preparation are documented in [browser testing](docs/browser-testing.md). The [pitch investigation](docs/pitch-investigation.md) records measured abstention and controlled confidence probes without changing acoustic-v1 or delivery-v0.

See the [mobile refinement audit](docs/mobile-refinement-audit.md) for compact navigation, task-first layouts, persistent track selection and executed responsive/print verification.

See the [reference inspection and PDF repair audit](docs/reference-inspection-audit.md) for single-input states, report identity protection, searchable browser print output and verification evidence.
