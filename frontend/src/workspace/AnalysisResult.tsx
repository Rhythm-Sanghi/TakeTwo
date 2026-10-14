import { label, number } from "../api";
import type { Evaluation, Job, Recording, Region, Report } from "../api";
import { Location } from "./Evidence";
import { referenceRequirements } from "./analysisContext";

export function evidenceRequirement(reason: { code: string; message: string }) {
  const wording: Record<string, string> = {
    pair_review_required:
      "Verify that both recordings contain the same spoken words.",
    transcript_unverified:
      "Transcripts need independent checks and a reviewed dataset version.",
    rights_pending:
      "Recording rights remain unresolved. Preserve permission and consent evidence.",
    timing_review_required:
      "Independent timing reviews are still required for both recordings.",
  };
  return wording[reason.code] ?? reason.message;
}

// Presentation of backend states only. This does not decide scientific eligibility.
export function assessmentTitle(
  job: Job | null,
  report: Report | null,
  loading: boolean,
  referenceOnly = false,
) {
  if (referenceOnly) {
    if (!job)
      return "Reference ready. Participant comparison pending selection.";
    if (job.state === "queued" || job.state === "running")
      return "Reference audio analysis in progress.";
    if (job.state === "failed") return "Reference audio analysis failed.";
    if (job.state === "cancelled") return "Reference audio analysis cancelled.";
    if (loading)
      return "Reference audio analysis complete. Loading measurements…";
    if (!report)
      return "Reference audio analysis complete. Measurements unavailable.";
    return "Reference audio analysis complete";
  }
  if (!job) return "Audio not processed.";
  if (job.state === "queued" || job.state === "running")
    return "Audio analysis in progress.";
  if (job.state === "failed") return "Audio analysis failed.";
  if (job.state === "cancelled") return "Audio analysis cancelled.";
  if (loading) return "Audio analysis complete. Loading assessment evidence…";
  if (!report)
    return "Audio analysis complete. Assessment evidence unavailable.";
  if (report.eligibility.state === "ELIGIBLE" && report.overall_score != null)
    return "Eligible comparison results available.";
  if (report.dimensions.some((d) => d.score != null))
    return "Some dimensions available. Overall assessment unavailable.";
  if (report.eligibility.state === "ELIGIBLE")
    return "Eligible evidence available. Overall assessment unavailable.";
  if (report.eligibility.state === "INELIGIBLE")
    return "Audio analysis complete. Delivery assessment unavailable.";
  return "Audio analysis complete. Delivery assessment awaiting verification.";
}

export function hasIndependentEvaluation(
  job: Job | null,
  report: Report | null,
  evaluations: Evaluation[],
) {
  const hash = job?.report_path?.match(/comparison-([a-f0-9]{64})\.json$/)?.[1];
  return Boolean(
    hash &&
    report &&
    evaluations.some(
      (e) =>
        e.report_sha256.includes(hash) &&
        e.dataset_sha256 === report.dataset_sha256 &&
        e.implementation_sha256 === report.implementation_sha256 &&
        e.policy_sha256 === report.policy_sha256 &&
        e.eligibility.state === "ELIGIBLE" &&
        e.origin === "human" &&
        e.independent_real_validation &&
        e.metrics &&
        e.config.mode === "held_out",
    ),
  );
}

export function printedAssessmentStatus(
  report: Report | null,
  referenceOnly: boolean,
) {
  if (referenceOnly)
    return "Automatic processing does not verify the reference. Independently checked text, timing and genuine rights evidence remain required.";
  if (!report)
    return "Verified assessment evidence is unavailable. Restore the completed report or finish processing before assessing eligibility.";
  if (report.overall_score != null && report.eligibility.state === "ELIGIBLE")
    return `Reference agreement: ${number(report.overall_score, 1)} / 100. This uncalibrated rubric is not overall speaking ability.`;
  if (
    report.eligibility.state === "ELIGIBLE" ||
    report.dimensions.some((d) => d.score != null) ||
    report.regions.some((r) => r.eligibility.state === "ELIGIBLE")
  )
    return "Some evidence is available; the overall assessment remains unavailable. Check dimension coverage and review requirements.";
  const reasons = [
    ...(report.eligibility.reasons ?? []),
    ...Object.values(report.feature_eligibility ?? {}).flatMap(
      (g) => g.reasons ?? [],
    ),
  ];
  return reasons.some((r) =>
    [
      "transcript_unverified",
      "timing_review_required",
      "pair_review_required",
    ].includes(r.code),
  )
    ? "Verified assessment is unavailable because independent review requirements have not been satisfied."
    : "Verified assessment is unavailable because stored eligibility or acoustic requirements have not been satisfied. Inspect the report's reasons before interpreting the measurements.";
}

