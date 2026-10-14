# Exploratory Speech Analysis v1

Exploratory Speech Analysis summarizes existing acoustic-v1 feature artifacts.
It is separate from Verified Assessment: it produces no delivery scores, review
approvals, flaw labels, calibrated confidence, or evaluation accuracy. It never
writes reviewer drafts, approvals, dataset annotations or comparison artifacts.

The versioned contract is `exploratory-schema-v1.json`. The API provides
`GET /api/v1/analyses/{job_id}/exploratory` and
`GET /api/v1/analyses/{job_id}/exploratory/export?format=json|csv`.
JSON includes the complete report with a canonical SHA-256 envelope. CSV contains
native recording intervals for automatic candidates. Both require ordinary
workspace access; reviewer handoffs cannot access these endpoints.

Reports bind the selected job, reference and optional pair to actual dataset and
feature hashes. Available features from a failed or incomplete job are explicitly
partial; an absent feature stage returns HTTP 409. Summaries are immutable,
content-addressed files under `derived/exploratory-v1/`. Existing alignment,
feature and comparison implementation hashes remain unchanged.

Measurements include actual duration, source and canonical sample rates, RMS,
peak, clipping fraction, energy baseline and linear 10th/50th/90th percentiles,
existing active energy range, observed activity/low-energy support, unobserved
tail, accepted pitch coverage, quality flags and provisional machine word times.
Activity support partitions the observed complete-frame support into disjoint
hop cells; overlapping full-window activity/quiet unions are not added together.
Digital levels depend on gain, microphone and noise and are not calibrated SPL,
perceived loudness or vocal effort.

Candidates use two deterministic rules. Contiguous low-energy hop cells lasting
at least 0.15 s are described by their position within the recording. Their
threshold is reconstructed from acoustic-v1's actual two-pass rule: seed the upper
quartile of audible frame levels, select initial frames within the activity drop,
then apply their median minus that drop together with the configured RMS floor.
The final descriptive baseline is recomputed after that selection and must not
be substituted for the threshold actually used. All-floor input has no relative
baseline; its candidates arise only from the absolute-floor rule. The stored mask
must agree with this reconstruction or exploratory generation fails closed.
Adjacent complete 0.5 s windows differing by at least 6 dB in median frame energy
produce energy-change candidates. Only fully contained energy frames contribute
to each window. Candidates carry the source feature hash, native bounds, actual
energy, method and relevant threshold. Energy changes have a delta threshold,
not a dBFS threshold. Boundaries have 10 ms hop resolution with 25 ms window
smearing. They cannot distinguish breath, background noise, intentional pause
and dropout; silence is not a mistake.

Pair summaries report participant minus reference duration, absolute duration
difference, relative difference using reference duration, RMS level difference
`20 log10(participant RMS / reference RMS)` and active energy-range difference.
RMS difference is unavailable if either RMS is below 0.001. Whole-recording
duration differences do not establish speech rate or a pacing flaw.

Provisional word correspondence requires validated successful alignment artifacts
with identical normalized token sequences. Matching token indices retain each
recording's native intervals. Estimated automatic word-span rate is
`60 * aligned word count / (last word end - first word start)` only for successful
complete alignment with at least two words and no OOV entries. It includes
internal gaps and uses supplied unverified text. It is separate from authoritative
reviewed rate and cannot establish transcription or timing accuracy.

Generated-signal tests verify implementation behavior, not real-speech accuracy.
No independent real F0 or timing ground truth is created by this feature.
Codex assisted implementation, test design and documentation under human direction.

The browser results view puts recording identity, measured summaries and automatic
observations before the native listening tools and separate Verified Assessment.
Candidate inspect/replay actions use their own recording clocks. First-eight display
limits do not truncate exports. Provisional words have seek controls. Deterministic
energy-distribution plots use the actual three percentiles, with a −120 to 0 dBFS axis.

CSV includes feature hashes, thresholds, frame/hop resolution and limitations.
The dedicated native print scope contains selectable measurements, energy plots,
all candidate rows, native automatic word times, provenance and actual assessment
requirements when loaded. It does not change the scientific six-page report.

A per-application 16-entry cache retains compact summaries only. Every request still
validates current source audio and environment identity. Dataset content, job/state,
selection, feature/alignment hashes, missing stages and exploratory implementation
hash participate in the key. Publication still checks existing content before reuse.
The existing stat-keyed validated-acoustic cache also supplies cached artifact digests,
avoiding repeated serialization during report/overlay/exploratory restoration. It
retains the existing managed-artifact metadata trust boundary; it is not a defense
against a privileged local attacker changing bytes while restoring file metadata.
