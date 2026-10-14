# Final hardening baseline audit

TakeTwo — Speech analysis workspace. Starting HEAD `24dc8a7`, clean `master`,
14 October 2026. This audit separates reproducible software defects, output-path
limitations and missing acceptance evidence. No source recording or scientific
policy may be changed to improve a readiness label.

## Reproduced print evidence

The owner's `taketwo21.pdf` (16 pages) and `taketwo2.pdf` (2 pages) were located
and inspected locally. Both declare `Microsoft: Print To PDF` as their producer.
PyMuPDF and the independent pypdf extractor return **zero text on every page**.
Both have zero font resources and no structure tree; their readable text is
represented by vector drawing paths. The analysis PDF contains 417–3,710 drawing
objects per page; dataset pages contain 1,342 and 1,133. Only the analysis chart
pages contain raster images. This is outlined text, not a missing OCR layer or
a report comprised entirely of screenshots.

The preserved Chromium paired summary has 2 pages, 2,260/2,015 PyMuPDF text
characters, four fonts on each page and a structure tree. Independent pypdf also
extracts its text. Current unchanged Chromium workspace printing reproduces
16 paired pages and 8 reference pages with extractable text. The concise/full
dedicated reports remain separate; the workspace print must not be mislabeled
as a dedicated Full Evidence Report.

The supplied analysis print's last page has an Evidence inspector followed by
an empty **Verified Assessment** heading. Current workspace printing reproduces
that empty heading. CSS hides `.analysis-outcome` while leaving the preceding
heading visible. Broad print rules also expand technical disclosures and place
the original acoustic appendices before the waveform tracks. Printing through
the workspace action clears `printScope` and does not select paired/reference
report mode, so the generic footer survives in the supplied output.

No custom webfont, font download or outlined-font authoring pipeline is present.
The same HTML/CSS generates searchable Chromium reports. The supplied files
establish vectorization in their Microsoft printer path; they do not establish
that every Microsoft printer/browser/version combination behaves this way.
Fresh system-printer reproduction requires the native Windows print dialog,
which browser-only automation cannot operate. Do not describe that unavailable
retest as executed or certify PDF/UA from text extraction or tagging alone.

## Findings and intended bounded repairs

| Finding | Classification / severity | Reproduction / cause | Intended response |
| --- | --- | --- | --- |
| No selectable text in the two supplied files | Confirmed output-path limitation / high | Both extractors return zero; font resources absent; vector paths present | Preserve files; verify Chromium Save as PDF for every supported report; explain destination choice |
| Empty final verification heading | Confirmed software defect / medium | Print current paired workspace; heading remains while outcome is hidden | Print a concise authoritative verification state and remove the duplicate heading |
| Workspace print expands all technical appendices | Confirmed product weakness / medium | Current paired workspace is 16 pages; charts follow appendices | Deliberate workspace view with selected findings and meaningful charts; retain complete dedicated evidence |
| Workspace footer lacks comparison identity | Confirmed software defect / medium | Supplied paired print says automatic inspection | Select paired/reference/dataset mode for button and ordinary browser printing; restore state afterward |
| Dataset print omits the selected recording name | Confirmed presentation defect / medium | Print hides the recording selector; only its label remains | Preserve recording and dataset identities as text |
| Dataset readiness provides one blocker, broad CLI help | Product weakness / medium | Rights-blocked recording shows a generic preparation action and help commands | Show each actual prerequisite, reason and legitimate location; document exact validated workflow |
| Connection-reset diagnostics | Observed operational limitation / investigate | WinError 10054 recurs in current baseline E2E | Reproduce abrupt resets and test service recovery; do not suppress unrelated faults |
| Cold restoration budget under load | Prior limitation / not yet reproduced in this stage | Previous reports describe request-budget expiry | Measure fresh process, cold/warm restoration and live-browser restart separately |
| Low accepted pitch coverage | Reproduced scientific/configuration limitation | Prior known-frequency/window/range/gain probes; unchanged 0.60/0.51% genuine coverage | Preserve null F0 and abstention; clarify still-valid duration/energy measurements |
| Human listening / spoken accessibility | Missing acceptance evidence | Owner explicitly reports no audio heard in Test 1; no genuine Narrator/NVDA review | Keep pending; provide exact owner-executable checks |
| Independent annotations, rights and held-out corpus | Human/legal/scientific dependency | Five takes, one declared speaker/family, zero reviewed text/timing/flaws/evaluation | Prepare legitimate version/import/evaluation handoff; never manufacture evidence |

## Baseline and preservation

Executed current baseline: 372 Python tests passed (233.57 s, one upstream
Starlette warning), 73 frontend tests passed (30.66 s), 13 generated browser
tests passed (4.3 min). TypeScript, ESLint, Prettier and production build passed.
The fresh genuine baseline passed all three tests (4.3 min) against the unchanged
built frontend: five real imports, fresh MFA/features, native replay, exports and
actual 200% Chromium tab zoom. Windows reset diagnostics recurred without a failed
baseline workflow; no universal reliability claim follows from these passes.

Thirty-eight protected file hashes are captured privately: the prior 28 protected
files, four final PDFs, the two supplied printer PDFs, the prior listening record
and its exact audio excerpts/provenance. All prior hashes matched before work.
Private recordings, PDFs, screenshots, reviewer observations and operational
traces remain outside Git. Existing architecture, scientific/review contracts,
release, CI, pitch and acceptance documentation were inspected before repair.

Stages: print repair; readiness guidance; Windows recovery measurements; human
handoffs; accessible interaction verification; full regression/release audit.
The [completion report](final-hardening-completion.md) will contain final evidence
and limitations. No push, publication, deployment or external submission.
