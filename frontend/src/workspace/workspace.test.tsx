import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import userEvent from "@testing-library/user-event";
import type { Recording, Region, Report } from "../api";
import { Inspector, Scores } from "./Evidence";
import { sampleAtTime, timeAtPosition, Timeline } from "./Timeline";
import { ImportForm } from "./ImportForm";

vi.mock("uplot", () => ({
  default: class {
    setSize() {}
    destroy() {}
  },
}));
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

// Component-only fixtures. These are not runtime reports, speech or human review claims.
const report: Report = {
  kind: "comparison",
  schema_version: 1,
  pair_id: null,
  dataset_version: "software-fixture",
  dataset_sha256: "0".repeat(64),
  implementation_sha256: "0".repeat(64),
  policy: {
    version: "delivery-v0",
    algorithm: "contrastive-v1",
    numerical_epsilon: 1e-12,
    pacing_tolerance: Math.log(1.15),
    pacing_width: 0.4054651081081644,
    pause_floor_s: 0.15,
    pause_relative: 0.25,
    pause_width_s: 0.75,
    pause_calibrated_tolerance_s: 0,
    energy_tolerance_db: 3,
    energy_width_db: 6,
    pitch_tolerance_st: 2,
    pitch_width_st: 4,
    contour_energy_tolerance_db: 6,
    contour_pitch_tolerance_st: 3,
    minimum_coverage: 0.8,
    minimum_pitch_fraction: 0.5,
    minimum_phrase_s: 0.5,
    minimum_phrase_words: 3,
    minimum_phrases: 2,
    minimum_gaps: 5,
    weights: {
      pacing: 0.25,
      pause_behavior: 0.25,
      energy_variation: 0.25,
      pitch_dynamics: 0.25,
    },
    frozen: false,
    calibration_group_ids: [],
    validation_group_ids: [],
  },
  policy_sha256: "0".repeat(64),
  inputs: [],
  eligibility: {
    state: "INELIGIBLE",
    reasons: [
      {
        code: "pair_missing",
        message: "No participant mirror/pair is available.",
      },
    ],
  },
  feature_eligibility: {
    pacing: {
      state: "INELIGIBLE",
      reasons: [
        { code: "transcript_unverified", message: "Transcript is unverified." },
      ],
    },
    pause_behavior: { state: "REVIEW_REQUIRED" },
    energy_variation: { state: "REVIEW_REQUIRED" },
    pitch_dynamics: { state: "INELIGIBLE" },
  },
  observations: [],
  regions: [],
  dimensions: [
    "pacing",
    "pause_behavior",
    "energy_variation",
    "pitch_dynamics",
  ].map((dimension) => ({
    dimension: dimension as Report["dimensions"][number]["dimension"],
    score: null,
    coverage: 0,
    eligible_count: 0,
    expected_count: 0,
    eligible_weight: 0,
    expected_weight: 0,
    weighted_penalty: 0,
    reasons: [{ code: "score_count", message: "Insufficient observations." }],
  })),
  overall_score: null,
  abstention_reasons: [],
  limitations: ["Fixture only; no statistical confidence."],
};

