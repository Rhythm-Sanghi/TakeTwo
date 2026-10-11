# Phase 1B pilot acquisition and human recording procedure

TakeTwo — Speech analysis workspace. Acquisition reviewed 2026-10-11. This is an engineering pilot, **not a completed competition corpus**. No human mirror, consent or independent review exists. No recordings are committed or published.

## Genuine sources and rights evidence

| Item | Rights and acquisition | Actual local status |
| --- | --- | --- |
| JFKWHA-001: Swearing-in Ceremony and Inaugural Address, 20 January 1961 | [JFK Library item](https://www.jfklibrary.org/asset-viewer/archives/jfkwha-001) explicitly states Public Domain and identifies the White House Army Signal Agency as archival creator. [Commons file](https://commons.wikimedia.org/wiki/File:JFK_inaugural_address.ogg) identifies the library source, PD-USGov and Public Domain Mark, and offers the original download | Downloaded the Commons Ogg; decoded a 24 s opening with soundfile 0.13.1, PCM16, 44.1 kHz; imported through the existing CLI. A shorter 17.3 s salutation candidate excludes the following passage, using automatic alignment as a draft cut guide |
| JFKWHA-190-002: Commencement Address at American University, 10 June 1963 | [JFK Library item](https://www.jfklibrary.org/asset-viewer/archives/jfkwha-190-002) explicitly states Public Domain, identifies the White House Communications Agency and provides an MP3 download | Downloaded genuine master; exploratory 35/28 s WAV decodes exist locally. No verified excerpt transcript or import is claimed |

These item-specific statements support local acquisition, excerpting and adaptation of the official recordings. They do not clear unrelated archive items, endorsement or personality rights. Attribution: John F. Kennedy; White House Audio Collection; John F. Kennedy Presidential Library and Museum; Commons copy for the inaugural master. Recheck rights and applicable release jurisdiction before a public dataset release. The library's shell page request returned a JavaScript challenge; the item rights statements were inspected through the web reader. Download permission was verified before acquisition. No bypass of that challenge was attempted.

Master download locations:

- Inaugural: `https://upload.wikimedia.org/wikipedia/commons/d/d5/JFK_inaugural_address.ogg`; SHA-256 `a257580da6eda796ed1c703e545865005753f7cb20cc042e0db3c44de82274fc`.
- American University: `https://static.jfklibrary.org/0y71h7t40eul01xc4g8yx8438jpj1gg3.mp3`; SHA-256 `546739606ee424590fbe757474084d18fd3d1f99b1e6f7ca4363ecb412ad38da`.

Keep masters in ignored `local-data/acquisition/`; preserve their bytes and acquisition metadata. External format conversion is acquisition preparation, not added MP3/Ogg ingestion support. The first inaugural decode used soundfile; the American University exploratory decode used the available FFmpeg executable. No FFmpeg dependency was added to TakeTwo. Excerpt offsets are relative to the downloaded master; the Commons edit's offset within the longer library ceremony is unknown. Never label that archival offset as verified.

Both sources share JFK's voice: they form **one connected speaker group**, unsuitable for independent train/test splits. A second speaker and meaningful substantive passages are still needed. The salutation is useful for integration testing, not evidence of an effective rhetorical baseline or the required delivery spectrum.

## Draft transcript and mirror script

The [published inaugural transcript](https://commons.wikimedia.org/wiki/File:JFK_inaugural_address.ogg#Transcript) supplies these actual source words. They remain an **archive-based draft** until two humans check the excerpt by listening. Alignment coverage cannot verify the transcript. `Mr.` maps explicitly to spoken `mister` in alignment configuration; original text/offsets are preserved.

> Vice President Johnson, Mr. Speaker, Mr. Chief Justice, President Eisenhower, Vice President Nixon, President Truman, Reverend Clergy, fellow citizens:

Before recording mirrors, two reviewers independently check every word, repetition and excerpt edge. Correct the draft and record real reviewer IDs/date only after review. The initial 24 s clip may contain subsequent speech outside this draft; keep it as an exploratory run. Use the shorter candidate only after listening QA confirms it contains exactly these words. For a substantive passage, select and verify its full spoken text separately.

1. Recruit consenting adults. Obtain explicit recording, annotation, adaptation and public-release permission; retain private consent evidence outside Git. Assign pseudonymous speaker IDs. Never create a fictional consent marker.
2. Use a quiet room, fixed microphone/distance/gain, mono PCM WAV at 16/44.1/48 kHz or FLAC. Avoid AGC, denoising and effects where controllable; document unavoidable device processing. Leave short natural leading/trailing room tone; do not clip.
3. Read the verified script exactly, including repetitions if present. Record one comfortable faithful delivery and separate intended mild/moderate/severe changes to pacing, pauses or emphasis. Describe the intention, not a confirmed flaw. Do not impersonate JFK or synthesize a human mirror.
4. Listen for omitted/added words and clipping; re-record rather than hide mismatches. Record microphone/settings/date and actual consent evidence in `ImportSpec`. Use `origin=self_recorded`, the same family/work, distinct source/speaker IDs and canonical words.
5. Import with `taketwo-dataset import-flawed`; do not assign detected intervals. Two independent labelers listen without engine/recipe windows, mark native-time flaw/acceptable/quality intervals and uncertainty, then adjudicate disagreements. Import their actual records with `annotate`.
6. Obtain split-disjoint speakers before freezing groups. Run draft and publication validation separately; missing mirrors/reviews/coverage must continue to fail publication.

```powershell
uv run taketwo-dataset import-flawed .\local-data\pilot-v2 --reference $referenceId --audio .\mirror.wav --metadata .\mirror-metadata.json --category pacing --severity 2
uv run taketwo-dataset annotate .\local-data\pilot-v2 --annotations .\independent-labels.json
uv run taketwo-dataset validate .\local-data\pilot-v2 --reproduce
uv run taketwo-dataset validate .\local-data\pilot-v2 --publication --reproduce
```

The paths/IDs in this example require genuine collected files. No microphone capture, human performance or annotation review was performed in this development run. The Phase 1B pilot gate remains open.
