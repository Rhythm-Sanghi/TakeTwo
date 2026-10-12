# TakeTwo dataset engineering (Phase 1)

Speech analysis workspace. The local dataset pipeline is implemented; the competition corpus is **incomplete, not independently annotated or ready for publication**. This guide describes the dataset tools. Alignment/acoustics, scoring and the web workspace are documented in [analysis engine](analysis-engine.md), [comparison engine](comparison-engine.md) and [frontend](frontend-workspace.md). [Dataset strategy](dataset-plan.md) and [scoring policy](scoring-policy.md) remain authoritative scientific policies.

## Install and verify on Windows

Use Python 3.11 and uv. Runtime dependencies are pinned in `pyproject.toml`; `uv.lock` locks the transitive graph and distribution hashes. No GPU framework is installed. Run from the repository root:

```powershell
uv sync --locked
uv run pytest -q
uv run ruff check src tests
uv run ruff format --check src tests
uv run taketwo-dataset --help
```

NumPy/SciPy provide arrays and polyphase resampling, soundfile decodes audio, Pydantic validates contracts, and librosa supplies pitch-preserving tempo/local pitch edits. librosa brings scikit-learn, Numba and llvmlite transitively; TakeTwo does not train or use a classifier. FastAPI/SQLite/frontend dependencies are deferred. CPU transformations run serially; first-use JIT time is not an inference benchmark.

## Workspace and schema

Initialize a new local directory, normally under ignored `local-data/` or outside the checkout. Never initialize over an existing directory. `manifest.jsonl` is the atomic source of truth, with `{kind,data}` rows: one version header, then recordings, pairs, annotations and an optional split report. Original and normalized audio live in `originals/<recording-id>.<wav|flac>` and `normalized/<recording-id>.wav`. The manifest contains no machine-specific absolute artifact paths. IDs are content-derived and stable for identical inputs/metadata/software versions; mutable recording names are not identifiers.

The implemented [JSON Schema](dataset-schema-v1.json) describes the assembled dataset object used by export; row payloads use its Recording/Pair/Annotation/SplitReport definitions. `schema` emits the same schema. Unknown fields/versions, duplicate JSON keys/IDs, nonfinite numbers and malformed relations are rejected. Changes to contracts require a schema version/migration; there is no silent migration command.

Recording rows contain dataset/family/speaker IDs, source vs self-recorded vs synthetic origin, role, original filename, immutable original/normalized hashes, canonical sample hash, decoded technical metadata, quality flags, processing versions, transcript and provenance. Transcript records preserve original text, normalized tokens and original-text token offsets. Normalization applies Unicode NFKC/case folding to tokens, standardizes apostrophes and ignores punctuation; spoken repetitions and word changes remain significant. This establishes *text metadata* identity, not proof the audio speaks those words. Unverified human pairs remain `needs_review` until both transcripts have explicit two-reviewer verification evidence.

Provenance requires source/work IDs, source description, URL or collection method, access date, excerpt offset, rights-holder, license/permission evidence reference, attribution and adaptation/redistribution permissions. References additionally need an explicit selection rationale. Self-recorded mirrors require a consent evidence reference. Pending rights are an honest draft state; missing required fields are errors. The program checks assertions and consistency, not the legal validity of a license or the authenticity of an approval. Keep private permission/consent records outside the public checkout and use stable evidence references, never credentials.

## Import metadata

Supply a JSON file matching `ImportSpec` in `src/taketwo/dataset/schema.py`. This structural example intentionally uses pending rights and an unverified transcript; replace identifiers/descriptions with actual acquisition records. It is not evidence of an acquired speech or permission.

```json
{
  "family_id": "speech-family-01",
  "speaker_id": "source-speaker-01",
  "origin": "source",
  "transcript": {
    "text": "Replace with the exact spoken excerpt.",
    "language": "en",
    "status": "unverified",
    "reviewers": [],
    "verification_date": null,
    "revision": "v1"
  },
  "provenance": {
    "source_id": "archive-item-01",
    "work_id": "speech-work-01",
    "source": "Replace with the actual archive title and publisher",
    "source_url": null,
    "collection_method": "Replace with the actual acquisition method",
    "access_date": "2026-10-11",
    "excerpt_offset_s": 0.0,
    "baseline_rationale": "Replace with the human reference-selection rationale",
    "consent_evidence": null,
    "rights": {
      "status": "pending",
      "holder": "Replace with the identified rights-holder",
      "license_name": "Permission pending",
      "evidence": "Replace with the actual rights-review ledger reference",
      "attribution": "Replace with the required attribution",
      "permits_adaptation": false,
      "permits_redistribution": false
    }
  },
  "channel": null
}
```

For a human mirror use `origin=self_recorded`, the same family/work and canonical words, a distinct speaker and collection source, and actual consent evidence. `status=verified` requires at least two distinct reviewer IDs and an ISO verification date. Do not assert verification without listening review. Human recordings get no automatic flaw timestamps.

