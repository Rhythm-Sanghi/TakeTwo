# Comparative insights audit — 14 October 2026

Starting revision: `365ed29` on `master`; clean working tree. This audit distinguishes
the reference-only browser state from the paired exploratory PDF.

| Category | Evidence | Decision |
| --- | --- | --- |
| Reproducible UX weakness | Fresh genuine reference/uneven GET returns 53 raw windows; the main component presents the first eight individual windows with repeated caveats. | Group compatible connected windows, retain all raw evidence, give a small inspection inventory. |
| Missing analytical feature | The report has 71 provisional indexed word correspondences but no duration/gap deltas, local acoustic context or ordering. | Add a separately versioned comparative layer. |
| Reproducible UX weakness | Current private four-page PDF puts raw windows and both machine word lists after its opening measurements. | Make comparative overview and selected evidence primary, move complete inventories into a marked appendix. |
| Confirmed error-state weakness | Missing artifact files raise FileNotFoundError into generic storage-unavailable HTTP 503; corrupt envelopes raise generic invalid-input 422. | Distinguish missing/corrupt artifacts from unavailable storage and invalidated input. This does not establish the screenshot's cause. |
| Unconfirmed reported bug | Five completed genuine historical jobs restore exploratory reports with HTTP 200, including two reference-only jobs. Inspected latest generated reference-only 390px screenshot shows a valid single-input result. | Original Not Found condition is not reproduced. Test selected identity, harmless GET recovery and restart; do not invent a root cause. |
| Scientific limitation | Accepted pitch coverage remains 0.596619% reference / 0.511771% uneven. Existing gain/window/range study has no independently checked speech F0. | Preserve acoustic-v1 and pitch abstention; no new extractor claim. |
| Scientific limitation | Machine alignment positions supplied text; timing confidence is unavailable. Reviewed phrase partitions exist only in independent timing reviews. | Complete exact indexed text mapping permits provisional word inspection; no phrase inference from wall-clock proximity or punctuation. |
| External/human dependency | Spoken text verification, independent timing/F0 labels, rights clearance and actual Narrator/NVDA acceptance are absent. | Keep these explicitly open; exploration never approves scoring or human review. |

Fresh isolated-copy measurements: 30.224375 s reference, 29.370 s uneven;
participant minus reference −0.854375 s (−2.826775%), RMS +0.043847 dB,
active energy-range delta −0.407866 dB. No perceived loudness/significance claim.
Five initial GETs took 2.37–9.56 s under concurrent baseline tests; these are mixed-load
restoration timings, not a capacity benchmark. Private evidence is retained under
`local-data/comparative-baseline*.json`. The five originals were found directly in
the user's Documents directory with matching hashes; their move's cause is unknown.
Seventeen original/review/historical-PDF hashes were captured before implementation.

Executed baseline: 340 Python tests passed (238.65 s, one upstream Starlette
deprecation warning); 55 frontend tests passed (5.63 s). Browser baseline is
historical until rerun; no new browser passing count is asserted here.

Reports bind job selection, current dataset content and original audio/sample/text
hashes; source feature/alignment envelopes are validated through managed paths and
source/environment identity checks on each GET. Frontend checks exact job and selected
members and aborts/ignores obsolete requests. New artifacts must retain this boundary.
Codex assisted this audit and implementation under human direction.
