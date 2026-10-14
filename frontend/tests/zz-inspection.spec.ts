import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { inflateSync } from "node:zlib";
import type { Job, Pair, Report } from "../src/api";
import { navigateWorkspace, openHistory } from "./navigation";

// Generated oscillators only. Routes test presentation/races, never stored evidence.
test("reference inspection, historical identity and searchable print remain distinct from comparison", async ({
  page,
  request,
}, info) => {
  const jobs: Job[] = await (await request.get("/api/v1/analyses")).json();
  const pairs: Pair[] = await (await request.get("/api/v1/pairs")).json();
  const reference = jobs.find(
    (job) =>
      job.state === "completed" && !job.request.pair_id && job.report_path,
  )!;
  const comparison = jobs.find(
    (job) =>
      job.state === "completed" && job.request.pair_id && job.report_path,
  )!;
  expect(reference).toBeTruthy();
  expect(comparison).toBeTruthy();
  expect(
    pairs.some((pair) => pair.reference_id === reference.request.reference_id),
  ).toBe(true);
  const originalReference: Report = await (
    await request.get(`/api/v1/analyses/${reference.id}/report`)
  ).json();
  const originalComparison: Report = await (
    await request.get(`/api/v1/analyses/${comparison.id}/report`)
  ).json();
  await page.goto("/");
  await openHistory(page, comparison.id.slice(0, 12));
  await expect(
    page.locator(".analysis-outcome .measurement-strip > div"),
  ).toHaveCount(2);
  await page
    .getByRole("combobox", { name: "Participant pair", exact: true })
    .selectOption("");
  await expect(
    page.locator(".analysis-outcome .measurement-strip"),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Print analysis summary", exact: true }),
  ).toBeDisabled();
  await expect(page.locator(".findings")).toHaveCount(0);
  await expect(page.locator(".analysis-outcome")).toContainText(
    "Participant comparison pending selection",
  );

  await openHistory(page, reference.id.slice(0, 12));
  await expect(
    page.getByRole("heading", {
      name: "Reference audio analysis complete",
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    page.locator(".analysis-outcome .measurement-strip > div"),
  ).toHaveCount(1);
  await expect(page.locator(".analysis-outcome")).not.toContainText(
    "No participant mirror/pair is available",
  );
  await expect(page.locator(".analysis-outcome")).not.toContainText(
    "both recordings",
  );
  await expect(page.getByRole("region", { name: "Rubric scores" })).toHaveCount(
    0,
  );
  await page
    .getByRole("button", { name: "Select a participant", exact: true })
    .click();
  await expect(
    page.getByRole("combobox", { name: "Participant pair", exact: true }),
  ).toBeFocused();
  await page
    .getByRole("button", { name: "Refresh workspace", exact: true })
    .click();
  await expect(
    page.locator(".analysis-outcome .measurement-strip > div"),
  ).toHaveCount(1);
  await expect(
    page.getByRole("combobox", { name: "Reference recording", exact: true }),
  ).toHaveValue(reference.request.reference_id);
  await expect(
    page.getByRole("combobox", { name: "Participant pair", exact: true }),
  ).toHaveValue("");
  for (const width of [320, 390, 800, 1366, 1920]) {
    await page.setViewportSize({ width, height: 740 });
    await page.evaluate(() => scrollTo(0, 0));
    expect(
      await page
        .locator(".analysis-outcome h2")
        .evaluate((node) => node.getBoundingClientRect().bottom),
    ).toBeLessThan(740);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.screenshot({
      path: info.outputPath(`reference-${width}-viewport.png`),
    });
    await page.screenshot({
      path: info.outputPath(`reference-${width}-full.png`),
      fullPage: true,
    });
  }
  await page
    .locator(".feature-chart .uplot")
    .first()
    .waitFor({ state: "attached" });
  await page.waitForFunction(() =>
    [...document.querySelectorAll<HTMLCanvasElement>("canvas.waveform")].every(
      (node) => node.style.visibility === "visible",
    ),
  );
  await page.emulateMedia({ media: "print" });
  await expect(
    page.getByText("Reference audio analysis complete", { exact: true }).last(),
  ).toBeVisible();
  await expect(page.getByLabel("Printed reference measurements")).toBeVisible();
  await expect(page.getByRole("region", { name: "Rubric scores" })).toHaveCount(
    0,
  );
  const pdf = await page.pdf({
    path: info.outputPath("reference-inspection.pdf"),
    format: "A4",
    printBackground: true,
    tagged: true,
  });
  await page.emulateMedia({ media: null });
  // Font maps and text operators distinguish native browser text from full-page raster output.
  expect(pdf.toString("latin1")).toContain("/ToUnicode");
  expect(pdf.toString("latin1")).toContain("/StructTreeRoot");
  const streams = [
    ...pdf.toString("latin1").matchAll(/stream\r?\n([\s\S]*?)\r?\nendstream/g),
  ];
  expect(
    streams.some((stream) => {
      try {
        return /\bBT\b/.test(
          inflateSync(Buffer.from(stream[1], "latin1")).toString("latin1"),
        );
      } catch {
        return false;
      }
    }),
  ).toBe(true);

  await page.route("**/api/v1/pairs", (route) =>
    route.fulfill({
      json: pairs.filter(
        (pair) => pair.reference_id !== reference.request.reference_id,
      ),
    }),
  );
  await page.reload();
  await openHistory(page, reference.id.slice(0, 12));
  await expect(
    page.getByRole("button", { name: "Add a participant", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".analysis-outcome")).toContainText(
    "No participant pair exists for this reference",
  );
  await page
    .getByRole("button", { name: "Add a participant", exact: true })
    .click();
  await expect(page.getByLabel("Recording type")).toHaveValue(
    "human_participant",
  );
  await expect(page.getByLabel("Compare with reference")).toHaveValue(
    reference.request.reference_id,
  );
  await page.unroute("**/api/v1/pairs");
  await page.reload();

  let release: () => void = () => {};
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(
    `**/api/v1/analyses/${comparison.id}/report`,
    async (route) => {
      await held;
      await route.fulfill({ json: originalComparison });
    },
  );
  await openHistory(page, comparison.id.slice(0, 12));
  await expect(
    page.locator(".analysis-outcome .measurement-strip"),
  ).toHaveCount(0);
  await openHistory(page, reference.id.slice(0, 12));
  await expect(
    page.locator(".analysis-outcome .measurement-strip > div"),
  ).toHaveCount(1);
  release();
  await expect(
    page.getByRole("heading", {
      name: "Reference audio analysis complete",
      exact: true,
    }),
  ).toBeVisible();
  await page.unroute(`**/api/v1/analyses/${comparison.id}/report`);
  await openHistory(page, comparison.id.slice(0, 12));
  await expect(
    page.locator(".analysis-outcome .measurement-strip > div"),
  ).toHaveCount(2);
  await expect(
    page.getByRole("combobox", { name: "Participant pair", exact: true }),
  ).toHaveValue(comparison.request.pair_id!);
  await page
    .getByRole("button", { name: "Refresh workspace", exact: true })
    .click();
  await expect(
    page.locator(".analysis-outcome .measurement-strip > div"),
  ).toHaveCount(2);
  for (const width of [320, 390, 800, 1366, 1920]) {
    await page.setViewportSize({ width, height: 740 });
    await page.evaluate(() => scrollTo(0, 0));
    expect(
      await page
        .locator(".analysis-outcome h2")
        .evaluate((node) => node.getBoundingClientRect().bottom),
    ).toBeLessThan(740);
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.screenshot({
      path: info.outputPath(`comparison-${width}-viewport.png`),
    });
    await page.screenshot({
      path: info.outputPath(`comparison-${width}-full.png`),
      fullPage: true,
    });
  }
  await page
    .locator(".feature-chart .uplot")
    .nth(1)
    .waitFor({ state: "attached" });
  await page.pdf({
    path: info.outputPath("participant-comparison.pdf"),
    format: "A4",
    printBackground: true,
    tagged: true,
  });
  await page.route(`**/api/v1/analyses/${comparison.id}/report`, (route) =>
    route.fulfill({ json: originalReference }),
  );
  await page.reload();
  await openHistory(page, comparison.id.slice(0, 12));
  await expect(page.getByRole("alert")).toContainText(
    "Report identity does not match",
  );
  await expect(
    page.locator(".analysis-outcome .measurement-strip"),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Print analysis summary", exact: true }),
  ).toBeDisabled();
  await navigateWorkspace(page, "Recording Library");
});
