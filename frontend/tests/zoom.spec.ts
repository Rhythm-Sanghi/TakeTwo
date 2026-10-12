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
      channel: "chromium",
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
    await page.goto("http://127.0.0.1:8765/");
    await expect(
      page.getByRole("heading", { name: "Recording Library", exact: true }),
    ).toBeVisible();
    const before = await page.evaluate(() => ({
      width: innerWidth,
      dpr: devicePixelRatio,
    }));
    const factor = await worker.evaluate(`async () => {
      const tabs = await chrome.tabs.query({url:'http://127.0.0.1:8765/*'});
      if(tabs.length !== 1) throw new Error('Expected one isolated local tab');
      await chrome.tabs.setZoom(tabs[0].id, 2);
      return chrome.tabs.getZoom(tabs[0].id);
    }`);
    expect(factor).toBe(2);
    await expect
      .poll(() => page.evaluate(() => devicePixelRatio))
      .toBeCloseTo(before.dpr * 2, 1);
    const after = await page.evaluate(() => ({
      width: innerWidth,
      dpr: devicePixelRatio,
    }));
    expect(after.width).toBeLessThanOrEqual(before.width / 2 + 1);
    for (const area of [
      "Recording Library",
      "Analysis Workspace",
      "Rubric and Evidence",
      "Dataset and Evaluation",
    ]) {
      await page.getByRole("button", { name: area, exact: true }).click();
      await expect(
        page.getByRole("heading", { name: area, exact: true }),
      ).toBeFocused();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
      await page.screenshot({
        path: testInfo.outputPath(
          "200-percent-" + area.replaceAll(" ", "-") + ".png",
        ),
        fullPage: true,
      });
    }
    await testInfo.attach("native-tab-zoom", {
      body: JSON.stringify({
        factor,
        before,
        after,
        browser: context.browser()?.version(),
      }),
      contentType: "application/json",
    });
  } finally {
    await context.close();
  }
});
