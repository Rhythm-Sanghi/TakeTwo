# Stabilization audit — 13 October 2026

TakeTwo — Speech analysis workspace. Starting checkout: clean `master`,
`cd2abe946b40892e3d164428f74b5acd92860d0d`, tracking `origin/master`.
This pass makes local commits only. Historical audits and private evidence remain intact.

Engineering commits on the existing master branch:
`86d1e57` requires exact independent ground truth; `a5e60cf` repairs responsive
selectors, diagnostic presentation and browser fixture isolation; `f8d7769`
retains bounded private worker failure diagnostics. The final
documentation commit and clean working-tree/remote check are identified in the
handoff. No new branch, force operation, push or external artifact publication
is performed. Remote master remains cd2abe9 until an owner-authorized release.

## Working defect register

| Priority / state | Evidence and root cause | Affected files | Acceptance |
| --- | --- | --- | --- |
| P1 / VERIFIED repair | Evaluation used `accepted[0].labels`; agreeing 0–1 s and 0.2–1.2 s reviews gave different matches for a 0–0.5 s prediction | comparison/evaluation.py, reviews.py; review workspace status | Counterexample now abstains; ID/list permutations, exact labels and explicit revisions pass |
| P2 / VERIFIED repair | Current documents called 35a1486 the latest public commit and CI red | README, current submission documents | Actual successful cd2abe9 run linked; later local work separate; historical audit blob preserved |
| P2 / VERIFIED repair | Long pair selector extended to x=440 at a 390-pixel viewport | frontend/style.css, workspace browser regression | Populated five-area screenshots pass at all five widths |
| P2 / VERIFIED repair | Software review test selected genuine clip and used a 15-second playback wait | frontend/tests/zz-review.spec.ts | Named two-second tone is asserted/imported; standalone and genuine runs pass |
| P2 / VERIFIED diagnostic repair | Unexpected worker exception details were discarded | web/worker.py, jobs.py; release preflight | Bounded private trace, redacted API, blocked-storage and package exclusion checks pass |
| Limitation / retained | Low pYIN acceptance is reproduced; no new implementation defect established | acoustic-v1, pitch diagnostics | Nulls and 0.8 threshold preserved; independent F0 accuracy remains unavailable |
| INCOMPLETE investigation | Earlier longer-workspace native MFA timeouts/permission failure; short-workspace run passes | native environment, test workspaces | Actual successful setup retained; cause and general reliability are not established |
| Human/external blockers | No independent genuine labels, release consent, public paired corpus or video | submission materials | Explicit incomplete/blocked status; no fabricated approval or external publication |

## Baseline evidence

GitHub API confirms [run 38357432224](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38357432224)
completed successfully at cd2abe9 on 13 October 2026. The earlier failed
[run 38350507487](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38350507487)
remains historical evidence. Existing loopback service responds ready, with alignment
configured, 45-second analysis limit, 100 MiB upload limit and 4 GiB worker protection.
No original workspace is modified for testing.

