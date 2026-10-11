# Phase 1 validation evidence

Executed on 2026-10-11 from baseline `b8438eb`, using native Windows PowerShell, CPython 3.11.9 and the locked uv environment. Phase 1 dataset software is implemented. The original real-data pilot gate remains **blocked/incomplete**: no rights-cleared competition reference or consented human mirror was acquired, no independent transcript/interval review was performed and nothing was published. Phase 2 has not started.

## Automated and repository checks

| Check actually executed | Result |
| --- | --- |
| `uv sync --locked` and `uv lock --check` | Succeeded; 38 resolved/installed packages including TakeTwo, development tools and transitive dependencies |
| `uv run pytest -q` (final run) | **114 passed**, zero failed/skipped, 74.87 seconds |
| `uv run ruff check src tests` | Passed |
| `uv run ruff format --check src tests` | Passed; 17 Python files already formatted |
| `uv build --no-sources` | Source distribution and wheel built successfully |
| Wheel archive inspection | Dataset CLI present, no WAV/FLAC recording assets included; audio module matches final source |
| JSON Schema/runtime comparison | Checked-in schema equals `Dataset.model_json_schema()` |
| PDF checksum | Original SHA-256 remains `0e621d35e6bfdbb9d9e169b259ebf9d3d923d1efcbab38ba2a4331f6958fb280` |

Tests cover valid WAV/FLAC decoding, unsupported limits, damaged headers/FLAC, nonfinite/silent/clipped signals, timing/amplitude preservation, stereo cancellation/channel selection, exact-content duplicates across containers, transformation determinism and tempo/pitch fixtures, sample-time mapping, combined recipes, generated-vs-human labels, provenance/schema errors, annotation bounds/history, processing/version metadata, altered/missing artifacts, family/work/transcript/source/speaker leakage, frozen split inheritance, structured CLI failures, exclusive locks, symlinks/reparse points, Windows path aliases, export overwrite prevention, disk-failure rollback and repeat-build artifacts. Generated signals and test-only reviewer/consent markers are software fixtures, not evidence about human speech or actual permissions.

Regression discovery: libsndfile's float-WAV PEAK chunk includes a volatile timestamp. Canonical derivatives now use a minimal deterministic IEEE float WAV/fact header; a delayed repeat-build test checks both file bytes and semantic manifests. A cross-container duplicate test also confirmed independently quantizing the same floating input can change PCM samples; the exact-content test now transcodes the same decoded PCM, and near-duplicate discovery remains a documented human QA task.

## Actual PowerShell CLI smoke run

All nine CLI commands were exercised using local generated WAV/FLAC fixtures in a temporary workspace, outside the competition corpus. `schema` and negative CLI paths were also exercised through subprocess tests.

| Operation | Observed result |
| --- | --- |
| `init --version smoke-v1` | Exit 0; empty versioned workspace |
| `import-reference` | Exit 0; immutable original and canonical derivative |
| `import-flawed` | Exit 0; explicit test mirror relationship, identity needs review |
| `split --seed 17` | Exit 0; one connected group, all members in train; insufficient-group warnings preserved |
| `generate --recipe` after splitting | Exit 0; combined pause insertion and faster tempo; derivative inherits the parent's frozen split |
| `annotate --annotations` | Exit 0; one unreviewed manual import label retained, no invented reviewer |
| `validate --reproduce` | Exit 0; 3 recordings, 2 pairs, 3 unreviewed annotations; zero errors, 7 provenance/review warnings |
| `export --output` | Exit 0; manifest and actual inventory summary, no audio publication |
| `validate --publication --reproduce` | Exit 1 as expected; 13 errors for absent rights/reviews/corpus/split coverage |

The smoke mirror and manual annotation exercise those import pathways using test-only signals. They are not real human recordings or independently reviewed flaw regions. Pending rights and unverified transcripts were deliberately retained; the publication gate correctly refused the fixture workspace.

## Reproducibility evidence

Rebuilt the complete smoke workspace independently from the same original files, import metadata, recipe and split seed, including the manual annotation. Compared assembled JSONL bytes and every normalized artifact: **identical**.

- Semantic manifest SHA-256: `829a962e35919d7c8028e6eefec6e8436ced3074529b1bb2ac321ff593618df1`.
- Generated derivative SHA-256: `efff82106a64d1905a6c0ecae0c982f359f1f462177d08c248cb187bc660ecee`.
- Measured derivative duration: 1.8666875 seconds from a two-second signal after a 0.2-second pause insertion and 1.5x tempo on a one-second region, with sample rounding recorded by the time map.

These hashes identify local software-test artifacts, not a released dataset. Same-platform evidence does not establish cross-platform equivalence. Replay uses absolute sample tolerance `1e-6`; second-environment checks, genuine speech perceptual review and target-hardware resource benchmarks remain pending.

## Remaining gates and next scope

Acquire two documented real public-speech references, clear adaptation/public release rights, independently verify transcripts, recruit consented split-disjoint mirror speakers and annotate near-perfect/severe human deliveries. A candidate archive was researched, but no rights clearance, download, reviewer approval or dataset completion is claimed.

After that pilot and a separate instruction, Phase 2 should install/lock a compatible native Windows CPU MFA environment and licensed English model/dictionary, implement transcript/OOV preflight and bounded CLI execution, produce validated word/phone intervals, preserve failed attempts and compare boundaries with independently timed audio. No dashboard, feature-scoring engine or model training belongs in that step.

## Later continuation

The evidence above is historical to Phase 1. Phase 1B/2 development from `cb0dbd7` is recorded in [Phase 2 validation](phase2-validation.md); its authorized scope includes acoustic extraction alongside alignment despite the earlier roadmap numbering. The original 114 tests are preserved.
