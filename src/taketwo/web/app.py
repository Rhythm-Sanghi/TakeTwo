"""Loopback API: typed adapters, bounded uploads, managed media and real artifacts."""

import csv
import io
import json
import os
import re
import tempfile
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import Annotated

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException

from taketwo.analysis.alignment import prerequisites
from taketwo.analysis.contracts import AlignmentConfig, AlignmentResult, Diagnostic, FeatureResult
from taketwo.analysis.limits import maximum_analysis_duration_s
from taketwo.analysis.storage import read_artifact as read_analysis
from taketwo.analysis.storage import recording_input, validate_identity
from taketwo.comparison.contracts import Evaluation, Policy, Report, Review, Span
from taketwo.comparison.engine import acoustic_gate
from taketwo.comparison.reviews import reviewed_timing
from taketwo.comparison.storage import bound_dataset, implementation_hash, read_artifact
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import (
    Pair,
    Recording,
    Transcript,
    canonical_json,
    content_hash,
)
from taketwo.dataset.storage import load, managed_path, read_json, safe_path, unique_json
from taketwo.dataset.workspace import find_recording, import_recording, initialize, summary

from .contracts import (
    AnalysisRequest,
    CorrectionRequest,
    DatasetSummary,
    ExcerptRequest,
    FeatureWindow,
    Health,
    ImportRequest,
    Job,
    LocalImportRequest,
    Overlay,
    ReviewImportRequest,
    Waveform,
    WorkspaceRevision,
)
from .imports import corrected_pair, excerpt, local_spec, upgrade_drafts
from .jobs import Jobs
from .processes import lease
from .review_api import handoff_denied, install_reviews

MAX_UPLOAD = 100 * 1024 * 1024
ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:8765",
    "http://localhost:8765",
]


def error(status, code, message, recovery="Review the input and retry."):
    return JSONResponse(
        {"error": {"code": code, "message": message, "recovery": recovery}}, status_code=status
    )


@lru_cache(maxsize=8)
def validated_analysis(path: str, modified_ns: int, size: int):
    return read_analysis(Path(path))


