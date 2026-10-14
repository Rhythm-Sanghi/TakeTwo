import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import userEvent from "@testing-library/user-event";
import type { Evaluation, Job, Recording, Region, Report } from "../api";
import {
  AnalysisResult,
  assessmentTitle,
  Findings,
  hasIndependentEvaluation,
} from "./AnalysisResult";
import { ReviewJourney } from "./ReviewJourney";
import { Inspector, Scores } from "./Evidence";
import {
  FeatureChart,
  sampleAtTime,
  timeAtPosition,
  Timeline,
} from "./Timeline";
import { ImportForm } from "./ImportForm";
import { ExcerptForm } from "./RecordingTools";
import { DatasetReadiness } from "./DatasetReadiness";
import type { DatasetSummary } from "./DatasetReadiness";
import { ReviewWorkspace } from "./ReviewWorkspace";
import { reportMatchesSelection } from "./analysisContext";
import { WorkspaceNavigation, workspacePages } from "./WorkspaceNavigation";

it("requires a deliberate recording type without changing contract choices", async () => {
  const fetch = vi.fn();
  vi.stubGlobal("fetch", fetch);
  render(<ImportForm recordings={[]} onImported={() => {}} />);
  const selector = screen.getByLabelText("Recording type");
  expect(selector).toHaveValue("");
  expect(selector).toBeRequired();
  expect(
    screen.getByRole("button", { name: "Import recording" }),
  ).toBeDisabled();
  fireEvent.submit(screen.getByRole("form", { name: "Import recording" }));
  expect(fetch).not.toHaveBeenCalled();
  expect(screen.getByRole("alert")).toHaveTextContent(
    "Choose the recording type",
  );
  await userEvent.selectOptions(selector, "public_reference");
  expect(selector).toHaveValue("public_reference");
  expect(
    screen.getByRole("button", { name: "Import recording" }),
  ).toBeEnabled();
});

it("exposes all five areas in the compact workspace selector", async () => {
  const navigate = vi.fn();
  render(
    <WorkspaceNavigation current="Analysis Workspace" onNavigate={navigate} />,
  );
  const selector = screen.getByRole("combobox", {
    name: "Workspace",
  });
  expect(selector).toHaveValue("Analysis Workspace");
  for (const page of workspacePages) {
    await userEvent.selectOptions(selector, page);
    expect(navigate).toHaveBeenLastCalledWith(page);
  }
  expect(
    screen.getByRole("button", { name: "Analysis Workspace" }),
  ).toHaveAttribute("aria-current", "page");
});

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

