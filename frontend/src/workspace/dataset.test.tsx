import {
  act,
  cleanup,
  render,
  renderHook,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { useDatasetSummary } from "./useDatasetSummary";
import { DatasetReadiness } from "./DatasetReadiness";

const summary = {
  schema_version: 2,
  recordings: 0,
  inventory_counts: {
    distinct_speaker_ids: 0,
    connected_families: 0,
    verified_transcripts: 0,
    submitted_independent_assertions: 0,
  },
  review_readiness: [],
};
const response = (body: unknown, status = 200) => ({
  ok: status === 200,
  status,
  json: async () => body,
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("distinguishes loading and authoritative zero from unknown inventory", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response(summary)));
  const { result } = renderHook(useDatasetSummary);
  expect(result.current.state.phase).toBe("loading");
  await act(async () => {
    await result.current.reload();
  });
  expect(result.current.state.phase).toBe("ready");
  expect(
    result.current.state.summary?.inventory_counts?.distinct_speaker_ids,
  ).toBe(0);
  render(
    <DatasetReadiness
      summary={result.current.state.summary}
      state={result.current.state}
      recordings={[]}
      selectedId=""
      onSelect={vi.fn()}
      onReview={vi.fn()}
    />,
  );
  expect(screen.getByText("0 takes")).toBeVisible();
});

it.each([
  [403, "restricted"],
  [503, "error"],
  [422, "unknown"],
])("explains HTTP %s without fabricating zero", async (status, phase) => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      response(
        {
          error: {
            code: "fixture",
            message: "Backend evidence failure.",
            recovery: "Retry.",
          },
        },
        status as number,
      ),
    ),
  );
  const { result } = renderHook(useDatasetSummary);
  await act(async () => {
    await result.current.reload();
  });
  expect(result.current.state.phase).toBe(phase);
  expect(result.current.state.summary).toBeNull();
  expect(result.current.state.diagnostic).toContain(String(status));
});

it("makes network failure recoverable and keeps missing counts unknown", async () => {
  const fetch = vi
    .fn()
    .mockRejectedValueOnce(new TypeError("Failed to fetch"))
    .mockResolvedValueOnce(response({ ...summary, inventory_counts: {} }));
  vi.stubGlobal("fetch", fetch);
  const { result } = renderHook(useDatasetSummary);
  await act(async () => {
    await result.current.reload();
  });
  expect(result.current.state.phase).toBe("unavailable");
  await act(async () => {
    await result.current.reload();
  });
  expect(result.current.state.phase).toBe("unknown");
  expect(result.current.state.diagnostic).toContain("distinct_speaker_ids");
});

it("retains inventory but withholds readiness after review evidence failure", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      response({
        ...summary,
        inventory_counts: {
          ...summary.inventory_counts,
          submitted_independent_assertions: undefined,
        },
        readiness_diagnostic: {
          code: "review_evidence_unavailable",
          message: "Review evidence unavailable.",
          recovery: "Validate and retry.",
        },
      }),
    ),
  );
  const { result } = renderHook(useDatasetSummary);
  await act(async () => {
    await result.current.reload();
  });
  expect(result.current.state.phase).toBe("partial");
  render(
    <DatasetReadiness
      summary={result.current.state.summary}
      state={result.current.state}
      onRetry={vi.fn()}
      recordings={[]}
      selectedId=""
      onSelect={vi.fn()}
      onReview={vi.fn()}
    />,
  );
  expect(screen.getByRole("alert")).toHaveTextContent(
    "Review evidence unavailable",
  );
  expect(
    screen.getByRole("button", { name: "Retry dataset readiness" }),
  ).toBeVisible();
  expect(
    screen.queryByRole("button", { name: "Open Review Workspace" }),
  ).not.toBeInTheDocument();
  expect(screen.getByText("Unknown assertions")).toBeVisible();
});

it("ignores an obsolete response even if the transport does not honor cancellation", async () => {
  let resolve: (value: unknown) => void = () => {};
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockImplementationOnce(
        () =>
          new Promise((done) => {
            resolve = done;
          }),
      )
      .mockResolvedValueOnce(response(summary)),
  );
  const { result } = renderHook(useDatasetSummary);
  let old: Promise<unknown>;
  act(() => {
    old = result.current.reload();
  });
  await act(async () => {
    await result.current.reload();
  });
  await act(async () => {
    resolve(response({ ...summary, recordings: 99 }));
    await old;
  });
  await waitFor(() => expect(result.current.state.summary?.recordings).toBe(0));
});
