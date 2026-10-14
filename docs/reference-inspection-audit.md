# Reference inspection and PDF repair — 14 October 2026

TakeTwo — Speech analysis workspace. Inspected clean local `master` at
`5ab0e16a47f280325c8c3098d24a56d8a9309610` and the permanent root
[engineering/product standards](../AGENTS.md). This is a frontend presentation
repair; backend scientific eligibility and export contracts remain unchanged.

## Reproduced causes

The backend uses the same report contract for single-reference extraction and
paired comparison. The UI previously interpreted every report as a delivery
assessment: a successful reference inspection inherited `pair_missing`, comparison
blockers, Findings, the four-dimension agreement table and comparison pitch-score
language. Existing pairs were confused with the absence of a selected pair.

Report visibility was guarded by the current job request, but the stored report
value did not carry its job/artifact identity. Switching historical jobs could
associate an earlier value with a newly selected job before the fetch effect
cleared it. Reference/pair changes also needed synchronous invalidation.

Desktop outcomes stretched across the entire available workspace, including
1920 px displays. Reference printing reused the comparison layout and its page
break constraints, leaving a largely unnecessary agreement/inspector page.

Both supplied files were found and inspected read-only in Downloads:

| File | Size | A4 pages | Extractable text |
| --- | --- | --- | --- |
| `test.pdf` | 716003 bytes | 2 | Zero on both pages |
| `taketwotest.pdf` | 1695016 bytes | 5 | Zero on all five pages |

Both identify Microsoft Print to PDF as producer and are untagged. Rendered
`test.pdf` confirms a reference-only waveform/plot followed by a comparison table.
The application's print button calls `window.print()` on HTML; there is no
full-page screenshot PDF renderer. Canvas plots are individually snapshotted for
paper, while headings, metadata, measurements and tables remain HTML. Metadata
alone does not identify the precise external rasterization step. Browser-native
Save as PDF is the verified searchable path; system printer behavior is separate.

## Precise fixes

| Context | Presentation |
| --- | --- |
| Reference selected, not processed | Reference ready; participant comparison pending selection; inspection remains available |
| Reference queued/running | Reference audio analysis in progress; actual stage and cancellation |
| Reference failed/cancelled | Reference-specific failure/cancellation, original recovery and retry |
| Reference completed, report loading/unavailable | Reference completion with loading/unavailable measurements; reload when needed |
| Reference completed with measurements | **Reference audio analysis complete**, actual measurements and select/add participant action |
| Participant selected, not processed | Actual pair, participant-comparison mode and processing controls |
| Comparison awaiting scientific verification | Original backend abstention, unavailable scores and applicable review requirements |
| Eligible comparison | Original backend scores, observations and grounded finding controls |
| Eligible comparison with zero findings | Explicit no threshold crossings; no perfect-performance inference |

The reference result reports actual available pair count separately from selection.
It never states that no pair exists merely because none is selected. Transcript
review and unresolved rights remain secondary reference-specific information;
comparison timing requirements are not applied to a single current recording.
Findings, correspondence and comparison score tables are not mounted for reference
inspection. Scientific exports still preserve the original backend JSON/CSV.

Loaded report state now carries job ID and report path. Before display, the exact
job request, report pair ID and expected one/two recording provenance IDs must
match the current selection. Wrong identities produce recovery guidance, with no
measurements or print action. Selection/history changes clear report, selected
region and seek requests synchronously; delayed obsolete responses are ignored.
Refresh revalidates the same selected job without substituting another report.

Outcomes have a 1120 px maximum reading width. Wide comparison timelines retain
the full working width; mobile navigation and mounted track switching are
preserved. Raw feature/alignment diagnostics remain closed by default.

Reference printing has its own identity/status/use-requirements introduction,
waveform/plot and compact nine-field measurement summary. It omits comparison
scores and empty export boxes. Paired printing retains both tracks, backend
agreement table and input evidence. Both use semantic HTML text; the controlled
Chromium exports request tagged PDF. On-screen print guidance names the browser's
Save as PDF destination. No PDF service or new dependency was introduced.

## Executed verification

Fresh relevant baseline: 39 frontend tests passed. Full Python after implementation:
322 passed, one existing Starlette/httpx deprecation warning. Final frontend:
43 passed. TypeScript, ESLint, Prettier, Ruff lint/format, lock check, production
build and wheel/sdist build passed. Four schema snapshots and the official Track C
PDF hash match; regenerated frontend API definitions are unchanged. npm audit
reported zero vulnerabilities; pip-audit reported no known vulnerabilities for
the exported pinned dependencies. These audits are not proof of absence of all
security defects.

