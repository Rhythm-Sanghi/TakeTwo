# TakeTwo dataset plan

Status: the Phase 1 import/transformation/annotation/split/validation pipeline is implemented; see the [dataset-engineering guide](dataset-engineering.md) and [schema](dataset-schema-v1.json). Two genuine public-domain masters have now been acquired and one draft reference candidate imported; see [pilot collection](pilot-collection.md). Human mirrors, independent labels and a releasable competition corpus remain missing. Quality and public redistribution rights determine inclusion; the target below is not a claim of available data.

## Compact acquisition target

Aim for 12 independent public-speech excerpt families, each 20-60 seconds, from different source speakers and distinct speech/transcript works. Start with two rights-cleared pilot families before scaling. Choose effective public speakers with intelligible solo speech, little music and a documented human rationale for using the passage as a reference. A reference is one chosen delivery, not a universal ideal.

For each family, target one real source reference, one near-perfect human re-recording, three human flawed re-recordings (mild, moderate, severe) and two controlled synthetic alterations: up to 84 files overall. Rotate the dominant flaw among pacing, pause behavior, energy variation and pitch dynamics, balancing categories across splits as far as the small corpus permits. Coverage is reported by dimension/severity/origin; missing cells remain visible. Add more samples only to close important gaps. Separate real and synthetic evaluation tables; a strong synthetic result cannot substitute for human-delivery performance.

Acquire baseline candidates from original publisher/rights-holder archives or explicitly licensed collections. Do not assume a public web page, famous speech, government context or download button grants recording/transcript adaptation and redistribution rights. For each item obtain and archive explicit terms or permission covering the recording, words, excerpts, modifications and public release; record attribution and restrictions. Reject unresolved, no-derivative or incompatible assets. Prefer clearly reusable permissions with attribution that can be met, or direct written permission. Current item-specific acquisition evidence is in [pilot collection](pilot-collection.md); do not generalize it to other archive items. If no effective public-speaker reference can be released, that is an official dataset blocker; self-recordings alone do not silently replace R1a.

Human mirrors: recruit consenting adults to read the identical verified excerpt, with explicit permission for recording, annotation and public dataset release. Use pseudonymous speaker IDs, retain consent evidence privately and publish only permitted metadata. Recruit distinct mirror speakers for each split, with more than one mirror voice per split where feasible. Record near-perfect and deliberately altered performances without impersonation claims. Human labelers, not scripts, confirm the intended flaw is actually audible and localized.

## Transcript and audio preparation

Two reviewers compare the source transcript with the audio, retaining spoken repetitions and disfluencies. Resolve disagreement and record reviewer IDs/revision. All mirrors must contain the same canonical word sequence; reject/re-record omissions and additions rather than concealing them with alignment. Save original text, normalized English tokens, token mapping and SHA-256. Do not use an unreviewed ASR transcript as ground truth.

Preserve originals and source excerpt offsets. Record container, codec, sample rate, channels and duration. Normalize an analysis derivative to mono 16 kHz without trimming or loudness normalization, following [architecture](architecture.md). Verify duration/time origin and channel quality. Record clipping, noise, silence and resampling configuration. Quarantine failed QA outside the evaluation corpus.

Controlled alterations may insert a bounded pause, change local tempo while preserving pitch, alter a local gain envelope or compress pitch excursions. Implement only transformations that can be reproduced and independently inspected. Save algorithm/version, seed, parameters, input/output hashes and a piecewise source-to-derivative time map, including inserted/deleted intervals. Whole-file gain and register shifts are invariance stress tests, not delivery-flaw labels. Synthetic material is always `origin=synthetic`; transformation windows are metadata, not automatic perceptual ground truth. Review boundary artifacts and avoid click/noise artifacts becoming unintended detector shortcuts.

## Manifest and annotation contracts

The table below is the semantic plan. Phase 1 implements version 1 JSONL rows with nested source/transcript/processing records as documented in the engineering guide. Phase 2 implements separately versioned alignment artifacts without modifying the dataset v1 schema; see [analysis engine](analysis-engine.md). The implementation retains the provenance and review distinctions here; it does not fabricate alignment labels.

Use UTF-8 JSONL manifests, JSON annotation files and CSV coverage summaries. Reject unknown versions, missing provenance and invalid intervals. Times are seconds, half-open `[start_s,end_s)`, in the specified recording's own decoded timeline.

