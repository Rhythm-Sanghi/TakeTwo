# Reproducing software and scientific evidence

TakeTwo — Speech analysis workspace. Run PowerShell from the repository root. Install the locked Python 3.11 and Node 24 environments with [Windows setup](windows-setup.md), and native CPU MFA 3.3.9 plus checksummed English US ARPA v3.0.0 resources with [alignment setup](analysis-engine.md). No dependency upgrade is required. Keep heavy jobs serial. Commands below use real collected files; they do not generate approvals.

## Software checks

```powershell
uv sync --locked
uv lock --check
npm --prefix frontend ci
npm --prefix frontend run build
uv run pytest -q
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv build --no-sources
uv run python scripts/export_api.py
npm --prefix frontend run contracts
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run test
npm --prefix frontend run build
uv run python scripts/make_browser_fixtures.py
npm --prefix frontend exec -- playwright install chromium
npm --prefix frontend run e2e
uv run python scripts/check_repository.py
uv run python scripts/audit_release.py --packages
git diff --check
```

Generated oscillator/browser fixtures establish software behavior only. Stop the known local service before E2E, which owns port 8765 and creates a fresh ignored workspace. If documented genuine source/config files exist locally, run `uv run python scripts/measure_browser_smoke.py --output .\local-data\acquisition\browser-smoke.json` once with a fresh filename; otherwise reacquire/review sources before that optional check. Models/audio are deliberately not shipped. The five Windows tests in `tests/test_web_recovery.py` exercise actual process termination, bounded allocations and restart behavior; full pytest includes them.

## Collected dataset to report

Prepare `dataset-annotations.json` as a nonempty array of actual dataset Annotation records from both reviewers, using the participant/pair IDs and text hash from the first inventory export. Follow [dataset fields](dataset-engineering.md): positive-width native intervals, reviewer, listening rationale, review status and uncertainty. Reviewed acceptable spans use severity 0; flaws use 1/2/3. Publication checks these manifest annotations separately from comparison Review artifacts. Missing-pause anchors belong only to comparison flaw reviews; never invent silence intervals for manifest labels. Complete annotations before comparison so report dataset hashes stay current. Pause the command sequence after export to fill these records from real listening.

