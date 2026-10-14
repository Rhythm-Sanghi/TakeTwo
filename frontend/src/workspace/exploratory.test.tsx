import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import type { ExploratoryReport } from "../api";
import { ExploratoryResult } from "./ExploratoryResult";
import { exploratoryMatchesSelection } from "./analysisContext";
import type { Job, Recording } from "../api";

afterEach(cleanup);
// Presentation fixtures only; never stored as acoustic or human evidence.
const fixture = {
  job_id: "fixture-job",
  reference_id: "reference",
  pair_id: null,
  config: { method: "exploratory-v1" },
  state: "partial",
  recordings: [],
  comparison: null,
  candidates: [],
  automatic_correspondence: [],
  unavailable_recordings: { reference: "Feature extraction failed." },
  limitations: ["Automatic observations do not establish speaking quality."],
} as unknown as ExploratoryReport;

it("offers recovery when browser printing fails and restores the report scope", () => {
  const print = vi.spyOn(window, "print").mockImplementation(() => {
    throw new Error("Blocked");
  });
  render(<ExploratoryResult report={fixture} onSeek={vi.fn()} />);
  fireEvent.click(
    screen.getByRole("button", {
      name: "Export Full Evidence Report / save PDF",
    }),
  );
  expect(screen.getByRole("alert")).toHaveTextContent("Retry the export");
  expect(document.body.dataset.reportMode).toBeUndefined();
  print.mockImplementation(() => {});
  fireEvent.click(
    screen.getByRole("button", {
      name: "Export Full Evidence Report / save PDF",
    }),
  );
  expect(screen.queryByRole("alert")).toBeNull();
  dispatchEvent(new Event("afterprint"));
  print.mockRestore();
});

it("explains partial data and empty candidates without inventing scores", () => {
  render(<ExploratoryResult report={fixture} onSeek={vi.fn()} />);
  expect(screen.getByRole("status")).toHaveTextContent(
    "Feature extraction failed",
  );
  expect(screen.getByText(/No intervals meet/)).toHaveTextContent(
    "not a delivery assessment",
  );
  expect(
    screen.getByRole("link", { name: "Export exploratory JSON" }),
  ).toHaveAttribute(
    "href",
    "/api/v1/analyses/fixture-job/exploratory/export?format=json",
  );
  expect(screen.queryByText(/\/ 100/)).toBeNull();
});

it("uses the candidate's native recording interval for inspect and replay", () => {
  const seek = vi.fn();
  render(
    <ExploratoryResult
      report={
        {
          ...fixture,
          candidates: [
            {
              id: "candidate",
              recording_id: "reference",
              kind: "internal_low_energy",
              start_s: 0.5,
              end_s: 0.75,
              duration_s: 0.25,
              median_energy_dbfs: -45,
              explanation: "Measured low energy",
              limitation: "Unverified",
              method: "activity mask",
            },
          ],
        } as ExploratoryReport
      }
      onSeek={seek}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Inspect interval" }));
  expect(seek).toHaveBeenLastCalledWith("reference", 0.5, 0.75);
  fireEvent.click(screen.getByRole("button", { name: "Replay interval" }));
  expect(seek).toHaveBeenLastCalledWith("reference", 0.5, 0.75, true);
});

it("rejects stale source hashes and duplicate members even when recording IDs match", () => {
  const recording = {
    id: "reference",
    normalized_sha256: "audio",
    sample_sha256: "samples",
    transcript_sha256: "text",
    normalized_info: { duration_s: 2 },
  } as Recording;
  const job = {
    id: "fixture-job",
    request: { reference_id: "reference", pair_id: null },
  } as Job;
  const source = {
    recording_id: "reference",
    duration_s: 2,
    provenance: {
      audio_sha256: "audio",
      sample_sha256: "samples",
      transcript_sha256: "text",
    },
  };
  const report = { ...fixture, recordings: [source] } as ExploratoryReport;
  expect(exploratoryMatchesSelection(report, job, recording, null)).toBe(true);
  expect(
    exploratoryMatchesSelection(
      {
        ...report,
        recordings: [
          {
            ...source,
            provenance: { ...source.provenance, audio_sha256: "changed" },
          },
        ],
      } as ExploratoryReport,
      job,
      recording,
      null,
    ),
  ).toBe(false);
  expect(
    exploratoryMatchesSelection(
      { ...report, recordings: [source, source] } as ExploratoryReport,
      job,
      recording,
      null,
    ),
  ).toBe(false);
  expect(
    exploratoryMatchesSelection(
      report,
      { ...job, id: "different" },
      recording,
      null,
    ),
  ).toBe(false);
});
