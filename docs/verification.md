# Verification and known limitations

TakeTwo — Speech analysis workspace.

Software fixtures verify implementation behavior. Genuine processing verifies that
real samples traverse the pipeline; neither establishes independent speech accuracy,
recording permissions, human listening acceptance or production readiness.

## Reproduce the checks

Use the locked [Windows setup](windows-setup.md), then the commands in
[reproducibility](reproducibility.md). Build the frontend before full pytest:
launcher and recovery tests start the complete application. Keep heavy native jobs
serial. [Browser testing](browser-testing.md) documents generated signals, optional
private genuine inputs, isolated workspaces and native zoom separately.

Current cleanup checks are recorded below after execution. Hosted CI must be checked
for the exact published commit; a previous green run does not certify later commits.

## Scientific and operational limits

- Five private same-speaker takes form one connected family, with no independent
  transcript/timing/flaw ground truth or approved public paired dataset. Genuine
  precision/recall/F1, boundary accuracy and cross-speaker generalization are unavailable.
- Delivery-v0 is uncalibrated. Missing evidence withholds scores without redistributing
  weights. Automatic alignment may fit incorrect words; timing remains provisional.
- Raw pYIN voiced coverage on the five takes was 69.3–76.4%, but accepted coverage was
  only 0.284–0.617%. Known 80/120/200/400 Hz controls accepted 0/0/100/100% despite
  accurate raw frequency. Production confidence remains 0.8; [pitch investigation](pitch-investigation.md)
  retains full diagnostics, probes and unresolved real-F0 validation.
- Cold evidence requests can exceed their 15 s budgets under contention. The measured
  29.431 s successful cold selection spans sequential requests; later cold attempts
  still timed out. Warm success does not close this limitation.
- Three Windows Proactor reset trials lost the listener with WinError 64; three
  Selector trials survived 30 resets each with identical content. Windows uses
  Selector within its 512-socket/no-asyncio-subprocess-pipe constraints. WinError
  10054 was observed separately and its broader cause remains unestablished.
  [Windows evidence](windows-hardening-evidence.md) preserves trials and telemetry.
- Native 200% tab zoom and automated focus/axe checks have passed historically.
  Headless zoom captures had blank/cropped limitations; actual human visual and
  [spoken accessibility acceptance](spoken-accessibility-acceptance.md) remain pending.
  Searchable/tagged PDFs do not establish PDF/UA or assistive reading order.
- Actual [human listening](comparative-listening-acceptance.md), clean second-machine
  replay, power-loss durability and independent scientific evaluation remain open.
  Reviewer capabilities do not authenticate people or defeat the trusted OS owner.

## Retained engineering evidence

The table consolidates superseded phase/audit reports removed from the current tree.
Each source link pins the complete original at the pre-cleanup revision
`0cdb837522de2957b147c48ce8d83f9b0b2c032a`; exact commands, hashes, intermediate
failures and private evidence locations remain traceable there. Dates and counts
below describe those historical runs, not a new execution. Original experiments and
private artifacts were not rewritten, moved or published.