export function AnalysisResult({
  job,
  report,
  loading,
  reference,
  participant,
  evaluations,
  onNext,
  nextLabel,
  referenceOnly = false,
  availablePairCount = 0,
}: {
  job: Job | null;
  report: Report | null;
  loading: boolean;
  reference?: Recording;
  participant?: Recording;
  evaluations: Evaluation[];
  onNext: () => void;
  nextLabel: string;
  referenceOnly?: boolean;
  availablePairCount?: number;
}) {
  const reasons = [
    ...(report?.eligibility.reasons ?? []),
    ...Object.values(report?.feature_eligibility ?? {}).flatMap(
      (g) => g.reasons ?? [],
    ),
  ];
  const messages =
    referenceOnly && report
      ? referenceRequirements(report)
      : [...new Set(reasons.map(evidenceRequirement))];
  const pending = !referenceOnly && report && report.overall_score == null;
  const availableEvidence =
    report &&
    (report.eligibility.state === "ELIGIBLE" ||
      report.dimensions.some((d) => d.score != null) ||
      report.regions.some((r) => r.eligibility.state === "ELIGIBLE"));
  return (
    <section className="panel analysis-outcome" aria-label="Analysis result">
      <section className="print-only workspace-assessment">
        <h2>
          {referenceOnly
            ? "Reference verification status"
            : "Verified Assessment"}
        </h2>
        <p>{printedAssessmentStatus(report, referenceOnly)}</p>
        {report && (
          <p>
            Dataset {report.dataset_version} · stored eligibility{" "}
            {label(report.eligibility.state)}. Machine observations and product
            listening do not constitute independent scientific validation.
          </p>
        )}
      </section>
      <div className="result-pair">
        <span>
          Reference{" "}
          <strong>
            {reference?.original_filename ?? "Choose a recording"}
          </strong>
        </span>
        {!referenceOnly && (
          <span>
            Participant{" "}
            <strong>{participant?.original_filename ?? "Not selected"}</strong>
          </span>
        )}
      </div>
      <div role="status" aria-live="polite" aria-atomic="true">
        <p className="eyebrow">
          Mode:{" "}
          {referenceOnly ? "Reference inspection" : "Participant comparison"} ·
          Processing: {job ? label(job.state) : "Not started"}
          {!referenceOnly && (
            <>
              {" "}
              · Assessment:{" "}
              {report
                ? report.overall_score != null &&
                  report.eligibility.state === "ELIGIBLE"
                  ? "Available"
                  : report.dimensions.some((d) => d.score != null)
                    ? "Partially available"
                    : report.eligibility.state === "ELIGIBLE"
                      ? "Evidence available; score unavailable"
                      : report.eligibility.state === "INELIGIBLE"
                        ? "Unavailable"
                        : "Pending verification"
                : "Unavailable"}
            </>
          )}
        </p>
        <h2>
          {assessmentTitle(
            job,
            report,
            loading,
            referenceOnly && Boolean(reference),
          )}
        </h2>
        {job && ["running", "queued"].includes(job.state) && (
          <p>
            Current stage: {label(job.stage)}. You can keep exploring or cancel
            this analysis. No completion estimate is available.
          </p>
        )}
        {job?.error && (
          <p>
            {job.error.message} {job.error.recovery}
          </p>
        )}
        {job?.state === "cancelled" && (
          <p>Processing stopped. Retry this analysis when you are ready.</p>
        )}
        {job?.cancel_requested && job.state !== "cancelled" && (
          <p>Cancellation requested. Waiting for the worker to stop.</p>
        )}
        {job?.state === "completed" && !report && !loading && (
          <p>
            Reconnect / refresh to reload the report. Do not re-import the
            recordings.
          </p>
        )}
      </div>
      {(referenceOnly || !report || pending) && (
        <button className="primary" onClick={onNext}>
          {nextLabel}
        </button>
      )}
      {referenceOnly && reference && (
        <>
          <p>
            {job?.state === "completed" && report
              ? "Reference measurements are available. No participant comparison was run."
              : "Run reference inspection to measure this audio, or choose a participant for a delivery comparison."}
          </p>
          <p className="meta">
            {availablePairCount
              ? `${availablePairCount} participant ${availablePairCount === 1 ? "pair is" : "pairs are"} available for this reference. Select one to compare delivery.`
              : "No participant pair exists for this reference. Add a participant to compare delivery."}
          </p>
          {messages.length > 0 && (
            <details className="result-requirements">
              <summary>Reference review and use requirements</summary>
              <ul>
                {messages.map((message) => (
                  <li key={message}>{message}</li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
      {pending && (
        <>
          <p>
            {availableEvidence
              ? "Some evidence is eligible. The overall score remains unavailable; inspect each dimension’s coverage and requirements. Findings describe reference agreement, not overall speaking ability."
              : "Measured audio features are available; independent evidence is needed before delivery-flaw conclusions. See evidence requirements."}
          </p>
          <details className="result-requirements">
            <summary>Evidence requirements</summary>{" "}
            <ul className="outcome-requirements">
              {messages.map((message) => (
                <li key={message}>{message}</li>
              ))}
            </ul>
          </details>
        </>
      )}
      {!referenceOnly && report?.overall_score != null && (
        <p>
          Reference agreement:{" "}
          <strong>{number(report.overall_score, 1)} / 100</strong>. This
          uncalibrated rubric describes agreement with this reference, not
          overall speaking ability.
        </p>
      )}
      {!referenceOnly && hasIndependentEvaluation(job, report, evaluations) && (
        <p>
          Independent evaluation completed for this report. See Dataset and
          Evaluation for the stored run and its limitations.
        </p>
      )}
      {report && (
        <dl className="measurement-strip">
          {report.inputs.map((input) => {
            const name =
              input.provenance.recording_id === reference?.id
                ? "Reference"
                : "Participant";
            return (
              <div key={input.provenance.recording_id}>
                <dt>{name} · measured audio</dt>
                <dd>
                  <strong>{number(input.duration_s, 2)} s</strong>
                </dd>
                <dd>
                  Reliable pitch coverage:{" "}
                  {number(input.pitch_valid_fraction * 100, 2)}% · diagnostic
                </dd>
                <dd>
                  <details>
                    <summary>Feature and alignment details</summary>
                    <p>{input.spectral_frame_count} spectral frames</p>{" "}
                    <p>
                      Automatic alignment:{" "}
                      {input.alignment
                        ? "Automatic artifact available"
                        : "Unavailable"}
                    </p>
                    <p>
                      Acoustic features:{" "}
                      {input.features ? "Artifact available" : "Unavailable"}
                    </p>
                  </details>
                </dd>
              </div>
            );
          })}
        </dl>
      )}
    </section>
  );
}

export function Findings({
  report,
  onSelect,
  onReplay,
}: {
  report: Report;
  onSelect: (region: Region) => void;
  onReplay: (region: Region) => void;
}) {
  const regions = report.regions.filter(
    (r) => r.eligibility.state === "ELIGIBLE",
  );
  return (
    <section className="panel findings" aria-label="Findings">
      <h2>Findings</h2>
      {!regions.length ? (
        <p>
          {report.eligibility.state === "ELIGIBLE"
            ? "No threshold crossings detected under this rubric. This does not establish a perfect performance or validated accuracy."
            : "Findings pending. Flaw detection unavailable until the required evidence is reviewed. Zero detected regions does not indicate a perfect performance."}
        </p>
      ) : (
        <ul className="findings-list">
          {regions.map((r) => (
            <li key={r.id}>
              <div className="section-heading">
                <h3>{label(r.category)}</h3>
                <span>Severity {r.severity} / 3 · eligible evidence</span>
              </div>
              <p>
                Participant:{" "}
                <Location
                  interval={r.participant_interval}
                  anchor={r.participant_anchor_s}
                />{" "}
                · Reference:{" "}
                <Location
                  interval={r.reference_interval}
                  anchor={r.reference_anchor_s}
                />
              </p>
              <p>{r.explanation.plain}</p>
              {report.observations
                .filter((o) => r.observation_ids.includes(o.id))
                .map((o) => (
                  <p key={o.id}>
                    {label(o.detector)}: reference {number(o.reference)}{" "}
                    {o.unit}; participant {number(o.participant)} {o.unit}.
                  </p>
                ))}
              <p className="meta">
                Confidence is not calibrated; timing uncertainty is unmeasured.{" "}
                {r.explanation.suggested_review}
              </p>
              <div className="toolbar">
                <button onClick={() => onSelect(r)}>Inspect and seek</button>
                {r.participant_interval && (
                  <button onClick={() => onReplay(r)}>
                    Replay participant interval
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
