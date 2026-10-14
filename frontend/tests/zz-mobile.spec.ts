import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { navigateWorkspace, openHistory } from "./navigation";
import type { Job } from "../src/api";

test("mobile result, collection and independent audio state remain usable", async ({
  page,
  request,
}, info) => {
  const jobs: Job[] = await (await request.get("/api/v1/analyses")).json();
  const job = jobs.find(
    (item) =>
      item.state === "completed" && item.request.pair_id && item.report_path,
  )!;
  expect(job).toBeTruthy();
  await page.setViewportSize({ width: 320, height: 740 });
  await page.goto("/");
  await openHistory(page, job.id.slice(0, 12));
  await expect(page.locator(".analysis-outcome h2")).toBeVisible();
  expect(
    await page
      .locator(".analysis-outcome h2")
      .evaluate((node) => node.getBoundingClientRect().bottom),
  ).toBeLessThan(740);
  await expect(page.locator(".library")).toHaveCount(0);
  const reference = page.getByLabel("reference audio", { exact: true });
  const participant = page.getByLabel("participant audio", { exact: true });
  const track = page.getByRole("region", {
    name: "reference timeline",
    exact: true,
  });
  await track
    .getByText("Precision selection and interval replay", { exact: true })
    .click();
  await page.getByLabel("reference selection start (s)").fill("0.2");
  await page.getByLabel("reference selection end (s)").fill("0.7");
  await reference.evaluate(async (node: HTMLAudioElement) => {
    node.currentTime = 0.3;
    await node.play();
  });
  await expect
    .poll(() => reference.evaluate((node: HTMLAudioElement) => node.paused))
    .toBe(false);
  await page
    .getByRole("button", { name: "Participant audio", exact: true })
    .click();
  await expect
    .poll(() => reference.evaluate((node: HTMLAudioElement) => node.paused))
    .toBe(true);
  const referenceTime = await reference.evaluate(
    (node: HTMLAudioElement) => node.currentTime,
  );
  await participant.evaluate((node: HTMLAudioElement) => {
    node.currentTime = 0.5;
  });
  await page
    .getByRole("button", { name: "Reference audio", exact: true })
    .click();
  await expect(page.getByLabel("reference selection start (s)")).toHaveValue(
    "0.2",
  );
  await expect(page.getByLabel("reference selection end (s)")).toHaveValue(
    "0.7",
  );
  expect(
    await reference.evaluate((node: HTMLAudioElement) => node.currentTime),
  ).toBeCloseTo(referenceTime);
  expect(
    await participant.evaluate((node: HTMLAudioElement) => node.currentTime),
  ).toBeCloseTo(0.5);
  await track
    .getByRole("button", { name: "Replay selected interval", exact: true })
    .click();
  await expect
    .poll(() =>
      reference.evaluate((node: HTMLAudioElement) => node.currentTime),
    )
    .toBeGreaterThanOrEqual(0.69);
  await expect
    .poll(() => reference.evaluate((node: HTMLAudioElement) => node.paused))
    .toBe(true);
  for (const area of [
    "Recording Library",
    "Analysis Workspace",
    "Rubric and Evidence",
    "Review Workspace",
    "Dataset and Evaluation",
  ] as const) {
    await navigateWorkspace(page, area);
    await expect(
      page.getByRole("heading", { name: area, exact: true }),
    ).toBeVisible();
    await expect(page.locator(".library")).toHaveCount(
      area === "Recording Library" ? 1 : 0,
    );
    if (area === "Recording Library") {
      expect(
        await page
          .locator(".library li")
          .evaluateAll((nodes) =>
            nodes.every(
              (node) => node.getBoundingClientRect().right <= innerWidth,
            ),
          ),
      ).toBe(true);
      await expect(page.locator(".library")).not.toContainText(
        "completed · completed",
      );
    }
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.screenshot({
      path: info.outputPath(`${area.replaceAll(" ", "-")}-320-viewport.png`),
    });
  }
  await page.getByRole("combobox", { name: "Workspace", exact: true }).focus();
  await page.keyboard.press("Home");
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("heading", { name: "Recording Library", exact: true }),
  ).toBeVisible();
});
