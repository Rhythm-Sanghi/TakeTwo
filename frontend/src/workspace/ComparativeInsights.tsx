import { useState } from "react";
import { label, number } from "../api";
import type { ComparativeReport } from "../api";

type Seek = (
  recording: string,
  start: number,
  end?: number,
  play?: boolean,
) => void;

export function ComparativeInsights({
  report,
  onSeek,
}: {
  report: ComparativeReport;
  onSeek: Seek;
}) {
  const [all, setAll] = useState(false);
  const e = report.exploratory;
  const reference = e.recordings.find((r) => r.recording_id === e.reference_id);
  const participant = e.recordings.find(
    (r) => r.recording_id !== e.reference_id,
  );
  const shown = all
    ? report.inspection_order
    : report.inspection_order.slice(0, report.config.initial_items);
  const listen = (rid: string, start: number, end: number, name: string) => (
    <button onClick={() => onSeek(rid, start, end, true)}>
      Listen to {name}
    </button>
  );
  const interval = (start: number, end: number) =>
    `${number(start, 2)}–${number(end, 2)} s`;
  return (
    <div className="comparative-insights">
      <p className="eyebrow">
        {e.pair_id
          ? "Automatic comparative insights"
          : "Automatic acoustic inspection"}{" "}
        · {report.config.method} · unverified
      </p>
      <h2>What analysis found</h2>
      {e.comparison ? (
        <>
          <h3>Overall recording comparison</h3>
          <p>{e.comparison.interpretation}</p>
          <p>
            {e.comparison.rms_level_delta_db == null
              ? "The digital RMS difference is unavailable."
              : `${Math.abs(e.comparison.rms_level_delta_db) < 0.1 ? "Small measured" : "Measured"} digital RMS difference: ${number(e.comparison.rms_level_delta_db, 3)} dB; no perceptual significance is established.`}{" "}
            Activity support difference {number(report.activity_delta_s, 3)} s;
            low-energy support difference {number(report.low_energy_delta_s, 3)}{" "}
            s.
          </p>
        </>
      ) : (
        <p>
          {e.pair_id
            ? "Only partial measurements are available; paired differences are withheld."
            : "Reference inspection uses one native recording timeline."}
        </p>
      )}
      <p>
        {report.groups.length} grouped observations retain all{" "}
        {e.candidates.length} raw acoustic windows.
        {e.pair_id && (
          <>
            {" "}
            {report.segments.filter((s) => s.kind === "word").length}{" "}
            provisional paired word measurements; {report.anomalies.length}{" "}
            alignment {report.anomalies.length === 1 ? "anomaly" : "anomalies"}.
          </>
        )}{" "}
        Counts describe observations, not speaking mistakes.
      </p>
      {e.pair_id && report.correspondence_unavailable_reason && (
        <p>{report.correspondence_unavailable_reason}</p>
      )}
      <p className="notice">
        Interpretation limits: Automatic observations are unverified, not
        delivery flaws. Supplied-text timings do not verify spoken words or
        alignment accuracy. Digital energy depends on gain, microphone and
        noise. Inspection order is not severity or confidence.
      </p>
      <p className="meta">
        Accepted pitch-frame coverage:{" "}
        {e.recordings
          .map(
            (r) =>
              `${r.filename} ${r.accepted_pitch_fraction == null ? "unavailable" : number(r.accepted_pitch_fraction * 100, 2) + "%"}`,
          )
          .join("; ")}
        . Coverage is not timing or pitch accuracy; pitch eligibility remains
        separately gated.
      </p>
      <h3>
        {e.pair_id
          ? "Differences worth inspecting"
          : "Recording observations worth inspecting"}
      </h3>
      <p className="local-comparison">
        {e.pair_id
          ? `Local differences worth inspecting: ${report.anomalies.length} provisional alignment ${report.anomalies.length === 1 ? "anomaly" : "anomalies"}; ${report.inspection_order.filter((i) => i.category === "gap_difference").length} word-gap and ${report.inspection_order.filter((i) => i.category === "word_duration").length} word-duration differences meet the inspection rules. Acoustic groups describe within-recording energy observations.`
          : "These are measured observations on one recording's native timeline; they describe no paired delivery difference."}
      </p>
      <p>
        <strong>Recommended inspection: </strong>Use the native replay controls
        on each selected item, then check provisional text and waveform/energy
        evidence. Each passage keeps its own clock; the listening questions
        below guide inspection without prescribing a judgment.
      </p>
      <p className="inspection-count">
        {shown.length
          ? `Showing ${shown.length} of ${report.inspection_order.length} inspection items. Complete support comes first, then alignment anomalies, gap differences, word-duration differences and acoustic groups; larger durations first within each category.`
          : e.pair_id
            ? "No supported local differences meet the inspection rules. This is not a delivery assessment."
            : "No supported recording observations meet the inspection rules. Absence of observations does not establish perfect delivery."}
      </p>
      <p className="print-only report-selection">
        Selected for inspection: first {Math.min(3, shown.length)} of{" "}
        {report.inspection_order.length} ordered items; full measurements follow
        in the appendix and JSON. Complete support precedes limited evidence;
        anomalies, gap differences, word duration and groups follow in that
        order, with larger measured durations first.
      </p>
      <ul className="insight-list">
        {shown.map((item, index) => {
          const group = report.groups.find((g) => g.id === item.evidence_id);
          const anomaly = report.anomalies.find(
            (a) => a.id === item.evidence_id,
          );
          const segment = report.segments.find(
            (s) => s.id === item.evidence_id,
          );
          const paired =
            segment ??
            (anomaly &&
              report.segments.find(
                (s) =>
                  s.kind === "word" &&
                  s.token_start === anomaly.before_token_index + 1,
              ));
          const gapMode =
            item.category === "gap_difference" || Boolean(anomaly);
          const leftStart = paired
            ? ((anomaly
                ? reference?.automatic_alignment?.words.find(
                    (w) => w.token_index === anomaly.before_token_index,
                  )?.start_s
                : undefined) ??
              paired.reference.start_s -
                (gapMode ? (paired.reference_gap_before_s ?? 0) : 0))
            : 0;
          const rightStart = paired
            ? ((anomaly
                ? participant?.automatic_alignment?.words.find(
                    (w) => w.token_index === anomaly.before_token_index,
                  )?.start_s
                : undefined) ??
              paired.participant.start_s -
                (gapMode ? (paired.participant_gap_before_s ?? 0) : 0))
            : 0;
          const recording = e.recordings.find(
            (r) =>
              r.recording_id === (group?.recording_id ?? anomaly?.recording_id),
          );
          const selectionReason =
            item.order_reason
              .split(
                /Complete native support without recording quality warnings\.|Quality\/support limited; shown after complete evidence\./,
              )[0]
              .trim() || item.order_reason;
          return (
            <li key={item.id} data-evidence-id={item.evidence_id}>
              <p className="eyebrow insight-category">
                {anomaly
                  ? "Alignment anomalies"
                  : segment
                    ? "Provisional timing and word-gap differences"
                    : group?.direction === "low_energy"
                      ? "Low-energy intervals"
                      : "Energy-change observations"}
                {item.quality_limited && " · recording-quality limitations"}
                {index < 3 && " · selected for inspection"}
              </p>
              <h4>
                {anomaly
                  ? `Inspect alignment: ${anomaly.before_word.label} → ${anomaly.after_word.label}`
                  : segment
                    ? `${item.category === "gap_difference" ? "Gap before" : "Word duration"}: ${segment.text}`
                    : group
                      ? `${label(group.kind)} · ${recording?.filename}`
                      : "Evidence unavailable"}
              </h4>
              {anomaly && (
                <>
                  <p>
                    {recording?.filename}: {anomaly.before_word.label}{" "}
                    {interval(
                      anomaly.before_word.start_s,
                      anomaly.before_word.end_s,
                    )}{" "}
                    → {anomaly.after_word.label}{" "}
                    {interval(
                      anomaly.after_word.start_s,
                      anomaly.after_word.end_s,
                    )}
                    .
                  </p>
                  <p>
                    Machine gap{" "}
                    {number(anomaly.gap.end_s - anomaly.gap.start_s, 3)} s.
                    Independently measured low-energy support in that gap:{" "}
                    {number(anomaly.measurement.low_energy_s, 3)} s /{" "}
                    {number(anomaly.measurement.observed_s, 3)} s observed.{" "}
                    {anomaly.measurement.complete
                      ? "Complete frame support."
                      : "Incomplete frame support; remaining activity is unknown."}{" "}
                    A gap is not proof of quiet or a pause.
                  </p>
                  <p>
                    {anomaly.measurement.complete &&
                    anomaly.measurement.low_energy_s === 0
                      ? "The acoustic activity measurement does not identify this interval as low-energy silence. Check the supplied text and automatic timing against the recording; activity can include noise."
                      : "Compare the provisional gap with independently measured activity; uncovered time remains unknown."}
                  </p>
                </>
              )}
              {segment && (
                <p>
                  {item.category === "gap_difference"
                    ? `Participant minus reference gap: ${number(segment.gap_delta_s, 3)} s (reference ${number(segment.reference_gap_before_s, 3)} s, participant ${number(segment.participant_gap_before_s, 3)} s).`
                    : `Participant minus reference word duration: ${number(segment.duration_delta_s, 3)} s (${number(segment.relative_duration_delta_percent, 1)}%). This is a machine boundary difference, not a pronunciation judgment.`}
                </p>
              )}
              {paired && reference && participant && (
                <>
                  <p>
                    Reference {interval(leftStart, paired.reference.end_s)} ·
                    participant {interval(rightStart, paired.participant.end_s)}
                    . Each plays its own native interval.
                  </p>
                  <div className="toolbar">
                    {listen(
                      reference.recording_id,
                      leftStart,
                      paired.reference.end_s,
                      "reference",
                    )}
                    {listen(
                      participant.recording_id,
                      rightStart,
                      paired.participant.end_s,
                      "participant",
                    )}
                    <button
                      onClick={() =>
                        onSeek(
                          reference.recording_id,
                          leftStart,
                          paired.reference.end_s,
                        )
                      }
                    >
                      Inspect reference waveform
                    </button>
                    <button
                      onClick={() =>
                        onSeek(
                          participant.recording_id,
                          rightStart,
                          paired.participant.end_s,
                        )
                      }
                    >
                      Inspect participant waveform
                    </button>
                  </div>
                </>
              )}
              {anomaly &&
                !paired &&
                recording &&
                listen(
                  recording.recording_id,
                  anomaly.context.start_s,
                  anomaly.context.end_s,
                  recording.filename,
                )}
              {group && (
                <>
                  <p>
                    {interval(group.start_s, group.end_s)} ·{" "}
                    {group.candidate_ids.length} connected{" "}
                    {group.candidate_ids.length === 1 ? "window" : "windows"} ·{" "}
                    {label(group.direction)}
                    {group.representative_delta_db == null
                      ? ""
                      : ` · median supporting change ${number(group.representative_delta_db, 2)} dB (${group.delta_range_db.map((v) => number(v, 2)).join(" to ")})`}
                    . No cause or delivery error is established.
                  </p>
                  <div className="toolbar">
                    {listen(
                      group.recording_id,
                      group.start_s,
                      group.end_s,
                      recording?.role ?? "recording",
                    )}
                    <button
                      onClick={() =>
                        onSeek(group.recording_id, group.start_s, group.end_s)
                      }
                    >
                      Inspect grouped interval
                    </button>
                  </div>
                </>
              )}
              <p className="selection-reason">
                <strong>Why inspect: </strong>
                {selectionReason}
              </p>
              <p className="listening-question">
                <strong>Listen for: </strong>
                {anomaly
                  ? "Do the supplied-text words and assigned timing correspond to the audible passage? A possible alignment or transcript mismatch still needs checking."
                  : segment
                    ? item.category === "gap_difference"
                      ? "Is the interval before this supplied-text word different in the two passages, and do the assigned boundaries fit what you hear? Timing alone does not establish hesitation."
                      : "Do the assigned word start and end fit the audible passage in each recording? A duration difference does not establish pronunciation quality."
                    : group?.direction === "low_energy"
                      ? "What is audible in this measured low-energy interval? Quiet energy does not by itself identify silence or a delivery flaw."
                      : "Is a digital-level change audible within this interval? Gain, microphone and noise can contribute; emphasis and cause are unestablished."}
              </p>
              <p className="print-only hash">
                Evidence reference: {item.evidence_id}
              </p>
              {anomaly && (
                <details className="print-controls">
                  <summary>Inspect provisional transcript</summary>
                  <p>Supplied text and machine boundaries remain unverified.</p>
                  {e.recordings.map((r) => (
                    <p key={r.recording_id}>
                      {r.filename}:{" "}
                      {r.automatic_alignment?.words
                        .filter(
                          (w) =>
                            w.token_index != null &&
                            w.token_index >= anomaly.before_token_index - 1 &&
                            w.token_index <= anomaly.before_token_index + 2,
                        )
                        .map(
                          (w) => `${w.label} [${interval(w.start_s, w.end_s)}]`,
                        )
                        .join(" · ") || "No automatic word timing available."}
                    </p>
                  ))}
                </details>
              )}
              <details>
                <summary>Inspect evidence and selection reason</summary>
                {selectionReason !== item.order_reason && (
                  <p>{item.order_reason}</p>
                )}
                {anomaly && <p>{anomaly.reason}</p>}
                {paired && (
                  <>
                    <p>{paired.limitation}</p>
                    <p>
                      Reference / participant median energy:{" "}
                      {number(
                        paired.reference_measurements.median_energy_dbfs,
                        2,
                      )}{" "}
                      /{" "}
                      {number(
                        paired.participant_measurements.median_energy_dbfs,
                        2,
                      )}{" "}
                      dBFS; within-recording relative energy delta{" "}
                      {number(paired.relative_energy_delta_db, 2)} dB.
                      Confidence unavailable.
                    </p>
                  </>
                )}
                {group && (
                  <>
                    <p>
                      {group.limitation} Boundary resolution{" "}
                      {group.detection.boundary_resolution_s} s; frame window{" "}
                      {group.detection.frame_window_s} s;{" "}
                      {group.detection.method}.
                    </p>
                    <p>Raw window IDs: {group.candidate_ids.join(", ")}</p>
                    <details>
                      <summary>Every contributing raw measurement</summary>
                      {e.candidates
                        .filter((c) => group.candidate_ids.includes(c.id))
                        .map((c) => (
                          <pre className="raw-measurement" key={c.id}>
                            {JSON.stringify(c, null, 2)}
                          </pre>
                        ))}
                    </details>
                    <p>
                      Threshold{" "}
                      {group.detection.threshold_delta_db == null
                        ? number(group.detection.threshold_dbfs, 2) +
                          " dBFS (or absolute floor)"
                        : number(group.detection.threshold_delta_db, 2) +
                          " dB change"}
                      ; median energy range{" "}
                      {group.median_energy_range_dbfs
                        .map((v) => number(v, 2))
                        .join(" to ")}{" "}
                      dBFS.
                    </p>
                  </>
                )}
              </details>
            </li>
          );
        })}
      </ul>
      {report.inspection_order.length > report.config.initial_items && (
        <button className="print-controls" onClick={() => setAll((v) => !v)}>
          {all
            ? "Show selected inspection items"
            : `Show all ${report.inspection_order.length} inspection items`}
        </button>
      )}
      <div className="toolbar print-controls">
        {e.recordings.map((r) => (
          <button
            key={r.recording_id}
            onClick={() => onSeek(r.recording_id, 0)}
          >
            Return to complete {r.role} recording
          </button>
        ))}
      </div>
      <details className="comparative-appendix">
        <summary>
          {e.pair_id
            ? "Comparative evidence — all groups and provisional measurements"
            : "Single-recording evidence — all grouped observations"}
        </summary>
        <h3>Technical appendix · comparative-insights-v1</h3>
        {e.pair_id && (
          <p>
            {report.phrase_unavailable_reason ??
              "Phrase identities use a common independently reviewed partition; native acoustic boundaries remain provisional."}
          </p>
        )}
        <p className="hash">
          Exploratory SHA-256: {report.exploratory_sha256} · comparative
          implementation: {report.implementation_sha256} · phrase review hashes:{" "}
          {(report.phrase_review_sha256 ?? []).join(", ") || "None"}
        </p>
        {report.anomalies.length > 0 && (
          <div className="table-scroll">
            <table>
              <caption>
                Complete provisional alignment anomaly inventory
              </caption>
              <thead>
                <tr>
                  <th>Recording / supplied words</th>
                  <th>Native gap / replay context</th>
                  <th>Observed / low-energy support</th>
                  <th>Interpretation limit</th>
                </tr>
              </thead>
              <tbody>
                {report.anomalies.map((a) => (
                  <tr key={a.id}>
                    <td>
                      {
                        e.recordings.find(
                          (r) => r.recording_id === a.recording_id,
                        )?.filename
                      }
                      : {a.before_word.label} → {a.after_word.label}
                      <br />
                      <span className="hash">{a.id}</span>
                    </td>
                    <td>
                      {interval(a.gap.start_s, a.gap.end_s)} (
                      {number(a.gap.end_s - a.gap.start_s, 3)} s)
                      <br />
                      {interval(a.context.start_s, a.context.end_s)}
                    </td>
                    <td>
                      {number(a.measurement.observed_s, 3)} /{" "}
                      {number(a.measurement.low_energy_s, 3)} s;{" "}
                      {a.measurement.complete ? "complete" : "incomplete"} frame
                      support
                    </td>
                    <td>{a.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="table-scroll">
          <table>
            <caption>Complete grouped observation inventory</caption>
            <thead>
              <tr>
                <th>Recording / category</th>
                <th>Native interval</th>
                <th>Windows</th>
                <th>Measured change / range</th>
              </tr>
            </thead>
            <tbody>
              {report.groups.map((g) => (
                <tr key={g.id}>
                  <td>
                    {
                      e.recordings.find(
                        (r) => r.recording_id === g.recording_id,
                      )?.filename
                    }{" "}
                    / {label(g.kind)} / {label(g.direction)}
                    <br />
                    <span className="hash">{g.id}</span>
                  </td>
                  <td>{interval(g.start_s, g.end_s)}</td>
                  <td>
                    {g.candidate_ids.length}
                    <details>
                      <summary>Raw window links</summary>
                      {g.candidate_ids.map((id) => (
                        <p className="hash" key={id}>
                          {id}
                        </p>
                      ))}
                    </details>
                  </td>
                  <td>
                    {g.representative_delta_db == null
                      ? "Low-energy support"
                      : `${number(g.representative_delta_db, 2)} dB · ${g.delta_range_db.map((v) => number(v, 2)).join(" to ")}`}
                    <button
                      onClick={() =>
                        onSeek(g.recording_id, g.start_s, g.end_s, true)
                      }
                    >
                      Replay group
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <table className="print-only group-provenance">
          <caption>Group-to-source window provenance</caption>
          <thead>
            <tr>
              <th>Grouped observation ID</th>
              <th>Every contributing raw window ID</th>
            </tr>
          </thead>
          <tbody>
            {report.groups.map((g) => (
              <tr key={g.id}>
                <td>
                  <span className="evidence-reference">{g.id}</span>
                </td>
                <td>
                  {g.candidate_ids.map((id) => (
                    <span className="evidence-reference" key={id}>
                      {id}{" "}
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {report.segments.length > 0 ? (
          <div className="table-scroll">
            <table>
              <caption>
                Complete provisional paired word / phrase measurements
              </caption>
              <thead>
                <tr>
                  <th>Supplied text</th>
                  <th>Reference / participant native time</th>
                  <th>Duration delta</th>
                  <th>Gap delta / relative energy delta</th>
                </tr>
              </thead>
              <tbody>
                {report.segments.map((s) => (
                  <tr key={s.id}>
                    <td>
                      {s.token_start + 1} · {s.text} ({s.kind})
                      <br />
                      <span className="hash">{s.id}</span>
                    </td>
                    <td>
                      {interval(s.reference.start_s, s.reference.end_s)} /{" "}
                      {interval(s.participant.start_s, s.participant.end_s)}
                      {reference && participant && (
                        <div className="toolbar print-controls">
                          {listen(
                            reference.recording_id,
                            s.reference.start_s,
                            s.reference.end_s,
                            `reference ${s.kind}`,
                          )}
                          {listen(
                            participant.recording_id,
                            s.participant.start_s,
                            s.participant.end_s,
                            `participant ${s.kind}`,
                          )}
                        </div>
                      )}
                    </td>
                    <td>{number(s.duration_delta_s, 3)} s</td>
                    <td>
                      {number(s.gap_delta_s, 3)} s /{" "}
                      {number(s.relative_energy_delta_db, 2)} dB
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : e.pair_id ? (
          <p>
            No paired segment measurements are available for this inspection.
          </p>
        ) : null}
        <ul>
          {report.limitations.map((l) => (
            <li key={l}>
              {e.pair_id ? l : l.replace("All comparisons", "All observations")}
            </li>
          ))}
        </ul>
      </details>
      <a
        className="print-controls"
        href={`/api/v1/analyses/${e.job_id}/insights/export`}
      >
        {e.pair_id
          ? "Export comparative JSON"
          : "Export single-recording insights JSON"}
      </a>
    </div>
  );
}
