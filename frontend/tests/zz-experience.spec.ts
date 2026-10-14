import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import type { Job, Region, Report } from "../src/api";

test("software UI states distinguish loading, partial evidence, eligible findings and eligible zero regions", async ({
  page,
  request,
}, info) => {
  // Route-only software fixtures. No stored report, recording or human review is changed.
  const jobs: Job[] = await (await request.get("/api/v1/analyses")).json();
  const job = jobs.find((j) => j.state === "completed" && j.report_path)!;
  expect(job).toBeTruthy();
  const original: Report = await (
    await request.get(`/api/v1/analyses/${job.id}/report`)
  ).json();
  const region: Region = {
    id: "software-ui-region",
    category: "pause_behavior",
    detector: "rubric",
    participant_interval: { start_s: 0.4, end_s: 0.8 },
    participant_anchor_s: null,
    reference_interval: { start_s: 0.2, end_s: 0.5 },
    reference_anchor_s: null,
    token_span: [0, 2],
    observation_ids: ["software-ui-observation"],
    severity: 2,
    confidence_reason: "not_calibrated",
    reliability: "reviewed",
    eligibility: { state: "ELIGIBLE" },
    explanation: {
      plain: "Software UI fixture: participant gap exceeds the reference gap.",
      technical: "Fixture display only.",
      suggested_review: "Listen to each native interval.",
      causal_scope: "calculation_only",
    },
  };
  const fixture: Report = {
    ...original,
    dataset_version: "software-ui-fixture-only",
    eligibility: { state: "ELIGIBLE" },
    overall_score: 75,
    feature_eligibility: Object.fromEntries(
      original.dimensions.map((d) => [d.dimension, { state: "ELIGIBLE" }]),
    ),
    dimensions: original.dimensions.map((d) => ({
      ...d,
      score: 75,
      reasons: [],
    })),
    regions: [region],
    observations: [
      {
        id: "software-ui-observation",
        dimension: "pause_behavior",
        detector: "rubric",
        token_span: [0, 2],
        participant_interval: region.participant_interval,
        reference_interval: region.reference_interval,
        unit: "s",
        reference: 0.3,
        participant: 0.4,
        delta: 0.1,
        tolerance: 0,
        saturation_width: 1,
        normalized_deviation: 0.1,
        excess: 0.1,
        penalty: 0.1,
        weight: 1,
        scored: true,
        eligibility: { state: "ELIGIBLE" },
      },
    ],
  };
  let displayed = fixture;
  let release: (() => void) | undefined;
  let hold: Promise<void> | null = new Promise((resolve) => {
    release = resolve;
  });
  await page.route(`**/api/v1/analyses/${job.id}/report`, async (route) => {
    if (hold) await hold;
    await route.fulfill({ json: displayed });
  });
  const open = async () => {
    await page.goto("/");
    await page.getByText("Local workspace ready", { exact: true }).waitFor();
    await page
      .locator(".library")
      .getByRole("button")
      .filter({ hasText: job.id.slice(0, 12) })
      .click();
  };
  await open();
  await expect(
    page.getByRole("heading", { name: /Loading assessment evidence/ }),
  ).toBeVisible();
  await page.screenshot({
    path: info.outputPath("software-fixture-loading.png"),
    fullPage: true,
  });
  release!();
  hold = null;
  await expect(
    page.getByRole("heading", {
      name: "Eligible comparison results available.",
    }),
  ).toBeVisible();
  await expect(page.locator(".findings")).toContainText(
    "reference 0.300 s; participant 0.400 s",
  );
  await page
    .getByRole("button", { name: "Inspect and seek", exact: true })
    .click();
  await expect
    .poll(() =>
      page
        .getByLabel("reference audio", { exact: true })
        .evaluate((n: HTMLAudioElement) => n.currentTime),
    )
    .toBeCloseTo(0.2);
  await expect
    .poll(() =>
      page
        .getByLabel("participant audio", { exact: true })
        .evaluate((n: HTMLAudioElement) => n.currentTime),
    )
    .toBeCloseTo(0.4);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page
    .getByRole("button", { name: "Replay participant interval" })
    .click();
  await expect
    .poll(() =>
      page
        .getByLabel("participant audio", { exact: true })
        .evaluate((n: HTMLAudioElement) => n.paused),
    )
    .toBe(true);
  await expect
    .poll(() =>
      page
        .getByLabel("participant audio", { exact: true })
        .evaluate((n: HTMLAudioElement) => n.currentTime),
    )
    .toBeCloseTo(0.8);
  await page.screenshot({
    path: info.outputPath("software-fixture-eligible-findings.png"),
    fullPage: true,
  });
  displayed = {
    ...fixture,
    overall_score: null,
    eligibility: { state: "INELIGIBLE" },
    dimensions: fixture.dimensions.map((d, i) => ({
      ...d,
      score: i === 0 ? 75 : null,
    })),
  };
  await open();
  await expect(
    page.getByRole("heading", { name: /Some dimensions available/ }),
  ).toBeVisible();
  await page.screenshot({
    path: info.outputPath("software-fixture-partial.png"),
    fullPage: true,
  });
  displayed = {
    ...fixture,
    overall_score: null,
    dimensions: fixture.dimensions.map((d) => ({ ...d, score: null })),
  };
  await open();
  await expect(
    page.getByRole("heading", {
      name: "Eligible evidence available. Overall assessment unavailable.",
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("status").filter({ hasText: "Processing:" }),
  ).toContainText("Evidence available; score unavailable");
  await expect(
    page.getByRole("status").filter({ hasText: "Processing:" }),
  ).not.toContainText("Pending verification");
  await page.screenshot({
    path: info.outputPath("software-fixture-eligible-evidence-no-score.png"),
    fullPage: true,
  });
  displayed = { ...fixture, regions: [] };
  await open();
  await expect(page.locator(".findings")).toContainText(
    "No threshold crossings detected",
  );
  await expect(page.locator(".findings")).not.toContainText("Findings pending");
  await page.screenshot({
    path: info.outputPath("software-fixture-eligible-zero.png"),
    fullPage: true,
  });
});