it("retains recovery guidance when an excerpt is saved but inventory refresh fails", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ id: "test-cut" }) }),
  );
  const onSaved = vi
    .fn()
    .mockRejectedValue(
      new Error(
        "Recording was stored but inventory refresh failed. Reconnect / refresh; do not re-import.",
      ),
    );
  render(
    <ExcerptForm
      maximumDuration={45}
      recording={
        {
          id: "test-parent",
          role: "reference",
          origin: "self_recorded",
        } as Recording
      }
      selection={[0, 1]}
      references={[]}
      onSaved={onSaved}
    />,
  );
  await userEvent.click(
    screen.getByText("Save selection as an analysis excerpt"),
  );
  await userEvent.type(
    screen.getByLabelText("Exact excerpt transcript"),
    "Fixture words.",
  );
  await userEvent.click(screen.getByRole("button", { name: "Save excerpt" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "do not re-import",
  );
  expect(onSaved).toHaveBeenCalledTimes(1);
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

it("leads withheld scores with recovery language and keeps codes in diagnostics", () => {
  const message =
    "This comparison needs two completed timing reviews before pacing can be evaluated.";
  render(
    <Scores
      report={{
        ...report,
        feature_eligibility: {
          ...report.feature_eligibility,
          pacing: {
            state: "REVIEW_REQUIRED",
            reasons: [{ code: "timing_review_required", message }],
          },
        },
      }}
    />,
  );
  fireEvent.click(screen.getByText("pacing · detailed eligibility"));
  expect(screen.getByText(message)).toBeVisible();
  expect(screen.getByText("timing_review_required")).not.toBeVisible();
  fireEvent.click(screen.getAllByText("Diagnostic reason codes")[0]);
  expect(screen.getByText("timing_review_required")).toBeVisible();
});

it("deduplicates shared blockers while preserving dimension diagnostics", () => {
  const reason = {
    code: "transcript_unverified",
    message: "Verify the exact spoken text.",
  };
  render(
    <Scores
      report={{
        ...report,
        eligibility: { state: "REVIEW_REQUIRED", reasons: [reason] },
        feature_eligibility: Object.fromEntries(
          Object.keys(report.feature_eligibility).map((name) => [
            name,
            { state: "REVIEW_REQUIRED", reasons: [reason, reason] },
          ]),
        ) as Report["feature_eligibility"],
      }}
    />,
  );
  expect(screen.getAllByText(reason.message)).toHaveLength(1);
  expect(screen.getByText("Comparison awaiting review")).toBeVisible();
  expect(
    screen.getByText("pacing · detailed eligibility").parentElement,
  ).not.toHaveAttribute("open");
  fireEvent.click(screen.getByText("pacing · detailed eligibility"));
  expect(
    screen.getAllByText(/Scientific eligibility: REVIEW REQUIRED/)[0],
  ).toBeVisible();
});

it.each([0.8, 0.006, 0, null])(
  "labels accepted-frame pitch as diagnostic at coverage %s",
  (fraction) => {
    const input = {
      origin: "self_recorded",
      provenance: { recording_id: "fixture", transcript_verified: false },
      duration_s: 30,
      spectral_frame_count: 2998,
      pitch_valid_fraction: fraction ?? 0,
      pitch_baseline_hz: fraction === null ? null : 186.7,
      feature_config: { voicing_threshold: 0.8 },
      energy_baseline_dbfs: -30,
      quality: { rms: 0.1, peak: 0.2 },
      reviews: [],
      features: { sha256: "0".repeat(64) },
    } as unknown as Report["inputs"][number];
    const view = render(
      <Inspector region={null} report={{ ...report, inputs: [input] }} />,
    );
    const evidence = within(
      view.container.querySelector(".input-evidence") as HTMLElement,
    );
    expect(
      evidence.getByText("Pitch baseline — diagnostic only"),
    ).toBeVisible();
    expect(
      evidence.getByText(`${((fraction ?? 0) * 100).toFixed(2)}%`),
    ).toBeVisible();
    expect(
      evidence.getByText(/Required reliable coverage: 50% per scored phrase/),
    ).toBeVisible();
    if (fraction !== null)
      expect(
        screen.getByText(/186.7 Hz · median of accepted F0 frames only/),
      ).toBeVisible();
    if ((fraction ?? 0) < 0.5)
      expect(
        screen.getByText(
          /Pitch scoring unavailable: insufficient reliable voiced frames/,
        ),
      ).toBeVisible();
  },
);

it("uses backend inventory and opens operator preparation without granting access", async () => {
  const onReview = vi.fn();
  const recordings = [
    {
      id: "fixture-take",
      original_filename: "tone.wav",
      role: "participant",
      normalized_info: { duration_s: 2 },
    },
  ] as Recording[];
  const readiness = {
    recording_id: "fixture-take",
    next_action: "transcript",
    review_scope: "transcript",
    message: "Complete independent transcript checks.",
    review_status: { transcript: "One assertion; another required" },
  } as const;
  const summary = {
    inventory_counts: {
      human_participant_takes: 4,
      distinct_speaker_ids: 1,
      connected_families: 1,
      verified_transcripts: 0,
    },
    review_readiness: [readiness],
  } as unknown as DatasetSummary;
  const view = render(
    <DatasetReadiness
      summary={summary}
      recordings={recordings}
      selectedId="fixture-take"
      onSelect={vi.fn()}
      onReview={onReview}
    />,
  );
  await userEvent.click(
    screen.getByText("Details · recording inventory and review assertions"),
  );
  expect(
    screen.getByRole("row", { name: "Human-recorded participant takes 4" }),
  ).toBeVisible();
  expect(
    screen.getByRole("row", { name: "Distinct recorded speaker IDs 1" }),
  ).toBeVisible();
  expect(
    screen.getByRole("row", { name: "Verified transcripts 0" }),
  ).toBeVisible();
  await userEvent.click(
    screen.getByRole("button", { name: "Open Review Workspace" }),
  );
  expect(onReview).toHaveBeenCalledWith(readiness);
  view.unmount();
  const fetcher = vi.fn();
  vi.stubGlobal("fetch", fetcher);
  render(
    <ReviewWorkspace
      recordings={recordings}
      jobs={[]}
      pairs={[]}
      initial={readiness}
    />,
  );
  expect(screen.getByLabelText("Recording", { exact: true })).toHaveValue(
    "fixture-take",
  );
  expect(
    screen.getByRole("textbox", { name: "Reviewer identifier" }),
  ).toHaveAccessibleDescription("An identity declaration, not authentication.");
  expect(
    screen.getByRole("button", { name: "Start reviewer handoff" }),
  ).toBeDisabled();
  expect(fetcher).not.toHaveBeenCalled();
});

it("retains independently available dimensions when pitch eligibility is absent", () => {
  render(
    <Scores
      report={{
        ...report,
        feature_eligibility: {
          ...report.feature_eligibility,
          pitch_dynamics: undefined,
        } as unknown as Report["feature_eligibility"],
        dimensions: report.dimensions.map((d) =>
          d.dimension === "energy_variation"
            ? {
                ...d,
                score: 72,
                coverage: 1,
                eligible_count: 2,
                expected_count: 2,
              }
            : d,
        ),
      }}
    />,
  );
  expect(screen.getByText("72.0")).toBeVisible();
  expect(screen.getByText("Overall: Unavailable")).toBeVisible();
});

it("handles absent analysis and absent pitch input measurements without inventing a baseline", () => {
  const view = render(<Inspector report={null} region={null} />);
  expect(
    screen.getByText("Run analysis to inspect measured evidence."),
  ).toBeVisible();
  view.rerender(<Inspector report={report} region={null} />);
  expect(screen.queryByText(/Hz/)).not.toBeInTheDocument();
});

it("keeps empty and entirely missing chart series unavailable", () => {
  const data = {
    name: "f0",
    unit: "Hz",
    times_s: [],
    values: [],
    frame_length: 1024,
    hop_length: 160,
    aggregation: "native_frames",
  } as unknown as import("../api").FeatureWindow;
  const view = render(
    <FeatureChart data={data} start={0} end={30} role="reference" />,
  );
  expect(
    screen.getByText(/Pitch evidence unavailable: no reliable frames/),
  ).toBeVisible();
  expect(view.container.querySelector(".chart-plot")).toBeNull();
  view.rerender(
    <FeatureChart
      data={{ ...data, times_s: [0.032, 29.962], values: [null, null] }}
      start={0}
      end={30}
      role="reference"
    />,
  );
  expect(view.container.querySelector(".chart-plot")).toBeNull();
  expect(screen.getByText(/0.000–30.000 s/)).toBeVisible();
});

it("distinguishes a loading inventory from an actual empty dataset", () => {
  const props = {
    recordings: [],
    selectedId: "",
    onSelect: vi.fn(),
    onReview: vi.fn(),
  };
  const view = render(<DatasetReadiness {...props} summary={null} loading />);
  expect(
    screen.getByText("Loading dataset inventory and review readiness…"),
  ).toBeVisible();
  expect(
    screen.queryByText(/Import a permitted recording before/),
  ).not.toBeInTheDocument();
  view.rerender(
    <DatasetReadiness
      {...props}
      summary={
        {
          inventory_counts: {},
          review_readiness: [],
        } as unknown as DatasetSummary
      }
    />,
  );
  expect(screen.getByText(/Import a permitted recording before/)).toBeVisible();
});

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
  expect(screen.getByLabelText("Recording type")).toHaveFocus();
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
    origin: "source",
    transcript: { status: "unverified" },
    normalized_info: { duration_s: 2 },
  } as Recording;
  const onPlay = vi.fn();
  const view = render(
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
  fireEvent.click(screen.getByText("Precision selection and interval replay"));
  fireEvent.change(screen.getByLabelText("reference selection start (s)"), {
    target: { value: ".5" },
  });
  expect(screen.getByText("Selection 1.500 s")).toBeInTheDocument();
  const play = vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue();
  const pause = vi
    .spyOn(HTMLMediaElement.prototype, "pause")
    .mockImplementation(() => {});
  fireEvent.change(screen.getByLabelText("reference selection end (s)"), {
    target: { value: "1" },
  });
  fireEvent.click(
    screen.getByRole("button", { name: "Replay selected interval" }),
  );
  expect(play).toHaveBeenCalled();
  expect(audio.currentTime).toBe(0.5);
  audio.currentTime = 1.1;
  fireEvent.timeUpdate(audio);
  expect(pause).toHaveBeenCalledOnce();
  expect(audio.currentTime).toBe(1);
  fireEvent.change(screen.getByLabelText("Seek reference"), {
    target: { value: "1.25" },
  });
  fireEvent.timeUpdate(audio);
  expect(audio.currentTime).toBe(1.25);
  await waitFor(() =>
    expect(
      screen.getByRole("img", { name: /Measured reference waveform/ }),
    ).toBeVisible(),
  );
  vi.mocked(fetch).mockReturnValue(new Promise(() => {}));
  view.rerender(
    <Timeline
      recording={{ ...item, id: "another-recording" }}
      job={null}
      regions={[]}
      selected={null}
      seek={null}
      onSelect={() => {}}
      onPlay={onPlay}
    />,
  );
  expect(screen.getByText("Loading reference waveform…")).toBeInTheDocument();
  expect(
    screen.queryByRole("img", { name: /Measured reference waveform/ }),
  ).not.toBeInTheDocument();
});

