# Blank consent and recording provenance record

TakeTwo — Speech analysis workspace. Copy per participant/source into private collection storage. **Blank form: no permissions or decisions are asserted.** The owner must agree a specific release scope with the participant before capture/publication. Keep names, signatures and contact details out of Git and public datasets.

| Private session field | To be completed by the actual collector/participant |
| --- | --- |
| Record ID / date / collector | |
| Participant name / adult eligibility confirmation | |
| Public speaker pseudonym / private identity-map location | |
| Family/work/script revision and transcript hash | |
| Recorded filenames / recording date | |
| Microphone, recorder, sample rate, channel, distance, gain | |
| Room/noise / AGC, enhancements or conversion used | |
| Intended delivery changes (kept hidden from labelers) | |
| Project contact / retention period / withdrawal contact and cutoff agreed | |

Discuss each permission separately and record **yes/no/unresolved**, the exact scope and any restrictions. An unresolved/declined public permission blocks redistribution; it does not become assent by leaving the row blank.

| Permission to be discussed | Decision / agreed scope / restrictions |
| --- | --- |
| Voluntary audio recording for TakeTwo analysis | |
| Local acoustic processing and independent annotation | |
| Creating controlled altered derivatives | |
| Public distribution of original/excerpt audio and transcript | |
| Public distribution of synthetic derivatives and annotations | |
| Inclusion in a hackathon demonstration/YouTube video | |
| Exact proposed audio/dataset license and public hosting destination | |
| Public pseudonymous metadata; excluded identifying information | |
| Withdrawal procedure before release and limits after public copying explained | |
| Questions answered / opportunity to decline | |
| Participant confirmation/signature/date; collector confirmation/date | |

Publish only a redacted permission summary if actually permitted. Metadata `consent_evidence` references this private record by stable ID; do not expose its filesystem path or identity mapping. Reviewers separately record independence/conflicts and actual listening evidence.

For source audio, also record original archive URL/item, creator/rights-holder, source/work IDs, access date, master hash, master-relative excerpt start/end, transcript source, item-specific license evidence, adaptation/redistribution permissions, required attribution and human baseline-selection rationale. Archive the actual evidence. Public availability alone is not a release decision.
