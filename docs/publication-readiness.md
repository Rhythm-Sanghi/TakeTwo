# Submission readiness

TakeTwo - Speech analysis workspace. Checked 15 October 2026.

## Public release and links

- [GitHub repository](https://github.com/Rhythm-Sanghi/TakeTwo): public `master` at `faebbc996b742e88a71101bda5322a2b5142a477`; fetched local/remote refs matched.
- [Windows CI for that exact release](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38617800894): **completed successfully**, including backend/frontend tests, builds, audits and generated browser E2E. New cleanup commits need their own hosted run.
- [TakeTwo demonstration](https://youtu.be/DfFTmNTAB6E): supplied by the owner; signed-out page access/playback and **6:23** duration verified. Sampled footage shows the actual TakeTwo UI; description links to the correct repository. This is a limited browser check, not full narration, permission or scientific acceptance review.
- [Current technical report](../output/pdf/taketwo-technical-report-2026-10-15.pdf): publicly downloadable six-page searchable PDF. A minimal creator-attribution correction is prepared locally; the approved previous bytes remain in Git history. [Source](technical-report.md).
- Public paired dataset: **unmet requirement**. No approved redistribution-ready independently annotated corpus or URL exists. Five private takes, models, consents and reviewer evidence remain excluded.
- Devpost: [field-ready checklist](submission-draft.md); no submitted-entry receipt supplied.

The [current organizer rules](https://multimodal-ai-hackathon-2026-7.devpost.com/rules) state
**15 October 2026, 12:15 PM IST**. This supersedes earlier midnight statements.
AI tools must appear in Built With and their contribution must be disclosed in README.
The required entries are **OpenAI Codex** and **ChatGPT**.

## Run and reproduce

Use `.\scripts\start-local.ps1 -Setup` once, then `.\scripts\start-local.ps1`.
Open `http://127.0.0.1:8765`; stop with Ctrl+C. [Windows prerequisites](windows-setup.md)
and separate [MFA/model configuration](analysis-engine.md) remain necessary.
Without MFA, actual acoustic inspection/playback work and alignment explicitly abstains.
The code license grants no recording/video redistribution permission.

## Verification scope

| Evidence | Executed result |
| --- | --- |
| Application hardening | 376 backend, 81 frontend, 18 generated browser and 3 private genuine-pilot tests passed; [exact counts, failures and limits](final-hardening-completion.md) |
| Previous publication pass | 31 relevant backend and 81 frontend tests passed; typecheck/build/lint/lock, normal and setup launch smoke, 72 Markdown/359 local links/6 schemas passed |
| Previous publication privacy | 226 files and 707 reachable history blobs; zero blocking candidate/history/package findings; 38 protected hashes matched |
| Previous report | Six rendered pages and dual text extraction; downloaded public bytes matched SHA-256 9cf5aab50f8f6811267a03c157ed3848f30b4309f54b409d2de9dc4c83a3287b |
| Current cleanup | 31 relevant backend tests passed (26.63 s, one existing upstream warning); frontend typecheck/build; Ruff lint/format (79 files); uv lock (49 packages); 65 Markdown/306 local links/6 schemas; startup and corrected six-page dual-extractor PDF checks passed |
| Cleanup privacy/package checks | 219 candidate files / 707 pre-commit reachable blobs, zero blocking findings; package inventory excludes all seven removed files; all 38 protected hashes unchanged |

Original phase records retain useful experimental/defect evidence. Redundant initial
planning files are consolidated into their completed validation documents, with links
repaired. No application source, test coverage, scripts, locks or scientific policy
was removed. `AGENTS.md` remains an active maintenance file; the official statement
stays at its existing path to preserve source/package checks and references.

## Remaining owner actions

1. Approve the concrete cleanup and corrected report before publishing; confirm final remote SHA and its own Actions result.
2. Review the full video's narration, visible/audible recording permission, claims and privacy. Access/duration checks do not establish those approvals.
3. Resolve the mandatory dataset requirement through [rights, independent review and release validation](dataset-publication.md), or disclose that it remains unmet.
4. Complete actual listening, spoken accessibility and clean-machine review before claiming acceptance.
5. Enter actual GitHub/video/report links and AI Built With tags in Devpost; verify the portal state/deadline and preserve the real submission receipt.
