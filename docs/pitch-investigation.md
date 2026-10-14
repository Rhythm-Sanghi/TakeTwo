# Pitch coverage investigation — 2026-10-13

These are actual local measurements on the five genuine private same-person practice takes, not independent pitch accuracy or detection evaluation. No recordings, identities or raw private diagnostic artifacts are released. `acoustic-v1` and `delivery-v0` remain unchanged: pYIN range 60–500 Hz, 1,024 samples (64 ms), 160-sample hop (10 ms), center=False, no padding, confidence >=0.8 and finite voiced F0. Unaccepted F0 remains null; relative pitch never supplies fabricated scores.

| Take | Duration s | Raw voiced % | Accepted % | Probability median | Probability p95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| reference | 30.224375 | 72.091 | 0.597 | 0.01185 | 0.54853 |
| natural | 30.590 | 76.351 | 0.295 | 0.01185 | 0.48499 |
| slow | 40.590 | 69.331 | 0.617 | 0.01082 | 0.54853 |
| uneven | 29.370 | 75.162 | 0.512 | 0.01310 | 0.54853 |
| near-perfect | 31.760 | 75.678 | 0.284 | 0.01185 | 0.42606 |

Raw voiced medians are 119.3–123.5 Hz; raw estimates include the 60 Hz floor and reach 231.8–249.9 Hz. All probability frames are finite; unvoiced NaNs are expected and masked before JSON serialization. No adjacent finite-frame jump exceeds 10 semitones in these runs; no pYIN warning was emitted. Canonical peaks are 0.297–0.400 and clipping fraction is zero. Median frame levels are -31.1 to -32.4 dBFS; fifth-percentile levels -43.3 to -44.7 dBFS. Those lower levels combine pauses and noise: no isolated noise reference/calibrated SNR or microphone response is available. These observations cannot establish the cause of each low-confidence frame.

## Controls and hypotheses

Three-second clean known-F0 sine controls at 80/120/200/400 Hz all produce 100% raw voiced estimates with median frequency within 0.7% of the known fundamental. Accepted fractions are respectively 0/0/100/100%; median probabilities 0.426/0.686/0.891/0.985. Thus even a clean low-frequency signal can be withheld with this window/confidence combination; input noise alone does not explain the limitation.

A diagnostic 2,048-sample window (not a production change) raises 80/120 Hz control acceptance to 60.069%/100%. Reference acceptance increases only from 0.597% to 1.362%, still far below the 50% local usable-pitch gate. Changing only bounds to 40–500 or 60–800 Hz leaves reference acceptance at 0.597%. Reducing reference gain by 20 dB leaves its raw voiced fraction, acceptance and probability quantiles unchanged. Gain normalization therefore does not solve this observed case. Window-dependent confidence is supported by controlled evidence; reliability on actual low-pitched speech is still unvalidated.

No swapped pYIN outputs, manufactured contour, NaN-to-score propagation or normalization defect was found. This is a verified configuration/model limitation, not evidence supporting a lower confidence threshold. Keep abstention. Any longer-window policy requires a separate version, native-time support checks, independent pitch labels, low/high-register/noise controls, benchmark and recalibration before adoption. No runtime acoustic/scoring code changed.

Reproduce diagnostics on authorized canonical input copies:

```powershell
uv run python scripts/inspect_pitch.py --workspace $privateWorkspace --output .\local-data\pitch-diagnostics.json --probes
```

The script reports raw/accepted coverage, quantiles, NaNs, jumps, levels, clipping, warnings and diagnostic runtime. It never publishes analysis features or modifies inputs. Initial diagnostic runtimes were 13.3–18.7 s per take under concurrent verification load (not isolated capacity benchmarks); the -20 dB control took 23.4 s. Raw diagnostic JSON is retained privately. Independent F0 accuracy, frame-wise confidence calibration and causal microphone/noise attribution remain open.

## Stabilization recheck — 13 October 2026

Reran the unchanged diagnostic on the authorized isolated five-take fixture copies.
Accepted fractions reproduce the table: reference 0.596619%, natural 0.294792%,
slow 0.616827%, uneven 0.511771%, near-perfect 0.283912%. The reference -20 dB
control remains 0.596619%. Known 80/120/200/400 Hz controls again accept
0/0/100/100%; all have 294 frames. Private diagnostic output is retained in
`local-data/stabilization-pitch.json`; no audio or review evidence is published.
Per-take diagnostic times were 6.96–12.33 s under mixed verification load, not
a comparable before/after benchmark. No performance improvement is claimed.
The previous window/range probes remain historical evidence; this recheck did not
repeat them or establish genuine F0 accuracy. Close the implementation-defect
hypothesis with the existing limitation and abstention, not a changed threshold.

## Product completion recheck — 14 October 2026

Repeated all five genuine takes, four known-frequency controls, reference gain
control and the complete window/range probe matrix on the authorized isolated copy.
Private evidence: `local-data/completion-pitch.json`. Accepted real fractions again
range from 0.283912% to 0.616827%; reference is 0.596619%, uneven is 0.511771%.
The reference gain control remains unchanged. No >10-semitone adjacent jump or
pYIN warning was observed. Controls again accept 0/0/100/100% at 80/120/200/400 Hz.
The 2,048-sample window accepts 60.069444%/100% at 80/120 Hz, but only 1.362126%
on the real reference; range-only probes do not improve its accepted coverage.

This repeats a configuration limitation, not real-speech F0 accuracy. There is no
permissible independently checked F0 corpus in this workspace. No experimental
extractor or relaxed score gate is justified. Acoustic-v1, delivery-v0, null F0
and scientific abstention remain unchanged. A future separately versioned study
needs independently checked F0, octave-error/coverage measures, register/noise
controls and a held-out protocol before replacing any scientific policy.
