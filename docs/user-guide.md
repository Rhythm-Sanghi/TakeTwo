# TakeTwo user guide

Speech analysis workspace. Audio and processing stay on your local Windows computer.
Use the [Windows setup guide](windows-setup.md) to install and start the application.

## Import recordings

TakeTwo — Speech analysis workspace. Start the local application, then use Recording Library. No internal IDs are needed for ordinary imports.

1. Choose **Public source reference** for an actual archival/public-speaker recording, **Self-recorded controlled reference** for a private practice baseline, or **Human participant recording** for a separate take of an existing reference's words. Participant type stays visible even in an empty workspace; import a reference first.
2. Choose a WAV/FLAC file and supply the actual spoken transcript. An optional title otherwise uses the filename. For a participant, select the reference by its title/filename; its text is copied as a draft and remains editable. Confirm the intended same-word relationship. Pasted text does not verify the audio.
3. Confirm actual permission to store/process locally. This is an importer assertion, not signed consent or a public license. Omitted ownership/license/evidence/attribution stay null and public rights stay pending. Open **Rights and permissions** only when you have actual clearance evidence; all four fields and adaptation/redistribution permission are required for clearance.
4. In **Source and provenance**, optionally record a speaker label, source URL, rationale and private consent reference. Reuse the same label for the same person or explicitly choose **Same speaker as the selected reference**. Unknown speakers share an unassigned identifier, conservatively preventing false independent-speaker groups. Internal family/source/work IDs and actual import time are generated; capture date is not guessed.
5. Click **Import recording**. Wait for successful storage and inventory refresh. The participant's actual pair is selected automatically. Use **Inspect audio in workspace** to open both tracks, then **Run analysis**. Invalid media, transcript mismatch, duplicate content and incomplete clearance preserve existing files and give recovery guidance.

Advanced **Recording details** holds channel selection and optional intended category/severity. Without a label, intent is `unspecified` and severity is null. It is not labeled near-perfect. If you do specify intent, acceptable uses 0 and other categories use 1–3. Intent is never human-reviewed or machine-detected ground truth.


## Inspect a recording

Choose Inspect audio in workspace. Leave Participant pair set to Reference inspection
only and run analysis. Automatic alignment is optional and requires the documented
local MFA resources. Acoustic measurements remain useful without alignment.

For an existing result, choose View latest analysis or open its history entry.
The backend reuses compatible acoustic stages; import is not necessary again.
Inputs over the configured analysis limit remain playable. Save an explicit excerpt
from each native timeline and provide the exact words in each cut.

## Compare two takes

Use Add participant for a separate recording of the intended same words. Choose its
pair in Analysis Workspace and run analysis. Each recording keeps its own duration
and native clock; equal timestamps are not assumed to represent the same word.

Read Measured recording differences first. Duration is whole-recording duration,
including quiet segments. RMS and peak are waveform amplitude in full-scale units.
dBFS values and differences depend on recording gain, microphone and noise. They do
not measure calibrated sound pressure, perceived loudness, confidence or vocal effort.

Energy P10/P50/P90 and the small distribution plot describe actual complete frames.
Activity is an energy heuristic, not verified speech duration. The unobserved tail
is reported separately. Accepted pitch coverage counts only frames meeting acoustic-v1's
existing finite/voiced/confidence rule. Missing F0 is never filled with invented values.

## Listen to automatic observations

Automatic observations include low-energy support and changes between adjacent
energy windows. These are unverified acoustic events, not mistakes. Energy-change
windows may overlap. The first eight rows are shown initially; Show all observations
reveals the remaining rows. Exports retain every row.

Inspect interval seeks and selects the interval on its own recording. Replay interval
switches the active track, pauses other playback, and stops at the interval boundary.
Open Candidate method and thresholds for its actual rule, threshold, frame resolution
and feature hash. Intentional pauses, breath, noise and dropout cannot be distinguished
by these rules alone.

Listen and explore evidence retains waveform selection, native audio, feature charts
and excerpt tools. Use the precision controls for keyboard-accessible numeric boundaries.

