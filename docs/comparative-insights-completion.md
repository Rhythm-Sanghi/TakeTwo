# TakeTwo comparative insights completion — 14 October 2026

Speech analysis workspace. Local implementation and measured acceptance evidence;
not production certification or independently evaluated speech accuracy.

## A. Confirmed problems and investigation

Starting revision `365ed29`, clean `master`. The [audit](comparative-insights-audit.md)
records repetitive individual windows, unused provisional correspondence and raw-heavy
printing as reproducible UX/analytic weaknesses. Missing stored acoustic/report files
previously returned generic storage 503; they now return `artifact_missing` 404.
Failed stored-envelope validation returns `artifact_corrupt` 422. Missing job IDs,
unavailable stages, invalidated inputs/reviews, denied access and storage failures
retain their distinct 404/409/403/503 states and recovery.
Stored comparative-envelope corruption also has a specific `artifact_corrupt` response
and restore/new-analysis recovery; it never overwrites the damaged evidence.

Final responsive acceptance found a confirmed transient overflow before uPlot's
ResizeObserver redraw: document width 642 at viewport 390, and 1602 at viewport 1366.
Containing the chart's interim visual overflow preserves the redraw and controls.
The new resize-event regression passes across breakpoints, including before observers
finish; a settled-layout assertion alone did not catch this race.
Returning from a panned long recording also exposed a conflicting view reset: the
seek-to-window branch could override full duration with two seconds. The reset now
keeps the complete native domain, verified with a ten-second component regression
and genuine recording controls.

The screenshot's original Not Found condition was not reproduced: five fresh genuine
historical GETs returned 200, including two reference-only jobs; the inspected prior
reference-only screenshot was valid. Historical GET restoration, refresh, selection
changes, controlled missing/corrupt artifacts, safe retry and restart are tested.
No invented root cause or automatic mutation retry was introduced.

## B. Candidate grouping and selection

Genuine reference/uneven: **53 raw windows → 44 groups**. Reference-only: 28 windows
→ 22 groups. Every window belongs to exactly one group and remains in the original
JSON/CSV, expanded browser evidence and printed technical appendix.

Grouping joins temporal connected components that overlap or touch, sharing recording,
exact category, direction, feature identity, detector and thresholds/resolution.
Positive gaps, opposing directions and unrelated categories/configuration never join.
Duplicate IDs, nonfinite/incomplete measurements and invalid native bounds are rejected.
Groups retain original IDs, bounds, count, median/range of changes, detector and limits.

The genuine report has 74 explained inspection items; browser starts with six and
print selects the first three. Quality/support-limited evidence follows complete
evidence; categories order anomalies, gap deltas, word-duration deltas, groups.
Within category larger measured durations precede native-start/ID ties. A gap anomaly's
following-word context is not highlighted twice; all original measurements remain.
Amplitude magnitude alone cannot outrank complete evidence. No severity/confidence
score is created. [Exact methods](comparative-insights.md) are reproducible.

## C. Genuine comparative evidence and abstention

The restored pair and fresh imported/processed pair both measure 30.224375 s reference
and 29.370 s participant: delta −0.854375 s (−2.826775%), RMS +0.043847 dB, active
energy-range delta −0.407866 dB. Restored activity support delta is −0.820 s and
low-energy support delta −0.030 s. These establish no pacing flaw or perceptual
significance.

Complete identical canonical text, offsets and explicit token indices support 71
**provisional** word comparisons. Repeated supplied-text positions require complete
indices; partial/missing/OOV/ambiguous mappings and mismatched text abstain. Successful
MFA still cannot verify actual omissions/repetitions or timing accuracy.

Restored local examples:

| Inspection | Reference native interval | Participant native interval | Actual measurement |
| --- | --- | --- | --- |
| Alignment context `technology` → `is` | 10.93–11.88 s | 10.12–13.47 s | Inter-word gap delta +2.890 s |
| Gap before `helps` | 13.23–13.64 s | 14.35–15.06 s | Gap delta +0.560 s |
| Gap before `a` | 15.39–15.98 s | 16.25–16.32 s | Gap delta −0.510 s |

