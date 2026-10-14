import { test, expect } from "@playwright/test";
import type { ComparativeReport, Job, Recording } from "../src/api";
import { openHistory, navigateWorkspace } from "./navigation";

test("summary and full evidence print separately with reference-only terminology", async ({
  page,
  request,
}, info) => {
  const jobs: Job[] = await (await request.get("/api/v1/analyses")).json();
  for (const paired of [true, false]) {
    const job = jobs.find(
      (j) => j.state === "completed" && Boolean(j.request.pair_id) === paired,
    )!;
    const report: ComparativeReport = await (
      await request.get(`/api/v1/analyses/${job.id}/insights`, {
        timeout: 120000,
      })
    ).json();
    await page.goto("/");
    await openHistory(page, job.id.slice(0, 12));
    await expect(page.locator(".comparative-insights")).toBeVisible({
      timeout: 30000,
    });
    if (!paired) {
      await expect(page.locator(".comparative-insights")).toContainText(
        "Automatic acoustic inspection",
      );
      await expect(page.locator(".comparative-insights")).not.toContainText(
        "Automatic comparison",
      );
      await expect(page.locator(".comparative-insights")).not.toContainText(
        "0 provisional paired",
      );
    }
    const originalTitle = await page.title();
    await page.evaluate(() => {
      window.print = () => {};
    });
    for (const type of ["summary", "evidence"]) {
      await page
        .getByRole("button", {
          name:
            type === "summary"
              ? "Export Analysis Summary / save PDF"
              : "Export Full Evidence Report / save PDF",
          exact: true,
        })
        .click();
      expect(await page.title()).toContain(
        paired ? "speech-comparison" : "reference-inspection",
      );
      await page.emulateMedia({ media: "print" });
      await expect(page.locator(".comparative-appendix")).toBeVisible({
        visible: type === "evidence",
      });
      await expect(page.locator(".exploratory-appendix")).toBeVisible({
        visible: type === "evidence",
      });
      if (type === "summary") {
        await expect(page.locator(".summary-title")).toBeVisible();
        await expect(page.locator(".summary-assessment")).toBeVisible();
        if (report.inspection_order.length) {
          await expect(
            page.locator(".insight-list .selection-reason").first(),
          ).toBeVisible();
        } else {
          await expect(page.locator(".comparative-insights")).toContainText(
            paired
              ? "No supported local differences meet the inspection rules"
              : "No supported recording observations meet the inspection rules",
          );
        }
      } else {
        const text = await page.locator(".comparative-appendix").textContent();
        for (const candidate of report.exploratory.candidates)
          expect(text).toContain(candidate.id);
      }
      const pdf = await page.pdf({
        path: info.outputPath(`${paired ? "paired" : "reference"}-${type}.pdf`),
        format: "A4",
        printBackground: true,
        tagged: true,
      });
      expect(pdf.toString("latin1")).toContain("/ToUnicode");
      await page.emulateMedia({ media: null });
      await page.evaluate(() => dispatchEvent(new Event("afterprint")));
      expect(await page.title()).toBe(originalTitle);
      expect(
        await page.evaluate(() => document.body.dataset.reportType),
      ).toBeUndefined();
    }
  }
});

test("native plots stay contained before resize observers finish across breakpoints", async ({
  page,
  request,
}) => {
  const jobs: Job[] = await (await request.get("/api/v1/analyses")).json();
  const job = jobs.find((j) => j.state === "completed" && j.request.pair_id)!;
  await page.goto("/");
  await openHistory(page, job.id.slice(0, 12));
  await expect(page.locator(".feature-chart .uplot")).toHaveCount(2);
  await page.evaluate(() => {
    const overflow: number[] = [];
    Object.assign(window, { plotResizeOverflow: overflow });
    addEventListener("resize", () =>
      overflow.push(document.documentElement.scrollWidth - innerWidth),
    );
  });
  for (const width of [390, 1366, 1920, 1366, 800, 320]) {
    await page.setViewportSize({ width, height: 900 });
    await expect
      .poll(() =>
        page
          .locator(".feature-chart .chart-plot")
          .evaluateAll((nodes) =>
            nodes.every(
              (node) =>
                node.querySelector(".uplot")!.getBoundingClientRect().width <=
                node.clientWidth + 1,
            ),
          ),
      )
      .toBe(true);
  }
  const overflows = await page.evaluate(
    () =>
      (window as Window & { plotResizeOverflow: number[] }).plotResizeOverflow,
  );
  expect(overflows.length).toBeGreaterThan(0);
  expect(overflows.every((width) => width <= 0)).toBe(true);
});

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
