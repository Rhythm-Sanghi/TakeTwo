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

Generated oscillator/browser fixtures establish software behavior only. Stop the known local service before E2E, which owns port 8765 and creates a fresh ignored workspace. If documented genuine source/config files exist locally, run `uv run python scripts/measure_browser_smoke.py --output .\local-data\acquisition\phase5-browser.json` once with a fresh filename; otherwise reacquire/review sources before that optional check. Models/audio are deliberately not shipped. The five Windows tests in `tests/test_web_recovery.py` exercise actual process termination, bounded allocations and restart behavior; full pytest includes them.

## Collected dataset to report

Prepare `dataset-annotations.json` as a nonempty array of actual dataset Annotation records from both reviewers, using the participant/pair IDs and text hash from the first inventory export. Follow [dataset fields](dataset-engineering.md): positive-width native intervals, reviewer, listening rationale, review status and uncertainty. Reviewed acceptable spans use severity 0; flaws use 1/2/3. Publication checks these manifest annotations separately from comparison Review artifacts. Missing-pause anchors belong only to comparison flaw reviews; never invent silence intervals for manifest labels. Complete annotations before comparison so report dataset hashes stay current. Pause the command sequence after export to fill these records from real listening.

Create all filenames described in [ACTION-REQUIRED](ACTION-REQUIRED.md), per [ImportSpec](dataset-engineering.md), before running this sequence. This is a parameterized operator recipe, not a claim that these collected files exist. Substitute the actual family directory once. Check `$LASTEXITCODE` after every native command; stop on operational failure before consuming output.

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

Find the actual pair ID in `collection-ledger.json` under `dataset.pairs`; bind it to `$pairId`. Inspect alignments/features and fill the six actual review files. The [schema](comparison-schema-v1.json) and [worksheet](annotation-worksheet.md) define every required field. Reviews use original **payload** digests and exact provenance, not file-byte hashes. Timing reviews require all canonical words plus complete phrase partitions. Flaw reviews require full listening coverage and two independently prepared, explicitly reconciled inventories; retain superseding history.

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

## Current technical-report draft

Use a separate ReportLab document-tool environment on Windows; do not add authoring packages to TakeTwo runtime dependencies. Run `python scripts/build_submission_report.py --date "13 OCT 2026"`. It renders current `docs/technical-report.md` to the Git-ignored owner-review file `output/pdf/taketwo-technical-report-current.pdf`, enforces six pages and rejects the historical PDF destination. Render/inspect every page before delivery. The archived source and historical PDF stay unchanged. A later public report release requires explicit owner approval; do not force-add this draft.

Source archives use an explicit Hatch manifest; after building, `scripts/audit_release.py --packages` also rejects unsafe wheel/sdist members. The wheel is API/CLI only; frontend source is preserved in the sdist for `npm ci`/build. LF checkouts are enforced by Git attributes. Old artifacts with differing byte-based source hashes require explicit recomputation; preserve originals rather than rewriting provenance.
