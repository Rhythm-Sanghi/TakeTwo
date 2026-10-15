# TakeTwo

Speech analysis workspace

**Compare speech. Understand the difference.**

TakeTwo is a local Windows workstation for comparing recordings of the same words. It connects acoustic and timing differences to each recording's native audio intervals, with evidence inspection, A/B playback and exports.

[Watch the demonstration](https://youtu.be/DfFTmNTAB6E) · [Technical report](output/pdf/taketwo-technical-report-2026-10-15.pdf)

![TakeTwo speech analysis workspace](docs/images/taketwo-exploratory-software.png)

Actual application screenshot using generated software signals. Private speech recordings are excluded from the repository.

## Features

- Import WAV/FLAC recordings and transcripts, preserving originals and provenance.
- Inspect duration, digital level, energy, activity and supported pitch.
- Compare grouped acoustic observations, provisional word timing and alignment anomalies.
- Replay reference and participant intervals on independent native timelines.
- Export Analysis Summaries, searchable Full Evidence Reports and JSON/CSV.
- Collect independent transcript, timing and flaw reviews; inspect dataset and evaluation prerequisites.

## Technology

Python 3.11, FastAPI, SQLite, React, TypeScript, Vite, uPlot, librosa, NumPy, SciPy, soundfile and CPU Montreal Forced Aligner/Kaldi. Supervised serial workers provide cancellation, timeouts and integrity-checked caching. No GPU, cloud account or paid inference API is required.

## Installation

Install Windows 11, Python **3.11**, **uv**, Git and Node.js **24** with npm. In PowerShell:

```powershell
git clone https://github.com/Rhythm-Sanghi/TakeTwo.git
cd TakeTwo
.\scripts\start-local.ps1 -Setup
```

Open [the workspace](http://127.0.0.1:8765). Stop with **Ctrl+C**. Next time, run `.\scripts\start-local.ps1`. Use `-Port 8876` if the default port is occupied. First-time downloads can take several minutes.

The default private workspace is `%LOCALAPPDATA%\TakeTwo\workspace`; `-Workspace .\local-data\practice` selects another. [Windows setup and troubleshooting](docs/windows-setup.md) provides prerequisites and manual commands.

Import, acoustic inspection and playback work before MFA is configured. Word alignment requires the separate [locked MFA/model setup](docs/analysis-engine.md#native-windows-mfa-setup), then:

```powershell
.\scripts\start-local.ps1 -AlignmentConfig .\local-data\alignment-config.json
```

Analysis supports **45 seconds per recording** by default; import supports **100 MiB / 600 seconds**. Longer originals remain playable and support explicit excerpts. No human corpus or model files are bundled. The Python wheel supplies API/CLI; build the frontend from the checkout.

## How to use

1. Import a permitted reference with its actual spoken words.
2. Add a participant take with the intended same-text relationship and run analysis.
3. Inspect measured differences and highlighted intervals; alternate native A/B playback.
4. Export a summary or complete evidence report. Complete independent reviews before requesting verified assessments or evaluation.

Supplied text and automatic timestamps remain unverified. The [user guide](docs/user-guide.md) covers import, pairing, analysis, playback and export; the [review workflow](docs/review-protocol.md#transcript-timing-flaw-review-and-scientific-eligibility) covers independent evidence.

## Technical report and documentation

The current six-page report is linked above; its [editable source](docs/technical-report.md) retains the dated submission evidence. See [architecture](docs/architecture.md) for component boundaries and method references, [reproducibility](docs/reproducibility.md) for verification commands, and [submission](docs/submission.md) for current deliverables and remaining owner actions.

## Scientific limitations

TakeTwo is a research prototype. Delivery-v0 is uncalibrated; independent speech annotations, held-out accuracy and cross-speaker generalization are unavailable. Automatic alignment can fit incorrect words. Pitch support was insufficient on the private practice takes, so affected scores abstain. Cold evidence requests can time out under contention. Human listening, spoken accessibility and clean second-machine acceptance remain pending.

**The required public paired dataset is not available.** Five private practice takes are not redistribution-approved ground truth. Acoustic differences do not establish persuasion, emotion or psychological causes.

## Creator and AI assistance

**Created by Rhythm Sanghi**, who directed the product, interface and workflows, supplied practice recordings and intended transcripts, reviewed results and guided submission preparation.

OpenAI Codex assisted implementation, integration, testing and documentation. ChatGPT assisted planning and technical review. Both tools are disclosed in the [submission checklist](docs/submission.md#devpost-fields).

## License

Original code and documentation: [MIT](LICENSE), copyright (c) 2026 Rhythm Sanghi. Recordings, consent/review records, models and third-party materials retain separate rights. See [licenses and attribution](docs/attributions.md).