| Record | Required fields |
| --- | --- |
| Source | `source_id`, original URL/publisher, title, speaker ID, access date, source hash, rights-holder, license/permission evidence reference, permitted uses, attribution, excerpt offset |
| Transcript | `transcript_id`, original/normalized text, token mapping, language, SHA-256, reviewers, verification date/version |
| Recording | `recording_id`, `source_id` (nullable for human mirrors), `family_id`, `speaker_id`, `origin`, role, transcript ID, relative path, SHA-256, duration, format, analysis derivative hash/config, consent reference where applicable, QA state |
| Pair | `pair_id`, family, reference ID, participant ID, canonical transcript hash, intended flaw, intended severity, reviewed severity, split |
| Transformation | derivative ID, parent recording ID, algorithm/version/seed, parameters, input/output hashes, temporal map |
| Alignment | recording ID, model/dictionary/config hashes, word/phone intervals, token indices, diagnostics, automatic/manual origin, review version |
| Annotation | annotation ID, pair ID, recording ID, dimension, start/end, token span, severity, audible rationale, reviewer, review state, boundary uncertainty, adjudication reference |
| Split | version, seed, family-to-split assignment, connected-group ID, hash of frozen membership, exclusions and reason |

Do not put private consent documents in the public repository. Rights evidence references can point to a redacted publishable permission record. Store only necessary speaker metadata; no inferred demographics.

## Labels and review

Severity is an ordinal human annotation: 0 near-perfect/no meaningful deviation; 1 mild localized deviation; 2 moderate sustained/repeated deviation; 3 severe disruption. These are listening criteria, not output score bins. A passage can differ from the reference yet be acceptable; explicitly label acceptable alternative deliveries and clean spans as negatives. Do not equate actor instructions or transformation strength with final severity.

Annotate flaw onset/offset on the participant waveform with repeated listening, using word/phrase anchors and linked reference intervals. Separate labels for delivery deviation, recording-quality defect and alignment uncertainty; quality defects must not become delivery ground truth. Overlapping dimensions are allowed; uncertain/unjudgeable spans are masked, never counted as negatives. Retain pre-adjudication annotations.

Two reviewers independently annotate all validation/test flaw intervals and a pilot sample of training intervals, without seeing detector output or synthetic recipe windows. Adjudicate category or severity disagreements and boundary differences over 200 ms. Record agreement (weighted ordinal agreement, category agreement, start/end difference distribution), reviewed counts and residual uncertainty. Manually time at least 100 word boundaries across the pilot and each held-out split, spanning pauses and difficult speech, for alignment evaluation. Adjust workload or target size if careful review cannot be completed; never invent a second review.

## Leakage-resistant evaluation

Before transformations or parameter tuning, construct connected groups joining shared original recordings, excerpt/transcript works, source speakers, mirror speakers and every derived recording. All connected members stay in one split; hash/near-duplicate checks detect accidental overlap. Do not let a recurring mirror speaker connect every family: recruit disjoint split-level speakers first. If constraints collapse groups, redesign acquisition rather than splitting individual files.

Target 6 families for training/calibration, 3 validation, 3 sealed test, subject to the group constraints above. No learned model is required: training means threshold/procedure development. Use validation to finalize thresholds and tests; freeze config/rubric before one final test run. Never adapt the aligner on held-out audio. A reference used for a test comparison is part of that test family and may not enter calibration. Document model training provenance where available and unknown pretraining overlap; group splits cannot prove absence of pretrained-model exposure.

Report metrics per family and by human/synthetic origin, dimension, severity and speaker pairing. Include unseen transformation settings as stress probes separate from the main human test set. Three test families give broad uncertainty; report exact counts and family-bootstrap intervals with that limitation, not general-population accuracy claims. If fewer than three independent test families survive QA, label results pilot-only and leave the evaluation gate open.

## Publication and acceptance

Release only approved audio, transcripts, reviewed alignment/region labels, manifests, transformation recipes, split membership, checksums, attribution and dataset card (scope, collection, exclusions, limitations and rights). Original and synthetic files use distinct directories/manifest roles. Publish in GitHub or public Google Drive and link it in README, as Track C requires. Keep local private recordings outside Git by default; publication is a deliberate separate release step.

Phase 1 pilot gate: two genuine cleared references, exact-text mirrors including near-perfect and severe deliveries, reviewed timestamps and valid manifests. Full dataset gate: rights complete for every released item, no cross-split connected group, explicit coverage gaps and reviewed held-out labels. No dataset claims are complete until those artifacts exist.
