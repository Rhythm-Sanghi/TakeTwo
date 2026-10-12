import { useEffect, useRef, useState } from "react";
import { api, label, number } from "../api";
import type {
  Alignment,
  FeatureWindow,
  Job,
  Recording,
  Region,
  Waveform,
} from "../api";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";

export function timeAtPosition(
  x: number,
  width: number,
  start: number,
  end: number,
) {
  return start + Math.min(1, Math.max(0, x / width)) * (end - start);
}
export function sampleAtTime(time: number) {
  return Math.round(time * 16000);
}

function FeatureChart({
  data,
  start,
  end,
  role,
}: {
  data: FeatureWindow;
  start: number;
  end: number;
  role: string;
}) {
  const container = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!container.current || !data.times_s.length) return;
    const target = container.current;
    const plot = new uPlot(
      {
        width: Math.max(260, target.clientWidth),
        height: 175,
        legend: { show: false },
        cursor: { show: true, drag: { x: false, y: false } },
        scales: { x: { time: false, min: start, max: end } },
        axes: [
          { label: "Native time (s)", size: 45 },
          { label: data.unit, size: 65 },
        ],
        series: [
          {},
          {
            label: `${role} ${data.name}`,
            stroke: role === "reference" ? "#235A50" : "#8B4D22",
            width: 1.5,
            dash: role === "participant" ? [5, 3] : [],
            spanGaps: false,
          },
        ],
      },
      [data.times_s, data.values],
      target,
    );
    const observer = new ResizeObserver(() =>
      plot.setSize({ width: Math.max(260, target.clientWidth), height: 175 }),
    );
    observer.observe(target);
    return () => {
      observer.disconnect();
      plot.destroy();
    };
  }, [data, start, end, role]);
  const available = data.values.some((v) => v != null);
  return (
    <section
      className="feature-chart"
      aria-label={`${role} ${data.name} chart`}
    >
      <p>
        <strong>
          {label(data.name)} · {data.unit}
        </strong>{" "}
        · {role} {role === "reference" ? "solid" : "dashed"}
      </p>
      {available ? (
        <div ref={container} aria-hidden="true" />
      ) : (
        <p className="notice">
          {data.name.includes("pitch") || data.name === "f0"
            ? "Pitch evidence unavailable: no reliable frames in this window."
            : "No observed frames in this window."}
        </p>
      )}
      <p className="meta">
        Frame {data.frame_length} samples / hop {data.hop_length} samples at 16
        kHz · {label(data.aggregation)}. Missing frames remain gaps.
      </p>
      <details>
        <summary>Nonvisual chart values ({data.values.length} points)</summary>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Acoustic chart values"
        >
          <table tabIndex={0} aria-label="Acoustic measurements by native time">
            <thead>
              <tr>
                <th>Native time (s)</th>
                <th>{data.unit}</th>
              </tr>
            </thead>
            <tbody>
              {data.times_s.map((t, i) => (
                <tr key={i}>
                  <td>{number(t)}</td>
                  <td>{number(data.values[i])}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}

export function Timeline({
  recording,
  job,
  regions,
  selected,
  seek,
  onSelect,
  onPlay,
}: {
  recording: Recording;
  job: Job | null;
  regions: Region[];
  selected: string | null;
  seek: { time: number; end?: number; nonce: number } | null;
  onSelect: (region: Region) => void;
  onPlay: (element: HTMLAudioElement) => void;
}) {
  const duration = recording.normalized_info.duration_s;
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(duration);
  const [cursor, setCursor] = useState(0);
  const [selection, setSelection] = useState<[number, number]>([0, duration]);
  const [waveform, setWaveform] = useState<Waveform | null>(null);
  const [alignment, setAlignment] = useState<Alignment | null>(null);
  const [feature, setFeature] = useState("rms");
  const [data, setData] = useState<FeatureWindow | null>(null);
  const [error, setError] = useState("");
  const canvas = useRef<HTMLCanvasElement>(null);
  const audio = useRef<HTMLAudioElement>(null);
  const pointerStart = useRef<number | null>(null);
  const hasFeatures = Boolean(job?.artifacts?.[recording.id]?.features);
  useEffect(() => {
    let active = true;
    setWaveform(null);
    api<Waveform>(
      `/recordings/${recording.id}/waveform?start_s=${start}&end_s=${end}&bins=1500`,
    )
      .then((value) => {
        if (active) {
          setWaveform(value);
          setError("");
        }
      })
      .catch((cause) => {
        if (active) setError(cause.message);
      });
    return () => {
      active = false;
    };
  }, [recording.id, start, end]);
  useEffect(() => {
    let active = true;
    setData(null);
    setAlignment(null);
    if (job && hasFeatures) {
      api<FeatureWindow>(
        `/analyses/${job.id}/features/${recording.id}?name=${feature}&start_s=${start}&end_s=${end}&max_points=1500`,
      )
        .then((value) => {
          if (active) setData(value);
        })
        .catch((cause) => {
          if (active) setError(cause.message);
        });
      if (job.artifacts?.[recording.id]?.alignment)
        api<Alignment>(`/analyses/${job.id}/alignments/${recording.id}`)
          .then((value) => {
            if (active) setAlignment(value);
          })
          .catch((cause) => {
            if (active) setError(cause.message);
          });
    }
    return () => {
      active = false;
    };
  }, [
    job?.id,
    job?.updated_at,
    recording.id,
    hasFeatures,
    feature,
    start,
    end,
  ]);
  useEffect(() => {
    if (seek && audio.current) {
      const target = Math.max(0, Math.min(duration, seek.time));
      audio.current.currentTime = target;
      setCursor(target);
      if (seek.end != null)
        setSelection([target, Math.min(duration, seek.end)]);
      if (target < start || target > end) {
        setStart(Math.max(0, target - 1));
        setEnd(Math.min(duration, (seek.end ?? target) + 2));
      }
    }
  }, [seek]); // Explicit seek requests preserve each track's independent cursor.
  useEffect(() => {
    const element = canvas.current;
    if (!element || !waveform) return;
    function draw() {
      if (!element || !waveform) return;
      const width = element.clientWidth,
        height = 140;
      element.width = width * devicePixelRatio;
      element.height = height * devicePixelRatio;
      const ctx = element.getContext("2d");
      if (!ctx) return;
      ctx.scale(devicePixelRatio, devicePixelRatio);
      ctx.clearRect(0, 0, width, height);
      const x = (time: number) => ((time - start) / (end - start)) * width;
      ctx.strokeStyle = "#D1D5CF";
      ctx.lineWidth = 1;
      for (let i = 0; i <= 8; i++) {
        const xx = (i * width) / 8;
        ctx.beginPath();
        ctx.moveTo(xx, 0);
        ctx.lineTo(xx, height);
        ctx.stroke();
      }
      ctx.fillStyle = "rgba(35,90,80,0.10)";
      ctx.fillRect(
        x(selection[0]),
        0,
        x(selection[1]) - x(selection[0]),
        height,
      );
      for (const region of regions) {
        const interval =
          recording.role === "reference"
            ? region.reference_interval
            : region.participant_interval;
        const anchor =
          recording.role === "reference"
            ? region.reference_anchor_s
            : region.participant_anchor_s;
        const left = interval?.start_s ?? anchor ?? 0,
          right = interval?.end_s ?? left;
        ctx.strokeStyle = selected === region.id ? "#A12C2C" : "#805100";
        ctx.setLineDash([4, 3]);
        ctx.strokeRect(
          x(left),
          8,
          Math.max(2, x(right) - x(left)),
          height - 16,
        );
        ctx.setLineDash([]);
      }
      ctx.strokeStyle = recording.role === "reference" ? "#235A50" : "#8B4D22";
      ctx.beginPath();
      for (const [a, b, low, high] of waveform.bins) {
        const xx = x((a + b) / 32000);
        ctx.moveTo(xx, height / 2 - high * height * 0.45);
        ctx.lineTo(xx, height / 2 - low * height * 0.45);
      }
      ctx.stroke();
      ctx.strokeStyle = "#76857C";
      for (const word of alignment?.words ?? [])
        if (word.start_s >= start && word.start_s <= end) {
          ctx.beginPath();
          ctx.moveTo(x(word.start_s), height - 12);
          ctx.lineTo(x(word.start_s), height);
          ctx.stroke();
        }
      ctx.strokeStyle = "#202824";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x(cursor), 0);
      ctx.lineTo(x(cursor), height);
      ctx.stroke();
    }
    draw();
    const observer = new ResizeObserver(draw);
    observer.observe(element);
    return () => observer.disconnect();
  }, [
    waveform,
    start,
    end,
    cursor,
    alignment,
    regions,
    selected,
    selection,
    recording.role,
  ]);
  function seekTo(time: number) {
    if (audio.current) {
      audio.current.currentTime = time;
      setCursor(time);
    }
  }
  function zoom(factor: number) {
    const width = Math.max(0.1, Math.min(duration, (end - start) * factor));
    const left = Math.max(0, Math.min(duration - width, cursor - width / 2));
    setStart(left);
    setEnd(left + width);
  }
  function pan(direction: number) {
    const width = end - start;
    const left = Math.max(
      0,
      Math.min(duration - width, start + direction * width * 0.5),
    );
    setStart(left);
    setEnd(left + width);
  }
  const visibleRegions = regions.filter((r) => {
    const interval =
      recording.role === "reference"
        ? r.reference_interval
        : r.participant_interval;
    const anchor =
      recording.role === "reference"
        ? r.reference_anchor_s
        : r.participant_anchor_s;
    return (
      (interval?.start_s ?? anchor ?? 0) <= end &&
      (interval?.end_s ?? anchor ?? 0) >= start
    );
  });
  return (
    <section
      className={`track ${recording.role}`}
      aria-label={`${recording.role} timeline`}
    >
      <div className="section-heading">
        <h2>
          {recording.role === "reference" ? "Reference" : "Participant"}{" "}
          <span>{recording.original_filename}</span>
        </h2>
        <span className="mono">{number(duration)} s · 16 kHz</span>
      </div>
      <audio
        ref={audio}
        controls
        preload="metadata"
        src={`/api/v1/recordings/${recording.id}/audio`}
        aria-label={`${recording.role} audio`}
        onPlay={(event) => onPlay(event.currentTarget)}
        onTimeUpdate={(event) => setCursor(event.currentTarget.currentTime)}
        onError={() =>
          setError(
            "Audio playback failed. Check that the managed WAV is still available.",
          )
        }
      />
      <div className="toolbar">
        <button
          onClick={() => zoom(0.5)}
          aria-label={`Zoom in ${recording.role}`}
        >
          Zoom in
        </button>
        <button
          onClick={() => zoom(2)}
          aria-label={`Zoom out ${recording.role}`}
        >
          Zoom out
        </button>
        <button
          aria-label={`Earlier ${recording.role} window`}
          onClick={() => pan(-1)}
          disabled={start <= 0}
        >
          Earlier
        </button>
        <button
          aria-label={`Later ${recording.role} window`}
          onClick={() => pan(1)}
          disabled={end >= duration}
        >
          Later
        </button>
        <button
          aria-label={`Fit ${recording.role} recording`}
          onClick={() => {
            setStart(0);
            setEnd(duration);
          }}
        >
          Fit recording
        </button>
        <output className="mono">
          {number(start)}–{number(end)} s
        </output>
      </div>
      <canvas
        ref={canvas}
        className="waveform"
        role="img"
        style={{ visibility: waveform ? "visible" : "hidden" }}
        aria-hidden={!waveform}
        aria-label={`Measured ${recording.role} waveform, ${number(start)} to ${number(end)} seconds. Use seek and selection controls below.`}
        onPointerDown={(event) => {
          pointerStart.current = timeAtPosition(
            event.clientX -
              event.currentTarget.getBoundingClientRect().left -
              event.currentTarget.clientLeft,
            event.currentTarget.clientWidth,
            start,
            end,
          );
          event.currentTarget.setPointerCapture(event.pointerId);
        }}
        onPointerUp={(event) => {
          const time = timeAtPosition(
            event.clientX -
              event.currentTarget.getBoundingClientRect().left -
              event.currentTarget.clientLeft,
            event.currentTarget.clientWidth,
            start,
            end,
          );
          const initial = pointerStart.current ?? time;
          setSelection([Math.min(time, initial), Math.max(time, initial)]);
          seekTo(time);
          pointerStart.current = null;
        }}
      />
      {!waveform && !error && (
        <p role="status">Loading {recording.role} waveform…</p>
      )}
      <div className="time-axis mono">
        <span>{number(start)} s</span>
        <span>Amplitude · full scale ±1</span>
        <span>{number(end)} s</span>
      </div>
      <label>
        Seek {recording.role} (s)
        <input
          aria-label={`Seek ${recording.role}`}
          aria-valuetext={`${number(cursor)} seconds of ${number(duration)} seconds`}
          type="range"
          min="0"
          max={duration}
          step={1 / 16000}
          value={cursor}
          onChange={(event) => seekTo(Number(event.target.value))}
        />
      </label>
      <div className="toolbar">
        <output className="mono" aria-live="off">
          Playhead {number(cursor)} s / sample {sampleAtTime(cursor)}
        </output>
        <label>
          Selection start (s)
          <input
            aria-label={`${recording.role} selection start (s)`}
            type="number"
            min="0"
            max={selection[1]}
            step="0.001"
            value={selection[0]}
            onChange={(event) =>
              setSelection([
                Math.max(0, Math.min(selection[1], Number(event.target.value))),
                selection[1],
              ])
            }
          />
        </label>
        <label>
          Selection end (s)
          <input
            aria-label={`${recording.role} selection end (s)`}
            type="number"
            min={selection[0]}
            max={duration}
            step="0.001"
            value={selection[1]}
            onChange={(event) =>
              setSelection([
                selection[0],
                Math.min(
                  duration,
                  Math.max(selection[0], Number(event.target.value)),
                ),
              ])
            }
          />
        </label>
        <button
          onClick={() => {
            seekTo(selection[0]);
            void audio.current
              ?.play()
              .catch(() =>
                setError(
                  "Playback was blocked by the browser; use the audio play control.",
                ),
              );
          }}
        >
          Play from selection
        </button>
        <output className="mono">
          Selection {number(selection[1] - selection[0])} s
        </output>
      </div>
      {error && <p role="alert">{error}</p>}
      {visibleRegions.length > 0 && (
        <div className="toolbar" aria-label="Detected regions">
          {visibleRegions.map((region) => (
            <button
              key={region.id}
              aria-pressed={selected === region.id}
              onClick={() => onSelect(region)}
            >
              {label(region.category)} ·{" "}
              {region.participant_interval
                ? number(region.participant_interval.start_s) + " s"
                : "boundary " + number(region.participant_anchor_s) + " s"}
            </button>
          ))}
        </div>
      )}
      {alignment ? (
        <details>
          <summary>
            Word alignment · {alignment.status} · automatic, independently
            unreviewed
          </summary>
          {(alignment.diagnostics ?? []).map((d) => (
            <p key={d.code}>
              {d.message} {d.recovery}
            </p>
          ))}
          <div className="word-strip">
            {(alignment.words ?? []).map((word) => (
              <button
                key={word.token_index}
                onClick={() => seekTo(word.start_s)}
                title={`${number(word.start_s)}–${number(word.end_s)} s`}
              >
                {word.label} <span>{number(word.start_s, 2)}</span>
              </button>
            ))}
          </div>
        </details>
      ) : (
        <p className="meta">
          Alignment unavailable or pending. No substitute word timestamps are
          displayed.
        </p>
      )}
      {hasFeatures ? (
        <>
          <label>
            Acoustic series
            <select
              aria-label={`${recording.role} acoustic series`}
              value={feature}
              onChange={(event) => setFeature(event.target.value)}
            >
              {[
                "rms",
                "energy",
                "relative_energy",
                "f0",
                "relative_pitch",
                "activity",
                "spectral_centroid",
              ].map((name) => (
                <option value={name} key={name}>
                  {label(name)}
                </option>
              ))}
            </select>
          </label>
          {!data && !error && (
            <p role="status">Loading {recording.role} acoustic measurements…</p>
          )}
          {data && (
            <>
              <FeatureChart
                data={data}
                start={start}
                end={end}
                role={recording.role}
              />
              <p>
                Speaking rate: {number(data.speaking_rate_wpm)} words/min.{" "}
                {data.rate_unavailable_reason}
              </p>
              <details>
                <summary>Measured quality and pause evidence</summary>
                <dl>
                  <dt>RMS (full scale)</dt>
                  <dd>{number(data.quality.rms, 6)}</dd>
                  <dt>Peak (full scale)</dt>
                  <dd>{number(data.quality.peak, 6)}</dd>
                  <dt>Clipping fraction</dt>
                  <dd>{number(data.quality.clipping_fraction, 6)}</dd>
                  <dt>Quality flags</dt>
                  <dd>
                    {data.quality.flags.join(", ") ||
                      "None detected by configured checks"}
                  </dd>
                </dl>
                {data.pauses.length ? (
                  <ul>
                    {data.pauses.map((p, i) => (
                      <li key={i}>
                        {number(p.start_s)}–{number(p.end_s)} s
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>
                    No eligible aligned pause intervals available; inspect
                    activity separately.
                  </p>
                )}
              </details>
            </>
          )}
        </>
      ) : (
        <p className="notice">
          Run analysis to inspect actual acoustic measurements.
        </p>
      )}
    </section>
  );
}