The new browser regression uses generated oscillator data and route-only software
states. It covers inspection with existing pairs and with no pairs, switching from
comparison to inspection, historical comparison restoration, refresh, delayed
responses, wrong report identity, focus of the participant selector, participant
import preparation, print content, font maps/text operators and tagged structure.
No route fixture changes stored evidence or grants genuine review approval.

Final fresh browser suite: **8 passed, 0 failed, 0 skipped**, in 3.8 minutes.
Existing import/processing/playback/export, five-workspace responsive controls,
native 200% zoom, native chart domains, scientific abstention, eligible/zero-finding
software UI states, mobile cursor/interval preservation and review capability/draft/
immutable submission cases all passed. The nonfatal Windows Proactor socket-reset
diagnostic occurred; no case failed. Browser `NO_COLOR` notices and pip-audit's
recommendation for hashed requirements are tool/environment notices.

The new case captured first-viewport and full-page screenshots for reference and
comparison at 320, 390, 800, 1366 and 1920 px: 20 PNGs. Both conclusions stayed in
the initial 740 px viewport. Axe found no violations in these states, and existing
five-workspace/native-zoom checks also passed. The ignored local index is
`local-data/inspection-screenshots.md`; original images are under
`local-data/inspection-final-results/zz-inspection-*`.

| Final native PDF | Pages | Extracted text characters by page | Size |
| --- | --- | --- | --- |
| Reference inspection | 1 | 1685 | 108052 bytes |
| Participant comparison | 3 | 939 / 677 / 1730 | 202608 bytes |

Both final outputs are tagged PDFs with font maps/text operators and searchable
headings, identity, status and measurements. pypdf checked actual extracted content:
the reference includes all nine measurements, no agreement table, no pair-missing
message and no requirements for both recordings. The comparison retains the actual
unavailable agreement table and both inputs. Poppler rendered all four final pages;
visual inspection found legible text/axes, complete plots and no clipped content
or unnecessary reference second page. Supplied older pages were also rendered
read-only; their screen controls/raw tables are absent from intended new print.

Final PDF QA caught a test-export mistake after the first successful full run:
explicit screen-media emulation remained active before saving. The test now saves
under the same print media used by its content assertions, then restores default
media. The complete fresh suite was rerun successfully and its corrected outputs
were re-extracted/rendered. Product printing was already using native print CSS.
The external Windows system-printer rasterization path is not claimed fixed or
manually verified; browser-native text preservation is verified.

Executed logs are ignored `local-data/inspection-{python,frontend-final,types-final,
lint-final,format-final,build,schema-final,e2e-final,pip-audit,precommit}.log` and
`inspection-npm-audit.json`. PDF extraction/tag/size evidence is
`inspection-pdf-verification.json`; private-file equality is
`inspection-integrity.json` (15 hashes, all unchanged).

During targeted verification, exact text-label selectors were replaced with
accessible combobox-role selectors; the participant selector has an explicit
stable name. A no-pairs route fixture now reloads inventory after restoring the
normal API, before testing historical comparison restoration. The final targeted
case passed. No existing test was removed.

## Scientific integrity and human limits

No changes to Python source/tests, scientific scripts, policy, dependencies,
schemas, locks or backend contracts. `acoustic-v1`, `delivery-v0`, consensus,
ground-truth selection, rights, reviewer independence, thresholds, abstention,
resource limits and artifact identity remain intact. No frontend score or flaw
calculation replaces backend results.

Fifteen hashes cover the five genuine WAVs, source workspace manifests/databases,
both technical-report files and the two supplied PDFs. Originals and genuine
reviewer drafts are untouched; all browser work uses isolated software workspaces.
Screenshots/PDFs remain ignored local artifacts. The separate six-page technical
report is not overwritten. AI assistance is disclosed in [attributions](attributions.md).

Genuine independent review, rights resolution and held-out speech accuracy remain
unresolved. Software eligibility fixtures establish presentation and interaction,
not human evidence. Spoken Narrator/NVDA acceptance and manual native-zoom visual
acceptance remain open; the isolated native Chromium zoom check supplies automated
geometry/focus/axe evidence, with the known headless screenshot capture limitation.
No push, publication or Devpost submission is performed.

## Local handoff

Implementation/regressions: `1ddc8da`; documentation is committed separately on
`master`. Final HEAD, clean working-tree status and post-commit release evidence
are reported at handoff and retained in ignored `local-data/inspection-final-git.txt`
and `local-data/inspection-release-final.log`.
