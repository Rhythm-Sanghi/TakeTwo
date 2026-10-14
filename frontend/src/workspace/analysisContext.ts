import type { Job, Report } from "../api";

// A report may be shown only for the exact job request and selected inputs.
export function reportMatchesSelection(
  report: Report,
  job: Job,
  referenceId: string,
  pairId: string | null,
  participantId?: string,
) {
  const expected = [referenceId, ...(participantId ? [participantId] : [])];
  return (
    Boolean(pairId) === Boolean(participantId) &&
    job.request.reference_id === referenceId &&
    job.request.pair_id === pairId &&
    report.pair_id === pairId &&
    report.inputs.length === expected.length &&
    expected.every((id) =>
      report.inputs.some((input) => input.provenance.recording_id === id),
    )
  );
}

export function referenceRequirements(report: Report) {
  const input = report.inputs[0];
  if (!input) return [];
  const requirements = [];
  if (!input.provenance.transcript_verified)
    requirements.push(
      "The reference transcript is unverified. Independent checking is required before reviewed use.",
    );
  if (
    [
      ...(report.eligibility.reasons ?? []),
      ...Object.values(report.feature_eligibility).flatMap(
        (gate) => gate.reasons ?? [],
      ),
    ].some((reason) => reason.code === "rights_pending")
  )
    requirements.push(
      "Reference rights remain unresolved. Preserve permission and consent evidence before public use.",
    );
  return requirements;
}
