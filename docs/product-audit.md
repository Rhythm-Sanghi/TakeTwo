# Product stabilization audit

TakeTwo — Speech analysis workspace. Baseline inspected: `be55e68`, 2026-10-12. Existing untracked `speech-01/` contains the user's five WAV originals; preserve privately. The user supplied the practice transcript and confirmed one speaker. No independent verification or public consent is inferred.

Fifteen reproducible defects: **0 P0, 12 P1, 3 P2**. Focused repairs address all fifteen; verification and external gates are recorded in [validation](product-validation.md).

| ID / priority | Reproduction / actual behavior | Expected / root cause | State |
| --- | --- | --- | --- |
| U1 / P1 | Open empty import; only Public source reference exists | Human participant type always visible, with an explicit missing-reference explanation. Type and pair selection are combined in ImportForm | Fixed |
| U2 / P1 | Import self-recorded reference through dataset API | Controlled local reference supported distinctly from public source. workspace rejects non-source references despite origin contract allowing self_recorded | Fixed |
| U3 / P1 | Try ordinary local import | User must fill internal family/work/source/speaker IDs and public-rights fields. Frontend forwards full scientific ImportSpec without a local draft adapter | Fixed |
| U4 / P1 | Import participant then inspect | UI clears pairId after import, so workspace defaults to reference-only. Async inventory refresh does not select returned pair | Fixed |
| U5 / P1 | Need to correct an accidental reference choice | No supported immutable correction action; UI requires external manifest/version work | Fixed |
| U6 / P1 | Open history | Offset timestamps are sliced then labeled UTC without conversion, and raw job IDs dominate labels | Fixed |
| U7 / P1 | Import then run a >30 s recording | Only late API failure explains analysis limit; no useful excerpt creation path. Four actual pilot files exceed cap (reference 30.224 s, natural 30.590 s, near-perfect 31.760 s, slow 40.590 s; uneven 29.370 s) | Fixed |
| U8 / P1 | Refresh after adding inputs/reviews | Active report effect depends only on job ID/path, allowing a stale displayed report after dataset change. Backend correctly rejects stale evidence | Fixed |
| U9 / P2 | Fail feature request then choose another series | Timeline error can persist after a successful feature fetch; shared waveform/feature error state | Fixed |
| U10 / P2 | Launch from script repeatedly | Launcher reinstalls/builds each time and omits port/prerequisite handling; no normal-start path | Fixed |
| U11 / P1 | Attempt eligible review handoff in browser | Existing reviewer imports are CLI-only. UI needs an actual review-file handoff and explicit transcript-correction guidance without generating approval | Fixed |

The first eleven rows above describe the original defects; their status is now **fixed**. New backend acceptance tests cover compact public/controlled/human imports, actual role mapping, draft rights, pairing/mismatch, duplicates/corrupt input, original retention, native excerpts, safe correction, v1 compatibility/backup, report persistence/replay, review handoff and launcher errors. Eleven frontend tests cover existing interactions, progressive imports and excerpt refresh recovery. The archival run additionally exposed delayed report delivery after job completion; U8's loading/revalidation repair now announces that state explicitly.

| ID / priority | Reproduction / root cause | Repair |
| --- | --- | --- |
| U12 / P1 | Unlabeled take defaulted to acceptable/severity 0 | V2 stores unspecified/null unless actual intended labels are supplied |
| U13 / P2 | Unavailable MFA checkbox appeared checked while request used false | Checkbox reflects actual availability/request |
| U14 / P1 | Unrelated import invalidated whole-dataset report digest | Checksummed snapshots retain exact context while validating used members/pair/reviews/artifacts/config/code |
| U15 / P1 | Fieldset intrinsic width overflowed 320 px | Explicit min-width zero; actual browser overflow assertions pass |

The software browser journey passed with CPU processing, cancellation/retry, playback/seeking/zoom/pan, report exports, historical report after unrelated import, controlled pairing and separate correction. The actual five private WAVs were imported through Chromium as one controlled reference/four participants, with four needs-review pairs, one speaker, null unknown rights/severity, real waveform/seek and explicit 30-second blocking. All four areas passed axe and no-page-overflow assertions at desktop and 320 px. These are software/import results, not independent human evaluation.

Actual 200% native browser zoom remains unverified: full Chromium cannot spawn on this host; its isolated real-zoom test is explicitly skipped. Spoken screen-reader verification is unavailable. Human text/timing/flaw reviews, public-release permission, rubric calibration and held-out accuracy remain external gates. No P0 defect is established. Public archive and controlled practice acceptance remain separate; passing tests do not close scientific or manual-accessibility gates.
