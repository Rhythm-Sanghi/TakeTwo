# TakeTwo scoring policy

Status: `delivery-v0` is implemented in Phase 3 with initial, uncalibrated tolerances; it must be calibrated and frozen before held-out evaluation. All numerical tolerances below are initial engineering hypotheses, not validated perceptual limits. The official judging weights assess the project; they are unrelated to this delivery rubric.

Evaluation ground truth is separate from delivery scoring. The
[exact-inventory-v1 policy](comparison-engine.md) withholds metrics when independent
flaw boundaries differ, even within semantic listening tolerance. It changes no
delivery-v0 weight, threshold, acoustic feature or detector output.

## Interpretation and coordinate system

Controlled local-reference support changes only permitted genuine input context: a self-recorded reference with explicit consent/rationale can be compared under the same rights, transcript, timing, quality and coverage gates. It is not an official effective-public-speaker baseline. `delivery-v0`, all dimensions, thresholds, formulas and uncertainty/abstention rules remain unchanged. Unlabeled acquisition intent is null and never contributes a human severity label or a perfect score.

Scores describe measured delivery agreement with a selected reference on the same words. They do not measure persuasion, emotion, intelligence, text quality or overall speaking ability. A stylistic difference can be intentional and effective. The UI calls a threshold crossing a "delivery deviation" and offers an audio review action. A human evaluator decides whether it is undesirable in context.

Each recording retains its native time axis. Correspondence uses canonical token indices and reviewed phrase boundaries (punctuation plus confirmed spoken boundaries). Compare matching phrases and inter-word gaps; never use unrestricted time warping to erase timing deviations. Frame masks exclude unreliable pitch, silence for pitch statistics, clipping-contaminated spans and invalid alignment. Intervals with poor evidence are unavailable, not zero deviation.

## Signal definitions

At analysis rate `fs=16000 Hz`, use 25 ms (400-sample) Hann windows, 10 ms (160-sample) hops and 512-point real FFT, `center=False`. Drop incomplete terminal frames and report their coverage; frame timestamps denote the center of the observed window. Freeze window normalization in config.

- `RMS(t)=sqrt(mean(x[n]^2))`; energy `E(t)=20 log10(max(RMS(t),1e-6)) dBFS`. This is a digital relative level, not calibrated sound pressure.
- Spectrum `P(k,t)=|FFT(w*x)|^2 / sum(w^2)`, with frequency bins `k*fs/512`. For one-sided total power, double non-DC/non-Nyquist bins and divide the sum by 512; Parseval fixtures check this normalization. Use 40 mel bands over 0-8000 Hz and 13 DCT-II orthonormal MFCC coefficients from natural-log mel power floored at `1e-10`. Freeze mel-filter normalization and quantile interpolation in config. MFCCs and spectral centroid support acoustic inspection/quality checks; they do not independently score articulation or "vocal clarity" without validated labels.
- F0: CPU pYIN, initial range 60-500 Hz, frame length 1024, hop 160, `center=False`. Its frame centers differ from FFT frames; join using actual timestamps, never array index. Exclude unvoiced/low-probability frames (initial voicing threshold 0.8). Flag range saturation, octave jumps and insufficient voiced coverage for review. These bounds may exclude some voices; make the range configurable and display the limitation.
- Pause candidates: non-speech gaps between aligned words lasting at least 150 ms, corroborated by low energy. Initial energy gate is voiced/speech median energy minus 25 dB; breath/noise and alignment artifacts need review. Leading/trailing silence is a recording-quality indicator and not an inter-word pause penalty.
- Phrase speech rate `v=60*N/T` words/minute where `T` spans first word start to last word end, including internal pauses. Also show articulation rate `60*N/(T-sum(internal pauses))` as evidence when denominator is valid. Token counts, not inferred syllables, define this version.

Pitch normalization: `p(t)=12 log2(F0(t)/median_voiced(F0))` semitones within each recording. Energy normalization: `e(t)=E(t)-median_speech(E)` dB. Both remove register/global gain offsets while retaining excursion magnitude. Do not divide each recording by its own variance: that would hide monotony. For robust calibration residuals use scales from acceptable training pairs, never from held-out examples. Normalization cannot remove all microphone, accent or speaker effects; evaluate them explicitly.

## Dimension measurements and initial tolerances

For corresponding phrase `q`, `Q90-Q10` denotes a robust excursion range. Use normalized contours for pitch/energy statistics. A phrase needs at least three words and 0.5 seconds of usable duration; pitch needs at least 50% valid voiced frames in both recordings. Rate compares the same word count. Reject zero/negative durations.

