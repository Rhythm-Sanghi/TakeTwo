# TakeTwo

Speech analysis workspace

Technical report | Track C | 15 October 2026 | Application release 9938bd8

## 1. Problem, scope and acceptance

TakeTwo compares reference and participant recordings of the same words, preserves their native audio timelines, and explains measured delivery deviations. Its objective is reproducible agreement with a selected reference, not persuasion, emotion, speaking ability or a psychological diagnosis. A stylistic difference can be intentional and effective.

The local Windows workstation implements provenance-aware imports, contrastive pairing, CPU forced alignment, FFT/MFCC/energy/pitch extraction, reviewed phrase correspondence, temporal regions, an explainable rubric and separate-label evaluation. Five functional areas cover recording import, analysis, evidence, human review, and dataset/evaluation. Workshop + Gridline + Studio Utility uses restrained colors, precise grids, system typography and functional controls.

Current acceptance is partial. Five genuine private same-person practice takes and two archival JFK masters exist locally. None has independent transcript/timing/flaw ground truth suitable for claimed real detection accuracy. Public-release consent for the private takes is absent. Public paired dataset and video remain missing; successful processing and software tests do not close these gates.

Public master is 9938bd8, verified against the fetched remote. Its Windows Actions run 38615636707 was in progress when this report was prepared. The earlier passing cd2abe9 run is historical evidence, not certification of this release. Final publication documentation and this PDF await owner approval.

Exploratory Speech Analysis provides descriptive summaries, measured energy/activity candidates, provisional same-text word differences and alignment-gap diagnostics. Comparative-insights-v1 groups compatible windows without discarding originals. Native A/B replay and searchable Summary/Full Evidence exports support inspection. A measured 2.890 s automatic gap had zero low-energy support: the app requests inspection rather than declaring silence. These observations do not approve text, timing, flaws or delivery scores.

Official judging weights are Data Engineering & Stress Testing 30%, Causal Explainability & Temporal Grounding 25%, Feature Extraction 20%, Visualization & Dashboard 15%, and Reproducibility & Code Quality 10%. Deliverables include public code, public paired audio/text/alignment labels, an interactive prototype, a report of at most six pages and a 3-10 minute YouTube demonstration [1].

OpenAI Codex extensively assisted implementation, tests, integration and documentation. ChatGPT assisted planning, architecture, interpretation and review. Humans supplied the actual recordings; independent human annotations remain separate requirements.

<!-- pagebreak -->

## 2. Dataset construction and provenance

The five private 48 kHz mono PCM16 takes form one controlled speech family: reference 30.224375 s, natural 30.590 s, slow 40.590 s, uneven 29.370 s and near-perfect 31.760 s. The supplied technology passage has 71 canonical words. Same-speaker identity and intended text are owner assertions, not independently verified labels. Filenames describe acquisition intent; no severity or detected interval is inferred from them.

Acquired public-speech masters are JFKWHA-001 (1961 inaugural) and JFKWHA-190-002 (1963 American University), with item-specific rights evidence, URLs and master hashes in the acquisition ledger [2]. Both share JFK's voice and one connected speaker group. The existing imported 17.3 s salutation remains an unverified integration candidate, not a substantive rhetorical baseline. The earlier acquisition audit rechecked the American University Public Domain statement; its inaugural fetch returned 403. This pass retains that evidence without claiming fresh rights clearance.

The smallest practical competition pilot is a permitted substantive public-speech excerpt plus same-text near-perfect, mild, moderate and severe mirrors. These new reviewed mirrors do not yet exist. Prefer genuine separate takes with explicit consent. Track C also permits declared synthesis/modification; such controls retain synthetic origin, recipes and sample time maps and cannot be described as real participant performances. All claimed ground truth still requires independent listening and temporal annotation.

Two people independently verify every word, repetition and cut edge. Reviewed text enters an explicit new dataset version; alignment/features are regenerated. Two timing reviews inspect every word and complete phrase partition. Two blinded flaw inventories retain full listened coverage, category, interval or pause anchor, severity, rationale and uncertainty. Disagreements and superseding revisions remain immutable; an operator note cannot confer approval.

Originals remain unchanged. Canonical derivatives are mono 16 kHz, without silence trimming, denoising or automatic loudness correction. Metadata binds audio/sample/text hashes, recording conditions, speaker/family, provenance and per-item rights. Identity mappings and consents remain private. Connected groups join speakers, works/text, lineage, hashes and pairs before splitting. One-family results are pilot-only; full held-out acceptance requires independent groups and a separately frozen calibrated policy. No public dataset has been released.

<!-- pagebreak -->

## 3. Architecture and acoustic extraction

