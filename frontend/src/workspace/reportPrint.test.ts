import { afterEach, expect, it, vi } from "vitest";
import { printAnalysisReport } from "./reportPrint";

afterEach(() => {
  dispatchEvent(new Event("afterprint"));
  vi.restoreAllMocks();
  delete document.body.dataset.printScope;
  delete document.body.dataset.reportType;
});

it("selects distinct summary/full print scopes and restores title after cancellation", () => {
  const print = vi.spyOn(window, "print").mockImplementation(() => {});
  document.title = "TakeTwo";
  printAnalysisReport("summary", false);
  expect(document.title).toBe("TakeTwo-reference-inspection-analysis-summary");
  expect(document.body.dataset.reportType).toBe("summary");
  expect(document.body.dataset.printScope).toBe("exploratory");
  dispatchEvent(new Event("afterprint"));
  expect(document.title).toBe("TakeTwo");
  expect(document.body.dataset.printScope).toBeUndefined();
  printAnalysisReport("evidence", true);
  expect(document.title).toBe("TakeTwo-speech-comparison-full-evidence-report");
  expect(document.body.dataset.reportType).toBe("evidence");
  expect(print).toHaveBeenCalledTimes(2);
});

it("restores previous scope and title when browser printing throws", () => {
  vi.spyOn(window, "print").mockImplementation(() => {
    throw new Error("Unavailable");
  });
  document.title = "Original";
  document.body.dataset.printScope = "previous";
  expect(() => printAnalysisReport("summary", true)).toThrow("Unavailable");
  expect(document.title).toBe("Original");
  expect(document.body.dataset.printScope).toBe("previous");
  expect(document.body.dataset.reportType).toBeUndefined();
});