## Inspect automatic words

Open Machine-aligned transcript — unverified. Each word button seeks its actual
automatic interval. Source transcript hashes identify the supplied text. Missing
alignment stays explicit. An automatic word-span rate is displayed only for complete
successful, non-OOV alignment with at least two words; it includes internal gaps and
uses unverified words. It is not the authoritative speaking-rate field.

Matching complete token sequences can show automatic word correspondence. No timestamp
is invented for missing, ambiguous or unaligned words. Neither view verifies the transcript.

## Understand assessment and readiness

Verified Assessment follows the listening tools. Missing evidence is listed explicitly.
Review Workspace supports independent transcript, timing and blinded flaw review; see
the [review guide](review-workspace.md). Automatic candidates are never copied into
reviewer annotations. Rights, consensus, coverage and scoring rules stay authoritative.

Dataset and Evaluation distinguishes successful inventory counts from review evidence.
Six prerequisite rows show stored rights, transcript, timing, flaw inventories,
reviewed-version processing and evaluation requirements with their next action/location.
The [reviewed evidence workflow](review-protocol.md#transcript-timing-flaw-review-and-scientific-eligibility) supplies the ordered
procedure and exact validated commands. Its read-only reviewer-file preflight imports
nothing. Actual reviewers and permission evidence are still required.
Zero means an authoritative zero; Unknown means the backend did not supply the value.
Loading, partial data, request errors and reviewer-handoff restrictions have separate
messages. Retry dataset readiness reloads that request. A prior inventory is labeled
as prior data and cannot establish current approvals. During handoff, complete or end
the authorized review before using general analysis APIs.

## Comparative findings and data exports

Read **What analysis found**, then **Differences worth inspecting**. Each selected
item shows **Why inspect**, a neutral **Listen for** question, actual measurements
and its limits. Selection follows a deterministic support/category/duration rule,
not validated importance or severity. Open **Comparative evidence** for all groups
and provisional words; **Exploratory details / technical appendix** retains original
windows, words, quality and configuration. Missing/partial correspondence withholds
paired comparisons. A machine gap is not automatically silence or hesitation.

**Listen to reference** and **Listen to participant** replay each observation on its
own clock, pausing the other track. **Inspect waveform** focuses that audio control.
**Return to complete recording** clears bounded replay. On narrow screens, switching
the mounted reference/participant tracks preserves each cursor and selected interval.

Comparative JSON (called single-recording insights JSON in reference inspection)
retains the complete result and original exploratory evidence. Exploratory JSON
includes its versioned checksum envelope; interval CSV contains every raw acoustic
window and its method/provenance columns. Display limits do not truncate exports.
**Retry comparative insights** repeats a safe GET; raw evidence remains available
if that additional layer fails.

## Searchable reports and workspace printing

1. Restore the intended completed analysis. Check reference/participant filenames,
   job ID, dataset version and native intervals before exporting.
2. Start with **Export Analysis Summary / save PDF**. It selects three existing
   observations and verification status; it is not a delivery-flaw diagnosis.
3. Use **Export Full Evidence Report / save PDF** for every group, provisional word,
   raw acoustic window, method and provenance. JSON retains the authoritative model;
   interval CSV retains raw windows. A summary is a separate document, not an appendix.
4. In Chromium's print destination, select **Save as PDF**. The two owner-supplied
   Microsoft Print to PDF files contain outlined glyphs and no extractable text.
   That printer path is unsuitable for those outputs. Changing a filename cannot
   restore absent text; re-export from the actual application rather than using OCR.
5. **Print workspace evidence** (or ordinary browser printing) produces a deliberate
   workspace view: selected observations, current native chart windows and an explicit
   verification state. It excludes technical inventories and interactive controls;
   those remain available through the dedicated full report and data exports.
6. In Dataset & Evaluation, use **Export Dataset Readiness / save PDF** for selected
   recording/version identity, all six prerequisites, inventory and scientific caveats.
   Interactive import shells are excluded; instructions remain available in the app
   and [reviewed-evidence workflow](review-protocol.md#transcript-timing-flaw-review-and-scientific-eligibility). Actual counts or
   unavailable states are preserved. Export does not approve evidence or rights.
7. Reopen the saved file. Select/copy a recording name and numeric measurement, search
   for a highlighted phrase, and check the correct comparison/reference footer and
   page counters. Inspect every page for clipping, blank sections and readable charts.
8. Recheck text with an independent extractor. The optional QA tools require no
   application dependency changes:

   ```powershell
   uv run --with pymupdf==1.28.2 --with pypdf==6.20.1 python scripts/check_pdf_text.py $pdfPath --expect TakeTwo
   ```

   Add repeated `--expect` arguments for actual recording names, headings, Unicode
   observations, numbers and limits. Use `scripts/check_analysis_pdf.py` with the
   matching JSON/CSV for complete comparative inventory, native intervals and hashes.
9. Searchable/selectable text, embedded fonts and an available structure tree are
   checked separately. They do not certify PDF/UA, reliable reading order in every
   viewer, keyboard audio usability or actual Narrator/NVDA speech. Review tagged
   headings/tables and reading order with the intended viewer/assistive technology;
   spoken acceptance remains a real-person task.

Reports containing private recordings, source identities or review evidence remain
local. Do not attach them to a public release without genuine rights and authorization.

## Excerpts and corrections

Imports support WAV/FLAC up to 100 MiB and 600 seconds; analysis defaults to 45 seconds
per member. The active server budget is shown in the app. Longer originals remain
playable. Select each take's own native boundaries and enter only the words actually
inside the cut; equal wall times across recordings are not corresponding words.
Save a reference excerpt first, then participant excerpts against it. Each cut must
fit the active budget and share canonical words. Parent hashes and cut offsets remain
recorded; the excerpt has its own time origin and unverified text. Never silently
truncate audio or attach a full transcript to a shorter cut.

### Persistence and legacy workspaces

**Correct this pairing safely** prepares a separate two-recording dataset version from the chosen reference and participant originals. It requires matching canonical words, resets text/review/intent assertions, and leaves the original workspace/history untouched. Stop the service and run the displayed restart command, retaining your existing MFA configuration. No identity or review is transferred automatically. A copied revision is not a new independent evaluation group.

New workspaces use [dataset schema v2](dataset-schema-v2.json). Existing v1 workspaces remain readable. **Enable private draft imports** explicitly upgrades the metadata header and retains an exact original manifest under managed `history/`; it grants no permissions or reviews. Original audio, IDs and existing artifacts remain. Legacy reports without bound snapshots or with changed code need a fresh comparison. New web reports retain a checksummed dataset snapshot: unrelated imports do not destroy historical reports, while changed inputs/pair/reviews/configuration/code or corrupt snapshots are rejected. Exports contain the same validated report.

Synthetic edits remain in the existing dataset tools, with actual recipes/time maps and explicit origin. The import dropdown does not invent a synthetic role for an arbitrary file. Keep local audio, models, consent forms, screenshots and databases outside Git.

The shared `TAKETWO_MAX_ANALYSIS_DURATION_S` setting accepts integer seconds 1–45, default 45. Restart after changing it. See [duration configuration and verification](verification.md#analysis-duration-and-capacity).

## Error recovery and human acceptance

Loading, authoritative empty data, unavailable requests and reviewer restrictions
are distinct states. Reconnect / refresh or Retry exploratory measurements restores
stored inputs; do not duplicate an import. Retry dataset readiness reloads only that
request. Previously loaded inventory is not a current approval. Processing failures
show the worker's reason; **Retry this analysis** preserves its original request.
During a reviewer handoff, finish or end the authorized review before general API use.

Actual listening and spoken accessibility remain pending until a person completes
the [review protocol](review-protocol.md). Keep product usefulness notes separate
from independent scientific annotations. Software tests and successful processing
do not establish detection accuracy, permissions or scientific acceptance.
