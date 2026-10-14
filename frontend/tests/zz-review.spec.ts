import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync } from "node:fs";
import path from "node:path";

// Isolated generated-audio software fixtures ONLY. These submissions are not human evidence.
test("review handoff, actual playback, immutable export and adjudication", async ({
  page,
  request,
}, info) => {
  const key = readFileSync(
    path.join(process.env.TAKETWO_BROWSER_WORKSPACE!, ".review-operator-key"),
    "utf8",
  );
  const fixtureReference = (r: { role: string; original_filename: string }) =>
    r.role === "reference" && r.original_filename === "generated-reference.wav";
  let recordings = await (await request.get("/api/v1/recordings")).json();
  // Genuine suites may contain only archival speech. Never attach software
  // approvals or intentionally wrong text to that clip; import the named tone.
  if (!recordings.some(fixtureReference)) {
    await page.goto("/");
    await page.getByLabel("Recording type").selectOption("public_reference");
    await page
      .getByLabel("Audio file", { exact: true })
      .setInputFiles(
        path.resolve(
          import.meta.dirname,
          "../../local-data/browser-fixtures/generated-reference.wav",
        ),
      );
    await page
      .getByLabel("Spoken transcript")
      .fill("Generated signal fixture only.");
    await page
      .getByLabel(
        "I have permission to store and process this recording locally",
      )
      .check();
    await page
      .getByRole("button", { name: "Import recording", exact: true })
      .click();
    await page
      .getByText("Recording metadata and source transcript", { exact: true })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "generated-reference.wav",
        exact: true,
      }),
    ).toBeVisible();
    recordings = await (await request.get("/api/v1/recordings")).json();
  }
  const recording = recordings.find(fixtureReference);
  expect(recording).toBeTruthy();
  expect(recording.normalized_info.duration_s).toBe(2);
  expect(recording.transcript.text).toBe("Generated signal fixture only.");
  async function start(reviewer: string) {
    await page.goto("/");
    await page
      .getByRole("button", { name: "Review Workspace", exact: true })
      .click();
    await page.getByLabel("Operator key", { exact: true }).fill(key);
    await page
      .getByLabel("Recording", { exact: true })
      .selectOption(recording.id);
    await page
      .getByLabel("Reviewer identifier", { exact: true })
      .fill(reviewer);
    await page.getByRole("button", { name: "Start reviewer handoff" }).click();
    await expect(
      page.getByRole("heading", { name: "Recording and native timeline" }),
    ).toBeVisible();
    expect((await request.get("/api/v1/reviews")).status()).toBe(403);
    expect((await request.get("/api/v1/analyses")).status()).toBe(403);
  }
  let fixtureReview = 0;
  async function finish() {
    fixtureReview += 1;
    await page
      .getByLabel("Evidence reference", { exact: true })
      .fill("Playwright software fixture, not a human worksheet");
    await page
      .getByLabel("Listening notes and uncertainty")
      .fill(
        "Automated playback test only; no real person performed this review.",
      );
    await page.getByLabel("Review decision").selectOption("approved");
    await page.getByLabel(/I performed my own review/).check();
    await expect(
      page.getByRole("region", { name: "Assigned review steps" }),
    ).toContainText("Unsaved changes");
    await page.screenshot({
      path: info.outputPath(`software-review-${fixtureReview}-unsaved.png`),
      fullPage: true,
    });
    await page.getByRole("button", { name: "Listen from beginning" }).click();
    await expect
      .poll(
        () => page.locator("audio").evaluate((a: HTMLAudioElement) => a.ended),
        { timeout: 15000 },
      )
      .toBe(true);
    const capabilityUrl = page.url();
    await page.getByRole("button", { name: "4. Validate and submit" }).click();
    await expect(page.locator("#review-submit")).toBeFocused();
    expect(page.url()).toBe(capabilityUrl);
    await page.getByRole("button", { name: "Save draft", exact: true }).click();
    await expect(
      page.getByText("Draft saved locally.", { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Submit review", exact: true }),
    ).toBeEnabled();
    await expect(
      page.getByRole("region", { name: "Assigned review steps" }),
    ).toContainText("Backend completion check passed");
    await page.screenshot({
      path: info.outputPath(`software-review-${fixtureReview}-validated.png`),
      fullPage: true,
    });
    await page
      .getByRole("button", { name: "Submit review", exact: true })
      .click();
    await expect(
      page.getByRole("link", { name: "Export scientific Review JSON" }),
    ).toBeVisible();
    await expect(
      page.getByLabel("Reviewer-corrected transcript"),
    ).toBeDisabled();
    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("link", { name: "Export scientific Review JSON" }).click(),
    ]);
    await download.saveAs(
      info.outputPath(`${Date.now()}-software-review.json`),
    );
  }
  async function unlock() {
    await page.getByText("Operator: end handoff", { exact: true }).click();
    await page.getByLabel("Local operator key", { exact: true }).fill(key);
    await page
      .getByRole("button", { name: "End handoff and return to operator" })
      .click();
    await expect(
      page.getByRole("heading", { name: "Recording Library", exact: true }),
    ).toBeVisible();
  }
  await start("software-reviewer-a");
  await page.screenshot({
    path: info.outputPath("software-review-draft.png"),
    fullPage: true,
  });
  await page
    .getByLabel("Reviewer-corrected transcript")
    .fill("Generated signal fixture only.");
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(
    page.getByText("Draft saved locally.", { exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Reviewer-corrected transcript")).toHaveValue(
    "Generated signal fixture only.",
  );
  await expect(
    page.getByRole("button", { name: "Submit review", exact: true }),
  ).toBeDisabled();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByLabel("Selection start (ms)").focus();
  await page.keyboard.press("ArrowUp");
  await expect(page.getByLabel("Selection start (ms)")).toHaveValue("1");
  for (const width of [1920, 1366, 800, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.screenshot({
      path: info.outputPath(`software-review-draft-${width}.png`),
      fullPage: true,
    });
  }
  await page.setViewportSize({ width: 1600, height: 1000 });
  await finish();
  await page.screenshot({
    path: info.outputPath("submitted-review.png"),
    fullPage: true,
  });
  await unlock();
  await start("software-reviewer-b");
  await page
    .getByLabel("Reviewer-corrected transcript")
    .fill("Different generated fixture words.");
  await finish();
  await unlock();
  await page
    .getByRole("button", { name: "Review Workspace", exact: true })
    .click();
  await page.getByLabel("Operator key", { exact: true }).fill(key);
  await page
    .getByRole("button", { name: "Load sessions and adjudication" })
    .click();
  await expect(
    page.getByText("Reviewers disagree on the checked canonical transcript.", {
      exact: true,
    }),
  ).toBeVisible();
  await page.getByLabel("Adjudicator identifier").fill("software-adjudicator");
  await page
    .getByLabel("Disagreement explanation")
    .fill("Software test: differing text.");
  await page
    .getByLabel("Resolution and required reviewer revisions")
    .fill("Retain both originals; actual reviewers must revisit audio.");
  await page
    .getByRole("button", { name: "Record adjudication for transcript" })
    .click();
  await expect(page.getByText(/awaiting_reviewer_revisions/)).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  const reviews = await (await request.get("/api/v1/reviews")).json();
  expect(
    reviews.filter((r: { reviewer_id: string }) =>
      r.reviewer_id.startsWith("software-reviewer"),
    ),
  ).toHaveLength(2);
});
