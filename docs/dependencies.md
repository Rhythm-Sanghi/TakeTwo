# Phase 1 dependency inventory

`pyproject.toml` pins direct versions and `uv.lock` locks the full transitive resolution and wheel hashes. Tested interpreter: CPython 3.11.9, native Windows. Python 3.11 is currently the supported minor version. Install with `uv sync --locked`; do not update the lock as part of a normal dataset build.

| Direct dependency | Version | Purpose | Package license |
| --- | --- | --- | --- |
| NumPy | 2.2.6 | Sample arrays, hashes and numerical operations | BSD-3-Clause; distribution includes additional notices |
| SciPy | 1.15.3 | Polyphase sample-rate conversion | BSD-3-Clause; bundled numerical libraries carry notices |
| soundfile | 0.13.1 | WAV/FLAC decoding and metadata | BSD-3-Clause; bundled libsndfile has separate LGPL terms |
| Pydantic | 2.11.7 | Strict manifest/metadata validation and JSON Schema | MIT |
| librosa | 0.11.0 | CPU phase-vocoder tempo and local pitch edits | ISC |
| pytest (development) | 8.4.1 | Automated verification | MIT |
| Ruff (development) | 0.12.5 | Lint and format checks | MIT |
| Hatchling (build) | 1.27.0 | Build/install the Python package and CLI | MIT |

Installed package metadata/license notices were inspected for the direct runtime packages and key transitive native/audio packages. soundfile used libsndfile 1.2.2 in this run. Librosa transitively installs Numba/llvmlite, scikit-learn and soxr; these are processing dependencies, not an added training pipeline. Installed soxr declares LGPL-2.1-or-later; bundled libsndfile, libsoxr, LLVM and BLAS components require preserving their upstream notices and applicable redistribution terms when packaging a binary distribution. This table is not a complete binary-redistribution legal audit. Resolve that gate before distributing a bundled app; using a local locked environment does not grant rights to dataset audio.

No FastAPI, GPU framework, aligner/model, frontend, cloud or database dependency is installed for Phase 1. Internet is needed to install dependencies; dataset operations use local files and do not contact external services or download models/audio.
