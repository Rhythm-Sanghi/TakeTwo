# Attribution and tool disclosure

TakeTwo — Speech analysis workspace. Preserve notices in their original distributions and the exact per-item permission records. Original TakeTwo source code and associated project documentation are licensed under the [MIT License](../LICENSE), copyright (c) 2026 Rhythm Sanghi, as selected by the owner. This grant does not cover private recordings, datasets, consent/reviewer records, externally licensed model or dictionary files, third-party software, or the official Track C specification. Those materials retain their own rights and attribution requirements. No permission to redistribute private data is implied.

## Acquired audio

John F. Kennedy; White House Audio Collection; John F. Kennedy Presidential Library and Museum. Item-specific evidence for `JFKWHA-001` (White House Army Signal Agency) and `JFKWHA-190-002` (White House Communications Agency) records public-domain status in the [acquisition ledger](pilot-collection.md). The inaugural master is the Wikimedia Commons copy. Preserve source URLs, access date, hashes and conversion/excerpt provenance. No acquired audio is included in Git or claimed publicly released. Both masters share a source speaker. Future recordings require their own rights/consent, terms and attribution.

## Alignment resources

Montreal Forced Aligner software: MIT. English (US) ARPA acoustic model and pronunciation dictionary release v3.0.0: CC BY 4.0, authors Michael McAuliffe and Morgan Sonderegger. Preserve model/dictionary cards and source acknowledgments, including Gorman, Howell and Wagner (2011), as recorded in [alignment setup](analysis-engine.md) and [model lock](../environments/mfa-models.json). Analysis uses an extracted PCM16 derivative and automatic word/phone alignment; manual reviews do not overwrite it. Model files are not redistributed here.

Kaldi/OpenFst/Pynini carry Apache-2.0 and other distribution notices as applicable. The full native environment has additional package terms; review them before bundling binaries. Lockfiles and installation instructions do not substitute for redistribution notices.

## Application dependencies

The dependency inventory below lists direct versions, purposes and licenses. NumPy/SciPy/soundfile use BSD licenses; librosa ISC; Pydantic/FastAPI/React/uPlot MIT; Uvicorn BSD-3-Clause; python-multipart Apache-2.0. Python SQLite is the standard-library integration. libsndfile/soxr and bundled native numerical components have additional terms/notices. Preserve full transitive package notices before bundled redistribution. No classifier is trained; scikit-learn is present transitively through librosa.

Report PDF generation uses ReportLab and pypdf from the external document-tool runtime. These are authoring/inspection tools, not application runtime dependencies; report source and regeneration instructions are retained. System fonts avoid a downloadable application font dependency.

## Creator and development tools

**Created by Rhythm Sanghi.** He directed TakeTwo: product direction/use cases, visual
identity, scope and workflow decisions, genuine practice recordings and intended
transcripts, review of analysis/report limitations, improvements and submission.
OpenAI Codex assisted software implementation, integration, testing and documentation.
ChatGPT supported planning, technical review and development guidance. Both tools
belong in Devpost's Built With list.

Generated signals are software fixtures, not human speech accuracy evidence. No
AI-generated consent, independent annotation or listening result is presented as real.
Human rights clearance, independent review, calibration and final submission remain
separate. Add any actual recording/editing tools to the final video/report disclosure.

## Dependency inventory

`pyproject.toml` pins direct versions and `uv.lock` locks the full transitive resolution and wheel hashes. Tested interpreter: CPython 3.11.9, native Windows. Python 3.11 is currently the supported minor version. Install with `uv sync --locked`; do not update the lock as part of a normal dataset build.

| Direct dependency | Version | Purpose | Package license |
| --- | --- | --- | --- |
| NumPy | 2.2.6 | Sample arrays, hashes and numerical operations | BSD-3-Clause; distribution includes additional notices |
| SciPy | 1.15.3 | Polyphase sample-rate conversion | BSD-3-Clause; bundled numerical libraries carry notices |
| soundfile | 0.13.1 | WAV/FLAC decoding and metadata | BSD-3-Clause; bundled libsndfile has separate LGPL terms |
| Pydantic | 2.11.7 | Strict manifest/metadata validation and JSON Schema | MIT |
| librosa | 0.11.0 | CPU phase-vocoder tempo and local pitch edits | ISC |
| threadpoolctl | 3.7.0 | Explicitly limit BLAS threads for reproducible MFCCs and bounded CPU use; already present transitively | BSD-3-Clause |
| pytest (development) | 9.0.3 | Automated verification | MIT |
| Ruff (development) | 0.12.5 | Lint and format checks | MIT |
| Hatchling (build) | 1.27.0 | Build/install the Python package and CLI | MIT |