Python 3.11/FastAPI/Uvicorn/Pydantic exposes typed loopback HTTP contracts. NumPy, SciPy, librosa and soundfile process actual samples; scikit-learn is transitive, with no trained classifier. SQLite persists jobs and supervised review lifecycle. Scientific authorities are immutable JSONL manifests and hash-addressed alignment/features/review/report artifacts. React, strict TypeScript, Vite and uPlot render the five workspace areas. No CUDA, paid inference or mandatory cloud service is required.

Unexpected worker exceptions retain private traces capped at 32 KiB; public errors omit their sensitive details. Log-storage failures do not replace the original processing error. Diagnostic logs are excluded from release candidates.

Windows Job Objects contain one disposable CPU worker, with single-thread numerical pools, 4 GiB aggregate commit, at most 16 worker-tree processes and a 600 s job deadline. Queueing, cancellation, crash recovery and integrity-checked caching remain unchanged. Interrupted jobs fail without automatic requeue; cleanup removes only owned managed temporary paths. Uploads support WAV/FLAC to 100 MiB and 600 s. Analysis defaults to 45 s per member; TAKETWO_MAX_ANALYSIS_DURATION_S accepts 1-45. Longer sources require explicit excerpts with exact text and retained offsets.

Native CPU MFA 3.3.9 uses the isolated locked Windows environment and checksummed English US ARPA model/dictionary v3.0.0. Each recording aligns independently against canonical words. OOV words and invalid/partial intervals are explicit failures or review states; there is no evenly spaced fallback. Automatic alignment can fit wrong words and never verifies a transcript.

Energy uses complete 400-sample unweighted RMS frames, hop 160: RMS=sqrt(mean(x^2)); E=20*log10(max(RMS,1e-6)) dBFS. STFT uses periodic Hann weighting and a 512-point real FFT; P=abs(FFT(w*x))^2/sum(w^2). One-sided total power doubles interior bins and divides by 512. MFCCs use 40 Slaney mel bands over 0-8000 Hz, natural-log floor 1e-10 and 13 orthonormal DCT-II coefficients. Centroid/MFCCs aid inspection, not validated vocal-clarity scoring.

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

Ground truth uses exact-inventory-v1. Semantic listening agreement alone cannot select authoritative boundaries: even 0-1 s versus 0.2-1.2 s changes a 0-0.5 s prediction's match at IoU 0.5. Differing numerical inventories withhold metrics until explicit same-reviewer revisions agree. Canonical label IDs derive from pair/content, excluding source IDs/prose; original reviews, hashes and adjudication history remain intact. No averaging or operator note creates independent agreement.

Evaluation retains category/severity counts, FP/FN identities, matched median/p90 boundary errors, clean-span false flags/minute, defined-only severity Spearman and seeded family bootstrap (1000 resamples, seed 17). Current genuine reviewed recordings/families: zero; real detection and timing metrics remain unavailable. A one-family pilot cannot establish held-out generalization.

The final local hardening pass executed 376 Python tests, 81 frontend tests, 18 generated browser tests and 3 private genuine-pilot tests, with zero failures/skips in the final runs [5]. Type/build/lint, lock, repository, package/history and dependency audits passed. Earlier failed attempts remain documented. Generated-signal tests verify software; genuine browser processing does not establish listening acceptance or detection accuracy.

The fresh five-recording genuine browser pilot took 237.640 s; reference/participant MFA stages took 116.671/91.219 s, feature extraction 15.297/11.375 s, comparison 1.328 s, and peak worker-tree commit was 2,081,546,240 bytes [6]. Cold comparison loading took 29.431 s on the measured host; individual 15 s evidence requests can still time out under contention. A reproduced Windows Proactor accept-socket failure led to Selector-loop startup; duplicate cold artifact reads were serialized without weakening identity validation. No general latency, clean-machine compatibility or scientific accuracy guarantee follows.

Reproducibility binds audio/sample/text, data version, model/dictionary, config, policy, implementation, review and artifact hashes. Native 200% Chromium tab zoom passed locally; responsive/axe checks are separate from heard Narrator/NVDA acceptance, which remains open. Public paired dataset, eligible genuine-flaw demonstration, public YouTube video and final submission remain incomplete. MIT copyright (c) 2026 Rhythm Sanghi covers original code/documentation only; private data and external resources retain separate rights.

References: [1] requirments/Track C.pdf, unchanged official statement and deliverables. [2] docs/pilot-collection.md; JFK Library JFKWHA-001/JFKWHA-190-002. [3] docs/scoring-policy.md. [4] docs/pitch-investigation.md; scripts/inspect_pitch.py. [5] docs/final-hardening-completion.md; github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38615636707 (pending at preparation). [6] docs/windows-hardening-evidence.md. MFA English US ARPA v3.0.0, CC BY 4.0; full notices: docs/attributions.md.
