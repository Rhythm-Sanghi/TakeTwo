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

## Creator and development tools

Rhythm Sanghi created and directed TakeTwo: product direction/use cases, visual
identity, scope and workflow decisions, genuine practice recordings and intended
transcripts, review of analysis/report limitations, improvements and submission.
OpenAI Codex assisted software implementation, integration, testing and documentation.
ChatGPT supported planning, technical review and development guidance. Both tools
belong in Devpost's Built With list.

Generated signals are software fixtures, not human speech accuracy evidence. No
AI-generated consent, independent annotation or listening result is presented as real.
Human rights clearance, independent review, calibration and final submission remain
separate. Add any actual recording/editing tools to the final video/report disclosure.
