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
import { Inspector, Location, Scores } from "./Evidence";
import { Timeline } from "./Timeline";
import { TokenOverlay } from "./TokenOverlay";

type Page =
  | "Recording Library"
  | "Analysis Workspace"
  | "Rubric and Evidence"
  | "Dataset and Evaluation";
const pages: Page[] = [
  "Recording Library",
  "Analysis Workspace",
  "Rubric and Evidence",
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
          {item.provenance.rights.license_name}
        </dd>
        <dt>Rights evidence</dt>
        <dd>{item.provenance.rights.evidence}</dd>
        <dt>Attribution</dt>
        <dd>{item.provenance.rights.attribution}</dd>
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
        Corrections require a new dataset version and regenerated evidence using
        the documented CLI. Original recordings and bound reviews are immutable.
        Deletion is unavailable while dependency-safe deletion is unsupported.
      </p>
    </section>
  );
}

function Rubric({ policy }: { policy: Policy | null }) {
  if (!policy) return <p>Loading rubric…</p>;
  return (
    <section className="panel">
      <h2>{policy.version} · reference agreement</h2>
      <p>
        Initial engineering tolerances; uncalibrated. Acoustic agreement does
        not measure persuasion, emotion or overall speaking ability. Effective
        alternative deliveries can differ.
      </p>
      <table>
        <thead>
          <tr>
            <th>Dimension</th>
            <th>Weight</th>
            <th>Signed deviation</th>
            <th>Tolerance</th>
            <th>Saturation width</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>Pacing</th>
            <td>
              {number(policy.weights ? policy.weights.pacing * 100 : null, 0)}%
            </td>
            <td>ln(participant rate / reference rate)</td>
            <td>{number(policy.pacing_tolerance, 6)}</td>
            <td>{number(policy.pacing_width, 6)}</td>
          </tr>
          <tr>
            <th>Pause behavior</th>
            <td>
              {number(
                policy.weights ? policy.weights.pause_behavior * 100 : null,
                0,
              )}
              %
            </td>
            <td>Participant gap − reference gap (s)</td>
            <td>
              max({policy.pause_floor_s} s, {policy.pause_relative} × reference
              gap, calibrated floor)
            </td>
            <td>{policy.pause_width_s} s</td>
          </tr>
          <tr>
            <th>Energy variation</th>
            <td>
              {number(
                policy.weights ? policy.weights.energy_variation * 100 : null,
                0,
              )}
              %
            </td>
            <td>Difference in relative Q90−Q10 excursion</td>
            <td>{policy.energy_tolerance_db} dB</td>
            <td>{policy.energy_width_db} dB</td>
          </tr>
          <tr>
            <th>Pitch dynamics</th>
            <td>
              {number(
                policy.weights ? policy.weights.pitch_dynamics * 100 : null,
                0,
              )}
              %
            </td>
            <td>Difference in relative Q90−Q10 excursion</td>
            <td>{policy.pitch_tolerance_st} semitones</td>
            <td>{policy.pitch_width_st} semitones</td>
          </tr>
        </tbody>
      </table>
      <h3>Explicit aggregation</h3>
      <p className="mono">
        excess = max(0, |delta| − tolerance)
        <br />
        penalty = min(1, excess / saturation width)
        <br />
        dimension = 100 × (1 − Σ(weight × penalty) / Σ(eligible weight))
      </p>
      <p>
        Reference phrase duration weights pacing, energy and pitch; pause
        boundaries have equal weight. Coverage must reach{" "}
        {policy.minimum_coverage * 100}% with at least {policy.minimum_phrases}{" "}
        eligible phrases or {policy.minimum_gaps} gaps. Overall scoring requires
        all four dimensions; missing weights are never redistributed.
      </p>
      <p>
        Two independent agreeing timing/phrase reviews and verified transcripts
        are required. Pitch needs at least {policy.minimum_pitch_fraction * 100}
        % reliable frames; observed frame support needs{" "}
        {policy.minimum_coverage * 100}% coverage. Clips need at least{" "}
        {policy.minimum_phrase_words} words and {policy.minimum_phrase_s} s per
        eligible phrase. Confidence and timing error remain unmeasured.
      </p>
      <p>
        Energy normalization subtracts median active energy in dB. Pitch
        normalization uses 12 log₂(F0 / median voiced F0). No per-recording
        variance scaling hides dynamics. Word contour detectors add evidence
        without additional rubric penalties.
      </p>
      <details>
        <summary>Complete versioned policy</summary>
        <pre>{JSON.stringify(policy, null, 2)}</pre>
      </details>
    </section>
  );
}

