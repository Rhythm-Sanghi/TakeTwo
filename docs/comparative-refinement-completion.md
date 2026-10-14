# Comparative refinement completion

## Subsequent final polish and acceptance

This document records the `35bf504` refinement milestone. The subsequent
[final acceptance/readiness report](final-product-acceptance.md) supersedes its print
presentation: both two-page summaries now show their first selected finding on page 1,
use correct separate-export references and report-specific footers, and retain readable
9.5 pt summary text. Full Evidence Reports preserve all measurements and provenance.
Historical outputs and scientific gates remain unchanged. Actual human listening and
spoken screen-reader acceptance remain pending with owner worksheets. See the final
report for current test evidence and the separate engineering/product/scientific/publication
decisions; passing engineering checks does not clear the other areas.

TakeTwo — Speech analysis workspace. Local product refinement and software evidence,
not independently established speech-analysis accuracy or production certification.
Starting revision `5b638cb`, clean `master`, 14 October 2026.

## A — Problems and root causes

The [baseline audit](comparative-refinement-audit.md) confirms reference-only
“Automatic comparison” wording, irrelevant paired zero counts, hidden selection
reasons, no neutral listening prompts and one print mode that expands all diagnostic
appendices. Historical reference/paired reports were six/ten pages. Their measurements
were valid; these were interpretation and reporting defects, not detector failures.
The report redesign also found raw IDs wrapping in the narrow window-count column.
They now have a dedicated group-to-source provenance table.

## B — Insight selection

The ordering rule is unchanged: complete native support, RMS at least 0.001, no
clipping or stored quality flags precede limited evidence; then anomaly, absolute
word-gap delta at least 0.150 s, absolute word-duration delta at least 0.100 s,
acoustic groups. Within category larger measured duration/delta precedes native-start
and evidence-ID ties. This is a deterministic presentation policy, not statistically
validated importance, severity, calibrated confidence or accuracy.

Every primary item now shows **Why inspect**, **Listen for**, native measurements
and item-specific uncertainty without opening JSON or a disclosure. Its expanded
evidence retains the complete order policy. Category labels distinguish alignment
anomalies, provisional timing/gaps, energy changes and low-energy intervals; limited
items identify recording-quality limitations. The browser starts with six items and
can expand the full ordered inventory; paper selects three. All counts are observations,
not speaking mistakes.

Actual examples: the 2.890 s gap meets the 1.000 s anomaly threshold and has
0.000 s low-energy support with complete coverage, prompting a transcript/timing check.
The absolute 0.560/0.510 s word-gap differences meet the 0.150 s inspection rule.
Listening questions ask whether assigned intervals fit the audible passage. None
establishes hesitation, incorrect pronunciation or a proven alignment failure.

## C — Candidate grouping

Before and after: paired **53 raw windows / 44 groups**; reference **28 / 22**.
Paired group sizes: 36 single, seven double, one triple; no group shorter than 0.1 s.
All 25 remaining overlapping/touching group pairs have opposing directions; there
are no compatible same-direction leftovers. The smallest positive same-direction
neighbouring gap is 0.5 s. No extra merging is justified, so the existing compatible
overlap/touch rule remains. Opposite signs, positive gaps, different recordings,
feature identities/configurations and unrelated categories remain separate.

Every source ID, timestamp, measurement, threshold and hash remains unchanged in
JSON/CSV. A card can expand to every original candidate's complete serialized record.
Full paper retains grouped measurements and a dedicated unbroken ID link inventory.
Boundary, alternating-direction/single-window, exact provenance and historical-envelope
compatibility regressions supplement existing overlap/touch/invalid/missing-support tests.

## D — Genuine comparison

The restored reference/uneven evidence is exactly unchanged beneath the presentation
layer: duration 30.224375 / 29.370 s; participant delta -0.854375 s (-2.826775%);
RMS +0.0438473107 dB; activity support delta -0.820 s; low-energy delta -0.030 s.
The overview calls +0.044 dB a small measured digital-level difference without established
perceptual significance. Whole-recording duration is not verified speaking rate.

