import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";

// Optional local acceptance: these originals are user-provided and never shipped.
const fixtures = process.env.TAKETWO_GENUINE_FIXTURES!;
const transcript =
  "Technology has changed the way we work, learn, and communicate. Every day, we rely on tools that make difficult tasks easier. But technology is most useful when it helps people solve real problems. A good idea does not need to be complicated. It needs to be practical, reliable, and easy to understand. The future will not be shaped by technology alone, but by the people who choose how to use it.";

test("actual private five-take pilot imports without invented rights or reviews", async ({
  page,
  request,
}, testInfo) => {
  await page.goto("/");
  await expect(page.getByText(/Library is empty/)).toBeVisible();
  await page.getByLabel("Recording type").selectOption("human_participant");
  await expect(
    page.getByText(/Import a public or self-recorded reference first/),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Import recording", exact: true }),
  ).toBeDisabled();
  for (const [index, name] of [
    "reference",
    "natural",
    "slow",
    "uneven",
    "near-perfect",
  ].entries()) {
    await page
      .getByLabel("Recording type")
      .selectOption(index === 0 ? "controlled_reference" : "human_participant");
    if (index) {
      await page
        .getByLabel("Compare with reference")
        .selectOption({ index: 1 });
      await page
        .getByLabel(
          "I intend this take to contain the same words as the selected reference",
        )
        .check();
    }
    await page
      .getByLabel("Audio file", { exact: true })
      .setInputFiles(path.join(fixtures, "pilot", name + ".wav"));
    await page.getByLabel("Spoken transcript").fill(transcript);
    await page
      .getByLabel(
        "I have permission to store and process this recording locally",
      )
      .check();
    const provenance = page.locator("details").filter({
      has: page.getByText("Source and provenance", { exact: true }),
    });
    if ((await provenance.getAttribute("open")) === null)
      await page.getByText("Source and provenance", { exact: true }).click();
    await page
      .getByLabel("Speaker label (optional)")
      .fill("User practice speaker; same person across these takes");
    if (index)
      await page.getByLabel("Same speaker as the selected reference").check();
    await page
      .getByRole("button", { name: "Import recording", exact: true })
      .click();
    await expect(
      page.getByRole("status").filter({ hasText: "Imported " + name + ".wav" }),
    ).toBeVisible();
  }
  const recordings = await (await request.get("/api/v1/recordings")).json();
  const pairs = await (await request.get("/api/v1/pairs")).json();
  expect(recordings).toHaveLength(5);
  expect(pairs).toHaveLength(4);
  expect(
    recordings.every((r: { origin: string }) => r.origin === "self_recorded"),
  ).toBe(true);
  expect(
    new Set(recordings.map((r: { speaker_id: string }) => r.speaker_id)).size,
  ).toBe(1);
  for (const r of recordings) {
    expect(r.transcript.status).toBe("unverified");
    expect(r.provenance.rights.status).toBe("pending");
    expect(r.provenance.rights.holder).toBeNull();
    expect(r.provenance.rights.license_name).toBeNull();
  }
  expect(
    pairs.every(
      (p: { identity_status: string }) => p.identity_status === "needs_review",
    ),
  ).toBe(true);
  expect(
    pairs.every(
      (p: { intended_severity: number | null }) => p.intended_severity === null,
    ),
  ).toBe(true);
  await page
    .getByRole("button", { name: "Analysis Workspace", exact: true })
    .click();
  await expect(page.getByLabel("Participant pair")).not.toHaveValue("");
  await expect(
    page.getByText(/A selected recording exceeds the 45-second/),
  ).not.toBeVisible();
  await expect(
    page.getByRole("button", { name: "Run analysis", exact: true }),
  ).toBeEnabled();
  await page.getByLabel("Seek reference", { exact: true }).fill("1.25");
  await expect
    .poll(() =>
      page
        .getByLabel("reference audio", { exact: true })
        .evaluate((a: HTMLAudioElement) => a.currentTime),
    )
    .toBeCloseTo(1.25, 1);
  const waveform = await (
    await request.get(
      "/api/v1/recordings/" + recordings[0].id + "/waveform?bins=20",
    )
  ).json();
  expect(waveform.bins.some((b: number[]) => b[3] > 0.01)).toBe(true);
  await page.screenshot({
    path: testInfo.outputPath("actual-pilot-workspace.png"),
    fullPage: true,
  });
  for (const width of [1600, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const area of [
      "Recording Library",
      "Analysis Workspace",
      "Rubric and Evidence",
      "Dataset and Evaluation",
    ]) {
      await page.getByRole("button", { name: area, exact: true }).click();
      expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
    }
  }
  await testInfo.attach("actual-pilot-inventory", {
    body: JSON.stringify({ recordings, pairs }, null, 2),
    contentType: "application/json",
  });
});