| Dimension (weight) | Signed measurement / deviation | Initial tolerance `tau` and saturation width `b` |
| --- | --- | --- |
| Pacing (0.25) | `d=ln(v_participant/v_reference)`; report both rates, ratio and phrase durations | `tau=ln(1.15)`, `b=ln(1.5)` |
| Pause behavior (0.25) | For each shared inter-word boundary, `d=g_participant-g_reference` seconds, where gap below 150 ms is 0; include missing/extra pause positions | `tau=max(0.15,0.25*g_reference)` seconds, `b=0.75` seconds |
| Energy variation (0.25) | `d=(Q90(e)-Q10(e))_participant-(Q90(e)-Q10(e))_reference` dB | `tau=3` dB, `b=6` dB |
| Pitch dynamics (0.25) | `d=(Q90(p)-Q10(p))_participant-(Q90(p)-Q10(p))_reference` semitones | `tau=2` semitones, `b=4` semitones |

The two range dimensions capture flattened/excessive dynamics but can miss misplaced emphasis. Display word-level normalized contours and signed deltas as context; do not claim the range metric detects every tonal flaw. Uniform gain/register shifts should leave these scores essentially invariant, while meaningful excursion changes remain detectable.

For non-pause dimensions, calibrate `tau_i=max(initial_tau_i,Q95(|d_i|))` from reviewed acceptable training pairs, and record sample counts and parameter change rationale. For pauses, use `tau_i=max(0.15,0.25*g_reference,Q95(|d_acceptable|))` seconds. Keep saturation widths fixed initially. Validation checks false alarms and severity ordering; any tuned policy receives a new version and freezes before test. Report sparse calibration cells and use conservative abstention instead of claiming a learned universal norm.

## Penalties and overall score

Per observation, `excess_i=max(0,|d_i|-tau_i)` and `penalty_i=min(1,excess_i/b_i)`. The sign remains in evidence even though magnitude determines the penalty. `score_dimension=100*(1-sum(a_i*penalty_i)/sum(a_i))`, with `a_i` equal to reference phrase duration for rate/energy/pitch, and equal to 1 for each eligible pause boundary. This makes dimensions bounded and the calculations auditable. Overlapping display regions do not create extra score observations.

Coverage is eligible observation weight divided by total expected observation weight for that dimension. Emit a dimension score only if coverage >=0.8 and at least two eligible phrases (rate/energy/pitch) or five eligible gaps (pauses) exist. Short clips can have evidence without a score. Never treat missing evidence as a perfect result. Overall `S=sum(w_d*S_d)` only when all four dimensions qualify, with weights summing to one; otherwise `overall_score=null` and report available dimensions and missing reasons. Do not silently reweight dimensions.

No confidence multiplier improves a score. Quality/confidence affects eligibility and presentation, not a bonus/penalty disguised as performance. Rubric versions include all tolerances, masks, dimension weights, aggregation and eligibility rules.

## Grounding and explanation

A qualifying observation is flagged when `excess>0`. Rate/energy/pitch regions span the matched participant phrase; their precision is phrase-level, never a fabricated frame-exact onset. Pause regions span an extra/long pause; a shortened/missing pause anchors to neighboring participant word boundaries and includes the corresponding reference gap. Store the boundary anchor distinctly from silence. All region bounds satisfy `0<=start<end<=duration`; if an anchor collapses, report a boundary event rather than inventing a nonzero interval.

Merge adjacent same-dimension phrase flags only when separated by <=200 ms and no intervening valid unflagged phrase. Preserve child observation IDs and their individual evidence; do not merge unrelated dimensions. Evaluation reports phrase-region detection separately from pause-event timing. Ground truth can be finer than the detector; publish the resulting limitation.

Each explanation is assembled from computed evidence: transcript span, native/reference intervals, dimension, unit, both measured values, signed delta, tolerance, normalized excess, rubric version and reliability. The review instruction is specific to the measured difference (for example, replay the flagged pause boundary and compare the reference gap). Labels or waveform highlights never come from demonstration constants or dataset recipe windows at runtime. Explain the acoustic trigger, not an unobserved human cause.

## Confidence, uncertainty and evaluation

Initial reliability states: `reviewed` (human-checked relevant alignment/evidence), `automatic` (all checks passed, not manually checked), `limited` (some usable evidence with warnings), `unavailable` (insufficient evidence). They are evidence categories, not calibrated probabilities. Show alignment coverage, pitch-valid fraction, quality flags and thresholds alongside them. Numeric timing uncertainty remains null until a reviewed benchmark supports a bound; display annotation uncertainty separately from engine uncertainty. Do not display arbitrary "95% confidence" on an individual score.

