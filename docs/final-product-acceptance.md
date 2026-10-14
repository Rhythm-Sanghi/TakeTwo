# Final product acceptance and release-readiness review

TakeTwo — Speech analysis workspace. Local engineering evidence and an owner decision
record; not production certification, independent speech accuracy or publication approval.
Starting HEAD `35bf504`, clean `master`, 14 October 2026.

## Confirmed issues and root causes

The [audit](final-report-polish-audit.md) reproduces four historical outputs: paired
summary/evidence 2/13 pages and reference summary/evidence 2/7. The paired summary's
intro ended near 606 pt on an 843 pt page, leaving insufficient room for its intact
leading anomaly card. The collection already allowed breaks between items. Repetitive
technical overview/ordering text, not a blanket keep-together rule, caused the shift.
One shared paragraph incorrectly promised an appendix in the separate summary; one
global page rule supplied a generic footer. Mechanical window(s) wording and repeated
item caveats made the presentation less readable.

## Changes and before/after layout

Summary print hides diagnostic counts, pitch coverage and detailed ordering rules,
retaining identities, processing, measured differences, a brief selection policy,
selected native intervals, specific reasons/listening questions and verification status.
The Full Evidence Report retains those diagnostics, explicit thresholds, tie-breaking
and all raw evidence. Summary text is 9.5 pt rather than 8.5/9 pt; margins remain 12 mm.
Each finding is kept intact where it fits; the collection can break between items.
Reference summaries with three observations put one on page 1 and two with verification
on page 2 for a more balanced layout. No break is forced for an absent second item.

The paired summary now puts the `technology` → `is` finding on page 1, alongside its
recording comparison. Both summaries use plain selected-passage/interval wording and
direct readers to the **separate Full Evidence Report and JSON**. CSV is precisely
described as retaining every raw acoustic window, not all paired/provenance fields.
Named page styles give every page the correct speech-comparison/reference-inspection
footer and accurate page counters. Print title, scope, type and mode restore after
cancel/success or a thrown browser error; the UI offers export-error recovery.

Readable reasons are derived from authoritative measurements; the technical disclosure
retains the recorded selection rule with grammatical singular/plural display. Repeated
cautions were consolidated while preserving item-specific hesitation, pronunciation,
noise and alignment uncertainty. No ordering, grouping, detector or score formula changed.

| Report | Historical pages | Final pages | Leading selected finding |
| --- | ---: | ---: | --- |
| Paired Analysis Summary | 2 | 2 | Page 1 |
| Reference Analysis Summary | 2 | 2 | Page 1 |
| Paired Full Evidence Report | 13 | 13 | Detailed front matter and complete appendices |
| Reference Full Evidence Report | 7 | 7 | Single-recording evidence and complete appendices |

New outputs are ignored owner files `output/pdf/taketwo-comparative-final-*`.
All historical PDFs remain intact, including the separate hackathon report. Every
final page is rendered at 100% and visually inspected; text remains searchable/selectable.
No clipped text, blank pages or orphan headings were found. Table headers repeat,
source IDs remain available and native times retain documented rounding.
Final visual review found a Chromium continuation page missing its word-inventory
header and splitting a row. Explicit print `break-inside: avoid` on the header fixed
the continuation without changing page counts; all four word-inventory pages now
repeat the header. The QA checker verifies this using standalone table evidence IDs.

## Genuine evidence and cross-format consistency

The complete restored authoritative JSON data is unchanged from the preceding
milestone: 53 raw windows, 44 groups, 71 provisional words, one anomaly and 74 ordered
items; reference-only 28 windows / 22 groups. No underlying measurement or provenance
changed. Reference/participant duration is 30.224375 / 29.370 s, difference -0.854375 s
(-2.826775%), digital RMS difference +0.0438473107 dB. These are recording measurements,
not verified pacing or perceptual differences.

