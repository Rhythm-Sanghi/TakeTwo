# TakeTwo product completion report

Speech analysis workspace. Local evidence, 14 October 2026. Engineering completion
and independent scientific acceptance are separate.

## A. Initial audit

The saved Stage A audit began at clean `01203ff`. This continuation inspected
`e2960fd` on master with uncommitted exploratory work and preserved it. Earlier
audit/readiness commits are `5c69360` and `e2960fd`.

Controlled failures reproduced all-or-nothing refresh, incomplete readiness without
diagnosis/retry, and review-evidence errors hiding successful inventory. Healthy
genuine-copy counts are five recordings, four participants, one controlled reference,
one declared speaker ID, one connected family, zero verified transcripts and zero
submitted independent reviews. Missing human review is not a code defect.
Other findings include missing useful results, buried alignment, repeated serialization,
low pitch coverage and intermittent Windows diagnostics. Initial reproduction and provenance decisions are consolidated below.

## B. Exploratory analysis

Exploratory-v1 summarizes existing feature artifacts: duration/source and canonical
rates, RMS/peak/clipping, baseline/energy percentiles/active range, disjoint activity/
quiet support, unobserved tail, accepted pitch/voicing diagnostics, quality flags
and native provisional words. It does not duplicate large feature arrays.

RMS = sqrt(mean(x²)); peak = max(abs(x)); clipping fraction counts abs(x) ≥0.999.
Frame energy = 20 log10(max(unweighted frame RMS, 10⁻⁶)) dBFS. Percentiles use
linear interpolation. Duration delta is participant minus reference; percentage
is 100 × delta/reference duration. RMS difference is 20 log10(participant/reference
RMS), withheld if either RMS is below 0.001.

Contiguous low-energy hop support ≥0.15 s becomes a candidate with its exact
two-pass acoustic-v1 threshold and absolute-floor configuration. Adjacent complete
0.5 s windows differing by ≥6 dB in median energy become energy-change candidates.
Boundaries have 10 ms hop resolution/25 ms window smearing. Overlapping windows
are not independent flaws. Each carries native identity, timing, energy, hashes,
thresholds and limitations; breath, noise, intentional pause and dropout remain
indistinguishable. [Methods and versioned schema](exploratory-analysis.md).

Genuine example: 30.224375 versus 29.370 s, −0.854375 s, −2.826775%; RMS
0.04110913/0.04131717, +0.04384731 dB. The 53 acoustic windows and 71 automatic
correspondences are unverified, not delivery mistakes or verified words. Invalid/
mismatched features fail closed. Missing, partial or OOV alignment withholds rate;
near-silent inputs withhold RMS differences. Whole-recording duration is not speech rate.

## C. Scientific integrity

Acoustic-v1 and delivery-v0 algorithms, historical artifacts, independent review,
exact-inventory selection, deterministic matching and rubric policies remain intact.
Exploration writes no human approval, annotation, flaw region or evaluation metric.
Automatic rate uses supplied aligned words divided by first-to-last word span,
including internal gaps; it is separate from authoritative verified speaking rate.

The [pitch study](pitch-investigation.md) repeated five real takes, sine/gain controls
and window/range probes. Accepted coverage remains 0.284–0.617%; a longer window
raises the real reference only to 1.362126%. No independent F0 reference exists here;
no replacement, confidence relaxation or score unlock is justified.

Verified scoring still needs rights, reviewed text/timing/correspondence and quality.
Phrases need ≥3 words/0.5 s, ≥80% frame support, and pitch ≥50% accepted frames.
Scores need ≥80% observation coverage and two phrases or five pause boundaries.
Overall score needs all four dimensions. Software fixtures exercise eligible/partial/
zero states. Genuine evidence cannot satisfy pitch/independent-review gates; real
precision/recall/F1 remain unavailable.

## D. UI, audio and reporting

Analysis order is identity → exploratory summary/observations → native listening →
Verified Assessment → technical evidence. Reference-only inspection, history,
latest-analysis entry, partial/error/retry, stale responses and source-hash checks
are integrated. Candidate actions select/seek/replay their own recording; automatic
words seek actual intervals. First-eight display does not truncate exports.

Readiness distinguishes loading, authoritative zero/counts, partial/unknown, transport/
server errors and handoff restrictions. Dataset and Evaluation can return to available
exploration without certifying it. Reviewer playback now retains an explicit zero
seek and waits for final acknowledgment before saving; backend gates remain unchanged.

Before images remain private under local-data/completion-before-*. Genuine after
images use completion-exploratory-genuine-{width}[-viewport].png. Widths 320, 390,
800, 1366 and 1920 passed axe and overflow checks. The public [software screenshot](images/taketwo-exploratory-software.png)
contains generated signals, not human speech or independent scientific evidence.

JSON has a version/checksum envelope. CSV contains every candidate and method,
threshold, resolution, feature hash and limitation. Dedicated native print provides
selectable measurements, energy plots, full interval tables, provisional words,
provenance and actual missing assessment requirements. The genuine example has four
inspected pages. A dated local/ignored technical draft has six inspected pages;
historical PDFs were not overwritten.

## E. Performance and reliability

Profiled pair restoration spent 6.27 of 9.16 s in canonical JSON serialization under
mixed local load. Validated artifacts now retain digests too. A per-app 16-entry
compact summary cache is promoted only after publication/size/integrity checks.
Every request still validates current source audio/environment, dataset and stages.

