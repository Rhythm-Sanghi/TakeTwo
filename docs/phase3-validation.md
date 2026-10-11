# Phase 3 validation evidence

Executed on 2026-10-11 from `d1aa575`, native Windows 11 build 26220, Intel Core i7-1365U, approximately 16 GB RAM, CPython 3.11.9 and the existing locked CPU environment. TakeTwo — Speech analysis workspace. Phase 3 implements comparison/detection/scoring/review/evaluation tooling. **Independent real human-reviewed detection evaluation remains incomplete.** No frontend, service, database, new runtime dependency, model download, remote branch or push belongs to this work.

## Implemented boundary

The seven cohesive modules in `src/taketwo/comparison/` define typed contracts, centralized eligibility, review validation/consensus, native-time comparison and detectors, scoring/templates, matching/evaluation, immutable storage and CLI operations (contracts/eligibility/reviews/engine/evaluation/storage/cli). The package initializer contains no application scaffold. Current [technical guide](comparison-engine.md) and [schema](comparison-schema-v1.json) document the executable boundary for Phase 4.

Actual categories: pacing, pause behavior, energy variation and pitch dynamics. Rubric detections cover phrase rate/excursion and aligned pause excess/omission. Additional evidence-only detectors cover sustained word-level energy differences, adjacent-word energy steps and reliable word-level pitch contours. They do not add penalties to the original range rubric. Detector resolution is word/phrase/gap, not independently measured frame-exact human flaw onset.

The four original equal weights, deviations, tolerances, saturation widths, reference-duration/gap weighting, 80% score coverage, two-phrase/five-gap minima and all-four overall gate are implemented. `delivery-v0` remains uncalibrated. Missing evidence never receives a zero penalty or redistributed weight. A fixed 1e-12 numerical epsilon stabilizes arithmetic equality at thresholds; full measured deltas remain available. The [scoring notes](scoring-policy.md) explain the smallest clarifications, evidence-only additions and engineering severity bins.

Dataset schema v1, Phase 2 schema/code, original tests, AGENTS.md, audio and official PDF remain unchanged. Comparison source has a separate digest; cached Phase 2 implementation digest remains `4007b3faa56ff95771eace60f501820c9567720b77172afac13e3d49dfc672f0`. Current comparison digest: `74ab0877f26480a936da95927d9876e7a377cdebf5d0597d1b20eb829b4b5a90` (exact working source bytes). Changing a policy/configuration or upstream input changes report identity; replay rejects source/dataset/upstream drift without rerunning MFA.

## Checks actually executed

| Check | Evidence |
| --- | --- |
| Earlier complete regression run | 196 passed, zero failed/skipped, 165.05 s; before the final exact-threshold regression |
| Final `uv run pytest -q` | **197 passed**, zero failed/skipped, **203.40 s**; all 155 original tests plus 42 Phase 3 tests |
| `uv run ruff check src tests scripts` / `ruff format --check src tests scripts` | Passed; 36 Python files already formatted |
| `uv lock --check` | Passed; 38 packages, dependencies unchanged |
| `uv build --no-sources` | Wheel and sdist built; final source/package inclusion inspected |
| Wheel inspection | All three CLI entry points present, comparison engine included, no audio/model assets |
| `uv run python scripts/check_repository.py` | Passed: 17 Markdown documents, 79 local links, three runtime-equivalent schemas, branding/fences/official weights and unchanged PDF checksum |
| Real CLI comparison/detection/scoring/evidence | Each returned expected exit 3 and the identical abstention artifact |
| Real CLI validate with replay / inspect / export | Each returned exit 0; no MFA or feature extraction invoked |
| Real CLI evaluate with no pair reports | Exit 3; null metrics and explicit missing-report/split reasons |

Phase 3 tests use analytic frame arrays to isolate hand calculations and generated signals to exercise the actual import/extraction/review/comparison/evaluation CLI. Reviewer, consent and rights assertions in tests are explicitly test-only. No actual human review is claimed. Tests cover known tempo ratios and pause durations, missing-pause anchors, energy-range/contour separation, pitch range/availability/confidence, per-feature abstention, clipping, transcript/alignment/rights/pair failures, frame support/units/clocks, exact-threshold roundoff, score determinism, coverage without reweighting, policy/config identity, review bounds/disagreement/history/blinding/corrections, unsupported categories, one-to-one overlap/event matching, severity bins, FP/FN inspection, split/calibration leakage, synthetic-origin/recipe isolation, ground-truth rejection by detectors, artifact hashes/schema, CLI failures/export protection and a fully eligible generated-signal CLI/replay workflow. Original Phase 1/2 regressions remain in the suite.

An implementation review identified a possible benchmark-helper deadlock on large pipe output. File-backed capture now prevents that failure; the helper still defaults to the original Phase 2 module and additionally accepts the comparison module. This does not alter Phase 2 extraction or alignment.

## Genuine recording findings

Used the existing rights-documented, unpublished 17.3 s JFK inaugural salutation in `local-data/pilot-v2`, recording `r-478a9405c1b10a75fda31972`. This is a real source candidate, not a human mirror or synthetic speech. Acquisition/provenance and remaining listening requirements are in [pilot collection](pilot-collection.md). Canonical audio SHA-256 remains `a342f051ea3b4ae23a40d293264bdee3946be235cb73c77e7e582c65dc873bc8`.

