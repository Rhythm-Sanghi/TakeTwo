import type { ExploratoryReport, Job, Recording, Report } from "../api";

export function exploratoryMatchesSelection(
  report: ExploratoryReport,
  job: Job,
  reference: Recording,
  pairId: string | null,
  participant?: Recording,
) {
  const expected = [reference, ...(participant ? [participant] : [])];
  return (
    report.job_id === job.id &&
    report.reference_id === reference.id &&
    report.pair_id === pairId &&
    job.request.reference_id === reference.id &&
    job.request.pair_id === pairId &&
    Boolean(pairId) === Boolean(participant) &&
    report.recordings.length > 0 &&
    report.recordings.length <= expected.length &&
    new Set(report.recordings.map((r) => r.recording_id)).size ===
      report.recordings.length &&
    report.recordings.every((r) => {
      const selected = expected.find((item) => item.id === r.recording_id);
      return (
        selected &&
        r.provenance.audio_sha256 === selected.normalized_sha256 &&
        r.provenance.sample_sha256 === selected.sample_sha256 &&
        r.provenance.transcript_sha256 === selected.transcript_sha256 &&
        r.duration_s === selected.normalized_info.duration_s
      );
    })
  );
}

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