| Genuine request | Repeat before (s) | Repeat after (s) |
| --- | ---: | ---: |
| Reference inspection | 3.013 | 0.131 |
| Reference/uneven | 6.536 | 0.218 |
| Reference/slow | 8.667 | 0.233 |

These are mixed-load local request measurements, not an isolated benchmark or faster
MFA claim. Historical cold jobs recorded 1.90–1.98 GB peak commit and 94–109 s;
a prior cached pair recorded 315 MB/19.766 s. No fresh RSS/accuracy benchmark is
claimed. CPU-only processing, 4 GiB worker-tree limit, 600 s timeout, supervision,
cancellation and immutable storage remain intact.

WinError 10054 may still log on abrupt cancellation; no universal reliability fix
is claimed. Legacy leases correctly fail closed. Fifteen preservation hashes match.
The five WAVs were found directly in Documents, unchanged; movement cause is unknown.

## F. Verification

Full Python suite: 340 passed, zero failed/skipped, one existing Starlette/httpx
deprecation warning. After cache-publication ordering refinement, 49 affected
exploratory/web/regression tests passed again. Frontend: 55 passed, zero failed/skipped,
including source-identity and two playback synchronization regressions.

Final full browser run: 10 passed, zero failed/skipped (5.2 minutes). It covered actual
import/CPU processing, all five workspaces/widths, native 200% zoom, 15/29/30/40/45 s
inputs, readiness failures/recovery, eligible software-only display states, reference/
history identity, exploratory replay/export/print/stale recovery, independent audio
switching and reviewer isolation/playback/submission/adjudication. Automated axe
reported zero violations in the tested states. Evidence is retained privately under
local-data/completion-accepted-browser-results. Earlier failures remain
retained: serialization contention, a status selector needing scope, and lost playback
beginning/terminal acknowledgment. An already-reviewed fixture correctly blocked
duplicate review without revision. No assertion was removed or gate relaxed.

TypeScript, ESLint, Prettier, Ruff lint/format, production build, wheel/sdist, lock
check, five runtime schemas/local links and unchanged Track C hash passed. npm and
pip-audit found no known vulnerabilities. Release preflight found no blocking private/
history/package findings. These checks do not establish universal security, spoken
screen-reader acceptance or production readiness.

## G. Documentation and reproduction

Updated README, [user guide](user-guide.md), exploratory methods/schema, [backend API](backend-api.md),
pitch study, editable technical report and audit. MIT copyright (c) 2026 Rhythm Sanghi,
separate private/external rights and honest Codex/ChatGPT disclosure are retained.

Use README verification commands. Browser isolation can use TAKETWO_BROWSER_PORT=8880;
native zoom requires the documented compatible TAKETWO_ZOOM_EXECUTABLE. Generated
fixtures come from make_browser_fixtures.py. Genuine inspect_pitch.py --probes needs
authorized local copies and writes private diagnostics. Restart the normal app to
load the new backend/build. Reviewed dataset rebuilding remains an explicit documented
operator/versioning step; it cannot be replaced by automatic candidate approval.

## H. Git

Local master: audit/readiness `5c69360`, `e2960fd`; exploratory backend `3019ded`;
exact thresholds/validated cache `2aec5e8`; results/native replay/review synchronization
`6eeee52`. The final documentation commit is recorded in the local log and completion
message. Final tracked working-tree status is clean; ignored private evidence remains local.

Changed areas: exploratory package/web API/Python regressions, generated contracts,
frontend API/context/App/exploratory component/print CSS, reviewer synchronization,
frontend/browser tests, README/guides/audits and software-only screenshot. Root
AGENTS.md remains the permanent authority. No push, release, private publication or
external submission occurred.

## I. Remaining acceptance actions

Obtain actual independent transcript, timing and blinded flaw reviews; reconcile
through revisions/adjudication and rebuild a reviewed dataset version. Resolve
per-item rights/consent for publication. Collect independent speaker/family groups,
freeze calibration/held-out evaluation, and acquire permissible independently checked
F0 references before judging a new extractor. Have a person perform Narrator/NVDA
review and record spoken behavior. Obtain owner approval for the public contrastive
dataset, technical draft, video and submission. Software fixtures and exploratory
measurements substitute for none of these. Cold processing and intermittent Windows
reset/permission diagnostics remain documented operational limitations.

## Consolidated initial reproduction and provenance decisions

At clean 01203ff, the initial baseline passed 322 Python, 43 frontend and 8 browser
tests, plus lint/build/lock/package/schema/dependency checks. Fifteen protected
hashes were captured. A reviews 503 concealed five successful recording responses;
inventory_counts={} and review_readiness=[] reproduced indefinite unavailable
counts. These controlled failures established independent-refresh/partial-evidence
defects, not the cause of an unseen historical server response. Initial evidence
remains private in local-data/completion-baseline-* and
local-data/completion-readiness-reproduction.json.

After the readiness repair, 50 frontend tests, three new partial-failure/zero backend
cases, 43 existing web/review tests and the new browser recovery case passed.
Later final counts remain distinct above. Exploration recovered the actual final
two-pass activity-mask threshold: the descriptive energy median can differ from
the median used in the last mask update. Stored masks and thresholds are checked;
incorrect masks/stale identities fail closed without changing acoustic-v1.
A software review began at 0.005914 s when a play callback overwrote explicit zero
seek; seek-before-play and terminal-acknowledgment repair preserved listening gates.
An already-reviewed fixture correctly required revision. Scientific gates, independent
reviews, immutable artifacts and source/environment identities were retained.
