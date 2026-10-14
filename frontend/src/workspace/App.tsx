import { useCallback, useEffect, useRef, useState } from "react";
import { api, label, number, post } from "../api";
import type {
  Evaluation,
  Health,
  Job,
  Pair,
  Policy,
  Recording,
  Region,
  Report,
  Review,
} from "../api";
import { ImportForm } from "./ImportForm";
import { Inspector, Scores } from "./Evidence";
import { AnalysisResult, Findings } from "./AnalysisResult";
import { Rubric } from "./Rubric";
import { RubricGuide } from "./RubricGuide";
import { Timeline } from "./Timeline";
import { TokenOverlay } from "./TokenOverlay";
import { PairCorrection, ReviewImport } from "./RecordingTools";
import { DatasetReadiness } from "./DatasetReadiness";
import type { DatasetSummary, Readiness } from "./DatasetReadiness";
import { ReviewWorkspace } from "./ReviewWorkspace";

type Page =
  | "Recording Library"
  | "Analysis Workspace"
  | "Rubric and Evidence"
  | "Review Workspace"
  | "Dataset and Evaluation";
const pages: Page[] = [
  "Recording Library",
  "Analysis Workspace",
  "Rubric and Evidence",
  "Review Workspace",
  "Dataset and Evaluation",
];

function Metadata({ item }: { item: Recording }) {
  return (
    <section className="panel">
      <h2>Recording metadata</h2>
      <h3>{item.original_filename}</h3>
      <dl>
        <dt>Role / origin</dt>
        <dd>
          {item.role} / {label(item.origin)}
        </dd>
        <dt>Duration / original format</dt>
        <dd>
          {number(item.original_info.duration_s)} s ·{" "}
          {item.original_info.format} / {item.original_info.subtype}
        </dd>
        <dt>Original sample rate / channels</dt>
        <dd>
          {item.original_info.sample_rate_hz} Hz / {item.original_info.channels}
        </dd>
        <dt>Analysis derivative</dt>
        <dd>16 kHz · mono · float WAV · no gain normalization or trimming</dd>
        <dt>Quality flags</dt>
        <dd>
          {item.quality_flags.join(", ") ||
            "None detected by configured checks"}
        </dd>
        <dt>Original RMS / peak / clipping</dt>
        <dd>
          {number(item.original_info.rms_dbfs)} dBFS /{" "}
          {number(item.original_info.peak)} /{" "}
          {number(item.original_info.clipping_fraction, 6)}
        </dd>
        <dt>Family / speaker</dt>
        <dd>
          {item.family_id} / {item.speaker_id}
        </dd>
        <dt>Source</dt>
        <dd>{item.provenance.source}</dd>
        <dt>Source URL</dt>
        <dd>
          {item.provenance.source_url ? (
            <a
              href={item.provenance.source_url}
              target="_blank"
              rel="noreferrer"
            >
              Source record
            </a>
          ) : (
            "Not provided"
          )}
        </dd>
        <dt>Collection / source offset</dt>
        <dd>
          {item.provenance.collection_method} /{" "}
          {number(item.provenance.excerpt_offset_s)} s
        </dd>
        <dt>Rights</dt>
        <dd>
          {item.provenance.rights.status} ·{" "}
          {item.provenance.rights.license_name ?? "Public license not provided"}
        </dd>
        <dt>Rights evidence</dt>
        <dd>{item.provenance.rights.evidence ?? "Not provided"}</dd>
        <dt>Attribution</dt>
        <dd>{item.provenance.rights.attribution ?? "Not provided"}</dd>
        <dt>Consent evidence</dt>
        <dd>{item.provenance.consent_evidence ?? "Not provided"}</dd>
        <dt>Transcript status</dt>
        <dd>
          {item.transcript.status} · {item.transcript.reviewers.length} recorded
          reviewers
        </dd>
        <dt>Audio SHA-256</dt>
        <dd className="hash">{item.normalized_sha256}</dd>
      </dl>
      <h3>Original transcript</h3>
      <p className="transcript">{item.transcript.text}</p>
      <p className="notice">
        Transcript or rights corrections require a reviewed new dataset version
        and regenerated evidence. The pairing correction action prepares a
        separate version. Original recordings and bound reviews are immutable.
        Deletion is unavailable while dependency-safe deletion is unsupported.
      </p>
    </section>
  );
}

