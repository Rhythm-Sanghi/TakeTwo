# Attribution and tool disclosure

TakeTwo — Speech analysis workspace. Preserve notices in their original distributions and the exact per-item permission records. Original TakeTwo source code and associated project documentation are licensed under the [MIT License](../LICENSE), copyright (c) 2026 Rhythm Sanghi, as selected by the owner. This grant does not cover private recordings, datasets, consent/reviewer records, externally licensed model or dictionary files, third-party software, or the official Track C specification. Those materials retain their own rights and attribution requirements. No permission to redistribute private data is implied.

## Acquired audio

John F. Kennedy; White House Audio Collection; John F. Kennedy Presidential Library and Museum. Item-specific evidence for `JFKWHA-001` (White House Army Signal Agency) and `JFKWHA-190-002` (White House Communications Agency) records public-domain status in the [acquisition ledger](pilot-collection.md). The inaugural master is the Wikimedia Commons copy. Preserve source URLs, access date, hashes and conversion/excerpt provenance. No acquired audio is included in Git or claimed publicly released. Both masters share a source speaker. Future recordings require their own rights/consent, terms and attribution.

## Alignment resources

Montreal Forced Aligner software: MIT. English (US) ARPA acoustic model and pronunciation dictionary release v3.0.0: CC BY 4.0, authors Michael McAuliffe and Morgan Sonderegger. Preserve model/dictionary cards and source acknowledgments, including Gorman, Howell and Wagner (2011), as recorded in [alignment setup](analysis-engine.md) and [model lock](../environments/mfa-models.json). Analysis uses an extracted PCM16 derivative and automatic word/phone alignment; manual reviews do not overwrite it. Model files are not redistributed here.

Kaldi/OpenFst/Pynini carry Apache-2.0 and other distribution notices as applicable. The full native environment has additional package terms; review them before bundling binaries. Lockfiles and installation instructions do not substitute for redistribution notices.

## Application dependencies

Direct versions, purpose and license inventory are in [dependencies](dependencies.md). NumPy/SciPy/soundfile use BSD licenses; librosa ISC; Pydantic/FastAPI/React/uPlot MIT; Uvicorn BSD-3-Clause; python-multipart Apache-2.0. Python SQLite is the standard-library integration. libsndfile/soxr and bundled native numerical components have additional terms/notices. Preserve full transitive package notices before bundled redistribution. No classifier is trained; scikit-learn is present transitively through librosa.

Report PDF generation uses ReportLab and pypdf from the external document-tool runtime. These are authoring/inspection tools, not application runtime dependencies; report source and regeneration instructions are retained. System fonts avoid a downloadable application font dependency.

## Human direction and AI assistance

The user directed the project scope, identity, standards and phase decisions. OpenAI Codex was extensively used for implementation, testing, integration and documentation, including repository changes, architecture/scoring documentation, source-rights research, dataset/analysis/comparison/service/frontend implementation, generated signal tests, CPU/browser/recovery checks and this submission draft. No AI-generated speech, fabricated participant, permission, independent review or evaluation result is presented as genuine evidence. Generated tones/analytic arrays are explicitly software fixtures. The initial rubric is an engineering proposal and lacks independent human calibration. Human source selection, collection, consent, annotation, licensing and final submission decisions remain external work.

No paid inference API, CUDA dependency, cloud storage account or external analytics service is required for local processing. Public dataset/video hosting and release remain owner actions. Identify any additional tools used during recording/editing in the final video/report disclosure.

The product stabilization pass used Codex for the import/pairing audit, versioned draft contracts, report persistence, progressive forms, launcher and regression/browser verification. The user supplied five private genuine practice recordings, their intended transcript and same-speaker assertion. No independent review, public-release permission or calibrated accuracy was inferred.

ChatGPT assisted architecture planning, problem interpretation, technical review and development instructions. Human participants supplied the genuine recordings. Independent human annotations are still required; passing AI-assisted software tests is not scientific validation. The intended Devpost Built With list includes both OpenAI Codex and ChatGPT.

The 13 October stabilization pass used Codex for audit, exact-inventory ground-truth
resolution, regression tests, responsive selector repair, documentation reconciliation
and the local report draft. These AI-assisted changes do not supply human reviewer
independence, acoustic accuracy, consent or publication approval.


The subsequent product-experience pass used Codex for outcome-first frontend
structure, scope-specific review navigation, bounded interval playback, interface
state fixtures, browser/print verification and documentation. Route-only eligible
UI fixtures and automated tone reviews are software acceptance evidence, not human
speech findings, genuine reviewer approvals or accuracy measurements.

The 14 October mobile refinement used Codex for collection placement, native workspace navigation, persistent audio-track switching, compact review/rubric/readiness flows, regression tests and isolated browser/PDF checks. Private recordings and scientific policies were preserved; automated acceptance supplies no independent human review.

Codex assisted the reference-inspection and print repair: explicit single-input presentation, report/job identity binding, compact print layout, software-only race/state fixtures, native searchable-PDF verification and documentation. No scientific gates, genuine audio or reviewer drafts were changed.