The new pipeline read and validated the saved Phase 2 feature payload `690c8285c5e6b421f4bbdb92a977c8fcb3557b56ced3c0d6bcb15021ef36111a` and alignment payload `3fbaaa23e370a9d242c3b9384a8f3d080dd88ce9841efad8c934fae28ddbdc7d`. No new alignment/model invocation was made. Actual inspection summaries retain 276,800 samples, 1,728 spectral frames, RMS 0.0772197731 full scale, peak 0.6856004596, clipping fraction 0, energy baseline -34.46671585 dBFS and pitch-valid fraction 0. These are acoustic measurements, not public-speaking quality results.

The draft transcript is unverified, independently checked word/phrase boundaries are absent, a participant mirror/pair is absent and pitch has no accepted frames. Eligibility is INELIGIBLE for comparison, with `pair_missing`, `transcript_unverified`, `timing_review_required` and pitch-specific `pitch_unreliable` reasons. All four scores and overall score are null; no deviation observations/regions are emitted. Zero regions here means **comparison unavailable**, not a perfect performance. No gates were bypassed and no human approvals were imported for this recording.

Actual `compare`, `detect`, `score` and `evidence` calls reused the same report payload SHA-256 `5e231e335a892268215942dd3e45b8c0c20d80be1ddd2e422800739cb5cd177a`. `validate --reproduce` rebuilt it identically from cached inputs/policy, followed by successful inspection and fresh JSON export. Evaluation with no pair reports correctly withheld metrics. Local command logs, report/export and benchmark remain ignored under `local-data/acquisition/` and `local-data/pilot-v2/`; they are not published dataset artifacts.

## Windows CPU measurement

Serial actual `evidence` CLI, including imports, dataset/audio integrity checks, cached JSON validation, eligibility and report publication: **7.220 s**, sampled peak process-tree working set **182,534,144 bytes (174.08 MiB)**, expected scientific-abstention exit 3. The helper samples every 100 ms; this is a sampled lower bound, can count shared pages and is not guaranteed true peak memory. Python's platform string reports Windows-10-10.0.26220-SP0 for this Windows 11 environment. The benchmark ran before the final regression suite, without concurrent tests.

This measures the available single-reference abstention/inspection path, not an eligible real paired detection workload, MFA latency or a 60-second capacity claim. The generated-signal eligible workflow is integration evidence, not a real-speech performance benchmark. No GPU or paid service was used.

## Software-fixture findings, separate from real audio

Known interval matching fixture: two overlapping predictions against one positive at IoU 1/3, threshold 0.3; one TP, one FP, zero FN; precision 0.5, recall 1, F1 2/3, matched boundary error 1 s. A separate exact-boundary fixture produces one TP/one FP, zero boundary error and demonstrates severity-bin disagreement accounting. At IoU 0.7 the partial-overlap fixture remains unmatched. Missing-pause events match independently within 200 ms.

Identical analytic features and the complete generated-signal CLI pair produce reference-agreement score 100 under supplied **test-only** review assertions. Known tempo/range penalties are checked against independent hand formulas; a six-semitone excursion difference saturates pitch penalty and gives overall agreement 75 when the other three dimensions qualify. Withholding half the pitch phrase weight makes pitch/overall unavailable while pacing remains available. The generated clean fixture has zero false flags, but precision/recall/F1 are null with no positives; 1,000 undefined bootstrap resamples are reported. None of these values is detection accuracy on real speech, a competition dataset result or a genuine human approval.

Synthetic-origin fixture reports are explicitly separate and never marked independent real validation. Recipe/intended labels cannot create detector outputs; flaw reviews are rejected as detector inputs. Evaluation cannot combine real/human and synthetic origins in one run. Ground-truth imports remain separate, hash-bound human assertions with actual disagreement states; no recipe window is promoted to ground truth.

## Unresolved gates and Phase 4 boundary

Human contrastive mirrors, independently verified transcripts, manually checked word/phrase boundaries, blinded flaw inventories, acceptable-alternative examples and enough split-disjoint families remain missing. Both downloaded masters share JFK; they do not form independent speaker groups. Rubric/perceptual calibration, independent alignment/detection accuracy, broader pitch/speaker/noise coverage, long-clip profiling, authenticated review provenance and cross-environment reproducibility remain open. Strict consensus and complete-window coverage may reduce availability, especially for short words.

Phase 3 software completion and independent human-evaluation completion are separate. Do not claim real accuracy from software fixtures or abstention outputs. Phase 4 should wrap `Report`, `Review`, `Evaluation`, eligibility reasons, observations, boundary events and null-score semantics in the real local service/React workspace. Preserve native timelines, explicit evidence units and Workshop + Gridline + Studio Utility. No Phase 4 implementation was started.

Final Git review checked whitespace and the complete staged inventory; no audio, models, credentials, runtime outputs or unrelated changes were included. Original dataset/analysis code, original tests, both prior schemas, AGENTS.md, uv.lock and the official PDF match `d1aa575`. The work is committed locally; no remote operation was authorized or performed.
