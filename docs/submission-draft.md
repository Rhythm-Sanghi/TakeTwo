# Devpost submission handoff

TakeTwo - Speech analysis workspace. Prepared 15 October 2026; not submitted.

## Fields to enter

| Field | Prepared value / owner action |
| --- | --- |
| Project name | TakeTwo |
| Tagline | Compare speech. Understand the difference. |
| GitHub | https://github.com/Rhythm-Sanghi/TakeTwo |
| Technical report | [Current public six-page report](https://github.com/Rhythm-Sanghi/TakeTwo/blob/master/output/pdf/taketwo-technical-report-2026-10-15.pdf); attribution correction prepared locally |
| YouTube | [TakeTwo demonstration](https://youtu.be/DfFTmNTAB6E); signed-out access/playback and 6:23 duration verified; correct GitHub description link; full narration/permissions remain owner review |
| Public paired dataset | Missing; release only an approved rights-cleared, independently labeled corpus; verify download/checksums |
| Built With | Python, FastAPI, NumPy, SciPy, librosa, soundfile, Montreal Forced Aligner, Kaldi, SQLite, React, TypeScript, Vite, uPlot, **OpenAI Codex**, **ChatGPT** |
| Submission receipt | Missing; save the actual portal confirmation after manual submission |

## Project story

Created and directed by Rhythm Sanghi, who defined the product goals, interface and workflows, supplied practice recordings/transcripts, reviewed results and guided improvements.

TakeTwo helps listeners compare two performances of the same words without losing their native audio timing. Instead of a single unexplained judgment, the workspace shows measured energy, timing and supported pitch observations, explains why an interval deserves inspection, and offers native A/B replay.

We built a local CPU pipeline with provenance-aware imports, Montreal Forced Aligner, FFT/MFCC/RMS/energy/pYIN features, immutable analysis artifacts and a React workspace. Comparative insights group related windows and expose provisional word differences and alignment diagnostics. Concise summaries and full evidence reports preserve measurements and verification status. Human Review Workspace collects separate transcript, timing and flaw reviews; Dataset & Evaluation shows missing prerequisites and withheld metrics.

Five genuine private practice recordings were processed locally. Their text/timing/flaws have not been independently verified and they have no public redistribution approval. The public paired dataset requirement remains unmet. Experimental rubric scores abstain when evidence is insufficient; there is no claimed held-out accuracy, calibrated confidence or cross-speaker generalization. Accepted pitch coverage was inadequate on these takes, and production thresholds were preserved. Actual listening and spoken accessibility acceptance remain pending.

OpenAI Codex assisted implementation, tests, integration and documentation under human direction. ChatGPT assisted planning, architecture, interpretation and technical review. These tools did not supply consent, independent human labels or listening evidence.

## Final owner checklist

1. The [organizer rules](https://multimodal-ai-hackathon-2026-7.devpost.com/rules) were rechecked on 15 October: deadline **15 October 2026, 12:15 PM IST**. Verify the actual portal state and submission confirmation; prepared files are not an entry.
2. Approve the reviewed cleanup/creator-attribution changes; after push, verify remote HEAD and its own Actions run. Public faebbc9 already passed run 38617800894.
3. Confirm the full 6:23 video has clear narration, accurate claims, recording permissions and no private paths/keys/identities. Signed-out playback and the repository link were verified; full audible content and consent were not. Video permission is separate from dataset redistribution.
4. Complete the [dataset release requirements](dataset-publication.md), or explicitly disclose the unmet mandatory requirement. Do not substitute software fixtures, automatic timestamps or invented approvals.
5. Enter the fields above, attach actual public links, keep both AI tools in Built With, compare claims against the published release and submit manually if the portal permits it.
6. Retain the actual submission receipt. The owner supplied the uploaded video; this pass performed no upload or Devpost submission.

[Release evidence](publication-readiness.md), [compliance](submission-compliance.md), [attributions](attributions.md).
