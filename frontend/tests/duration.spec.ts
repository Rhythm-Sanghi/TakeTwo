import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

// Optional local capacity acceptance. Requires the documented archival 45 s
// workspace and supervised benchmark; synthetic control is explicitly separate.
test("45 s native playback, alignment, responsive CPU processing and report", async ({
  page,
  request,
}, info) => {
  // Retry one stale keep-alive ECONNRESET on idempotent evidence reads only.
  const get = (url: string) => request.get(url, { maxRetries: 1 });
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const health = await (await get("/api/v1/health")).json();
  expect(health.maximum_analysis_duration_s).toBe(45);
  const recordings = await (await get("/api/v1/recordings")).json();
  expect(recordings).toHaveLength(2);
  expect(
    recordings.every(
      (r: { normalized_info: { duration_s: number } }) =>
        r.normalized_info.duration_s === 45,
    ),
  ).toBe(true);
  expect(recordings.map((r: { origin: string }) => r.origin).sort()).toEqual([
    "source",
    "synthetic",
  ]);
  await page.goto("/");
  await page
    .getByRole("button", { name: "Analysis Workspace", exact: true })
    .click();
  await page
    .getByLabel("Reference recording")
    .selectOption(
      recordings.find((r: { role: string }) => r.role === "reference").id,
    );
  await page.getByLabel("Participant pair").selectOption({ index: 1 });
  await expect(page.getByLabel("reference selection end (s)")).toHaveValue(
    "45",
  );
  await expect(page.getByText(/45 s analysis limit/)).toBeVisible();
  await page.getByLabel("Seek reference", { exact: true }).fill("44");
  const audio = page.getByLabel("reference audio", { exact: true });
  await expect
    .poll(() => audio.evaluate((a: HTMLAudioElement) => a.currentTime))
    .toBeCloseTo(44, 1);
  await audio.evaluate((a: HTMLAudioElement) => a.play());
  await expect
    .poll(() => audio.evaluate((a: HTMLAudioElement) => a.currentTime))
    .toBeGreaterThan(44.1);
  await audio.evaluate((a: HTMLAudioElement) => a.pause());
  await page.getByLabel("Run automatic alignment").check();
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect
    .poll(async () => (await (await get("/api/v1/analyses")).json())[0]?.state)
    .toBe("running");
  // Interact with the actual UI while the separate worker processes 45 s inputs.
  for (const name of [
    "Rubric and Evidence",
    "Dataset and Evaluation",
    "Analysis Workspace",
  ]) {
    await page.getByRole("button", { name, exact: true }).click();
    await expect(
      page.getByRole("heading", { name, exact: true }),
    ).toBeFocused();
  }
  await page.getByLabel("Seek reference", { exact: true }).fill("40");
  await expect
    .poll(() => audio.evaluate((a: HTMLAudioElement) => a.currentTime))
    .toBeCloseTo(40, 1);
  await expect
    .poll(
      async () => {
        const jobs = await (await get("/api/v1/analyses")).json();
        if (jobs[0].state === "failed")
          throw new Error(JSON.stringify(jobs[0].error));
        return jobs[0].state;
      },
      { timeout: 610000 },
    )
    .toBe("completed");
  await expect(page.getByText("Overall: Unavailable")).toBeVisible({
    timeout: 30000,
  });
  const job = (await (await get("/api/v1/analyses")).json())[0];
  const report = await (await get(`/api/v1/analyses/${job.id}/report`)).json();
  expect(
    report.inputs.every(
      (r: { duration_s: number; spectral_frame_count: number }) =>
        r.duration_s === 45 && r.spectral_frame_count === 4498,
    ),
  ).toBe(true);
  expect(job.cache_hits).toEqual([]);
  for (const input of report.inputs) {
    const alignment = await (
      await get(
        `/api/v1/analyses/${job.id}/alignments/${input.provenance.recording_id}`,
      )
    ).json();
    expect(alignment.status).toBe("succeeded");
    expect(alignment.duration_s).toBe(45);
    expect(alignment.words).toHaveLength(60);
    expect(alignment.phones).toHaveLength(265);
    expect(alignment.independently_reviewed).toBe(false);
  }
  expect(report.overall_score).toBeNull();
  await info.attach("duration-browser-evidence.json", {
    body: JSON.stringify({ job, eligibility: report.eligibility }, null, 2),
    contentType: "application/json",
  });
  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Export report JSON" }).click();
  await (await download).saveAs(info.outputPath("duration-report.json"));
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  expect(errors).toEqual([]);
});
