import { afterEach, expect, it, vi } from "vitest";
import {
  installWorkspacePrint,
  printAnalysisReport,
  printWorkspaceReport,
} from "./reportPrint";

afterEach(() => {
  dispatchEvent(new Event("afterprint"));
  vi.restoreAllMocks();
  delete document.body.dataset.printScope;
  delete document.body.dataset.reportType;
  delete document.body.dataset.reportMode;
});

it("gives ordinary browser printing the selected workspace identity and restores it", () => {
  document.title = "TakeTwo";
  const cleanup = installWorkspacePrint("paired");
  dispatchEvent(new Event("beforeprint"));
  expect(document.title).toBe("TakeTwo-speech-comparison-workspace-view");
  expect(document.body.dataset.reportType).toBe("workspace");
  expect(document.body.dataset.reportMode).toBe("paired");
  dispatchEvent(new Event("afterprint"));
  expect(document.title).toBe("TakeTwo");
  expect(document.body.dataset.reportMode).toBeUndefined();
  cleanup();
});

it("does not replace a dedicated evidence export with the default workspace view", () => {
  vi.spyOn(window, "print").mockImplementation(() => {});
  const cleanup = installWorkspacePrint("reference");
  printAnalysisReport("evidence", true);
  dispatchEvent(new Event("beforeprint"));
  expect(document.body.dataset.reportType).toBe("evidence");
  expect(document.body.dataset.reportMode).toBe("paired");
  dispatchEvent(new Event("afterprint"));
  expect(document.body.dataset.reportType).toBeUndefined();
  cleanup();
});

it("uses dataset identity and recovers workspace export metadata when printing throws", () => {
  vi.spyOn(window, "print").mockImplementation(() => {
    throw new Error("Unavailable");
  });
  document.title = "Original";
  expect(() => printWorkspaceReport("dataset")).toThrow("Unavailable");
  expect(document.title).toBe("Original");
  expect(document.body.dataset.reportMode).toBeUndefined();
  const cleanup = installWorkspacePrint("dataset");
  dispatchEvent(new Event("beforeprint"));
  expect(document.body.dataset.reportMode).toBe("dataset");
  expect(document.title).toBe("TakeTwo-dataset-readiness-report");
  cleanup();
  expect(document.title).toBe("Original");
});

it("selects distinct summary/full print scopes and restores title after cancellation", () => {
  const print = vi.spyOn(window, "print").mockImplementation(() => {});
  document.title = "TakeTwo";
  printAnalysisReport("summary", false);
  expect(document.title).toBe("TakeTwo-reference-inspection-analysis-summary");
  expect(document.body.dataset.reportType).toBe("summary");
  expect(document.body.dataset.reportMode).toBe("reference");
  expect(document.body.dataset.printScope).toBe("exploratory");
  dispatchEvent(new Event("afterprint"));
  expect(document.title).toBe("TakeTwo");
  expect(document.body.dataset.printScope).toBeUndefined();
  expect(document.body.dataset.reportMode).toBeUndefined();
  printAnalysisReport("evidence", true);
  expect(document.title).toBe("TakeTwo-speech-comparison-full-evidence-report");
  expect(document.body.dataset.reportType).toBe("evidence");
  expect(document.body.dataset.reportMode).toBe("paired");
  expect(print).toHaveBeenCalledTimes(2);
});

it("restores previous scope and title when browser printing throws", () => {
  vi.spyOn(window, "print").mockImplementation(() => {
    throw new Error("Unavailable");
  });
  document.title = "Original";
  document.body.dataset.printScope = "previous";
  document.body.dataset.reportMode = "previous-mode";
  expect(() => printAnalysisReport("summary", true)).toThrow("Unavailable");
  expect(document.title).toBe("Original");
  expect(document.body.dataset.printScope).toBe("previous");
  expect(document.body.dataset.reportType).toBeUndefined();
  expect(document.body.dataset.reportMode).toBe("previous-mode");
});
