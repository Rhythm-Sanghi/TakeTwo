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
function ReferenceMeasurements({ input }: { input: Report["inputs"][number] }) {
  const measurements = [
    ["Duration (s)", number(input.duration_s)],
    ["Spectral frames", String(input.spectral_frame_count)],
    [
      "RMS / peak (full scale)",
      `${number(input.quality.rms, 6)} / ${number(input.quality.peak, 6)}`,
    ],
    ["Energy baseline (dBFS)", number(input.energy_baseline_dbfs)],
    ["Pitch baseline — diagnostic (Hz)", number(input.pitch_baseline_hz, 1)],
    [
      "Reliable pitch coverage",
      `${number(input.pitch_valid_fraction * 100, 2)}%`,
    ],
    [
      "Accepted F0 confidence mask",
      number(input.feature_config.voicing_threshold, 2),
    ],
    [
      "Transcript reviewed",
      input.provenance.transcript_verified ? "Verified" : "Unverified",
    ],
    ["Independent review artifacts", String(input.reviews.length)],
  ];
  return (
    <dl
      className="reference-measurements"
      aria-label="Printed reference measurements"
    >
      {measurements.map(([name, value]) => (
        <div key={name}>
          <dt>{name}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function Scores({ report }: { report: Report }) {
  const key = (r: { code: string; message: string }) =>
    r.code + "\0" + r.message;
  const gates = Object.values(report.feature_eligibility).filter(Boolean);
  const shared = new Map(
    (report.eligibility.reasons ?? []).map((r) => [key(r), r]),
  );
  for (const gate of gates)
    for (const r of gate.reasons ?? []) {
      if (
        gates.filter((g) => g.reasons?.some((other) => key(other) === key(r)))
          .length > 1
      )
        shared.set(key(r), r);
    }
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
      {shared.size > 0 && (
        <div className="comparison-blockers">
          <h3>
            {report.eligibility.state === "REVIEW_REQUIRED"
              ? "Comparison awaiting review"
              : "Comparison evidence blockers"}
          </h3>
          <ul>
            {Array.from(shared.values()).map((r) => (
              <li key={key(r)}>{r.message}</li>
            ))}
          </ul>
        </div>
      )}
      <table tabIndex={0} aria-label="Dimension scores and coverage">
        <thead>
          <tr>
            <th>Dimension</th>
            <th>Weight</th>
            <th>Score / 100</th>
            <th>Coverage</th>
            <th>Eligible / expected</th>
            <th>Evidence status</th>
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
              <td>
                {label(
                  report.feature_eligibility[d.dimension]?.state ??
                    "Unavailable",
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="dimension-diagnostics">
        {report.dimensions.map((d) => {
          const gate = report.feature_eligibility[d.dimension];
          const unique = Array.from(
            new Map((gate?.reasons ?? []).map((r) => [key(r), r])).values(),
          ).filter((r) => !shared.has(key(r)));
          return (
            <details key={d.dimension}>
              <summary>{label(d.dimension)} · detailed eligibility</summary>
              <p>
                Scientific eligibility: {label(gate?.state ?? "Unavailable")}.{" "}
                {d.eligible_count} eligible / {d.expected_count} expected
                observations; coverage {number(d.coverage * 100, 1)}%. Required
                coverage: {number(report.policy.minimum_coverage * 100, 0)}%;
                minimum observations:{" "}
                {d.dimension === "pause_behavior"
                  ? report.policy.minimum_gaps
                  : report.policy.minimum_phrases}
                .
              </p>
              {shared.size > 0 && <p>Shared blockers are listed once above.</p>}
              {unique.map((r) => (
                <p key={key(r)}>{r.message}</p>
              ))}
              {d.reasons.map((r) => (
                <p key={key(r)}>{r.message}</p>
              ))}
              <details>
                <summary>Diagnostic reason codes</summary>
                <ul>
                  {Array.from(
                    new Set(
                      [...(gate?.reasons ?? []), ...d.reasons].map(
                        (r) => r.code,
                      ),
                    ),
                  ).map((code) => (
                    <li key={code}>
                      <code>{code}</code>
                    </li>
                  ))}
                </ul>
              </details>
            </details>
          );
        })}
      </div>
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
  referenceOnly = false,
}: {
  region: Region | null;
  report: Report | null;
  referenceOnly?: boolean;
}) {
  const referenceInspection = referenceOnly;
  return (
    <aside className="inspector" aria-label="Evidence inspector">
      <h2>Evidence inspector</h2>
      {!report ? (
        <p>Run analysis to inspect measured evidence.</p>
      ) : !region ? (
        <>
          <p>
            {referenceInspection
              ? "Reference measurements only. No participant comparison was run."
              : report.regions.length
                ? "Select a delivery deviation to inspect its calculation."
                : report.overall_score == null
                  ? "Comparison is unavailable. Zero detected regions does not indicate a perfect performance."
                  : "No threshold crossings were detected under this policy."}
          </p>
          <h3>Actual input evidence</h3>
          {report.inputs.length > 0 && (
            <div className="print-only">
              {referenceInspection ? (
                <ReferenceMeasurements input={report.inputs[0]} />
              ) : (
                <table aria-label="Printed input measurement summary">
                  <thead>
                    <tr>
                      <th>Measurement</th>
                      {report.inputs.map((input, index) => (
                        <th key={input.provenance.recording_id}>
                          {index === 0 ? "Reference" : "Participant"}
                          <br />
                          {input.provenance.recording_id}
                          <br />
                          {input.origin}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(
                      [
                        ["Duration (s)", (input) => number(input.duration_s)],
                        [
                          "Spectral frames",
                          (input) => String(input.spectral_frame_count),
                        ],
                        [
                          "Reliable pitch coverage",
                          (input) =>
                            `${number(input.pitch_valid_fraction * 100, 2)}%`,
                        ],
                        [
                          "Pitch baseline — diagnostic only (Hz)",
                          (input) => number(input.pitch_baseline_hz, 1),
                        ],
                        [
                          "Accepted F0 confidence mask",
                          (input) =>
                            number(input.feature_config.voicing_threshold, 2),
                        ],
                        [
                          "Energy baseline (dBFS)",
                          (input) => number(input.energy_baseline_dbfs),
                        ],
                        [
                          "RMS / peak (full scale)",
                          (input) =>
                            `${number(input.quality.rms, 6)} / ${number(input.quality.peak, 6)}`,
                        ],
                        [
                          "Transcript reviewed",
                          (input) =>
                            input.provenance.transcript_verified
                              ? "Verified"
                              : "Unverified",
                        ],
                        [
                          "Independent review artifacts",
                          (input) => String(input.reviews.length),
                        ],
                      ] satisfies [
                        string,
                        (input: Report["inputs"][number]) => string,
                      ][]
                    ).map(([name, value]) => (
                      <tr key={name}>
                        <th scope="row">{name}</th>
                        {report.inputs.map((input) => (
                          <td key={input.provenance.recording_id}>
                            {value(input)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              {referenceInspection ? (
                <p>
                  Pitch baselines summarize accepted voiced frames only.
                  Recording-wide pitch coverage is diagnostic. Audio
                  measurements do not verify the transcript or establish a
                  delivery flaw.
                </p>
              ) : (
                <p>
                  Pitch baselines are medians of accepted F0 frames only, not
                  robust estimates over the whole recording. Required reliable
                  coverage:{" "}
                  {number(report.policy.minimum_pitch_fraction * 100, 0)}% per
                  scored phrase; recording-wide coverage is diagnostic.
                  Scientific pitch eligibility:{" "}
                  {label(
                    report.feature_eligibility.pitch_dynamics?.state ??
                      "Unavailable",
                  )}
                  . Pitch-dynamics score:{" "}
                  {number(
                    report.dimensions.find(
                      (d) => d.dimension === "pitch_dynamics",
                    )?.score,
                    1,
                  )}
                  . When reliable voiced frames are insufficient, pitch scoring
                  is unavailable; other gates and observation requirements also
                  apply.
                </p>
              )}
            </div>
          )}
          {report.inputs.map((input) => (
            <section
              className="input-evidence"
              key={input.provenance.recording_id}
            >
              <h3>
                {input.origin} · {input.provenance.recording_id}
              </h3>
              <dl>
                <dt>Duration</dt>
                <dd>{number(input.duration_s)} s</dd>
                <dt>Spectral frames</dt>
                <dd>{input.spectral_frame_count}</dd>
                <dt>Reliable pitch coverage</dt>
                <dd>{number(input.pitch_valid_fraction * 100, 2)}%</dd>
                <dt>Energy baseline</dt>
                <dd>{number(input.energy_baseline_dbfs)} dBFS</dd>
                <dt>Pitch baseline — diagnostic only</dt>
                <dd>
                  {input.pitch_baseline_hz == null
                    ? "Unavailable"
                    : `${number(input.pitch_baseline_hz, 1)} Hz · median of accepted F0 frames only`}
                </dd>
                {!referenceInspection && (
                  <>
                    <dt>Pitch evidence and scoring</dt>
                    <dd>
                      Required reliable coverage:{" "}
                      {number(report.policy.minimum_pitch_fraction * 100, 0)}%
                      per scored phrase. Accepted F0 uses the stored confidence
                      mask ({number(input.feature_config.voicing_threshold, 2)}
                      ). Scientific pitch eligibility:{" "}
                      {label(
                        report.feature_eligibility.pitch_dynamics?.state ??
                          "Unavailable",
                      )}
                      .{" "}
                      {report.dimensions.find(
                        (d) => d.dimension === "pitch_dynamics",
                      )?.score != null
                        ? "Pitch-dynamics score available in the rubric table."
                        : input.pitch_baseline_hz == null ||
                            input.pitch_valid_fraction <
                              report.policy.minimum_pitch_fraction
                          ? "Pitch scoring unavailable: insufficient reliable voiced frames. Recording-wide coverage is diagnostic; phrase eligibility and all other gates still apply."
                          : "Pitch scoring unavailable: inspect the pitch dimension for evidence, coverage and observation requirements."}
                    </dd>
                  </>
                )}
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
