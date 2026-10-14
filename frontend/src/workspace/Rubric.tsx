import { number } from "../api";
import type { Policy } from "../api";

export function Rubric({ policy }: { policy: Policy | null }) {
  if (!policy) return <p>Loading rubric…</p>;
  return (
    <section className="panel">
      <h2>{policy.version} · reference agreement</h2>
      <p>
        Initial engineering tolerances; uncalibrated. Acoustic agreement does
        not measure persuasion, emotion or overall speaking ability. Effective
        alternative deliveries can differ.
      </p>
      <table tabIndex={0} aria-label="Rubric definitions">
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