it("keeps human participant type visible before a reference exists", async () => {
  const user = userEvent.setup();
  render(<ImportForm recordings={[]} onImported={() => {}} />);
  await user.selectOptions(
    screen.getByLabelText("Recording type"),
    "human_participant",
  );
  expect(
    screen.getByText(/Import a public or self-recorded reference first/),
  ).toBeVisible();
  expect(
    screen.getByRole("button", { name: "Import recording" }),
  ).toBeDisabled();
});

it("discloses advanced provenance and supports controlled local drafts without IDs", async () => {
  const user = userEvent.setup();
  render(<ImportForm recordings={[]} onImported={() => {}} />);
  await user.selectOptions(
    screen.getByLabelText("Recording type"),
    "controlled_reference",
  );
  expect(screen.getByText(/does not replace the public-speaker/)).toBeVisible();
  expect(screen.getByLabelText("Rights holder")).not.toBeVisible();
  expect(screen.queryByLabelText("Speech family ID")).not.toBeInTheDocument();
  expect(screen.queryByLabelText("Source ID")).not.toBeInTheDocument();
  expect(
    screen.getByLabelText(
      "I have permission to store and process this recording locally",
    ),
  ).toBeRequired();
  expect(
    screen.getByLabelText(
      "I have permission to store and process this recording locally",
    ),
  ).not.toBeChecked();
  await user.click(screen.getByText("Rights and permissions", { exact: true }));
  expect(screen.getByLabelText("Rights holder")).toBeVisible();
});

