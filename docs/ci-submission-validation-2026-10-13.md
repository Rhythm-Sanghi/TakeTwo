# CI repair and submission verification - 2026-10-13

TakeTwo - Speech analysis workspace. Started clean on master at published
35a1486a1a4cf93bf30e17cb4224adf6df4f2cb4. The three prior audited commits
30b671e, 1c5c183 and 35a1486 are public. New changes require fresh push
authorization; no dataset/video publication or submission is authorized.

## 1. GitHub Actions failure and correction

[Actual failed run](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38350507487),
job 115141577792, Windows Server 2025: 293 passed, three failed, one warning,
192.28 s. Packaging/frontend/security/browser steps were skipped after pytest.
The source checked out was exactly 35a1486. Python tests ran before npm install/build.

A new local Windows checkout of master, fresh uv environment and no frontend/dist
reproduced all three named failures: three failed in 73.71 s. The busy-port test
hits the launcher's earlier missing-build guard; both spawned recovery services
exit at the same guard rather than listening. Original harness suppressed their
startup output and waited 30 s, obscuring the shared prerequisite failure.

The workflow now performs locked Python sync/lock validation and npm ci/build
before pytest. All original checks remain. Application/launcher validation is
unchanged; the missing-build test still explicitly selects a nonexistent path.
No production or recovery deadline was increased.

Recovery tests continuously drain combined startup output into an eight-chunk
bounded buffer, report sanitized command/exit/liveness/health/timeout details,
fail early on exit and clean the owned startup tree on failure. Normal hard-crash
tests still kill only the service PID to exercise application/kernel containment.
Two new diagnostic tests and an equal-quality matching-tie test passed locally.
The first diagnostic test exposed a sanitizer treating the end of http: as a drive
prefix; word-boundary handling corrected it and the focused rerun passed three tests.

First corrected clean-checkout Python run: 299 passed, zero failed/skipped, one
existing warning, 194.67 s. New inventory is the original 296 plus three tests.
A final Ruff check then found one overlong diagnostic line; it was split without
behavior changes and the three focused cases passed again (2.50 s).

The first fresh frontend check revealed 24 Prettier failures: Windows Git checkout
converted LF blobs to CRLF. TypeScript/ESLint passed; frontend tests were not run
past that failed formatting gate. Added .gitattributes for LF text checkouts and
explicit binary PDFs. A second fresh clone verifies this actual checkout policy;
no production code is reformatted or changed to conceal the failure.
Second fresh checkout: all 299 tests passed again (162.25 s), TypeScript/ESLint/
Prettier passed, and Vitest passed all 20 tests (18.12 s). After the browser-port
change, static checks and all 20 frontend tests passed again (2.47 s).

Fresh browser installation in an isolated PLAYWRIGHT_BROWSERS_PATH fixed the
installation-specific Chromium launch problem: Chromium 156.0.8078.4 passes actual
native 200% tab zoom. All three generated browser workflows passed in 46.2 s on
port 8877 with zero skips, covering import/CPU processing/playback/export, five-area
zoom/accessibility, and review handoff/submission/export/adjudication. The original
private service remains running on 8765; no stop/migration is needed.

Packaging inspection exposed an additional reproducibility/release defect after
frontend installation: the sdist contained 8,480 members/37,976,680 bytes, including
8,323 node_modules files and compiled frontend output. An explicit Hatch source
manifest now retains code/docs/tests/schemas/locks/licenses/reproducibility inputs
while excluding caches/build products. The first rebuilt source archive had 153 members and 576,416 bytes; later documentation-only rebuild sizes can differ. Package preflight is now required in CI; two wheel/sdist negative
controls reject dependency-cache binaries and accept legitimate source/license.
No runtime dependency or lock resolution changed. Final full-suite result: 301 passed, zero failures/skips, one existing warning, 211.99 s. All original 296 remain; five new cases cover startup diagnostics, exact ties and both package formats.
Remote CI remains the failed published-baseline run until a new authorized push.

