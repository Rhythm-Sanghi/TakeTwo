import { useEffect, useRef, useState } from "react";
import uPlot from "uplot";
import { api, number } from "../api";
import type { components } from "../api.generated";

type Overlay = components["schemas"]["Overlay"];

export function TokenOverlay({
  jobId,
  onSeek,
}: {
  jobId: string;
  onSeek: (reference: number, participant: number) => void;
}) {
  const [name, setName] = useState("relative_energy");
  const [data, setData] = useState<Overlay | null>(null);
  const [error, setError] = useState("");
  const target = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let active = true;
    setData(null);
    setError("");
    api<Overlay>(`/analyses/${jobId}/overlay?name=${name}`)
      .then((value) => {
        if (active) setData(value);
      })
      .catch((cause) => {
        if (active) setError(cause.message);
      });
    return () => {
      active = false;
    };
  }, [jobId, name]);
  useEffect(() => {
    if (
      !target.current ||
      !data ||
      data.unavailable_reason ||
      !data.tokens.length
    )
      return;
    const element = target.current;
    const plot = new uPlot(
      {
        width: Math.max(260, element.clientWidth),
        height: 200,
        scales: { x: { time: false } },
        axes: [
          { label: "Canonical word index (zero-based)", size: 50 },
          { label: data.unit, size: 65 },
        ],
        legend: { show: true },
        series: [
          {},
          { label: "Reference · solid", stroke: "#235A50", spanGaps: false },
          {
            label: "Participant · dashed",
            stroke: "#8B4D22",
            dash: [5, 3],
            spanGaps: false,
          },
        ],
      },
      [
        data.tokens.map((_, i) => i),
        data.reference_values,
        data.participant_values,
      ],
      element,
    );
    const observer = new ResizeObserver(() =>
      plot.setSize({ width: Math.max(260, element.clientWidth), height: 200 }),
    );
    observer.observe(element);
    return () => {
      observer.disconnect();
      plot.destroy();
    };
  }, [data]);
  return (
    <section className="panel" aria-label="Canonical word acoustic overlay">
      <h2>Matched-word acoustic overlay</h2>
      <p>
        Reference and participant use reviewed canonical word correspondence.
        The horizontal axis is word index, not shared wall time. Curves show
        backend-computed word medians, not interpolated frame contours.
      </p>
      <label>
        Overlay measurement
        <select value={name} onChange={(event) => setName(event.target.value)}>
          <option value="relative_energy">Relative energy (dB)</option>
          <option value="relative_pitch">Relative pitch (semitones)</option>
        </select>
      </label>
      {error && <p role="alert">{error}</p>}
      {!data && !error && <p role="status">Loading correspondence…</p>}
      {data?.unavailable_reason ? (
        <>
          <p className="notice">{data.unavailable_reason}</p>
          <button disabled>Seek matching word in both tracks</button>
        </>
      ) : (
        data && (
          <>
            <div ref={target} aria-hidden="true" />
            <p className="meta">
              Median of eligible complete native frames inside each
              independently reviewed word. Energy uses 400-sample windows; pitch
              uses 1024; hop 160 at 16 kHz. Missing or unreliable word
              measurements remain gaps.
            </p>
            <details>
              <summary>Matched word values and native seek positions</summary>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Word index / text</th>
                      <th>Reference {data.unit}</th>
                      <th>Participant {data.unit}</th>
                      <th>Native starts (s)</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.tokens.map((token, i) => (
                      <tr key={i}>
                        <th scope="row">
                          {i} / {token}
                        </th>
                        <td>{number(data.reference_values[i])}</td>
                        <td>{number(data.participant_values[i])}</td>
                        <td>
                          {number(data.reference_words[i]?.start_s)} /{" "}
                          {number(data.participant_words[i]?.start_s)}
                        </td>
                        <td>
                          <button
                            onClick={() =>
                              onSeek(
                                data.reference_words[i].start_s,
                                data.participant_words[i].start_s,
                              )
                            }
                          >
                            Seek both to word {i}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          </>
        )
      )}
    </section>
  );
}
