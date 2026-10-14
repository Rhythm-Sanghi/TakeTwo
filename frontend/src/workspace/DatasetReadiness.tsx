import type { components } from "../api.generated";
import type { Recording, Report } from "../api";

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
}: {
  report?: Report | null;
  summary: DatasetSummary | null;
  recordings: Recording[];
  selectedId: string;
  onSelect: (id: string) => void;
  onReview: (item: Readiness) => void;
  loading?: boolean;
}) {
  const current = summary?.review_readiness?.find(
    (r) => r.recording_id === selectedId,
  );
  return (
    <section className="panel">
      <h2>Dataset readiness</h2>
      <p>
        Resolve the next requirement for the selected recording before
        evaluating delivery.
      </p>
      <h3>Next required action</h3>
      {loading ? (
        <p role="status">Loading dataset inventory and review readiness…</p>
      ) : !summary ? (
        <p>
          Dataset readiness unavailable. Reconnect / refresh to recover the
          inventory.
        </p>
      ) : recordings.length ? (
        <>
          <label>
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
              <p className="meta">
                Opens operator preparation only. An operator key is still
                required; this does not create a session, approve evidence or
                grant reviewer access.
              </p>
              <details>
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
                <details>
                  <summary>
                    Version and evaluation workflow instructions
                  </summary>
                  <p>
                    The remaining version/import/evaluation operations use the
                    documented CLI:{" "}
                    <code>
                      uv run taketwo-dataset init --help; uv run taketwo-dataset
                      import-reference --help; uv run taketwo-dataset
                      import-flawed --help
                    </code>
                    ; <code>uv run taketwo-comparison evaluate --help</code>.
                    Follow the local <code>docs/human-pilot-kit.md</code> and{" "}
                    <code>docs/reproducibility.md</code>; preserve originals and
                    regenerate dependent artifacts.
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
          <dd>{recordings.length} takes</dd>
          <dd>
            {summary?.inventory_counts?.distinct_speaker_ids ?? "Unavailable"}{" "}
            recorded speaker IDs ·{" "}
            {summary?.inventory_counts?.connected_families ?? "Unavailable"}{" "}
            connected families
          </dd>
        </div>
        <div>
          <dt>Verified transcripts</dt>
          <dd>
            {summary?.inventory_counts?.verified_transcripts ?? "Unavailable"}
          </dd>
        </div>
        <div>
          <dt>Submitted review evidence</dt>
          <dd>
            {summary?.inventory_counts?.submitted_independent_assertions ??
              "Unavailable"}{" "}
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
      <details>
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
                <td>{summary?.inventory_counts?.[key] ?? "Unavailable"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
      <details>
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
