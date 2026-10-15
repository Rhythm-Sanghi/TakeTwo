# Source acquisition and rights ledger

TakeTwo — Speech analysis workspace. Acquisition reviewed 2026-10-11. This is an engineering pilot, **not a completed competition corpus**. The acquisition record below predates the later five private practice takes; it supplies no independent human review or release consent. No recordings are committed or published.

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

### Imported draft candidate

The 17.3 s salutation candidate is `r-478a9405c1b10a75fda31972`, family
`jfk-inaugural-1961-opening`. Canonical WAV SHA-256 is
`a342f051ea3b4ae23a40d293264bdee3946be235cb73c77e7e582c65dc873bc8`.
The original master SHA above identifies the source; canonical-container bytes are a
different identity from decoded sample hashes. Retain both in actual manifests.
No verified script, consented spectrum or independent boundary labels are asserted.

Use the [recording/review protocol](review-protocol.md) for consent, microphone settings,
same-text recording, independent annotation, import/evaluation and blank forms. The
[dataset engineering guide](dataset-engineering.md) and [reproduction commands](reproducibility.md)
retain the actual `import-flawed`, `annotate` and draft/publication validation commands.
This ledger records acquired source evidence; it does not claim a complete corpus.

## Unacquired source lead

The [FDR Presidential Library audio index](https://www.fdrlibrary.org/utterancesfdr) was inspected as an acquisition lead. Its MP3 downloads and general reference-use notice do not by themselves clear a particular recording for adaptation/public dataset release. No asset was downloaded or marked cleared; obtain item-specific terms/permission and a supported archival WAV/FLAC or document a reviewed external conversion separately. No MP3 dependency was added.