| Historical source | Evidence retained / reason the separate report is redundant |
| --- | --- |
| [Phase 1](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/phase1-validation.md), 11 Oct | 114 Python tests, 74.87 s. libsndfile's volatile float-WAV PEAK timestamp required deterministic headers. Independent rebuilt smoke manifests/derivatives matched; publication correctly rejected 13 missing-evidence errors. Current dataset contract and reproduction guide supersede the roadmap. |
| [Phase 2](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/phase2-validation.md), 11 Oct | 155 Python tests, 81.75 s. Native MFA 3.3.9 aligned the unverified 17.3 s JFK candidate into 19 words/115 phones, identical boundaries on repeat. BLAS differences up to 1.42e-14 led to single-thread extraction. Final alignment/extraction 86.943/10.788 s; sampled working sets 1,944,772,608/269,778,944 bytes. Current engine guide and acquisition ledger retain the supported setup. |
| [Phase 3](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/phase3-validation.md), 11 Oct | 197 Python tests, 203.40 s; real CLI comparison/evaluation exit 3 with unavailable metrics. Evidence CLI 7.220 s / sampled tree working set 182,534,144 bytes. Hand-calculated rubric fixtures are software evidence. Current comparison/scoring docs supersede the implementation checklist. |
| [Phase 4](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/phase4-validation.md), 11 Oct | 212 Python / 7 frontend tests. Windows stage replacement sharing violations required bounded retry; generated and genuine browser workflows then passed. Current architecture/API describe worker lifecycle. |
| [Phase 4B](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/phase4b-validation.md), 12 Oct | 217 Python tests, 162.08 s. Actual MFA descendant stopped 0.049 s after service kill; cancellation 0.334 s, explicit retry succeeded. Genuine job 187.422 s / peak worker commit 1,892,315,136 bytes; cached 8.859 s. Peak commit is distinct from sampled working set. Unknown locks/corrupt caches refused; screen-reader/zoom attempts were unverified then. |
| [Phase 5](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/phase5-validation.md), 12 Oct | 217 Python tests, 181.29 s / 7 frontend. Genuine browser 255.927 s; job 200.469 s / commit 1,899,757,568 bytes. First workflow exceeded the test envelope; final processing passed, not scientific evaluation. Six-page historical report and original failure records remain in Git. |
| [Product validation](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/product-validation.md), 12 Oct | 235 Python tests, 378.15 s / 11 frontend. Fifteen import/pairing/excerpt/history/rights/selection defects addressed, including unspecified labels and immutable corrections. Five private originals matched imported bytes. Initial stale schema, 320 px fieldset overflow and cold-report assertion failures were corrected; old 30 s limits are superseded by duration validation. |
| [Review workspace](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/review-workspace-validation.md), 12 Oct | 264 Python tests, 153.52 s / 20 frontend; two generated browser tests, native zoom skipped. Genuine JSON phrase arrays exposed strict HTTP tuple-validation mismatch; adapter fixed without weakening scientific contracts. Genuine job 102.062 s / commit 1,893,294,080 bytes, five unresolved drafts and no approvals. Current review guide replaces the handoff. |
| [Repair audit](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/final-repair-audit.md), 13 Oct | 296 Python tests, 481.46 s / 20 frontend. Greedy matching gave TP=1/FP=1/FN=1 where two matches existed; matching-v2 gives TP=2/FP=0/FN=0, tested against 30 exhaustive small graphs. Semantic-v2 ignores UUID/prose and checks coverage; journaled review publication survives process kills. These are software regressions, not speech accuracy. Current methods retain policies. |
| [CI repair](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/ci-submission-validation-2026-10-13.md), 13 Oct | Published 35a1486 failed three launcher/recovery tests because frontend build ran after pytest. Clean-checkout reproduction led to corrected CI order. CRLF caused 24 Prettier failures; LF attributes fixed checkout behavior. Sdist originally included 8,323 node_modules files; explicit Hatch inputs/package negative controls fixed leakage. Final 301 Python / 20 frontend / 3 generated browser tests. |
| [CI status](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/ci-submission-validation.md), 13 Oct | cd2abe9 passed run 38357432224 after failed run 38350507487. This status sheet is superseded by exact-commit release evidence, not proof of current hosted CI. |
| [Stabilization](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/stabilization-audit.md), 13 Oct | 316 Python tests, 288.93 s / 21 frontend / 4 generated browser. Reviews 0–1 s vs 0.2–1.2 s change a 0–0.5 s prediction's match: exact-inventory-v1 withholds metrics until revisions agree; never select the first reviewer. MFA version/stage timeout and PermissionError attempts remain unresolved; a short-workspace original-config genuine run passed in 261.548 s, not a proven path-length fix. Private diagnostics capped at 32 KiB. Same-host clean setup/start 151.103/12.482 s is not second-machine validation. |
| [Presentation repair](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/presentation-repair-audit.md), 13 Oct | 322 Python tests, 186.14 s / 31 frontend / 5 generated browser. Takes separated from people, missing pitch gates remain unavailable, print redraw fixes screen-width canvas clipping; a visible 22 s cutoff was presentation, not truncated extraction. Boundary fixtures cover 15/29/30/40/45 s. First browser run 1 failed/4 passed (encoding); final passed. |
| [Product experience](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/product-experience-audit.md), 13 Oct | 322 Python tests, 320.73 s / 37 frontend / 6 generated browser. Distinct pending/partial/eligible/eligible-zero states, bounded replay and rejected-heartbeat continuity. Route-only eligible UI fixtures never grant genuine review. 25 genuine area/width checks had zero axe violations; spoken acceptance remains open. |
| [Mobile refinement](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/mobile-refinement-audit.md), 14 Oct | 322 Python / 39 frontend / 7 browser tests. Collection belongs in Library; phone selector and independent-track switch preserve cursors. Initial 5 pass/2 fail exposed pre-mount navigation and accessible-name issues, then fixed. Three-page private print rendered both tracks. Current frontend/design guides describe the final interface. |
| [Reference inspection](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/reference-inspection-audit.md), 14 Oct | 322 Python / 43 frontend / 8 browser tests. Reference completion no longer implies paired comparison failure. Supplied printer PDFs (2/5 pages) had zero extractable text; Chromium outputs retained fonts/text/tags. Current exports guide supersedes the repair narrative; no universal printer or PDF/UA claim. |
| [Product completion](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/product-completion-report.md), 14 Oct | 340 Python / 55 frontend / 10 browser tests; 49 affected backend checks rerun after cache ordering repair. Reviews 503 previously hid successful inventory; independent refresh preserves partial results. Bounded source-checked caching improved repeat observations (3.013→0.131, 6.536→0.218, 8.667→0.233 s), not a universal speed benchmark. Current exploratory guide retains methods. |
| [Comparative insights](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/comparative-insights-completion.md), 14 Oct | 369 Python / 62 frontend / 12 generated and 3 genuine browser tests. 53 windows→44 groups, 71 provisional words, one anomaly, 74 items; reference 28→22. Missing/corrupt artifacts distinguish 404/422, interim chart overflow and full-domain reset repaired. Original Not Found screenshot cause not reproduced. First genuine timeout retained; final uncached job 262.453 s / commit 2,076,827,648 bytes. Current comparative methods retain exact selection/grouping rules. |
| [Comparative refinement](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/comparative-refinement-completion.md), 14 Oct | 372 Python tests, 217.46 s / 66 frontend / 13 generated and 3 genuine browser. All 25 remaining overlapping groups oppose direction; smallest compatible positive gap 0.5 s, so no extra merging justified. Earlier full run failed real heartbeat gate at 0.975466/2 s coverage; isolated replay passed without relaxing gate. Summary/full exports retain complete evidence. |
| [Report polish audit](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/final-report-polish-audit.md), 14 Oct | Excess front matter pushed the leading intact finding off page one; shared prose incorrectly promised a summary appendix and generic footer. Root causes and fixes are consolidated in the next row and current export guide. |
| [Final product acceptance](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/final-product-acceptance.md), 14 Oct | 372 Python tests, 249.56 s / 73 frontend / 13 generated and 3 genuine browser. Summaries 2/2 pages, evidence 13/7; leading findings page one, 9.5 pt summaries, correct export-specific footers. QA covers 169 paired/50 reference evidence IDs, CSV fields, bounds and table headers. Human acceptance remained pending. |
| [Final hardening](https://github.com/Rhythm-Sanghi/TakeTwo/blob/0cdb837522de2957b147c48ce8d83f9b0b2c032a/docs/final-hardening-completion.md), 14 Oct | 376 Python tests, 873.66 s / 81 frontend / 18 generated and 3 genuine browser; 25 genuine views. Seven exports/33 rendered pages passed dual extraction and visual QA. All 38 then-protected hashes matched. Initial browser run 14 pass/3 fail; final 18 passed after readiness, outage recovery and print repairs. Concurrent frontend/crash/cold-load failures retained, not counted as passes. |

## Important measured findings

The genuine reference/uneven comparison measured 30.224375/29.370 s, a duration
delta of −0.854375 s (−2.826775%) and RMS delta +0.0438473107 dB. These do not
establish pacing, emphasis or perceptual significance. Provisional `technology → is`
replay intervals were reference 10.93–11.88 s / participant 10.12–13.47 s. Its
2.890 s machine gap had **0.000 s low-energy support**; silence/hesitation cannot
be inferred. Gaps before `helps` and `a` differed +0.560/−0.510 s. Listening and
independent phrase/timing annotation remain necessary.

The two supplied Microsoft printer outputs contained outlined vector text, zero
fonts and no structure tree; one had 417–3,710 drawing objects per page. Chromium
retained text/fonts. This demonstrates an output-path difference, not an identified
universal driver cause. Final historical paired/reference summaries/evidence were
2/13/2/7 pages; workspace prints 4/2 and dataset readiness 3 (33 pages total).
Source-of-truth JSON/CSV inventories were preserved. See [export QA](report-export-guide.md).

Focused research remains in the current tree: [acquisition/provenance](pilot-collection.md),
[45 s capacity](duration-validation.md), [pitch](pitch-investigation.md) and
[Windows restoration](windows-hardening-evidence.md). The 45 s workload measured
223.516 s / 2,113,093,632-byte peak tree commit; both alignments produced 60 words/
265 phones and null scores. Windows cold-cache repair reduced six duplicate validations
of one 25,592,607-byte artifact (29.187 s) to one validation (4.412 s), preserving
models and identity checks. Neither observation establishes general throughput.

The superseded `docs/technical-report-2026-10-12.md` and
`output/pdf/taketwo-technical-report.pdf` are retained at that same immutable Git
revision. They describe earlier limits/status and are replaced in the current tree
by the unchanged [current report source](technical-report.md) and
[15 October report](../output/pdf/taketwo-technical-report-2026-10-15.pdf).
Its original numbered references remain a historical snapshot; reference [5]'s
hardening evidence is the pinned original above. `ACTION-REQUIRED.md` is consolidated
into [submission readiness](publication-readiness.md) and its owner checklist.

## Cleanup verification, 15 October 2026

Cleanup baseline: fetched local/remote `master` at
`0cdb837522de2957b147c48ce8d83f9b0b2c032a`, initially clean. Inventory read all
219 tracked files and indexed references, Python symbols and document links.
The final public tree has 195 files: 25 redundant files removed and this consolidated
verification document added. No helper script was proven unused; all 15 remain.
At that baseline, root `AGENTS.md` was retained. It is now an optional, ignored
local development file, excluded from public sources and packages; checkout
verification does not require it.

| Executed check | Result |
| --- | --- |
| Full backend `uv run pytest -q` | **376 passed**, 207.51 s; one existing Starlette/httpx deprecation warning |
| Frontend `npm --prefix frontend test -- --maxWorkers=1` | **81 passed**, nine files, 37.67 s |
| Generated browser `npm --prefix frontend run e2e` | **18 passed**, zero failed/skipped, 3.7 min; fresh isolated workspace/port 9015, including real CPU processing, native 200% zoom, review isolation, printing and error recovery |
| Python Ruff lint / format | Passed; 79 Python files already formatted |
| Frontend ESLint / TypeScript / Prettier | Passed |
| Frontend production build | Passed; JS 447.73 kB / 138.27 kB gzip, CSS 23.86 kB / 5.62 kB gzip |
| `uv lock --check` / `uv build --no-sources` | Passed; 49 locked packages; wheel and sdist built |
| Repository/schema/specification checks | Local Markdown files and links resolve; all six current runtime schemas match, official PDF SHA-256 unchanged |
| Supplemental Markdown check | File targets and heading fragments checked across README, AGENTS and docs; no broken links or fragments |
| Release/history/package preflight | 195 candidates / 726 pre-commit reachable history blobs; zero blocking candidate/history/package findings or personal absolute-path files |
| Preserved byte identities | **154** source/runtime/test/tool/CI/lock/schema/standard/license/current-report/screenshot inputs unchanged; only the obsolete PDF sdist entry removed from packaging configuration |
| Current technical PDF | Six pages rendered and visually inspected; all 45 source blocks found by both pypdf and pdfplumber; report PDF and source unchanged |
| Documented normal launcher | Fresh isolated workspace on port 9016 reached health and served branded frontend (HTTP 200 each) in 4.672 s; owned process tree stopped afterward |
| Git whitespace | `git diff --check` passed |

Private genuine suites were not rerun for this documentation cleanup. Their historical
results above remain distinct from the newly executed generated browser suite.
No dependency vulnerability audit was rerun; locks did not change. Source/history/
package preflight is a pattern and inventory check, not exhaustive security or
rights certification. Poppler text extraction was unavailable in the bundled tools;
PDF source comparison used pypdf/pdfplumber and Poppler rendering succeeded.

The current report remains a dated scientific/submission snapshot; its original
references resolve through the immutable sources above. The older source/PDF are
removed from the current tree, not from Git history. The official statement stays
at `requirments/Track C.pdf` because its exact path and digest are used by checks and
packaging. Private WAVs, models, databases, consent and reviewer records are excluded
from release candidates/packages. Local evidence and the complete per-file deletion/
inventory/tree review are ignored under `local-data/repository-cleanup/`.

Push and hosted CI for the cleanup remain pending owner authorization. Dataset,
independent human annotation/evaluation, real listening/spoken acceptance and clean
second-machine blockers remain open. No claim of complete submission or production
readiness follows from these software checks.
