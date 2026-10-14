import { navigateWorkspace } from "./navigation";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";
import type { ComparativeReport, Job, Pair, Recording } from "../src/api";

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
  await navigateWorkspace(page, "Analysis Workspace");
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
      await navigateWorkspace(page, area);
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

test("genuine selected pair runs comparative analysis with native A/B listening and complete exports", async ({
  page,
  request,
}, info) => {
  const recordings: Recording[] = await (
    await request.get("/api/v1/recordings")
  ).json();
  const pairs: Pair[] = await (await request.get("/api/v1/pairs")).json();
  const reference = recordings.find(
    (r) => r.original_filename === "reference.wav",
  )!;
  const participant = recordings.find(
    (r) => r.original_filename === "uneven.wav",
  )!;
  const pair = pairs.find(
    (p) =>
      p.reference_id === reference.id && p.participant_id === participant.id,
  )!;
  await page.goto("/");
  await navigateWorkspace(page, "Analysis Workspace");
  await page
    .getByRole("combobox", { name: "Reference recording", exact: true })
    .selectOption(reference.id);
  await page
    .getByRole("combobox", { name: "Participant pair", exact: true })
    .selectOption(pair.id);
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "What analysis found", exact: true }),
  ).toBeVisible({ timeout: 630000 });
  const jobs: Job[] = await (await request.get("/api/v1/analyses")).json();
  const job = jobs.find(
    (j) => j.state === "completed" && j.request.pair_id === pair.id,
  )!;
  expect(job).toBeTruthy();
  const endpoint = `/api/v1/analyses/${job.id}/insights`;
  const report: ComparativeReport = await (await request.get(endpoint)).json();
  expect(
    report.exploratory.recordings.map((r) => r.provenance.audio_sha256).sort(),
  ).toEqual(
    [reference.normalized_sha256, participant.normalized_sha256].sort(),
  );
  expect(report.groups.length).toBeLessThan(
    report.exploratory.candidates.length,
  );
  expect(report.segments.filter((s) => s.kind === "word")).toHaveLength(
    reference.tokens.length,
  );
  expect(report.phrase_unavailable_reason).toBeTruthy();
  expect(report.anomalies.length).toBeGreaterThan(0);
  const anomaly = report.anomalies[0];
  const card = page.locator(`[data-evidence-id="${anomaly.id}"]`);
  for (const role of ["reference", "participant"]) {
    await card
      .getByRole("button", { name: `Listen to ${role}`, exact: true })
      .click();
    const audio = page.getByLabel(`${role} audio`, { exact: true });
    await expect
      .poll(() => audio.evaluate((n: HTMLAudioElement) => n.paused))
      .toBe(false);
    await expect
      .poll(() => audio.evaluate((n: HTMLAudioElement) => n.paused), {
        timeout: 15000,
      })
      .toBe(true);
  }
  const exported = await (await request.get(endpoint + "/export")).json();
  expect(exported.result).toEqual(report);
  const csv = await (
    await request.get(
      `/api/v1/analyses/${job.id}/exploratory/export?format=csv`,
    )
  ).text();
  expect(
    csv
      .split(/\r?\n/)
      .filter((row) => row.startsWith("c-"))
      .map((row) => row.split(",")[0])
      .sort(),
  ).toEqual(report.exploratory.candidates.map((c) => c.id).sort());
  const assessment = await (
    await request.get(`/api/v1/analyses/${job.id}/report`)
  ).json();
  expect(assessment.eligibility.state).not.toBe("ELIGIBLE");
  await info.attach("genuine-comparative-report", {
    body: JSON.stringify(report),
    contentType: "application/json",
  });
  await page.setViewportSize({ width: 1366, height: 900 });
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({
    path: info.outputPath("genuine-comparative-workspace.png"),
    fullPage: true,
  });
});
