# TakeTwo

Current-status addendum (2026-10-13): five genuine private same-person practice recordings and intended text are available, with no independent transcript/timing/flaw ground truth or public-release consent. MIT is owner-selected, copyright (c) 2026 Rhythm Sanghi, for original code/documentation only. Current software corrections and evidence are in [final repair audit](final-repair-audit.md). The dated Phase 5 statements and existing six-page PDF below remain historical; the final submission PDF still needs owner reconciliation and regeneration. OpenAI Codex was extensively used for implementation/testing/integration/documentation; ChatGPT assisted architecture, interpretation, technical review and instructions.

Historical evidence: limits and measurements below describe that recorded release. Current duration policy and measurements are in [duration validation](duration-validation.md).

Speech analysis workspace

Technical report draft | Track C | 2026-10-12 | Software baseline 9551d73

## 1. Problem and objective

Competitive speech delivery assessment often blends acoustic observations with subjective judgments. TakeTwo compares performances of the same spoken text and exposes measured differences, their native-time locations and the calculations that trigger review. The objective is reproducible delivery agreement with a selected reference, not a universal score for persuasion, emotion or speaking ability.

The local workstation implements dataset import and provenance, contrastive pairing, CPU forced alignment, acoustic extraction, reviewed correspondence, threshold-based regions, rubric reports and independent-label evaluation. Its React interface supports real audio/text uploads, waveform playback/seek, feature inspection, evidence, job history and JSON/CSV export. The Workshop + Gridline + Studio Utility design uses restrained colors, precise grids, system typography and functional controls.

Acceptance is partial. Genuine archival reference processing has executed, but no consented participant recordings or independent transcript/timing/flaw reviews are available. Human detection accuracy, boundary accuracy, calibration and speaker generalization are unavailable. Synthetic signals verify software behavior and do not constitute a speech corpus. This draft does not claim a completed hackathon submission.

Official priorities are Data Engineering & Stress Testing 30%, Causal Explainability & Temporal Grounding 25%, Feature Extraction 20%, Visualization & Dashboard 15%, and Reproducibility & Code Quality 10%. These judging weights are separate from the equal-weight delivery rubric. The official deliverables include public code, a public paired dataset, a prototype, a report of at most six pages and a 3-10 minute YouTube video.

Evidence references: unchanged official statement at requirments/Track C.pdf; docs/submission-compliance.md; docs/phase4b-validation.md; docs/phase5-validation.md. This editable source generates the accompanying PDF; historical measurements are explicitly attributed to their phase.

<!-- pagebreak -->

## 2. Contrastive dataset methodology

Two genuine source masters were acquired in Phase 1B: JFKWHA-001, the 1961 inaugural address, and JFKWHA-190-002, the 1963 American University address. Item-specific public-domain evidence and master hashes are recorded in docs/pilot-collection.md. Both share JFK's voice and form one connected speaker group. They cannot establish independent train/test speaker coverage.

One 17.3 s salutation candidate is imported in local-data/pilot-v2 as r-478a9405c1b10a75fda31972. Its canonical WAV SHA-256 is a342f051ea3b4ae23a40d293264bdee3946be235cb73c77e7e582c65dc873bc8. Its archive-derived transcript remains unverified; the salutation is useful for integration but lacks substantive rhetorical range. There are zero consented human mirrors and zero independent review records. No paired dataset has been published.

Collection prioritizes substantive 15-25 s excerpts and a second source speaker before scale. Two humans verify every spoken word and cut edge. Consenting adults separately record natural, near-reference, mild, moderate and severe intended departures using identical words and fixed recording conditions. Intent does not determine reviewed severity. Acceptable alternative deliveries are required negatives. Names, signatures and identity mappings remain private; public metadata uses permitted pseudonyms.

Originals are immutable. Canonical analysis audio is mono 16 kHz with the original time origin; there is no silence trimming, denoising or automatic loudness correction. Channel cancellation, clipping, silence and finite samples are checked. Source, self-recorded and synthetic origins remain distinct. Controlled synthetic edits preserve recipe, software/seed, hashes and piecewise sample time maps; edit support is not perceptual ground truth.

Two independent blinded flaw reviewers annotate full native listening coverage, intervals or missing-pause anchors, severity, rationale and uncertainty. Timing reviews cover every word and a complete phrase partition. Original disagreements and superseding reconciliations are retained. Connected groups join family, source/work/text, speakers, hashes, pairs and lineage before splitting. Real imports after freezing require a new dataset version. A compact pilot is preferable to invented coverage; full held-out acceptance requires disjoint train/validation groups and at least three independent test groups.

<!-- pagebreak -->

