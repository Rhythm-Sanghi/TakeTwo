# Track C submission

TakeTwo — Speech analysis workspace. **Created by Rhythm Sanghi.** No submission
receipt has been supplied; portal submission status is unverified.

## Deliverables and current evidence

| Deliverable | Link / verified scope / remaining action |
| --- | --- |
| Public code and documentation | [TakeTwo repository](https://github.com/Rhythm-Sanghi/TakeTwo). Code baseline `6c35e65` passed [Windows CI](https://github.com/Rhythm-Sanghi/TakeTwo/actions/runs/38683403376); the pilot tag identifies that code. Subsequent documentation commits require their own exact-commit CI. |
| Public paired dataset, text and alignment labels | [TakeTwo Pilot Dataset v1](https://github.com/Rhythm-Sanghi/TakeTwo/releases/tag/pilot-dataset-v1), [verified ZIP](https://github.com/Rhythm-Sanghi/TakeTwo/releases/download/pilot-dataset-v1/taketwo-pilot-v1.zip): five genuine same-speaker recordings, original intended passage and four automatic, unreviewed alignments. Public pilot available; **full Track C corpus requirement remains incomplete**. No independent transcript/timing/flaw ground truth. See [contents, rights and checksum verification](dataset-publication.md#published-pilot-dataset-v1). |
| Functional interactive prototype | Local import, CPU alignment/features, native playback, review and exports have scoped software/genuine-processing evidence. Actual usefulness, spoken accessibility and independent speech accuracy remain open. |
| Technical report, at most six pages | [Current PDF](../output/pdf/taketwo-technical-report-2026-10-15.pdf), [public report link](https://github.com/Rhythm-Sanghi/TakeTwo/blob/master/output/pdf/taketwo-technical-report-2026-10-15.pdf), [editable source](technical-report.md). Dated snapshot predating pilot publication; its no-public-dataset statements are superseded by the verified pilot status above. Historical evidence citations are resolved in verification. |
| YouTube demonstration, 3–10 minutes | [Owner-supplied demonstration](https://youtu.be/DfFTmNTAB6E). Prior publication checks recorded signed-out playback, 6:23 duration and the repository description link. Full narration/recording permission review remains an owner task; video permission does not grant dataset rights. |

The unchanged [Track C statement](../requirments/Track%20C.pdf) and
[requirements matrix](requirements-matrix.md) retain every technical requirement,
acceptance criterion and official 30/25/20/15/10 judging weight. Software fixtures,
performer intent and automatic timestamps cannot replace independent human labels.
One connected family cannot establish held-out generalization. No mandatory gate is
waived and acoustic association is not psychological causation. See
[verification](verification.md) for measured results, failures and limits.

## Devpost fields

| Field | Prepared value |
| --- | --- |
| Project | TakeTwo |
| Description | Speech analysis workspace |
| Tagline | Compare speech. Understand the difference. |
| Repository / demonstration / report | Use the actual links above; verify access after final publication |
| Built With | Python, FastAPI, NumPy, SciPy, librosa, soundfile, Montreal Forced Aligner, Kaldi, SQLite, React, TypeScript, Vite, uPlot, **OpenAI Codex**, **ChatGPT** |
| Public dataset | Use the published pilot release/ZIP above, accurately labeled single-speaker and preliminary; independent ground truth and full corpus acceptance remain unavailable |
| Submission receipt | Not supplied; preserve the actual portal confirmation when available |

Rhythm Sanghi directed the product goals, visual identity, interface/workflows and
scope, supplied private practice recordings and intended transcripts, reviewed results
and guided submission preparation. TakeTwo compares native-time acoustic/timing evidence
and supports A/B inspection instead of an unexplained judgment. Delivery-v0 remains
uncalibrated; independent F0/timing/flaw truth, held-out accuracy, calibration and
cross-speaker generalization are unavailable. Scores abstain when evidence is missing.

OpenAI Codex assisted implementation, integration, testing and documentation.
ChatGPT assisted planning, technical review and development guidance. The creator
directed decisions and reviewed results; neither tool supplies consent, independent
human labels or listening acceptance. Keep both tools in Built With and retain the
README disclosure. See [licenses and attribution](attributions.md).

## Owner checklist

1. Review the exact local documentation changes, authorize push when satisfied, then
   verify remote HEAD and its own Actions result. Do not infer green CI from an older SHA.
2. Check the full video for clear narration, accurate claims, permissions and private
   paths/identities/keys. Dataset redistribution needs separate item-specific clearance.
3. Obtain permitted substantive public sources, exact-text spectrum and actual independent
   transcript/timing/flaw review using the [review protocol](review-protocol.md). Retain
   disagreements, immutable revisions, exclusions and unavailable metrics honestly.
4. Complete real listening, manual zoom/spoken accessibility and clean second-machine
   acceptance. A green automated suite supplies none of those human results.
5. Verify the live [organizer rules and portal](https://multimodal-ai-hackathon-2026-7.devpost.com/rules),
   deadline/state and actual public downloads before submission. Enter real links and
   both AI Built With tags, distinguish the public pilot from unmet full-corpus requirements and retain a real
   submission receipt. Prepared files are not a submitted entry.

Only the five approved recordings, original intended passage and documented pilot
metadata/automatic exports were published as a release asset. Signed consents, identity
mappings, models, operator keys, reviewer records and databases remain private.
The pilot audio and passage are CC BY 4.0, copyright (c) 2026 Rhythm Sanghi; MIT
covers original code/documentation separately. No portal submission is claimed.
