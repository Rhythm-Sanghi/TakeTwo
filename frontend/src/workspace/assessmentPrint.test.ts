import { expect, it } from "vitest";
import type { Report } from "../api";
import { printedAssessmentStatus } from "./AnalysisResult";

const report = (reasons: { code: string; message: string }[]) =>
  ({
    overall_score: null,
    eligibility: { state: "INELIGIBLE", reasons },
    dimensions: [],
    regions: [],
    feature_eligibility: {},
  }) as unknown as Report;

it("prints a reason for unavailable assessment without inventing a score", () => {
  expect(
    printedAssessmentStatus(
      report([
        {
          code: "timing_review_required",
          message: "Missing independent timing",
        },
      ]),
      false,
    ),
  ).toContain("independent review requirements");
  expect(
    printedAssessmentStatus(
      report([{ code: "near_silent", message: "Too quiet" }]),
      false,
    ),
  ).toContain("acoustic requirements");
  expect(printedAssessmentStatus(null, false)).toContain(
    "Restore the completed report",
  );
  expect(printedAssessmentStatus(null, true)).toContain(
    "does not verify the reference",
  );
  expect(
    printedAssessmentStatus({ ...report([]), overall_score: 100 }, false),
  ).not.toContain("100");
});
