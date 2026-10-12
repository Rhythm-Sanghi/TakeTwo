# Attribution and tool disclosure

TakeTwo — Speech analysis workspace. Preserve notices in their original distributions and the exact per-item permission records. No source-code license has been selected in this repository; the rights owner must choose one before a code release claim. Do not apply a proposed code license to recordings or third-party resources.

## Acquired audio

John F. Kennedy; White House Audio Collection; John F. Kennedy Presidential Library and Museum. Item-specific evidence for `JFKWHA-001` (White House Army Signal Agency) and `JFKWHA-190-002` (White House Communications Agency) records public-domain status in the [acquisition ledger](pilot-collection.md). The inaugural master is the Wikimedia Commons copy. Preserve source URLs, access date, hashes and conversion/excerpt provenance. No acquired audio is included in Git or claimed publicly released. Both masters share a source speaker. Future recordings require their own rights/consent, terms and attribution.

## Alignment resources

Montreal Forced Aligner software: MIT. English (US) ARPA acoustic model and pronunciation dictionary release v3.0.0: CC BY 4.0, authors Michael McAuliffe and Morgan Sonderegger. Preserve model/dictionary cards and source acknowledgments, including Gorman, Howell and Wagner (2011), as recorded in [alignment setup](analysis-engine.md) and [model lock](../environments/mfa-models.json). Analysis uses an extracted PCM16 derivative and automatic word/phone alignment; manual reviews do not overwrite it. Model files are not redistributed here.

Kaldi/OpenFst/Pynini carry Apache-2.0 and other distribution notices as applicable. The full native environment has additional package terms; review them before bundling binaries. Lockfiles and installation instructions do not substitute for redistribution notices.

## Application dependencies

Direct versions, purpose and license inventory are in [dependencies](dependencies.md). NumPy/SciPy/soundfile use BSD licenses; librosa ISC; Pydantic/FastAPI/React/uPlot MIT; Uvicorn BSD-3-Clause; python-multipart Apache-2.0. Python SQLite is the standard-library integration. libsndfile/soxr and bundled native numerical components have additional terms/notices. Preserve full transitive package notices before bundled redistribution. No classifier is trained; scikit-learn is present transitively through librosa.

Report PDF generation uses ReportLab and pypdf from the external document-tool runtime. These are authoring/inspection tools, not application runtime dependencies; report source and regeneration instructions are retained. System fonts avoid a downloadable application font dependency.

## Human direction and AI assistance

The user directed the project scope, identity, standards and phase decisions. OpenAI Codex assisted with repository changes, architecture/scoring documentation, source-rights research, dataset/analysis/comparison/service/frontend implementation, generated signal tests, CPU/browser/recovery checks and this submission draft. No AI-generated speech, fabricated participant, permission, independent review or evaluation result is presented as genuine evidence. Generated tones/analytic arrays are explicitly software fixtures. The initial rubric is an engineering proposal and lacks independent human calibration. Human source selection, collection, consent, annotation, licensing and final submission decisions remain external work.

No paid inference API, CUDA dependency, cloud storage account or external analytics service is required for local processing. Public dataset/video hosting and release remain owner actions. Identify any additional tools used during recording/editing in the final video/report disclosure.

The product stabilization pass used Codex for the import/pairing audit, versioned draft contracts, report persistence, progressive forms, launcher and regression/browser verification. The user supplied five private genuine practice recordings, their intended transcript and same-speaker assertion. No independent review, public-release permission or calibrated accuracy was inferred.