describe("native timeline coordinates", () => {
  it("maps viewport positions to native seconds and samples", () => {
    expect(timeAtPosition(250, 1000, 2, 6)).toBe(3);
    expect(sampleAtTime(3)).toBe(48000);
    expect(timeAtPosition(-1, 1000, 2, 6)).toBe(2);
    expect(timeAtPosition(1500, 1000, 2, 6)).toBe(6);
  });
  it("does not equate native timestamps across different durations", () => {
    expect(timeAtPosition(500, 1000, 0, 10)).toBe(5);
    expect(timeAtPosition(500, 1000, 0, 20)).toBe(10);
  });
});
it("shows unavailable scores and never redistributes weights", () => {
  render(<Scores report={report} />);
  expect(screen.getByText("Overall: Unavailable")).toBeInTheDocument();
  expect(screen.getAllByText("25%")).toHaveLength(4);
  expect(screen.getByText(/Transcript is unverified/)).toBeInTheDocument();
  expect(screen.queryByText("100.0")).not.toBeInTheDocument();
});
it("explains that zero regions is not a perfect result", () => {
  render(<Inspector report={report} region={null} />);
  expect(
    screen.getByText(
      /Zero detected regions does not indicate a perfect performance/,
    ),
  ).toBeInTheDocument();
});
it("displays numeric observation evidence and boundary events directly", () => {
  const region: Region = {
    id: "fixture-region",
    category: "pause_behavior",
    detector: "rubric",
    participant_interval: null,
    participant_anchor_s: 2,
    reference_interval: { start_s: 1, end_s: 2 },
    reference_anchor_s: null,
    token_span: [0, 2],
    observation_ids: ["fixture-observation"],
    severity: 2,
    confidence_reason: "not_calibrated",
    reliability: "reviewed",
    eligibility: { state: "ELIGIBLE" },
    explanation: {
      plain: "Computed fixture pause difference.",
      causal_scope: "calculation_only",
      technical: "excess = 0.6; fixture only",
      suggested_review: "Replay this boundary.",
    },
  };
  const data: Report = {
    ...report,
    regions: [region],
    observations: [
      {
        id: "fixture-observation",
        dimension: "pause_behavior",
        detector: "rubric",
        token_span: [0, 2],
        participant_interval: null,
        participant_anchor_s: 2,
        reference_interval: { start_s: 1, end_s: 2 },
        unit: "s",
        reference: 1,
        participant: 0,
        delta: -1,
        tolerance: 0.4,
        saturation_width: 0.75,
        normalized_deviation: -2.5,
        excess: 0.6,
        penalty: 0.8,
        weight: 1,
        scored: true,
        eligibility: { state: "ELIGIBLE" },
      },
    ],
  };
  render(<Inspector report={data} region={region} />);
  expect(screen.getByText("Boundary at 2.000 s")).toBeInTheDocument();
  expect(screen.getByText("-1.000000 s")).toBeInTheDocument();
  expect(screen.getByText("0.400000 / 0.750000")).toBeInTheDocument();
  expect(
    screen.getByText("Computed fixture pause difference."),
  ).toBeInTheDocument();
});
it("import begins with unverified text and no invented approvals", async () => {
  const user = userEvent.setup();
  render(<ImportForm recordings={[]} onImported={() => {}} />);
  expect(
    screen.getByText(/Imported text remains unverified/),
  ).toBeInTheDocument();
  expect(
    screen.getByLabelText(
      "I have evidence permitting adaptation and public redistribution",
    ),
  ).not.toBeChecked();
  expect(screen.getByLabelText("Audio file")).toBeRequired();
  expect(screen.getByLabelText("Spoken transcript")).toBeRequired();
  await user.tab();
  expect(screen.getByLabelText("Recording role")).toHaveFocus();
});
it("seeks actual native audio and exposes numeric interval controls", async () => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        start_s: 0,
        end_s: 2,
        sample_rate_hz: 16000,
        aggregation: "sample_min_max",
        bins: [[0, 32000, -0.2, 0.2]],
      }),
    }),
  );
  const item = {
    id: "fixture",
    role: "reference",
    original_filename: "generated-fixture.wav",
    normalized_info: { duration_s: 2 },
  } as Recording;
  const onPlay = vi.fn();
  render(
    <Timeline
      recording={item}
      job={null}
      regions={[]}
      selected={null}
      seek={null}
      onSelect={() => {}}
      onPlay={onPlay}
    />,
  );
  fireEvent.change(screen.getByLabelText("Seek reference"), {
    target: { value: "1.25" },
  });
  const audio = screen.getByLabelText("reference audio") as HTMLAudioElement;
  await waitFor(() => expect(audio.currentTime).toBe(1.25));
  fireEvent.play(audio);
  expect(onPlay).toHaveBeenCalledWith(audio);
  expect(screen.getByText(/sample 20000/)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Selection start (s)"), {
    target: { value: ".5" },
  });
  expect(screen.getByText("Selection 1.500 s")).toBeInTheDocument();
});
