import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { ReviewEntry, Reviewer, ReviewWorkspace } from "./ReviewWorkspace";

beforeEach(() => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

// Minimal lifecycle fixture for component interaction only, never scientific evidence.
const session = {
  id: "software-session",
  assignment: { reviewer_id: "software-a", scope: "transcript" },
  state: "draft",
  duration_s: 2,
  recording_name: "Assigned recording",
  revision: 1,
  edit_revision: 0,
  created_at: "2026-10-13T00:00:00Z",
  original_text: "Fixture words.",
  machine_text: null,
  suggestions: [],
  assisted_alignment: false,
  listened_spans: [],
  inspected_words: [],
  draft: {
    corrected_text: "Fixture words.",
    words: [],
    phrase_spans: [],
    labels: [],
    unclear_spans: [],
    uncertain_words: [],
    decision: "unresolved",
    independent: false,
    blinded_to_predictions: false,
    evidence_reference: "",
    notes: "",
  },
};

it("does not mount operator data views during active handoff", async () => {
  const mounted = vi.fn();
  function Operator() {
    mounted();
    return <p>Private peer data</p>;
  }
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => ({
      ok: true,
      json: async () =>
        url.endsWith("/mode")
          ? { active_session: session.id }
          : url.includes("waveform")
            ? { bins: [], start_s: 0, end_s: 2 }
            : session,
    })),
  );
  render(
    <ReviewEntry>
      <Operator />
    </ReviewEntry>,
  );
  expect(
    await screen.findByRole("heading", {
      name: "Review Workspace",
    }),
  ).toBeInTheDocument();
  expect(mounted).not.toHaveBeenCalled();
  expect(screen.queryByText("Private peer data")).not.toBeInTheDocument();
});

it("retains failed draft edits and warns before leaving", async () => {
  const fetcher = vi.fn(async (url: string) =>
    url.endsWith("/draft")
      ? {
          ok: false,
          json: async () => ({
            error: {
              message: "Conflicting edit revision.",
              recovery: "Reload saved draft.",
            },
          }),
        }
      : {
          ok: true,
          json: async () =>
            url.includes("waveform")
              ? { bins: [], start_s: 0, end_s: 2 }
              : session,
        },
  );
  vi.stubGlobal("fetch", fetcher);
  render(<Reviewer sessionId={session.id} />);
  const input = await screen.findByLabelText("Reviewer-corrected transcript");
  await userEvent.clear(input);
  await userEvent.type(input, "Corrected fixture words.");
  const leaving = new Event("beforeunload", { cancelable: true });
  window.dispatchEvent(leaving);
  expect(leaving.defaultPrevented).toBe(true);
  await userEvent.click(screen.getByRole("button", { name: "Save draft" }));
  await waitFor(() =>
    expect(screen.getByRole("status")).toHaveTextContent(
      "Conflicting edit revision",
    ),
  );
  expect(input).toHaveValue("Corrected fixture words.");
  expect(screen.getByRole("button", { name: "Submit review" })).toBeDisabled();
});

it("shows original timing differences for adjudication without selecting a winner", async () => {
  // Software-only differences, not real review evidence.
  const reviews = [
    {
      id: "fixture-review-a",
      reviewer_id: "fixture-a",
      scope: "timing",
      decision: "approved",
      notes: "Fixture only",
      words: [{ label: "fixture", start_s: 0.1, end_s: 0.5 }],
      phrase_spans: [[0, 1]],
      reviewed_spans: [],
    },
    {
      id: "fixture-review-b",
      reviewer_id: "fixture-b",
      scope: "timing",
      decision: "unresolved",
      notes: "Fixture uncertainty",
      words: [{ label: "fixture", start_s: 0.31, end_s: 0.7 }],
      phrase_spans: [[0, 1]],
      reviewed_spans: [],
    },
  ];
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: true,
      json: async () => ({
        sessions: [],
        disagreements: [
          {
            recording_id: "fixture",
            scope: "timing",
            issue: "Fixture boundary disagreement",
            reviews,
          },
        ],
        decisions: [],
      }),
    })),
  );
  render(<ReviewWorkspace recordings={[]} jobs={[]} pairs={[]} />);
  await userEvent.type(
    screen.getByLabelText("Operator key", { exact: true }),
    "fixture-key",
  );
  await userEvent.click(
    screen.getByRole("button", { name: "Load sessions and adjudication" }),
  );
  expect(
    await screen.findByText("Fixture boundary disagreement"),
  ).toBeInTheDocument();
  expect(screen.getByText("210.0 / 200.0")).toBeInTheDocument();
  expect(
    screen.getByRole("button", { name: "Record adjudication for timing" }),
  ).toBeDisabled();
});