export function App() {
  const [page, setPage] = useState<Page>("Recording Library");
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [schemaVersion, setSchemaVersion] = useState(2);
  const [datasetSummary, setDatasetSummary] = useState<DatasetSummary | null>(
    null,
  );
  const [reviewTarget, setReviewTarget] = useState<Readiness | null>(null);
  const [pairs, setPairs] = useState<Pair[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [participantFor, setParticipantFor] = useState("");
  const [pairId, setPairId] = useState("");
  const [jobId, setJobId] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [region, setRegion] = useState<Region | null>(null);
  const [seek, setSeek] = useState<
    Record<
      string,
      { time: number; end?: number; play?: boolean; nonce: number }
    >
  >({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [align, setAlign] = useState(true);
  const playback = useRef<HTMLAudioElement | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const selected = recordings.find((r) => r.id === selectedId) ?? recordings[0];
  const reference =
    selected?.role === "reference"
      ? selected
      : recordings.find(
          (r) =>
            r.id ===
            pairs.find((p) => p.participant_id === selected?.id)?.reference_id,
        );
  const availablePairs = pairs.filter((p) => p.reference_id === reference?.id);
  const pair = availablePairs.find((p) => p.id === pairId);
  const participant = recordings.find((r) => r.id === pair?.participant_id);
  const overLimit = [reference, participant].some(
    (r) =>
      r &&
      r.normalized_info.duration_s > (health?.maximum_analysis_duration_s ?? 0),
  );
  const job = jobs.find((j) => j.id === jobId) ?? null;
  const jobMatches =
    job?.request.reference_id === reference?.id &&
    job?.request.pair_id === (pair?.id ?? null);
  const activeJob = jobMatches ? job : null;
  const activeReport = jobMatches ? report : null;
  const hasAvailableDimensions =
    activeReport &&
    (activeReport.eligibility.state === "ELIGIBLE" ||
      activeReport.dimensions.some((d) => d.score != null) ||
      activeReport.regions.some((r) => r.eligibility.state === "ELIGIBLE"));

  const refresh = useCallback(async () => {
    try {
      const [r, p, j, h, pol, e, v, d] = await Promise.all([
        api<Recording[]>("/recordings"),
        api<Pair[]>("/pairs"),
        api<Job[]>("/analyses"),
        api<Health>("/health"),
        api<Policy>("/rubrics/delivery-v0"),
        api<Evaluation[]>("/evaluations"),
        api<Review[]>("/reviews"),
        api<DatasetSummary>("/dataset"),
      ]);
      setRecordings(r);
      setSchemaVersion(d.schema_version);
      setDatasetSummary(d);
      setPairs(p);
      setJobs(j);
      setHealth(h);
      setPolicy(pol);
      setEvaluations(e);
      setReviews(v);
      setError("");
      return { recordings: r, pairs: p };
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void refresh();
  }, [refresh]);
  useEffect(() => {
    if (!jobs.some((j) => j.state === "running" || j.state === "queued"))
      return;
    const timer = setInterval(() => {
      api<Job[]>("/analyses")
        .then(setJobs)
        .catch((cause) => setError(cause.message));
    }, 1000);
    return () => clearInterval(timer);
  }, [jobs]);
  useEffect(() => {
    let active = true;
    setReport(null);
    setRegion(null);
    setReportLoading(Boolean(activeJob?.report_path));
    if (activeJob?.report_path)
      api<Report>(`/analyses/${activeJob.id}/report`)
        .then((value) => {
          if (active) setReport(value);
        })
        .catch((cause) => {
          if (active) setError(cause.message);
        })
        .finally(() => {
          if (active) setReportLoading(false);
        });
    return () => {
      active = false;
    };
  }, [activeJob?.id, activeJob?.report_path, recordings, reviews]);

  function navigate(next: Page) {
    setPage(next);
    requestAnimationFrame(() => heading.current?.focus());
  }
  function selectRecording(item: Recording) {
    setParticipantFor("");
    setSelectedId(item.id);
    setPairId(pairs.find((p) => p.participant_id === item.id)?.id ?? "");
    setJobId("");
    setReport(null);
    setRegion(null);
  }
  async function start(retry?: Job) {
    if (!reference) return;
    setStarting(true);
    setError("");
    try {
      const item = await post<Job>(
        "/analyses",
        retry?.request ?? {
          reference_id: reference.id,
          pair_id: pair?.id ?? null,
          align: align && Boolean(health?.alignment_configured),
        },
      );
      setJobs((current) => [item, ...current.filter((j) => j.id !== item.id)]);
      setJobId(item.id);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setStarting(false);
    }
  }
  function inspect(item: Region, replay = false) {
    setRegion(item);
    const nonce = Date.now();
    const requests: typeof seek = {};
    if (reference)
      requests[reference.id] = {
        time: item.reference_interval?.start_s ?? item.reference_anchor_s ?? 0,
        end: item.reference_interval?.end_s,
        nonce,
      };
    if (participant)
      requests[participant.id] = {
        time:
          item.participant_interval?.start_s ?? item.participant_anchor_s ?? 0,
        end: item.participant_interval?.end_s,
        play: replay && Boolean(item.participant_interval),
        nonce,
      };
    setSeek(requests);
  }
  function openHistory(item: Job) {
    setSelectedId(item.request.reference_id);
    setPairId(item.request.pair_id ?? "");
    setJobId(item.id);
    navigate("Analysis Workspace");
  }
  function onPlay(element: HTMLAudioElement) {
    if (playback.current && playback.current !== element)
      playback.current.pause();
    playback.current = element;
  }
  async function imported(item: Recording) {
    const current = await refresh();
    if (!current)
      throw new Error(
        "Recording was stored but inventory refresh failed. Reconnect / refresh; do not re-import.",
      );
    setSelectedId(item.id);
    setPairId(
      current?.pairs.find((p) => p.participant_id === item.id)?.id ?? "",
    );
    setJobId("");
    setReport(null);
    setRegion(null);
  }

  return (
    <>
      <a className="skip" href="#main">
        Skip to workspace
      </a>
      <header className="app-header">
        <div className="brand">
          <strong>TakeTwo</strong>
          <span>Speech analysis workspace</span>
        </div>
        <span className="environment">LOCAL / CPU</span>
        <span role="status">
          {activeJob?.state === "running"
            ? activeJob.stage
            : health
              ? health.ready
                ? "Local workspace ready"
                : "CPU supervisor unavailable"
              : "Connecting to local service…"}
        </span>
      </header>
      <nav aria-label="Workspace areas">
        {pages.map((name) => (
          <button
            key={name}
            aria-current={page === name ? "page" : undefined}
            onClick={() => navigate(name)}
          >
            {name}
          </button>
        ))}
      </nav>
      <div className="workspace-shell">
        <aside className="library" aria-label="Recording library">
          <div className="section-heading">
            <h2>Recordings</h2>
            <button
              onClick={() => void refresh()}
              aria-label="Refresh workspace"
            >
              Refresh
            </button>
          </div>
          <p className="meta">
            {recordings.length} recordings · {pairs.length} pairs
          </p>
          {loading ? (
            <p role="status">Loading recordings…</p>
          ) : recordings.length === 0 ? (
            <p>
              Library is empty. Import a public or self-recorded reference and
              the words spoken. Then add a participant.
            </p>
          ) : (
            <ul>
              {recordings.map((item) => (
                <li key={item.id}>
                  <button
                    className="recording-button"
                    aria-pressed={selected?.id === item.id}
                    onClick={() => selectRecording(item)}
                  >
                    <strong>{item.original_filename}</strong>
                    <span>
                      {item.role} / {label(item.origin)}
                    </span>
                    <span className="mono">
                      {number(item.normalized_info.duration_s)} s ·{" "}
                      {item.transcript.status}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          <h3>Analysis history</h3>
          {jobs.length ? (
            <ul>
              {jobs.slice(0, 30).map((item) => (
                <li key={item.id}>
                  <button
                    className="history-button"
                    onClick={() => openHistory(item)}
                  >
                    <span>
                      {new Date(item.created_at)
                        .toISOString()
                        .slice(0, 19)
                        .replace("T", " ")}{" "}
                      UTC
                    </span>
                    <strong>
                      {recordings.find(
                        (r) => r.id === item.request.reference_id,
                      )?.original_filename ?? "Recording"}{" "}
                      · {item.state} · {item.stage}
                    </strong>
                    <span className="mono">{item.id.slice(0, 12)}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="meta">No analyses have run.</p>
          )}
        </aside>
        <main id="main" tabIndex={-1}>
          <h1 tabIndex={-1} ref={heading}>
            {page}
          </h1>
          {page === "Review Workspace" && (
            <ReviewWorkspace
              recordings={recordings}
              jobs={jobs}
              pairs={pairs}
              initial={reviewTarget}
            />
          )}
          {error && (
            <div role="alert" className="error">
              <p>{error}</p>
              <button onClick={() => void refresh()}>
                Reconnect / refresh
              </button>
            </div>
          )}
          {page === "Recording Library" && (
            <div className="library-content">
              <section className="panel">
                <ImportForm
                  maximumDuration={health?.maximum_analysis_duration_s}
                  recordings={recordings}
                  participantFor={participantFor}
                  schemaVersion={schemaVersion}
                  onUpgraded={() => void refresh()}
                  onImported={imported}
                />
              </section>
              <div>
                {selected ? (
                  <>
                    <section className="panel">
                      <h2>Pair relationships</h2>
                      {pairs
                        .filter(
                          (p) =>
                            p.reference_id === selected.id ||
                            p.participant_id === selected.id,
                        )
                        .map((p) => (
                          <div key={p.id}>
                            <button
                              onClick={() => {
                                setSelectedId(p.reference_id);
                                setPairId(p.id);
                                setJobId("");
                                navigate("Analysis Workspace");
                              }}
                            >
                              Compare{" "}
                              {
                                recordings.find(
                                  (r) => r.id === p.participant_id,
                                )?.original_filename
                              }{" "}
                              with{" "}
                              {
                                recordings.find((r) => r.id === p.reference_id)
                                  ?.original_filename
                              }
                            </button>{" "}
                            · {label(p.identity_status)}
                            <PairCorrection pair={p} recordings={recordings} />
                          </div>
                        ))}
                      {!pairs.some(
                        (p) =>
                          p.reference_id === selected.id ||
                          p.participant_id === selected.id,
                      ) && (
                        <p>
                          Incomplete pair: no participant mirror. Raw acoustic
                          inspection is available.
                        </p>
                      )}
                      <button onClick={() => navigate("Analysis Workspace")}>
                        Inspect audio in workspace
                      </button>
                      {reference && (
                        <button
                          onClick={() => {
                            setParticipantFor(reference.id);
                            navigate("Recording Library");
                          }}
                        >
                          Add participant
                        </button>
                      )}
                      <details>
                        <summary>What needs independent review?</summary>
                        <p>
                          Verify the spoken words with two independent
                          listeners. Matching pasted text is not verification.
                          Then check every aligned word and phrase; run a new
                          analysis after importing real timing reviews. The
                          Dataset and Evaluation area accepts actual review
                          files. Corrections use a new dataset version; approval
                          is never automatic.
                        </p>
                      </details>
                    </section>
                    <details className="panel">
                      <summary>
                        Recording metadata and source transcript
                      </summary>
                      <Metadata item={selected} />
                    </details>
                  </>
                ) : (
                  <section className="panel">
                    <h2>Start with a reference</h2>
                    <p>
                      Choose Public source reference for archival speech, or
                      Self-recorded controlled reference for private practice.
                      Add a separate participant of the same words, then open
                      Analysis Workspace. Missing reviews keep scores
                      unavailable. Synthetic derivatives from dataset tools
                      remain explicitly labeled.
                    </p>
                  </section>
                )}
              </div>
            </div>
          )}
          {page === "Analysis Workspace" && (
            <>
              <AnalysisResult
                job={activeJob}
                report={activeReport}
                loading={reportLoading}
                reference={reference}
                participant={participant}
                evaluations={evaluations}
                nextLabel={
                  !reference
                    ? "Import a reference"
                    : activeJob?.state === "completed" &&
                        !activeReport &&
                        !reportLoading
                      ? "Reload assessment evidence"
                      : hasAvailableDimensions
                        ? "Understand available dimensions"
                        : activeReport
                          ? "Check dataset and review requirements"
                          : "Choose recordings and run analysis"
                }
                onNext={() =>
                  !reference
                    ? navigate("Recording Library")
                    : activeJob?.state === "completed" &&
                        !activeReport &&
                        !reportLoading
                      ? void refresh()
                      : hasAvailableDimensions
                        ? navigate("Rubric and Evidence")
                        : activeReport
                          ? navigate("Dataset and Evaluation")
                          : document.getElementById("analysis-setup")?.focus()
                }
              />
              <section
                className="panel analysis-controls"
                id="analysis-setup"
                tabIndex={-1}
              >
                <h2>Choose recordings and process audio</h2>
                <div className="toolbar">
                  <label>
                    Reference recording
                    <select
                      value={reference?.id ?? ""}
                      onChange={(event) => {
                        const item = recordings.find(
                          (r) => r.id === event.target.value,
                        );
                        if (item) selectRecording(item);
                      }}
                    >
                      <option value="" disabled>
                        Select a reference
                      </option>
                      {recordings
                        .filter((r) => r.role === "reference")
                        .map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.original_filename}
                          </option>
                        ))}
                    </select>
                  </label>
                  <label>
                    Participant pair
                    <select
                      value={pairId}
                      onChange={(event) => {
                        setPairId(event.target.value);
                        setJobId("");
                        setRegion(null);
                      }}
                    >
                      <option value="">Reference inspection only</option>
                      {availablePairs.map((p) => (
                        <option value={p.id} key={p.id}>
                          {
                            recordings.find((r) => r.id === p.participant_id)
                              ?.original_filename
                          }{" "}
                          · {label(p.identity_status)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="check">
                    <input
                      type="checkbox"
                      checked={align && Boolean(health?.alignment_configured)}
                      onChange={(event) => setAlign(event.target.checked)}
                      disabled={!health?.alignment_configured}
                    />{" "}
                    Run automatic alignment
                  </label>
                  <button
                    className="primary"
                    onClick={() => void start()}
                    disabled={
                      !reference ||
                      overLimit ||
                      !health?.ready ||
                      starting ||
                      activeJob?.state === "running" ||
                      activeJob?.state === "queued"
                    }
                  >
                    {starting ? "Queuing…" : "Run analysis"}
                  </button>
                  {activeJob &&
                    ["failed", "cancelled"].includes(activeJob.state) && (
                      <button
                        onClick={() => void start(activeJob)}
                        disabled={starting || !health?.ready}
                      >
                        Retry this analysis
                      </button>
                    )}
                  {activeJob &&
                    (activeJob.state === "running" ||
                      activeJob.state === "queued") && (
                      <button
                        onClick={() =>
                          post<Job>(`/analyses/${activeJob.id}/cancel`, {})
                            .then((item) =>
                              setJobs((current) =>
                                current.map((j) =>
                                  j.id === item.id ? item : j,
                                ),
                              ),
                            )
                            .catch((cause) => setError(cause.message))
                        }
                      >
                        Cancel analysis
                      </button>
                    )}
                </div>
                {overLimit && (
                  <p className="notice">
                    A selected recording exceeds the{" "}
                    {health?.maximum_analysis_duration_s}-second analysis limit.
                    Playback remains available. Use each timeline's selection
                    controls and Save selection as an analysis excerpt; supply
                    the exact words for each cut, then choose the excerpt
                    reference and participant.
                  </p>
                )}
                <details>
                  <summary>Processing configuration and diagnostics</summary>
                  {health?.alignment_diagnostics.map((d) => (
                    <p className="notice" key={d.code}>
                      {d.message} {d.recovery}
                    </p>
                  ))}
                  {!participant && (
                    <p>
                      Reference inspection only: comparison and scoring require
                      a participant mirror.
                    </p>
                  )}
                  <p className="meta">
                    {health?.maximum_analysis_duration_s ?? "…"} s analysis
                    limit · one CPU worker · no fabricated progress estimate.
                    Completed acoustic artifacts are reused only when
                    input/configuration/code hashes match.
                  </p>
                  <p role="status" aria-live="polite" aria-atomic="true">
                    {activeJob ? (
                      <>
                        Analysis {activeJob.state}: {activeJob.stage}.{" "}
                        {activeJob.error &&
                          `${activeJob.error.message} ${activeJob.error.recovery}`}
                      </>
                    ) : (
                      "No analysis selected."
                    )}
                  </p>
                </details>
              </section>
              {activeReport && (
                <Findings
                  report={activeReport}
                  onSelect={inspect}
                  onReplay={(item) => inspect(item, true)}
                />
              )}
              <h2 className="exploration-heading">
                Listen and explore evidence
              </h2>
              <p className="exploration-heading meta">
                Each recording keeps its own native clock. Reviewed
                correspondence is required for linked navigation.
              </p>
              <div className="print-controls">
                <button onClick={() => window.print()} disabled={!activeReport}>
                  Print analysis summary
                </button>
              </div>
              {activeReport && (
                <p className="print-only">
                  Analysis {activeJob?.id} · dataset{" "}
                  {activeReport.dataset_version} · {activeReport.policy.version}
                  . Machine processing does not verify transcripts, reviewed
                  evidence or accuracy.
                </p>
              )}
              <div className="analysis-grid">
                <div className="timeline-stack">
                  {reference ? (
                    <Timeline
                      maximumDuration={health?.maximum_analysis_duration_s}
                      key={reference.id}
                      recording={reference}
                      job={activeJob}
                      regions={activeReport?.regions ?? []}
                      selected={region?.id ?? null}
                      seek={seek[reference.id] ?? null}
                      onSelect={inspect}
                      onPlay={onPlay}
                      references={recordings}
                      onExcerpt={imported}
                    />
                  ) : (
                    <section className="panel">
                      <p>
                        Select or import a reference recording to open its
                        timeline.
                      </p>
                    </section>
                  )}
                  {participant && (
                    <Timeline
                      maximumDuration={health?.maximum_analysis_duration_s}
                      key={participant.id}
                      recording={participant}
                      job={activeJob}
                      regions={activeReport?.regions ?? []}
                      selected={region?.id ?? null}
                      seek={seek[participant.id] ?? null}
                      onSelect={inspect}
                      onPlay={onPlay}
                      references={recordings}
                      onExcerpt={imported}
                    />
                  )}
                  <section className="panel native-correspondence">
                    <h2>Native-time correspondence</h2>
                    <p>
                      Each track retains its own seconds and cursor. Selecting a
                      grounded deviation seeks both tracks to their
                      corresponding intervals or boundary anchors. Equal
                      timestamps are never assumed.
                    </p>
                    <button
                      disabled={!activeReport?.regions.length}
                      onClick={() => {
                        const items = activeReport?.regions ?? [];
                        if (items.length)
                          inspect(
                            items[
                              (items.findIndex((r) => r.id === region?.id) +
                                1) %
                                items.length
                            ],
                          );
                      }}
                    >
                      Next detected deviation
                    </button>
                    {!activeReport?.regions.length && (
                      <p className="meta">
                        Synchronized deviation seeking is unavailable until
                        reviewed correspondence produces grounded regions.
                      </p>
                    )}
                  </section>
                  {activeReport && activeJob && (
                    <TokenOverlay
                      jobId={activeJob.id}
                      onSeek={(referenceTime, participantTime) => {
                        const nonce = Date.now();
                        const requests: typeof seek = {};
                        if (reference)
                          requests[reference.id] = {
                            time: referenceTime,
                            nonce,
                          };
                        if (participant)
                          requests[participant.id] = {
                            time: participantTime,
                            nonce,
                          };
                        setRegion(null);
                        setSeek(requests);
                      }}
                    />
                  )}
                  {activeReport && (
                    <details className="panel score-panel technical-details">
                      <summary>
                        Technical details · scores, coverage and scientific
                        exports
                      </summary>
                      <Scores report={activeReport} />
                      <div className="toolbar">
                        <a
                          className="button"
                          href={`/api/v1/analyses/${activeJob!.id}/export?format=json`}
                          download
                        >
                          Export report JSON
                        </a>
                        <a
                          className="button"
                          href={`/api/v1/analyses/${activeJob!.id}/export?format=csv`}
                          download
                        >
                          Export region CSV
                        </a>
                      </div>
                    </details>
                  )}
                </div>
                {reportLoading ? (
                  <aside className="panel" aria-busy="true">
                    <h2>Evidence inspector</h2>
                    <p role="status">
                      Validating and loading the completed report…
                    </p>
                  </aside>
                ) : (
                  <details
                    className="panel evidence-details"
                    open={Boolean(region)}
                    key={region?.id ?? "inputs"}
                  >
                    <summary>
                      Evidence inspector · measurements and provenance
                    </summary>
                    <Inspector region={region} report={activeReport} />
                  </details>
                )}
              </div>
            </>
          )}
          {page === "Rubric and Evidence" && (
            <>
              <RubricGuide report={activeReport} />
              <details className="panel">
                <summary>
                  Technical details · thresholds, normalization and weighting
                </summary>
                <Rubric policy={policy} />
              </details>
              {activeReport && (
                <details className="panel">
                  <summary>
                    Technical details · selected comparison scores
                  </summary>
                  <Scores report={activeReport} />
                </details>
              )}
              <p>
                All displayed scoring values come from backend report contracts.
                Use the workspace inspector for a selected region's numeric
                evidence.
              </p>
            </>
          )}
          {page === "Dataset and Evaluation" && (
            <>
              <DatasetReadiness
                report={activeReport}
                summary={datasetSummary}
                loading={loading}
                recordings={recordings}
                selectedId={selected?.id ?? ""}
                onSelect={(id) => {
                  const item = recordings.find((r) => r.id === id);
                  if (item) selectRecording(item);
                }}
                onReview={(item) => {
                  setReviewTarget(item);
                  navigate("Review Workspace");
                }}
              />
              <ReviewImport
                jobs={jobs}
                recordings={recordings}
                onImported={() => void refresh()}
              />
              <section className="panel">
                <h2>Persisted evaluation runs</h2>
                {evaluations.length > 0 && (
                  <p className="notice">
                    Stored runs preserve their original policy and metrics.
                    Evaluations created before exact-inventory-v1 may depend on
                    reviewer ordering. Recompute those runs with resolved
                    independent reviews before using their metrics as current
                    evidence; keep the original artifacts.
                  </p>
                )}
                {!evaluations.length ? (
                  <p>
                    No evaluation results exist. Detection accuracy is
                    unavailable until independent labels and valid splits are
                    present.
                  </p>
                ) : (
                  evaluations.map((e, i) => (
                    <section key={i}>
                      <h3>
                        {e.config.mode} · {e.origin} ·{" "}
                        {label(e.eligibility.state)}
                      </h3>
                      <p>
                        {e.independent_real_validation
                          ? "Independent real-validation gate passed for this stored run."
                          : "Independent real validation is not established."}
                      </p>
                      {e.config.mode === "software_fixture" && (
                        <p className="notice">
                          Software fixture only; these metrics do not measure
                          speech performance.
                        </p>
                      )}
                      <dl>
                        <dt>Precision / recall / F1</dt>
                        <dd>
                          {number(e.metrics?.precision)} /{" "}
                          {number(e.metrics?.recall)} / {number(e.metrics?.f1)}
                        </dd>
                        <dt>Families</dt>
                        <dd>{e.family_ids.length}</dd>
                      </dl>
                      {(e.eligibility.reasons ?? []).map((r) => (
                        <p key={r.code}>{r.message}</p>
                      ))}
                      <details>
                        <summary>
                          Full evaluation evidence and limitations
                        </summary>
                        <pre>{JSON.stringify(e, null, 2)}</pre>
                      </details>
                    </section>
                  ))
                )}
              </section>
            </>
          )}
        </main>
      </div>
      <footer>
        Local files stay on this computer. Acoustic deviations describe
        reference agreement; independent human evaluation remains a separate
        gate.
      </footer>
    </>
  );
}
