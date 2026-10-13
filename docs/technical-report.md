# TakeTwo

Speech analysis workspace

Technical report draft | Track C | 13 October 2026 | Published baseline 35a1486 plus local CI repair

## 1. Problem, scope and acceptance

TakeTwo compares reference and participant recordings of the same words, preserves their native audio timelines, and explains measured delivery deviations. Its objective is reproducible agreement with a selected reference, not persuasion, emotion, speaking ability or a psychological diagnosis. A stylistic difference can be intentional and effective.

The local Windows workstation implements provenance-aware imports, contrastive pairing, CPU forced alignment, FFT/MFCC/energy/pitch extraction, reviewed phrase correspondence, temporal regions, an explainable rubric and separate-label evaluation. Five functional areas cover recording import, analysis, evidence, human review, and dataset/evaluation. Workshop + Gridline + Studio Utility uses restrained colors, precise grids, system typography and functional controls.

Current acceptance is partial. Five genuine private same-person practice takes and two archival JFK masters exist locally. None has independent transcript/timing/flaw ground truth suitable for claimed real detection accuracy. Public-release consent for the private takes is absent. Public paired dataset and video remain missing; successful processing and software tests do not close these gates.

The three audited source repairs are public on master at 35a1486. Its first GitHub Windows run failed three startup tests because frontend installation/build occurred after pytest. A fresh local checkout reproduced those failures; building the frontend first restored those cases; the final suite passes 301 Python tests. New repairs and this report require owner authorization before publication. Remote CI is still red until an authorized repair push is actually verified.

Official judging weights are Data Engineering & Stress Testing 30%, Causal Explainability & Temporal Grounding 25%, Feature Extraction 20%, Visualization & Dashboard 15%, and Reproducibility & Code Quality 10%. Deliverables include public code, public paired audio/text/alignment labels, an interactive prototype, a report of at most six pages and a 3-10 minute YouTube demonstration [1].

OpenAI Codex extensively assisted implementation, tests, integration and documentation. ChatGPT assisted planning, architecture, interpretation and review. Humans supplied the actual recordings; independent human annotations remain separate requirements.

<!-- pagebreak -->

## 2. Dataset construction and provenance

The five private 48 kHz mono PCM16 takes form one controlled speech family: reference 30.224375 s, natural 30.590 s, slow 40.590 s, uneven 29.370 s and near-perfect 31.760 s. The supplied technology passage has 71 canonical words. Same-speaker identity and intended text are owner assertions, not independently verified labels. Filenames describe acquisition intent; no severity or detected interval is inferred from them.

Acquired public-speech masters are JFKWHA-001 (1961 inaugural) and JFKWHA-190-002 (1963 American University), with item-specific public-domain evidence, URLs and master hashes in the acquisition ledger [2]. Both share JFK's voice and one connected speaker group. The existing imported 17.3 s salutation remains an unverified integration candidate, not a substantive rhetorical baseline. The American University item's Public Domain statement was rechecked; the inaugural item fetch returned 403 on this pass, so prior evidence is retained without claiming a fresh verification.

The smallest practical competition pilot is a permitted substantive public-speech excerpt plus same-text near-perfect, mild, moderate and severe mirrors. These new reviewed mirrors do not yet exist. Prefer genuine separate takes with explicit consent. Track C also permits declared synthesis/modification; such controls retain synthetic origin, recipes and sample time maps and cannot be described as real participant performances. All claimed ground truth still requires independent listening and temporal annotation.

Two people independently verify every word, repetition and cut edge. Reviewed text enters an explicit new dataset version; alignment/features are regenerated. Two timing reviews inspect every word and complete phrase partition. Two blinded flaw inventories retain full listened coverage, category, interval or pause anchor, severity, rationale and uncertainty. Disagreements and superseding revisions remain immutable; an operator note cannot confer approval.

Originals remain unchanged. Canonical derivatives are mono 16 kHz, without silence trimming, denoising or automatic loudness correction. Metadata binds audio/sample/text hashes, recording conditions, speaker/family, provenance and per-item rights. Identity mappings and consents remain private. Connected groups join speakers, works/text, lineage, hashes and pairs before splitting. One-family results are pilot-only; full held-out acceptance requires independent groups and a separately frozen calibrated policy. No public dataset has been released.

<!-- pagebreak -->

## 3. Architecture and acoustic extraction

Python 3.11/FastAPI/Uvicorn/Pydantic exposes typed loopback HTTP contracts. NumPy, SciPy, librosa and soundfile process actual samples; scikit-learn is transitive, with no trained classifier. SQLite persists jobs and supervised review lifecycle. Scientific authorities are immutable JSONL manifests and hash-addressed alignment/features/review/report artifacts. React, strict TypeScript, Vite and uPlot render the five workspace areas. No CUDA, paid inference or mandatory cloud service is required.

