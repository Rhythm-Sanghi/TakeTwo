# Final repair audit

TakeTwo — Speech analysis workspace. Started 2026-10-13 at local and remote
`51d122c0585a29b4ec471e298b4c1f1d128ba60e` (`master`), clean working tree.
This ledger separates executed software evidence from human scientific acceptance.
The official Track C PDF remains unchanged.

## Initial findings and acceptance plan

| Priority | Finding / root cause | Required evidence |
| --- | --- | --- |
| P0 | Flaw consensus compares serialized IDs, rationale and listening segmentation | Independent IDs, tolerated bounds and equivalent coverage agree; real category/severity/coverage/identity disagreements abstain |
| P1 | Greedy overlap assignment can sacrifice a valid second match | Adversarial two-by-two graph, cardinality then quality, deterministic permutations and event/interval isolation |
| P1 | File publication precedes SQLite commit without persistent intent | Actual subprocess interruption before/after publication, restart reconciliation, corruption rejection and idempotent retry |
| P1 | Genuine browser fixtures reference private host-specific paths | External fixture preparation/configuration, early missing-input errors, generated fixture CI |
| P1 | Release preflight does not fail for missing license | Owner-selected MIT, separate third-party/data scope, negative preflight tests and history audit |
| Investigation | Low accepted pYIN coverage may reflect signal/range/confidence | Raw/accepted coverage, confidence quantiles, quality and known-F0 controls; retain threshold 0.8 and abstention |
| Investigation | Reviewed dataset revision and evidence consumption | Explicit isolated fixture lifecycle plus genuine draft checks; no fabricated real approvals |
| External gate | Native zoom / spoken screen reader | Native Chromium alternative attempt; manual heard announcements if unavailable |

Available genuine data: five private same-person practice WAVs and intended
transcript, with no independent human reviews or public-release permission.
Originals, private workspaces, drafts and historical evidence are preserved.
Safety limits: 45 s analysis, 600 s import, 100 MiB upload, one CPU worker,
4 GiB worker commit and 600 s deadline. Native MFA configuration exists locally;
it is not a public fixture. No cloud service or new solver dependency is planned.

The publication audit found private WAV objects in unreachable local Git trees,
outside published branch history. Do not share this checkout or rewrite history
automatically. Public source/dataset/PDF rights remain separate decisions.

## Execution evidence

Baseline: 264 Python tests passed (275.88 s), 20 frontend tests passed,
TypeScript and ESLint passed. Two deliberately focused reproductions then failed:
serialized flaw UUIDs prevented agreement, and greedy matching returned TP=1,
FP=1, FN=1, F1=0.5 for a graph admitting two valid matches.

The repaired graph returns TP=2, FP=0, FN=0, F1=1.0. This is a numerical
software regression, not measured speech-detection accuracy. Thirty seeded small
graphs are checked against exhaustive cardinality/quality optima. Semantic review
cases cover UUIDs, timing tolerances, severity/category/uncertainty, coverage unions,
missing labels, multiple reviewers, transitive disagreement, supersession and
identity conflicts. Public result schemas remain unchanged; implementation hashes
and explicit matching-v2/semantic-v2 limitations distinguish new evaluations.
Historical evidence is immutable and requires explicit recomputation for current
metrics. The stable lowest-review-ID inventory represents agreed labels; all review
hashes remain in evaluation provenance.

A durable publication intent and exclusive atomic artifact publication recover
actual killed subprocesses before and after publication. Restart returns exactly
one original review; retry is idempotent. Corrupt journals/artifacts, contradictory
payloads and legacy orphans fail closed with backup/reconciliation guidance.
Private lifecycle schema 2 migrates additively; public Review v1 is unchanged.
This establishes process-crash recovery, not power-loss/storage durability.

The complete reviewed-version lifecycle passed on isolated generated signals:
automatic alignment, two transcript assertions, explicit new-version imports,
regenerated alignment, timing/phrase assertions, blinded flaw assertions, comparison
and evaluation. Those assertions are labeled software fixtures. Genuine human
approvals were neither supplied nor manufactured. Reviewer endpoint tests reject
missing/wrong capabilities; operator routes, cross-origin saves, rotation, handoff
isolation, immutability and artifact/provenance failures are checked. Supervised
local capabilities still do not authenticate people, expire by time, prove listening
or prevent the OS account owner reading evidence.

[Pitch measurements](pitch-investigation.md) show raw voiced coverage of
69.3–76.4% but accepted coverage of only 0.284–0.617% on the five genuine takes.
Known 80/120 Hz controls also fail the unchanged confidence gate despite correct raw
F0. Diagnostic window probes improve controls but not reference usability; gain and
range changes do not resolve this case. No extraction implementation defect was
established. Acoustic-v1, delivery-v0, threshold 0.8 and pitch abstention remain
unchanged. These are confidence/configuration limitations, not calibrated accuracy.