71 provisional word measurements, one anomaly and 74 ordered items remain: one anomaly,
seven gap differences, 22 word-duration differences and 44 acoustic groups. No independent
phrase partition is present. The participant's `technology` is 10.12–10.50 s and `is`
13.39–13.47 s. Their 10.50–13.39 s gap has 2.890 s measured support, **0.000 s low-energy**.
The UI explicitly explains that activity can include noise and calls for listening,
without asserting speech, silence, a pause, a transcript error or an alignment failure.

Fresh isolated job `j-9e4a5cd9e93342aab8d9b351b7a0ea64` reproduced 53 raw windows,
44 groups, 71 words, one anomaly and the same whole-recording deltas/pitch coverage.
It completed in 282.125 s with no cache hits and peak worker-tree commit
2,078,994,432 bytes (about 1.94 GiB). Reference/participant alignment took
137.641/110.391 s; extraction 18.437/12.422 s. SQLite integrity check returned `ok`.
The CPU worker, 600 s deadline and 4 GiB commit limit remain unchanged.

| Selected item | Reference native replay | Participant native replay |
| --- | --- | --- |
| `technology` → `is` alignment context | 10.93–11.88 s | 10.12–13.47 s |
| Gap before `helps`, delta +0.560 s | 13.23–13.64 s | 14.35–15.06 s |
| Gap before `a`, delta -0.510 s | 15.39–15.98 s | 16.25–16.32 s |

## E — Audio acceptance

Actual restored browser checks verified alternating A/B, pausing the other track,
bounded replay, surrounding words, direct provisional-transcript inspection and
waveform actions moving focus to the proper native audio control. Existing routing,
cancellation/navigation and independent native clocks remain; no time stretching.

**Human listening acceptance is pending.** No person performed the private audio
acceptance in this task. The [owner procedure and review form](comparative-listening-acceptance.md)
covers all four participant takes, with six usefulness/problem categories and evidence
needed. It is separate from scientific annotations, rights approval and detection accuracy.
Software replay events are not a listener's acceptance.

## F — Reports

**Analysis Summary** includes identities, processing, measured overview, three selected
observations/reasons/questions, native intervals, shared and item-specific limits,
verification status and a short method/version note. **Full Evidence Report** adds all
grouped/raw windows, paired measurements with stable IDs, all anomalies, threshold
methods, full hashes/configuration, dataset and implementation versions and provenance.
The old whole-workspace layout remains as **Print workspace evidence**, avoiding a
second misleading “summary” action. Save as PDF suggested titles identify the mode.

| Private owner output | Pages | Evidence ID checks |
| --- | ---: | ---: |
| Paired Analysis Summary | 2 | All three selected evidence IDs |
| Reference Analysis Summary | 2 | All three selected group IDs |
| Paired Full Evidence Report | 13 | 44 groups + 71 segments + 1 anomaly + 53 raw IDs = 169 |
| Reference Full Evidence Report | 7 | 22 groups + 28 raw IDs = 50 |

Outputs are ignored local files under `output/pdf/taketwo-comparative-refined-*`.
Historical reports and the separate hackathon technical PDFs are unchanged. All 24
pages have searchable text, no blank pages and zero characters outside page bounds.
Every printed page was rendered and visually inspected, including table continuations,
repeated headers, row wrapping and section headings. Printed disclosures have no
confusing triangles. Full IDs are contiguous searchable text in dedicated provenance
rows. Summary has no full inventory; JSON/CSV are never truncated. All raw CSV IDs
and numeric/threshold/resolution fields match JSON exactly; selected PDF values match
native rounding. Private checks are in `local-data/refinement-printed/verification.json`.

## G — UI/UX

Workshop + Gridline + Studio Utility is retained. Current identities/processing lead
the measured overview, selected observations with direct replay, native listening and
separate Verified Assessment. Lower-priority inventories remain expandable, not the
primary result. Reference-only headings, counts, downloads, empty/loading/recovery
states and paper use single-recording terminology. Paired absence is shown only where
it matters to the requested action. Shared uncertainty avoids copying the entire order
policy into each visible reason; item-specific caution remains.

Restored genuine and reference-only screens were checked at 320, 390, 800, 1366 and
1920 px: zero overflow and zero axe violations at all ten checks. Actual private desktop,
mobile and full-page screenshots were inspected; result/identity remain near the top.
Screenshots are private `local-data/refinement-{genuine,reference}-*`, not public assets.
Native Chromium zoom uses a test-only isolated extension with `chrome.tabs.setZoom(2)`,
not CSS scaling or a user's profile. Its executed outcome is recorded below.

