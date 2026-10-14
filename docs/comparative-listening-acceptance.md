# Comparative listening acceptance

TakeTwo — Speech analysis workspace. **Actual human listening: pending.**
Software checks verify routes, native clocks and cancellation; they do not establish
that a listener finds the passage useful. This workflow is a product acceptance
exercise, not scientific ground truth or flaw-detection accuracy.

## Prepare

Use authorized private copies of `reference.wav`, `uneven.wav`, `natural.wav`,
`slow.wav` and `near-perfect.wav`. Preserve originals. Select the reference and one
participant, run or restore a completed analysis, and keep the dataset version,
job ID, source hashes and comparative method/implementation hash with the review.
No rights, text, phrase or annotation approval is implied by this exercise.

## Review each selected insight

1. Read the observation, native timestamps, **Why inspect**, listening question
   and item-specific limit. Explain why it was selected in your own words.
2. Play the reference segment, then the participant segment. Each uses its own
   native clock; do not assume matching timestamps or time stretching.
   Confirm that each starts at its displayed native timestamp and stops at its
   displayed end boundary. Record either discrepancy rather than treating a play
   event as successful acceptance.
3. Replay either passage as needed. Confirm the bounding words or acoustic change
   are inspectable and that playback stops at the intended end.
4. Inspect provisional transcript boundaries and waveform/energy evidence.
   Distinguish a machine word gap from measured low-energy support.
5. Record whether the measurement is audible or inspectable, whether the
   explanation helped, any misleading wording and additional evidence needed.
6. Select one or more review categories below. Record the listener's name/date
   only with their permission. Keep the notes private unless cleared for release.

For the restored reference/uneven anomaly, check `technology` → `is`: reference
10.93–11.88 s; participant 10.12–13.47 s. The participant's provisional gap is
10.50–13.39 s (2.890 s), with 0.000 s low-energy support and complete frame
support. Check audible words and alignment/transcript correspondence. Activity
can include noise; do not assume a pause, speech, incorrect pronunciation or a
proven alignment error. Fresh runs must use their own actual reported intervals.

## Review form

Repeat for each selected item in all four participant comparisons. Leave fields
blank until an actual listener completes them; do not prefill a favourable result.

| Field | Listener entry |
| --- | --- |
| Date / listener (with permission) | |
| Reference / participant / source hashes | |
| Dataset version / job / implementation hash | |
| Stable evidence ID / observation category | |
| Reference native interval / participant native interval | |
| Selection reason understood? Explain in own words | |
| Reference played / participant played / replay needed | |
| Provisional text and waveform/energy inspected | |
| Audible or inspectable? Describe evidence | |
| Explanation useful? Why? | |
| Misleading wording or navigation problems | |
| Additional evidence needed | |
| Review category or categories | |

Categories: **Useful comparison**; **Possible machine-alignment problem**;
**Technically correct but not useful**; **Misleading explanation**;
**Playback problem**; **Inconclusive**. Earlier worksheet categories remain valid
historical notes; do not rewrite a completed review to fit the new labels.

Store completed notes separately from independent annotations. Do not import these
notes into review approval, score eligibility, calibration or accuracy metrics.
Actual screen-reader listening acceptance (Narrator/NVDA) is also pending. Use the
[separate spoken-accessibility worksheet](spoken-accessibility-acceptance.md) to
record focus, announcements and transport failures separately from axe results.