The participant's actual `technology` interval is 10.12–10.50 s and `is` 13.39–13.47 s.
Its 2.890 s machine gap has complete acoustic support but **0.000 s low-energy support**
under the unchanged activity rule. A quiet-pause conclusion is withheld. Misalignment,
text mismatch or repeated/omitted speech requires listening; confidence is unavailable.
Phrase comparison is withheld in this genuine pair because independently reviewed
common phrase partitions are absent. The versioned engine supports validated shared
partitions when available, retaining their review hashes.

## D. Results experience and native listening

Selected identities/processing/job appear first, followed by **What analysis found**,
six initial **Differences worth inspecting**, native listening, expandable comparative
and raw evidence, and the separate Verified Assessment. Original controls remain.
Reference-only output does not present participant prerequisites as reference defects.

A/B replay uses each supported interval's own clock, pauses the other track and
honors bounds. Inspect moves focus to its audio control. Return-to-complete clears
selection/window; navigation and obsolete bounded-play requests pause audio and ignore
late rejected promises. Exploration never satisfies independent reviewer listening.
Alignment-anomaly A/B includes both surrounding provisional words on each native
timeline, so the user hears the gap in its supplied-text context.
The complete paired table also provides native reference/participant replay for every
word or supported phrase, including measurements outside the initial highlights.

Actual genuine screenshots at 320/390/800/1366/1920 px were inspected privately;
all have zero document overflow and zero axe violations. Genuine native 200% zoom
used Chromium's tab API: width 1600→800, DPR 1→2, reported zoom factor 2. Generated
fixture UI screenshot in README was refreshed from actual processing, explicitly
labelled software signals. No genuine screenshot/audio is in the public repository.

## E. Reports and export agreement

Owner reports are separate ignored outputs: paired 10 pages and reference-only
6 pages. Their first pages show overview and selected actual observations; marked
appendices retain all groups, native paired measurements, all raw windows, automatic
word lists, extraction configuration, source/sample/text/alignment/feature hashes,
methods and applicable evidence requirements. Page numbers and table headers repeat.
Page counts follow content; these are not the six-page hackathon technical report.

Rendered and visually inspected every page. All 16 pages have selectable/searchable
text, no blank pages and zero text characters outside page bounds. Paired PDF contains
all 44 group IDs and 53 original candidate IDs, plus 71 paired measurements. PDF
opening values match fresh API data. Full CSV IDs and every numeric measurement,
threshold/window/hop match the source JSON; comparative envelope checksum matches
its full report. Historical PDFs were preserved.

## F. Scientific integrity

No changes to `analysis/`, `exploratory/` or `comparison/` versus starting HEAD:
acoustic-v1, exploratory-v1 and delivery-v0 remain reproducible. The new separately
versioned layer has its own schema, hash-addressed artifacts and bounded cache.
Source identity/integrity checks remain mandatory on cache hits. General comparative
APIs are denied during reviewer handoff. No audio upload/cloud dependency was added.

Accepted pitch remains 0.596619% / 0.511771% in both restored and newly processed
genuine data. Reviewed prior pitch diagnostics found no independently checked real
F0 corpus or new defect justifying another extractor study. No mask/threshold change,
fabricated contour, pitch score or synthetic-tone accuracy claim was introduced.
The real pair remains scientifically ineligible; eligible/eligible-zero cases in
software fixtures are clearly distinguished from independently validated speech.

Seventeen pre-existing original/review/database/historical-PDF hashes match the
pre-implementation baseline, including all five originals in the user's Documents
directory. Their earlier relocation's cause remains unknown; no original was moved.

## G. Performance and Windows reliability

Final genuine restored comparative GET: cold 12.778 s, repeats 0.233/0.235 s under
mixed verification load. Earlier first/repeat measurements were 9.864/0.322 s and
11.970/0.290/0.312 s.
The last simultaneous package/audit verification measured 54.264 s cold and
1.058/1.270 s repeats. Cold restoration can exceed the browser's 15 s request
budget under load; safe retry remains necessary. The cause of that slowdown has
not been isolated, and predictable restoration latency remains an operational limit.
These show bounded cache reuse, not a comparable before/after speed benchmark.
The compact comparative response is about 256 KiB; no feature arrays are copied into it.

Fresh isolated genuine job `j-28db55b5f5d046efbac770e400967a75` completed in 262.453 s,
peak worker-tree commit 2,076,827,648 bytes (1.934 GiB), no cache hits. Stages:
reference alignment 118.140 s, participant alignment 106.469 s, extraction
19.516/14.812 s, comparison 1.406 s, validation 0.313 s. CPU-only, 4 GiB tree
limit, 600 s service deadline and original acoustic calculations are unchanged.

