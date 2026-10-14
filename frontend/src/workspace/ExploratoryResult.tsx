import { label, number } from "../api";
import { useState } from "react";
import type { AcousticCandidate, ExploratoryReport, Report } from "../api";
import { evidenceRequirement } from "./AnalysisResult";
import { ComparativeInsights } from "./ComparativeInsights";
import { referenceRequirements } from "./analysisContext";
import type { ComparativeReport } from "../api";

function EnergyDistribution({ values }: { values: number[] }) {
  if (values.length !== 3) return null;
  const minimum = Math.min(-120, ...values);
  const maximum = Math.max(0, ...values);
  return (
    <svg
      viewBox="0 0 320 48"
      width="100%"
      role="img"
      aria-label={`Measured frame energy distribution: P10 ${number(values[0], 2)}, P50 ${number(values[1], 2)}, P90 ${number(values[2], 2)} dBFS`}
    >
      <line x1="20" x2="300" y1="15" y2="15" stroke="#76857c" />
      {values.map((v, i) => (
        <circle
          key={i}
          cx={20 + ((v - minimum) / (maximum - minimum)) * 280}
          cy="15"
          r={i === 1 ? 4 : 2.5}
          fill="#235a50"
        />
      ))}
      <g fill="#4d5b54" fontSize="10">
        <text x="20" y="37">
          {number(minimum, 0)}
        </text>
        <text x="160" y="37" textAnchor="middle">
          {number((minimum + maximum) / 2, 0)}
        </text>
        <text x="300" y="37" textAnchor="end">
          {number(maximum, maximum === 0 ? 0 : 2)} dBFS
        </text>
      </g>
    </svg>
  );
}