## 3. Architecture and signal processing

Python 3.11 with FastAPI/Uvicorn/Pydantic provides typed local HTTP contracts. NumPy/SciPy/librosa/soundfile operate on actual audio. SQLite persists job lifecycle/history; the immutable JSONL manifest and content-addressed analysis/comparison JSON remain scientific authorities. React, strict TypeScript, Vite and uPlot render the four workspace areas. Model/config paths are operator-controlled startup inputs. Processing requires no CUDA or paid inference service.

Native CPU MFA 3.3.9 runs in an isolated locked Windows environment with Kaldi and checksummed English US ARPA model/dictionary v3.0.0. The loopback service launches one disposable CPU worker with three queue slots and single-thread numerical pools. Windows kill-on-close Job Objects cap the worker tree at 4 GiB aggregate commit and 16 processes. Kernel leases and startup recovery mark interrupted jobs failed without requeueing, preserve originals/complete artifacts and clean only checked managed temporary paths.

Ingestion accepts WAV/FLAC up to 100 MiB and 600 s; analysis remains capped at 30 s. A 16 kHz native timeline is shared by stored samples, intervals and envelopes. Waveforms use real min/max samples. Energy uses 400-sample frames with a 160-sample hop: RMS=sqrt(mean(x^2)); E=20*log10(max(RMS,1e-6)) dBFS. This is digital level, not sound pressure.

The periodic-Hann STFT uses 400 samples and a 512-point real FFT. Power is abs(FFT(w*x))^2/sum(w^2); one-sided total power doubles interior bins and divides by 512. MFCCs use 40 Slaney mel bands over 0-8000 Hz, natural-log power floor 1e-10 and the first 13 orthonormal DCT-II coefficients. Spectral centroid/MFCCs support inspection; they do not prove vocal clarity.

pYIN uses 1024-sample frames, hop 160, 60-500 Hz and probability at least 0.8. Only reliable finite voiced F0 is accepted. Relative pitch is 12*log2(F0/median(valid_F0)); relative energy subtracts the active-energy median. No variance normalization hides monotony. Raw baselines, masks, complete-window support and distinct frame clocks are retained. Gain/register invariance has fixture evidence; arbitrary speaker/microphone invariance is unmeasured.

<!-- pagebreak -->

## 4. Alignment and temporal grounding

Each recording is independently forced-aligned against canonical words. Original text and token offsets remain available; dictionary coverage and spoken-form replacements are explicit. Unknown words, omissions and malformed intervals cause failure or review states. There is no evenly spaced fallback, guessed pronunciation or synthetic timestamp substitution. Automatic words/phones must be chronological, nonoverlapping and within native recording bounds.

Successful alignment is not transcript verification. A complete alignment can fit wrong words. Two distinct independent timing reviews bind the original alignment payload hash and exact provenance. Every canonical word and phrase partition must be checked; disagreements exceeding 200 ms or unresolved decisions block correspondence. Agreed median boundaries support manually assisted comparison. They do not provide an independent benchmark of the original MFA output.

Phrase pacing compares the same word count over each member's native duration. Pauses are consecutive-word gaps of at least 150 ms corroborated by complete low-energy frames; leading/trailing silence is not an inter-word penalty. Raw phrase/gap durations remain visible. No unrestricted warping erases duration differences, and unrelated frame-array positions are never treated as correspondence.

Detections identify native participant intervals and independently corresponding reference intervals. Phrase rate/energy/pitch flags have phrase-level resolution. Extra/long pauses have actual silence intervals; missing/short pauses use real boundary anchors with null participant intervals. Adjacent same-dimension phrase flags merge only across at most 200 ms with contiguous tokens and no intervening unflagged phrase. Child observations remain inspectable.

Complete frame support must cover at least 80% of the reviewed span; pitch also requires at least 50% reliable voiced frames in both members. Clipped or unreliable spans are withheld. Evidence-only sustained-energy/energy-step and word-pitch-contour detectors use versioned thresholds; they do not add penalties to the four rubric dimensions. Every explanation binds location, feature/unit, both measurements, signed delta, tolerance, excess, penalty and a replay suggestion. It explains a calculation, not anxiety, intention or a proven human cause.

<!-- pagebreak -->

## 5. Scoring and explainability

Policy delivery-v0 remains unchanged and uncalibrated. Each dimension has weight 0.25. Initial tolerances and saturation widths are engineering hypotheses, not validated perceptual limits. Any evidence-supported change requires a new policy version; held-out labels must never tune thresholds.

