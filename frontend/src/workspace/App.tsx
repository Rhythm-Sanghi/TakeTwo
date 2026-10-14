import { useCallback, useEffect, useRef, useState } from "react";
import { api, label, number, post } from "../api";
import type {
  Evaluation,
  ExploratoryReport,
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
import {
  reportMatchesSelection,
  exploratoryMatchesSelection,
  referenceRequirements,
} from "./analysisContext";
import { AnalysisResult, Findings } from "./AnalysisResult";
import { ExploratoryResult } from "./ExploratoryResult";
import { Rubric } from "./Rubric";
import { RubricGuide } from "./RubricGuide";
import { Timeline } from "./Timeline";
import { TokenOverlay } from "./TokenOverlay";
import { PairCorrection, ReviewImport } from "./RecordingTools";
import { DatasetReadiness } from "./DatasetReadiness";
import { useDatasetSummary } from "./useDatasetSummary";
import type { Readiness } from "./DatasetReadiness";
import { ReviewWorkspace } from "./ReviewWorkspace";
import { installWorkspacePrint, printWorkspaceReport } from "./reportPrint";

import { WorkspaceNavigation } from "./WorkspaceNavigation";
import type { Page } from "./WorkspaceNavigation";

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
  const [workspacePrintError, setWorkspacePrintError] = useState("");
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [schemaVersion, setSchemaVersion] = useState(2);
  const { state: datasetState, reload: reloadDataset } = useDatasetSummary();
  const datasetSummary = datasetState.summary;
  const [reviewTarget, setReviewTarget] = useState<Readiness | null>(null);
  const [pairs, setPairs] = useState<Pair[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [serviceState, setServiceState] = useState<
    "connecting" | "ready" | "unavailable"
  >("connecting");
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [evaluationState, setEvaluationState] = useState<
    "loading" | "ready" | "unavailable"
  >("loading");
  const [reviews, setReviews] = useState<Review[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [participantFor, setParticipantFor] = useState("");
  const [pairId, setPairId] = useState("");
  const [jobId, setJobId] = useState("");
  const [reportState, setReportState] = useState<{
    jobId: string;
    path: string;
    report: Report | null;
    loading: boolean;
  } | null>(null);
  const [region, setRegion] = useState<Region | null>(null);
  const [exploration, setExploration] = useState<ExploratoryReport | null>(
    null,
  );
  const [explorationError, setExplorationError] = useState("");
  const [insights, setInsights] = useState<
    import("../api").ComparativeReport | null
  >(null);
  const [insightsError, setInsightsError] = useState("");
  const [explorationLoading, setExplorationLoading] = useState(false);
  const [explorationRetry, setExplorationRetry] = useState(0);
  const [seek, setSeek] = useState<
    Record<
      string,
      { time: number; end?: number; play?: boolean; nonce: number }
    >
  >({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [audioTrack, setAudioTrack] = useState<"reference" | "participant">(
    "reference",
  );
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
  useEffect(() => {
    if (page !== "Analysis Workspace" && page !== "Dataset and Evaluation")
      return;
    return installWorkspacePrint(
      page === "Dataset and Evaluation"
        ? "dataset"
        : participant
          ? "paired"
          : "reference",
    );
  }, [page, participant?.id]);
  const latestAnalysis = jobs.find(
    (j) =>
      j.request.reference_id === reference?.id &&
      j.request.pair_id === (pair?.id ?? null) &&
      j.state === "completed",
  );
  const maximumDuration = health?.maximum_analysis_duration_s;
  const overLimit =
    maximumDuration != null &&
    [reference, participant].some(
      (r) => r && r.normalized_info.duration_s > maximumDuration,
    );
  const job = jobs.find((j) => j.id === jobId) ?? null;
  const jobMatches =
    job?.request.reference_id === reference?.id &&
    job?.request.pair_id === (pair?.id ?? null);
  const activeJob = jobMatches ? job : null;
  const currentReportState =
    activeJob &&
    reportState?.jobId === activeJob.id &&
    reportState.path === activeJob.report_path
      ? reportState
      : null;
  const reportLoading = Boolean(
    activeJob?.report_path &&
    (!currentReportState || currentReportState.loading),
  );
  const activeReport =
    currentReportState?.report &&
    activeJob &&
    reference &&
    reportMatchesSelection(
      currentReportState.report,
      activeJob,
      reference.id,
      pair?.id ?? null,
      participant?.id,
    )
      ? currentReportState.report
      : null;
  const comparisonReport = participant ? activeReport : null;
  const activeExploration =
    exploration &&
    activeJob &&
    reference &&
    exploratoryMatchesSelection(
      exploration,
      activeJob,
      reference,
      pair?.id ?? null,
      participant,
    )
      ? exploration
      : null;
  const hasAvailableDimensions =
    activeReport &&
    (activeReport.eligibility.state === "ELIGIBLE" ||
      activeReport.dimensions.some((d) => d.score != null) ||
      activeReport.regions.some((r) => r.eligibility.state === "ELIGIBLE"));

  const refreshGeneration = useRef(0);
  const refreshRequest = useRef<AbortController | null>(null);
  useEffect(
    () => () => {
      ++refreshGeneration.current;
      refreshRequest.current?.abort();
    },
    [],
  );
  useEffect(() => {
    if (datasetSummary) setSchemaVersion(datasetSummary.schema_version);
  }, [datasetSummary]);
  const refresh = useCallback(async () => {
    const generation = ++refreshGeneration.current;
    setServiceState("connecting");
    setEvaluationState("loading");
    refreshRequest.current?.abort();
    const controller = new AbortController();
    refreshRequest.current = controller;
    const timer = setTimeout(() => controller.abort(), 15000);
    const read = <T,>(path: string, receive: (value: T) => void) =>
      api<T>(path, { signal: controller.signal }).then((value) => {
        if (generation === refreshGeneration.current) receive(value);
        return value;
      });
    try {
      const results = await Promise.allSettled([
        read<Recording[]>("/recordings", (value) => {
          setRecordings(value);
          setLoading(false);
        }),
        read<Pair[]>("/pairs", setPairs),
        read<Job[]>("/analyses", setJobs),
        read<Health>("/health", setHealth),
        read<Policy>("/rubrics/delivery-v0", setPolicy),
        read<Evaluation[]>("/evaluations", setEvaluations),
        read<Review[]>("/reviews", setReviews),
        reloadDataset(),
      ]);
      if (generation !== refreshGeneration.current) return;
      setServiceState(
        results[3].status === "fulfilled" ? "ready" : "unavailable",
      );
      setEvaluationState(
        results[5].status === "fulfilled" ? "ready" : "unavailable",
      );
      const failures = results.flatMap((result, index) =>
        result.status === "rejected"
          ? [
              `${["Recordings", "Pairs", "Analyses", "Service", "Rubric", "Evaluations", "Review evidence", "Dataset"][index]}: ${result.reason instanceof Error ? result.reason.message : "Request failed. Retry refresh."}`,
            ]
          : [],
      );
      setError(failures.join(" "));
      const [r, p] = results;
      if (r.status === "fulfilled" && p.status === "fulfilled")
        return { recordings: r.value, pairs: p.value };
    } finally {
      clearTimeout(timer);
      if (generation === refreshGeneration.current) setLoading(false);
    }
  }, [reloadDataset]);
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
    const controller = new AbortController();
    setRegion(null);
    if (!activeJob?.report_path) {
      setReportState(null);
      return;
    }
    const identity = { jobId: activeJob.id, path: activeJob.report_path };
    const timer = setTimeout(() => controller.abort(), 15000);
    setReportState({ ...identity, report: null, loading: true });
    api<Report>(`/analyses/${activeJob.id}/report`, {
      signal: controller.signal,
    })
      .then((value) => {
        if (!active) return;
        if (
          !reference ||
          !reportMatchesSelection(
            value,
            activeJob,
            reference.id,
            pair?.id ?? null,
            participant?.id,
          )
        )
          throw new Error(
            "Report identity does not match the selected analysis. Refresh to reload its original inputs.",
          );
        setReportState({ ...identity, report: value, loading: false });
      })
      .catch((cause) => {
        if (active) {
          setReportState({ ...identity, report: null, loading: false });
          setError(
            controller.signal.aborted
              ? "Assessment request timed out. Refresh to reload evidence."
              : cause.message,
          );
        }
      })
      .finally(() => clearTimeout(timer));
    return () => {
      active = false;
      clearTimeout(timer);
      controller.abort();
    };
  }, [activeJob?.id, activeJob?.report_path, recordings, reviews]);

  useEffect(() => {
    const controller = new AbortController();
    setExploration(null);
    setExplorationError("");
    setExplorationLoading(false);
    if (!activeJob || ["queued", "running"].includes(activeJob.state)) return;
    // Avoid competing serializations of large native feature arrays during report
    // restoration. A failed formal-report load still permits exploratory recovery.
    if (
      activeJob.report_path &&
      (!currentReportState || currentReportState.loading)
    )
      return;
    const job = activeJob;
    setExplorationLoading(true);
    const timer = setTimeout(() => controller.abort(), 15000);
    let active = true;
    api<ExploratoryReport>(`/analyses/${job.id}/exploratory`, {
      signal: controller.signal,
    })
      .then((value) => {
        if (!active) return;
        if (
          !reference ||
          !exploratoryMatchesSelection(
            value,
            job,
            reference,
            pair?.id ?? null,
            participant,
          )
        )
          throw new Error(
            "Exploratory result identity differs from the selected analysis. Refresh its original inputs.",
          );
        setExploration(value);
      })
      .catch((cause) => {
        if (active)
          setExplorationError(
            controller.signal.aborted
              ? "Measurement request timed out. Retry loading; do not re-import audio."
              : cause.message,
          );
      })
      .finally(() => {
        clearTimeout(timer);
        if (active) setExplorationLoading(false);
      });
    return () => {
      active = false;
      clearTimeout(timer);
      controller.abort();
    };
  }, [
    activeJob?.id,
    activeJob?.state,
    currentReportState?.loading,
    explorationRetry,
  ]);

  useEffect(() => {
    setInsights(null);
    setInsightsError("");
    if (!activeExploration) return;
    let current = true;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    api<import("../api").ComparativeReport>(
      `/analyses/${activeExploration.job_id}/insights`,
      { signal: controller.signal },
    )
      .then((value) => {
        if (!current) return;
        if (
          !activeJob ||
          !reference ||
          !exploratoryMatchesSelection(
            value.exploratory,
            activeJob,
            reference,
            pair?.id ?? null,
            participant,
          ) ||
          value.exploratory.dataset_sha256 !==
            activeExploration.dataset_sha256 ||
          value.exploratory.recordings.some(
            (r) =>
              r.feature_artifact.sha256 !==
              activeExploration.recordings.find(
                (s) => s.recording_id === r.recording_id,
              )?.feature_artifact.sha256,
          ) ||
          value.exploratory.recordings.some(
            (r) =>
              r.alignment_artifact?.sha256 !==
              activeExploration.recordings.find(
                (s) => s.recording_id === r.recording_id,
              )?.alignment_artifact?.sha256,
          )
        )
          throw new Error(
            "Comparative source identity changed. Refresh the selected analysis.",
          );
        setInsights(value);
      })
      .catch((cause) => {
        if (current)
          setInsightsError(
            controller.signal.aborted
              ? "Comparative request timed out; retry loading the measurements."
              : cause.message,
          );
      })
      .finally(() => clearTimeout(timer));
    return () => {
      current = false;
      clearTimeout(timer);
      controller.abort();
    };
  }, [activeExploration]);

  function seekObservation(
    recording: string,
    start: number,
    end?: number,
    play = false,
  ) {
    if (recording !== reference?.id && recording !== participant?.id) return;
    playback.current?.pause();
    setRegion(null);
    setAudioTrack(recording === participant?.id ? "participant" : "reference");
    setSeek({ [recording]: { time: start, end, play, nonce: Date.now() } });
    if (!play)
      requestAnimationFrame(() => {
        const role =
          recording === participant?.id ? "participant" : "reference";
        document
          .querySelector<HTMLAudioElement>(`.track.${role} audio`)
          ?.focus();
      });
  }

  function navigate(next: Page) {
    playback.current?.pause();
    setPage(next);
    requestAnimationFrame(() => {
      heading.current?.focus({ preventScroll: true });
      window.scrollTo(0, 0);
    });
  }
  function selectRecording(item: Recording) {
    playback.current?.pause();
    setSeek({});
    setParticipantFor("");
    setSelectedId(item.id);
    setPairId(pairs.find((p) => p.participant_id === item.id)?.id ?? "");
    setJobId("");
    setReportState(null);
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
    if (participant) setAudioTrack("participant");
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
    playback.current?.pause();
    setReportState(null);
    setRegion(null);
    setSeek({});
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
    setReportState(null);
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
          {serviceState === "unavailable"
            ? "Local service unavailable. Retry refresh."
            : serviceState === "connecting"
              ? "Connecting to local service…"
              : activeJob?.state === "running"
                ? activeJob.stage
                : health
                  ? health.ready
                    ? "Local workspace ready"
                    : "CPU supervisor unavailable"
                  : "Connecting to local service…"}
        </span>
        <button onClick={() => void refresh()} aria-label="Refresh workspace">
          Refresh
        </button>
      </header>
      <WorkspaceNavigation current={page} onNavigate={navigate} />
      <div className="workspace-shell">
        <main id="main" tabIndex={-1} data-workspace={page}>
          <h1 tabIndex={-1} ref={heading}>
            {page}
          </h1>
          {["Rubric and Evidence", "Review Workspace"].includes(page) &&
            reference && (
              <p className="comparison-context">
                Current analysis comparison:{" "}
                <strong>{reference.original_filename}</strong> /{" "}
                <strong>
                  {participant?.original_filename ?? "No participant selected"}
                </strong>
              </p>
            )}
          {page === "Recording Library" && (
            <div className="toolbar library-shortcuts">
              <button
                onClick={() =>
                  document.getElementById("recording-collection")?.focus()
                }
              >
                Recordings and history
              </button>
              <button
                onClick={() =>
                  document.getElementById("recording-import")?.focus()
                }
              >
                Import a recording
              </button>
            </div>
          )}
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
            <div className="library-workspace">
              <aside
                className="library"
                id="recording-collection"
                tabIndex={-1}
                aria-label="Recording library"
              >
                <div className="section-heading">
                  <h2>Recordings</h2>
                </div>
                <p className="meta">
                  {recordings.length} recordings · {pairs.length} pairs
                </p>
                {loading ? (
                  <p role="status">Loading recordings…</p>
                ) : recordings.length === 0 ? (
                  <p>
                    Library is empty. Import a public or self-recorded reference
                    and the words spoken. Then add a participant.
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
                            · {item.state}
                            {item.stage !== item.state &&
                            !["completed", "cancelled"].includes(item.state)
                              ? ` · ${label(item.stage)}`
                              : ""}
                          </strong>
                          <span>
                            {(() => {
                              const historicPair = pairs.find(
                                (p) => p.id === item.request.pair_id,
                              );
                              return historicPair
                                ? (recordings.find(
                                    (r) => r.id === historicPair.participant_id,
                                  )?.original_filename ??
                                    "Participant metadata unavailable")
                                : item.request.pair_id
                                  ? "Participant metadata unavailable"
                                  : "Reference inspection";
                            })()}
                          </span>
                          <span className="mono">{item.id.slice(0, 12)}</span>
                        </button>
                        <details className="history-details">
                          <summary>Job details</summary>
                          <dl>
                            <dt>Job</dt>
                            <dd>{item.id}</dd>
                            <dt>Stage</dt>
                            <dd>{label(item.stage)}</dd>
                            <dt>Original request</dt>
                            <dd>
                              <pre>{JSON.stringify(item.request, null, 2)}</pre>
                            </dd>
                          </dl>
                        </details>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="meta">No analyses have run.</p>
                )}
              </aside>

              <div className="library-content">
                <section className="panel" id="recording-import" tabIndex={-1}>
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
                                  recordings.find(
                                    (r) => r.id === p.reference_id,
                                  )?.original_filename
                                }
                              </button>{" "}
                              · {label(p.identity_status)}
                              <PairCorrection
                                pair={p}
                                recordings={recordings}
                              />
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
                        {latestAnalysis && (
                          <button onClick={() => openHistory(latestAnalysis)}>
                            View latest analysis
                          </button>
                        )}
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
                            files. Corrections use a new dataset version;
                            approval is never automatic.
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
            </div>
          )}
          {page === "Analysis Workspace" && (
            <>
              <section
                className="panel recording-identities"
                aria-label="Selected recordings"
              >
                <h2>
                  {participant ? "Speech comparison" : "Reference inspection"}
                </h2>
                <p>
                  Reference:{" "}
                  <strong>
                    {reference?.original_filename ?? "Choose a recording"}
                  </strong>
                  {reference &&
                    ` · ${number(reference.normalized_info.duration_s, 3)} s`}
                </p>
                {participant && (
                  <p>
                    Participant:{" "}
                    <strong>{participant.original_filename}</strong> ·{" "}
                    {number(participant.normalized_info.duration_s, 3)} s
                  </p>
                )}
                <p role="status">
                  Processing:{" "}
                  {activeJob ? label(activeJob.state) : "Not started"}
                  {activeJob &&
                    ["queued", "running"].includes(activeJob.state) &&
                    ` · ${label(activeJob.stage)}`}
                </p>
              </section>
              {activeExploration && (
                <p className="hash meta">
                  Analysis {activeExploration.job_id} · dataset{" "}
                  {activeExploration.dataset_version} ·{" "}
                  {activeExploration.state}
                </p>
              )}
              {activeExploration && (
                <ExploratoryResult
                  report={activeExploration}
                  onSeek={seekObservation}
                  insights={
                    insights?.exploratory.job_id === activeExploration.job_id
                      ? insights
                      : null
                  }
                  assessment={activeReport}
                />
              )}
              {explorationLoading && (
                <p role="status">Loading exploratory measurements…</p>
              )}
              {activeExploration && !insights && !insightsError && (
                <p role="status">
                  {activeExploration.pair_id
                    ? "Loading comparative insights…"
                    : "Loading recording insights…"}
                </p>
              )}
              {activeExploration && insightsError && (
                <section
                  className="panel"
                  aria-label={
                    activeExploration.pair_id
                      ? "Comparative insight recovery"
                      : "Acoustic insight recovery"
                  }
                >
                  <p role="alert">
                    {insightsError} Raw exploratory evidence remains available.
                  </p>
                  <button onClick={() => setExplorationRetry((v) => v + 1)}>
                    {activeExploration.pair_id
                      ? "Retry comparative insights"
                      : "Retry recording insights"}
                  </button>
                </section>
              )}
              {activeJob && explorationError && (
                <section
                  className="panel"
                  aria-label="Exploratory measurement recovery"
                >
                  <p role="alert">{explorationError}</p>
                  <button onClick={() => setExplorationRetry((v) => v + 1)}>
                    Retry exploratory measurements
                  </button>
                </section>
              )}
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
                      id="participant-pair"
                      aria-label="Participant pair"
                      value={pair?.id ?? ""}
                      onChange={(event) => {
                        playback.current?.pause();
                        setSeek({});
                        setReportState(null);
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
              <h2 className="exploration-heading">
                Listen and explore evidence
              </h2>
              <p className="exploration-heading meta">
                Each recording keeps its own native clock. Reviewed
                correspondence is required for linked navigation.
              </p>
              <div className="print-controls">
                <button
                  onClick={() => {
                    setWorkspacePrintError("");
                    try {
                      printWorkspaceReport(
                        participant ? "paired" : "reference",
                      );
                    } catch {
                      setWorkspacePrintError(
                        "Browser printing could not open. Retry, or use the complete JSON exports.",
                      );
                    }
                  }}
                  disabled={!activeReport}
                >
                  Print workspace evidence
                </button>
                {activeReport && (
                  <p className="meta">
                    Workspace printing includes selected observations and
                    current charts. Start with Analysis Summary for a concise
                    report; Full Evidence Report retains all technical evidence.
                  </p>
                )}
              </div>
              {workspacePrintError && (
                <p role="alert" className="print-controls">
                  {workspacePrintError}
                </p>
              )}
              <p className="print-only workspace-print-note">
                Workspace view: selected observations and current native chart
                windows. Full inventories, methods and provenance remain in the
                separate Full Evidence Report and JSON. Charts are visual
                summaries; complete numerical measurements remain in the data
                exports.
              </p>
              {activeReport && (
                <p className="print-only">
                  {participant
                    ? "Participant comparison"
                    : "Reference inspection"}{" "}
                  · Processing: {activeJob?.state}. Analysis {activeJob?.id} ·
                  dataset {activeReport.dataset_version} ·{" "}
                  {activeReport.policy.version}. Machine processing does not
                  verify transcripts, reviewed evidence or accuracy.
                </p>
              )}
              {activeReport && !participant && (
                <section className="print-only reference-print-intro">
                  <h2>Reference audio analysis complete</h2>
                  <p>
                    Reference measurements only. No participant comparison was
                    run.
                  </p>
                  {referenceRequirements(activeReport).map((message) => (
                    <p key={message}>{message}</p>
                  ))}
                </section>
              )}
              {reference && participant && (
                <div
                  className="mobile-track-switch"
                  role="group"
                  aria-label="Audio track"
                >
                  <button
                    aria-pressed={audioTrack === "reference"}
                    onClick={() => {
                      playback.current?.pause();
                      setAudioTrack("reference");
                    }}
                  >
                    Reference audio
                  </button>
                  <button
                    aria-pressed={audioTrack === "participant"}
                    onClick={() => {
                      playback.current?.pause();
                      setAudioTrack("participant");
                    }}
                  >
                    Participant audio
                  </button>
                  <p className="meta">
                    Switching pauses playback. Each track keeps its own cursor
                    and selection.
                  </p>
                </div>
              )}
              <div
                className={`analysis-grid ${participant ? "comparison-analysis" : "reference-analysis"}`}
              >
                <div
                  className="timeline-stack"
                  data-audio-track={participant ? audioTrack : "reference"}
                >
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
                  {participant && (
                    <details className="panel correspondence-details">
                      <summary>
                        Reviewed correspondence and linked navigation
                      </summary>
                      <section className="panel native-correspondence">
                        <h2>Native-time correspondence</h2>
                        <p>
                          Each track retains its own seconds and cursor.
                          Selecting a grounded deviation seeks both tracks to
                          their corresponding intervals or boundary anchors.
                          Equal timestamps are never assumed.
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
                    </details>
                  )}
                  {activeReport && (
                    <details className="panel score-panel technical-details">
                      <summary>
                        {participant
                          ? "Technical details · scores, coverage and scientific exports"
                          : "Technical details · reference report exports"}
                      </summary>
                      {participant && <Scores report={activeReport!} />}
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
                    <Inspector
                      region={region}
                      report={activeReport}
                      referenceOnly={!participant}
                    />
                  </details>
                )}
              </div>
              {comparisonReport && (
                <Findings
                  report={comparisonReport}
                  onSelect={inspect}
                  onReplay={(item) => inspect(item, true)}
                />
              )}
              <h2 className="interactive-assessment-heading">
                {participant
                  ? "Verified Assessment"
                  : "Reference evidence and next steps"}
              </h2>
              <AnalysisResult
                job={activeJob}
                report={activeReport}
                loading={reportLoading}
                availablePairCount={availablePairs.length}
                reference={reference}
                participant={participant}
                referenceOnly={!participant}
                evaluations={evaluations}
                nextLabel={
                  !reference
                    ? "Import a reference"
                    : activeJob &&
                        ["queued", "running"].includes(activeJob.state)
                      ? "View processing controls"
                      : activeJob?.state === "completed" &&
                          !activeReport &&
                          !reportLoading
                        ? "Reload assessment evidence"
                        : !participant && activeJob?.state === "completed"
                          ? availablePairs.length
                            ? "Select a participant"
                            : "Add a participant"
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
                      : !participant && activeJob?.state === "completed"
                        ? availablePairs.length
                          ? document.getElementById("participant-pair")?.focus()
                          : (setParticipantFor(reference.id),
                            navigate("Recording Library"))
                        : hasAvailableDimensions
                          ? navigate("Rubric and Evidence")
                          : activeReport
                            ? navigate("Dataset and Evaluation")
                            : document.getElementById("analysis-setup")?.focus()
                }
              />
            </>
          )}
          {page === "Rubric and Evidence" && (
            <>
              {activeReport && !participant && (
                <p className="notice">
                  Reference inspection selected. Choose a participant in
                  Analysis Workspace before interpreting comparison scores.
                </p>
              )}
              <RubricGuide report={comparisonReport} />
              <details className="panel">
                <summary>
                  Technical details · thresholds, normalization and weighting
                </summary>
                <Rubric policy={policy} />
              </details>
              {comparisonReport && (
                <details className="panel">
                  <summary>
                    Technical details · selected comparison scores
                  </summary>
                  {participant && <Scores report={activeReport!} />}
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
              {activeExploration && (
                <p>
                  Exploratory measurements are available for the selected
                  analysis. They do not certify dataset or review readiness.{" "}
                  <button onClick={() => navigate("Analysis Workspace")}>
                    View exploratory measurements
                  </button>
                </p>
              )}
              <DatasetReadiness
                report={comparisonReport}
                summary={datasetSummary}
                loading={datasetState.phase === "loading"}
                state={datasetState}
                onRetry={() => void reloadDataset()}
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
              <details className="panel print-controls">
                <summary>Import independent review evidence</summary>
                <ReviewImport
                  jobs={jobs}
                  recordings={recordings}
                  onImported={() => void refresh()}
                />
              </details>
              <section className="panel">
                <h2>Persisted evaluation runs</h2>
                {evaluationState === "loading" && (
                  <p role="status">Loading persisted evaluation runs…</p>
                )}
                {evaluationState === "unavailable" && (
                  <p role="alert">
                    Evaluation inventory is unavailable. Reconnect / refresh to
                    retry; no zero-run count or accuracy result is established.
                  </p>
                )}
                {evaluationState !== "ready" && evaluations.length > 0 && (
                  <p className="meta">
                    Previously loaded runs are shown below; the current
                    evaluation inventory is not established.
                  </p>
                )}
                {evaluations.length > 0 && (
                  <p className="notice">
                    Stored runs preserve their original policy and metrics.
                    Evaluations created before exact-inventory-v1 may depend on
                    reviewer ordering. Recompute those runs with resolved
                    independent reviews before using their metrics as current
                    evidence; keep the original artifacts.
                  </p>
                )}
                {!evaluations.length && evaluationState === "ready" ? (
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
