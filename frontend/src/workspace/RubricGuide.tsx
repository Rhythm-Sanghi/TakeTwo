import { number } from "../api";
import type { Report } from "../api";
import { evidenceRequirement } from "./AnalysisResult";

const dimensions = [
  [
    "pacing",
    "Pacing",
    "How quickly the same words are spoken within reviewed phrases.",
    "Reviewed words and phrase timing in both recordings.",
  ],
  [
    "pause_behavior",
    "Pauses",
    "How gaps between corresponding words differ from the reference.",
    "Reviewed word boundaries and enough eligible gaps.",
  ],
  [
    "energy_variation",
    "Energy",
    "How the range of relative loudness changes within a phrase.",
    "Acoustic energy frames supported by reviewed phrase timing.",
  ],
  [
    "pitch_dynamics",
    "Pitch",
    "How the range of relative pitch changes within a phrase.",
    "Enough reliable voiced frames in reviewed phrases.",
  ],
];
export function RubricGuide({ report }: { report: Report | null }) {
  const shared = new Set(
    (report?.eligibility.reasons ?? []).map((r) => r.message),
  );
  return (
    <section className="panel">
      <h2>Understand reference agreement</h2>
      <p>
        Compare delivery of the same words across four dimensions. These
        engineering tolerances are uncalibrated: a different delivery can be
        effective. This is not a public-speaking quality score.
      </p>
      {shared.size > 0 && (
        <div className="comparison-blockers">
          <h3>Required for this comparison</h3>
          <ul>
            {(report?.eligibility.reasons ?? [])
              .map(evidenceRequirement)
              .filter(
                (message, index, messages) =>
                  messages.indexOf(message) === index,
              )
              .map((message) => (
                <li key={message}>{message}</li>
              ))}
          </ul>
        </div>
      )}
      <div className="rubric-guide">
        {dimensions.map(([key, name, meaning, evidence]) => {
          const dimension = report?.dimensions.find((d) => d.dimension === key);
          const gate = report?.feature_eligibility[key];
          return (
            <section key={key}>
              <h3>{name}</h3>
              <p>{meaning}</p>
              <p className="meta">Required evidence: {evidence}</p>
              <p>
                <strong>
                  {dimension?.score != null
                    ? `${number(dimension.score, 1)} / 100 reference agreement`
                    : report
                      ? "Assessment unavailable"
                      : "No comparison selected"}
                </strong>
              </p>
              {dimension && (
                <p>
                  {dimension.eligible_count} eligible /{" "}
                  {dimension.expected_count} expected observations. Higher
                  agreement means less measured deviation from this reference.
                </p>
              )}
              {report && (
                <>
                  <p>
                    Evidence:{" "}
                    {gate?.state === "ELIGIBLE"
                      ? "Eligible"
                      : "Requirements incomplete"}
                    .{" "}
                    {dimension?.score == null
                      ? "No eligible score returned. Resolve the comparison requirements and check dimension coverage."
                      : "Backend evidence requirements met for this dimension."}
                  </p>
                  <details>
                    <summary>{name} · evidence details</summary>
                    <ul>
                      {[
                        ...new Set(
                          [
                            ...(gate?.reasons ?? []),
                            ...(dimension?.reasons ?? []),
                          ].map((r) => r.message),
                        ),
                      ]
                        .filter((message) => !shared.has(message))
                        .map((message) => (
                          <li key={message}>{message}</li>
                        ))}
                    </ul>
                    <p className="meta">
                      Shared requirements are listed above. Full thresholds and
                      reason codes remain in Technical details.
                    </p>
                  </details>
                </>
              )}
            </section>
          );
        })}
      </div>
      <p className="meta">
        Overall agreement requires all four dimensions. Missing evidence is
        never replaced or reweighted. Acoustic association does not establish a
        cause.
      </p>
    </section>
  );
}
