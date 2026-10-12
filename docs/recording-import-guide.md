# Import, pair and inspect recordings

TakeTwo — Speech analysis workspace. Start the local application, then use Recording Library. No internal IDs are needed for ordinary imports.

1. Choose **Public source reference** for an actual archival/public-speaker recording, **Self-recorded controlled reference** for a private practice baseline, or **Human participant recording** for a separate take of an existing reference's words. Participant type stays visible even in an empty workspace; import a reference first.
2. Choose a WAV/FLAC file and supply the actual spoken transcript. An optional title otherwise uses the filename. For a participant, select the reference by its title/filename; its text is copied as a draft and remains editable. Confirm the intended same-word relationship. Pasted text does not verify the audio.
3. Confirm actual permission to store/process locally. This is an importer assertion, not signed consent or a public license. Omitted ownership/license/evidence/attribution stay null and public rights stay pending. Open **Rights and permissions** only when you have actual clearance evidence; all four fields and adaptation/redistribution permission are required for clearance.
4. In **Source and provenance**, optionally record a speaker label, source URL, rationale and private consent reference. Reuse the same label for the same person or explicitly choose **Same speaker as the selected reference**. Unknown speakers share an unassigned identifier, conservatively preventing false independent-speaker groups. Internal family/source/work IDs and actual import time are generated; capture date is not guessed.
5. Click **Import recording**. Wait for successful storage and inventory refresh. The participant's actual pair is selected automatically. Use **Inspect audio in workspace** to open both tracks, then **Run analysis**. Invalid media, transcript mismatch, duplicate content and incomplete clearance preserve existing files and give recovery guidance.

Advanced **Recording details** holds channel selection and optional intended category/severity. Without a label, intent is `unspecified` and severity is null. It is not labeled near-perfect. If you do specify intent, acceptable uses 0 and other categories use 1–3. Intent is never human-reviewed or machine-detected ground truth.

## Your five practice WAV files

The originals in `speech-01/` are private and ignored by Git. The user supplied one practice transcript and confirmed one speaker. They have not been independently reviewed or cleared for public release.

| File | Measured duration | Import choice |
| --- | --- | --- |
| `reference.wav` | 30.224 s | Self-recorded controlled reference |
| `natural.wav` | 30.590 s | Human participant, select reference.wav |
| `slow.wav` | 40.590 s | Human participant, select reference.wav |
| `uneven.wav` | 29.370 s | Human participant, select reference.wav |
| `near-perfect.wav` | 31.760 s | Human participant, select reference.wav |

All are mono, 48 kHz, PCM16 WAV. A filename is not a reviewed severity label. Use a single speaker label for the reference and explicitly choose same speaker for the other four. Keep public rights pending unless real evidence is supplied. Do not classify any as a public archival reference or synthetic speech.

The default analysis cap is **45 seconds per recording**, separate from 600-second storage. All five originals fit this budget. Operators can lower the limit; the app displays the active server limit and disables analysis above it. This grants no transcript verification or scientific eligibility. Originals and playback remain available. Do not truncate audio silently or paste the full transcript onto a shorter cut.

For a compact pilot, select the same complete passage in each track, for example the first two sentences ending “easier.” Listen and locate each take's own start/end with the numeric selection controls; do not copy seconds from another take. Under **Save selection as an analysis excerpt**, supply only the words inside that cut. Save the reference excerpt first; save participant excerpts against that new reference. Each cut must fit the active server limit (45 seconds by default) and contain identical canonical words. Cut times and parent content hash are retained, with a new native time origin and unverified text.

Select the reference excerpt and a participant excerpt in Analysis Workspace. Run real alignment/extraction, inspect each native waveform/feature series, use playback/seek/zoom/pan and export JSON/CSV. Until independent evidence exists, scores remain unavailable; raw acoustic measurements are still useful. A controlled practice baseline does not satisfy the official effective-public-speaker dataset requirement.

## Review and evaluation

Two independent listeners must verify every spoken word in each take, retain actual reviewer IDs/date/evidence and resolve disagreements. A user confirming the intended text or an automatic aligner fitting it is not sufficient. Create a reviewed new dataset version using the [human pilot kit](human-pilot-kit.md); do not modify manifests or generated artifact flags manually. Rebuild alignment/features against that verified version.

Have two people check every native word boundary and agree a complete phrase partition. Prepare actual review JSON using the [worksheet](annotation-worksheet.md) and [review contract](comparison-schema-v1.json). **Dataset and Evaluation → Independent review handoff** imports those files against their original analysis. It validates binding/bounds and stores the actual decision; it never approves or authenticates a reviewer. Import both timing reviews per member, then run a new analysis. This works without editing JSON manifests. The review records themselves must be prepared from real listening, not generated approvals.

For scientific evaluation, collect two independently prepared, prediction/recipe-blinded full-coverage flaw inventories per pair, reconcile them explicitly, and retain originals/superseding history. Use [reproduction commands](reproducibility.md) to evaluate actual reports and separate human/synthetic origins. This one-person, one-transcript pilot is one connected group; it cannot establish held-out speaker generalization. `delivery-v0` is uncalibrated and unchanged.

## Corrections, persistence and legacy workspaces

**Correct this pairing safely** prepares a separate two-recording dataset version from the chosen reference and participant originals. It requires matching canonical words, resets text/review/intent assertions, and leaves the original workspace/history untouched. Stop the service and run the displayed restart command, retaining your existing MFA configuration. No identity or review is transferred automatically. A copied revision is not a new independent evaluation group.

New workspaces use [dataset schema v2](dataset-schema-v2.json). Existing v1 workspaces remain readable. **Enable private draft imports** explicitly upgrades the metadata header and retains an exact original manifest under managed `history/`; it grants no permissions or reviews. Original audio, IDs and existing artifacts remain. Legacy reports without bound snapshots or with changed code need a fresh comparison. New web reports retain a checksummed dataset snapshot: unrelated imports do not destroy historical reports, while changed inputs/pair/reviews/configuration/code or corrupt snapshots are rejected. Exports contain the same validated report.

Synthetic edits remain in the existing dataset tools, with actual recipes/time maps and explicit origin. The import dropdown does not invent a synthetic role for an arbitrary file. Keep local audio, models, consent forms, screenshots and databases outside Git.

The shared `TAKETWO_MAX_ANALYSIS_DURATION_S` setting accepts integer seconds 1–45, default 45. Restart after changing it. See [duration configuration and verification](duration-validation.md).
