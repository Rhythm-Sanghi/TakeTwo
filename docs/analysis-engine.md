# Phase 2 acoustic and alignment engine

TakeTwo â€” Speech analysis workspace. The local CLI operates on imported recordings; no HTTP service, database, frontend, flaw detector or score is implemented. Dataset v1 manifests remain unchanged. Current gates and actual measurements are in [Phase 2 validation](phase2-validation.md); genuine source acquisition and missing human gates are in [pilot collection](pilot-collection.md).

## Native Windows MFA setup

The executed environment uses MFA 3.3.9, CPython 3.11.17, Kaldi 5.5.1172 **CPU**, kalpy 0.10.5, OpenFst 1.8.4 and Pynini 2.1.7. TakeTwo itself remains CPython 3.11.9 with its existing locked dependencies. No CUDA/PyTorch or paid service was added. The existing transitive threadpoolctl 3.7.0 is now explicitly pinned and used to enforce one BLAS thread during extraction, after a real replay exposed thread-dependent rounding. This installation was actually exercised on Windows; documentation alone is not the compatibility evidence.

The [official MFA installation guide](https://montreal-forced-aligner.readthedocs.io/en/stable/installation.html) recommends Conda/Miniforge. This run used portable micromamba 2.9.0 from `https://micro.mamba.pm/api/micromamba/win-64/latest`, then a separate conda-forge environment with `python=3.11`, `montreal-forced-aligner=3.3.9`, `kaldi=*=cpu*`. The resulting exact win-64 package URLs/builds/MD5 digests are in [the environment lock](../environments/mfa-win-64.lock). The bootstrap download URL is mutable; record/review the manager version if repeating bootstrap. Do not install MFA into `.venv` with pip alone: native Kaldi/OpenFst/kalpy binaries and DLL search paths are required.

With micromamba available, use a separate user-writable prefix. These commands install the locked environment; downloads need network access. No shell activation is required by the adapter.

```powershell
$prefix = Join-Path $env:LOCALAPPDATA 'TakeTwo\mfa'
micromamba create -y -p $prefix -f .\environments\mfa-win-64.lock
$env:PATH = "$prefix;$prefix\Scripts;$prefix\Library\bin;" + $env:PATH
$env:MFA_ROOT_DIR = Join-Path $env:LOCALAPPDATA 'TakeTwo\mfa-state'
& "$prefix\Scripts\mfa.exe" version
& "$prefix\Scripts\mfa.exe" model download acoustic english_us_arpa --version v3.0.0
& "$prefix\Scripts\mfa.exe" model download dictionary english_us_arpa --version v3.0.0
uv run python scripts/configure_alignment.py --prefix $prefix --models "$env:MFA_ROOT_DIR\pretrained_models" --output .\local-data\alignment-config.json
uv run taketwo-analysis check --config .\local-data\alignment-config.json
```

MFA 3.3.9's tested `model download ... english_us_arpa` resolved release v3.0.0. If a newer upstream command or artifact differs, use the exact release URLs in [model lock](../environments/mfa-models.json); configuration creation refuses mismatched hashes. Do not weaken hashes to accommodate an unreviewed download. The lock includes the observed acoustic and pronunciation dictionary checksums. English US ARPA release v3.0.0 uses **CC BY 4.0** for both resources: [acoustic model card](https://mfa-models.readthedocs.io/en/latest/acoustic/English/English%20%28US%29%20ARPA%20acoustic%20model%20v3_0_0.html), [dictionary card](https://mfa-models.readthedocs.io/en/latest/dictionary/English/English%20%28US%29%20ARPA%20dictionary%20v3_0_0.html). Attribute Montreal Forced Aligner model authors Michael McAuliffe and Morgan Sonderegger; preserve dictionary/source acknowledgments (including Gorman, Howell and Wagner, 2011) and the linked license when distributing resources. MFA software is MIT; Kaldi/OpenFst/Pynini use Apache-2.0. The complete binary environment has additional notices; this is not a bundled-distribution license audit.

The acoustic archive's `meta.json` records training date `2024-02-10`, GMM-HMM architecture and internal training-tool version `3.0.0a2.dev0+g940e907.d20230824`; that internal version is distinct from the downloaded **model release v3.0.0** and installed MFA **3.3.9**. Its training material is LibriSpeech read speech; historical public-address/noise/accent behavior is an evaluation risk. The downloaded acoustic archive is about 91.9 MB and dictionary 7.2 MB; extracted environment disk use and measured working sets are reported separately. No alternative backend is substituted because native MFA executes successfully here.

## CLI and states

```powershell
uv sync --locked
$workspace = '.\local-data\pilot-v2'
$recording = 'r-478a9405c1b10a75fda31972' # Actual local pilot ID; use your import result elsewhere
$aligned = uv run taketwo-analysis align $workspace --recording $recording --config .\local-data\alignment-config.json | ConvertFrom-Json
# Check $LASTEXITCODE before using a result. Failed attempts still have diagnostic artifacts.
$features = uv run taketwo-analysis extract $workspace --recording $recording --alignment $aligned.artifact | ConvertFrom-Json
uv run taketwo-analysis inspect $workspace --artifact $features.artifact
uv run taketwo-analysis validate $workspace --artifact $aligned.artifact
uv run taketwo-analysis validate $workspace --artifact $features.artifact --reproduce --alignment $aligned.artifact
uv run taketwo-analysis export $workspace --artifact $features.artifact --output .\local-data\features-export.json
```

`extract` also works without `--alignment`. Optional feature configuration is JSON matching `FeatureConfig`. Initial feature limit is **30 seconds**, separate from Phase 1's unchanged 600-second ingest limit; shorter excerpts bound pYIN/JSON memory. There is one job per command, one lock per workspace, one MFA worker and single-thread native numerical pools in subprocesses. Run heavy commands serially across workspaces. No queue or speculative concurrency framework is introduced.

Exit 0: prerequisite check passed, extraction completed or artifact checks passed. `align` returns 0 only for structurally complete automatic alignment. Exit 1: missing/mismatched prerequisites, partial/failed/timeout/cancelled alignment; its JSON artifact preserves diagnostics. Exit 2: arguments, schema, input/hash/path/I/O errors. Ctrl+C returns 130 after process cleanup. Successful status never certifies transcript correctness, independently reviewed timing or perceptual quality.

The adapter preserves original text, Phase 1 NFKC/casefold/apostrophe tokens and original character offsets. Punctuation is not spoken. Dictionary preflight covers every normalized token; digits, isolated initials, common abbreviations and short uppercase acronyms require explicit spoken-form review. `replacements` is a versioned one-token map (`mr` -> `mister`); multiword expansions require a revised transcript with actual spoken words. Unknown words stop alignment rather than silently using `<unk>` or guessed G2P output. User-supplied pronunciations must use the model's phone set and receive a newly checksummed dictionary/configuration.

Each attempt uses an isolated temporary directory and local model paths, no automatic model downloads. The canonical float WAV is exported to PCM16 for MFA; its prepared byte hash is recorded. This introduces quantization and can saturate out-of-range samples; original quality flags and canonical samples remain available and must be reviewed. MFA runs `align ... --single_speaker --num_jobs 1 --no_use_mp --clean --output_format long_textgrid --temporary_directory ...`. Single-speaker mode disables speaker adaptation. The version subprocess is bounded by min(configured timeout, 30 s); alignment itself uses configured timeout (default 120 s, local setup chooses 180 s). Logs are capped during polling and the retained tail is 64 KiB. Windows `taskkill /T /F` terminates the process tree on timeout/cancellation, followed by parent kill/wait; temporary files are removed. No arbitrary shell string interpolation is used.

Words carry canonical token indices; phones have native timestamps and null token indices. Blank/silence labels are omitted from interval lists; real gaps remain visible. Output intervals must be finite, positive-width, chronological, nonoverlapping within their tier and in recording bounds. Missing words yield `partial`; unexpected words/order or malformed intervals yield `failed` with no usable intervals. No proportional-duration fallback exists. A complete alignment against wrong words can still be wrong: inspect against audio and independent labels before scoring. `timing_uncertainty_s=null` means unmeasured; automatic alignments never assert independent review.

## Measurements and normalization

All coordinates refer to the unchanged mono 16 kHz canonical recording. Full-scale samples are dimensionless; dBFS is not sound pressure. No trimming, denoising or automatic gain correction is performed. Every series stores unit, integer start samples, window/hop and center times `(start + length/2)/16000`. Incomplete terminal windows are omitted, and covered-until times are explicit. Waveform envelopes cover every sample in 160-sample bins with half-open sample bounds and actual min/max.

| Evidence | Fixed acoustic-v1 definition |
| --- | --- |
| RMS and energy | 400-sample unweighted RMS, hop 160; `20 log10(max(RMS,1e-6))` dBFS |
| STFT/spectrum | Periodic Hann, 400 samples, 512-point real FFT; `P=abs(FFT(w*x))Â²/sum(wÂ²)`, 257 bins `k*16000/512`. Store power spectra, not phase. Total one-sided power doubles interior bins, sums and divides by 512; centroid is power-weighted Hz, zero for zero power |
| MFCC | 40 Slaney-normalized mel filters, 0-8000 Hz, HTK false, float64; natural log of mel power floored at `1e-10`; orthonormal DCT-II, first 13 coefficients including c0. Rows are frame-major, unit log-power cepstral coefficient |
| Pitch/voicing | CPU librosa pYIN, 1024 samples, hop 160, center false, 60-500 Hz initially; accept voiced finite F0 with model probability >=0.8. Raw valid Hz, probability, binary mask, relative semitones and union-of-observed-support voiced/unvoiced regions are retained. Their centers differ from energy frames |
| Energy activity | Upper quartile of audible frame energy seeds a median activity baseline; frames >=baseline-25 dB and RMS>1e-6 are candidates, then median is recomputed once. This energy heuristic can include noise/music and omit quiet speech; it is not a trained speech detector |
| Low-energy regions | Union of complete observed frame supports below the activity gate. Leading/trailing quiet spans remain evidence; incomplete tail has no invented silence decision. Overlapping supports may make active/quiet or voiced/unvoiced unions overlap near transitions; no exact acoustic onset is implied |
| Pauses | Only consecutive aligned-word gaps >=150 ms with at least one complete energy frame inside, all those frames below the activity gate. Available only with successful alignment and verified transcript; no alignment -> no inter-word pauses |
| Rate | `60*N/(last_end-first_start)` words/min including internal gaps; articulation rate subtracts corroborated internal pause durations. Require complete alignment plus the manifest's independently verified transcript assertion. Automatic timing remains unreviewed and can still be wrong |
| Quality | Whole-signal mean/RMS/peak, fraction abs(sample)>=0.999, near silence RMS<1e-3, clipping fraction>0.001 or peak>1, short-window coverage, unavailable pitch, range-edge and >7-semitone adjacent pitch-jump warnings |

Relative energy is `E - median(candidate_active_E)` in dB. Relative pitch is `12*log2(F0/median(valid_F0))` in semitones. Store raw baselines and contours alongside normalized values. Q90-Q10 excursion uses linear quantile interpolation; energy uses active frames and pitch valid voiced frames. No division by each recording's variance, which would hide monotony. Global gain/register invariance is verified on fixtures, not asserted for arbitrary microphones/speakers. The absolute energy floor breaks gain invariance near silence; pitch range/confidence gates can change coverage. Configurable bounds may exclude some voices. Missing pitch/baselines/rates are null with diagnostic context; never zero or a perfect score. Silence and extremely short finite inputs still yield honest statistics and empty/unavailable feature windows. Corrupt/nonfinite samples fail; clipping preserves raw measurements and flags quality. MFCC/centroid do not certify articulation or vocal clarity.

## Artifacts and reproducibility

Typed Pydantic contracts are in `src/taketwo/analysis/contracts.py`; [analysis JSON Schema v1](analysis-schema-v1.json) is checked against runtime schemas. Canonical JSON artifacts live at `derived/v1/<recording-id>/<kind>-<payload-sha256>.json`, with an envelope checksum. No manifest migration or audio overwrite occurs. New files use exclusive creation and fsync; a failed write removes its partial file. Identical content reuses an existing artifact only after byte equality. Local paths retain Phase 1 traversal/reparse safeguards. Derived JSON is bounded to 32 MiB; shorter excerpts are recovery for large artifacts.

Provenance binds dataset/recording ID, canonical file/sample hashes, canonical transcript hash, original text hash, transcript review assertion, processing versions and analysis source-code digest. Alignment adds model/dictionary/config, executable version, prepared PCM hash, TextGrid hash, intervals and diagnostics/log tail. No wall-clock duration is placed in deterministic feature content. `validate` checks structure, units, frame shapes/time mapping, bounds, hashes and current input/code/environment identity. `--reproduce` recomputes features, requiring the original alignment when used. Changed implementation/environment is explicit drift; create new artifacts rather than blessing stale output. Export returns the real typed result without audio, and refuses overwrite.

JSON stores full-precision finite measurements and null masks. Same-environment repeats must match exactly in this phase; cross-platform tolerance/decision behavior remains unmeasured. Alignment log paths are per-attempt and may change payload hashes even when intervals agree. Backend dither/numerics may also change boundaries; repeat runs compare intervals separately and never claim identical alignment merely from a feature test.

Use `scripts/benchmark_analysis.py --output <new.json> -- <analysis arguments>` through uv for actual elapsed time and Windows sampled process-tree working set. Memory is sampled every 100 ms; it is a lower bound on true peak, may miss very short children and counts shared pages across processes. Timing includes CLI import, validation, engine and artifact serialization. Keep failed measurements. A full resource-profile or another computer's performance is not inferred from these measurements.