Installed package metadata/license notices were inspected for the direct runtime packages and key transitive native/audio packages. soundfile used libsndfile 1.2.2 in this run. Librosa transitively installs Numba/llvmlite, scikit-learn and soxr; these are processing dependencies, not an added training pipeline. Installed soxr declares LGPL-2.1-or-later; bundled libsndfile, libsoxr, LLVM and BLAS components require preserving their upstream notices and applicable redistribution terms when packaging a binary distribution. This table is not a complete binary-redistribution legal audit. Resolve that gate before distributing a bundled app; using a local locked environment does not grant rights to dataset audio.

MFA/model resources use the separate locked environment in [analysis engine](analysis-engine.md). TakeTwo explicitly pins threadpoolctl, which is also transitive. The service/frontend inventory follows; no GPU framework/cloud/broker/ORM is required. SQLite uses the Python standard library. Internet is needed to install dependencies; analysis/dataset operations use local files and do not download models/audio.

The acoustic engine uses NumPy/SciPy/librosa for spectra, MFCC and pYIN, and Pydantic for analysis contracts. Standard-library ctypes supplies the Windows benchmark memory sampler; no extra benchmark package was installed. Model files are about 91.9 MB and 7.2 MB and carry CC BY 4.0 separately from MFA MIT software. Preserve all environment package notices before any bundled distribution.

### Service, frontend and development tools

| Dependency | Pinned version | Purpose / license |
| --- | --- | --- |
| FastAPI | 0.143.0 | Typed HTTP integration/OpenAPI; MIT |
| Uvicorn | 0.42.0 | Loopback ASGI server; BSD-3-Clause |
| python-multipart | 0.0.31 | Audio/JSON multipart import parsing; Apache-2.0 |
| httpx (development) | 0.28.1 | pytest ASGI HTTP client; BSD-3-Clause. Current Starlette warns that its TestClient is moving to httpx2; actual tests still pass |
| React / React DOM | 19.3.0 | Stateful local browser workspace; MIT |
| uPlot | 1.6.32 | Small maintained canvas time-series renderer with explicit null gaps/native axes; MIT |
| TypeScript / Vite / React plugin | 5.9.3 / 8.3.4 / 6.1.2 | Strict checks, local dev proxy and static production bundle; Apache-2.0 / MIT / MIT |
| openapi-typescript | 7.13.0 | Generate client types from actual Python schemas, avoiding duplicate scientific contracts; MIT |
| Vitest / jsdom / Testing Library | 5.0.3 / 30.1.2 / versions in npm lock | Component/DOM/interaction verification; MIT |
| Playwright / axe-core browser integration | 1.64.0 / 4.13.0 | Actual Chromium playback/upload/export and accessibility checks; Apache-2.0 / MPL-2.0 |
| ESLint / TypeScript ESLint / Prettier | Versions in npm lock | Lint/format maintainable source and generated contracts; MIT |

`frontend/package-lock.json` pins the full npm resolution/integrities. Runtime UI dependencies are only React, React DOM and uPlot; native HTML audio and a small measured-envelope canvas renderer avoid a second audio decoding/waveform dependency. No font CDN, UI framework, animation/icon library or remote inference client is added. Measured production bundle sizes and verification scope are recorded in [verification](verification.md).

Selection references: [FastAPI heavy-computation guidance](https://fastapi.tiangolo.com/tutorial/background-tasks/), [uPlot's upstream project](https://github.com/leeoniya/uPlot), [Vite's maintained tooling guide](https://vite.dev/guide/). Versions were resolved and exercised in the actual local environment. FastAPI's locked transitive Starlette is 1.7.0; Python's existing acoustic dependency pins are unchanged. Preserve transitive notices before any standalone redistribution; the current launcher runs a local installed environment, not a bundled binary installer.

Security maintenance (2026-10-13): python-multipart 0.0.31 addresses the upstream multipart header/preamble and parse-form advisories; pytest 9.0.3 addresses the tmpdir advisory. Acoustic dependencies and scientific policy are unchanged. See [multipart advisories](https://github.com/Kludex/python-multipart/security/advisories) and [pytest advisory](https://github.com/advisories/GHSA-6w46-j5rx-g56g).