Pacing uses d=ln(rate_participant/rate_reference), tolerance ln(1.15), width ln(1.5). Pause behavior uses d=gap_participant-gap_reference seconds, tolerance max(0.15,0.25*gap_reference), width 0.75 s. Energy variation uses the participant-minus-reference difference in Q90-Q10 normalized active-energy excursion, tolerance 3 dB, width 6 dB. Pitch dynamics uses the corresponding reliable relative-pitch excursion difference, tolerance 2 semitones, width 4 semitones. Quantiles use linear interpolation.

For observation i: excess_i=max(0,abs(d_i)-tolerance_i); penalty_i=min(1,excess_i/width_i). Dimension score=100*(1-sum(weight_i*penalty_i)/sum(weight_i)). Phrase weights are reference durations; pause boundaries have unit weight. Signed deviation and original measurements remain visible. Display-region merging never adds score weight. A 1e-12 arithmetic epsilon stabilizes exact threshold comparisons; it is not measurement uncertainty.

All expected observations remain in the coverage denominator, including unusable short phrases. A dimension requires coverage at least 0.8 and at least two eligible phrases or five eligible pause boundaries. Phrases need at least three words and 0.5 s. Overall agreement is the four-weight sum only when every dimension qualifies. Missing dimensions remain null; weights are never redistributed. Quality/uncertainty affects eligibility, not an invented confidence bonus.

Detector severity bins reflect normalized penalty thirds and remain separate from human ordinal severity. Relative excursion can miss misplaced emphasis; additional contours support review without silently changing range scores. A stylistic difference may be acceptable. Region confidence and engine timing uncertainty remain null until measured. pYIN probability is not flaw confidence.

Future calibration may increase tolerance to the Q95 absolute residual of reviewed acceptable training pairs, with fixed initial floors and widths. Validation groups then freeze a separately versioned policy before sealed testing. No such calibration data exists. Current genuine-source scoring correctly abstains because the pair, verified text, independent timing and reliable pitch are missing.

<!-- pagebreak -->

## 6. Evaluation, limitations and reproducibility

Phase 5 reran all 217 Python tests, including five Windows recovery tests, with one existing Starlette/httpx deprecation warning. All seven frontend tests passed. Tests use analytic arrays/generated signals and test-only review assertions; their scores and matching fixtures are not real-speech accuracy. Exact current commands, browser checks and repository audit findings are retained in docs/phase5-validation.md.

Historical Phase 4B genuine browser evidence: 17.3 s source, 19 automatic word intervals/115 phones, 1,728 spectral frames and 1,724 pitch frames. Accepted pitch fraction was 0; all scores were null and no regions were claimed. The uncached processing job took 187.422 s; cached reuse took 8.859 s. Worker-tree peak commit was 1,892,315,136 bytes. Whole browser-tree sampled working set was 2,772,697,088 bytes at 100 ms sampling, a lower bound that may double-count shared pages. These are one-source operational observations, not paired capacity guarantees.

The real evaluator with no pairs/reviews reports zero paired reports, zero families, independent_real_validation=false and null metrics with missing-report/split reasons. Independent word-boundary error, human detection F1, severity association, clean-span false flags, cross-speaker fairness and calibration remain unavailable. Zero regions during abstention does not mean zero errors.

Implemented evaluation performs one-to-one category-specific interval matching at IoU 0.5 (sensitivity 0.3/0.7); missing-pause events use a separate 200 ms tolerance. Outputs retain P/R/F1, boundary median/p90, category/severity counts, FP/FN IDs, clean-reviewed-time denominators and defined-only severity Spearman. Family bootstrap uses 1,000 resamples and seed 17, reporting undefined resamples. Human/synthetic origins are separate; missing/unresolved reviews withhold metrics. Full held-out validation requires a frozen policy and independent test groups.

Reproduction binds audio/sample/text, review, configuration, policy, implementation, lock and model/dictionary hashes. Same-Windows feature replay is verified; second-environment equivalence remains open. Run commands in docs/reproducibility.md and keep all failure/abstention artifacts. Actual 200% browser zoom and heard screen-reader output remain unverified; responsive/axe checks do not replace them. Historical public-address audio has weak pitch coverage; reference-style bias, difficult alignment, short-word support, small corpora and authenticated reviewer independence remain risks.

Attribution: JFK/White House Audio Collection/JFK Presidential Library, Commons inaugural copy; MFA model/dictionary authors Michael McAuliffe and Morgan Sonderegger, CC BY 4.0. Dependency/source notices are in docs/attributions.md. Codex assisted implementation, documentation and verification under human direction; no human data or approvals were fabricated. Public paired dataset, video, final owner release and submission receipt remain absent. Source-code license selection remains an owner action.
