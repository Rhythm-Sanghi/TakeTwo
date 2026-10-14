# Final report polish audit

TakeTwo — Speech analysis workspace. Starting `35bf504`, clean `master`.
Current historical reports were read/rendered without overwriting them: paired
summary/evidence 2/13 pages; reference summary/evidence 2/7 pages. Their hashes and
100% page renders are recorded privately under `local-data/final-acceptance-baseline-pdfs`.
All 28 protected original/review/database/historical-PDF files match baseline hashes.

## Confirmed issues and root causes

1. Paired summary page 1 ends its introductory text at approximately 606 pt on an
   843 pt page. The intact anomaly card needs more space than remains. The current
   findings list already uses block layout and breaks between individual items;
   no overbroad keep-together rule on the entire list was found. Repetitive overview
   counts, pitch diagnostics, category totals and the long ordering paragraph consume
   space better used for the selected evidence. Shorten the summary, not its font.
2. One shared print paragraph says full measurements follow in the appendix even
   in the separate Analysis Summary, which has no appendix. Use mode-specific
   directions to Full Evidence Report, JSON and CSV.
3. A global unnamed `@page` rule prints “TakeTwo / automatic inspection” for every
   report. Use named page styles selected by report mode, preserving page counters.
4. Selected-item prose contains literal “source window(s)” and detector/ordering
   details. Use grammatical, measurement-derived readable reasons; preserve exact
   backend reasoning and thresholds in the technical evidence.

## Executed baseline before source changes

| Check | Actual result |
| --- | --- |
| Python | 372 passed; zero failed/skipped; 285.10 s; upstream Starlette warning |
| Frontend | 66 passed; zero failed/skipped; 7.25 s |
| Generated browser | 13 passed; zero failed/skipped; 5.1 min; native zoom/five widths |
| Fresh genuine pilot | 3 passed; zero failed/skipped; 4.1 min; real processing/native zoom |

Windows Proactor WinError 10054 diagnostics recur. Baselines do not establish absence
of the previously observed real-time heartbeat rejection or predictable cold loading.
No new detector/grouping/scoring change is justified by these presentation issues.
Human listening and audible Narrator/NVDA acceptance remain pending; their worksheets
contain no invented pass results. Scientific and publication readiness require separate
independent review, annotations, validation, rights/consent and owner approvals.