Evaluation uses sealed human labels from the [dataset plan](dataset-plan.md):

- Alignments: median/p90 absolute word-start/end error, coverage, failures and annotation uncertainty; no removal of failed cases from the denominator without reporting them.
- Regions: temporal IoU `intersection_duration/union_duration`; within each recording and dimension maximize eligible one-to-one match cardinality, then total IoU (ID-sorted solver ties under pinned SciPy; matching-v2), with main threshold 0.5 and sensitivity at 0.3/0.7. Report precision/recall/F1, unmatched predictions/labels and matched boundary errors. Use boundary tolerance +/-200 ms for missing-pause events, separately from interval IoU. Publish false flags/minute on reviewed clean spans and near-perfect examples.
- Severity: per-dimension Spearman rank agreement with adjudicated ordinal severity and synthetic parameter-order checks, reported separately. These are association checks, not proof of rhetorical quality. Report ties, sample counts and undefined metrics explicitly.
- Acoustic fixtures: known sinusoids, amplitude envelopes and inserted silences test F0, energy, FFT scaling and timing; boundary/gain/register stress tests probe invariance. Fixtures are test inputs, never product outputs or real-speech dataset claims.
- Repeatability: identical decisions and scores within `1e-6` on the same locked environment; cross-environment numeric tolerance initially `1e-4`, with every threshold-induced decision difference investigated. Store full precision, round only for display.

Report failure/abstention rates and results by origin/dimension/severity/family. Compute 1000 family-level bootstrap resamples with a recorded seed for metric uncertainty; three held-out families are too few for strong statistical conclusions, and an interval is not a guarantee. When an entire resample has no positives, keep its metric undefined and report the count. No accuracy result or gate attainment is claimed in Phase 0.

## Phase 3 implementation notes

The executable [contracts and CLI](comparison-engine.md) implement the formulas above without changing dimension weights, saturation widths or score gates. The [validation report](verification.md) records checks actually executed. No real human-reviewed accuracy result exists.

Small clarifications: all reviewed phrases remain in the expected reference-duration denominator even if too short/unusable; eligibility cannot improve by deleting missing observations. Complete observed frame supports must cover >=80% of a region; pitch additionally needs >=50% reliable frames. Two independent agreeing timing/phrase reviews are required, with median reviewed word boundaries and retained originals. A missing/short pause is a boundary event with null participant interval and an actual word-end anchor; no zero-width or invented silence interval is published. These clarify the existing evidence/grounding policy rather than weaken it.

Normalized deviation is signed `d/tau`; normalized excess is represented by `penalty=min(1,excess/b)`. The measured feature unit for pacing remains words/min while its delta/tolerance/width are natural-log rate ratios, explicitly named in explanations. Initial engineering severity bins are penalty <=1/3, <=2/3 and >2/3, distinct from independently listened human severity.

Word-median sustained-energy (>6 dB), energy-step residual (>6 dB), and pitch-contour residual (>3 semitones) detectors add evidence about contour placement. Their exact gates are in the guide. They are versioned, unvalidated hypotheses and **do not add score penalties**: energy and pitch rubric scores remain Q90-Q10 excursion agreement. Thus a changed emphasis can trigger review while range scores remain unchanged; the report does not conceal that limitation. No arbitrary new overall quality score was introduced.

Calibrated tolerances require a new policy version and cannot be below their initial values. The optional pause training-Q95 floor is `pause_calibrated_tolerance_s`, initially zero. Frozen policy metadata identifies calibration/validation groups and evidence; evaluation audits group assignments and rejects overlap. No data-dependent calibration is claimed without reviewed examples. Comparisons use categorical eligibility and null detection confidence/timing uncertainty, never a made-up probability.

Evaluation implements category/time one-to-one matching, separate pause events, per-severity counts, FP/FN IDs, matched boundary errors, clean-span false flags/minute, defined-only Spearman and seeded family bootstrap. Missing/unresolved human labels withhold metrics. Software-fixture and synthetic-origin runs cannot establish independent real validation. Full human held-out acceptance additionally requires three independent groups, a frozen policy, valid reviewed labels and explicit failure/abstention reporting.

Floating-point clarification: a fixed `1e-12` absolute numerical epsilon treats a delta at its tolerance as zero excess, and stabilizes coverage/severity boundary comparisons. This is roundoff handling in the stated units, not a perceptual margin or measurement uncertainty; full measured deltas remain exported. An exact-tolerance tempo fixture verifies no spurious flag.
