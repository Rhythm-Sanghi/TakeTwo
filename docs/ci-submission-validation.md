# CI and submission verification — 13 October 2026

TakeTwo — Speech analysis workspace.

## Current public baseline

Public `master` at `cd2abe946b40892e3d164428f74b5acd92860d0d` passed
[Windows Actions run 38357432224](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38357432224).
The GitHub API was checked directly during this audit: completed/success,
06:34:05–06:39:40 UTC on 13 October 2026. The workflow includes Python/frontend
checks and builds, repository/schema validation, package preflight, dependency
audits and generated browser workflows. The published baseline has 301 Python,
20 frontend and three browser tests. Those counts describe that baseline.

The failed run at 35a1486 is historical, not current hosted status. Its actual
failures, local reproductions, build-order correction, package repair, clean
checkouts and original six-page report verification are preserved unchanged in
[the archived CI repair audit](ci-submission-validation-2026-10-13.md).
Earlier historical reports must not be read as the current release state.

## Subsequent local stabilization

The [stabilization audit](stabilization-audit.md) records the later evaluation
ground-truth correction, review/adjudication integration, responsive regression,
diagnostic-language improvement and executed checks. This work is local only;
no push or hosted run for these new commits has been performed. Green baseline CI
does not certify later changes. A future authorized push needs its own verification.

Ground truth now uses `exact-inventory-v1`: retain independent reviews, require
identical numerical inventories, derive canonical IDs from content, and withhold
metrics for differing boundaries until explicit reviewer revisions. Review and
evaluation v1 remain readable; historical results are never overwritten. Source
hash changes invalidate old comparison replay; regenerate comparisons from cached
acoustic inputs. Acoustic-v1 and delivery-v0 remain unchanged.

## Deliverables and owner actions

| Deliverable | Current acceptance |
| --- | --- |
| Public GitHub code/documentation | VERIFIED public cd2abe9 baseline; later local release INCOMPLETE until authorized push and exact-commit CI |
| Public paired dataset/transcripts/alignment labels | BLOCKED by rights, collection, independent annotation and public release/download verification |
| Interactive prototype | VERIFIED software workflows; genuine independent caught-deviation acceptance INCOMPLETE |
| Technical report, maximum six pages | Local owner-review draft; final content/publication approval required; historical PDF preserved |
| YouTube demonstration, 3–10 minutes | BLOCKED by permitted recording, owner-approved upload and public playback verification |
| Submission | BLOCKED by owner review, actual deliverables and manual portal submission |

The [organizer rules](https://multimodal-ai-hackathon-2026-7.devpost.com/rules)
were checked again: deadline **October 15, 2026 at 00:15 IST** (October 14 at
18:45 UTC). Finish on October 14. AI coding assistants are permitted with disclosure
in README and Devpost Built With. The checked-in three-page Track C PDF supplies
the detailed criteria; the linked hosted Drive viewer did not expose text for a
fresh byte comparison. Review organizer updates before final submission.

Five private practice takes form one unreviewed family. Existing JFK masters share
one speaker group; the imported salutation remains unverified. Neither filenames,
software-fixture assertions nor green tests establish independent ground truth,
publication consent or held-out accuracy. Spoken Narrator/NVDA acceptance and a
clean second-machine replay remain INCOMPLETE. See [owner checklist](ACTION-REQUIRED.md)
and [five-minute filming plan](demo-script.md).
