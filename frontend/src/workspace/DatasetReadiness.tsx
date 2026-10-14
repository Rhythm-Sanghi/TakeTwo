import { useState } from "react";
import type { components } from "../api.generated";
import type { Recording, Report } from "../api";
import type { DatasetState } from "./useDatasetSummary";
import { readinessRequirements } from "./readinessRequirements";
import { printWorkspaceReport } from "./reportPrint";

export type Readiness = components["schemas"]["RecordingReadiness"];
export type DatasetSummary = components["schemas"]["DatasetSummary"];
const inventoryLabels: [string, string][] = [
  ["human_participant_takes", "Human-recorded participant takes"],
  ["distinct_speaker_ids", "Distinct recorded speaker IDs"],
  ["connected_families", "Connected speech families"],
  ["reference_takes", "Reference takes"],
  ["participant_takes", "Participant takes"],
  ["controlled_reference_takes", "Controlled self-recorded references"],
  ["public_source_candidates", "Public-source candidates"],
  ["synthetic_derivatives", "Synthetic derivatives"],
  ["verified_transcripts", "Verified transcripts"],
  [
    "submitted_independent_assertions",
    "Submitted independent review assertions",
  ],
  ["timing_reviews", "Timing reviews"],
  ["flaw_reviews", "Flaw reviews"],
];

