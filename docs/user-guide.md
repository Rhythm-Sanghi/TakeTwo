# TakeTwo user guide

Speech analysis workspace. Audio and processing stay on your local Windows computer.
Use the [Windows setup guide](windows-setup.md) to install and start the application.

## Inspect a recording

In Recording Library, import a reference WAV/FLAC and its actual words. Choose the
recording type deliberately and confirm permission for local processing. Source,
speaker, consent and rights information remain editable before import; unknown
information stays unknown. Originals are preserved.

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
Zero means an authoritative zero; Unknown means the backend did not supply the value.
Loading, partial data, request errors and reviewer-handoff restrictions have separate
messages. Retry dataset readiness reloads that request. A prior inventory is labeled
as prior data and cannot establish current approvals. During handoff, complete or end
the authorized review before using general analysis APIs.

## Export and recover

Read **What analysis found**, then **Differences worth inspecting**. Initial items
explain their actual difference and selection rule; they are never confirmed flaws.
Use **Listen to reference** and **Listen to participant** on a paired observation:
each recording plays its own native interval. **Inspect waveform** moves focus to
that track's audio control. **Return to complete recording** clears bounded replay.
Open **Comparative evidence** for every group and provisional word measurement,
or **Exploratory details / technical appendix** for the original windows, words,
quality and extraction configuration. Missing/partial text correspondence withholds
paired comparisons. A machine gap is not automatically silence or hesitation.

**Export comparative JSON** includes the complete new result and original exploratory
evidence. Printing starts with the measured overview and selected local observations,
followed by marked technical appendices. **Retry comparative insights** reloads a safe
GET; raw evidence remains available if the additional layer fails.

Export exploratory JSON saves the full versioned report and its checksum. Export interval
CSV saves every automatic event and method/provenance columns. Print exploratory report /
save PDF opens native browser printing: select Save as PDF for selectable text and plots.
Scientific report exports and the hackathon technical report remain separate.

If loading fails, use Retry exploratory measurements or Reconnect / refresh. Do not
re-import a stored file. Processing failures show the worker's reason and recovery action;
Retry this analysis preserves the original request. Successful software tests do not
establish real-speech detection accuracy or independent scientific acceptance.