### Final executed software checks

| Check | Executed result |
| --- | --- |
| Full backend | 296 passed, zero failed/skipped, 481.46 s; one existing Starlette/httpx deprecation warning |
| Frontend | 20 passed in two files, zero failed/skipped, 41.40 s on the final isolated run |
| Ruff | Lint passed; 63 files formatted |
| TypeScript / ESLint / Prettier | Passed; final changed browser files formatted and rechecked |
| Production frontend / Python builds | Passed; wheel and sdist inspected for MIT holder and absence of private data |
| Dependency lock / security | uv lock check, locked sync and npm ci executed; pip-audit no known vulnerabilities, npm audit zero |
| Bandit | No medium/high findings, no scan errors; low-severity subprocess/temporary-file findings reviewed |
| Repository contracts | 44 Markdown files, 272 local links, all four runtime schema snapshots, product identity, judging weights and unchanged official PDF passed |
| Release negative controls | Seven tests passed, including deleted-history secret and missing LICENSE |
| Release inventory before commits | 149 candidates, 302 reachable history blobs, no blocking candidates or personal absolute paths |
| Git whitespace | git diff --check passed |

The wheel contains 43 files and the source archive 150; neither includes private
recordings, databases or model weights. MIT is present in packaged metadata.
Security updates are limited to python-multipart 0.0.31 and pytest 9.0.3; no acoustic
dependency or algorithm was changed. Pattern scans do not prove absence of every
secret or confer redistribution rights. The two existing PDFs require their
respective content/rights review. The official specification and historical report
PDF bytes are preserved.

Earlier attempts remain relevant: one loaded 295-test run had 293 passes and two
failures (a generic supervision/storage error and a child not reaching its 20 s
crash barrier). Both isolated reruns passed; the test-only barrier is now 60 s and
supervision retains local exception details while redacting HTTP diagnostics. The
final complete suite passed. The storage error's underlying cause was not captured,
so it is not claimed causally repaired. A concurrent frontend attempt ran no tests
because both workers timed out at startup; the isolated final run passed. One
Prettier invocation used the wrong working-directory glob; corrected paths exposed
and fixed formatting in three test/config files. A clean second machine remains a
separate reproducibility gate.

### Browser and genuine-data evidence

The native 200% zoom check passed on isolated Chromium 153.0.8010.12: tab zoom 2.0,
DPR 1 to 2, layout viewport 1600 to 800. All five workspace areas passed heading
focus, geometry/overflow and axe checks; actual viewport screenshots were visually
inspected. Newer installed Chromium 156.0.8078.4 fails Windows SideBySide activation;
the alternate executable is explicit test configuration, not CSS zoom. Repair the
newer host browser environment separately. Narrator is installed, but no actual
spoken announcements were heard/verified. The manual checklist remains open.

The five-take genuine browser review run passed in 4.3 minutes on new private
copies: native playback, saved/reopened unresolved drafts, boundary edit/restore,
annotation editing and 1600/800/320 px checks. It produced five drafts and **zero
scientific reviews**. The reference native job used 195.828 s wall time and
1,897,512,960 bytes peak aggregate worker commit, including alignment 160.219 s and
feature extraction 30.984 s, under concurrent verification load; 71 MFA words.
This is an observed run, not an isolated speed guarantee or alignment-accuracy
measurement. Original recordings, manifests and lifecycle databases matched all 11
saved hashes before restoring the idle service.

An initial fresh 45 s browser attempt stopped waiting at its 300 s test budget while
the job was still running under concurrent load; teardown cancelled it. No production
deadline failure was established. Genuine-suite polling now allows the unchanged
600 s job deadline to finish; test timeout is 900 s. Production limits remain
45 s / 600 s import / 100 MiB / one worker / 4 GiB / 600 s.

The final fresh 45 s browser run passed (one test, 5.8 min), with **314.813 s**
job wall time and **2,122,432,512 bytes** peak aggregate worker commit, no cache hits.
Native reference alignment took 135.062 s, synthetic participant alignment 115.484 s,
reference extraction 32.579 s, participant extraction 25.625 s, comparison 2.641 s,
and validation 0.344 s. Both inputs retain 60 aligned words, 265 phones and 4,498
spectral frames. Native playback/seek, navigation/focus during processing, report
export, null overall score and axe checks passed. This fits the unchanged 600 s /
4 GiB safety limits on this host; it is one observed workload, not a universal SLA.
One Windows asyncio connection-reset callback was logged during browser traffic;
the final assertions passed. The source is genuine archival speech; the paired
control remains explicitly synthetic, with no independent human ground truth.

