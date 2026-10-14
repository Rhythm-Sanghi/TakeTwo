# Comparative insights v1

TakeTwo's comparative layer turns existing acoustic measurements into native-time
inspection targets. It produces no verified flaw, approval, delivery score,
calibrated confidence, emotion inference or independently evaluated accuracy.
`acoustic-v1`, `exploratory-v1` and `delivery-v0` remain unchanged.

## Contract and provenance

`GET /api/v1/analyses/{job_id}/insights` returns
[comparative-insights-schema-v1.json](comparative-insights-schema-v1.json).
`/insights/export` returns the complete canonical SHA-256 JSON envelope.
The original `/exploratory/export?format=json|csv` remains available and preserves
every raw candidate. New content-addressed envelopes live in
`derived/comparative-insights-v1/`; existing reports are never rewritten.

The report embeds the complete exploratory report once, with its checksum, job,
dataset version/content hash, selected members, source audio/sample/original-text
hashes, feature/alignment artifact paths and hashes, configuration and method hashes.
Common reviewed phrase partitions retain their review hashes. No feature arrays
are duplicated. Each request still validates the current managed source and
environment identities. A separate 16-entry compact cache keys the exploratory
content, comparative implementation and phrase-review hashes/partition; publication
checks existing bytes even on cache hits. Envelopes are bounded to 4 MiB.

## Evidence levels

1. **Raw feature:** actual waveform/frame measurement with native support.
2. **Automatic candidate:** a configured acoustic threshold window, not a mistake.
3. **Grouped observation:** connected compatible windows, with original IDs retained.
4. **Provisional paired segment:** corresponding supplied-text positions, not verified speech.
5. **Verified flaw region:** a separate assessment requiring independent evidence and eligibility.
6. **Independently evaluated detection:** comparison against independent held-out labels;
   software fixture tests do not establish this.

## Grouping

Reject foreign source hashes, duplicate IDs, nonfinite/incomplete measurements,
invalid native bounds and inconsistent duration. Partition by recording, exact
candidate category, energy-change sign (or low-energy family), feature hash,
method, threshold, frame window and hop resolution. Within each partition sort by
start, end and ID. Form temporal connected components when the next interval starts
at or before the component's maximum end (1e-9 s arithmetic tolerance).
Touching intervals join; positive gaps are never bridged. Transitive overlaps join.
Opposing directions, unrelated categories/configurations and recordings never join.
This is structural grouping, not an independently detected physical event.

Groups expose native union bounds/duration, original IDs, supporting window count,
median signed change, min/max changes and frame-median levels, detector configuration,
hop/window resolution, replay and limits. Overlapping raw windows are not independent
statistical support; a larger window count supplies no confidence probability.

## Word and phrase correspondence

Validate original alignment artifacts and hashes. Both must have succeeded, no OOV,
identical normalized tokens, original supplied text/hash and original token offsets.
Each must cover every canonical token index once in order with valid native bounds.
Repeated words are disambiguated by their complete canonical positions/offsets;
missing, reordered, partial, repeated ambiguous indices or mismatched text abstain.
No nearest-time, nth-output-word or fuzzy token fallback is used. Complete supplied
text mapping still does not establish the words actually spoken: omissions/repetitions
can be misaligned even in a successful MFA run. Listening remains necessary.

Each word compares native duration (`participant - reference`), relative duration
(`100 * delta / reference duration`) and preceding inter-word gap difference.
The first word has no preceding gap. Local acoustic context uses disjoint hop cells
clipped to each interval: observed support, low-energy support, frame-median energy,
linear P90-P10 energy range and energy relative to that recording's baseline.
No missing frame/tail is called quiet. Cross-take relative-energy delta is withheld
unless both intervals have complete support and valid baselines. Digital amplitude
does not establish microphone-independent effort or perceived loudness.

Phrase comparison requires equal complete phrase partitions from validated
independent approved timing consensus for each selected source and original alignment.
The API hashes those reviews into the cache/result. Phrase intervals use the first
and last provisional machine word bounds within that explicit partition, so they
remain labelled unverified. Without a common reviewed partition, phrase comparison
is withheld; punctuation, pauses and matching wall-clock times do not invent phrases.

## Alignment-gap diagnostics

Flag a gap between consecutive indexed machine words when it is at least 1 s.
Where paired correspondence exists, it must also exceed the other take's gap by
at least 0.5 s. These are inspection thresholds, not validated perceptual cutoffs.
Include actual before/after words, gap/context bounds, replay, independent hop-cell
activity measurements, selection reason and unavailable alignment confidence.
Never convert an alignment gap into a pause candidate or flaw.

The genuine reference/uneven pair has a 2.890 s machine gap after `technology`
(10.12–10.50 s) before `is` (13.39–13.47 s). The reference has a zero gap there.
Complete acoustic support in the participant gap has **0.000 s low-energy support**
under acoustic-v1's activity rule. This does not support a quiet-pause conclusion.
Misalignment, text mismatch, repeated/omitted speech or another cause requires listening.
Confidence and independently checked timing accuracy remain unavailable.

## Inspection order

No priority score is produced. First place evidence with complete native support,
RMS >=0.001, no clipping and no stored recording-quality flags; limited evidence
follows. This is a diagnostic screen, not proof of clean speech: no isolated noise
reference/calibrated SNR exists. Categories then sort: alignment anomaly, preceding
gap difference (absolute delta >=0.15 s), word duration difference (>=0.1 s), grouped
acoustic observation. Within category sort by descending measured gap/duration delta
or group union duration, then native start and evidence ID. Amplitude alone cannot
outrank other evidence. Every item includes its reason; no confidence or severity.

The following-word context of an alignment anomaly is not highlighted again as a
gap/duration item. Other words with both gap and duration changes use one gap item;
all original word measurements remain in the complete appendix/JSON. Main view starts
with six inspection items; the full ordered inventory and all groups remain accessible.

Genuine initial output: **53 raw windows → 44 groups**, 71 provisional word segments,
one gap anomaly. Grouping alone does not make all 44 observations important; the
initial selection and full inventory are distinct. Recording-level −0.854375 s
(−2.826775%) and +0.043847 dB RMS differences establish no flaw or perceptual significance.
Phrase comparison is withheld because independent phrase partitions are absent.

## Listening, reporting and limitations

Each A/B action reuses one existing native audio element and its own bounds. Switching
pauses the other track; audio is neither stretched nor synchronized by equal seconds.
Inspect moves keyboard focus to the selected native audio control. Return-to-complete
clears bounded selection and restores its full window. Navigation pauses playback.
Exploratory listening never submits reviewer completion or independent approval.

Native print puts the measured overview and selected observations first; clearly marked
print highlights use the first three ordered items (the browser starts with six).
appendices preserve all groups, paired measurements, original candidates, provisional
word lists, methods and source hashes. JSON/CSV provide full precision. The separate
six-page hackathon technical draft and historical PDFs remain separate.

Low pitch coverage and the existing independent F0 limitation remain explicit; no
new validation data justifies a changed extractor, confidence mask or scoring gate.
Actual Narrator/NVDA acceptance, independent timing/F0/flaw truth, rights and calibration
remain human/external dependencies. Codex assisted code, tests and documentation under
human direction. MIT copyright © 2026 Rhythm Sanghi remains unchanged.
