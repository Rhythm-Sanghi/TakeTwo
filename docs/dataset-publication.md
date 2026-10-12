# Dataset publication guide

TakeTwo — Speech analysis workspace. **No releasable paired dataset or public dataset URL exists.** Two acquired masters share JFK, one draft source is imported, and human mirrors/reviews are absent. This guide prepares a future owner-approved release; it does not authorize one.

## Release gate

1. Collect real substantive references, exact reviewed text, permitted faithful/flawed mirrors and independent temporal labels using [ACTION-REQUIRED](ACTION-REQUIRED.md). Separate human takes and controlled synthetic derivatives. Preserve originals and transformation lineage/maps; never call synthetic alterations real speeches.
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

Current blocker: no human corpus/labels or publication approval. The release checklist must stay open. [Attributions](attributions.md) record current sources/resources; they are not a blanket license for future media.