it("submits an unverified private draft without fictional rights or severity", async () => {
  const user = userEvent.setup();
  const fetcher = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      id: "fixture",
      original_filename: "generated.wav",
      provenance: { rights: { status: "pending" } },
    }),
  });
  vi.stubGlobal("fetch", fetcher);
  const imported = vi.fn();
  render(<ImportForm recordings={[]} onImported={imported} />);
  await user.selectOptions(
    screen.getByLabelText("Recording type"),
    "controlled_reference",
  );
  await user.upload(
    screen.getByLabelText("Audio file"),
    new File(["test-only bytes"], "generated.wav", { type: "audio/wav" }),
  );
  expect(
    (screen.getByLabelText("Audio file") as HTMLInputElement).files,
  ).toHaveLength(1);
  await user.type(
    screen.getByLabelText("Spoken transcript"),
    "Generated software fixture.",
  );
  await user.click(
    screen.getByLabelText(
      "I have permission to store and process this recording locally",
    ),
  );
  // jsdom's required-file validity does not recognize the user-event FileList.
  // Actual Chromium acceptance checks native validation; this checks the submitted contract.
  fireEvent.submit(screen.getByRole("form", { name: "Import recording" }));
  await waitFor(() => expect(imported).toHaveBeenCalled());
  const body = fetcher.mock.calls[0][1].body as FormData;
  const metadata = JSON.parse(String(body.get("metadata")));
  expect(metadata.recording_type).toBe("controlled_reference");
  expect(metadata.rights).toBeNull();
  expect(metadata.severity).toBeNull();
  expect(metadata.category).toBe("unspecified");
  expect(metadata).not.toHaveProperty("speaker_id");
  expect(metadata).not.toHaveProperty("verification_date");
});

