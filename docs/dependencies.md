# TakeTwo dependency inventory

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

Phase 2 adds an isolated, explicitly locked MFA/model environment, documented in [analysis engine](analysis-engine.md); TakeTwo adds an explicit threadpoolctl pin/use; it was already installed transitively. Phase 4 adds the local service/frontend below; no GPU framework/cloud/broker/ORM is required. SQLite uses the Python standard library. Internet is needed to install dependencies; analysis/dataset operations use local files and do not download models/audio.

Phase 2 also uses existing NumPy/SciPy/librosa for spectra, MFCC and pYIN, and Pydantic for analysis contracts. Standard-library ctypes supplies the Windows benchmark memory sampler; no extra benchmark package was installed. Model files are about 91.9 MB and 7.2 MB and carry CC BY 4.0 separately from MFA MIT software. Preserve all environment package notices before any bundled distribution.

## Phase 4 additions

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

`frontend/package-lock.json` pins the full npm resolution/integrities. Runtime UI dependencies are only React, React DOM and uPlot; native HTML audio and a small measured-envelope canvas renderer avoid a second audio decoding/waveform dependency. No font CDN, UI framework, animation/icon library or remote inference client is added. The executed production bundle is recorded in [Phase 4 validation](phase4-validation.md), rather than estimating library marketing sizes.

Selection references: [FastAPI heavy-computation guidance](https://fastapi.tiangolo.com/tutorial/background-tasks/), [uPlot's upstream project](https://github.com/leeoniya/uPlot), [Vite's maintained tooling guide](https://vite.dev/guide/). Versions were resolved and exercised in the actual local environment. FastAPI's locked transitive Starlette is 1.7.0; Python's existing acoustic dependency pins are unchanged. Preserve transitive notices before any standalone redistribution; the current launcher runs a local installed environment, not a bundled binary installer.

Security maintenance (2026-10-13): python-multipart 0.0.31 addresses the upstream multipart header/preamble and parse-form advisories; pytest 9.0.3 addresses the tmpdir advisory. Acoustic dependencies and scientific policy are unchanged. See [multipart advisories](https://github.com/Kludex/python-multipart/security/advisories) and [pytest advisory](https://github.com/advisories/GHSA-6w46-j5rx-g56g).