## Working commands (PowerShell)

These examples require your actual local audio, metadata, recipe and annotation files. The command paths/IDs are placeholders for those inputs, not included dataset assets.

```powershell
$workspace = '.\local-data\pilot-v1'
uv run taketwo-dataset init $workspace --version pilot-v1
$reference = uv run taketwo-dataset import-reference $workspace --audio .\reference.wav --metadata .\reference.json | ConvertFrom-Json
uv run taketwo-dataset import-flawed $workspace --reference $reference.recording_id --audio .\mirror.flac --metadata .\mirror.json --category pacing --severity 2
uv run taketwo-dataset split $workspace --seed 17 --ratios 0.5 0.25 0.25
uv run taketwo-dataset generate $workspace --reference $reference.recording_id --recipe .\recipe.json
uv run taketwo-dataset annotate $workspace --annotations .\annotations.json
uv run taketwo-dataset validate $workspace --reproduce
uv run taketwo-dataset export $workspace --output .\pilot-manifest-export.json
uv run taketwo-dataset validate $workspace --publication --reproduce
```

Success emits JSON on stdout; structured argument/schema/I/O errors go to stderr with exit 2. A decoded-but-invalid dataset produces a validation report and exit 1; valid drafts return 0 with warnings. Check `$LASTEXITCODE` after every command before using its output. No command overwrites an export or audio artifact. The export contains the assembled manifest and inventory/validation summary; it does **not** copy audio or private evidence. Include the managed audio directories separately only after release review.

## Transformations and time maps

A recipe is JSON with a required recorded `seed` and an ordered list of nonoverlapping operations in **parent native time**. Operations are deterministic and currently use no randomness; the seed is provenance, not a promise of stochastic generation. Each operation includes `kind`, `start_s`, `end_s`, `value`, and intended severity 1/2/3. Severity is the author's intended label, not a calibrated or independently reviewed rating.

```json
{
  "seed": 17,
  "operations": [
    {"kind":"insert_pause","start_s":1.2,"end_s":1.5,"value":0.3,"severity":1},
    {"kind":"tempo","start_s":2.0,"end_s":4.0,"value":1.5,"severity":2},
    {"kind":"gain","start_s":4.5,"end_s":5.5,"value":0.5,"severity":2}
  ]
}
```

This example is valid only when the actual parent contains the stated reviewed pause/speech intervals and sufficient duration. Do not apply guessed intervals to a real recording.

| Kind | Meaning and bounds | Timing and safeguards |
| --- | --- | --- |
| `insert_pause` | Value adds 0.05-5 seconds of silence at the start of a selected quiet gap | Selected interval RMS must be <=-50 dBFS; original samples retained |
| `shorten_pause` | Value retains 0.05-0.95 of a selected pause | At least 150 ms, RMS <=-50 dBFS; quiet-gap interpolation is not a speech tempo method |
| `tempo` | Value 0.5-2 is speed; >1 faster, <1 slower; 1 rejected | Librosa phase vocoder, at least 128 ms; output length `round(input_length/value)`; pitch preservation checked on fixtures |
| `gain` | Local amplitude multiplier 0.1-3; 1 rejected | At least 20 ms; 10 ms boundary ramps; whole-file gain rejected as a delivery label |
| `pitch_shift` | Local shift -4 to +4 semitones; 0 rejected | At least 128 ms; same duration, 5 ms boundary fades; whole-file register shift rejected |

Combined flaws use multiple operations on one reference; nested synthetic parents are rejected to keep lineage/time maps auditable. Phase-vocoder edits can smear transients/change timbre; local pitch shifts do not implement pitch-range compression or guarantee formant preservation. Listen and independently annotate before using them as perceptual examples. Unsupported transformations are rejected, never replaced with approximate labels.

Each synthetic recording stores parent ID/hash, exact recipe/hash, software versions and a piecewise integer-sample map at 16 kHz. Segments distinguish unchanged, modified and inserted support; inserted segments have zero source width and positive output width. Mapping covers the entire parent and output. `remap_interval` projects parent intervals into derivative time; do not copy parent timestamps directly. New automatic annotations describe the resulting **edit support**, not detected flaws or validated onset/offset. They are always `source=synthetic_recipe`, `review_status=unreviewed`, with no invented reviewer or numeric uncertainty.

## Annotation workflow

`annotate` imports a nonempty JSON array of Annotation objects. Obtain pair/recording IDs and transcript hashes from export. Required fields: ID, pair/participant IDs, transcript hash, category, start/end seconds, severity, source, review status, nullable reviewer ID, rationale, nullable uncertainty seconds, nullable half-open token span and nullable transformation hash. Optional `supersedes` links a prior annotation without deleting it.