it.each([
  [45, 44.9999375, true],
  [45, 45, true],
  [45, 45.0000625, false],
  [12, 12, true],
  [12, 12.0000625, false],
  [undefined, 1, false],
])("uses server budget %s for a %s second selection", (limit, end, enabled) => {
  render(
    <ExcerptForm
      maximumDuration={limit}
      recording={
        { id: "fixture", role: "reference", origin: "source" } as Recording
      }
      selection={[0, end as number]}
      references={[]}
    />,
  );
  fireEvent.click(screen.getByText("Save selection as an analysis excerpt"));
  const button = screen.getByRole("button", { name: "Save excerpt" });
  if (enabled) expect(button).toBeEnabled();
  else expect(button).toBeDisabled();
});

it("keeps processing, missing evidence, partial results and eligible zero findings distinct", () => {
  const job = { state: "completed" } as Job;
  expect(assessmentTitle(null, null, false)).toBe("Audio not processed.");
  for (const state of ["queued", "running", "failed", "cancelled"] as const)
    expect(assessmentTitle({ ...job, state }, report, false)).not.toContain(
      "results available",
    );
  expect(assessmentTitle(job, null, true)).toContain("Loading assessment");
  expect(assessmentTitle(job, null, false)).toContain("evidence unavailable");
  expect(
    assessmentTitle(
      job,
      { ...report, eligibility: { state: "ELIGIBLE" } },
      false,
    ),
  ).toBe("Eligible evidence available. Overall assessment unavailable.");
  expect(assessmentTitle(job, report, false)).toBe(
    "Audio analysis complete. Delivery assessment unavailable.",
  );
  expect(
    assessmentTitle(
      job,
      { ...report, eligibility: { state: "REVIEW_REQUIRED" } },
      false,
    ),
  ).toBe("Audio analysis complete. Delivery assessment awaiting verification.");
  expect(
    assessmentTitle(
      job,
      { ...report, dimensions: [{ ...report.dimensions[0], score: 70 }] },
      false,
    ),
  ).toContain("Some dimensions available");
  const onNext = vi.fn();
  const view = render(
    <AnalysisResult
      job={job}
      report={report}
      loading={false}
      evaluations={[]}
      onNext={onNext}
      nextLabel="Check requirements"
    />,
  );
  expect(screen.queryByText(/100/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Check requirements" }));
  expect(onNext).toHaveBeenCalledOnce();
  view.rerender(
    <Findings report={report} onSelect={vi.fn()} onReplay={vi.fn()} />,
  );
  expect(screen.getByText(/Findings pending/)).toBeVisible();
  view.rerender(
    <Findings
      report={{
        ...report,
        eligibility: { state: "ELIGIBLE" },
        overall_score: 100,
      }}
      onSelect={vi.fn()}
      onReplay={vi.fn()}
    />,
  );
  expect(screen.getByText(/No threshold crossings/)).toBeVisible();
  expect(screen.queryByText(/Findings pending/)).not.toBeInTheDocument();
});

it.each([0, 2])(
  "presents completed reference inspection honestly with %s existing pairs",
  (availablePairCount) => {
    render(
      <AnalysisResult
        job={{ state: "completed" } as Job}
        report={report}
        reference={
          { id: "reference", original_filename: "reference.wav" } as Recording
        }
        referenceOnly
        availablePairCount={availablePairCount}
        loading={false}
        evaluations={[]}
        nextLabel={
          availablePairCount ? "Select a participant" : "Add a participant"
        }
        onNext={vi.fn()}
      />,
    );
    expect(
      screen.getByRole("heading", {
        name: "Reference audio analysis complete",
      }),
    ).toBeVisible();
    expect(
      screen.getByText(
        "Reference measurements are available. No participant comparison was run.",
      ),
    ).toBeVisible();
    expect(
      screen.queryByText(
        /Delivery assessment|both recordings|No participant mirror/,
      ),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: availablePairCount ? "Select a participant" : "Add a participant",
      }),
    ).toBeEnabled();
  },
);

