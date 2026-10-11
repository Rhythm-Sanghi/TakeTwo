"""Central gates; invalid pitch never disables independently usable energy or timing."""

from taketwo.analysis.alignment import validate_alignment
from taketwo.analysis.contracts import AlignmentResult, FeatureResult
from taketwo.analysis.storage import validate_features
from taketwo.dataset.audio import sha256
from taketwo.dataset.schema import Pair, Recording, content_hash, tokenize

from .contracts import Eligibility, Policy, Reason, Review
from .reviews import reviewed_timing, validate_review

DIMENSIONS = ("pacing", "pause_behavior", "energy_variation", "pitch_dynamics")


def decision(reasons: list[Reason], *, review: bool = False) -> Eligibility:
    return Eligibility(
        state=("REVIEW_REQUIRED" if review else "INELIGIBLE") if reasons else "ELIGIBLE",
        reasons=reasons,
    )


def reason(code: str, message: str) -> Reason:
    return Reason(code=code, message=message)


def recording_gates(
    recording: Recording,
    features: FeatureResult,
    alignment: AlignmentResult | None,
    reviews: list[Review],
    policy: Policy,
):
    """Invalid structure/identity is operational failure; absent evidence is abstention."""
    validate_features(features)
    p = features.provenance
    tokens, offsets = tokenize(recording.transcript.text)
    if (
        p.recording_id != recording.id
        or p.dataset_version != recording.dataset_version
        or p.audio_sha256 != recording.normalized_sha256
        or p.sample_sha256 != recording.sample_sha256
        or p.transcript_sha256 != recording.transcript_sha256
        or p.original_text_sha256 != sha256(recording.transcript.text.encode("utf-8"))
        or p.transcript_verified != (recording.transcript.status == "verified")
        or tokens != recording.tokens
        or offsets != recording.token_offsets
        or content_hash(tokens) != recording.transcript_sha256
        or features.quality.sample_count != recording.normalized_info.frames
    ):
        raise ValueError("Feature/recording input integrity differs.")
    if alignment:
        validate_alignment(alignment)
        if alignment.provenance != p or alignment.duration_s != features.quality.duration_s:
            raise ValueError("Alignment identity/duration differs from features.")
        if features.alignment_sha256 != content_hash(alignment.model_dump(mode="json")):
            raise ValueError("Features must reference the supplied Phase 2 alignment.")
    for review in reviews:
        validate_review(review, recording, alignment)
    common = []
    if not p.transcript_verified:
        common.append(
            reason(
                "transcript_unverified",
                "The Phase 2 transcript is unverified; "
                "import independent checks and rebuild in a reviewed dataset version.",
            )
        )
    if alignment is None or alignment.status != "succeeded":
        common.append(reason("alignment_unavailable", "Complete successful alignment is required."))
    provenance = recording.provenance
    if provenance.rights.status != "cleared":
        common.append(reason("rights_pending", "Relevant dataset rights are not cleared."))
    if recording.role == "reference" and (
        recording.origin != "source" or not provenance.baseline_rationale
    ):
        common.append(
            reason("reference_provenance", "Reference needs real source and selection rationale.")
        )
    if recording.origin == "self_recorded" and not provenance.consent_evidence:
        common.append(reason("consent_missing", "Human recording consent reference is missing."))
    if recording.origin == "synthetic" and recording.transformation is None:
        common.append(
            reason("synthetic_provenance", "Synthetic input lacks transformation provenance.")
        )
    if "near_silent" in features.quality.flags or features.quality.rms < 0.001:
        common.append(
            reason("near_silent", "Near-silent recording cannot support delivery conclusions.")
        )
    words, phrases, timing_reason = reviewed_timing(reviews)
    if timing_reason:
        common.append(reason("timing_review_required", timing_reason))
    decisions = {}
    for dimension in DIMENSIONS:
        issues = list(common)
        if dimension in {"pause_behavior", "energy_variation"} and (
            features.config.minimum_pause_s != policy.pause_floor_s
            or features.config.activity_drop_db != 25
        ):
            issues.append(
                reason(
                    "policy_incompatible",
                    "Activity/pause extraction differs from the scoring policy.",
                )
            )
        if dimension == "pitch_dynamics":
            if (
                features.pitch_baseline_hz is None
                or features.config.voicing_threshold < 0.8
                or set(features.quality.flags) & {"pitch_range_edge", "pitch_jump_review"}
            ):
                issues.append(
                    reason(
                        "pitch_unreliable",
                        "Pitch is unavailable, range-limited, "
                        "has octave-jump warnings or uses an incompatible confidence mask.",
                    )
                )
        decisions[dimension] = decision(
            issues,
            review=bool(issues)
            and all(
                r.code in {"transcript_unverified", "timing_review_required", "rights_pending"}
                for r in issues
            ),
        )
    return decisions, words, phrases


def pair_gate(
    pair: Pair | None, reference: Recording, participant: Recording | None
) -> Eligibility:
    if pair is None or participant is None:
        return decision([reason("pair_missing", "No participant mirror/pair is available.")])
    if (
        pair.reference_id != reference.id
        or pair.participant_id != participant.id
        or reference.id == participant.id
        or reference.role != "reference"
        or participant.role != "participant"
        or reference.family_id != participant.family_id
        or reference.dataset_version != participant.dataset_version
        or pair.transcript_sha256 != reference.transcript_sha256
        or pair.transcript_sha256 != participant.transcript_sha256
        or reference.tokens != participant.tokens
    ):
        return decision(
            [reason("pair_relationship", "Pair roles, family or canonical transcript differ.")]
        )
    expected = (
        "derived"
        if participant.origin == "synthetic"
        else (
            "verified"
            if reference.transcript.status == participant.transcript.status == "verified"
            else "needs_review"
        )
    )
    if pair.identity_status != expected or expected == "needs_review":
        return decision(
            [reason("pair_review_required", "Pair transcript identity needs review.")], review=True
        )
    if participant.origin == "synthetic" and (
        participant.transformation is None
        or participant.transformation.parent_id != reference.id
        or participant.transformation.source_sha256 != reference.normalized_sha256
    ):
        return decision(
            [reason("pair_relationship", "Synthetic input does not derive from this reference.")]
        )
    return decision([])


def combine(decisions: list[Eligibility]) -> Eligibility:
    reasons = list({(r.code, r.message): r for d in decisions for r in d.reasons}.values())
    states = {d.state for d in decisions}
    if states == {"ELIGIBLE"}:
        state = "ELIGIBLE"
    elif "ELIGIBLE" in states or "PARTIALLY_ELIGIBLE" in states:
        state = "PARTIALLY_ELIGIBLE"
    elif "INELIGIBLE" in states:
        state = "INELIGIBLE"
    else:
        state = "REVIEW_REQUIRED"
    return Eligibility(state=state, reasons=reasons)