## H — Scientific integrity

No diff in `src/taketwo/analysis`, `exploratory` or `comparison` from `5b638cb`:
acoustic-v1, exploratory-v1 and delivery-v0 and all scientific gates remain unchanged.
Comparative schema v1, category/order semantics and raw data remain compatible; only
the item-specific explanation string changed. Its implementation hash publishes a new
immutable envelope while retaining historical artifacts. Existing source validation,
cache identities, exact-inventory ground truth, reviewed phrase requirements, eligibility
and abstention are unchanged. The real pair stays REVIEW REQUIRED.

Pitch acceptance remains 0.596619% / 0.511771%; readable coverage appears without
weakening masks or creating pitch conclusions. Independent timing/text/F0/flaw truth,
rights/consent and held-out calibration remain absent. No fabricated metrics or reviews.
All 24 protected original/database/review/historical-PDF files match the starting hashes.
Codex assisted implementation, tests and documentation under human direction; MIT
copyright © 2026 Rhythm Sanghi is preserved.

## I — Verification and Git

Baseline executed: 369 Python (281.17 s), 62 frontend (28.21 s), 12 generated browser
(4.6 min), zero failed/skipped; Windows reset diagnostics and one upstream Starlette
deprecation warning remain. These were established before source edits.

| Current executed check | Result |
| --- | --- |
| Full Python | 372 passed, zero failed/skipped, 217.46 s; one upstream warning |
| Focused comparative regressions | 31 passed, zero failed/skipped, 65.97 s |
| Frontend | 66 passed, zero failed/skipped, six files |
| TypeScript / ESLint / Prettier / production build | Passed |
| Ruff check / format | Passed; 76 Python files |
| Contract/documentation/official Track C checks | Passed; existing schemas and official PDF unchanged |
| Lock / wheel / source build | Passed |
| npm / pinned Python dependency audit | Zero known vulnerabilities; editable local project not an audited registry package |
| Generated browser final suite | 13 passed, zero failed/skipped, 4.5 min; native 200% and five widths |
| Fresh private five-take pipeline / native 200% | 3 passed, zero failed/skipped, 5.5 min; actual import, fresh MFA/extraction, A/B, both print modes and full exports |
| Release/history/package preflight | 208 candidate files / 615 reachable history blobs; zero blocking/history/package findings |

Earlier failures are retained honestly: a new print test initially assumed nonempty
findings, then its targeted reused-workspace attempt used the five-second UI assertion
while cold evidence was still restoring. It now covers empty findings, waits for the
completed export and tests print mode separately from cold restoration latency. An
over-specific generated filename filter was also corrected. A later full browser run
passed 12 and failed one review submission: the final heartbeat was rejected by the
unchanged real-time playback gate; validation retained only 0.975466 s of a two-second
fixture and correctly withheld submission. Its trace is preserved privately. Isolated
actual replay passed (one test, 19.0 s); no scientific assertion or gate was relaxed.
The private PDF verification helper initially used `id` rather than CSV `candidate_id`;
the corrected helper validates all rows. A private browser script initially mistyped a
historical reference job ID; the actual ID was looked up and the run passed.

Local commits so far: `9ad4e7c` audit/listening workflow; `71bb2f7` measurement-based
selection reasons and provenance regressions; `cb466af` summary/full reports, native
listening explanations and reference terminology. Final evidence commit and clean
tree are recorded at handoff. No push, deployment, publication or external submission.

## J — Remaining limitations

Actual human listening and Narrator/NVDA spoken acceptance remain pending. Automated
axe and native replay tests do not satisfy these. Independent reviewed text/timing,
phrase partitions, F0/flaw annotations, rights clearance and held-out evaluation remain
external tasks. No causal speech-quality or pronunciation conclusions are made.

Windows Proactor WinError 10054 and the observed real-time heartbeat rejection remain
operational reliability limits; isolated passing runs do not establish universal absence.
Warm restored requests in this task were roughly 0.1–0.6 s and the reference
initial request roughly 3 s; these are not cold-load benchmarks or a latency repair.
Prior mixed-load cold restoration exceeded the UI request budget. That performance
limit remains open and safe retry remains available.