it("keeps reference pending, failed, missing measurements and comparison selection separate", () => {
  expect(assessmentTitle(null, null, false, true)).toContain(
    "Participant comparison pending selection",
  );
  expect(assessmentTitle({ state: "running" } as Job, null, false, true)).toBe(
    "Reference audio analysis in progress.",
  );
  expect(assessmentTitle({ state: "failed" } as Job, null, false, true)).toBe(
    "Reference audio analysis failed.",
  );
  expect(
    assessmentTitle({ state: "completed" } as Job, null, true, true),
  ).toContain("Loading measurements");
  expect(
    assessmentTitle({ state: "completed" } as Job, null, false, true),
  ).toContain("Measurements unavailable");
});

it("rejects mismatched report pair, reference, participant and incomplete inputs", () => {
  const input = (id: string) =>
    ({ provenance: { recording_id: id } }) as Report["inputs"][number];
  const job = { request: { reference_id: "r", pair_id: "pair" } } as Job;
  const paired = {
    ...report,
    pair_id: "pair",
    inputs: [input("r"), input("p")],
  };
  expect(reportMatchesSelection(paired, job, "r", "pair", "p")).toBe(true);
  expect(reportMatchesSelection(paired, job, "r", null)).toBe(false);
  expect(reportMatchesSelection(paired, job, "other", "pair", "p")).toBe(false);
  expect(reportMatchesSelection(paired, job, "r", "pair", "other")).toBe(false);
  expect(
    reportMatchesSelection(
      { ...paired, inputs: [input("r")] },
      job,
      "r",
      "pair",
      "p",
    ),
  ).toBe(false);
  expect(
    reportMatchesSelection({ ...paired, pair_id: null }, job, "r", "pair", "p"),
  ).toBe(false);
  expect(
    reportMatchesSelection(
      { ...paired, pair_id: null, inputs: [input("r")] },
      { request: { reference_id: "r", pair_id: null } } as Job,
      "r",
      null,
    ),
  ).toBe(true);
});

it("binds independent evaluation to report, dataset, implementation and policy without promoting software metrics", () => {
  const hash = "a".repeat(64);
  const job = {
    report_path: `derived/comparison-v1/comparison-${hash}.json`,
  } as Job;
  const evaluation = {
    report_sha256: [hash],
    dataset_sha256: report.dataset_sha256,
    implementation_sha256: report.implementation_sha256,
    policy_sha256: report.policy_sha256,
    eligibility: { state: "ELIGIBLE" },
    origin: "human",
    independent_real_validation: true,
    metrics: {},
    config: { mode: "held_out" },
  } as Evaluation;
  expect(hasIndependentEvaluation(job, report, [evaluation])).toBe(true);
  for (const change of [
    { report_sha256: ["b".repeat(64)] },
    { dataset_sha256: "other" },
    { implementation_sha256: "other" },
    { policy_sha256: "other" },
    { origin: "synthetic" },
    { independent_real_validation: false },
    { metrics: null },
    { config: { mode: "software_fixture" } },
  ])
    expect(
      hasIndependentEvaluation(job, report, [
        { ...evaluation, ...change } as Evaluation,
      ]),
    ).toBe(false);
});

it.each(["transcript", "timing", "flaws"] as const)(
  "guides %s without approving evidence by navigation",
  (scope) => {
    render(
      <ReviewJourney
        scope={scope}
        dirty={true}
        busy={false}
        submitted={false}
        validated={false}
        issues={["Listen to the complete recording."]}
      />,
    );
    const link = screen.getByRole("button", { name: "4. Validate and submit" });
    const fragment = window.location.hash;
    fireEvent.click(link);
    expect(window.location.hash).toBe(fragment);
    expect(link).toHaveAttribute("aria-current", "step");
    expect(screen.getByText(/Unsaved changes/)).toBeVisible();
    expect(
      screen.getByText(/Moving between steps does not approve/),
    ).toBeVisible();
    expect(screen.getByText("Listen to the complete recording.")).toBeVisible();
    expect(
      screen.queryByText("Backend completion check passed."),
    ).not.toBeInTheDocument();
  },
);
