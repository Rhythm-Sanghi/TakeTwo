import { ReviewJourney } from "./ReviewJourney";
import { useEffect, useRef, useState } from "react";
import { api, label, post } from "../api";
import type { components } from "../api.generated";
import type { Job, Pair, Recording, Review, Waveform } from "../api";
import { ReviewImport } from "./RecordingTools";

type Session = Omit<
  Required<components["schemas"]["ReviewSession"]>,
  "draft"
> & { draft: Draft };
type Draft = Required<components["schemas"]["ReviewDraft-Output"]>;
type Validation = components["schemas"]["ReviewValidation"];
type Grant = components["schemas"]["ReviewGrant"];
type Annotation = components["schemas"]["Label"];
type Inventory = {
  sessions: Session[];
  disagreements: {
    recording_id: string;
    scope: string;
    issue: string | null;
    reviews: Review[];
  }[];
  decisions: {
    id: string;
    created_at: string;
    explanation: string;
    resolution: string;
    status: string;
  }[];
};
const base = "/review-workspace";

function BoundaryComparison({ reviews }: { reviews: Review[] }) {
  const words = reviews.find((r) => r.words?.length)?.words ?? [];
  if (!words.length) return null;
  return (
    <div
      className="table-scroll"
      role="region"
      aria-label="Original and revised word boundary differences"
      tabIndex={0}
    >
      <table>
        <caption>
          Native boundaries in milliseconds. All originals/revisions are shown;
          consensus uses active reviews only.
        </caption>
        <thead>
          <tr>
            <th>Word</th>
            {reviews.map((r) => (
              <th key={r.id}>
                {r.reviewer_id} · {r.id}
              </th>
            ))}
            <th>Start / end spread (ms)</th>
          </tr>
        </thead>
        <tbody>
          {words.map((word, i) => {
            const starts = reviews.flatMap((r) =>
              r.words?.[i] ? [r.words[i].start_s] : [],
            );
            const ends = reviews.flatMap((r) =>
              r.words?.[i] ? [r.words[i].end_s] : [],
            );
            return (
              <tr key={i}>
                <th>
                  {i + 1}. {word.label}
                </th>
                {reviews.map((r) => (
                  <td key={r.id}>
                    {r.words?.[i]
                      ? `${(r.words[i].start_s * 1000).toFixed(0)}–${(r.words[i].end_s * 1000).toFixed(0)}`
                      : "Missing"}
                  </td>
                ))}
                <td>
                  {((Math.max(...starts) - Math.min(...starts)) * 1000).toFixed(
                    1,
                  )}{" "}
                  /{" "}
                  {((Math.max(...ends) - Math.min(...ends)) * 1000).toFixed(1)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
const categories = [
  "pause_behavior",
  "pacing",
  "energy_variation",
  "pitch_dynamics",
] as const;

function enter(grant: Grant) {
  window.location.assign(`/?review=${grant.session_id}#${grant.access_token}`);
}

export function ReviewWorkspace({
  recordings,
  jobs,
  pairs,
  initial,
}: {
  recordings: Recording[];
  jobs: Job[];
  pairs: Pair[];
  initial?: {
    recording_id: string;
    review_scope?: "transcript" | "timing" | "flaws" | null;
    job_id?: string | null;
  } | null;
}) {
  const [key, setKey] = useState("");
  const [rid, setRid] = useState(
    initial?.recording_id ?? recordings[0]?.id ?? "",
  );
  const [reviewer, setReviewer] = useState("");
  const [scope, setScope] = useState<"transcript" | "timing" | "flaws">(
    initial?.review_scope ?? "transcript",
  );
  const [jobId, setJobId] = useState(initial?.job_id ?? "");
  const [supersedes, setSupersedes] = useState("");
  const [inventory, setInventory] = useState<Inventory | null>(null);
  const [status, setStatus] = useState("");
  const [adjudicator, setAdjudicator] = useState("");
  const [explanation, setExplanation] = useState("");
  const [resolution, setResolution] = useState("");
  async function owner<T>(path: string, value?: unknown): Promise<T> {
    return api<T>(`${base}${path}`, {
      method: value === undefined ? "GET" : "POST",
      headers: { "X-Review-Operator": key, "Content-Type": "application/json" },
      ...(value === undefined ? {} : { body: JSON.stringify(value) }),
    });
  }
  async function action(work: () => Promise<void>) {
    try {
      await work();
    } catch (error) {
      setStatus((error as Error).message);
    }
  }
  return (
    <section className="panel review-tools">
      <h2>Prepare an independent handoff</h2>
      <p>
        Choose a recording, assign a review activity, then authorize an isolated
        reviewer handoff.
      </p>
      <p className="assignment-context">
        Recording to assign:{" "}
        <strong>
          {recordings.find((r) => r.id === rid)?.original_filename ??
            "None selected"}
        </strong>{" "}
        · {label(scope)} review
      </p>
      <label>
        Recording to review
        <select
          aria-label="Recording"
          value={rid}
          onChange={(e) => {
            setRid(e.target.value);
            setJobId("");
          }}
        >
          {recordings.map((r) => (
            <option key={r.id} value={r.id}>
              {r.original_filename} · {r.normalized_info.duration_s.toFixed(3)}{" "}
              s
            </option>
          ))}
        </select>
      </label>
      <label>
        Review activity
        <select
          aria-label="Review activity"
          value={scope}
          onChange={(e) => setScope(e.target.value as typeof scope)}
        >
          <option value="transcript">Independent transcript check</option>
          <option value="timing">Assisted word / phrase timing</option>
          <option value="flaws">Blinded flaw annotation</option>
        </select>
      </label>
      <label>
        Reviewer identifier
        <input
          aria-label="Reviewer identifier"
          aria-describedby="reviewer-identity-help"
          value={reviewer}
          onChange={(e) => setReviewer(e.target.value)}
          placeholder="Pseudonym agreed with the operator"
        />
        <span className="meta" id="reviewer-identity-help">
          An identity declaration, not authentication.
        </span>
      </label>
      {scope !== "flaws" && (
        <label>
          Original MFA suggestion artifact
          <select
            aria-label="Original MFA suggestion artifact"
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
          >
            <option value="">No alignment (transcript only)</option>
            {jobs
              .filter((j) => j.artifacts?.[rid]?.alignment)
              .map((j) => (
                <option key={j.id} value={j.id}>
                  {j.created_at} · {j.id}
                </option>
              ))}
          </select>
        </label>
      )}
      <details>
        <summary>Revise an existing review</summary>
        <label>
          Superseded review ID (revision only)
          <input
            value={supersedes}
            onChange={(e) => setSupersedes(e.target.value)}
          />
        </label>
      </details>
      <fieldset>
        <legend>Operator authorization</legend>{" "}
        <details>
          <summary>Operator key and private handoff instructions</summary>
          <p>
            Use a fresh private browser window for each reviewer. End handoff
            and close that window before viewing peer evidence. An active
            handoff opens its assigned reviewer session instead of the general
            workspace. Read the operator key from{" "}
            <code>.review-operator-key</code> in the active workspace. Keep it
            from reviewers. Starting a session blocks general APIs until the
            operator ends handoff, including after a restart.
          </p>
        </details>
        <label>
          Operator key
          <input
            type="password"
            autoComplete="off"
            value={key}
            onChange={(e) => setKey(e.target.value)}
          />
        </label>
      </fieldset>
      <p id="handoff-requirements" className="meta">
        {[
          !rid && "Choose a recording.",
          !reviewer.trim() && "Enter the reviewer’s declared identifier.",
          scope === "timing" &&
            !jobId &&
            "Choose an original alignment for timing review.",
          !key && "Provide the local operator key.",
        ]
          .filter(Boolean)
          .join(" ") ||
          "Ready to request a handoff; the backend validates authorization and assignment."}
      </p>
      <button
        aria-describedby="handoff-requirements"
        disabled={
          !key || !rid || !reviewer.trim() || (scope === "timing" && !jobId)
        }
        onClick={() =>
          void action(async () => {
            const grant = await owner<Grant>("/sessions", {
              recording_id: rid,
              reviewer_id: reviewer,
              scope,
              job_id: scope !== "flaws" ? jobId || null : null,
              pair_id:
                scope === "flaws"
                  ? (pairs.find((p) => p.participant_id === rid)?.id ?? null)
                  : null,
              supersedes: supersedes || null,
            });
            enter(grant);
          })
        }
      >
        Start reviewer handoff
      </button>
      <button
        disabled={!key}
        onClick={() =>
          void action(async () => {
            setInventory(await owner<Inventory>("/inventory"));
            setStatus(
              "Loaded operator inventory. Never show this view to independent reviewers.",
            );
          })
        }
      >
        Load sessions and adjudication
      </button>
      <p role="status">{status}</p>
      <details>
        <summary>Import an existing review file</summary>
        <ReviewImport
          jobs={jobs}
          recordings={recordings}
          onImported={() =>
            setStatus(
              "Review imported using the existing Phase 3 pipeline. Reload operator inventory to inspect it.",
            )
          }
        />
      </details>
      {inventory && (
        <>
          <h2>Saved sessions</h2>
          <ul>
            {inventory.sessions.map((s) => (
              <li key={s.id}>
                {recordings.find((r) => r.id === s.assignment.recording_id)
                  ?.original_filename ?? "Recording"}{" "}
                · {s.assignment.reviewer_id} · {s.assignment.scope} · {s.state}{" "}
                · {s.updated_at}
                <details>
                  <summary>Session uncertainty and provenance</summary>
                  <p>
                    {s.assisted_alignment
                      ? "MFA-assisted timing suggestions"
                      : "No alignment suggestions"}{" "}
                    · submitted {s.submitted_at ?? "not submitted"}
                  </p>
                  <p>
                    Uncertain word numbers:{" "}
                    {s.draft.uncertain_words.map((i) => i + 1).join(", ") ||
                      "None recorded"}
                  </p>
                  <p>
                    Unclear speech:{" "}
                    {s.draft.unclear_spans
                      .map(
                        (span) =>
                          `${span.start_s.toFixed(3)}–${span.end_s.toFixed(3)} s`,
                      )
                      .join(", ") || "None recorded"}
                  </p>
                  <p>{s.draft.notes}</p>
                  <p className="hash">
                    Audio {s.provenance.audio_sha256} · alignment{" "}
                    {s.alignment_sha256 ?? "not assigned"} · session integrity{" "}
                    {s.integrity_sha256}
                  </p>
                </details>
                <button
                  onClick={() =>
                    void action(async () =>
                      enter(await owner<Grant>(`/${s.id}/resume`, {})),
                    )
                  }
                >
                  Resume {s.assignment.reviewer_id} {s.assignment.scope}
                </button>
              </li>
            ))}
          </ul>
          <h2>Adjudication</h2>
          <p>
            Compare original submissions below. Decisions preserve originals and
            never override consensus. Disputes require each reviewer to inspect
            and submit an explicit superseding review. Assisted corrections are
            not an independent measurement of MFA accuracy.
          </p>
          <label>
            Adjudicator identifier
            <input
              value={adjudicator}
              onChange={(e) => setAdjudicator(e.target.value)}
            />
          </label>
          <label>
            Disagreement explanation
            <textarea
              value={explanation}
              onChange={(e) => setExplanation(e.target.value)}
            />
          </label>
          <label>
            Resolution and required reviewer revisions
            <textarea
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
            />
          </label>
          {inventory.disagreements.map((group) => (
            <section
              key={`${group.recording_id}-${group.scope}`}
              className="review-comparison"
            >
              <h3>
                {
                  recordings.find((r) => r.id === group.recording_id)
                    ?.original_filename
                }{" "}
                · {group.scope}
              </h3>
              <p>
                {group.issue ??
                  "Existing Phase 3 consensus agrees. Other eligibility gates still apply."}
              </p>
              {group.reviews.map((r) => (
                <details key={r.id}>
                  <summary>
                    {r.reviewer_id} · {r.decision} · {r.id}
                  </summary>
                  <p>{r.corrected_text}</p>
                  <p>{r.notes}</p>
                  <p>Evidence: {r.evidence_reference}</p>
                  <p>Supersedes: {r.supersedes ?? "Original submission"}</p>
                  {r.phrase_spans?.length ? (
                    <p>
                      Phrase word ranges:{" "}
                      {r.phrase_spans
                        .map(([a, b]) => `${a + 1}–${b}`)
                        .join(", ")}
                    </p>
                  ) : null}
                  <p>
                    Listened intervals:{" "}
                    {r.reviewed_spans
                      ?.map(
                        (s) =>
                          `${s.start_s.toFixed(3)}–${s.end_s.toFixed(3)} s`,
                      )
                      .join(", ") || "Not a flaw inventory"}
                  </p>
                  {r.scope === "flaws" && (
                    <ul>
                      {r.labels?.map((l) => (
                        <li key={l.id}>
                          {l.id} · {label(l.category)} · severity {l.severity} ·{" "}
                          {l.interval
                            ? `${l.interval.start_s.toFixed(3)}–${l.interval.end_s.toFixed(3)} s`
                            : `boundary ${l.anchor_s?.toFixed(3)} s`}{" "}
                          · uncertainty {l.uncertainty_s ?? "unknown"} s ·{" "}
                          {l.rationale}
                        </li>
                      ))}
                      {!r.labels?.length && (
                        <li>
                          No positive labels over the listed listening coverage.
                        </li>
                      )}
                    </ul>
                  )}
                </details>
              ))}
              {group.scope === "timing" && (
                <BoundaryComparison reviews={group.reviews} />
              )}
              <button
                disabled={
                  group.reviews.length < 2 ||
                  !adjudicator ||
                  !explanation ||
                  !resolution
                }
                onClick={() =>
                  void action(async () => {
                    await owner("/adjudications", {
                      recording_id: group.recording_id,
                      scope: group.scope,
                      review_ids: group.reviews.map((r) => r.id),
                      adjudicator_id: adjudicator,
                      explanation,
                      resolution,
                    });
                    setInventory(await owner<Inventory>("/inventory"));
                    setStatus(
                      "Adjudication recorded separately. No review or scientific gate was changed.",
                    );
                  })
                }
              >
                Record adjudication for {group.scope}
              </button>
            </section>
          ))}
          <h3>Decision history</h3>
          {inventory.decisions.map((d) => (
            <p key={d.id}>
              {d.created_at} · {d.status} · {d.explanation} · {d.resolution}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

export function Reviewer({ sessionId }: { sessionId: string }) {
  const [session, setSession] = useState<Session | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [validation, setValidation] = useState<Validation | null>(null);
  const [status, setStatus] = useState("Opening isolated reviewer session…");
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [wordIndex, setWordIndex] = useState(0);
  const [context, setContext] = useState(0.25);
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(1);
  const [view, setView] = useState<[number, number]>([0, 1]);
  const [waveform, setWaveform] = useState<Waveform | null>(null);
  const [category, setCategory] =
    useState<Annotation["category"]>("pause_behavior");
  const [severity, setSeverity] = useState<1 | 2 | 3>(1);
  const [notes, setNotes] = useState("");
  const [uncertainty, setUncertainty] = useState<number | null>(null);
  const [anchor, setAnchor] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [annotationId, setAnnotationId] = useState("");
  const [operator, setOperator] = useState("");
  const [token, setToken] = useState("");
  const audio = useRef<HTMLAudioElement>(null);
  const referenceAudio = useRef<HTMLAudioElement>(null);
  const last = useRef<number | null>(null);
  const inFlight = useRef(false);
  const editRevision = useRef(0);
  const playEnd = useRef<number | null>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const drag = useRef<"start" | "end" | "region" | null>(null);
  const path = `${base}/${sessionId}`;

  function received(s: Session, replaceDraft = false) {
    setSession(s);
    if (replaceDraft) {
      setDraft(s.draft);
      editRevision.current = s.edit_revision;
      setDirty(false);
    }
  }
  async function refreshValidation() {
    setValidation(await api<Validation>(`${path}/validation`));
  }
  async function action(work: () => Promise<void>) {
    setBusy(true);
    try {
      await work();
    } catch (error) {
      setStatus((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    let active = true;
    const accessToken = window.location.hash.slice(1);
    if (accessToken)
      window.history.replaceState(
        null,
        "",
        window.location.pathname + window.location.search,
      );
    const request = accessToken
      ? post<Session>(`${path}/activate`, { access_token: accessToken })
      : api<Session>(path);
    void request
      .then((s) => {
        if (active) {
          received(s, true);
          setEnd(s.duration_s);
          setView([0, s.duration_s]);
          setStatus("Draft loaded. Listen before confirming evidence.");
        }
      })
      .catch((e) => {
        if (active) setStatus(e.message);
      });
    return () => {
      active = false;
    };
  }, [path]);
  useEffect(() => {
    const protect = (event: BeforeUnloadEvent) => {
      if (dirty) event.preventDefault();
    };
    window.addEventListener("beforeunload", protect);
    return () => window.removeEventListener("beforeunload", protect);
  }, [dirty]);
  useEffect(() => {
    if (!session) return;
    let active = true;
    void api<Waveform>(
      `${path}/waveform?start_s=${view[0]}&end_s=${view[1]}&bins=1200`,
    )
      .then((w) => {
        if (active) setWaveform(w);
      })
      .catch((e) => {
        if (active) setStatus(e.message);
      });
    return () => {
      active = false;
    };
  }, [path, session?.id, view]);
  const word = draft?.words[wordIndex];
  const suggestion = session?.suggestions[wordIndex];
  useEffect(() => {
    const target = canvas.current;
    if (!target || !waveform) return;
    const draw = () => {
      target.width =
        Math.max(260, target.clientWidth) * window.devicePixelRatio;
      target.height = 150 * window.devicePixelRatio;
      const ctx = target.getContext("2d");
      if (!ctx) return;
      const x = (t: number) =>
        ((t - view[0]) / (view[1] - view[0])) * target.width;
      ctx.clearRect(0, 0, target.width, target.height);
      ctx.strokeStyle = "#235A50";
      ctx.beginPath();
      waveform.bins.forEach(([a, b, low, high]) => {
        const px = x((a + b) / 32000);
        ctx.moveTo(px, ((1 - high) * target.height) / 2);
        ctx.lineTo(px, ((1 - low) * target.height) / 2);
      });
      ctx.stroke();
      ctx.fillStyle = "#8B4D2230";
      ctx.fillRect(x(start), 0, x(end) - x(start), target.height);
      if (word) {
        ctx.strokeStyle = "#202824";
        [word.start_s, word.end_s].forEach((t) => {
          ctx.beginPath();
          ctx.moveTo(x(t), 0);
          ctx.lineTo(x(t), target.height);
          ctx.stroke();
        });
      }
      draft?.labels.forEach((l) => {
        const t = l.interval?.start_s ?? l.anchor_s ?? 0;
        ctx.fillStyle = "#202824";
        ctx.fillText(label(l.category), x(t), target.height - 8);
      });
    };
    draw();
    const observer = new ResizeObserver(draw);
    observer.observe(target);
    return () => observer.disconnect();
  }, [waveform, view, word, start, end, draft?.labels]);
  function change(next: Partial<Draft>) {
    if (draft) {
      setDraft({ ...draft, ...next });
      setDirty(true);
      setValidation(null);
      setStatus("Unsaved changes");
    }
  }
  function boundary(which: "start_s" | "end_s", value: number) {
    if (!draft || !word) return;
    change({
      words: draft.words.map((w, i) =>
        i === wordIndex ? { ...w, [which]: value } : w,
      ),
    });
  }
  async function save() {
    if (!session || !draft) return;
    audio.current?.pause();
    // Wait for an outstanding playback heartbeat before optimistic draft save.
    while (inFlight.current)
      await new Promise((resolve) => setTimeout(resolve, 25));
    const s = await post<Session>(`${path}/draft`, {
      revision: editRevision.current,
      draft,
    });
    received(s, true);
    await refreshValidation();
    setStatus("Draft saved locally.");
  }
  function replay(a: number, b: number) {
    if (!audio.current || !session) return;
    audio.current.currentTime = Math.max(0, a - context);
    last.current = null;
    playEnd.current = Math.min(session.duration_s, b + context);
    void audio.current.play().catch((e) => setStatus(e.message));
  }
  async function tick() {
    const player = audio.current;
    if (!player || (player.paused && !player.ended) || player.seeking) {
      last.current = null;
      return;
    }
    const t = player.currentTime;
    const previous = last.current;
    if (previous === null) {
      last.current = t;
      return;
    }
    if (
      (t - previous >= 0.2 || (player.ended && t > previous)) &&
      !inFlight.current &&
      session?.state === "draft"
    ) {
      last.current = t;
      if (t - previous < 2.5) {
        inFlight.current = true;
        try {
          received(
            await post<Session>(`${path}/listen`, {
              start_s: previous,
              end_s: t,
            }),
          );
        } catch (e) {
          // A rejected heartbeat must not silently discard observed playback.
          // Carry this continuous span into the next real timeupdate; seeking
          // or stopping still clears the cursor and the backend retains its gates.
          if (last.current === t && !player.seeking && !player.paused)
            last.current = previous;
          setStatus((e as Error).message);
        } finally {
          inFlight.current = false;
        }
      }
    }
    if (playEnd.current !== null && t >= playEnd.current) {
      player.pause();
      playEnd.current = null;
    }
  }
  function addLabel() {
    if (!draft) return;
    const item: Annotation = {
      id: annotationId.trim() || editing || `l-${crypto.randomUUID()}`,
      category,
      severity,
      interval: anchor ? null : { start_s: start, end_s: end },
      anchor_s: anchor ? start : null,
      rationale: notes,
      uncertainty_s: uncertainty,
    };
    change({
      labels: editing
        ? draft.labels.map((l) => (l.id === editing ? item : l))
        : [...draft.labels, item],
    });
    setEditing(null);
    setAnnotationId("");
    setNotes("");
  }
  const frozen = session?.state === "submitted";
  return (
    <>
      <header className="app-header">
        <div className="brand">
          <strong>TakeTwo</strong>
          <span>Speech analysis workspace</span>
        </div>
        <span>INDEPENDENT REVIEW HANDOFF</span>
      </header>
      <main className="review-shell" id="main">
        <h1>Review Workspace</h1>
        <p role="status" aria-live="polite">
          {status}
        </p>
        {!session && (
          <section className="panel">
            <label>
              Reviewer access token
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
            </label>
            <button
              onClick={() =>
                void action(async () => {
                  const s = await post<Session>(`${path}/activate`, {
                    access_token: token,
                  });
                  received(s, true);
                  setEnd(s.duration_s);
                  setView([0, s.duration_s]);
                  setToken("");
                  setStatus("Session opened.");
                })
              }
            >
              Open assigned session
            </button>
          </section>
        )}
        {session && draft && (
          <>
            <p>
              {session.recording_name} · {session.duration_s.toFixed(3)} s ·
              Reviewer {session.assignment.reviewer_id} ·{" "}
              {label(session.assignment.scope)} · {session.state}
            </p>
            <ReviewJourney
              scope={session.assignment.scope}
              dirty={dirty}
              busy={busy}
              submitted={frozen}
              validated={Boolean(validation?.can_submit)}
              issues={validation?.issues ?? []}
            />
            <details>
              <summary>Session provenance and assistance</summary>
              <p className="meta">
                Session {session.id} · revision {session.revision} · created{" "}
                {session.created_at} ·{" "}
                {session.assisted_alignment
                  ? "MFA-assisted inspection; suggestions are unverified"
                  : "No machine flaw predictions or scores exposed"}
              </p>
            </details>
            <p>
              Listen to the whole recording. Use your own judgment and notes.
              Playback telemetry records interaction, not comprehension or
              authenticated identity. Do not consult another reviewer, intended
              labels, scores or processing recipes.
            </p>
            <section className="panel" id="review-listen" tabIndex={-1}>
              <h2>Recording and native timeline</h2>
              <button
                onClick={() => {
                  if (audio.current) {
                    audio.current.currentTime = 0;
                    last.current = 0;
                    playEnd.current = null;
                    void audio.current
                      .play()
                      .catch((e) => setStatus(e.message));
                  }
                }}
              >
                Listen from beginning
              </button>
              {session.assignment.scope === "flaws" && (
                <>
                  <h3>Reference context</h3>
                  <audio
                    ref={referenceAudio}
                    controls
                    preload="metadata"
                    aria-label="Reference context playback"
                    src={`/api/v1${path}/reference-audio`}
                    onPlay={() => audio.current?.pause()}
                  />
                  <h3>Assigned participant</h3>
                </>
              )}
              <audio
                ref={audio}
                controls
                preload="metadata"
                aria-label="Assigned recording playback"
                src={`/api/v1${path}/audio`}
                onTimeUpdate={() => void tick()}
                onSeeking={() => {
                  last.current = null;
                }}
                onSeeked={() => {
                  last.current = audio.current?.currentTime ?? null;
                }}
                onEnded={() => {
                  void (async () => {
                    while (inFlight.current)
                      await new Promise((resolve) => setTimeout(resolve, 25));
                    await tick();
                  })();
                }}
                onPlay={() => {
                  referenceAudio.current?.pause();
                  last.current = audio.current?.currentTime ?? null;
                }}
              />
              <canvas
                ref={canvas}
                className="waveform review-waveform"
                role="img"
                aria-label="Native waveform with editable selection. Numeric controls below provide all actions."
                onPointerDown={(e) => {
                  if (frozen) return;
                  e.currentTarget.setPointerCapture(e.pointerId);
                  const rect = e.currentTarget.getBoundingClientRect();
                  const t =
                    view[0] +
                    ((e.clientX - rect.left) / rect.width) *
                      (view[1] - view[0]);
                  drag.current =
                    word &&
                    Math.abs(t - word.start_s) < (view[1] - view[0]) * 0.025
                      ? "start"
                      : word &&
                          Math.abs(t - word.end_s) < (view[1] - view[0]) * 0.025
                        ? "end"
                        : "region";
                  if (drag.current === "region") {
                    setStart(t);
                    setEnd(t);
                  }
                }}
                onPointerMove={(e) => {
                  if (!drag.current || frozen) return;
                  const rect = e.currentTarget.getBoundingClientRect();
                  const t = Math.max(
                    view[0],
                    Math.min(
                      view[1],
                      view[0] +
                        ((e.clientX - rect.left) / rect.width) *
                          (view[1] - view[0]),
                    ),
                  );
                  if (drag.current === "region") setEnd(t);
                  else
                    boundary(
                      drag.current === "start" ? "start_s" : "end_s",
                      Math.round(t * 1000) / 1000,
                    );
                }}
                onPointerUp={() => {
                  if (end < start) {
                    setStart(end);
                    setEnd(start);
                  }
                  drag.current = null;
                }}
              />
              <p className="mono">
                View {view[0].toFixed(3)}–{view[1].toFixed(3)} s · selection{" "}
                {(start * 1000).toFixed(0)}–{(end * 1000).toFixed(0)} ms
              </p>
              <div className="review-row">
                <label>
                  Selection start (ms)
                  <input
                    type="number"
                    min={0}
                    max={session.duration_s * 1000}
                    step={1}
                    value={Math.round(start * 1000)}
                    onChange={(e) => setStart(Number(e.target.value) / 1000)}
                  />
                </label>
                <label>
                  Selection end (ms)
                  <input
                    type="number"
                    min={0}
                    max={session.duration_s * 1000}
                    step={1}
                    value={Math.round(end * 1000)}
                    onChange={(e) => setEnd(Number(e.target.value) / 1000)}
                  />
                </label>
                <label>
                  Replay context (s)
                  <input
                    type="number"
                    min={0}
                    max={3}
                    step={0.05}
                    value={context}
                    onChange={(e) => setContext(Number(e.target.value))}
                  />
                </label>
              </div>
              <button
                onClick={() => replay(start, end)}
                disabled={end <= start}
              >
                Replay selection
              </button>
              <button
                disabled={end <= start}
                onClick={() => setView([start, end])}
              >
                Zoom to selection
              </button>
              <button onClick={() => setView([0, session.duration_s])}>
                Show whole recording
              </button>
              <label>
                Seek recording (s)
                <input
                  type="range"
                  min={0}
                  max={session.duration_s}
                  step={0.05}
                  defaultValue={0}
                  onChange={(e) => {
                    if (audio.current) {
                      audio.current.currentTime = Number(e.target.value);
                      last.current = null;
                    }
                  }}
                />
              </label>
            </section>
            <fieldset
              disabled={frozen || busy}
              className="panel"
              id="review-evidence"
              tabIndex={-1}
            >
              <legend>{label(session.assignment.scope)} evidence</legend>
              <details>
                <summary>Original supplied transcript</summary>
                <p>{session.original_text}</p>
              </details>
              {session.machine_text && (
                <details>
                  <summary>Machine-aligned spoken forms (unverified)</summary>
                  <p>{session.machine_text}</p>
                </details>
              )}
              {session.assignment.scope === "transcript" && (
                <>
                  <label>
                    Reviewer-corrected transcript
                    <textarea
                      rows={7}
                      value={draft.corrected_text}
                      onChange={(e) =>
                        change({ corrected_text: e.target.value })
                      }
                    />
                  </label>
                  <p>
                    Include missing words and repetitions; remove words not
                    spoken. Changes are stored separately. Changed word
                    sequences require a reviewed dataset revision and
                    regenerated alignment; no timing approval is inherited.
                  </p>
                  <button
                    disabled={end <= start}
                    onClick={() =>
                      change({
                        unclear_spans: [
                          ...draft.unclear_spans,
                          { start_s: start, end_s: end },
                        ],
                      })
                    }
                  >
                    Mark selection as unclear speech
                  </button>
                  {draft.unclear_spans.map((s, i) => (
                    <p key={i}>
                      Unclear: {s.start_s.toFixed(3)}–{s.end_s.toFixed(3)} s{" "}
                      <button
                        onClick={() =>
                          change({
                            unclear_spans: draft.unclear_spans.filter(
                              (_, j) => i !== j,
                            ),
                          })
                        }
                      >
                        Remove unclear span {i + 1}
                      </button>
                    </p>
                  ))}
                </>
              )}
              {session.assignment.scope !== "flaws" &&
                session.suggestions.length > 0 && (
                  <div
                    className="review-word-list"
                    aria-label="Machine word suggestions"
                  >
                    {session.suggestions.map((w, i) => (
                      <button
                        key={i}
                        aria-pressed={i === wordIndex}
                        onClick={() => {
                          setWordIndex(i);
                          setStart(w.start_s);
                          setEnd(w.end_s);
                          if (audio.current)
                            audio.current.currentTime = w.start_s;
                        }}
                      >
                        {i + 1}. {w.label} · {Math.round(w.start_s * 1000)}–
                        {Math.round(w.end_s * 1000)} ms
                      </button>
                    ))}
                  </div>
                )}
              {session.assignment.scope === "timing" && (
                <>
                  {!draft.words.length && (
                    <button
                      onClick={() =>
                        change({
                          words: session.suggestions.map((w) => ({ ...w })),
                        })
                      }
                    >
                      Load MFA suggestions for manual inspection
                    </button>
                  )}
                  <p>
                    Loading suggestions does not approve them. Listen, correct
                    and explicitly inspect each word. Neighboring words remain
                    in the list; overlapping boundaries are rejected when
                    saving.
                  </p>
                  <label>
                    Phrase end word numbers (comma separated, including last
                    word)
                    <input
                      defaultValue={draft.phrase_spans
                        .map((p) => p[1])
                        .join(", ")}
                      onBlur={(e) => {
                        let cursor = 0;
                        const spans = e.target.value
                          .split(",")
                          .filter((s) => s.trim())
                          .map((value) => {
                            const end = Number(value.trim());
                            const pair: [number, number] = [cursor, end];
                            cursor = end;
                            return pair;
                          });
                        change({ phrase_spans: spans });
                      }}
                    />
                  </label>
                  {word && suggestion && (
                    <>
                      <h3>
                        Word {wordIndex + 1}: {word.label}
                      </h3>
                      <p>
                        Original MFA suggestion:{" "}
                        {(suggestion.start_s * 1000).toFixed(0)}–
                        {(suggestion.end_s * 1000).toFixed(0)} ms ·{" "}
                        {session.inspected_words.includes(wordIndex)
                          ? "Inspected at saved boundary"
                          : "Needs inspection"}
                      </p>
                      <div className="review-row">
                        <label>
                          Word start (ms)
                          <input
                            type="number"
                            step={1}
                            value={Math.round(word.start_s * 1000)}
                            onChange={(e) =>
                              boundary("start_s", Number(e.target.value) / 1000)
                            }
                          />
                        </label>
                        <label>
                          Word end (ms)
                          <input
                            type="number"
                            step={1}
                            value={Math.round(word.end_s * 1000)}
                            onChange={(e) =>
                              boundary("end_s", Number(e.target.value) / 1000)
                            }
                          />
                        </label>
                      </div>
                      <button onClick={() => replay(word.start_s, word.end_s)}>
                        Replay selected word
                      </button>
                      <button
                        disabled={dirty}
                        onClick={() =>
                          void action(async () => {
                            audio.current?.pause();
                            while (inFlight.current)
                              await new Promise((resolve) =>
                                setTimeout(resolve, 25),
                              );
                            received(
                              await post<Session>(`${path}/inspect`, {
                                token_index: wordIndex,
                              }),
                            );
                            await refreshValidation();
                            setStatus("Saved boundary inspection.");
                          })
                        }
                      >
                        Mark saved boundary inspected
                      </button>
                      <label>
                        <input
                          type="checkbox"
                          checked={draft.uncertain_words.includes(wordIndex)}
                          onChange={(e) =>
                            change({
                              uncertain_words: e.target.checked
                                ? [...draft.uncertain_words, wordIndex]
                                : draft.uncertain_words.filter(
                                    (i) => i !== wordIndex,
                                  ),
                            })
                          }
                        />
                        Boundary uncertain
                      </label>
                    </>
                  )}
                </>
              )}
              {session.assignment.scope === "flaws" && (
                <>
                  <p>
                    Annotate only what you hear. Long/unexpected pauses use
                    intervals; missing/shortened pauses can use a boundary
                    anchor. No predictions, scores, recipes or intended
                    filenames are supplied.
                  </p>
                  <label>
                    Category
                    <select
                      aria-label="Category"
                      value={category}
                      onChange={(e) => {
                        setCategory(e.target.value as typeof category);
                        setAnchor(false);
                      }}
                    >
                      {categories.map((c) => (
                        <option key={c} value={c}>
                          {label(c)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Severity
                    <select
                      aria-label="Severity"
                      value={severity}
                      onChange={(e) =>
                        setSeverity(Number(e.target.value) as 1 | 2 | 3)
                      }
                    >
                      <option value={1}>1 · mild</option>
                      <option value={2}>2 · moderate</option>
                      <option value={3}>3 · severe</option>
                    </select>
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      disabled={category !== "pause_behavior"}
                      checked={anchor}
                      onChange={(e) => setAnchor(e.target.checked)}
                    />
                    Missing / shortened pause boundary event (selection start)
                  </label>
                  <label>
                    Annotation rationale
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </label>
                  <label>
                    Annotation identifier (optional; explicit for reconciled
                    revisions)
                    <input
                      value={annotationId}
                      onChange={(e) => setAnnotationId(e.target.value)}
                    />
                  </label>
                  <label>
                    Timing uncertainty (s)
                    <input
                      type="number"
                      min={0}
                      step={0.01}
                      value={uncertainty ?? ""}
                      onChange={(e) =>
                        setUncertainty(
                          e.target.value === "" ? null : Number(e.target.value),
                        )
                      }
                    />
                  </label>
                  <button
                    disabled={!notes.trim() || (!anchor && end <= start)}
                    onClick={addLabel}
                  >
                    {editing ? "Update annotation" : "Add annotation"}
                  </button>
                  <ul>
                    {draft.labels.map((l, index) => (
                      <li key={l.id}>
                        {label(l.category)} · severity {l.severity} ·{" "}
                        {l.interval
                          ? `${l.interval.start_s.toFixed(3)}–${l.interval.end_s.toFixed(3)} s`
                          : `boundary ${l.anchor_s?.toFixed(3)} s`}{" "}
                        · uncertainty {l.uncertainty_s ?? "unspecified"} s ·{" "}
                        {l.rationale}
                        <button
                          onClick={() => {
                            setEditing(l.id);
                            setAnnotationId(l.id);
                            setCategory(l.category);
                            setSeverity(l.severity);
                            setNotes(l.rationale);
                            setAnchor(l.anchor_s != null);
                            setStart(l.interval?.start_s ?? l.anchor_s ?? 0);
                            setEnd(l.interval?.end_s ?? l.anchor_s ?? 0);
                            setUncertainty(l.uncertainty_s ?? null);
                          }}
                        >
                          Edit annotation {index + 1}
                        </button>
                        <button
                          onClick={() =>
                            change({
                              labels: draft.labels.filter(
                                (item) => item.id !== l.id,
                              ),
                            })
                          }
                        >
                          Delete annotation {index + 1}
                        </button>
                      </li>
                    ))}
                  </ul>
                </>
              )}
              <section id="review-notes" tabIndex={-1}>
                <h2>Notes and uncertainty</h2>
                <label>
                  Evidence reference
                  <input
                    value={draft.evidence_reference}
                    onChange={(e) =>
                      change({ evidence_reference: e.target.value })
                    }
                    placeholder="Your private listening worksheet / session reference"
                  />
                </label>
                <label>
                  Listening notes and uncertainty
                  <textarea
                    value={draft.notes}
                    onChange={(e) => change({ notes: e.target.value })}
                  />
                </label>
                <label>
                  Review decision
                  <select
                    aria-label="Review decision"
                    value={draft.decision}
                    onChange={(e) =>
                      change({ decision: e.target.value as Draft["decision"] })
                    }
                  >
                    <option value="unresolved">Unresolved</option>
                    <option value="rejected">Rejected</option>
                    <option value="approved">Approved after inspection</option>
                  </select>
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={draft.independent}
                    onChange={(e) => change({ independent: e.target.checked })}
                  />
                  I performed my own review, did not review my own performance,
                  and did not consult peer decisions.
                </label>
                {session.assignment.scope === "flaws" && (
                  <label>
                    <input
                      type="checkbox"
                      checked={draft.blinded_to_predictions}
                      onChange={(e) =>
                        change({ blinded_to_predictions: e.target.checked })
                      }
                    />
                    I did not inspect machine predictions, scores, intended
                    labels or recipes.
                  </label>
                )}
              </section>
            </fieldset>
            <section className="panel" id="review-submit" tabIndex={-1}>
              <h2>Progress and submission</h2>
              <p>
                {session.listened_spans
                  .reduce((sum, s) => sum + s.end_s - s.start_s, 0)
                  .toFixed(2)}{" "}
                / {session.duration_s.toFixed(2)} s playback observed ·{" "}
                {session.inspected_words.length} word boundaries inspected
              </p>
              <p>
                Unsaved changes: {dirty ? "yes" : "no"}. No automatic submission
                or approval.
              </p>
              <button
                disabled={busy || frozen}
                onClick={() => void action(save)}
              >
                Save draft
              </button>
              <button
                disabled={dirty || busy}
                onClick={() => void action(refreshValidation)}
              >
                Check completion
              </button>
              {validation && (
                <>
                  <ul>
                    {validation.issues.map((issue, i) => (
                      <li key={i}>{issue}</li>
                    ))}
                  </ul>
                  {validation.alignment_needs_regeneration && (
                    <p role="alert">
                      Corrected words differ: timing needs regeneration in a
                      reviewed dataset version.
                    </p>
                  )}
                  <p>{validation.scientific_notice}</p>
                </>
              )}
              <button
                disabled={dirty || busy || frozen || !validation?.can_submit}
                onClick={() =>
                  void action(async () => {
                    audio.current?.pause();
                    received(
                      await post<Session>(`${path}/submit`, {
                        revision: editRevision.current,
                        draft,
                      }),
                      true,
                    );
                    setStatus(
                      "Submitted assertion saved. Original machine artifacts and scientific gates are unchanged.",
                    );
                  })
                }
              >
                Submit review
              </button>
              {frozen && (
                <a href={`/api/v1${path}/export`} download>
                  Export scientific Review JSON
                </a>
              )}
              <a
                href={`/api/v1${path}/summary`}
                target="_blank"
                rel="noreferrer"
              >
                Open session summary / draft provenance
              </a>
            </section>
          </>
        )}
        <details className="panel">
          <summary>Operator: end handoff</summary>
          <p>
            Close the reviewer window and clear its storage after handoff. Do
            not expose peer evidence to a reviewer awaiting independent work.
          </p>
          <label>
            Local operator key
            <input
              type="password"
              value={operator}
              onChange={(e) => setOperator(e.target.value)}
            />
          </label>
          <button
            disabled={dirty}
            onClick={() =>
              void action(async () => {
                await post(`${base}/unlock`, { operator_key: operator });
                window.location.assign("/");
              })
            }
          >
            End handoff and return to operator
          </button>
        </details>
      </main>
    </>
  );
}

export function ReviewEntry({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<{ active_session: string | null } | null>(
    null,
  );
  const [error, setError] = useState("");
  useEffect(() => {
    void api<{ active_session: string | null }>(`${base}/mode`)
      .then(setMode)
      .catch((e) => setError(e.message));
  }, []);
  const sid =
    new URLSearchParams(window.location.search).get("review") ??
    mode?.active_session;
  if (!mode)
    return (
      <main>
        <h1>TakeTwo</h1>
        <p role="status">{error || "Opening local workspace…"}</p>
      </main>
    );
  return sid ? <Reviewer sessionId={sid} /> : children;
}