Windows Job Objects contain one disposable CPU worker, with single-thread numerical pools, 4 GiB aggregate commit, at most 16 worker-tree processes and a 600 s job deadline. Queueing, cancellation, crash recovery and integrity-checked caching remain unchanged. Interrupted jobs fail without automatic requeue; cleanup removes only owned managed temporary paths. Uploads support WAV/FLAC to 100 MiB and 600 s. Analysis defaults to 45 s per member; TAKETWO_MAX_ANALYSIS_DURATION_S accepts 1-45. Longer sources require explicit excerpts with exact text and retained offsets.

Native CPU MFA 3.3.9 uses the isolated locked Windows environment and checksummed English US ARPA model/dictionary v3.0.0. Each recording aligns independently against canonical words. OOV words and invalid/partial intervals are explicit failures or review states; there is no evenly spaced fallback. Automatic alignment can fit wrong words and never verifies a transcript.

Energy uses 400-sample Hann frames, hop 160: RMS=sqrt(mean(x^2)); E=20*log10(max(RMS,1e-6)) dBFS. STFT uses a 512-point real FFT; P=abs(FFT(w*x))^2/sum(w^2). One-sided total power doubles interior bins and divides by 512. MFCCs use 40 Slaney mel bands over 0-8000 Hz, natural-log floor 1e-10 and 13 orthonormal DCT-II coefficients. Centroid/MFCCs aid inspection, not validated vocal-clarity scoring.

pYIN uses 1024-sample frames, hop 160, 60-500 Hz, center=False and finite voiced F0 with probability >=0.8. Frame centers and complete-window support are preserved; pitch and spectral arrays are not joined by index. Relative pitch is 12*log2(F0/median(valid F0)); relative energy subtracts the active-energy median. No per-recording variance normalization erases dynamics. Gain/register fixtures support these transformations; arbitrary speaker/microphone invariance is unmeasured.

<!-- pagebreak -->

## 4. Human evidence and temporal grounding

The supervised local Review Workspace provides playback, exact text edits, numeric/native-word boundary correction, phrase partitioning, flaw CRUD, saved drafts and scientific JSON export/import. Recording-scoped capabilities and a private operator key control sequential handoff. During handoff, general analysis and peer-evidence APIs close. Cookies are HttpOnly/SameSite=Strict on loopback HTTP; resume rotates capabilities. Typed reviewer IDs do not authenticate humans, prove independence or defeat the trusted OS owner.

Transcript approvals remain separate from original machine evidence. Explicit reviewed-version import and regenerated artifacts are required before new timing reviews; old approvals cannot be copied to new hashes. Timing consensus requires distinct independent approved reviewers, equal token inventories/phrase partitions and boundary differences no greater than 200 ms; median checked boundaries define correspondence.

Semantic-v2 flaw agreement compares exact category, severity and uncertainty, equal listened-span unions, like interval/event types, and complete one-to-one label matches. Interval boundaries must be within 200 ms and IoU >=0.5; anchors within 200 ms. UUIDs/listening segmentation and independently worded rationale do not determine numerical agreement. Null uncertainty is unknown, unlike explicit zero. Exact uncertainty equality is conservative and uncalibrated; disagreement requires revision/adjudication, not silent tolerance expansion. Every pair of active reviewers must agree, preventing transitive chains.

Durable SQLite publication intent pins review identity, timestamp and draft hash. A fsynced staging file is atomically linked without replacement to immutable evidence. Restart reconciles pending intents and verifies hashes; retry returns one logical submission. Corrupt/contradictory artifacts and legacy orphans fail closed. Actual process-kill regressions cover both sides of publication. This establishes process-crash recovery, not power-loss durability.

Phrase rate compares equal word counts on native durations. Pauses are aligned inter-word gaps >=150 ms corroborated by complete low-energy frames. Leading/trailing silence is recording quality, not a pause penalty. Phrase flags declare phrase-level resolution. Extra/long pauses have real intervals; shortened/missing pauses use boundary anchors rather than invented silence. Adjacent compatible flags merge only within 200 ms with no intervening unflagged phrase. Each region links native/reference positions, measurements, units, signed delta, tolerance, excess and a replay action; no inferred psychological cause is claimed.

<!-- pagebreak -->

## 5. Explainable rubric and pitch limitations

Delivery-v0 remains unchanged, experimental and uncalibrated. Pacing, pause behavior, energy variation and pitch dynamics each weigh 0.25. Initial tolerances are engineering hypotheses, not perceptual limits. Pacing: d=ln(rate participant/rate reference), tolerance ln(1.15), width ln(1.5). Pauses: d=gap participant-gap reference, tolerance max(0.15,0.25*reference gap), width 0.75 s. Energy: participant-minus-reference Q90-Q10 normalized excursion, tolerance 3 dB, width 6 dB. Pitch excursion: corresponding semitone difference, tolerance 2, width 4. Quantiles use linear interpolation [3].