The [organizer rules](https://multimodal-ai-hackathon-2026-7.devpost.com/rules)
confirm October 15, 2026 at 00:15 IST and require AI-tool disclosure. Their linked
Drive viewer does not expose PDF text to this browser tool; the checked-in Track C
PDF is the detailed requirement authority. No claim of a fresh byte comparison
against the hosted problem statement is made.

## Defect resolutions

### P1: reviewer-dependent ground truth

The original 0–1 s / 0.2–1.2 s counterexample was reproduced with a failing test:
baseline evaluation returned TP=1 rather than abstaining. Semantic agreement
permits those intervals, while a 0–0.5 s prediction matches only the former.

`exact-inventory-v1` now requires identical numerical label multisets after normal
independence, blinding, identity, coverage and supersession validation. It excludes
IDs/prose, never averages boundaries, and derives evaluation label IDs from pair,
numerical content and sorted occurrence. Retained original review hashes identify
every source, including revisions; the canonical inventory can be reconstructed
with `resolved_flaws`. Different numerical inventories withhold aggregate metrics.
This conservative policy also blocks differences that leave TP counts unchanged
but alter boundary errors or clean-time denominators. It is not perceptual calibration.

Review inventory and adjudication use the same resolution gate. An operator note
cannot unlock evaluation; explicit same-author revisions can resolve the issue
without deleting original evidence or decision history. Review/Evaluation v1
schemas are unchanged. Historical artifacts remain readable and immutable; old
first-review metrics must be recomputed against current source, not relabeled.

New tests cover the original counterexample, reviewer ID/list permutations,
annotation ID/list permutations, independent wording, equivalent exact labels,
empty/multiple inventories, three reviewers, overlapping detections, categories,
severity, null versus zero uncertainty, interval/event differences, revisions,
forked authorship, adjudication preservation, fresh-process replay, tampering and
threshold-edge IoU. Existing maximum-cardinality/quality, invalid identity/timing,
family leakage and mathematically undefined metric regressions remain intact.

### P2: populated narrow-screen selector overflow

The new screenshot regression passed on an empty workspace, then failed on six
generated recordings: at 390 pixels the participant-pair label/select extended
to x=440. A long excerpt filename gave the flex label an intrinsic minimum width.
Added `min-width: 0; max-width: 100%` to toolbar labels. The populated regression
now passes all five workspaces at 1920×1080, 1366×768, 800, 390 and 320 pixels.
Screenshots are retained privately under `local-data/stabilization-overflow-fixed`;
the failed captures and before/after image remain separate. No theme changes,
hidden critical controls or speculative frontend restructuring were needed.

Withheld-score UI now shows explanatory recovery messages first. Exact backend
reason codes remain available in collapsed diagnostics and exports. The focused
frontend regression failed before the change and passed afterward.

Persisted evaluation history now explicitly warns that runs predating
exact-inventory-v1 may depend on reviewer ordering and need recomputation before
use as current evidence. Original metrics/artifacts remain inspectable. Comparison
report endpoints already reject changed source/upstream identities; that existing
stale-report protection is preserved.

### P2: current-status documents report obsolete failed CI

Reconciled README, compliance, requirements, owner checklist, submission draft,
demo script and current report against successful public cd2abe9 CI. Preserved the
entire previous CI report in `ci-submission-validation-2026-10-13.md`, unchanged;
other dated historical reports remain untouched. Later local work is explicitly
separate from the hosted baseline. No new hosted result or publication is claimed.

### P2: optional genuine suite uses software-review assumptions

An actual optional run failed with processing still running at its 210-second
fixture wait. The unchanged service permits 600 seconds. Genuine polling now
observes that terminal deadline with a 630-second test budget and still fails
immediately on a failed job; generated processing retains its original budget.
No production deadline or scientific gate changed.

The same run's software-review test selected the first reference, a 17.3-second
archival recording, then waited only 15 seconds for playback. That also risked
attaching intentionally wrong software-review transcripts to a genuine fixture.
It now explicitly finds/imports the named two-second generated tone and asserts
its duration/transcript before creating clearly marked software submissions.
All testing remains in disposable isolated workspaces, never real review records.

The repaired review workflow also passed alone against an empty fresh workspace
(**one passed, 48.9 s**), exercising the new tone-import branch rather than relying
on an earlier test's recordings. Its actual playback/submissions remain explicitly
software fixtures.

## Scientific and security findings

Matching remains maximum cardinality then total quality, like category/location
types, with pinned assignment ties. Canonical ground-truth IDs remove source-label
ID dependence from those ties. Full coverage and positive-category evidence gates
remain conservative. Null denominators, absent/constant severity correlation and
all undefined bootstrap resamples remain unavailable rather than perfect scores.
No detection threshold, acoustic-v1 or delivery-v0 rule was changed.

Pitch control acceptance reproduced 0/0/100/100% at 80/120/200/400 Hz; the five
isolated private takes reproduce 0.284–0.617% accepted pitch coverage. No new
implementation defect or independent F0 accuracy is established. Keep confidence
0.8 and null pitch. [Pitch evidence](pitch-investigation.md) records exact values.

Inspected loopback/origin/content-length controls, path confinement and Windows
reparse rejection, bounded uploads/JSON, capability cookies/handoff, draft revision
conflicts, immutable journaled publication, hash-bound cache/replay, worker launch,
cancellation/crash recovery and resource protection. Existing tests exercise these
boundaries; no additional confirmed production security defect was found.
Bandit's final scan covered 7,422 source lines with zero medium/high findings and zero scan
errors; this is not proof of complete security. Python/npm dependency audits found
no known vulnerabilities. Release preflight and wheel/sdist checks found no
blocking candidates. The historical report and official PDF still require their
respective rights context; the current PDF remains Git-ignored.

Reviewer capabilities still do not authenticate people or defeat the OS owner.
No enterprise authentication was added. No private recordings, tokens, databases,
models, consents or unreviewed current PDF are staged for publication. Earlier
unreachable private Git objects remain outside publication refs; do not share the
whole checkout. Root AGENTS.md already contains all supplied permanent standards
and remains the engineering/product authority.

## Verification ledger

Baseline: 301 Python tests passed in 150.81 s (zero failed/skipped, one existing
Starlette/httpx deprecation warning); 20 frontend tests passed in 21.96 s.
The first post-correction full Python run passed 311 tests in 132.35 s. After
threshold-edge and overlapping-prediction additions and fixture corrections,
the final full run passed **313 tests**, zero failures/skips, one existing warning,
in **744.33 s**. Runtime variation is retained, not advertised as an improvement.
After adding private worker diagnostics, the final complete backend suite passed
**316 tests**, zero failures/skips, one existing warning, in **288.93 s**. All
original tests remain; three new cases cover privacy, truncation and unavailable
log storage. Source lint/format checks pass after removing an unnecessary explicit
UTF-8 argument flagged by Ruff; byte behavior is unchanged.
Frontend now passes 21 tests; strict TypeScript, ESLint, Prettier, Ruff,
repository links/schema snapshots and unchanged official-PDF hash checks passed.
Python wheel/sdist and production frontend builds succeeded. Locked dependency
validation and Python/npm vulnerability checks executed successfully.

Failures are retained: original scientific regression; an initial restart fixture
used Python validation for JSON tuple fields, then the expanded prediction fixture
referenced an observation absent from its saved report. Corrected both test inputs
without weakening production validation. One Ruff pass found two overlong lines;
they were shortened. One Prettier pass caught the new diagnostic test formatting;
it was corrected. A PDF rendering attempt found PyMuPDF absent; bundled Poppler
rendered the report successfully without new application dependencies.

Initial browser run: two passed, one skipped because default full Chromium could
not launch. The isolated known-working installation verified actual tab zoom 2.0,
doubled DPR, halved layout width, focus and axe across all five areas. Another
populated run failed the reproduced selector overflow; the fixed responsive run
passed all 25 captures. A subsequent full attempt had a Playwright worker process
exit with Windows code 3221226505 before its first workflow; the other three tests
passed. The underlying process failure is not claimed repaired. Final isolated
suite results must be recorded separately, never inferred from partial successes.

Final isolated generated browser run: **four passed**, zero failed/skipped, **58.5 s**.
It covers real import/CPU processing, playback/export, cancellation/retry/cache,
all five workspaces at five widths, actual native 200% tab zoom with focus/axe,
and generated-tone review handoff, immutable export and adjudication. Captures are
retained under `local-data/stabilization-browser-final-isolated`. These results
verify software; Narrator/NVDA spoken acceptance remains incomplete.

The genuine measured attempt failed two tests as described above; total wall time
346.843 s, sampled entire browser/service tree working set 2,069,385,216 bytes.
This failed workflow is not a successful MFA benchmark or worker commit measurement.
No performance optimization or speed gain is claimed. Preserve one CPU worker,
4 GiB worker commit, 600-second deadline, 45-second member analysis and 600-second
import boundaries. Existing cache/duplicate-request tests verify reuse; genuine
speed and memory measurements remain workload/environment-specific.

A later isolated genuine attempt completed extraction but failed the required
alignment assertion: the saved alignment reports `timeout` with `backend_version`
because MFA's separate 30-second version startup check did not finish. Three other
browser tests passed. Total 159.733 s, sampled entire-tree working set
1,754,714,112 bytes. This is not successful forced alignment. Direct configured
MFA version diagnosis then returned **3.3.9**, exit 0, in **21.798 s**. The launch
timeout was not reproduced by that probe; no causal repair or changed guard is
claimed. Retain both measurements and keep the 30-second version protection.

The next native retry passed version checking but the align subprocess reached
the configured **180-second** stage guard after corpus loading/text normalization.
The browser suite had one failure and three passes; complete workflow 349.802 s,
sampled entire-tree working set 2,179,592,192 bytes, actual job peak worker commit
1,370,738,688 bytes. No out-of-memory cause or algorithmic error is established.
An additional diagnostic uses a separate private test config with a 360-second
alignment-stage budget, within the unchanged 600-second supervised job deadline.
The original 180-second config, acoustic/scoring rules, 30-second version guard,
4 GiB worker bound and original audio remain unchanged. Different operational
configurations have different bound hashes; do not patch old artifacts to match.

The 360-second diagnostic failed with a sanitized `PermissionError`, not successful
alignment (one failed, three passed; 543.621 s, sampled entire-tree working set
2,213,642,240 bytes). The old worker discarded private traceback details. A focused
failing regression now drives bounded private diagnostic retention: the original
HTTP error stays redacted; `.diagnostics/<job-id>.log` keeps at most 32 KiB and is
ignored/excluded from release candidates. Log-write failure cannot replace the
original processing error. This repairs observability, not the unproven cause of
native MFA failure. A large-message test initially exposed lost exception type
after truncation; a bounded type header preserves it. Additional native diagnosis
uses a fresh short external temporary workspace and the original 180-second config;
no path-length cause is claimed without evidence.

A frontend rerun overlapping native diagnosis had 16 passes/five five-second test
timeouts. It is retained as a failed attempt; frontend timeouts are not increased.
The final isolated frontend rerun passed **all 21 tests in 11.02 s**, with zero
failures/skips. TypeScript, ESLint, Prettier and the production frontend build
also passed against the final source, including the historical-evaluation notice.

The controlled short-workspace probe **passed all four genuine browser tests**
with the **original 180-second config**, zero skips, in 4.3 minutes (measured full
process workflow **261.548 s**; sampled entire-tree working set **2,371,076,096
bytes**). Actual MFA alignment, acoustic extraction, playback, export, responsive
screens, native zoom and explicitly generated-tone reviews executed successfully.
This verifies that setup, not independent alignment accuracy or a universal fix.
One nonfatal Windows asyncio connection-reset callback was logged during browser
navigation; all assertions completed. Original long-workspace failures remain
unresolved environmental/reliability observations; path length is a hypothesis,
not an established cause. Do not present the larger stage-budget experiment as
a repair. The original config and private service remain unchanged.

Successful genuine artifact summary: MFA **3.3.9**, **19 words / 115 phones**;
alignment stage **166.937 s**, extraction **10.141 s**, comparison **0.390 s**,
peak supervised worker commit **1,887,477,760 bytes**. Overall score remains null;
these are processing measurements, not ground-truth accuracy. No acoustic or
scientific policy changed. A generated private-log wheel negative control was
rejected by package preflight, verifying that diagnostic traces cannot silently
enter the release manifest.

## Clean checkout and startup evidence

Created a fresh same-host clone via Git transport (`--no-local`), transferring
reachable history rather than copying unreachable private objects or runtime
directories. Fast-forwarded it to the code/UI commit `a5e60cf`. Ran the exact
documented `scripts/start-local.ps1 -Setup` against a fresh empty workspace on
port 8878: locked uv sync, npm ci and frontend build reached ready health in
**151.103 s**. Normal documented startup reused those installations/build and
reached health in **12.482 s**. Both returned zero recordings, correct TakeTwo
branding, explicit missing-alignment diagnostics and unchanged resource limits.
The harness stopped only its owned launcher tree; the original private service
was not restarted. These are current setup/startup measurements, not controlled
before/after gains or evidence of second-machine compatibility.

The clean clone's complete comparison suite passed **70 tests in 223.40 s**,
including persisted restart, threshold and permutation checks against the committed
LF checkout. The final root run covers the complete 316-test backend suite;
the full backend suite was not duplicated in the clone. Byte-based source hashes
can differ from historical mixed-line-ending workspaces; retained old artifacts
are not patched to bypass that binding.

Clean-clone frontend: **21 tests passed**, zero failures/skips, **70.11 s**.
Ruff lint/format and Prettier also passed on the fresh LF checkout. This verifies
the documented setup on this Windows host, not a second independent machine.

The clone was subsequently fast-forwarded to `f8d7769`; all three private worker
diagnostic regressions passed in **2.95 s** on that checkout.

## Final verification reconciliation

| Final check | Executed result |
| --- | --- |
| Complete backend suite | 316 passed, zero failed/skipped, 288.93 s; one existing Starlette/httpx warning |
| Frontend unit suite | 21 passed, zero failed/skipped, 11.02 s |
| Generated browser workflow | Four passed, zero failed/skipped, 2.7 minutes as rounded by the reporter |
| Genuine native browser workflow | Four passed, zero failed/skipped, measured 261.548 s in the controlled short workspace with the original configuration |
| Private preservation snapshot | All 11 snapshotted files retain their original SHA-256; zero changed or missing |

The final generated run supersedes the earlier 58.5-second isolated run as the
last browser verification; both evidence sets remain private. Runtime variation
is not a performance improvement claim. The original service still has five
recordings, zero reviews and one family; it was not restarted or used to invent
human approvals. Save any open drafts and restart it when idle to load the new
backend policy and interface. General native reliability, spoken accessibility
acceptance and a genuinely independent second-machine replay remain incomplete.

## Materials and owner gates

The current technical report remains an owner-review draft at the ignored
`output/pdf/taketwo-technical-report-current.pdf`; six A4 pages were rendered with
Poppler and every page visually inspected. Its editable source records the current
methodology, genuine-data limits, tool attribution and public baseline CI. The
historical PDF/source and official statement remain unchanged. Its final source
and six rendered pages reflect the reconciled verification counts above.

The [operator checklist](operator-review-checklist.md) guides two actual people
through browser transcript, timing and blinded flaw reviews, explicit revisions
and versioning. The [five-minute demo](demo-script.md) distinguishes precomputed
genuine output, unresolved demonstration drafts and scientific abstention. No
review approvals, dataset release, video, upload or submission are manufactured.

| Deliverable | State / acceptance still required |
| --- | --- |
| Public code/docs | VERIFIED cd2abe9 baseline; later local release requires owner-authorized push and exact-commit CI |
| Interactive prototype | VERIFIED scoped software workflows; independent genuine caught-deviation and spoken accessibility acceptance INCOMPLETE |
| Public paired dataset/text/alignment labels | BLOCKED: permitted substantive public reference, same-text spectrum, independent human labels, rights and public download verification |
| <=6-page report | Prepared locally; BLOCKED on final owner content/publication approval |
| 3–10-minute YouTube demo | BLOCKED: permitted footage, actual recording, owner-approved upload and signed-out playback |
| Scientific metrics/calibration/held-out validation | BLOCKED: actual independent labels, calibration and sufficient disjoint families |
| Narrator/NVDA spoken acceptance | INCOMPLETE until a person actually hears and records behavior |
| Clean second-machine replay | INCOMPLETE; same-machine clean checkout is a separate software check |
| Devpost submission | BLOCKED on owner review, actual artifacts and manual submission/receipt |

Shortest owner sequence: collect a permitted substantive source and same-text
contrastive pilot; have two people complete the browser checklist and resolve
disagreements; validate/export without forcing unavailable metrics; approve exact
code/report/data/video contents; publish authorized artifacts and verify downloads;
record a permitted 3–10-minute demonstration; finish manual accessibility and submit
on October 14 before the October 15 00:15 IST deadline. A one-family pilot must
remain explicitly pilot-only; missing criteria must remain visible in the entry.
