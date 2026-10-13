# Independent annotation worksheet

TakeTwo — Speech analysis workspace. Blank collection material; **not an imported review or ground truth**. Copy per reviewer and per recording. Fill fields only from actual listening and source artifacts. Use [the pilot kit](human-pilot-kit.md) for CLI steps.

| Session binding | Actual value |
| --- | --- |
| Dataset version / recording ID / pair ID | |
| Speaker pseudonym / origin (source, self_recorded, synthetic) | |
| Audio canonical sample hash / transcript hash / original text hash | |
| Analysis implementation hash / original alignment payload hash | |
| Reviewer pseudonym / date / private evidence reference | |
| Independence from performer/other reviewer and conflicts | |
| Predictions and edit recipes hidden during flaw review? | |
| Full duration / listened intervals / unjudgeable intervals | |
| Decision (unresolved until actually completed) / notes | |

## Transcript and native timing

Listen to the whole clip before checking machine boundaries. Record exact words/repetitions and audible start/end edges. Preserve the original transcript and checked correction separately. Index canonical tokens from zero; intervals are native seconds, not the other track's clock. Repeat rows for **every token**. Do not fill human boundaries by copying machine values without listening.

| Token index / canonical word / spoken form | Draft machine start/end (s) | Human checked start/end (s) | Uncertainty / mismatch / listening note |
| --- | --- | --- | --- |
| | | | |

| Phrase half-open token span [start,end) | Native phrase / pause observation | Reviewer reason / disputed boundary |
| --- | --- | --- |
| | | |

Phrase spans must partition all tokens without gaps/overlap. Review each member separately. More than 200 ms disagreement or unresolved review blocks correspondence; retain both original records and use explicit superseding revisions after reconciliation. Human timing uncertainty is not a measured detection-confidence probability.

## Independent flaw inventory

Listen without predictions, rubric scores or intended edit locations. Use the reference as acoustic context; allow effective alternatives. Mark measurable differences separately from your subjective appraisal. Label only the four evaluation categories: pacing, pause_behavior, energy_variation, pitch_dynamics. Use a positive-width native interval, or a boundary anchor only for a missing/short pause. Never invent silence for an absent pause.

| Stable label ID | Category | Native start/end or pause anchor (s) | Severity 1/2/3 | Uncertainty (s or unknown) | Audible evidence / acceptable alternative / rationale |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Severity guide for human review: **1 mild** = local noticeable difference with delivery largely maintained; **2 moderate** = clear sustained/repeated departure; **3 severe** = strong pervasive departure that materially disrupts the intended delivery. These are provisional annotation anchors, not validated engine thresholds or judgments of persuasion/ability. Record disagreements; do not infer severity from a transformation parameter or automatic score.

| Inspected native span (s) | Acceptable/no-positive coverage | Recording-quality or alignment uncertainty | Reason / re-listen required |
| --- | --- | --- | --- |
| | | | |

No-positive labels require actual full listening coverage. Null uncertainty means unknown. Use dataset annotations for acceptable (severity 0), quality and alignment uncertainty; keep these out of comparison flaw `Label` records. Keep original independent sheets before reconciliation. The current evaluator requires two approved full-coverage blinded inventories with matching IDs/category/location/severity/rationale/uncertainty. Agree a reconciled inventory only after both people have reviewed it; preserve original differences with `supersedes` history. Record exclusions and missing categories rather than choosing the more favorable reviewer.

## Handoff checklist

The [Review Workspace](review-workspace.md) provides these fields, native playback, explicit word inspection, draft saves and submitted JSON export. Use this sheet as the private evidence reference or take notes directly. Phrase end numbers are one-based word counts in the UI; exported phrase spans remain zero-based half-open token intervals. Machine suggestions are never human ground truth merely because they were loaded. Record unclear/uncertain spans honestly, preserve independent originals and retain the separate adjudicator's explanation. The operator must end handoff and close the reviewer window before showing peer evidence.

- Exact provenance copied from actual current analysis; transcript verification agrees with the reviewed dataset version.
- Actual identities/date/evidence references and independence declarations completed; consent stored privately.
- Every word and complete phrase partition checked; no guessed timestamps.
- Full flaw-review listening coverage recorded; positives, acceptable alternatives and uncertainty preserved.
- Two separate original reviews retained; any revised records identify what they supersede.
- Review JSON validates/imports with existing CLI; detector inputs contain timing reviews only.
- Evaluation split/group identities were frozen before tuning; no held-out labels used for calibration.

This checklist records reviewer work when completed; blank fields and unchecked external actions are not approvals.