The first genuine browser attempt failed: its 240 s pilot test timeout expired while
participant processing ran; its reference MFA version check had timed out at the
existing 30 s limit. The pilot harness now uses the same 900 s test envelope as
other genuine runs, allowing the unchanged 600 s service deadline. No scientific
threshold/deadline or assertion was relaxed. The adapter's native version check
returned MFA 3.3.9 in 3.56 s in isolation; the subsequent isolated fresh run passed.
Load-related cause is unproven. The failed run and trace remain private evidence.

Restart of that interrupted isolated workspace marks the job failed with the explicit
`interrupted` diagnostic, preserves completed artifacts, does not requeue and returns
409 when insufficient completed evidence exists. SQLite integrity checks returned `ok`
for both failed/recovered and successful genuine workspaces.

Windows Proactor connection-reset WinError 10054 diagnostics recurred during browser
request cancellation. Tests still passed, but no universal reset/reliability fix is
claimed; these remain operational limitations, not suppressed logs.

## H. Executed verification

| Final check | Passed | Failed | Skipped | Evidence |
| --- | ---: | ---: | ---: | --- |
| Full Python | 369 | 0 | 0 | Latest 492.09 s; one upstream Starlette deprecation warning |
| Frontend | 62 | 0 | 0 | 5 files; latest 21.60 s under mixed load |
| Full generated browser | 12 | 0 | 0 | Latest 4.3 min; resize-event containment, native zoom, five widths, axe, replay, recovery, review isolation |
| Genuine browser pilot | 3 | 0 | 0 | 5.2 min; real five-file import, fresh MFA/extraction, pair, A/B, exports, native zoom |
| Genuine native zoom after resize repair | 1 | 0 | 0 | 18.7 s; existing isolated genuine pair, actual tab zoom factor 2 |
| TypeScript / ESLint / Prettier | pass | 0 | 0 | Executed against current frontend |
| Ruff / formatting | pass | 0 | 0 | 76 Python files checked |
| Vite / wheel / source builds | pass | 0 | 0 | Actual production and package builds |
| Schema / local documentation / official Track C hash | pass | 0 | 0 | Runtime contracts and unchanged official PDF |
| npm / Python dependency audit | pass | 0 | 0 | No known vulnerabilities in pinned dependencies |
| Private-data / package preflight | pass | 0 | 0 | 203 staged candidate files; zero blocking/history/package findings |

Earlier attempts are not hidden: first genuine suite **2 passed / 1 failed / 0 skipped**;
after timeout-harness correction and isolated execution **3 passed / 0 failed / 0 skipped**.
One intermediate frontend run had 58 passed / 1 failed due to a misencoded test literal;
the literal was corrected and the expanded current suite passes 62. A read-only export
verification script initially called HTTPX's text property as a function; corrected
verification then checked the complete raw CSV and envelope. No product assertion
was removed or skipped to pass.

## I. Local Git and delivery state

Starting HEAD `365ed29`. Focused local commits on `master`:

- `7d3190d` — audit comparative evidence and restoration states.
- `96d7cc1` — versioned grouping/native-time comparative backend and contract tests.
- `82159cf` — results hierarchy, native playback, print highlights and browser coverage.
- `aa5dd00` — transient chart containment, specific artifact-corruption recovery and methods/evidence documentation.
- `f59b9d5` — complete native-window restoration after panned inspection.
- `5300ce9` — paired anomaly replay includes both surrounding provisional words.

The final documentation/evidence commit accompanies this report; its hash and clean
working tree are reported at handoff. Staged source/history/wheel/archive preflight
returned zero blocking findings. No push, publication, release, original-audio change or external
submission is authorized or performed. Owner PDFs remain ignored local artifacts.

## J. Remaining limitations

Independent spoken-text/timing/flaw/F0 labels, common human phrase partitions, rights
and consent clearance, held-out calibration/evaluation, actual Narrator/NVDA spoken
acceptance and broader Windows reliability remain open. Axe/browser passing is not
spoken screen-reader acceptance. A successful fresh run does not certify all machines.
No causal speech-quality, pronunciation, emotion or confidence conclusions are made.

Codex assisted implementation, test design, interpretation and documentation under
human direction. MIT copyright © 2026 Rhythm Sanghi remains unchanged.
