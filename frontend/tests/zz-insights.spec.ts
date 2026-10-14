import { test, expect } from "@playwright/test";
import type { ComparativeReport, Job, Recording } from "../src/api";
import { openHistory, navigateWorkspace } from "./navigation";

test("comparative groups retain raw evidence, native replay and recovery after missing artifacts", async ({
  page,
  request,
}, info) => {
  const recordings: Recording[] = await (
    await request.get("/api/v1/recordings")
  ).json();
  const jobs: Job[] = await (await request.get("/api/v1/analyses")).json();
  const ref = recordings.find(
    (r) => r.original_filename === "generated-reference.wav",
  )!;
  const job = jobs.find(
    (j) =>
      j.state === "completed" &&
      j.request.reference_id === ref.id &&
      j.request.pair_id,
  )!;
  const path = `/api/v1/analyses/${job.id}/insights`;
  const report: ComparativeReport = await (await request.get(path)).json();
  expect(report.exploratory.recordings).toHaveLength(2);
  expect(report.segments).toHaveLength(0); // Actual generated-tone run has no machine text alignment.
  expect(report.correspondence_unavailable_reason).toBeTruthy();
  const linked = report.groups.flatMap((g) => g.candidate_ids).sort();
  expect(linked).toEqual(report.exploratory.candidates.map((c) => c.id).sort());
  await page.goto("/");
  await openHistory(page, job.id.slice(0, 12));
  await expect(
    page.getByRole("heading", { name: "What analysis found", exact: true }),
  ).toBeVisible();
  const group = report.groups.find(
    (g) => g.id === report.inspection_order[0].evidence_id,
  )!;
  const card = page.locator(`[data-evidence-id="${group.id}"]`);
  const role = report.exploratory.recordings.find(
    (r) => r.recording_id === group.recording_id,
  )!.role;
  const audio = page.getByLabel(`${role} audio`, { exact: true });
  await card.getByRole("button", { name: "Inspect grouped interval" }).click();
  await expect(audio).toBeFocused();
  await expect
    .poll(() => audio.evaluate((node: HTMLAudioElement) => node.currentTime))
    .toBeCloseTo(group.start_s, 2);
  await card
    .getByRole("button", { name: `Listen to ${role}`, exact: true })
    .click();
  await expect
    .poll(() => audio.evaluate((node: HTMLAudioElement) => node.currentTime))
    .toBeGreaterThanOrEqual(group.end_s - 0.025);
  await expect
    .poll(() => audio.evaluate((node: HTMLAudioElement) => node.paused))
    .toBe(true);
  await page
    .getByRole("button", { name: `Return to complete ${role} recording` })
    .click();
  await expect
    .poll(() => audio.evaluate((node: HTMLAudioElement) => node.currentTime))
    .toBe(0);
  const exported = await (await request.get(path + "/export")).json();
  expect(exported.result).toEqual(report);
  await card.getByText("Inspect evidence and selection reason").click();
  await expect(card).toContainText(report.inspection_order[0].order_reason);
  await page.route(`**${path}`, (route) =>
    route.fulfill({
      status: 404,
      json: {
        error: {
          code: "artifact_missing",
          message: "Stored acoustic evidence is missing.",
          recovery: "Restore the original managed artifact.",
        },
      },
    }),
  );
  await page.reload();
  await openHistory(page, job.id.slice(0, 12));
  await expect(
    page.getByRole("region", { name: "Comparative insight recovery" }),
  ).toContainText("Stored acoustic evidence is missing");
  await expect(page.locator(".comparative-insights")).toHaveCount(0);
  await page.unroute(`**${path}`);
  await page
    .getByRole("button", { name: "Retry comparative insights" })
    .click();
  await expect(page.locator(".comparative-insights")).toBeVisible();
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({
    path: info.outputPath("comparative-software-viewport.png"),
  });
  await page.screenshot({
    path: info.outputPath("comparative-software.png"),
    fullPage: true,
  });
  await card
    .getByRole("button", { name: `Listen to ${role}`, exact: true })
    .click();
  await navigateWorkspace(page, "Dataset and Evaluation");
  await expect(page.locator("audio")).toHaveCount(0);
  let release: () => void = () => {};
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(`**${path}`, async (route) => {
    await held;
    await route.fulfill({ json: report });
  });
  await page.reload();
  await openHistory(page, job.id.slice(0, 12));
  await page
    .getByRole("combobox", { name: "Participant pair", exact: true })
    .selectOption("");
  release();
  await expect(page.locator(".comparative-insights")).toHaveCount(0);
});