Prepare the files specified by the [collection kit](review-protocol.md#recording-preparation-and-participant-permissions) and [annotation worksheet](review-protocol.md#independent-annotation-worksheet), per [ImportSpec](dataset-engineering.md), before running this sequence. This is a parameterized operator recipe, not a claim that these collected files exist. Substitute the actual family directory once. Check `$LASTEXITCODE` after every native command; stop on operational failure before consuming output.

```powershell
$collection = '.\local-data\collection\<actual-family>'
$workspace = '.\local-data\human-pilot-v1'
$config = '.\local-data\alignment-config.json'
uv run taketwo-dataset init $workspace --version human-pilot-v1
$ref = uv run taketwo-dataset import-reference $workspace --audio "$collection\reference.wav" --metadata "$collection\reference.json" | ConvertFrom-Json
$member = uv run taketwo-dataset import-flawed $workspace --reference $ref.recording_id --audio "$collection\speaker-<id>-mild.wav" --metadata "$collection\speaker-<id>-mild.json" --category pacing --severity 1 | ConvertFrom-Json
# Repeat for all genuine takes/families; category and intended severity reflect that take.
# Near-perfect/natural candidates use category acceptable and intended severity 0.
uv run taketwo-dataset validate $workspace --reproduce
uv run taketwo-dataset split $workspace --seed 17 --ratios 0.5 0.25 0.25
uv run taketwo-dataset export $workspace --output .\local-data\collection-ledger.json
# Fill actual independent dataset annotations using the returned pair/recording IDs.
uv run taketwo-dataset annotate $workspace --annotations "$collection\dataset-annotations.json"
$aRef = uv run taketwo-analysis align $workspace --recording $ref.recording_id --config $config | ConvertFrom-Json
$fRef = uv run taketwo-analysis extract $workspace --recording $ref.recording_id --alignment $aRef.artifact | ConvertFrom-Json
$aMember = uv run taketwo-analysis align $workspace --recording $member.recording_id --config $config | ConvertFrom-Json
$fMember = uv run taketwo-analysis extract $workspace --recording $member.recording_id --alignment $aMember.artifact | ConvertFrom-Json
uv run taketwo-analysis validate $workspace --artifact $fRef.artifact --alignment $aRef.artifact --reproduce
uv run taketwo-analysis validate $workspace --artifact $fMember.artifact --alignment $aMember.artifact --reproduce
```

Find the actual pair ID in `collection-ledger.json` under `dataset.pairs`; bind it to `$pairId`. Inspect alignments/features and fill the six actual review files. The [schema](comparison-schema-v1.json) and [worksheet](review-protocol.md#independent-annotation-worksheet) define every required field. Reviews use original **payload** digests and exact provenance, not file-byte hashes. Timing reviews require all canonical words plus complete phrase partitions. Flaw reviews require full listening coverage and two independently prepared, explicitly reconciled inventories; retain superseding history.

```powershell
$rtA = uv run taketwo-comparison import-review $workspace --review "$collection\reference-timing-A.json" --alignment $aRef.artifact | ConvertFrom-Json
$rtB = uv run taketwo-comparison import-review $workspace --review "$collection\reference-timing-B.json" --alignment $aRef.artifact | ConvertFrom-Json
$ptA = uv run taketwo-comparison import-review $workspace --review "$collection\participant-timing-A.json" --alignment $aMember.artifact | ConvertFrom-Json
$ptB = uv run taketwo-comparison import-review $workspace --review "$collection\participant-timing-B.json" --alignment $aMember.artifact | ConvertFrom-Json
$flA = uv run taketwo-comparison import-review $workspace --review "$collection\participant-flaws-A.json" --alignment $aMember.artifact | ConvertFrom-Json
$flB = uv run taketwo-comparison import-review $workspace --review "$collection\participant-flaws-B.json" --alignment $aMember.artifact | ConvertFrom-Json
$report = uv run taketwo-comparison compare $workspace --pair $pairId --reference-features $fRef.artifact --reference-alignment $aRef.artifact --participant-features $fMember.artifact --participant-alignment $aMember.artifact --review $rtA.artifact --review $rtB.artifact --review $ptA.artifact --review $ptB.artifact | ConvertFrom-Json
uv run taketwo-comparison validate $workspace --artifact $report.artifact --reproduce
uv run taketwo-comparison evaluate $workspace --report $report.artifact --review $flA.artifact --review $flB.artifact --config "$collection\evaluation-pilot.json"
uv run taketwo-dataset validate $workspace --publication --reproduce
```

`evaluation-pilot.json` content: `{"mode":"pilot","split":"test","iou_threshold":0.5,"boundary_tolerance_s":0.2,"bootstrap_resamples":1000,"seed":17}`. Only evaluate reports assigned to that frozen split. A one-family pilot may be assigned train, leaving no test reports: keep missing metrics, collect more groups, and never move files just to obtain a result. Repeat sensitivity evaluation at IoU 0.3/0.7 with separate config/output artifacts. Synthetic pairs are separate runs. Exit 3 means scientific abstention; dataset publication exit 1 means preflight failed; neither means a complete validated corpus.

Preserve `delivery-v0` and its policy hash. For a future held-out study create a new reviewed calibrated policy using training residual Q95 floors, fixed widths, validation-group evidence and `frozen=true`; compare with `--policy <actual-policy.json>`. Only then use evaluation mode `held_out` on disjoint test groups (at least three for full acceptance). No code change is needed to import valid data/reviews and run these existing commands. Missing evidence cannot be filled by changing thresholds or using `software_fixture` mode.

Save code/lock/model/config/data/review/report hashes, commands, exit codes, hardware, OS, seeds, exclusions and full FP/FN lists. Repeat on a clean second environment; investigate any decision difference. Same-Windows exact feature replay is established; cross-environment tolerance is proposed, not measured. Refer to [scoring evaluation](scoring-policy.md) for denominators and uncertainty.

## Technical-report source and regeneration

Evaluation uses [exact-inventory-v1](comparison-engine.md): supply all original
flaw reviews and same-author revisions, not only a preferred review. Reconstruct
canonical labels from exact numerical agreement; unresolved temporal differences
withhold metrics. Preserve historical first-review evaluations without relabeling
them as current-policy results. The [stabilization audit](verification.md)
records public baseline CI separately from subsequent local verification.

Use a separate ReportLab document-tool environment on Windows; do not add authoring packages to TakeTwo runtime dependencies. Run `python scripts/build_submission_report.py --date "15 OCT 2026"`. It renders unchanged `docs/technical-report.md` to the Git-ignored owner-review file `output/pdf/taketwo-technical-report-current.pdf` and enforces six pages. Render and inspect every page before publication. The current approved report is `output/pdf/taketwo-technical-report-2026-10-15.pdf`; do not overwrite it during verification. The legacy historical destination remains protected by the renderer; older PDF/source bytes and the original reference [5] are accessible through the pinned historical sources in [verification](verification.md). Regeneration need not reproduce PDF metadata bytes; compare all source paragraphs, page count and visible layout. A new report requires owner content/publication approval.

Source archives use an explicit Hatch manifest; after building, `scripts/audit_release.py --packages` also rejects unsafe wheel/sdist members. The wheel is API/CLI only; frontend source is preserved in the sdist for `npm ci`/build. LF checkouts are enforced by Git attributes. Old artifacts with differing byte-based source hashes require explicit recomputation; preserve originals rather than rewriting provenance.

## Browser verification and fixture configuration

The generated suite includes `zz-experience.spec.ts`, a route-only
software UI fixture for report loading, partial dimensions, eligible findings,
native interval replay and eligible-zero presentation. It intercepts report
responses in that test only, never edits a stored report or supplies genuine
review evidence. The other integration cases use actual processing/review APIs.
See [experience audit](verification.md) for executed checks and limits.

The generated suite includes `zy-presentation.spec.ts`: actual generated 15/29/30/40/45
second WAV imports and CPU extraction, complete native domains/end samples at all
five widths, same-speaker take counts, operator preselection without access grants,
axe on expanded dimension diagnostics and real Chromium printing with all accessible
chart disclosures open. These are software signals, not speech or human evidence.
The serial case can take several minutes; production limits are unchanged. Native
zoom also loads completed charts when present. Print verification additionally
requires rendering and visually inspecting every PDF page.

Standard software tests require no private data, MFA installation or external account:

The generated suite also covers five-area screenshots at 1920×1080, 1366×768,
800, 390 and 320 pixels, including populated long-filename selectors. Review
software assertions select the named two-second generated tone; genuine audio
must never receive those intentionally incorrect software transcripts. Optional
genuine processing observes the unchanged 600-second service deadline (630-second
poll budget), failing immediately for an actual failed job. This accommodates
native MFA/extraction rather than treating a shorter fixture wait as production failure.

```powershell
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
uv run python scripts/make_browser_fixtures.py
cd frontend
npx playwright install chromium
npm run e2e
```

The generated tones and explicitly labeled review assertions exercise software only. The server uses a fresh ignored workspace. Port 8765 is the default; set TAKETWO_BROWSER_PORT to an unused local port (for example 8877) to keep an existing private service running. The setting accepts integers 1-65535 and applies to API, browser and native-zoom checks. If using the default occupied port, stop only the known idle service before testing. A real failed test is a failure, even if another workflow passes. Native zoom is a separate actual extension/tab-zoom check; a recorded host launch failure leaves that check unverified.

### Private genuine fixtures

Genuine suites are opt-in and are not shipped or run in normal CI. Prepare copies of authorized inputs explicitly. `$privateKit` must be a fresh external directory or an ignored directory under `local-data`; never add it to Git. Supply actual paths for the selected options:

```powershell
uv run python scripts/prepare_genuine_fixtures.py --output $privateKit --pilot $fiveWavDirectory --review-workspace $existingFiveTakeWorkspace --duration-workspace $existing45SecondWorkspace
$env:TAKETWO_GENUINE_FIXTURES = $privateKit
$env:TAKETWO_TEST_ALIGNMENT_CONFIG = $actualAlignmentConfig
# Select one suite per invocation:
$env:TAKETWO_REVIEW_PILOT = '1'
npm --prefix frontend run e2e -- --output=../local-data/genuine-review-results
Remove-Item Env:TAKETWO_REVIEW_PILOT
$env:TAKETWO_PILOT_SMOKE = '1'
npm --prefix frontend run e2e
Remove-Item Env:TAKETWO_PILOT_SMOKE
$env:TAKETWO_DURATION_SMOKE = '1'
npm --prefix frontend run e2e
Remove-Item Env:TAKETWO_DURATION_SMOKE
```

Options are independent; only provide sources for the desired mode. Preparation validates inputs and refuses an existing output. It copies originals, normalized audio and manifest, never databases, capabilities, scientific reviews or cached stages. The five-take fixture expects the user-confirmed 71-word technology transcript and files `reference.wav`, `natural.wav`, `slow.wav`, `uneven.wav`, `near-perfect.wav`. Duration mode expects the documented 45 s archival reference plus its explicitly synthetic controlled derivative. Review mode creates only unresolved drafts on fresh copies, never approvals. Native MFA/model paths remain private operator configuration.

For the optional JFK salutation import suite, additionally prepare `--archive $salutationWav --transcript $exactSalutationTextFile`, then set `TAKETWO_REAL_SMOKE=1`. This is specifically the existing 17.3 s/19-word JFK fixture and rights metadata, not a generic rights claim for any supplied audio. Early configuration errors mean **not configured**, never successful genuine-data acceptance. `TAKETWO_BROWSER_WORKSPACE` is an advanced override for an already isolated test workspace; it does not authorize using production drafts.

### Native zoom and human accessibility

`TAKETWO_ZOOM_EXECUTABLE` optionally selects a compatible full Chromium executable for the isolated extension test; no installed profile/settings are touched. The older installation failed Windows SideBySide activation; an alternate Chromium first verified native zoom. On 2026-10-13 a fresh isolated Chromium 156.0.8078.4 download passed the entire suite, including native `chrome.tabs.setZoom/getZoom` at 2.0, doubled DPR and halved layout viewport. Existing browser profiles/installations were not deleted. CSS zoom and simulated DPR are not substitutes. See [repair evidence](verification.md) for actual results. Repair/reinstall the affected Playwright browser environment before requiring that newer build.

A person must still use Narrator/NVDA to hear labels, skip/heading focus, import errors, processing stages, numeric boundary editing, selection playback, annotation descriptions, submission feedback and table/chart alternatives. Record actual spoken behavior, browser/version and failures. Automated axe/zoom does not close this gate.

### Complete-application Python tests

Run `npm --prefix frontend ci` and `npm --prefix frontend run build` before the full pytest suite on a fresh checkout. Launcher and Windows recovery tests start the real service and require `frontend/dist/index.html`. The intentionally missing-build test still supplies a missing path. Recovery startup diagnostics retain at most 8 KiB of sanitized command/status/output, drain subprocess pipes continuously, fail early on exit and retain the 30 s startup budget. Normal hard-crash tests still verify application/kernel cleanup. See [current CI evidence](verification.md).

To test a fresh browser installation without replacing existing caches, set `PLAYWRIGHT_BROWSERS_PATH` to a new ignored directory under `local-data` before both `npm --prefix frontend exec -- playwright install chromium` and `npm --prefix frontend run e2e`. Use `TAKETWO_BROWSER_PORT=8877` when preserving the normal private service at 8765.

### Mobile refinement regression

`navigation.ts` selects the native phone workspace control or desktop navigation buttons. Full collection/history selection occurs in Recording Library; history reopens Analysis Workspace with its stored request. `zz-mobile.spec.ts` checks first-viewport result visibility at 320 px, absence of the collection in other tasks, complete card reachability, independent native audio cursors/selections across switching, bounded replay, keyboard selection and axe on all five areas. Generated signals remain software-only fixtures. The five-width genuine-copy screenshot/print results are documented in [mobile refinement audit](verification.md).

`zz-inspection.spec.ts` verifies single-reference and paired states with generated oscillators: pair inventories, historical selection/refresh, delayed and mismatched report identity, five-width first viewports, axe and separate print presentations. Font maps, PDF text operators and tagged structure guard against full-page raster output; local pypdf/Poppler inspection separately verifies extracted text and rendered page layout. See [reference inspection audit](verification.md).

## Resource and pitch diagnostics

Use authorized imported recordings and a fresh output name for each measurement.
Keep heavy jobs serial; benchmarks neither approve text nor create ground truth.
The helpers refuse output overwrite and preserve original inputs:

```powershell
uv run python scripts/benchmark_duration.py $privateWorkspace --reference $referenceId --pair $pairId --alignment-config $actualAlignmentConfig --output $newMeasurementJson
uv run python scripts/inspect_pitch.py --workspace $privateWorkspace --output $newPitchJson --probes
```

For arbitrary analysis CLI timing use `uv run python scripts/benchmark_analysis.py
--output $newMeasurementJson -- <actual analysis arguments>`. Record commands, exits,
configuration, hardware and concurrency. Kernel worker commit, sampled process-tree
working set and browser/API measurements are distinct; sampling can miss peaks and
count shared pages twice. The measured workloads and unresolved failures are in
[verification](verification.md), not general capacity guarantees.
