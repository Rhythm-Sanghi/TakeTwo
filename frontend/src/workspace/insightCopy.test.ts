import { expect, it } from "vitest";
import type { ComparativeReport } from "../api";
import {
  inspectionReason,
  readableEvidenceReason,
  selectionLabel,
} from "./insightCopy";

it("uses grammatical selected-passage labels including empty reference inspection", () => {
  expect(selectionLabel(3, true)).toBe(
    "Three passages selected for inspection.",
  );
  expect(selectionLabel(1, false)).toBe(
    "One interval selected for inspection.",
  );
  expect(selectionLabel(0, false)).toBe(
    "No supported intervals selected for inspection.",
  );
});

it("formats historical mechanical wording without changing the source string", () => {
  const original = "1 source window(s); 3 source window(s); no confidence.";
  expect(readableEvidenceReason(original)).toBe(
    "1 source window; 3 source windows; no confidence.",
  );
  expect(original).toContain("window(s)");
});

it("explains supported single-window evidence while preserving exact input identity", () => {
  const report = {
    anomalies: [],
    segments: [],
    groups: [
      {
        id: "group",
        candidate_ids: ["raw"],
        duration_s: 0.5,
        direction: "increase",
      },
    ],
  } as unknown as ComparativeReport;
  const item = {
    evidence_id: "group",
    category: "group",
  } as ComparativeReport["inspection_order"][number];
  const snapshot = JSON.stringify(report);
  expect(inspectionReason(report, item)).toContain(
    "1 supporting window describes a 0.500 s",
  );
  expect(inspectionReason(report, item)).not.toContain("threshold");
  expect(JSON.stringify(report)).toBe(snapshot);
});

it("does not invent a measurement when supporting evidence is missing", () => {
  const report = {
    anomalies: [],
    segments: [],
    groups: [],
  } as unknown as ComparativeReport;
  expect(
    inspectionReason(report, {
      evidence_id: "missing",
    } as ComparativeReport["inspection_order"][number]),
  ).toContain("Supporting evidence is unavailable");
});

it("withholds a low-energy inconsistency claim when frame support is partial", () => {
  const report = {
    groups: [],
    segments: [],
    anomalies: [
      {
        id: "gap",
        gap: { start_s: 1, end_s: 3.89 },
        measurement: { complete: false, low_energy_s: 0 },
      },
    ],
  } as unknown as ComparativeReport;
  const result = inspectionReason(report, {
    evidence_id: "gap",
  } as ComparativeReport["inspection_order"][number]);
  expect(result).toContain("2.890 s");
  expect(result).not.toContain("does not match");
  expect(result).toContain("neither silence nor an alignment error");
});
