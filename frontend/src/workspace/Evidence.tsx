import { label, number } from "../api";
import type { Observation, Region, Report } from "../api";

export function Location({
  interval,
  anchor,
}: {
  interval: { start_s: number; end_s: number } | null;
  anchor: number | null | undefined;
}) {
  return (
    <>
      {interval
        ? `${number(interval.start_s)}–${number(interval.end_s)} s`
        : anchor != null
          ? `Boundary at ${number(anchor)} s`
          : "Unavailable"}
    </>
  );
}
export function Scores({ report }: { report: Report }) {
  return (
    <section aria-label="Rubric scores">
      <div className="section-heading">
        <h2>Reference agreement</h2>
        <strong>Overall: {number(report.overall_score, 1)}</strong>
      </div>
      <p>
        {report.policy.version} · {label(report.eligibility.state)} · all four
        dimensions required. Unavailable weights are never redistributed.
      </p>
      <table tabIndex={0} aria-label="Dimension scores and coverage">
        <thead>
          <tr>
            <th>Dimension</th>
            <th>Weight</th>
            <th>Score / 100</th>
            <th>Coverage</th>
            <th>Eligible / expected</th>
          </tr>
        </thead>
        <tbody>
          {report.dimensions.map((d) => (
            <tr key={d.dimension}>
              <th scope="row">{label(d.dimension)}</th>
              <td>
                {number(
                  report.policy.weights
                    ? report.policy.weights[d.dimension] * 100
                    : null,
                  0,
                )}
                %
              </td>
              <td>{number(d.score, 1)}</td>
              <td>{number(d.coverage * 100, 1)}%</td>
              <td>
                {d.eligible_count} / {d.expected_count}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <details open={report.overall_score == null}>
        <summary>Eligibility and withheld-score reasons</summary>
        {Object.entries(report.feature_eligibility).map(([name, gate]) => (
          <div key={name}>
            <h3>
              {label(name)} · {label(gate.state)}
            </h3>
            <ul>
              {Array.from(
                new Map(
                  (gate.reasons ?? []).map((r) => [r.code + r.message, r]),
                ).values(),
              ).map((r, i) => (
                <li key={i}>{r.message}</li>
              ))}
            </ul>
            {Boolean(gate.reasons?.length) && (
              <details>
                <summary>Diagnostic reason codes</summary>
                <ul>
                  {Array.from(new Set(gate.reasons?.map((r) => r.code))).map(
                    (code) => (
                      <li key={code}>
                        <code>{code}</code>
                      </li>
                    ),
                  )}
                </ul>
              </details>
            )}
            {report.dimensions
              .find((d) => d.dimension === name)
              ?.reasons.map((r) => (
                <p key={r.code}>{r.message}</p>
              ))}
          </div>
        ))}
      </details>
    </section>
  );
}
function Measurement({ observation: o }: { observation: Observation }) {
  return (
    <section>
      <h3>
        {label(o.detector)} · {label(o.dimension)}
      </h3>
      <dl>
        <dt>Canonical token span</dt>
        <dd>[{o.token_span.join(", ")})</dd>
        <dt>Reference location</dt>
        <dd>
          <Location
            interval={o.reference_interval}
            anchor={o.reference_anchor_s}
          />
        </dd>
        <dt>Participant location</dt>
        <dd>
          <Location
            interval={o.participant_interval}
            anchor={o.participant_anchor_s}
          />
        </dd>
        <dt>Reference measurement</dt>
        <dd>
          {number(o.reference, 6)} {o.unit}
        </dd>
        <dt>Participant measurement</dt>
        <dd>
          {number(o.participant, 6)} {o.unit}
        </dd>
        <dt>Signed deviation</dt>
        <dd>
          {number(o.delta, 6)}{" "}
          {o.dimension === "pacing" ? "natural-log rate ratio" : o.unit}
        </dd>
        <dt>Tolerance / saturation width</dt>
        <dd>
          {number(o.tolerance, 6)} / {number(o.saturation_width, 6)}
        </dd>
        <dt>Normalized deviation</dt>
        <dd>{number(o.normalized_deviation, 6)}</dd>
        <dt>Excess / penalty</dt>
        <dd>
          {number(o.excess, 6)} / {number(o.penalty, 6)}
        </dd>
        <dt>Rubric contribution</dt>
        <dd>
          {o.scored ? "Scored observation" : "Evidence only; no extra penalty"}
        </dd>
        <dt>Valid reference / participant fraction</dt>
        <dd>
          {number(o.reference_valid_fraction)} /{" "}
          {number(o.participant_valid_fraction)}
        </dd>
        <dt>Eligibility</dt>
        <dd>
          {label(o.eligibility.state)}{" "}
          {(o.eligibility.reasons ?? []).map((r) => r.message).join(" ")}
        </dd>
      </dl>
    </section>
  );
}
export function Inspector({
  region,
  report,
}: {
  region: Region | null;
  report: Report | null;
}) {
  return (
    <aside className="inspector" aria-label="Evidence inspector">
      <h2>Evidence inspector</h2>
      {!report ? (
        <p>Run analysis to inspect measured evidence.</p>
      ) : !region ? (
        <>
          <p>
            {report.regions.length
              ? "Select a delivery deviation to inspect its calculation."
              : report.overall_score == null
                ? "Comparison is unavailable. Zero detected regions does not indicate a perfect performance."
                : "No threshold crossings were detected under this policy."}
          </p>
          <h3>Actual input evidence</h3>
          {report.inputs.map((input) => (
            <section key={input.provenance.recording_id}>
              <h3>
                {input.origin} · {input.provenance.recording_id}
              </h3>
              <dl>
                <dt>Duration</dt>
                <dd>{number(input.duration_s)} s</dd>
                <dt>Spectral frames</dt>
                <dd>{input.spectral_frame_count}</dd>
                <dt>Pitch-valid fraction</dt>
                <dd>{number(input.pitch_valid_fraction)}</dd>
                <dt>Energy baseline</dt>
                <dd>{number(input.energy_baseline_dbfs)} dBFS</dd>
                <dt>Pitch baseline</dt>
                <dd>{number(input.pitch_baseline_hz)} Hz</dd>
                <dt>RMS / peak</dt>
                <dd>
                  {number(input.quality.rms, 6)} /{" "}
                  {number(input.quality.peak, 6)}
                </dd>
                <dt>Transcript reviewed</dt>
                <dd>
                  {input.provenance.transcript_verified
                    ? "Verified"
                    : "Unverified"}
                </dd>
                <dt>Independent review artifacts</dt>
                <dd>{input.reviews.length}</dd>
              </dl>
            </section>
          ))}
        </>
      ) : (
        <>
          <h3>
            {label(region.category)} · severity {region.severity}
          </h3>
          <p>{region.explanation.plain}</p>
          <p>{region.explanation.suggested_review}</p>
          <p>
            Reliability: {region.reliability}. Detection confidence: unavailable
            ({label(region.confidence_reason ?? "not_calibrated")}). Timing
            uncertainty: unavailable.
          </p>
          <p>
            Normalization: pitch is relative to median voiced F0; energy is
            relative to median active energy. Pacing uses matched token counts;
            pauses retain native seconds.
          </p>
          {report.observations
            .filter((o) => region.observation_ids.includes(o.id))
            .map((o) => (
              <Measurement key={o.id} observation={o} />
            ))}
          <details open>
            <summary>Mathematical explanation</summary>
            <p>{region.explanation.technical}</p>
          </details>
        </>
      )}
      {report && (
        <details>
          <summary>Processing provenance and limitations</summary>
          <dl>
            <dt>Dataset version</dt>
            <dd>{report.dataset_version}</dd>
            <dt>Policy hash</dt>
            <dd className="hash">{report.policy_sha256}</dd>
            <dt>Comparison implementation</dt>
            <dd className="hash">{report.implementation_sha256}</dd>
          </dl>
          {report.inputs.map((input) => (
            <dl key={input.provenance.recording_id}>
              <dt>Audio SHA-256</dt>
              <dd className="hash">{input.provenance.audio_sha256}</dd>
              <dt>Feature SHA-256</dt>
              <dd className="hash">{input.features.sha256}</dd>
              <dt>Feature implementation SHA-256</dt>
              <dd className="hash">{input.provenance.implementation_sha256}</dd>
            </dl>
          ))}
          <ul>
            {report.limitations.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </details>
      )}
    </aside>
  );
}