The fresh genuine reference/natural pair also passed native processing on private
input copies: 30.224375 s / 30.590 s, all 71 canonical tokens in order per input,
274 phones each, bounded native timestamps and raw acoustic summaries. No cache
hits. Job wall time was **287.469 s** and peak aggregate worker commit
**2,075,697,152 bytes**. Stage times: reference alignment 117.860 s, participant
alignment 110.797 s, reference extraction 21.078 s, participant extraction 29.297 s,
comparison 3.484 s, validation 1.297 s. No human review was created; scientific
eligibility and overall score remain unavailable. Token/timestamp consistency is
not a human judgment of boundary accuracy.

Measured host: Windows 11 Pro Insider Preview 10.0.26220, Intel Core i7-1365U
(10 cores / 12 logical processors), 16,421,584 KiB visible RAM. Execution is CPU;
peak measurements are aggregate worker **commit**, not resident-set size. Wall
time includes subprocess startup and supervision. Measurements do not establish
performance on every target Windows machine.

The final combined portable browser run passed all three tests (2.2 min): generated
imports/processing/cancellation/native playback/report export, actual native 200%
zoom across all five populated workspace areas, and generated review handoff,
playback, immutable submission/export and adjudication. Zero failures/skips.
The diagnostic CLI also completed --probes on generated canonical fixtures; this
checks its optional execution path and does not add genuine scientific evidence.

The original idle workspace is restored only after a private database backup and
logical job/session snapshot. Startup is healthy, native alignment configured, five
recordings present and zero reviews. Both original database byte hashes changed
through initialization/additive lifecycle migration, while every saved job/session
row is identical. The other nine saved file hashes remain exact, including all
five original WAVs, both manifests and the separate five-draft workspace databases.
The lifecycle schema is now 2. No analysis or approval ran in the original workspace.

After adding explicit selected-heading scroll for clearer viewport captures, the
native zoom test passed again (20.3 s, 28.0 s total). Captures are scrolled viewport
samples, not proof every control is simultaneously visible or a substitute for
manual accessibility acceptance. Fixture preparation was tightened to copy only
manifest-listed audio; 21 prepared input hashes match the previously tested kit,
and an incidental test database in a source audio directory was correctly excluded.

Windows GitHub Actions CI is configured for locked installs, Python/frontend
checks, packaging, schemas, security and generated browser workflows. It requires
no private audio or MFA models. **No GitHub Actions run occurred:** no push was
performed. Portable fixture setup and opt-in genuine tests are described in
[browser testing](browser-testing.md). Missing private inputs fail before startup.

No application frontend refactor was justified by a reproduced product defect.
Existing cohesive UI sections and Workshop + Gridline + Studio Utility styling
are preserved. Browser test races/heading assertions were corrected in tests;
no decorative UI or fake authentication was introduced.

### Changed files

- Scientific/review implementation: src/taketwo/comparison/{matching,evaluation,reviews,storage}.py;
  src/taketwo/web/{review_workspace,jobs}.py; tests/test_comparison.py;
  tests/test_review_workspace.py.
- Release/licensing: LICENSE; pyproject.toml; uv.lock; frontend/package.json;
  frontend/package-lock.json; scripts/audit_release.py; tests/test_release_audit.py;
  .github/workflows/ci.yml.
- Diagnostics/portable tests: scripts/inspect_pitch.py; scripts/prepare_genuine_fixtures.py;
  frontend/playwright.config.ts; frontend/tests/{duration,pilot,review-pilot,workspace,zoom}.spec.ts.
- Documentation: README.md; docs/{ACTION-REQUIRED,attributions,browser-testing,
  comparison-engine,demo-script,dependencies,final-repair-audit,pitch-investigation,
  requirements-matrix,review-workspace,submission-compliance,submission-draft,
  technical-report}.md.

AGENTS.md, official Track C.pdf, historical report PDF, acoustic implementation,
delivery-v0 and public schemas are unchanged. Local commits contain only the listed
source/documentation materials. No branch, remote write, history rewrite, dataset
publication or submission is performed.

## Owner decisions and scientific gates

Owner selected MIT with `Copyright (c) 2026 Rhythm Sanghi`. This licenses original
project code; private recordings, datasets and externally licensed resources are
excluded. Independent people must still verify transcripts, boundaries and blinded
flaws; rights, calibration, held-out evaluation, video and submission remain open.
No push, dataset publication or submission is authorized by this repair.