## 2. Scientific verification

No acoustic algorithm, delivery-v0, eligibility, rights, consent, independence,
family isolation, public schema or production resource limit changes.
Matching-v2, semantic-v2 and journaled review publication remain the prior fixes.
The retained genuine reference/natural report successfully replayed against current
root source, with identical provenance/correspondence and null overall score.
Known 80/120/200/400 Hz controls were rerun: 294 pitch frames each, raw F0 error
below 0.7%, finite probabilities, accepted 0/0/100/100%, no clipping. Production
mask/threshold is unchanged. UI presents explicit text/rights/timing blockers and
actual pitch-valid fractions; it does not infer frame validity from a score.

LF checkouts can change byte-based implementation hashes relative to an older
mixed-line-ending environment. This intentionally invalidates those source-bound
caches on a fresh checkout. Preserve historical artifacts and recompute against
that source; never patch their hashes or approval metadata. No algorithm changed.
The added exact-tie case checks 540 equal-quality assignments across repeated
runs/input permutations, retaining the pinned SciPy result and existing exhaustive
maximum-cardinality/quality regressions.

Exact uncertainty equality remains conservative: null is unknown, zero is an
explicit claim, and no independent annotations calibrate a tolerance for unequal
estimates. Differing values require reviewer revision/adjudication; allowing a
range would need justified separately versioned semantics and tests. Prose/UUIDs
remain preserved and no numerical agreement proves human independence.

Pitch diagnostics/masks retain confidence >=0.8 and finite voiced F0. Known-signal
and real diagnostic evidence is in [pitch investigation](pitch-investigation.md).
Accepted coverage remains below 1% on the five private takes; no score is unlocked.
Human boundary accuracy, TP/FP/FN, precision/recall/F1, severity association and
held-out performance are unavailable. Zero reviewed recordings/families does not
mean zero detection errors. Software fixtures are not human ground truth.

## 3. Private inventory and preservation

Five genuine same-person practice WAVs: reference 30.224375 s, natural 30.590 s,
slow 40.590 s, uneven 29.370 s, near-perfect 31.760 s. One controlled speech family,
unverified intended 71-word technology transcript, no public-release consent or
independent approvals. The original application workspace has five recordings,
zero submitted reviews; the separately retained review workspace has five drafts
and zero submissions. Eleven private file hashes were recorded for preservation.

Two acquired JFK masters share one speaker group; the imported 17.3 s salutation
is unverified. [Acquisition evidence](pilot-collection.md) remains historical.
The JFK Library American University item was rechecked and states Public Domain;
the inaugural item fetch returned 403, so no new rights verification is claimed for
that request. No new audio was acquired/uploaded. Models retain their own CC BY 4.0
terms; MIT applies only to original code/project documentation.

## 4. Submission materials and shortest viable dataset

The smallest practical competition pilot is one rights-cleared substantive public
speech excerpt, independently checked text, and four separately recorded same-text
mirrors spanning near-perfect/mild/moderate/severe intended changes. Two people must
review exact text, all timing/phrases and blinded full-coverage flaws; intended
severity is not ground truth. These recordings do not currently exist. Existing
private technology takes cannot silently stand in for the public-speaker baseline.
If genuine mirrors cannot be collected, the official statement permits explicitly declared synthesized/modified spectra from a permitted public source. Retain synthetic origin, exact text/time maps and independent listened annotations; disclose that this is a synthetic pilot, not observed human performance. No such review/publication gate is waived. A one-family pilot cannot
support TakeTwo's full leakage-resistant held-out acceptance; disclose pilot-only
or null results rather than forcing groups into train/test.

