# TakeTwo

**Compare speech. Understand the difference.**

Speech analysis workspace

TakeTwo is a local Windows workstation for comparing two recordings of the same words. It connects acoustic and timing differences to native audio intervals, so you can listen, inspect the evidence and understand what changed.

## Demonstration

**Watch the demonstration:** [TakeTwo — Speech Analysis Demo](https://youtu.be/DfFTmNTAB6E)

The 6:23 video opens and plays while signed out; its description links to this repository. Sampled footage shows TakeTwo. This access check does not establish scientific accuracy or recording redistribution rights.

![TakeTwo exploratory speech analysis](docs/images/taketwo-exploratory-software.png)

Actual application screenshot using generated software signals to exercise the interface. Private speech recordings and screenshots are excluded from Git.

## Features

- Import WAV/FLAC recordings and transcripts with retained originals and provenance.
- Inspect duration, digital level, energy, activity and supported pitch.
- Compare grouped observations, provisional word timing and alignment anomalies.
- Replay reference and participant intervals on their own native timelines with A/B controls.
- Export concise Analysis Summaries, searchable Full Evidence Reports and JSON/CSV.
- Collect independent transcript/timing/flaw reviews and inspect dataset/evaluation prerequisites.

## Technology

Python 3.11, FastAPI, React, TypeScript, SQLite, librosa, NumPy, SciPy, soundfile, uPlot and CPU Montreal Forced Aligner/Kaldi. Serial supervised workers provide cancellation, timeouts, crash containment and integrity-checked caches. No GPU, cloud account or paid inference API is required.

## Getting started

Install Windows 11, Python **3.11**, **uv**, Git and Node.js **24** with npm. From PowerShell:

```powershell
git clone https://github.com/Rhythm-Sanghi/TakeTwo.git
cd TakeTwo
.\scripts\start-local.ps1 -Setup
```

Open [the workspace](http://127.0.0.1:8765). Stop with **Ctrl+C**. Next time, run `.\scripts\start-local.ps1` without `-Setup`. Use `-Port 8876` if the default port is occupied. First-time downloads can take several minutes.

[Windows setup and recovery](docs/windows-setup.md) covers prerequisites and manual commands. The default workspace is `%LOCALAPPDATA%\TakeTwo\workspace`; `-Workspace .\local-data\practice` selects a separate private workspace. No human corpus is bundled.

Import, acoustic inspection and playback work before MFA is configured. For word alignment, follow the separate [locked MFA/model setup](docs/analysis-engine.md#native-windows-mfa-setup), then launch:

```powershell
.\scripts\start-local.ps1 -AlignmentConfig .\local-data\alignment-config.json
```

MFA resources are installed separately, not downloaded by analysis requests. Analysis supports **45 seconds per recording** by default; imports support **100 MiB / 600 seconds**. Longer originals remain playable and can be explicitly excerpted. The Python wheel supplies the API/CLI; the frontend must be built from the checkout.

## How it works

1. Import a permitted reference recording with its actual spoken words.
2. Add a participant take with the intended same-text relationship and run analysis.
3. Inspect measured differences, provisional alignment and highlighted intervals; alternate native A/B playback.
4. Export a summary or complete evidence report. Use independent human reviews before requesting verified assessments or evaluation.

Supplied transcripts and automatic timestamps remain unverified. Read the [user guide](docs/user-guide.md), [comparison methods](docs/comparative-insights.md) and [review workflow](docs/reviewed-evidence-workflow.md) for details.

## Reports and reproducibility

Read the [six-page technical report](output/pdf/taketwo-technical-report-2026-10-15.pdf) or its [editable source](docs/technical-report.md). [Architecture](docs/architecture.md), [scoring formulas](docs/scoring-policy.md) and [reproduction commands](docs/reproducibility.md) describe the pipeline and evidence contracts. [Report exports](docs/report-export-guide.md) explains searchable PDF generation.

Python/npm/native resources are locked. Reports bind input, transcript, configuration, model, implementation and review hashes. [Browser tests](docs/browser-testing.md) distinguish software fixtures from genuine private inputs. Public release `faebbc9` passed its [Windows CI run](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38617800894). New cleanup commits require their own CI. Current submission links are in [submission readiness](docs/publication-readiness.md).

```powershell
uv run pytest -q
npm --prefix frontend test -- --maxWorkers=1
npm --prefix frontend run typecheck
npm --prefix frontend run build
uv run python scripts/check_repository.py
```

## Limitations

TakeTwo is a working research prototype. Delivery-v0 remains uncalibrated; independent speech annotations, held-out accuracy and cross-speaker generalization are unavailable. Automatic alignment can fit incorrect words. Pitch coverage was insufficient on the private practice takes, so affected scores abstain. Human listening, spoken accessibility and clean second-machine acceptance remain pending; cold evidence requests can time out under contention.

**The required public paired dataset is not yet available.** Five private practice takes are not redistribution-approved ground truth. See [dataset publication requirements](docs/dataset-publication.md). Acoustic differences do not establish persuasion, emotion or a psychological cause.

## Creator

**Created by Rhythm Sanghi**

I developed TakeTwo around a question I wanted to explore: how can we compare two speech recordings and understand the differences without relying on an unexplained score? I defined the product direction and use cases, shaped the visual identity and workflows, made scope decisions, supplied practice recordings and intended transcripts, reviewed analysis results and reports, and guided improvements and submission preparation.

## AI assistance

OpenAI Codex assisted with software implementation, integration, testing and documentation. ChatGPT supported planning, technical review and development guidance. The project direction, product decisions, practice recordings, review of results and submission decisions were directed by Rhythm Sanghi. Both tools are included in the [Devpost Built With checklist](docs/submission-draft.md).

## License

Original code and documentation use the [MIT License](LICENSE), copyright (c) 2026 Rhythm Sanghi. Recordings, consent/review records, models and third-party materials retain separate rights. [Licenses and attribution](docs/attributions.md).
