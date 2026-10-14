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

## Guided session order

Work through one test at a time with the facilitator. Before advancing, the listener
reports audible content, usefulness and transport problems in their own words. Keep
the actual wording; separate any facilitator interpretation from the observation.
An unanswered test remains pending. Preparation or automatic playback is not a result.

1. **Uneven alignment anomaly.** Replay the existing `technology` → `is` card in
   reference / participant / reference order at unchanged comfortable volume. Describe
   the words and sounds inside the participant interval before classifying it. Check
   each native start/end and whether a bounding word is clipped. The 2.890 s machine
   gap and zero low-energy support do not prescribe what the listener should hear.
2. **Gap before `helps`.** In the retained uneven comparison use reference
   13.23–13.64 s and participant 14.35–15.06 s (provisional gap difference +0.560 s).
   Fresh runs must use their own reported intervals. Compare the
   transition into the word; report an audible difference or uncertainty, and whether
   assigned boundaries make the comparison understandable. Timing alone is not hesitation.
3. **Gap before `a`.** In the retained comparison use reference 15.39–15.98 s and
   participant 16.25–16.32 s (provisional gap difference −0.510 s).
   Check both clips, including the very short participant interval.
   Report if the bounded replay is technically correct but too short to interpret.
   Inspect surrounding recording context separately; do not silently change the finding's bounds.
4. **Energy observations.** The retained uneven group `g-b807761964c99fe6fae32f69`
   covers participant 0.00–1.50 s with two measured windows. Open that actual
   grouped observation and replay its native
   interval. Describe any audible level change and whether the explanation is useful.
   These are within-recording changes; they do not establish cross-take emphasis or cause.
5. **Transport.** Switch tracks while one is playing, replay the same selection twice,
   then return to the complete recording. Report overlapping audio, missing sound,
   incorrect cursor/bounds, a lingering stop boundary or unexpected speed changes.
6. **Other participant takes.** Repeat on `natural.wav`, `slow.wav` and `near-perfect.wav`
   using each completed analysis's actual selected observations and native intervals.
   Recording titles do not establish performance quality. Missing analysis or absent
   categories must be recorded as such; never invent a corresponding finding.
7. **Reference-only playback.** Restore the completed reference inspection. Play
   an actual selected observation, then use Inspect waveform and the native audio
   control. Record whether its identity and boundaries are clear, and whether
   absent participant controls or comparison language cause confusion.
8. **Full recording playback.** Clear bounded replay by using the native complete
   recording controls. Play the reference and uneven recording individually from
   their beginning to their end (retained durations 30.224375 s and 29.370 s).
   Record truncated words, unexpected stops, overlap, silence or failures actually
   heard. Switch tracks mid-play and verify that the previous track stops.

For every case, collect exact heard words/sounds, start/end clipping, switching
and overlap behaviour, any missing sound, and explanation usefulness before
assigning an outcome. Use **Passed**, **Failed**, **Inconclusive**, **Not performed**
or **Blocked**, separate from the observation categories below. A useful explanation
alone cannot pass an unheard playback test. Record a blocker and recovery action;
an unperformed or blocked case keeps overall human acceptance pending.

The earlier Test 1 response explicitly said human listening was not performed;
audible content and playback were unassessed. Its text-only observation about
2.890 s versus zero low-energy support is retained privately. It is neither a
listening pass nor proof of an alignment error. No later audible observation is
available. Do not overwrite this historical response with facilitator conclusions.

Classify **after** collecting observations: useful comparison, possible machine-alignment
problem, technically correct but not useful, misleading explanation, playback problem,
or inconclusive. Multiple categories may apply. A usability report of an alignment
problem does not become independent reviewed timing or scientific ground truth.
For a suspected defect, retain the exact card/job, control sequence, expected/observed
behaviour and repeat outcome. Reproduce it before changing code; recheck the affected
journey and relevant regressions afterward. Keep private listener notes outside Git.

## Listener entries

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
| Outcome / reason / reproducible steps / repeat outcome | |

Categories: **Useful comparison**; **Possible machine-alignment problem**;
**Technically correct but not useful**; **Misleading explanation**;
**Playback problem**; **Inconclusive**. Earlier worksheet categories remain valid
historical notes; do not rewrite a completed review to fit the new labels.

Store completed notes separately from independent annotations. Do not import these
notes into review approval, score eligibility, calibration or accuracy metrics.
Actual screen-reader listening acceptance (Narrator/NVDA) is also pending. Use the
[separate spoken-accessibility worksheet](spoken-accessibility-acceptance.md) to
record focus, announcements and transport failures separately from axe results.