For observation i, excess=max(0,abs(d)-tolerance), penalty=min(1,excess/width). Dimension score=100*(1-sum(a*penalty)/sum(a)). Phrase weights a are reference durations; pause boundaries have unit weight. Original signed measurements remain visible; display-region merging does not add score weight. A 1e-12 arithmetic epsilon handles roundoff, not measurement uncertainty.

Every expected observation remains in coverage denominators. Phrases need at least three words and 0.5 s; usable frame support must cover >=80%. Pitch additionally requires >=50% reliable voiced frames in both members. A dimension score needs coverage >=0.8 and two eligible phrases or five pause boundaries. Overall agreement is available only when all four dimensions qualify; unavailable weights are never redistributed. Clipping, weak alignment, missing rights/text/timing or insufficient frames withhold affected conclusions.

Pitch diagnostics on the five genuine takes found raw pYIN voiced coverage 69.3-76.4%, but accepted coverage only 0.284-0.617%. Raw medians were 119.3-123.5 Hz; probabilities were finite. Canonical recordings had no clipping, adjacent >10-semitone jumps or pYIN warnings in those runs. No calibrated noise reference or independent F0 labels exist [4].

Known 80/120/200/400 Hz sine controls yield accurate raw F0 but accepted fractions 0/0/100/100%. A diagnostic 2048-sample window improves low-frequency controls but reference acceptance reaches only 1.362%, still unusable. Gain and range probes do not solve that case. No swapped outputs, manufactured contour or NaN-to-score defect was established. Production confidence >=0.8 and null pitch values remain unchanged; no threshold was tuned to unlock the five takes.

Region confidence and engine timing uncertainty remain null until calibrated. Evidence-only contour detectors do not add rubric penalties. Future calibration requires real acceptable training pairs, validation and a separately versioned frozen policy; held-out labels cannot tune it. Acoustic association is not rhetorical quality or causal certainty.

<!-- pagebreak -->

## 6. Evaluation, verification and deliverables

Matching-v2 first maximizes eligible one-to-one match count, then total IoU/proximity, with ID-sorted rows/columns and pinned SciPy ties. Interval IoU defaults to 0.5 (sensitivity 0.3/0.7); boundary events use 200 ms and cannot match intervals. The adversarial software graph improves TP=1/FP=1/FN=1 to TP=2/FP=0/FN=0; F1 0.5 to 1.0. This is numerical regression evidence, not measured speech accuracy. Equal-quality ties are tested across 540 repeated/permuted assignments.

The evaluator retains category/severity counts, FP/FN identities, matched median/p90 boundary errors, clean-span false flags/minute, defined-only severity Spearman and seeded family bootstrap (1000 resamples, seed 17). Missing/unresolved independent labels withhold metrics. Current genuine reviewed recordings/families: zero; human TP/FP/FN, precision, recall, F1 and timing errors are unavailable, not zero. A one-family pilot cannot establish held-out generalization.

Final local Windows checkout: 301 Python tests passed, no failures/skips, one existing Starlette/httpx warning, 211.99 s. The original 296 tests remain plus five diagnostic/tie/package cases. Frontend checks and 20 unit tests passed; all three browser workflows passed, including actual 200% zoom on freshly installed Chromium 156. This verifies software and generated review assertions, not human accuracy. The published baseline Actions run remains red; the build-order correction is local pending authorized push and actual remote verification [5].

Prior genuine CPU runs on Windows 11/i7-1365U/16 GB RAM: a fresh 45 s archival excerpt plus declared synthetic control took 314.813 s, peak aggregate worker commit 2,122,432,512 bytes. A fresh genuine 30.224375/30.590 s reference/natural pair took 287.469 s, peak 2,075,697,152 bytes; both aligned 71 tokens/274 phones. Both fit unchanged 600 s/4 GiB limits; neither had human approvals or overall scores. These dated operational observations are not alignment accuracy or universal speed guarantees [6].

Reproducibility binds audio/sample/text, data version, model/dictionary, config, policy, implementation, review and artifact hashes. Native 200% Chromium tab zoom passed locally; responsive/axe checks are separate from heard Narrator/NVDA acceptance, which remains open. Public paired dataset, eligible genuine-flaw demonstration, public YouTube video and final submission remain incomplete. MIT copyright (c) 2026 Rhythm Sanghi covers original code/documentation only; private data and external resources retain separate rights.

References: [1] requirments/Track C.pdf, unchanged three-page official statement. [2] docs/pilot-collection.md; JFK Library items JFKWHA-001/JFKWHA-190-002, https://www.jfklibrary.org/asset-viewer/archives/jfkwha-190-002. [3] docs/scoring-policy.md. [4] docs/pitch-investigation.md and scripts/inspect_pitch.py. [5] docs/ci-submission-validation.md, actual GitHub run 38350507487. [6] docs/final-repair-audit.md. MFA resources: McAuliffe/Sonderegger, English US ARPA v3.0.0, CC BY 4.0; full notices in docs/attributions.md.
