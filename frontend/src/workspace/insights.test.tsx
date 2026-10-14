import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { ComparativeInsights } from "./ComparativeInsights";
import type { ComparativeReport } from "../api";

afterEach(cleanup);
// Presentation fixtures only: deliberately different native clocks.
const fixture = {
  config: { method: "comparative-insights-v1", initial_items: 6 },
  exploratory: {
    job_id: "job",
    reference_id: "ref",
    pair_id: "pair",
    candidates: [],
    recordings: [
      { recording_id: "ref", role: "reference", filename: "reference.wav" },
      {
        recording_id: "part",
        role: "participant",
        filename: "participant.wav",
      },
    ],
  },
  groups: [],
  anomalies: [],
  phrase_review_sha256: [],
  limitations: [],
  segments: [
    {
      id: "word",
      kind: "word",
      text: "example",
      token_start: 1,
      token_end: 2,
      reference: { start_s: 10, end_s: 10.5 },
      participant: { start_s: 13, end_s: 13.8 },
      duration_delta_s: 0.3,
      relative_duration_delta_percent: 60,
      reference_gap_before_s: 0.2,
      participant_gap_before_s: 2,
      gap_delta_s: 1.8,
      relative_energy_delta_db: null,
      reference_measurements: { median_energy_dbfs: -30 },
      participant_measurements: { median_energy_dbfs: -31 },
      limitation: "Automatic and unverified",
    },
  ],
  inspection_order: [
    {
      id: "item",
      category: "gap_difference",
      evidence_id: "word",
      order_reason: "Larger measured gap; not confidence",
    },
  ],
  phrase_unavailable_reason:
    "No reviewed phrase partition; comparison withheld",
} as unknown as ComparativeReport;

it("includes both surrounding words when replaying a paired alignment anomaly", () => {
  const seek = vi.fn();
  const report = {
    ...fixture,
    exploratory: {
      ...fixture.exploratory,
      recordings: fixture.exploratory.recordings.map((r, i) => ({
        ...r,
        automatic_alignment: {
          words: [
            {
              token_index: 0,
              start_s: i === 0 ? 9.2 : 8,
              end_s: i === 0 ? 9.8 : 11,
            },
          ],
        },
      })),
    },
    anomalies: [
      {
        id: "anomaly",
        recording_id: "part",
        before_token_index: 0,
        before_word: { label: "previous", start_s: 8, end_s: 11 },
        after_word: { label: "example", start_s: 13, end_s: 13.8 },
        gap: { start_s: 11, end_s: 13 },
        context: { start_s: 8, end_s: 13.8 },
        measurement: { low_energy_s: 0, observed_s: 2, complete: true },
        reason: "Generated presentation anomaly",
      },
    ],
    inspection_order: [
      {
        id: "item",
        category: "alignment_anomaly",
        evidence_id: "anomaly",
        order_reason: "Inspectable gap context",
      },
    ],
  } as unknown as ComparativeReport;
  render(<ComparativeInsights report={report} onSeek={seek} />);
  fireEvent.click(screen.getByRole("button", { name: "Listen to reference" }));
  expect(seek).toHaveBeenLastCalledWith("ref", 9.2, 10.5, true);
  fireEvent.click(
    screen.getByRole("button", { name: "Listen to participant" }),
  );
  expect(seek).toHaveBeenLastCalledWith("part", 8, 13.8, true);
});

it("plays corresponding native gap intervals independently and returns to full recordings", () => {
  const seek = vi.fn();
  render(<ComparativeInsights report={fixture} onSeek={seek} />);
  fireEvent.click(screen.getByRole("button", { name: "Listen to reference" }));
  expect(seek).toHaveBeenLastCalledWith("ref", 9.8, 10.5, true);
  fireEvent.click(
    screen.getByRole("button", { name: "Listen to participant" }),
  );
  expect(seek).toHaveBeenLastCalledWith("part", 11, 13.8, true);
  fireEvent.click(
    screen.getByRole("button", {
      name: "Return to complete participant recording",
    }),
  );
  expect(seek).toHaveBeenLastCalledWith("part", 0);
});

it("retains actual deltas, selection reason, full evidence and versioned JSON export", () => {
  render(<ComparativeInsights report={fixture} onSeek={vi.fn()} />);
  expect(screen.getByText(/Participant minus reference gap/)).toHaveTextContent(
    "1.800 s",
  );
  fireEvent.click(screen.getByText("Inspect evidence and selection reason"));
  expect(screen.getByText("Larger measured gap; not confidence")).toBeVisible();
  fireEvent.click(
    screen.getByText(
      "Comparative evidence — all groups and provisional measurements",
    ),
  );
  expect(screen.getByText(/No reviewed phrase partition/)).toBeVisible();
  expect(
    screen.getByRole("link", { name: "Export comparative JSON" }),
  ).toHaveAttribute("href", "/api/v1/analyses/job/insights/export");
});

it("abstains without paired intervals and does not fabricate scores", () => {
  render(
    <ComparativeInsights
      report={{
        ...fixture,
        segments: [],
        inspection_order: [],
        correspondence_unavailable_reason: "Incomplete indexed text; withheld",
      }}
      onSeek={vi.fn()}
    />,
  );
  expect(screen.getByText(/No supported local differences/)).toBeVisible();
  expect(screen.getByText("Incomplete indexed text; withheld")).toBeVisible();
  expect(
    screen.queryByRole("button", {
      name: "Listen to participant",
    }),
  ).toBeNull();
  expect(screen.queryByText(/\/ 100|confidence: \d/)).toBeNull();
});

it("keeps reference-only groups on their own recording clocks", () => {
  const seek = vi.fn();
  const group = {
    id: "group",
    recording_id: "ref",
    kind: "energy_change",
    direction: "increase",
    start_s: 1,
    end_s: 2,
    candidate_ids: ["c1", "c2"],
    representative_delta_db: 7,
    delta_range_db: [6, 8],
    median_energy_range_dbfs: [-32, -30],
    detection: {
      boundary_resolution_s: 0.01,
      frame_window_s: 0.025,
      method: "fixture",
      threshold_delta_db: 6,
    },
    limitation: "Unverified",
  };
  render(
    <ComparativeInsights
      report={
        {
          ...fixture,
          exploratory: {
            ...fixture.exploratory,
            pair_id: null,
            recordings: fixture.exploratory.recordings.slice(0, 1),
          },
          segments: [],
          groups: [group],
          inspection_order: [
            {
              id: "i",
              category: "group",
              evidence_id: "group",
              quality_limited: false,
              order_reason: "Group support duration",
            },
          ],
        } as unknown as ComparativeReport
      }
      onSeek={seek}
    />,
  );
  expect(screen.getByText(/2 connected windows/)).toBeVisible();
  fireEvent.click(
    screen.getByRole("button", { name: "Inspect grouped interval" }),
  );
  expect(seek).toHaveBeenLastCalledWith("ref", 1, 2);
  expect(
    screen.queryByRole("button", {
      name: "Listen to participant",
    }),
  ).toBeNull();
});