export function ExploratoryResult({
  report,
  onSeek,
  assessment = null,
  insights = null,
}: {
  report: ExploratoryReport;
  onSeek: (
    recording: string,
    start: number,
    end?: number,
    play?: boolean,
  ) => void;
  assessment?: Report | null;
  insights?: ComparativeReport | null;
}) {
  const [showAll, setShowAll] = useState(false);
  const replay = (candidate: AcousticCandidate) =>
    onSeek(candidate.recording_id, candidate.start_s, candidate.end_s, true);
  return (
    <section
      className="panel exploratory-result"
      aria-label="Exploratory analysis"
    >
      {insights && <ComparativeInsights report={insights} onSeek={onSeek} />}
      <details className="exploratory-appendix" open={!insights}>
        <summary>Exploratory details / technical appendix</summary>
        <h3 className="print-only">
          Technical appendix · raw acoustic evidence
        </h3>
        <p className="eyebrow">
          Exploratory Speech Analysis · {report.config.method} · {report.state}
        </p>
        <h2>
          {report.pair_id
            ? "Measured recording differences"
            : "Measured reference audio"}
        </h2>
        {report.comparison && (
          <>
            <p>{report.comparison.interpretation}</p>
            <p>
              Participant minus reference RMS level:{" "}
              {number(report.comparison.rms_level_delta_db, 2)} dB. Active
              energy range difference:{" "}
              {number(report.comparison.active_energy_range_delta_db, 2)} dB.
            </p>
          </>
        )}
        <p className="notice">
          Digital amplitude depends on microphone, gain and noise. It is not
          calibrated SPL, perceived loudness or vocal effort. Automatic
          observations are unverified; they are not delivery flaws.
        </p>
        <dl className="measurement-strip">
          {report.recordings.map((r) => (
            <div key={r.recording_id}>
              <dt>
                {label(r.role)} · {r.filename}
              </dt>
              <dd>
                <strong>{number(r.duration_s, 3)} s</strong> · source{" "}
                {r.source_sample_rate_hz} Hz · analysis {r.sample_rate_hz} Hz
              </dd>
              <dd>
                RMS {number(r.rms, 5)} · peak {number(r.peak, 5)} · clipping{" "}
                {number(r.clipping_fraction * 100, 3)}%
              </dd>
              <dd>
                Energy baseline {number(r.energy_baseline_dbfs, 2)} dBFS ·
                active range {number(r.active_energy_range_db, 2)} dB
              </dd>
              <dd>
                Frame energy P10 / P50 / P90:{" "}
                {r.energy_quantiles_dbfs.map((v) => number(v, 2)).join(" / ") ||
                  "No complete frames"}{" "}
                dBFS
              </dd>
              <dd>
                <EnergyDistribution values={r.energy_quantiles_dbfs} />
              </dd>
              <dd>
                Observable activity {number(r.activity_support_s, 2)} s · low
                energy {number(r.low_energy_support_s, 2)} s · unobserved tail{" "}
                {number(r.unobserved_tail_s, 3)} s
              </dd>
              <dd>
                Accepted pitch coverage{" "}
                {number(
                  r.accepted_pitch_fraction == null
                    ? null
                    : r.accepted_pitch_fraction * 100,
                  2,
                )}
                % ({r.accepted_pitch_frames} / {r.pitch_frames} frames)
              </dd>
              {r.quality_flags.length > 0 && (
                <dd>
                  Quality warnings: {r.quality_flags.map(label).join(", ")}
                </dd>
              )}
            </div>
          ))}
        </dl>
        {Object.entries(report.unavailable_recordings).map(([id, reason]) => (
          <p role="status" key={id}>
            {id}: {reason}
          </p>
        ))}
        <p>
          Stored acoustic configuration:{" "}
          {report.recordings
            .map(
              (r) =>
                `${r.filename}: ${Object.entries(r.feature_config)
                  .map(([key, value]) => `${key}=${value}`)
                  .join("; ")}`,
            )
            .join(" · ")}
        </p>
        <h3>Automatic observations — unverified</h3>
        {report.candidates.length > 0 && (
          <p>
            {report.candidates.length} intervals meet the configured rules.
            Energy-change windows can overlap. These counts are not counts of
            mistakes.
          </p>
        )}
        {!report.candidates.length && (
          <p>
            No intervals meet the configured acoustic candidate rules. This is
            not a delivery assessment.
          </p>
        )}
        <ul className="findings-list">
          {(showAll ? report.candidates : report.candidates.slice(0, 8)).map(
            (c) => (
              <li key={c.id}>
                <h4>
                  {label(c.kind)} ·{" "}
                  {
                    report.recordings.find(
                      (r) => r.recording_id === c.recording_id,
                    )?.filename
                  }
                </h4>
                <p>
                  {number(c.start_s, 2)}–{number(c.end_s, 2)} s ·{" "}
                  {number(c.duration_s, 2)} s · median{" "}
                  {number(c.median_energy_dbfs, 2)} dBFS
                </p>
                <p>{c.explanation}</p>
                <p className="meta">{c.limitation}</p>
                <div className="toolbar">
                  <button
                    onClick={() => onSeek(c.recording_id, c.start_s, c.end_s)}
                  >
                    Inspect interval
                  </button>
                  <button onClick={() => replay(c)}>Replay interval</button>
                </div>
                <details>
                  <summary>Candidate method and thresholds</summary>
                  <p>
                    {c.method} · threshold{" "}
                    {c.threshold_dbfs == null
                      ? c.threshold_delta_db == null
                        ? "No relative baseline; activity is below the configured RMS floor"
                        : `${number(c.threshold_delta_db)} dB change`
                      : `${number(c.threshold_dbfs)} dBFS`}{" "}
                    · boundary resolution {c.boundary_resolution_s} s · window{" "}
                    {c.frame_window_s} s
                  </p>
                  <p className="hash">Feature SHA-256: {c.feature_sha256}</p>
                </details>
              </li>
            ),
          )}
        </ul>
        {report.candidates.length > 8 && (
          <button onClick={() => setShowAll((v) => !v)}>
            {showAll
              ? "Show first 8 observations"
              : `Show all ${report.candidates.length} observations`}
          </button>
        )}
        {report.candidates.length > 0 && (
          <table className="print-only candidate-table">
            <caption>
              Automatic acoustic candidates — unverified; native recording
              seconds
            </caption>
            <thead>
              <tr>
                <th>Recording / event</th>
                <th>Start–end (s)</th>
                <th>Median (dBFS)</th>
                <th>Change (dB)</th>
              </tr>
            </thead>
            <tbody>
              {report.candidates.map((c) => (
                <tr key={c.id}>
                  <td>
                    {
                      report.recordings.find(
                        (r) => r.recording_id === c.recording_id,
                      )?.filename
                    }{" "}
                    / {label(c.kind)}
                  </td>
                  <td>
                    {number(c.start_s, 2)}–{number(c.end_s, 2)}
                  </td>
                  <td>{number(c.median_energy_dbfs, 2)}</td>
                  <td>
                    {c.energy_delta_db == null
                      ? "—"
                      : number(c.energy_delta_db, 2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <details>
          <summary>Machine-aligned transcript — unverified</summary>
          <p>
            These timestamps align supplied text. They do not verify spoken
            words or timing accuracy.
          </p>
          {report.recordings.map((r) => (
            <div key={r.recording_id}>
              <h3>{r.filename}</h3>
              {r.automatic_alignment ? (
                <>
                  <p>
                    Alignment: {r.automatic_alignment.status}. Automatic
                    word-span estimate:{" "}
                    {number(
                      r.automatic_alignment.estimated_words_per_minute,
                      1,
                    )}{" "}
                    words/min.
                  </p>
                  <p>
                    {r.automatic_alignment.rate_unavailable_reason ??
                      "Uses unverified transcript words and includes internal gaps; this is not active speech rate."}
                  </p>
                  <p className="hash">
                    Source transcript SHA-256:{" "}
                    {r.automatic_alignment.original_text_sha256}
                  </p>
                  <div className="toolbar">
                    {r.automatic_alignment.words.map((w, i) => (
                      <button
                        key={i}
                        onClick={() =>
                          onSeek(r.recording_id, w.start_s, w.end_s)
                        }
                      >
                        {w.label} · {number(w.start_s, 2)}–{number(w.end_s, 2)}{" "}
                        s
                      </button>
                    ))}
                  </div>
                  <p className="print-only">
                    {r.automatic_alignment.words
                      .map(
                        (w) =>
                          `${w.label} [${number(w.start_s, 2)}–${number(w.end_s, 2)} s]`,
                      )
                      .join(" · ")}
                  </p>
                  {r.automatic_alignment.diagnostics.map((d, i) => (
                    <p key={i}>{d}</p>
                  ))}
                </>
              ) : (
                <p>No automatic alignment artifact is available.</p>
              )}
            </div>
          ))}
          {report.automatic_correspondence.length > 0 && (
            <div className="automatic-correspondence">
              <h3>Automatic word correspondence — unverified</h3>
              {report.automatic_correspondence.map((w) => (
                <p key={w.token_index}>
                  {w.token}: reference {number(w.reference.start_s, 2)}–
                  {number(w.reference.end_s, 2)} s; participant{" "}
                  {number(w.participant.start_s, 2)}–
                  {number(w.participant.end_s, 2)} s
                </p>
              ))}
            </div>
          )}
        </details>
        <details>
          <summary>Methods, limitations and reproducibility</summary>
          <p>
            RMS and peak measure canonical waveform amplitude; clipping is the
            sample fraction meeting the acoustic extractor threshold. Energy
            uses complete native frames and linear percentiles. Activity uses
            the existing baseline-relative energy rule.
          </p>
          <ul>
            {report.limitations.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
          <p>
            Dataset version: {report.dataset_version} · job: {report.job_id} ·
            processing: {report.processing_state}
          </p>
          <p className="hash">Dataset SHA-256: {report.dataset_sha256}</p>
          {report.recordings.map((r) => (
            <p className="hash" key={r.recording_id}>
              {r.filename}: audio {r.provenance.audio_sha256} · features{" "}
              {r.feature_artifact.sha256}
              {" · samples "}
              {r.provenance.sample_sha256}
              {" · supplied text "}
              {r.provenance.original_text_sha256}
              {" · alignment "}
              {r.alignment_artifact?.sha256 ?? "Unavailable"}
            </p>
          ))}
          <p className="hash">
            Implementation SHA-256: {report.implementation_sha256}
          </p>
          <p>
            Candidate rules: contiguous low-energy support ≥
            {report.config.minimum_quiet_s} s from acoustic-v1's two-pass
            activity mask (upper-quartile seed, initial active median minus
            configured activity drop, and absolute RMS floor); adjacent{" "}
            {report.config.energy_window_s} s median-energy windows differing by
            ≥{report.config.energy_step_db} dB. Boundaries follow native frame
            hops; overlapping energy-change windows are not independent events.
          </p>
        </details>
        <section className="print-only">
          <h3>
            {report.pair_id
              ? "Verified Assessment — separate evidence"
              : "Reference evidence requirements — separate"}
          </h3>
          <p>
            {!report.pair_id
              ? "Reference-only inspection; paired delivery assessment is not requested. Processing alone does not verify the reference."
              : assessment
                ? `Stored assessment eligibility: ${label(assessment.eligibility.state)}. This exploratory report supplies no scientific approval or delivery score.`
                : "Formal assessment evidence is not loaded. Independently checked text, rights and temporal correspondence are required; processing alone does not verify delivery."}
          </p>
          {assessment && (
            <ul>
              {(report.pair_id
                ? [
                    ...new Set(
                      [
                        ...(assessment.eligibility.reasons ?? []),
                        ...Object.values(
                          assessment.feature_eligibility,
                        ).flatMap((g) => g.reasons ?? []),
                      ].map(evidenceRequirement),
                    ),
                  ]
                : referenceRequirements(assessment)
              ).map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          )}
        </section>
      </details>
      <div className="toolbar print-controls">
        <a
          href={`/api/v1/analyses/${report.job_id}/exploratory/export?format=json`}
        >
          Export exploratory JSON
        </a>
        <a
          href={`/api/v1/analyses/${report.job_id}/exploratory/export?format=csv`}
        >
          Export interval CSV
        </a>
        <button
          onClick={() => {
            document.body.dataset.printScope = "exploratory";
            window.addEventListener(
              "afterprint",
              () => {
                delete document.body.dataset.printScope;
              },
              { once: true },
            );
            window.print();
          }}
        >
          Print exploratory report / save PDF
        </button>
      </div>
    </section>
  );
}
