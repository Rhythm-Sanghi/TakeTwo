# Browser verification

The product-experience suite also includes `zz-experience.spec.ts`, a route-only
software UI fixture for report loading, partial dimensions, eligible findings,
native interval replay and eligible-zero presentation. It intercepts report
responses in that test only, never edits a stored report or supplies genuine
review evidence. The other integration cases use actual processing/review APIs.
See [experience audit](product-experience-audit.md) for executed checks and limits.

The generated suite includes `zy-presentation.spec.ts`: actual generated 15/29/30/40/45
second WAV imports and CPU extraction, complete native domains/end samples at all
five widths, same-speaker take counts, operator preselection without access grants,
axe on expanded dimension diagnostics and real Chromium printing with all accessible
chart disclosures open. These are software signals, not speech or human evidence.
The serial case can take several minutes; production limits are unchanged. Native
zoom also loads completed charts when present. Print verification additionally
requires rendering and visually inspecting every PDF page.

Standard software tests require no private data, MFA installation or external account:

The stabilization suite adds five-area screenshots at 1920×1080, 1366×768,
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

## Private genuine fixtures

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

## Native zoom and human accessibility

`TAKETWO_ZOOM_EXECUTABLE` optionally selects a compatible full Chromium executable for the isolated extension test; no installed profile/settings are touched. The older installation failed Windows SideBySide activation; an alternate Chromium first verified native zoom. On 2026-10-13 a fresh isolated Chromium 156.0.8078.4 download passed the entire suite, including native `chrome.tabs.setZoom/getZoom` at 2.0, doubled DPR and halved layout viewport. Existing browser profiles/installations were not deleted. CSS zoom and simulated DPR are not substitutes. See [repair evidence](final-repair-audit.md) for actual results. Repair/reinstall the affected Playwright browser environment before requiring that newer build.

A person must still use Narrator/NVDA to hear labels, skip/heading focus, import errors, processing stages, numeric boundary editing, selection playback, annotation descriptions, submission feedback and table/chart alternatives. Record actual spoken behavior, browser/version and failures. Automated axe/zoom does not close this gate.

## Complete-application Python tests

Run `npm --prefix frontend ci` and `npm --prefix frontend run build` before the full pytest suite on a fresh checkout. Launcher and Windows recovery tests start the real service and require `frontend/dist/index.html`. The intentionally missing-build test still supplies a missing path. Recovery startup diagnostics retain at most 8 KiB of sanitized command/status/output, drain subprocess pipes continuously, fail early on exit and retain the 30 s startup budget. Normal hard-crash tests still verify application/kernel cleanup. See [current CI evidence](ci-submission-validation.md).

To test a fresh browser installation without replacing existing caches, set `PLAYWRIGHT_BROWSERS_PATH` to a new ignored directory under `local-data` before both `npm --prefix frontend exec -- playwright install chromium` and `npm --prefix frontend run e2e`. Use `TAKETWO_BROWSER_PORT=8877` when preserving the normal private service at 8765.