[Current report source](technical-report.md) replaces the submission-facing draft.
[Archived source](technical-report-2026-10-12.md) and the existing historical PDF are
preserved. A new current PDF was rendered and visually inspected on all six pages, with readable text and no clipping/overlap. It is ignored by Git and not approved for publication. [Current submission checklist](submission-draft.md) (which supersedes the historical filming plan) provides an exact
five-minute filming sequence with disclosed precomputed genuine outputs and honest
abstention if reviews remain missing. No video is recorded/uploaded by this work.

## 5. Official deliverables and gates

| Deliverable | Current acceptance |
| --- | --- |
| Public GitHub code/documentation | Published baseline exists; latest required CI red, local repair verification pending |
| Public contrastive dataset/transcripts/alignment labels | Blocked by human rights/collection/independent annotation and release actions |
| Functional interactive prototype | Implemented; local software/genuine unreviewed processing verified historically; eligible genuine flaw demonstration incomplete |
| Technical document, <=6 pages | Six-page current PDF generated and visually inspected locally; incomplete until owner approves content/publication |
| YouTube video, 3-10 minutes | Blocked by human recording, public permissions, upload and review; script prepared |

## 6. Deadline and owner actions

The [organizer announcement](https://multimodal-ai-hackathon-2026-7.devpost.com/updates/46710-problem-statements-are-live-multimodal-ai-hackathon-2026)
was checked on 2026-10-13: submissions close October 15, 2026 at 00:15 IST
(18:45 UTC October 14). Plan to finish on October 14, not the evening of October 15.
Owner must collect legitimate evidence, authorize a reviewed code push for remote CI,
verify public dataset downloads, review the six-page report, hear screen-reader
announcements, record/upload the permitted video and submit manually. No missing
human/scientific deliverable is closed by a green software test.

## Final local verification

- Documented PowerShell start-local.ps1 -Setup on an isolated fresh workspace/port
  reached health in 27.890 s. Normal startup reached health in 3.000 s without npm
  reinstallation. Both loaded zero recordings in the assigned test workspace;
  the original service at 8765 stayed healthy with its five recordings.
- uv locked installs/lock validation, npm ci/production build, Ruff lint/format,
  strict TypeScript, ESLint, Prettier, 20 Vitest tests and all three Playwright
  workflows passed. Browser checks used a fresh download and port 8877, not a
  private workspace. Generated review assertions remain software fixtures.
- Python dependency audit reports no known vulnerabilities; npm audit reports zero.
  Bandit reports no medium/high findings. Source/history preflight and built-package
  inspection found no blocking candidates; they do not prove absence of every
  secret or resolve third-party rights. Existing unreachable local private WAV
  objects remain outside publication refs; do not share the whole checkout.
- Current report has six rendered pages, all visually inspected. The historical
  report overwrite guard was exercised and preserved its bytes. Archived report
  source matches the published baseline; the official PDF and prior audit/review
  reports remain unchanged. Current PDF is Git-ignored and requires owner approval.
- Eleven saved private audio/manifest/database hashes remain unchanged, with no
  original review/draft mutation or new scientific approval. Current source schemas,
  acoustic implementation, comparison policy and service safety limits are unchanged.
- Only the original published baseline has run on GitHub; no new push is performed
  by this local repair. Actual hosted verification remains a required owner-authorized
  next step, not a locally inferred green result.

## Changed files

- .gitattributes
- .github/workflows/ci.yml
- .gitignore
- README.md
- docs/ACTION-REQUIRED.md
- docs/browser-testing.md
- docs/ci-submission-validation.md
- docs/demo-script.md
- docs/reproducibility.md
- docs/requirements-matrix.md
- docs/scoring-policy.md
- docs/submission-compliance.md
- docs/submission-draft.md
- docs/technical-report-2026-10-12.md
- docs/technical-report.md
- docs/windows-setup.md
- frontend/playwright.config.ts
- frontend/tests/zoom.spec.ts
- pyproject.toml
- scripts/audit_release.py
- scripts/build_submission_report.py
- tests/test_comparison.py
- tests/test_release_audit.py
- tests/test_web_recovery.py
