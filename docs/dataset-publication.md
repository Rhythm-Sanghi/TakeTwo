# Dataset publication guide

TakeTwo — Speech analysis workspace. A genuine single-speaker pilot is public.
The complete independently reviewed Track C corpus remains incomplete. The pilot
below is separate from the full-corpus publication gate in the rest of this guide.

## Published pilot dataset v1

[TakeTwo Pilot Dataset v1](https://github.com/Rhythm-Sanghi/TakeTwo/releases/tag/pilot-dataset-v1)
was published on 15 October 2026 after owner approval of the exact ZIP and release
notes. [Download the ZIP](https://github.com/Rhythm-Sanghi/TakeTwo/releases/download/pilot-dataset-v1/taketwo-pilot-v1.zip).
Creator, speaker and original passage author: **Rhythm Sanghi**. Copyright (c) 2026
Rhythm Sanghi; the five recordings and complete passage are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), separately from the code's MIT license.

| Published contents | Evidence status |
| --- | --- |
| Five original 48 kHz mono PCM16 WAVs | One reference plus natural, slow, uneven and intended near-perfect participant takes; genuine self-recorded human speech, copied byte-for-byte |
| Original 71-word intended passage | Authorship/redistribution rights confirmed by its author; not independently reviewed against the recordings; identical spoken words, omissions and repetitions remain unverified |
| Four MFA 3.3.9 alignment exports | Reference, natural, slow and uneven only; automatically generated word boundaries, not independently reviewed ground truth. No near-perfect alignment is included |
| Manifest, dataset card, rights and checksums | 14 files total, including five WAVs, one transcript and four alignment JSON files; no private workspace, logs, models, database, consent or reviewer records |

Archive size: **12,882,263 bytes**. SHA-256:
`117f9fb59d7fe5575aaccdbf38c4baa5b6cff1c9331d72d14983ede75bd4a70e`.
Release asset ID 642808587 remained unchanged at publication; GitHub's digest and
the anonymously downloaded bytes matched the approved archive. The release page
and direct download returned HTTP 200 without authentication. Fresh extraction,
all 13 payload checksums, manifest/transcript/alignment references, and full decoding
of all five WAVs passed. Originals remain unchanged and ignored by Git; no binary
recordings were committed. No unrelated personal metadata or authorization record
is included. The release's dataset card supplies import/reproduction instructions.

All five takes share one speaker and one connected family. Delivery names describe
recording intention, not verified severity. The reference is a controlled practice
take, not an effective-public-speaker baseline. No human-verified timing/flaw labels,
held-out speaker results, calibration or validated precision/recall/F1 are supplied.
Automatic timestamps do not verify text or flaw regions. Full Track C dataset
requirements remain incomplete. No split, human annotation or metric was invented.

This is a preliminary portable pilot package, not a managed workspace that passes
the strict corpus publication validator. That validator remains unchanged; its
independent review, provenance, spectrum and split requirements are not waived.
The full-corpus workflow below applies to a future independently reviewed corpus.

## Release gate

1. Collect real substantive references, exact reviewed text, permitted faithful/flawed mirrors and independent temporal labels using [owner checklist](submission.md#owner-checklist). Separate human takes and controlled synthetic derivatives. Preserve originals and transformation lineage/maps; never call synthetic alterations real speeches.
2. Complete item-specific rights/attribution and actual consent. Check recording, words, excerpts, derivatives, public metadata and demonstration permissions. A code license does not license audio. Redact identity mappings/signatures/private evidence; do not merely rename consent scans.
3. Freeze connected source/work/text/speaker/family/hash/lineage groups before derivatives/calibration. Audit coverage by origin, dimension, intended and reviewed severity, speaker and split. Include near-perfect/acceptable alternatives. Record exclusions; do not increase counts with unusable clips.
4. Run `uv run taketwo-dataset validate <workspace> --publication --reproduce`. Resolve every error without weakening gates. Replay current alignment/features/comparison reports and independently inspect labels. Validation is structural preflight; actual rights/listening/release review remains necessary.
5. Export with `uv run taketwo-dataset export <workspace> --output <fresh-manifest-export.json>`. It exports metadata, not audio. Assemble a new staging directory containing only approved files and the dataset card. Preserve `manifest.jsonl` plus its exact `originals/`, `normalized/` and `derived/` relative paths in a `workspace/` directory; do not rename audio by origin and break stored references. Use a dedicated fully approved dataset version, rather than hand-filtering files from a manifest. If an original lacks redistribution permission, exclude that recording through a separately reviewed new dataset version before validation; never leave dangling references or remove required paired audio/labels.

Suggested release layout (future files, not current assets):

```text
taketwo-dataset-<version>/
  DATASET-CARD.md
  RIGHTS-AND-ATTRIBUTION.md
  manifest-export.json
  transcripts/
  workspace/
    manifest.jsonl
    originals/
    normalized/
    derived/v1/
    derived/comparison-v1/
  labels/independent-and-reconciled/
  recipes-and-time-maps/
  splits/
  evaluation/
  SHA256SUMS.txt
```

The manifest identifies source/self-recorded/synthetic origin and lineage; provide separate origin inventories in the card without changing managed paths. Automatic alignments/features are under `derived/v1`; immutable timing/flaw reviews, reports and evaluation are under `derived/comparison-v1`. Exclude `.runtime`, locks and SQLite history. The dataset card must state actual release version/date, creators/contact, scope/selection, per-origin file/pair/family/speaker counts, duration, exact-text QA, severity/category coverage, reviewers/agreement/adjudication, native clocks, exclusions, frozen split method, permitted uses/licenses per item, preprocessing/model/config/code hashes, evaluation denominators/abstentions, limitations and known pretrained-model overlap uncertainty. Do not fill target counts as achieved counts. Unavailable metrics are null with reasons.

## Checksums and public access

Generate checksums from the final staged bytes; do not hash an earlier draft. Include audio, text, labels, splits, policies and card. Review archive inventory for personal data, path traversal, absolute paths, models, environment directories, databases and credentials. Preserve upstream notices for any redistributed component. Publish only approved dataset files to GitHub or public Google Drive and put that **verified public dataset link** in README, as Track C requires.

After owner authorization/publication, download as a signed-out reader into a new directory. Verify every checksum, paired inventory, transcript identity and label bounds; run `uv run taketwo-dataset validate <download-directory>/workspace --publication --reproduce` and the documented analysis/comparison replay against those downloaded managed paths. Record URL, access date, exact archive hash, downloader commands and results. A sharing screen or logged-in preview is insufficient. Preserve prior versions. No private consent record is uploaded to demonstrate release permission.

Full-corpus blockers: effective-public-speaker baselines, independently reviewed
contrastive spectrum and temporal labels remain missing. The pilot's owner approval
and public availability do not close that checklist. [Attributions](attributions.md)
record current sources/resources; they are not a blanket license for future media.


## Release contents and provenance

A release needs actual approved audio, exact transcripts, independently reviewed
alignment/region labels, versioned manifests, transformation recipes/maps, connected
split membership, checksums, required attribution and a dataset card describing scope,
collection, exclusions, coverage gaps, limitations and item-specific rights. Distinguish
original, human take and synthetic lineage in paths and metadata. Keep signed consents,
identity mappings and unapproved media private. A redacted permission summary is public
only when its release is itself permitted. Public availability is not permission.

Publish a full reviewed corpus only after the complete rights/review gate, then
verify download hashes and link it from README as Track C requires. The published
pilot above provides real audio and automatic evidence, not completed human review.
Substantive public sources, a reviewed same-text spectrum and independent temporal
labels remain mandatory acceptance requirements.
