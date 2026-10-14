# Comparative refinement audit

TakeTwo — Speech analysis workspace. Starting local revision `5b638cb`, clean
`master`, 14 October 2026. This audit separates presentation defects from
scientific limitations. Historical PDFs and private recordings are preserved.

## Reproduced presentation issues

- The historical reference PDF has six pages and labels a single recording
  “Automatic comparison”; it also prints zero paired word/anomaly counts.
- The historical paired PDF has ten pages. Both reports automatically expand
  comparative and exploratory appendices through print CSS. There is only one
  exploratory print action; no concise summary export.
- Each inspection item has a deterministic backend `order_reason`, but the UI
  places it inside a disclosure that print CSS hides. The main list explains
  category ordering without an immediately visible individual selection reason
  or neutral listening question.
- The anomalous 2.890-second machine gap is accurately measured, but the visible
  explanation does not explicitly connect its zero low-energy support to the
  reason for checking supplied text and automatic timing. Activity may be noise.
- Whole-recording figures are valid. Their diagnostic presentation does not
  distinguish the small +0.044 dB digital-level difference from more inspectable
  local timing observations. No perceptual significance is established.

## Grouping investigation

The preserved genuine response contains 53 raw windows in 44 groups: 36
single-window groups, seven two-window groups, one three-window group. There are
22 increasing and 20 decreasing energy groups and two leading low-energy groups;
none is shorter than 0.1 seconds. Existing grouping joins compatible overlapping
or touching windows, without bridging positive gaps, opposing signs, different
recordings, hashes or detector configurations. A single window is not itself a
bug, and a reduction target is not scientific justification for merging.
The actual inventory has 25 touching/overlapping group pairs, all with opposite
directions, zero compatible same-direction leftovers, and a smallest positive
same-direction neighbouring gap of 0.5 seconds. Keep the existing rule; no extra
merging is justified by this evidence.
All exact source-window values and IDs must remain available.

## Reproducible baseline evidence

- Historical PDF text/render inventory:
  `local-data/refinement-baseline/reports.json`, with all 16 rendered pages.
  Reference SHA-256 `777e51b03ef68d34ebe43cfa1d196e68f4868aa5049cf1b0e5c7665a80558c9a`;
  paired SHA-256 `e6883d2b32ba567a9e1c37876fa24ac574b43d70c15ba174dcac77cb0db7da2b`.
- Current frontend baseline: 62 passed, zero failed/skipped, five files,
  `npm test -- --run`, 28.21 seconds.
- Full Python baseline: 369 passed, zero failed/skipped, 281.17 seconds, one
  upstream Starlette deprecation warning. Generated browser: 12 passed, zero
  failed/skipped, 4.6 minutes. Windows connection-reset diagnostics recurred.
  The first browser invocation could not start because port 8884 was occupied; retry used 8997
  without stopping the existing service.

## Scientific and human limits

71 paired word measurements are provisional supplied-text positions, not checked
spoken identity. No common independent phrase partition is present. The genuine
pair remains ineligible for Verified Assessment. Accepted pitch coverage remains
low; no scoring, detector or review threshold changes are justified here.
Automated playback routing is not human listening acceptance. Prepare an
owner-executable review workflow; actual listening and spoken screen-reader
acceptance remain pending. Cold restoration latency and Windows connection-reset
diagnostics remain operational concerns unless separately reproduced and fixed.