Categories: `pacing`, `pause_behavior`, `energy_variation`, `pitch_dynamics`, `acceptable`, `recording_quality`, `alignment_uncertainty`. Only `acceptable` uses severity 0. Human review records can use `unreviewed`, `reviewed` or `adjudicated`; the latter two require an actual reviewer ID. Intervals must be finite, positive-width and within the participant's duration. Token spans must be within its canonical tokens. Null uncertainty means not estimated, not zero error. Phase 1 stores interval labels only; boundary-event labels for absent pauses belong to the later alignment/grounding schema extension.

Retain recipe labels and independent human labels separately. A human review of a synthetic edit uses a new `source=human` annotation; never relabel the generated record as reviewed. Apply the independent two-reviewer/adjudication process in the dataset plan, keeping unjudgeable spans and disagreements. Intended pair severity and reviewed annotation severity can disagree; generated parameter strength is not a human rating. The optional pair `reviewed_severity` is reserved for an explicitly curated aggregate and validated against human labels; the CLI does not invent one.

## Splits, validation and publication

Create splits after importing all real references and mirrors, before derivatives or calibration. Connected groups join family, source ID, work ID, exact canonical transcript, original/canonical-sample hashes, source/mirror speakers, reference pairs and transformation parents. Fixed-seed group shuffling with largest-remainder allocation targets 50/25/25 by **group**, not file count. Group IDs depend on real members so adding derivatives retains existing assignments. Imports of new real recordings and split reassignment are blocked after freezing; use a new dataset version/workspace for acquisition revisions. Small corpora report empty split and fewer-than-three-test-group warnings. Near-duplicate/semantic paraphrase discovery still needs human acquisition QA; hashes only detect exact matches.

`validate` checks schema, relations, severity, annotation provenance, managed paths, files, hashes, actual decoding/technical metadata, channel/quality metadata, time maps and deterministic split replay. `--reproduce` additionally rebuilds normalized/altered samples and checks transformation time maps. Use the locked environment: version drift is a warning for ordinary validation and an error for replay. Same-runtime output bytes and semantic manifests are regression-tested; replay uses absolute sample tolerance `1e-6` with no relative tolerance. Cross-platform numerical equivalence has not been measured; a second-platform run is still required before claiming it.

Canonical derivatives are mono 16 kHz IEEE float32 WAV with a deterministic header/fact chunk and no volatile PEAK timestamp. No trimming, denoising or automatic loudness correction occurs. Channel cancellation requires explicit selection. Inputs support PCM/float WAV and PCM FLAC, 8-96 kHz, 1-2 channels, >0 to 600 seconds and <=100 MiB. Silence/near-silence below -60 dBFS RMS is rejected. Clipping (>0.1% samples at magnitude >=0.999 or any value >1) is preserved/flagged in draft imports and blocks publication; transformations that create clipping/near-silence are rejected. These heuristics are not speech-quality judgments.

`--publication` turns pending rights, unverified transcripts/identity and recording-quality flags into errors. It also requires two source families, reviewed human near-perfect/severe mirrors, the intended severity spectrum, reviewed annotation by two reviewers per pair, frozen splits with train/validation and at least three independent test groups. Passing is a structural release preflight, not proof of legal clearance, perceptual validity, official acceptance or dataset completion. Final human release review remains necessary.

Mutations use an exclusive workspace lock and atomic manifest replacement; failed operations roll back their new artifacts. Existing artifacts are never overwritten. Paths reject traversal, symlinks/junctions/reparse points, UNC paths, alternate data streams and reserved Windows names. Keep the workspace under the user's exclusive local control: checks do not promise protection against a hostile process changing filesystem objects between checks. After a crash, inspect the lock and any unreferenced artifacts before removing them; do not delete originals automatically.

## Acquisition status and next action

Phase 1 initially had no cleared reference. Phase 1B now has two public-domain source masters and one imported draft candidate; see [pilot collection](pilot-collection.md). No consented mirror, independent transcript review or public dataset exists. Automated tests and CLI smoke runs use explicitly labeled generated signal fixtures outside the competition dataset. They establish software behavior only.

The [FDR Presidential Library audio index](https://www.fdrlibrary.org/utterancesfdr) was inspected as an acquisition lead. Its MP3 downloads and general reference-use notice do not by themselves clear a particular recording for adaptation/public dataset release. No asset was downloaded or marked cleared; obtain item-specific terms/permission and a supported archival WAV/FLAC or document a reviewed external conversion separately. No MP3 dependency was added.

Next: identify two suitable public-speech excerpts, archive asset-specific rights evidence, verify exact transcripts with two reviewers, recruit consenting split-disjoint mirror speakers, record near-perfect/severe variants and import independent interval annotations. Until then the original Phase 1 **dataset pilot** gate remains open even though the software pipeline is available.