| Selected passage | Reference native replay | Participant native replay | Supporting observation |
| --- | --- | --- | --- |
| `technology` → `is` | 10.93–11.88 s | 10.12–13.47 s | Provisional 2.890 s gap; 0.000 s low-energy support, complete frames |
| Before `helps` | 13.23–13.64 s | 14.35–15.06 s | Provisional gap difference +0.560 s |
| Before `a` | 15.39–15.98 s | 16.25–16.32 s | Provisional gap difference -0.510 s |

Activity can include noise. The gap does not establish silence, a missed word,
hesitation, a transcript error or an alignment failure. All machine word timing is
unverified; no common independent phrase partition is available.

The read-only [PDF acceptance checker](../scripts/check_analysis_pdf.py) validates
the authoritative v1 model/checksum, every CSV field and inventory, recording names
and durations, selected evidence/order/native bounds, versions, full hashes, footers,
page counters, text bounds and expected page-one placement. It checks all three selected
IDs in each summary, 169 IDs in paired evidence (44+71+1+53) and 50 in reference evidence
(22+28). The summary promises no internal appendix or hidden findings. PDF screenshots
are layout evidence, not the data oracle.

Reproduce using optional QA tooling (no application dependency change):

```powershell
uv run --with pymupdf==1.28.2 python scripts/check_analysis_pdf.py `
  --insights local-data/final-acceptance-genuine-insights.json `
  --csv local-data/final-acceptance-genuine-windows.csv `
  --summary output/pdf/taketwo-comparative-final-genuine-summary-2026-10-14.pdf `
  --evidence output/pdf/taketwo-comparative-final-genuine-evidence-2026-10-14.pdf `
  --expect-first-highlight