def window(series, start, end, maximum):
    indices = [i for i, t in enumerate(series.times_s) if start <= t <= end]
    if len(indices) <= maximum:
        return (
            [series.times_s[i] for i in indices],
            [series.values[i] for i in indices],
            "native_frames",
        )
    selected = []
    for group in np.array_split(indices, max(1, maximum // 3)):
        missing = [int(i) for i in group if series.values[int(i)] is None]
        if missing:
            selected.append(missing[0])  # Conservative gap: never draw through unobserved pitch.
        else:
            selected.extend(
                sorted(
                    {
                        int(min(group, key=lambda i: series.values[int(i)])),
                        int(max(group, key=lambda i: series.values[int(i)])),
                    }
                )
            )
    return (
        [series.times_s[i] for i in selected],
        [series.values[i] for i in selected],
        "min_max_with_gap_markers",
    )


def create_app(
    root: Path | None = None,
    alignment_config: Path | None = None,
    *,
    timeout_s=600.0,
    frontend: Path | None = None,
):
    maximum_analysis_duration_s()  # Reject invalid deployment configuration before startup.
    root = safe_path(
        root
        or Path(
            os.environ.get(
                "TAKETWO_WORKSPACE",
                str(
                    Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "TakeTwo" / "workspace"
                ),
            )
        )
    )
    configured = os.environ.get("TAKETWO_ALIGNMENT_CONFIG")
    alignment_config = (
        safe_path(alignment_config or Path(configured)) if alignment_config or configured else None
    )
    if not root.exists():
        initialize(root, "local-v1")
    load(root)
    jobs = Jobs(root, alignment_config, timeout_s)

    @asynccontextmanager
    async def lifespan(app):
        # An exclusive lease prevents two HTTP services from supervising the same history.
        with lease(root, ".service.lock"):
            try:
                jobs.start()
                yield
            finally:
                jobs.close()

    app = FastAPI(
        title="TakeTwo", description="Speech analysis workspace", version="1.0.0", lifespan=lifespan
    )
    app.state.jobs, app.state.root = jobs, root
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Review-Operator"],
    )

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        if handoff_denied(app, request):
            return error(
                403,
                "review_handoff",
                "Independent reviewer handoff is active.",
                "Ask the local operator to end handoff before using analysis or peer evidence.",
            )
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            same_origin = f"{request.url.scheme}://{request.headers.get('host', '')}"
            if request.headers.get("origin") not in [None, same_origin, *ORIGINS]:
                return error(
                    403, "origin_rejected", "Mutation origin is not a configured local workspace."
                )
            length = request.headers.get("content-length")
            if length is None:
                return error(411, "length_required", "A bounded Content-Length is required.")
            if request.url.path.startswith("/api/v1/review-workspace") and (
                not length.isdigit() or len(length) > 12 or int(length) > 1024 * 1024
            ):
                return error(413, "review_limit", "Review request exceeds 1 MiB.")
            if not length.isdigit() or len(length) > 12 or int(length) > MAX_UPLOAD + 1024 * 1024:
                return error(
                    413,
                    "upload_limit",
                    "Request exceeds the 100 MiB audio plus 1 MiB metadata limit.",
                )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; media-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def request_invalid(request, exc):
        fields = ", ".join(".".join(map(str, e["loc"])) for e in exc.errors())
        return error(
            422,
            "request_validation",
            f"Invalid request fields: {fields}.",
            "Use the documented API schema; private input values are omitted.",
        )

    @app.exception_handler(ValidationError)
    async def metadata_invalid(request, exc):
        fields = ", ".join(".".join(map(str, e["loc"])) for e in exc.errors())
        return error(422, "metadata_validation", f"Invalid metadata fields: {fields}.")

    @app.exception_handler(DatasetError)
    async def dataset_error(request, exc):
        return error(
            409 if exc.code in {"duplicate_audio", "workspace_busy", "split_frozen"} else 422,
            exc.code,
            str(exc),
            exc.recovery,
        )

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return error(404, "not_found", "The requested identifier does not exist.")

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return error(422, "invalid_input", str(exc))

    @app.exception_handler(OSError)
    async def unavailable_storage(request, exc):
        return error(
            503,
            "storage_unavailable",
            "Managed local storage is unavailable.",
            "Check disk access and restore missing managed artifacts before retrying.",
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        return error(exc.status_code, "request_state", str(exc.detail))

    def recording(rid):
        try:
            return find_recording(load(root), rid)
        except DatasetError as exc:
            if exc.code == "recording_missing":
                raise KeyError(rid) from exc
            raise

    def analysis(job_id, rid, kind):
        job = jobs.get(job_id)
        relative = job.artifacts.get(rid, {}).get(kind)
        if not relative:
            raise HTTPException(409, "Requested evidence is not available for this job member.")
        path = managed_path(root, relative)
        stat = path.stat()
        result = validated_analysis(str(path), stat.st_mtime_ns, stat.st_size)
        validate_identity(root, result)
        return result

    def report(job_id):
        job = jobs.get(job_id)
        if not job.report_path:
            raise HTTPException(409, "Analysis has no completed report.")
        result = read_artifact(managed_path(root, job.report_path))
        if not isinstance(result, Report):
            raise ValueError("Stored artifact is not a comparison report.")
        if result.implementation_sha256 != implementation_hash():
            raise HTTPException(
                409, "Report inputs or comparison version changed; start a new analysis."
            )
        try:
            bound_dataset(root, load(root), result)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        for member in result.inputs:
            features = analysis(job_id, member.provenance.recording_id, "features")
            if content_hash(features.model_dump(mode="json")) != member.features.sha256:
                raise ValueError("Report feature hash differs.")
            if member.alignment:
                aligned = analysis(job_id, member.provenance.recording_id, "alignment")
                if content_hash(aligned.model_dump(mode="json")) != member.alignment.sha256:
                    raise HTTPException(409, "Alignment evidence changed; start a new analysis.")
            current_reviews = []
            for path in managed_path(root, "derived/comparison-v1").glob("review-*.json"):
                review = read_artifact(path)
                if (
                    isinstance(review, Review)
                    and review.scope != "flaws"
                    and (review.provenance.recording_id == member.provenance.recording_id)
                ):
                    current_reviews.append(content_hash(review.model_dump(mode="json")))
            if sorted(current_reviews) != sorted(ref.sha256 for ref in member.reviews):
                raise HTTPException(
                    409, "Transcript/timing review evidence changed; start a new analysis."
                )
        return result

    @app.get("/api/v1/health", response_model=Health)
    def health():
        issues = []
        if alignment_config:
            try:
                issues = prerequisites(
                    AlignmentConfig.model_validate_json(canonical_json(read_json(alignment_config)))
                )
            except (ValueError, OSError, DatasetError):
                issues = [
                    Diagnostic(
                        code="alignment_config_invalid",
                        message="Local alignment configuration is invalid or unavailable.",
                        recovery="Set TAKETWO_ALIGNMENT_CONFIG to the reviewed configuration.",
                    )
                ]
        else:
            issues = [
                Diagnostic(
                    code="alignment_not_configured",
                    message="Automatic alignment is not configured.",
                    recovery="Set TAKETWO_ALIGNMENT_CONFIG and restart; "
                    "acoustic inspection remains available.",
                )
            ]
        return Health(
            ready=jobs.thread.is_alive(),
            alignment_configured=bool(alignment_config) and not issues,
            alignment_diagnostics=issues,
        )

    @app.get("/api/v1/recordings", response_model=list[Recording])
    def recordings():
        return load(root).recordings

    @app.get("/api/v1/recordings/{rid}", response_model=Recording)
    def detail(rid: str):
        return recording(rid)

    @app.get("/api/v1/recordings/{rid}/transcript", response_model=Transcript)
    def transcript(rid: str):
        return recording(rid).transcript

    @app.post("/api/v1/recordings", response_model=Recording, status_code=201)
    async def upload(
        audio: Annotated[UploadFile, File()], metadata: Annotated[str, Form(max_length=1000000)]
    ):
        if len(metadata.encode("utf-8")) > 1024 * 1024:
            raise HTTPException(413, "Import metadata exceeds 1 MiB.")
        payload = json.loads(metadata, object_pairs_hook=unique_json)
        if not isinstance(payload, dict):
            raise ValueError("Import metadata must be a JSON object.")
        spec = ImportRequest.model_validate_json(metadata) if "metadata" in payload else None
        if any(j.state == "running" for j in jobs.list()):
            raise HTTPException(409, "Analysis owns the dataset. Wait or cancel before importing.")
        filename = (audio.filename or "recording.wav").replace("\\", "/").split("/")[-1]
        filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)[:100]
        if (
            not filename
            or filename.startswith(".")
            or filename.rstrip(". ") != filename
            or Path(filename).is_reserved()
        ):
            raise ValueError("Filename needs an ordinary WAV or FLAC basename.")
        allowed = {
            "audio/wav",
            "audio/x-wav",
            "audio/wave",
            "audio/vnd.wave",
            "audio/flac",
            "audio/x-flac",
            "application/octet-stream",
        }
        if audio.content_type not in allowed:
            raise HTTPException(
                415,
                "Supported audio MIME types are WAV, FLAC or binary; "
                "actual contents are decoded and validated.",
            )
        if spec is None:
            local = LocalImportRequest.model_validate_json(metadata)
            spec = ImportRequest(
                metadata=local_spec(root, local, filename),
                reference_id=local.reference_id,
                category=local.category,
                severity=local.severity,
            )
        if spec.category == "unspecified" and spec.severity is not None:
            raise ValueError("Unspecified acquisition intent has no severity.")
        if spec.category != "unspecified" and (spec.category == "acceptable") != (
            spec.severity == 0
        ):
            raise ValueError("Only acceptable intended categories use severity zero.")
        if spec.reference_id and recording(spec.reference_id).role != "reference":
            raise ValueError("Participant import requires a reference recording.")
        try:
            with tempfile.TemporaryDirectory(prefix="taketwo-upload-") as directory:
                path = Path(directory) / filename
                size = 0
                with path.open("xb") as stream:
                    while chunk := await audio.read(1024 * 1024):
                        size += len(chunk)
                        if size > MAX_UPLOAD:
                            raise HTTPException(413, "Audio exceeds 100 MiB.")
                        stream.write(chunk)
                return await run_in_threadpool(
                    import_recording,
                    root,
                    path,
                    spec.metadata,
                    reference_id=spec.reference_id,
                    category=spec.category,
                    severity=spec.severity,
                )
        finally:
            await audio.close()

    @app.get("/api/v1/pairs", response_model=list[Pair])
    def pairs():
        return load(root).pairs

    @app.post("/api/v1/recordings/{rid}/excerpt", response_model=Recording, status_code=201)
    def save_excerpt(rid: str, request: ExcerptRequest):
        return excerpt(root, rid, request)

    @app.post(
        "/api/v1/pairs/{pair_id}/correction", response_model=WorkspaceRevision, status_code=201
    )
    def correct_pair(pair_id: str, request: CorrectionRequest):
        return corrected_pair(root, pair_id, request.reference_id)

    @app.post("/api/v1/reviews/import")
    def import_review(request: ReviewImportRequest):
        from argparse import Namespace

        from taketwo.comparison.cli import run

        job = jobs.get(request.job_id)
        rid = request.review.provenance.recording_id
        if rid not in job.artifacts:
            raise ValueError("Review must bind a member of the selected analysis.")
        relative = job.artifacts[rid].get("alignment")
        with tempfile.TemporaryDirectory(prefix="taketwo-review-") as directory:
            path = Path(directory) / "review.json"
            path.write_text(request.review.model_dump_json(), encoding="utf-8")
            result, _ = run(
                Namespace(
                    command="import-review",
                    workspace=root,
                    review=path,
                    alignment=managed_path(root, relative) if relative else None,
                )
            )
        return {"decision": result["decision"], "notice": result["notice"]}

    @app.get("/api/v1/recordings/{rid}/audio")
    def audio(rid: str):
        item, _, _ = recording_input(root, rid)
        return FileResponse(
            managed_path(root, item.normalized_path),
            media_type="audio/wav",
            headers={"Content-Disposition": "inline"},
        )

    @app.get("/api/v1/recordings/{rid}/waveform", response_model=Waveform)
    def waveform(
        rid: str,
        start_s: float = Query(0, ge=0, le=600),
        end_s: float = Query(600, gt=0, le=600),
        bins: int = Query(1000, ge=1, le=5000),
    ):
        _, samples, _ = recording_input(root, rid)
        left, right = int(start_s * 16000), min(len(samples), int(end_s * 16000))
        if left >= right:
            raise ValueError("Waveform window must overlap the recording.")
        edges = np.linspace(left, right, min(bins, right - left) + 1, dtype=int)
        points = [
            (int(a), int(b), float(np.min(samples[a:b])), float(np.max(samples[a:b])))
            for a, b in zip(edges[:-1], edges[1:], strict=True)
        ]
        return Waveform(start_s=left / 16000, end_s=right / 16000, bins=points)

    @app.get("/api/v1/analyses", response_model=list[Job])
    def history():
        return jobs.list()

    @app.post("/api/v1/analyses", response_model=Job, status_code=202)
    def submit(request: AnalysisRequest):
        if not jobs.thread.is_alive():
            raise HTTPException(503, "CPU supervisor is unavailable; restart the local service.")
        item = recording(request.reference_id)
        if item.role != "reference":
            raise ValueError("Analysis must begin with a reference recording.")
        if request.pair_id and not any(
            p.id == request.pair_id and p.reference_id == item.id for p in load(root).pairs
        ):
            raise HTTPException(409, "Pair does not belong to the selected reference.")
        members = [item]
        if request.pair_id:
            pair = next(p for p in load(root).pairs if p.id == request.pair_id)
            members.append(recording(pair.participant_id))
        if any(r.normalized_info.duration_s > maximum_analysis_duration_s() for r in members):
            raise ValueError(
                f"Analysis supports {maximum_analysis_duration_s()}-second excerpts; "
                "originals up to 600 seconds can be stored."
            )
        try:
            return jobs.submit(request)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/api/v1/analyses/{job_id}", response_model=Job)
    def status(job_id: str):
        return jobs.get(job_id)

    @app.post("/api/v1/analyses/{job_id}/cancel", response_model=Job, status_code=202)
    def cancel(job_id: str):
        try:
            return jobs.cancel(job_id)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/api/v1/analyses/{job_id}/report", response_model=Report)
    def get_report(job_id: str):
        return report(job_id)

    @app.get("/api/v1/analyses/{job_id}/alignments/{rid}", response_model=AlignmentResult)
    def alignment(job_id: str, rid: str):
        return analysis(job_id, rid, "alignment")

    @app.get("/api/v1/analyses/{job_id}/features/{rid}", response_model=FeatureWindow)
    def features(
        job_id: str,
        rid: str,
        name: str = "rms",
        start_s: float = Query(0, ge=0),
        end_s: float = Query(600, gt=0, le=600),
        max_points: int = Query(1200, ge=3, le=5000),
    ):
        result = analysis(job_id, rid, "features")
        if not isinstance(result, FeatureResult) or name not in result.series or start_s >= end_s:
            raise ValueError("Choose an available acoustic series and a positive time window.")
        series = result.series[name]
        times, values, aggregation = window(series, start_s, end_s, max_points)
        return FeatureWindow(
            name=name,
            unit=series.unit,
            frame_length=series.frame_length,
            hop_length=series.hop_length,
            aggregation=aggregation,
            times_s=times,
            values=values,
            quality=result.quality,
            pauses=result.pauses,
            speaking_rate_wpm=result.speaking_rate_wpm,
            rate_unavailable_reason=result.rate_unavailable_reason,
        )

    @app.get("/api/v1/rubrics/delivery-v0", response_model=Policy)
    def rubric():
        return Policy()

    @app.get("/api/v1/analyses/{job_id}/overlay", response_model=Overlay)
    def overlay(job_id: str, name: str = "relative_energy"):
        if name not in {"relative_energy", "relative_pitch"}:
            raise ValueError("Word overlay supports relative_energy or relative_pitch.")
        result = report(job_id)
        dimension = "energy_variation" if name == "relative_energy" else "pitch_dynamics"
        gate = result.feature_eligibility[dimension]
        unit = "dB" if name == "relative_energy" else "semitones"
        output = Overlay(
            name=name,
            unit=unit,
            unavailable_reason=None,
            tokens=[],
            reference_words=[],
            participant_words=[],
            reference_values=[],
            participant_values=[],
        )
        if len(result.inputs) != 2 or gate.state != "ELIGIBLE":
            output.unavailable_reason = "Reviewed token correspondence unavailable. " + " ".join(
                dict.fromkeys(reason.message for reason in gate.reasons)
            )
            return output
        values, words = [], []
        for member in result.inputs:
            reviews = [read_artifact(managed_path(root, ref.path)) for ref in member.reviews]
            timing, _, issue = reviewed_timing(reviews)
            if issue:
                raise HTTPException(409, "Timing reviews changed; run comparison again.")
            features = analysis(job_id, member.provenance.recording_id, "features")
            measured = []
            for word in timing:
                samples, local_gate, _ = acoustic_gate(
                    features, Span(start_s=word.start_s, end_s=word.end_s), name, gate
                )
                measured.append(
                    float(np.median(samples)) if local_gate.state == "ELIGIBLE" else None
                )
            words.append(timing)
            values.append(measured)
        output.tokens = recording(result.inputs[0].provenance.recording_id).tokens
        output.reference_words, output.participant_words = words
        output.reference_values, output.participant_values = values
        return output

    @app.get("/api/v1/evaluations", response_model=list[Evaluation])
    def evaluations():
        results = []
        for path in managed_path(root, "derived/comparison-v1").glob("evaluation-*.json"):
            result = read_artifact(path)
            if isinstance(result, Evaluation):
                results.append(result)
        return results

    @app.get("/api/v1/reviews", response_model=list[Review])
    def reviews():
        return [
            read_artifact(p)
            for p in managed_path(root, "derived/comparison-v1").glob("review-*.json")
        ]

    @app.get("/api/v1/dataset", response_model=DatasetSummary)
    def dataset_summary():
        return DatasetSummary.model_validate_json(canonical_json(summary(load(root))))

    @app.post("/api/v1/dataset/upgrade", response_model=DatasetSummary)
    def enable_drafts():
        return summary(upgrade_drafts(root))

    @app.get("/api/v1/analyses/{job_id}/export")
    def export(job_id: str, format: str = "json"):
        result = report(job_id)
        if format == "json":
            body, media, extension = (
                canonical_json(result.model_dump(mode="json")),
                "application/json",
                "json",
            )
        elif format == "csv":
            stream = io.StringIO(newline="")
            writer = csv.writer(stream)
            writer.writerow(
                [
                    "region_id",
                    "category",
                    "participant_start_s",
                    "participant_end_s",
                    "participant_anchor_s",
                    "reference_start_s",
                    "reference_end_s",
                    "reference_anchor_s",
                    "severity",
                    "policy_version",
                    "observation_ids",
                ]
            )
            for region in result.regions:
                writer.writerow(
                    [
                        region.id,
                        region.category,
                        region.participant_interval.start_s
                        if region.participant_interval
                        else None,
                        region.participant_interval.end_s if region.participant_interval else None,
                        region.participant_anchor_s,
                        region.reference_interval.start_s if region.reference_interval else None,
                        region.reference_interval.end_s if region.reference_interval else None,
                        region.reference_anchor_s,
                        region.severity,
                        result.policy.version,
                        "|".join(region.observation_ids),
                    ]
                )
            body, media, extension = stream.getvalue(), "text/csv", "csv"
        else:
            raise ValueError("Export format must be json or csv.")
        return Response(
            body,
            media_type=media,
            headers={"Content-Disposition": f'attachment; filename="taketwo-{job_id}.{extension}"'},
        )

    install_reviews(app, root, jobs, audio, waveform)

    if frontend and frontend.is_dir():
        app.mount("/", StaticFiles(directory=frontend, html=True), name="workspace")
    return app
