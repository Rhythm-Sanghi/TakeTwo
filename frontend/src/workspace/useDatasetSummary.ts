import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError } from "../api";
import type { DatasetSummary } from "./DatasetReadiness";

export type DatasetState = {
  phase:
    | "loading"
    | "ready"
    | "partial"
    | "unknown"
    | "unavailable"
    | "restricted"
    | "error";
  summary: DatasetSummary | null;
  message: string;
  diagnostic: string;
};
const requiredCounts = [
  "distinct_speaker_ids",
  "connected_families",
  "verified_transcripts",
  "submitted_independent_assertions",
];

export function useDatasetSummary() {
  const [state, setState] = useState<DatasetState>({
    phase: "loading",
    summary: null,
    message: "",
    diagnostic: "",
  });
  const request = useRef<AbortController | null>(null);
  const generation = useRef(0);
  const reload = useCallback(async () => {
    const current = ++generation.current;
    request.current?.abort();
    const controller = new AbortController();
    request.current = controller;
    const timer = setTimeout(() => controller.abort(), 15000);
    setState((previous) => ({
      ...previous,
      phase: "loading",
      message: "",
      diagnostic: "",
    }));
    try {
      const summary = await api<DatasetSummary>("/dataset", {
        signal: controller.signal,
      });
      if (current !== generation.current) return;
      if (
        !summary ||
        ![1, 2].includes(summary.schema_version) ||
        !Number.isInteger(summary.recordings) ||
        summary.recordings < 0
      )
        throw new ApiError(
          "The backend returned an invalid dataset summary. Restart the matching service and retry.",
          200,
          "response_shape",
        );
      const missing = requiredCounts.filter(
        (key) =>
          !Number.isInteger(summary.inventory_counts?.[key]) ||
          (summary.inventory_counts?.[key] ?? -1) < 0,
      );
      const diagnostic = summary.readiness_diagnostic;
      const readinessMissing =
        !Array.isArray(summary.review_readiness) ||
        summary.review_readiness.length !== summary.recordings;
      const phase = diagnostic
        ? "partial"
        : missing.length || readinessMissing
          ? "unknown"
          : "ready";
      setState({
        phase,
        summary,
        message: diagnostic
          ? `${diagnostic.message} ${diagnostic.recovery}`
          : phase === "unknown"
            ? "The backend returned incomplete readiness data. Restart the matching local service and retry."
            : "",
        diagnostic:
          diagnostic?.code ??
          (missing.length
            ? `Missing authoritative counts: ${missing.join(", ")}`
            : ""),
      });
      return summary;
    } catch (failure) {
      if (current !== generation.current) return;
      const error =
        failure instanceof Error
          ? failure
          : new Error("Dataset request failed.");
      const phase =
        error instanceof ApiError
          ? error.status === 403
            ? "restricted"
            : error.status >= 500
              ? "error"
              : "unknown"
          : "unavailable";
      setState((previous) => ({
        ...previous,
        phase,
        message:
          phase === "restricted"
            ? "Dataset access is restricted during reviewer handoff. Return through the existing operator workflow."
            : phase === "unavailable"
              ? "The local dataset service did not respond. Check that it is running, then retry."
              : error.message,
        diagnostic:
          error instanceof ApiError
            ? `HTTP ${error.status} · ${error.code}`
            : error.name,
      }));
    } finally {
      clearTimeout(timer);
    }
  }, []);
  useEffect(
    () => () => {
      ++generation.current;
      request.current?.abort();
    },
    [],
  );
  return { state, reload };
}
