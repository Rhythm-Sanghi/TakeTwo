import io

import numpy as np
import pytest
import soundfile as sf

from taketwo.dataset.audio import decode, normalize, quality, read_audio, sample_hash
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.workspace import import_recording, initialize


@pytest.mark.parametrize(
    "container,subtype", [("WAV", "FLOAT"), ("WAV", "PCM_16"), ("FLAC", "PCM_24")]
)
def test_supported_decoding(signal, container, subtype):
    buffer = io.BytesIO()
    sf.write(buffer, signal, 16000, format=container, subtype=subtype)
    decoded, info = decode(buffer.getvalue())
    assert info.frames == len(signal) and info.format == container
    np.testing.assert_allclose(decoded[:, 0], signal, atol=1 / 32768)


@pytest.mark.parametrize("payload", [b"", b"not audio", b"RIFF\x00\x00\x00\x00WAVE"])
def test_corrupt_audio(payload):
    with pytest.raises(DatasetError, match="corrupt|unreadable"):
        decode(payload)


@pytest.mark.parametrize(
    "rate,channels,frames", [(4000, 1, 100), (16000, 3, 100), (16000, 1, 0), (8000, 1, 8000 * 601)]
)
def test_unsupported_limits(rate, channels, frames):
    buffer = io.BytesIO()
    sf.write(buffer, np.zeros((frames, channels), np.float32), rate, format="WAV", subtype="FLOAT")
    with pytest.raises(DatasetError):
        decode(buffer.getvalue())


def test_nonfinite_samples():
    buffer = io.BytesIO()
    sf.write(
        buffer, np.array([0, np.nan, np.inf], np.float32), 16000, format="WAV", subtype="FLOAT"
    )
    with pytest.raises(DatasetError, match="NaN"):
        decode(buffer.getvalue())


def test_silence_rejected(tmp_path, spec):
    path = tmp_path / "silent.wav"
    sf.write(path, np.zeros(1600), 16000)
    root = tmp_path / "dataset"
    initialize(root, "v1")
    with pytest.raises(DatasetError, match="silent"):
        import_recording(root, path, spec)
    assert list((root / "originals").iterdir()) == []


def test_clipping_preserved_and_flagged(tmp_path, spec):
    path = tmp_path / "clipped.wav"
    sf.write(path, np.tile([-1.0, 1.0], 1000), 16000, subtype="FLOAT")
    before = path.read_bytes()
    root = tmp_path / "dataset"
    initialize(root, "v1")
    recording = import_recording(root, path, spec)
    assert recording.quality_flags == ["clipping"]
    assert (root / recording.original_path).read_bytes() == before == path.read_bytes()


def test_resampling_time_and_amplitude():
    rate = 48000
    x = 0.2 * np.sin(2 * np.pi * 220 * np.arange(rate) / rate)
    result = normalize(np.column_stack([x, x]).astype(np.float32), rate, None)
    assert len(result) == 16000
    assert abs(np.sqrt(np.mean(result**2)) - 0.2 / np.sqrt(2)) < 1e-4
    impulse = np.zeros((4800, 1), np.float32)
    impulse[2400] = 0.2
    assert np.argmax(normalize(impulse, rate, None)) == 800


def test_stereo_cancellation_requires_selection(signal):
    stereo = np.column_stack([signal, -signal])
    with pytest.raises(DatasetError, match="cancels"):
        normalize(stereo, 16000, None)
    np.testing.assert_array_equal(normalize(stereo, 16000, 0), signal)
    with pytest.raises(DatasetError, match="channel"):
        normalize(signal[:, None], 16000, 1)


def test_duplicate_detection_across_container(imported, audio_path, spec, signal, tmp_path):
    root, _ = imported
    with pytest.raises(DatasetError, match="already exists"):
        import_recording(root, audio_path, spec)
    path = tmp_path / "same-content.wav"
    sf.write(path, signal, 16000, subtype="FLOAT")
    with pytest.raises(DatasetError, match="already exists"):
        import_recording(root, path, spec)
    assert len(list((root / "originals").iterdir())) == 1


def test_missing_and_wrong_extension(tmp_path, audio_path):
    with pytest.raises(DatasetError, match="does not exist"):
        read_audio(tmp_path / "missing.wav")
    with pytest.raises(DatasetError, match="extension"):
        read_audio(tmp_path / "test.mp3")
    wrong = tmp_path / "wrong.flac"
    wrong.write_bytes(audio_path.read_bytes())
    with pytest.raises(DatasetError, match="Extension"):
        read_audio(wrong)


def test_quality_and_sample_hash(signal):
    _, info = decode(sf_buffer(signal))
    assert quality(info) == []
    assert sample_hash(signal) == sample_hash(signal.copy())


def sf_buffer(signal):
    buffer = io.BytesIO()
    sf.write(buffer, signal, 16000, format="WAV", subtype="FLOAT")
    return buffer.getvalue()


def test_duplicate_pcm_across_wav_flac(tmp_path, signal, spec):
    wav = tmp_path / "source.wav"
    flac = tmp_path / "duplicate.flac"
    sf.write(wav, signal, 16000, subtype="PCM_16")
    # Different encoders can quantize a floating input differently. Compare actual
    # identical PCM content, rather than assuming two lossy quantizations agree.
    pcm, _ = sf.read(wav, dtype="float32")
    sf.write(flac, pcm, 16000, subtype="PCM_16")
    np.testing.assert_array_equal(sf.read(flac, dtype="float32")[0], pcm)
    root = tmp_path / "different-containers"
    initialize(root, "v1")
    import_recording(root, wav, spec)
    with pytest.raises(DatasetError, match="already exists"):
        import_recording(root, flac, spec)


def test_corrupt_flac_rejected(signal):
    buffer = io.BytesIO()
    sf.write(buffer, signal, 16000, format="FLAC", subtype="PCM_16")
    with pytest.raises(DatasetError):
        decode(buffer.getvalue()[:100])
