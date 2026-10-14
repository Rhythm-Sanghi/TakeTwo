import { expect, it } from "vitest";
import type { Recording } from "../api";
import type { Readiness, DatasetSummary } from "./DatasetReadiness";
import { readinessRequirements } from "./readinessRequirements";

// Presentation fixtures only; never human approvals or rights evidence.
const recording = {
  origin: "self_recorded",
  provenance: {
    rights: { status: "pending" },
    consent_evidence: "Local processing assertion only",
  },
  transcript: { status: "unverified" },
} as unknown as Recording;
const readiness = {
  next_action: "rights",
  review_agreement: { transcript: false, timing: false, flaws: false },
  review_status: {
    transcript: "No submitted reviews",
    timing: "No submitted reviews",
    flaws: "No submitted reviews",
  },
  pair_id: "software-pair",
  job_id: null,
} as unknown as Readiness;
const summary = { dataset_version: "software-v1" } as DatasetSummary;

it("keeps missing and obsolete evidence unknown rather than zero or approved", () => {
  expect(
    readinessRequirements(recording, readiness, summary, null, false).every(
      (r) => r.status === "Unknown",
    ),
  ).toBe(true);
  const rows = readinessRequirements(
    recording,
    { ...readiness, review_agreement: undefined },
    summary,
    null,
    true,
  );
  expect(rows.find((r) => r.name === "Word and phrase timing")?.status).toBe(
    "Unknown",
  );
});
it("makes all six missing prerequisites actionable without clearing permission", () => {
  const rows = readinessRequirements(recording, readiness, summary, null, true);
  expect(rows).toHaveLength(6);
  expect(rows[0].status).toBe("Blocked");
  expect(rows[0].missing).toContain("does not grant redistribution");
  expect(rows.find((r) => r.name === "Spoken transcript")?.status).toBe(
    "Pending",
  );
  expect(rows.every((r) => r.why && r.action && r.location)).toBe(true);
});
it("keeps agreeing transcript assertions distinct from verified dataset metadata", () => {
  const rows = readinessRequirements(
    recording,
    {
      ...readiness,
      review_agreement: { ...readiness.review_agreement, transcript: true },
    },
    summary,
    null,
    true,
  );
  expect(rows.find((r) => r.name === "Spoken transcript")?.status).toBe(
    "Agreement recorded",
  );
  expect(rows.find((r) => r.name === "Reviewed dataset version")?.status).toBe(
    "Pending",
  );
});