export function App() {
  const [page, setPage] = useState<Page>("Recording Library");
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [pairs, setPairs] = useState<Pair[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [pairId, setPairId] = useState("");
  const [jobId, setJobId] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [region, setRegion] = useState<Region | null>(null);
  const [seek, setSeek] = useState<
    Record<string, { time: number; end?: number; nonce: number }>
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
  const job = jobs.find((j) => j.id === jobId) ?? null;
  const jobMatches =
    job?.request.reference_id === reference?.id &&
    job?.request.pair_id === (pair?.id ?? null);
  const activeJob = jobMatches ? job : null;
  const activeReport = jobMatches ? report : null;

  const refresh = useCallback(async () => {
    try {
      const [r, p, j, h, pol, e, v] = await Promise.all([
        api<Recording[]>("/recordings"),
        api<Pair[]>("/pairs"),
        api<Job[]>("/analyses"),
        api<Health>("/health"),
        api<Policy>("/rubrics/delivery-v0"),
        api<Evaluation[]>("/evaluations"),
        api<Review[]>("/reviews"),
      ]);
      setRecordings(r);
      setPairs(p);
      setJobs(j);
      setHealth(h);
      setPolicy(pol);
      setEvaluations(e);
      setReviews(v);
      setError("");
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
    if (activeJob?.report_path)
      api<Report>(`/analyses/${activeJob.id}/report`)
        .then((value) => {
          if (active) setReport(value);
        })
        .catch((cause) => {
          if (active) setError(cause.message);
        });
    return () => {
      active = false;
    };
  }, [activeJob?.id, activeJob?.report_path]);

  function navigate(next: Page) {
    setPage(next);
    requestAnimationFrame(() => heading.current?.focus());
  }
  function selectRecording(item: Recording) {
    setSelectedId(item.id);
    setPairId(pairs.find((p) => p.participant_id === item.id)?.id ?? "");
    setJobId("");
    setReport(null);
    setRegion(null);
  }
  async function start() {
    if (!reference) return;
    setStarting(true);
    setError("");
    try {
      const item = await post<Job>("/analyses", {
        reference_id: reference.id,
        pair_id: pair?.id ?? null,
        align,
      });
      setJobs((current) => [item, ...current.filter((j) => j.id !== item.id)]);
      setJobId(item.id);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setStarting(false);
    }
  }
  function inspect(item: Region) {
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
              Library is empty. Import a public reference and its exact spoken
              transcript.
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
                      {item.created_at.slice(0, 19).replace("T", " ")} UTC
                    </span>
                    <strong>
                      {item.state} · {item.stage}
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
        <main id="main">
          <h1 tabIndex={-1} ref={heading}>
            {page}
          </h1>
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
                  recordings={recordings}
                  onImported={(item) => {
                    void refresh();
                    setSelectedId(item.id);
                    setPairId("");
                  }}
                />
              </section>
              <div>
                {selected ? (
                  <>
                    <Metadata item={selected} />
                    <section className="panel">
                      <h2>Pair relationships</h2>
                      {pairs
                        .filter(
                          (p) =>
                            p.reference_id === selected.id ||
                            p.participant_id === selected.id,
                        )
                        .map((p) => (
                          <p key={p.id}>
                            <button
                              onClick={() => {
                                setSelectedId(p.reference_id);
                                setPairId(p.id);
                                setJobId("");
                                navigate("Analysis Workspace");
                              }}
                            >
                              Open pair {p.id}
                            </button>{" "}
                            · {label(p.identity_status)}
                          </p>
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
                    </section>
                  </>
                ) : (
                  <section className="panel">
                    <h2>Start with a reference</h2>
                    <p>
                      Import real public-source audio, provenance and the exact
                      words spoken. Then add a consented participant recording
                      of the same text. Synthetic derivatives imported through
                      dataset tooling remain explicitly labeled.
                    </p>
                  </section>
                )}
              </div>
            </div>
          )}
          {page === "Analysis Workspace" && (
            <>
              <section className="panel analysis-controls">
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
                      checked={align}
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
                      !health?.ready ||
                      starting ||
                      activeJob?.state === "running" ||
                      activeJob?.state === "queued"
                    }
                  >
                    {starting ? "Queuing…" : "Run analysis"}
                  </button>
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
                {health?.alignment_diagnostics.map((d) => (
                  <p className="notice" key={d.code}>
                    {d.message} {d.recovery}
                  </p>
                ))}
                {!participant && (
                  <p>
                    Reference inspection only: comparison and scoring require a
                    participant mirror.
                  </p>
                )}
                <p className="meta">
                  30 s analysis limit · one CPU worker · no fabricated progress
                  estimate. Completed acoustic artifacts are reused only when
                  input/configuration/code hashes match.
                </p>
                {activeJob && (
                  <p role="status" aria-live="polite">
                    Analysis {activeJob.state}: {activeJob.stage}.{" "}
                    {activeJob.error &&
                      `${activeJob.error.message} ${activeJob.error.recovery}`}
                  </p>
                )}
              </section>
              <div className="analysis-grid">
                <div className="timeline-stack">
                  {reference ? (
                    <Timeline
                      key={reference.id}
                      recording={reference}
                      job={activeJob}
                      regions={activeReport?.regions ?? []}
                      selected={region?.id ?? null}
                      seek={seek[reference.id] ?? null}
                      onSelect={inspect}
                      onPlay={onPlay}
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
                      key={participant.id}
                      recording={participant}
                      job={activeJob}
                      regions={activeReport?.regions ?? []}
                      selected={region?.id ?? null}
                      seek={seek[participant.id] ?? null}
                      onSelect={inspect}
                      onPlay={onPlay}
                    />
                  )}
                  <section className="panel">
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
                    <section className="panel">
                      <Scores report={activeReport} />
                      <h2>Detected deviations</h2>
                      {activeReport.regions.length ? (
                        <table>
                          <thead>
                            <tr>
                              <th>Category</th>
                              <th>Participant location</th>
                              <th>Severity</th>
                              <th>Action</th>
                            </tr>
                          </thead>
                          <tbody>
                            {activeReport.regions.map((r) => (
                              <tr key={r.id}>
                                <th>{label(r.category)}</th>
                                <td>
                                  <Location
                                    interval={r.participant_interval}
                                    anchor={r.participant_anchor_s}
                                  />
                                </td>
                                <td>{r.severity}</td>
                                <td>
                                  <button onClick={() => inspect(r)}>
                                    Inspect and seek
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <p>
                          {activeReport.overall_score == null
                            ? "Detection unavailable: evidence gates are unmet."
                            : "No threshold crossings detected under this rubric."}
                        </p>
                      )}
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
                    </section>
                  )}
                </div>
                <Inspector region={region} report={activeReport} />
              </div>
            </>
          )}
          {page === "Rubric and Evidence" && (
            <>
              <Rubric policy={policy} />
              {activeReport && (
                <section className="panel">
                  <Scores report={activeReport} />
                </section>
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
              <section className="panel">
                <h2>Dataset readiness</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Evidence</th>
                      <th>Actual workspace count</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th>Public-source candidates</th>
                      <td>
                        {recordings.filter((r) => r.origin === "source").length}
                      </td>
                    </tr>
                    <tr>
                      <th>Human-recorded participants</th>
                      <td>
                        {
                          recordings.filter((r) => r.origin === "self_recorded")
                            .length
                        }
                      </td>
                    </tr>
                    <tr>
                      <th>Synthetic derivatives</th>
                      <td>
                        {
                          recordings.filter((r) => r.origin === "synthetic")
                            .length
                        }
                      </td>
                    </tr>
                    <tr>
                      <th>Verified transcripts</th>
                      <td>
                        {
                          recordings.filter(
                            (r) => r.transcript.status === "verified",
                          ).length
                        }
                      </td>
                    </tr>
                    <tr>
                      <th>Independent review assertions</th>
                      <td>{reviews.filter((r) => r.independent).length}</td>
                    </tr>
                    <tr>
                      <th>Timing / flaw review artifacts</th>
                      <td>
                        {reviews.filter((r) => r.scope === "timing").length} /{" "}
                        {reviews.filter((r) => r.scope === "flaws").length}
                      </td>
                    </tr>
                  </tbody>
                </table>
                <p className="notice">
                  Competition dataset readiness is not certified. Counts are
                  inventory, not proof of reviewer independence, licensed
                  release or independent accuracy. Machine alignment is separate
                  from human ground truth.
                </p>
                <p>
                  Collect independent transcript checks, agreeing timing/phrase
                  reviews and blinded flaw inventories. Preserve acceptable
                  alternatives and split-disjoint families. Use the dataset and
                  comparison CLI to validate, import review assertions and run
                  evaluation; this view never generates approvals.
                </p>
              </section>
              <section className="panel">
                <h2>Persisted evaluation runs</h2>
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
