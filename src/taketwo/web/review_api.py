"""Recording-scoped review routes. General API access closes during handoff."""

from typing import Annotated

from fastapi import APIRouter, Cookie, Header, HTTPException, Query, Response
from fastapi.responses import FileResponse

from taketwo.dataset.schema import canonical_json
from taketwo.dataset.storage import load

from .contracts import Waveform
from .review_contracts import (
    ActivateReview,
    Adjudication,
    AdjudicationRecord,
    DraftSave,
    ListeningEvent,
    OperatorKey,
    ReviewAssignment,
    ReviewGrant,
    ReviewInventory,
    ReviewMode,
    ReviewSession,
    ReviewSummary,
    ReviewValidation,
    WordInspection,
)
from .review_workspace import ReviewWorkspace

PREFIX = "/api/v1/review-workspace"


def install_reviews(app, root, jobs, audio, waveform):
    workspace = ReviewWorkspace(root, jobs)
    app.state.review_workspace = workspace
    router = APIRouter(prefix=PREFIX)

    def operator(x_review_operator: Annotated[str | None, Header()] = None):
        workspace.operator(x_review_operator)

    def access(sid, token):
        workspace.authorize(sid, token)
        session = workspace.get(sid)
        workspace.check_current(session)
        return session

    @router.get("/mode", response_model=ReviewMode)
    def mode():
        return {"active_session": workspace.active()}

    @router.post("/sessions", response_model=ReviewGrant, status_code=201)
    def create(
        request: ReviewAssignment, x_review_operator: Annotated[str | None, Header()] = None
    ):
        operator(x_review_operator)
        return workspace.create(request)

    @router.get("/inventory", response_model=ReviewInventory)
    def inventory(x_review_operator: Annotated[str | None, Header()] = None):
        operator(x_review_operator)
        if workspace.active():
            raise HTTPException(403, "End handoff before opening peer evidence.")
        return workspace.inventory()

    @router.post("/unlock")
    def unlock(request: OperatorKey, response: Response):
        workspace.operator(request.operator_key)
        workspace.unlock()
        response.delete_cookie("taketwo_review", path=PREFIX)
        return {"notice": "Handoff ended. Close the reviewer browser before operator work."}

    @router.post("/{sid}/resume", response_model=ReviewGrant)
    def resume(sid: str, x_review_operator: Annotated[str | None, Header()] = None):
        operator(x_review_operator)
        return workspace.resume(sid)

    @router.post("/{sid}/activate", response_model=ReviewSession)
    def activate(sid: str, request: ActivateReview, response: Response):
        session = access(sid, request.access_token)
        response.set_cookie(
            "taketwo_review", request.access_token, httponly=True, samesite="strict", path=PREFIX
        )
        return session

    @router.get("/{sid}", response_model=ReviewSession)
    def get(sid: str, taketwo_review: Annotated[str | None, Cookie()] = None):
        return access(sid, taketwo_review)

    @router.post("/{sid}/draft", response_model=ReviewSession)
    def save(sid: str, request: DraftSave, taketwo_review: Annotated[str | None, Cookie()] = None):
        access(sid, taketwo_review)
        return workspace.save(sid, request)

    @router.post("/{sid}/listen", response_model=ReviewSession)
    def listen(
        sid: str, request: ListeningEvent, taketwo_review: Annotated[str | None, Cookie()] = None
    ):
        access(sid, taketwo_review)
        return workspace.listen(sid, request)

    @router.post("/{sid}/inspect", response_model=ReviewSession)
    def inspect(
        sid: str, request: WordInspection, taketwo_review: Annotated[str | None, Cookie()] = None
    ):
        access(sid, taketwo_review)
        return workspace.inspect(sid, request.token_index)

    @router.get("/{sid}/validation", response_model=ReviewValidation)
    def validation(sid: str, taketwo_review: Annotated[str | None, Cookie()] = None):
        return workspace.validation(access(sid, taketwo_review))

    @router.post("/{sid}/submit", response_model=ReviewSession)
    def submit(
        sid: str, request: DraftSave, taketwo_review: Annotated[str | None, Cookie()] = None
    ):
        session = access(sid, taketwo_review)
        if request.draft != session.draft:
            raise HTTPException(409, "Save the draft before submitting it.")
        return workspace.submit(sid, request.revision)

    @router.get("/{sid}/export")
    def export(sid: str, taketwo_review: Annotated[str | None, Cookie()] = None):
        session = access(sid, taketwo_review)
        if session.state != "submitted":
            raise HTTPException(409, "Drafts cannot be exported as scientific Review evidence.")
        return Response(
            canonical_json(session.review.model_dump(mode="json")),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="taketwo-review-{sid}.json"'},
        )

    @router.get("/{sid}/summary", response_model=ReviewSummary)
    def summary(sid: str, taketwo_review: Annotated[str | None, Cookie()] = None):
        session = access(sid, taketwo_review)
        return {"session": session, "validation": workspace.validation(session)}

    @router.get("/{sid}/audio", response_class=FileResponse)
    def media(sid: str, taketwo_review: Annotated[str | None, Cookie()] = None):
        return audio(access(sid, taketwo_review).assignment.recording_id)

    @router.get("/{sid}/reference-audio", response_class=FileResponse)
    def reference_media(sid: str, taketwo_review: Annotated[str | None, Cookie()] = None):
        session = access(sid, taketwo_review)
        if session.assignment.scope != "flaws":
            raise HTTPException(403, "Reference context is assigned only for flaw review.")
        pair = next(p for p in load(root).pairs if p.id == session.assignment.pair_id)
        return audio(pair.reference_id)

    @router.get("/{sid}/waveform", response_model=Waveform)
    def peaks(
        sid: str,
        start_s: float = Query(0, ge=0, le=600),
        end_s: float = Query(600, gt=0, le=600),
        bins: int = Query(1000, ge=1, le=5000),
        taketwo_review: Annotated[str | None, Cookie()] = None,
    ):
        return waveform(access(sid, taketwo_review).assignment.recording_id, start_s, end_s, bins)

    @router.post("/adjudications", response_model=AdjudicationRecord)
    def adjudicate(
        request: Adjudication, x_review_operator: Annotated[str | None, Header()] = None
    ):
        operator(x_review_operator)
        if workspace.active():
            raise HTTPException(403, "Peer comparison is unavailable during independent handoff.")
        return workspace.adjudicate(request)

    app.include_router(router)


def handoff_denied(app, request):
    """Fail closed for every general endpoint, including newly added future APIs."""
    active = app.state.review_workspace.active()
    path = request.url.path
    if not active:
        return False
    if path in {f"{PREFIX}/mode", f"{PREFIX}/unlock"}:
        return False
    if path == f"{PREFIX}/{active}" or path.startswith(f"{PREFIX}/{active}/"):
        return False  # Each scoped route still checks its capability.
    # Only static application assets are public; no scientific or API payloads.
    return path.startswith("/api/") or path in {"/openapi.json", "/docs", "/redoc"}
