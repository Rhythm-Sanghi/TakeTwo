"""Duration admission boundaries use generated signals, never speech-quality evidence."""

import io
from unittest.mock import Mock

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from taketwo.analysis.contracts import FeatureConfig
from taketwo.analysis.features import extract
from taketwo.analysis.limits import maximum_analysis_duration_s
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import canonical_json
from taketwo.web.app import create_app


@pytest.mark.parametrize("value", ["0", "46", "1.5", "nan", "", "-1"])
def test_invalid_budget_fails_startup(tmp_path, monkeypatch, value):
    monkeypatch.setenv("TAKETWO_MAX_ANALYSIS_DURATION_S", value)
    with pytest.raises(ValueError, match="TAKETWO_MAX_ANALYSIS_DURATION_S"):
        create_app(tmp_path / "workspace")


def test_configured_budget_and_explicit_feature_config_cannot_bypass(imported, monkeypatch):
    monkeypatch.setenv("TAKETWO_MAX_ANALYSIS_DURATION_S", "1")
    assert maximum_analysis_duration_s() == FeatureConfig().maximum_duration_s == 1
    from taketwo.analysis.storage import recording_input

    _, samples, provenance = recording_input(imported[0], imported[1].id)
    with pytest.raises(DatasetError, match="at most 1 seconds"):
        extract(samples, provenance, FeatureConfig(maximum_duration_s=45))


@pytest.mark.parametrize("limit", [45, 12])
def test_excerpt_and_submission_sample_boundaries(tmp_path, monkeypatch, limit):
    monkeypatch.setenv("TAKETWO_MAX_ANALYSIS_DURATION_S", str(limit))
    # Imported originals can exceed the analysis budget. Retain native 16 kHz coordinates.
    stream = io.BytesIO()
    sf.write(
        stream,
        0.2 * np.sin(2 * np.pi * 220 * np.arange((limit + 1) * 16000) / 16000),
        16000,
        format="WAV",
        subtype="PCM_16",
    )
    with TestClient(create_app(tmp_path / "workspace")) as client:
        health = client.get("/api/v1/health").json()
        assert health["maximum_analysis_duration_s"] == limit
        assert health["maximum_upload_bytes"] == 100 * 1024 * 1024
        assert health["maximum_worker_commit_bytes"] == 4 * 1024**3
        assert health["worker_concurrency"] == 1
        response = client.post(
            "/api/v1/recordings",
            files={"audio": ("fixture.wav", stream.getvalue(), "audio/wav")},
            data={
                "metadata": canonical_json(
                    {
                        "recording_type": "controlled_reference",
                        "transcript": "Generated tone fixture only.",
                        "local_permission": True,
                    }
                )
            },
        )
        assert response.status_code == 201, response.text
        original = response.json()
        assert (
            client.post("/api/v1/analyses", json={"reference_id": original["id"]}).status_code
            == 422
        )
        # Inspect admission without starting costly DSP in this boundary-only test.
        submit = Mock(side_effect=ValueError("admitted to supervisor"))
        monkeypatch.setattr(client.app.state.jobs, "submit", submit)
        for delta, accepted in [(-1, True), (0, True), (1, False)]:
            end = (limit * 16000 + delta) / 16000
            response = client.post(
                f"/api/v1/recordings/{original['id']}/excerpt",
                json={
                    "start_s": 0,
                    "end_s": end,
                    "transcript": "Generated tone fixture excerpt.",
                },
            )
            assert response.status_code == (201 if accepted else 422), response.text
            if accepted:
                cut = response.json()
                assert cut["normalized_info"]["frames"] == limit * 16000 + delta
                assert cut["provenance"]["excerpt_offset_s"] == 0
                submit.reset_mock()
                client.post("/api/v1/analyses", json={"reference_id": cut["id"]})
                submit.assert_called_once()
        assert client.get(f"/api/v1/recordings/{original['id']}").json() == original


def test_worker_rechecks_actual_samples_before_processing(imported, tmp_path, monkeypatch):
    from taketwo.web.contracts import AnalysisRequest
    from taketwo.web.worker import run

    monkeypatch.setenv("TAKETWO_MAX_ANALYSIS_DURATION_S", "1")
    temporary = tmp_path / "worker"
    temporary.mkdir()
    with pytest.raises(ValueError, match="excerpts up to 1 seconds"):
        run(imported[0], temporary, AnalysisRequest(reference_id=imported[1].id, align=False), None)


def test_alignment_rejects_oversized_input_before_tool_launch(imported):
    from taketwo.analysis.alignment import align
    from taketwo.analysis.storage import recording_input

    item, _, provenance = recording_input(imported[0], imported[1].id)
    with pytest.raises(DatasetError, match="at most 45 seconds"):
        align(
            imported[0] / item.normalized_path,
            item.transcript.text,
            provenance,
            45 + 1 / 16000,
            None,
        )
