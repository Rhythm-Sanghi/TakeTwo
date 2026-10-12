# Human recording session package

TakeTwo — Speech analysis workspace. This package is ready for a human session; it contains no consent, approval or human performance. Use [ACTION-REQUIRED](ACTION-REQUIRED.md) for the ordered handoff.

## Source and text

Existing draft: `jfkwha-001`, family `jfk-inaugural-1961-opening`, original candidate `r-478a9405c1b10a75fda31972`. Master SHA-256 `a257580da6eda796ed1c703e545865005753f7cb20cc042e0db3c44de82274fc`; canonical WAV `a342f051ea3b4ae23a40d293264bdee3946be235cb73c77e7e582c65dc873bc8`, 17.3 s. See [acquisition](pilot-collection.md) for source/rights and the distinct sample digest. The following is an **archive draft, NOT a verified recording script**:

> Vice President Johnson, Mr. Speaker, Mr. Chief Justice, President Eisenhower, Vice President Nixon, President Truman, Reverend Clergy, fellow citizens:

Two independent listeners must check audio and cut edges before copying approved words to `transcript-verified.txt`. `Mr.` has explicit spoken-form `mister` replacement. Preserve corrections and reviewers/date. The salutation has limited rhetorical variation; prefer a separately selected substantive passage. `jfkwha-190-002` is another acquired master, not a verified excerpt or a second independent source speaker. No verified segment is currently available.

## Recording directions

Record with one fixed microphone/distance/gain in a quiet room. Mono PCM WAV or PCM FLAC at 16/44.1/48 kHz is preferred; record device/settings/room/date and unavoidable AGC/processing. Disable enhancement where possible. Keep short natural room tone, no clipping, music, voice synthesis, denoising or post-recording loudness edits. Target 15–25 s; default analysis cap is 45 s (operators can lower the configured budget). Listen before import; re-record added/missing words or clipped takes. Preserve raw originals.

| Take filename suffix | Instruction to performer | Interpretation |
| --- | --- | --- |
| `natural.wav` | Read the exact script comfortably in your own voice | Clean/acceptable alternative candidate, not certified ideal |
| `near-perfect.wav` | Listen to reference; preserve phrase pacing, pause locations and emphasis while using your own voice | Near-reference candidate; do not impersonate the speaker |
| `mild.wav` | Make one modest local change to rate, pause or emphasis without changing words | Intended mild departure, requiring listening confirmation |
| `moderate.wav` | Make a clear sustained/repeated change in one designated dimension | Intended moderate departure, not automatic ground truth |
| `severe.wav` | Make a strong departure in pacing, pauses or dynamics while keeping every word intelligible and identical | Intended severe departure; re-record text errors |

Rotate target dimensions across families; include mixed flaws and acceptable alternative delivery. Record performer intention separately, hidden from flaw labelers. Do not prescribe guessed timestamp windows as detection output. Synthetic stress edits may be made later with saved recipes/time maps and explicit `origin=synthetic`; they do not become human takes.

## Metadata and review

Use the [blank form](consent-provenance-form.md) and [ImportSpec fields](dataset-engineering.md). Source metadata needs item-specific rights, exact cut offset, attribution and selection rationale. Participant metadata uses `origin=self_recorded`, the same family/work/canonical words, actual pseudonymous speaker/source/session IDs, consent evidence and actual permitted uses. Do not change pending rights to cleared on convenience alone. Full names/signatures stay private.

Two people check transcripts before eligible analysis. Independently review every member's word boundaries and complete phrase partition; preserve automatic alignment unchanged. Two flaw reviewers listen over the full participant duration without predictions, scores, recipes or intended severity; annotate native intervals/absent-pause anchors and uncertainty. Retain disagreements and explicit reconciliation. Human severity is 0 acceptable, 1 mild, 2 moderate, 3 severe; engine penalty bins are a different concept. Use [worksheets](annotation-worksheet.md) and [review CLI](comparison-engine.md). An empty flaw inventory requires actual full listening coverage, not a default blank approval.

The shared `TAKETWO_MAX_ANALYSIS_DURATION_S` setting accepts integer seconds 1–45, default 45. Restart after changing it. See [duration configuration and verification](duration-validation.md).