```

Repeat with `reference` in place of `genuine`. The flag is for cases where the leading
finding can fit legibly, not a universal requirement to squeeze arbitrary long inputs.
Inputs are never modified. Human layout review remains necessary alongside these checks.

## Playback, human listening and spoken accessibility

Final browser checks use a freshly restarted local backend and private workspace copies.
Restored checks alternate reference/participant replay, pause the other track, verify
native focus/selection, inspect provisional text and waveform, and export both modes.
Each recording keeps its independent clock; no time stretching. Five widths
320/390/800/1366/1920 retain controls without document overflow or axe violations.
Actual Chromium 200% tab zoom is verified separately from CSS scaling.
The fresh genuine pilot passed all three tests with new imports, uncached MFA alignment
and extraction. Its analysis job took 215.281 s and reached 2,074,923,008 bytes of peak
committed memory (about 1.93 GiB); these are one-machine observations, not a benchmark.
It reproduced 53 raw windows, 44 groups, 71 provisional words and one anomaly.

**Actual human listening is pending.** No person supplied completed observations in
this task. Use the [listening worksheet](comparative-listening-acceptance.md) on all four
participant comparisons, checking both native starts/stops, usefulness and misleading
language. Record Useful comparison / Possible machine-alignment problem / Technically
correct but not useful / Misleading explanation / Playback problem / Inconclusive.
Keep these usability notes separate from formal ground truth and scientific review.

**Narrator/NVDA spoken acceptance is pending.** No audible screen-reader session was
genuinely reviewed by a person. The [spoken worksheet](spoken-accessibility-acceptance.md)
covers navigation, selectors, loading/completion announcements, headings, times, replay,
focus, expanded evidence, exports and recovery without relying on graphs. Axe passing
and tagged PDFs do not constitute spoken acceptance.

## Readiness decision and exact outstanding actions

| Area | Current decision | Required action |
| --- | --- | --- |
| Engineering | Core local analysis, replay and exports demonstrated; operational limits remain | Validate representative Windows machines and cold restoration; investigate connection resets/heartbeat rejection; perform owner operational acceptance |
| Product | Readable reports and technical routing checked; human usefulness/accessibility pending | Actual listeners complete all four comparisons; Narrator and preferably NVDA reviewers complete spoken worksheet and recheck failures |
| Scientific | Not ready for validated speech-quality/accuracy claims | Independently review spoken text and temporal boundaries, annotate actual flaws with exact inventory, establish real F0 references, calibrate thresholds and run held-out evaluation with actual metrics |
| Publication | Private-data distribution and public submission not approved | Obtain recording/distribution permissions and consent evidence, prepare rights-cleared public examples/demos, and obtain technical-report owner approval before publishing |

acoustic-v1, delivery-v0, exploratory-v1, comparative schema v1, exact-inventory ground
truth, independent review, abstention and eligibility gates remain unchanged. Accepted
pitch coverage is approximately 0.596619% / 0.511771%; no mask/threshold lowering or
pitch score is justified. Automated usability checks do not authenticate reviewers,
create independent annotations, clear rights or establish detection accuracy.

Known Windows Proactor WinError 10054 diagnostics recur. The prior final-heartbeat
rejection correctly withheld review submission; no universal reliability repair is
claimed. Cold restoration may exceed the UI budget under load; current timing samples
are not a speed benchmark. Testing one machine is not production certification.

## Verification, preservation and local Git

Baseline before source edits: 372 Python (285.10 s), 66 frontend (7.25 s), 13 generated
browser (5.1 min), three fresh genuine tests (4.1 min), zero failures/skips.

| Executed final check | Actual result |
| --- | --- |
| Full Python | 372 passed, zero failed/skipped, 249.56 s; one upstream Starlette warning |
| Frontend | 73 passed, zero failed/skipped, seven files |
| Generated browser | 13 passed, zero failed/skipped, 5.0 min; mode/printing, native zoom, replay, recovery, review isolation |
| Fresh genuine pilot | Three passed, zero failed/skipped; new imports, real pipeline, replay, exports and native 200% zoom |
| PDF/JSON/CSV checks | Both modes pass; first summary finding page 1; 169/50 full evidence IDs |
| TypeScript / ESLint / Prettier / Vite | Passed |
| Ruff / format | Passed; 77 Python files |
| Schema/documentation | Six schemas, 66 Markdown files and 356 local documentation links validated |
| Dependencies | uv lock check and npm audit pass; npm reports zero vulnerabilities, pip-audit reports no known vulnerabilities in resolved dependencies (editable local package skipped) |
| Packages / private-data checks | Wheel/sdist built; release preflight found no blocking candidate/history/package findings; all 28 protected hashes match |

No backend implementation diff exists from `35bf504`; complete restored comparative
JSON equals the prior evidence. All 28 protected original/review/database/historical
PDF hashes match. Genuine audio, screenshots and PDFs remain ignored/private.

One intermediate frontend run correctly failed the former assertion that the technical
ordering sentence was visible in the primary finding. The updated test checks the new
measurement-derived visible reason and still checks the full recorded policy after
expansion. No assertion or scientific gate was removed. Initial private script preparation
hit a PowerShell quotation error; it was corrected before generating reports. Ruff
flagged an `isinstance` style issue in the new QA script; corrected and checked.
The new continuation-header check initially mistook selected-item references for table
rows; it now checks standalone row IDs, and both final modes pass. No product or
scientific assertion was relaxed.

Local commits: `2418b67` audits pagination and pending human acceptance; `622a2d7`
polishes summaries, native reasons, print recovery and read-only PDF QA. The final
documentation closeout commit, titled **Record final product acceptance and release
readiness**, contains this report and updated guide/completion links. Its full HEAD and
post-commit clean working-tree check are recorded at handoff. Final handoff state is
clean `master`; resolve `git rev-parse HEAD` for the documentation closeout revision.
The pre-commit release audit inspected 214 candidates and 631 reachable history blobs,
with no blocking findings in candidates, history or built packages. The release preflight
also reviews the three existing binary deliverables separately; it is a pattern and
inventory check, not proof of rights clearance or the absence of every possible secret.

No push, deployment, publication or external submission. Codex assisted implementation, tests and documentation
under human direction. MIT copyright © 2026 Rhythm Sanghi remains unchanged.