export function DatasetReadiness({
  report = null,
  summary,
  recordings,
  selectedId,
  onSelect,
  onReview,
  loading = false,
  state,
  onRetry,
}: {
  report?: Report | null;
  summary: DatasetSummary | null;
  recordings: Recording[];
  selectedId: string;
  onSelect: (id: string) => void;
  onReview: (item: Readiness) => void;
  loading?: boolean;
  state?: DatasetState;
  onRetry?: () => void;
}) {
  const [printError, setPrintError] = useState("");
  const phase =
    state?.phase ?? (loading ? "loading" : summary ? "ready" : "unknown");
  const current = summary?.review_readiness?.find(
    (r) => r.recording_id === selectedId,
  );
  const selectedRecording = recordings.find((r) => r.id === selectedId);
  return (
    <section className="panel">
      <h2>Dataset readiness</h2>
      <p className="print-only readiness-identity">
        Recording: {selectedRecording?.original_filename ?? "Not selected"} ·
        dataset {summary?.dataset_version ?? "Unknown"} · inventory{" "}
        {phase === "ready" ? "current stored data" : phase}.
      </p>
      <p>
        Resolve the next requirement for the selected recording before
        evaluating delivery.
      </p>
      <div className="print-controls">
        <button
          disabled={phase === "loading" || phase === "restricted"}
          onClick={() => {
            setPrintError("");
            try {
              printWorkspaceReport("dataset");
            } catch {
              setPrintError(
                "Browser printing could not open. Retry the readiness export after reconnecting.",
              );
            }
          }}
        >
          Export Dataset Readiness / save PDF
        </button>
        <p className="meta">
          Choose Save as PDF in Chromium for searchable text. Microsoft Print to
          PDF can outline text.
        </p>
        {printError && <p role="alert">{printError}</p>}
      </div>
      <h3>Next required action</h3>
      {phase === "loading" ? (
        <p role="status">Loading dataset inventory and review readiness…</p>
      ) : phase !== "ready" && state ? (
        <div>
          <p role="alert">{state.message}</p>
          {summary && (
            <p className="meta">
              {phase === "partial" || phase === "unknown"
                ? "Available inventory is shown below; missing values are unknown."
                : "Inventory below is from the last successful request. Current review readiness is not established."}
            </p>
          )}
          {onRetry && (
            <button onClick={onRetry}>Retry dataset readiness</button>
          )}
          <details>
            <summary>Readiness request diagnostics</summary>
            <p className="mono">
              GET /api/v1/dataset ·{" "}
              {state.diagnostic || "Incomplete authoritative response"}
            </p>
          </details>
        </div>
      ) : !summary ? (
        <p>
          Dataset readiness unavailable. Reconnect / refresh to recover the
          inventory.
        </p>
      ) : recordings.length ? (
        <>
          <label className="print-controls">
            Readiness recording
            <select
              value={selectedId}
              onChange={(e) => onSelect(e.target.value)}
            >
              {recordings.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.original_filename} · {r.role}
                </option>
              ))}
            </select>
          </label>
          {current ? (
            <>
              <p role="status">{current.message}</p>
              <button onClick={() => onReview(current)}>
                Open Review Workspace
              </button>
              <p className="meta print-controls">
                Opens operator preparation only. An operator key is still
                required; this does not create a session, approve evidence or
                grant reviewer access.
              </p>
              <details className="print-controls">
                <summary>Existing review status for this recording</summary>
                <dl>
                  {Object.entries(current.review_status ?? {}).map(
                    ([scope, status]) => (
                      <div key={scope}>
                        <dt>{scope}</dt>
                        <dd>{status}</dd>
                      </div>
                    ),
                  )}
                </dl>
              </details>
              {["rights", "reviewed_version", "comparison"].includes(
                current.next_action,
              ) && (
                <details className="print-controls">
                  <summary>
                    Version and evaluation workflow instructions
                  </summary>
                  <p>
                    Set these variables to your actual files and new version
                    before running commands. Stop on a nonzero exit code.
                    Metadata must describe genuine permission and two real
                    independent transcript reviewers; leave missing evidence
                    pending.
                  </p>
                  <pre className="workflow-commands">{`uv run taketwo-dataset init $newWorkspace --version $newVersion
uv run taketwo-dataset import-reference $newWorkspace --audio $referenceAudio --metadata $referenceMetadata
uv run taketwo-dataset import-flawed $newWorkspace --reference $referenceId --audio $participantAudio --metadata $participantMetadata --category $declaredCategory --severity $declaredSeverity
uv run taketwo-dataset validate $newWorkspace --reproduce
uv run taketwo-comparison import-review $newWorkspace --review $actualReviewJson --alignment $currentAlignment
uv run taketwo-comparison evaluate $newWorkspace --report $eligibleReport --review $flawReviewA --review $flawReviewB --config $evaluationConfig`}</pre>
                  <p className="meta">
                    Import returns the actual reference ID. Regenerate
                    alignment/features before collecting hash-bound timing and
                    flaw reviews. The full ordered procedure and prerequisites
                    are in <code>docs/reviewed-evidence-workflow.md</code>;
                    these snippets do not supply reviews, rights or labels.
                  </p>
                </details>
              )}
            </>
          ) : (
            <p>
              Readiness unavailable. Refresh to load authoritative backend
              status.
            </p>
          )}
        </>
      ) : (
        <p>
          Import a permitted recording before preparing independent reviews.
        </p>
      )}
      <dl className="measurement-strip">
        <div>
          <dt>Recording inventory</dt>
          <dd>
            {summary
              ? `${summary.recordings} takes`
              : recordings.length
                ? `${recordings.length} loaded takes`
                : "Recording inventory unknown"}
          </dd>
          <dd>
            {summary?.inventory_counts?.distinct_speaker_ids ?? "Unknown"}{" "}
            recorded speaker IDs ·{" "}
            {summary?.inventory_counts?.connected_families ?? "Unknown"}{" "}
            connected families
          </dd>
        </div>
        <div>
          <dt>Verified transcripts</dt>
          <dd>
            {summary?.inventory_counts?.verified_transcripts ?? "Unknown"}
          </dd>
        </div>
        <div>
          <dt>Submitted review evidence</dt>
          <dd>
            {summary?.inventory_counts?.submitted_independent_assertions ??
              "Unknown"}{" "}
            assertions
          </dd>
          <dd>Inspect recording-specific review status.</dd>
        </div>
        <div>
          <dt>Eligible pairs</dt>
          <dd>
            {report
              ? `Selected comparison: ${report.eligibility.state === "ELIGIBLE" ? "eligible" : "not eligible"}`
              : "No comparison selected"}
          </dd>
          <dd>Workspace-wide eligible pair count unavailable.</dd>
        </div>
      </dl>
      <h3>Requirements for legitimate evaluation</h3>
      <p className="meta">
        Statuses describe stored evidence for this selection. A declaration or
        recorded agreement does not authenticate people, grant rights or
        validate accuracy.
      </p>
      <ol className="readiness-requirements">
        {readinessRequirements(
          selectedRecording,
          current,
          summary,
          report,
          phase === "ready",
        ).map((requirement) => (
          <li key={requirement.name}>
            <h4>
              {requirement.name}{" "}
              <span className="readiness-status">{requirement.status}</span>
            </h4>
            <p>{requirement.missing}</p>
            <p className="meta">
              <strong>Why:</strong> {requirement.why}
            </p>
            <p>
              <strong>Next:</strong> {requirement.action}
            </p>
            <p className="meta">
              <strong>Where:</strong> {requirement.location}
            </p>
          </li>
        ))}
      </ol>
      {phase === "ready" &&
        summary?.inventory_counts?.distinct_speaker_ids === 1 &&
        summary?.inventory_counts?.connected_families === 1 && (
          <p className="notice">
            This inventory has one declared speaker and one connected family.
            Splitting related takes across train/test would not establish
            speaker-independent generalization; acquire additional authorized,
            independently annotated groups before making that claim.
          </p>
        )}
      <details className="readiness-inventory">
        <summary>Details · recording inventory and review assertions</summary>{" "}
        <table tabIndex={0} aria-label="Dataset readiness counts">
          <thead>
            <tr>
              <th>Evidence</th>
              <th>Actual workspace count</th>
            </tr>
          </thead>
          <tbody>
            {inventoryLabels.map(([key, text]) => (
              <tr key={key}>
                <th scope="row">{text}</th>
                <td>{summary?.inventory_counts?.[key] ?? "Unknown"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
      <details className="readiness-caveats">
        <summary>Scientific caveats and evaluation requirements</summary>
        <p>
          Counts describe recording takes, declared speaker IDs and stored
          assertions, not authenticated people or verified independence.
          Connected families use the existing split grouping. Rights, resolved
          independent transcript/timing reviews and valid labels/splits are
          still required. Processing success and inventory counts do not
          establish eligible detection or validated accuracy.
        </p>
      </details>
    </section>
  );
}
