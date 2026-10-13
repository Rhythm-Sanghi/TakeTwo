import { test, expect, chromium } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs/promises";
import path from "node:path";

test("actual Chromium tab zoom at 200 percent retains all workspace areas", async ({
  browserName,
}, testInfo) => {
  expect(browserName).toBe("chromium"); // Isolated test-only extension uses the native tab zoom API, not CSS or pinch scaling.
  // No user's installed browser, extensions, profile or settings are touched.
  const extension = testInfo.outputPath("zoom-extension");
  await fs.mkdir(extension, { recursive: true });
  await fs.writeFile(
    path.join(extension, "manifest.json"),
    JSON.stringify({
      manifest_version: 3,
      name: "TakeTwo isolated zoom verification",
      version: "1.0",
      permissions: ["tabs"],
      background: { service_worker: "background.js" },
    }),
  );
  await fs.writeFile(
    path.join(extension, "background.js"),
    "chrome.runtime.onInstalled.addListener(() => {});",
  );
  const context = await chromium
    .launchPersistentContext(testInfo.outputPath("zoom-profile"), {
      ...(process.env.TAKETWO_ZOOM_EXECUTABLE
        ? { executablePath: process.env.TAKETWO_ZOOM_EXECUTABLE }
        : { channel: "chromium" }),
      headless: true,
      viewport: { width: 1600, height: 1000 },
      args: [
        "--disable-extensions-except=" + extension,
        "--load-extension=" + extension,
      ],
    })
    .catch((error: Error) => {
      if (error.message.includes("spawn UNKNOWN")) {
        test.skip(
          true,
          "Full Chromium cannot launch on this Windows host (spawn UNKNOWN); actual browser zoom remains unverified.",
        );
      }
      throw error;
    });
  try {
    const worker =
      context.serviceWorkers()[0] ??
      (await context.waitForEvent("serviceworker"));
    const page = await context.newPage();
    const baseURL = testInfo.project.use.baseURL;
    if (!baseURL)
      throw new Error("Native zoom requires the configured browser baseURL.");
    await page.goto(baseURL + "/");
    await expect(
      page.getByRole("heading", { name: "Recording Library", exact: true }),
    ).toBeVisible();
    await expect(
      page.getByText("Local workspace ready", { exact: true }),
    ).toBeVisible();
    const before = await page.evaluate(() => ({
      width: innerWidth,
      dpr: devicePixelRatio,
    }));
    const factor = await worker.evaluate(`(async () => {
      const tabs = await chrome.tabs.query({url:${JSON.stringify(baseURL + "/*")}});
      if(tabs.length !== 1) throw new Error('Expected one isolated local tab');
      await chrome.tabs.setZoom(tabs[0].id, 2);
      return chrome.tabs.getZoom(tabs[0].id);
    })()`);
    expect(factor).toBe(2);
    await expect
      .poll(() => page.evaluate(() => devicePixelRatio))
      .toBeCloseTo(before.dpr * 2, 1);
    const after = await page.evaluate(() => ({
      width: innerWidth,
      dpr: devicePixelRatio,
    }));
    expect(after.width).toBeLessThanOrEqual(before.width / 2 + 1);
    let chartLoadMs: number | null = null;
    for (const area of [
      "Recording Library",
      "Analysis Workspace",
      "Rubric and Evidence",
      "Review Workspace",
      "Dataset and Evaluation",
    ]) {
      await page.getByRole("button", { name: area, exact: true }).click();
      await expect(
        page.getByRole("heading", { name: area, exact: true }),
      ).toBeFocused();
      if (area === "Analysis Workspace") {
        const completed = page
          .locator(".library")
          .getByRole("button")
          .filter({ hasText: "completed" });
        if (await completed.count()) {
          const chartStarted = Date.now();
          await completed.first().click();
          await expect(
            page.locator(".feature-chart .chart-plot").first(),
          ).toBeVisible({ timeout: 30000 }); // Same delivery budget as the completed report workflow.
          chartLoadMs = Date.now() - chartStarted;
          await expect
            .poll(() =>
              page
                .locator(".feature-chart")
                .evaluateAll((nodes) =>
                  nodes.every(
                    (node) =>
                      node.querySelector(".uplot")!.getBoundingClientRect()
                        .width <=
                      node.clientWidth + 1,
                  ),
                ),
            )
            .toBe(true);
          await page
            .locator(".feature-chart")
            .first()
            .screenshot({
              path: testInfo.outputPath("200-percent-populated-chart.png"),
            });
        }
      }
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      const geometry = await page
        .locator("main, .panel, nav")
        .evaluateAll((elements) =>
          elements.map((element) => ({
            tag: element.tagName,
            right: element.getBoundingClientRect().right,
            width: element.getBoundingClientRect().width,
            viewport: innerWidth,
          })),
        );
      expect(geometry.every((box) => box.right <= box.viewport + 1)).toBe(true);
      expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
      await page
        .getByRole("heading", { name: area, exact: true })
        .evaluate((heading) => heading.scrollIntoView({ block: "start" }));
      await page.screenshot({
        path: testInfo.outputPath(
          "200-percent-" + area.replaceAll(" ", "-") + ".png",
        ),
        fullPage: false,
      });
    }
    const evidence = {
      factor,
      before,
      after,
      chartLoadMs,
      browser: context.browser()?.version(),
    };
    const evidencePath = testInfo.outputPath("native-tab-zoom.json");
    await fs.writeFile(evidencePath, JSON.stringify(evidence, null, 2));
    await testInfo.attach("native-tab-zoom", {
      path: evidencePath,
      contentType: "application/json",
    });
  } finally {
    await context.close();
  }
});
