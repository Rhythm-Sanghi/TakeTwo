import { useState } from "react";
import type { FormEvent } from "react";
import { post } from "../api";
import type { Job, Pair, Recording, Review } from "../api";
import type { components } from "../api.generated";

export function ExcerptForm({
  recording,
  selection,
  references,
  onSaved,
}: {
  recording: Recording;
  selection: [number, number];
  references: Recording[];
  onSaved?: (item: Recording) => void | Promise<void>;
}) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function save(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    setBusy(true);
    setError("");
    try {
      const item = await post<Recording>(
        `/recordings/${recording.id}/excerpt`,
        {
          start_s: selection[0],
          end_s: selection[1],
          transcript: data.get("text"),
          reference_id: data.get("reference") || null,
        },
      );
      await onSaved?.(item);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <details>
      <summary>Save selection as an analysis excerpt</summary>
      <p>
        Original audio stays unchanged. Select at most 30 seconds, listen, then
        supply exactly the words inside this track's selection. Each take has
        its own cut times. New text remains unverified.
      </p>
      <form onSubmit={save} aria-label={`${recording.role} excerpt`}>
        <p>
          Selection: {selection[0].toFixed(3)}–{selection[1].toFixed(3)} s
        </p>
        {recording.role === "participant" && (
          <label>
            Excerpt reference
            <select name="reference" required>
              <option value="">Select the matching reference excerpt</option>
              {references
                .filter((r) => r.role === "reference")
                .map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.provenance.source} · {r.original_filename}
                  </option>
                ))}
            </select>
          </label>
        )}
        <label>
          Exact excerpt transcript
          <textarea name="text" required rows={3} maxLength={100000} />
        </label>
        <button
          disabled={
            busy ||
            selection[1] <= selection[0] ||
            selection[1] - selection[0] > 30 ||
            recording.origin === "synthetic"
          }
        >
          Save excerpt
        </button>
        {selection[1] - selection[0] > 30 && (
          <p className="notice">Shorten the selection to 30 seconds or less.</p>
        )}
        <p role="status">{busy ? "Saving explicit excerpt…" : ""}</p>
        {error && <p role="alert">{error}</p>}
      </form>
    </details>
  );
}

export function PairCorrection({
  pair,
  recordings,
}: {
  pair: Pair;
  recordings: Recording[];
}) {
  const [error, setError] = useState("");
  const [result, setResult] = useState<
    components["schemas"]["WorkspaceRevision"] | null
  >(null);
  const [busy, setBusy] = useState(false);
  return (
    <details>
      <summary>Correct this pairing safely</summary>
      <p>
        Prepare a new two-recording dataset version using the chosen reference
        and original participant. Existing pairs, files and reports stay
        unchanged. Reviews do not transfer; restart into the new version.
      </p>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          const data = new FormData(e.currentTarget);
          setError("");
          setBusy(true);
          try {
            setResult(
              await post(`/pairs/${pair.id}/correction`, {
                reference_id: data.get("reference"),
              }),
            );
          } catch (cause) {
            setError((cause as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <label>
          Correct reference
          <select name="reference" required>
            <option value="">Choose a different reference</option>
            {recordings
              .filter(
                (r) => r.role === "reference" && r.id !== pair.reference_id,
              )
              .map((r) => (
                <option key={r.id} value={r.id}>
                  {r.provenance.source} · {r.original_filename}
                </option>
              ))}
          </select>
        </label>
        <button disabled={busy}>Prepare corrected version</button>
      </form>
      {error && <p role="alert">{error}</p>}
      {result && (
        <div role="status">
          <p>{result.notice}</p>
          <p>Stop the current service, then run from the repository:</p>
          <pre>{`uv run taketwo-web --workspace '${result.workspace.replaceAll("'", "''")}'`}</pre>
          <p>
            Use your existing MFA configuration when restarting. The corrected
            pair requires independent text/timing review before scoring.
          </p>
        </div>
      )}
    </details>
  );
}

export function ReviewImport({
  jobs,
  recordings,
  onImported,
}: {
  jobs: Job[];
  recordings: Recording[];
  onImported: () => void;
}) {
  const [review, setReview] = useState<Review | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <section className="panel">
      <h2>Independent review handoff</h2>
      <p>
        Two independent people must check the transcript and every word/phrase
        boundary. Blinded flaw reviews are separate from detection. Matching
        text or successful alignment is not approval.
      </p>
      <details>
        <summary>Import an actual reviewer file</summary>
        <p>
          Use the documented review JSON contract. This imports an assertion and
          never authenticates the person or generates approval. Transcript
          corrections require a reviewed new dataset version and fresh
          alignment; imported transcript checks alone do not change
          verification.
        </p>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            setError("");
            setNotice("");
            setBusy(true);
            try {
              const response = await post<{ notice: string }>(
                "/reviews/import",
                { job_id: new FormData(e.currentTarget).get("job"), review },
              );
              setNotice(response.notice);
              onImported();
            } catch (cause) {
              setError((cause as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <label>
            Analysis for review
            <select name="job" required>
              <option value="">Select the original analysis</option>
              {jobs
                .filter((j) => Object.keys(j.artifacts ?? {}).length)
                .map((j) => (
                  <option key={j.id} value={j.id}>
                    {
                      recordings.find((r) => r.id === j.request.reference_id)
                        ?.original_filename
                    }{" "}
                    · {new Date(j.created_at).toLocaleString()} · {j.state}
                  </option>
                ))}
            </select>
          </label>
          <label>
            Independent review JSON
            <input
              type="file"
              accept=".json,application/json"
              required
              onChange={async (e) => {
                setReview(null);
                setError("");
                const file = e.target.files?.[0];
                if (!file) return;
                if (file.size > 1000000) {
                  setError("Review exceeds 1 MiB.");
                  return;
                }
                try {
                  setReview(JSON.parse(await file.text()) as Review);
                } catch {
                  setError(
                    "Choose valid review JSON prepared by the reviewer.",
                  );
                }
              }}
            />
          </label>
          {review && (
            <p>
              Declared scope: {review.scope}; decision: {review.decision}.
              Server validates identity, bounds and provenance.
            </p>
          )}
          <button disabled={!review || busy}>Import review assertion</button>
        </form>
        <p role="status">{busy ? "Validating review assertion…" : notice}</p>
        {error && <p role="alert">{error}</p>}
      </details>
    </section>
  );
}
