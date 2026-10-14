import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
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

it("keeps operator data locked after mode failure and retry into an active handoff", async () => {
  const mounted = vi.fn();
  let modeRequests = 0;
  function Operator() {
    mounted();
    return <p>Private peer data</p>;
  }
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      if (url.endsWith("/mode") && ++modeRequests === 1)
        throw new Error("Software connection failure");
      return {
        ok: true,
        json: async () =>
          url.endsWith("/mode")
            ? { active_session: session.id }
            : url.includes("waveform")
              ? { bins: [], start_s: 0, end_s: 2 }
              : session,
      };
    }),
  );
  render(
    <ReviewEntry>
      <Operator />
    </ReviewEntry>,
  );
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "could not be opened",
  );
  expect(mounted).not.toHaveBeenCalled();
  await userEvent.click(
    screen.getByRole("button", { name: "Retry opening local workspace" }),
  );
  expect(
    await screen.findByRole("heading", { name: "Review Workspace" }),
  ).toBeInTheDocument();
  expect(modeRequests).toBe(2);
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

it("retains a rejected continuous playback span for the next real update without counting seeks", async () => {
  const observed: { start_s: number; end_s: number }[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      if (url.endsWith("/listen")) {
        observed.push(JSON.parse(init?.body as string));
        if (observed.length === 1)
          return {
            ok: false,
            json: async () => ({
              error: {
                message: "Heartbeat rejected.",
                recovery: "Continue listening.",
              },
            }),
          };
      }
      return {
        ok: true,
        json: async () =>
          url.includes("waveform")
            ? { bins: [], start_s: 0, end_s: 2 }
            : session,
      };
    }),
  );
  render(<Reviewer sessionId={session.id} />);
  const player = (await screen.findByLabelText(
    "Assigned recording playback",
  )) as HTMLAudioElement;
  Object.defineProperty(player, "paused", { configurable: true, value: false });
  fireEvent.play(player);
  player.currentTime = 0.5;
  fireEvent.timeUpdate(player);
  await screen.findByText(/Heartbeat rejected/);
  player.currentTime = 1;
  fireEvent.timeUpdate(player);
  await waitFor(() => expect(observed).toHaveLength(2));
  expect(observed[1]).toEqual({ start_s: 0, end_s: 1 });
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "Save draft" })).toBeEnabled(),
  );
  fireEvent.seeking(player);
  player.currentTime = 1.4;
  fireEvent.seeked(player);
  player.currentTime = 1.7;
  fireEvent.timeUpdate(player);
  await waitFor(() => expect(observed).toHaveLength(3));
  expect(observed[2]).toEqual({ start_s: 1.4, end_s: 1.7 });
  expect(screen.getByRole("button", { name: "Submit review" })).toBeDisabled();
});

it("keeps an explicitly sought beginning when the play callback arrives milliseconds later", async () => {
  const observed: unknown[] = [];
  vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue();
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      if (url.endsWith("/listen"))
        observed.push(JSON.parse(init?.body as string));
      return {
        ok: true,
        json: async () =>
          url.includes("waveform")
            ? { bins: [], start_s: 0, end_s: 2 }
            : session,
      };
    }),
  );
  render(<Reviewer sessionId={session.id} />);
  const player = (await screen.findByLabelText(
    "Assigned recording playback",
  )) as HTMLAudioElement;
  Object.defineProperty(player, "paused", { configurable: true, value: false });
  await userEvent.click(
    screen.getByRole("button", { name: "Listen from beginning" }),
  );
  player.currentTime = 0.006;
  fireEvent.play(player);
  player.currentTime = 0.5;
  fireEvent.timeUpdate(player);
  await waitFor(() => expect(observed).toEqual([{ start_s: 0, end_s: 0.5 }]));
  expect(screen.getByRole("button", { name: "Submit review" })).toBeDisabled();
});

it("waits for the terminal listening acknowledgment before saving and validating", async () => {
  const calls: string[] = [];
  let first: (value: unknown) => void = () => {};
  let terminal: (value: unknown) => void = () => {};
  const pendingFirst = new Promise((resolve) => {
    first = resolve;
  });
  const pendingTerminal = new Promise((resolve) => {
    terminal = resolve;
  });
  const success = { ok: true, json: async () => session };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      if (url.endsWith("/listen")) {
        const span = JSON.parse(init?.body as string);
        calls.push(`listen:${span.start_s}-${span.end_s}`);
        return span.end_s === 0.5 ? pendingFirst : pendingTerminal;
      }
      if (url.endsWith("/draft")) calls.push("draft");
      if (url.endsWith("/validation")) {
        calls.push("validation");
        return {
          ok: true,
          json: async () => ({
            can_submit: false,
            issues: ["Independent decision still missing."],
            scientific_notice: "Software fixture only.",
          }),
        };
      }
      return url.includes("waveform")
        ? { ok: true, json: async () => ({ bins: [], start_s: 0, end_s: 2 }) }
        : success;
    }),
  );
  render(<Reviewer sessionId={session.id} />);
  const player = (await screen.findByLabelText(
    "Assigned recording playback",
  )) as HTMLAudioElement;
  Object.defineProperty(player, "paused", { configurable: true, value: false });
  fireEvent.play(player);
  player.currentTime = 0.5;
  fireEvent.timeUpdate(player);
  await waitFor(() => expect(calls).toEqual(["listen:0-0.5"]));
  player.currentTime = 2;
  Object.defineProperty(player, "ended", { configurable: true, value: true });
  Object.defineProperty(player, "paused", { configurable: true, value: true });
  fireEvent.ended(player);
  await userEvent.click(screen.getByRole("button", { name: "Save draft" }));
  expect(calls).not.toContain("draft");
  first(success);
  await waitFor(() => expect(calls).toEqual(["listen:0-0.5", "listen:0.5-2"]));
  expect(calls).not.toContain("draft");
  terminal(success);
  await waitFor(() =>
    expect(calls).toEqual([
      "listen:0-0.5",
      "listen:0.5-2",
      "draft",
      "validation",
    ]),
  );
  expect(screen.getByRole("button", { name: "Submit review" })).toBeDisabled();
});
