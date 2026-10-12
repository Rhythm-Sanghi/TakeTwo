import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";

const repository = path.resolve(import.meta.dirname, "../..");
const genuine = process.env.TAKETWO_REAL_SMOKE === "1";

test("actual import → CPU processing → native playback → evidence → export", async ({
  page,
  request,
}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Recording Library", exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/Library is empty/)).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to workspace" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();
  async function fillImport(participant = false) {
    if (participant)
      await page
        .getByLabel("Recording role")
        .selectOption({ label: "Participant for generated-reference.wav" });
    await page
      .getByLabel("Audio file", { exact: true })
      .setInputFiles(
        path.join(
          repository,
          genuine
            ? "local-data/acquisition/inaugural-salutation.wav"
            : `local-data/browser-fixtures/generated-${participant ? "participant" : "reference"}.wav`,
        ),
      );
    await page
      .getByLabel("Spoken transcript")
      .fill(
        genuine
          ? "Vice President Johnson, Mr. Speaker, Mr. Chief Justice, President Eisenhower, Vice President Nixon, President Truman, Reverend Clergy, fellow citizens:"
          : "Generated signal fixture only.",
      );
    if (!participant)
      await page
        .getByLabel("Speech family ID")
        .fill(genuine ? "jfk-inaugural-salutation" : "browser-fixture-family");
    await page
      .getByLabel("Speaker ID")
      .fill(
        genuine
          ? "john-f-kennedy"
          : `software-fixture-${participant ? "participant" : "reference"}`,
      );
    await page
      .getByLabel("Source ID")
      .fill(genuine ? "jfkwha-001" : `fixture-${participant ? "p" : "r"}`);
    if (!participant)
      await page
        .getByLabel("Work ID")
        .fill(genuine ? "jfk-inaugural-1961" : "fixture-work");
    await page
      .getByLabel("Source title / recording session")
      .fill(
        genuine
          ? "JFK inaugural address — salutation draft excerpt"
          : "Generated oscillator software fixture; not speech",
      );
    await page
      .getByLabel("Source URL")
      .fill(
        genuine
          ? "https://www.jfklibrary.org/asset-viewer/archives/jfkwha-001"
          : "https://example.invalid/software-fixture",
      );
    await page.getByLabel("Access / recording date").fill("2026-10-11");
    if (participant)
      await page
        .getByLabel("Consent evidence reference")
        .fill("TEST ONLY; generated tone, no human speaker or consent claim");
    else
      await page
        .getByLabel("Reference selection rationale")
        .fill(
          genuine
            ? "Public-domain archival candidate for real acoustic inspection; transcript and excerpt remain independently unreviewed."
            : "TEST ONLY; generated signal is not an effective public speaker",
        );
    await page
      .getByLabel("Rights holder")
      .fill(
        genuine
          ? "United States government / White House Signal Agency"
          : "Test signal generator",
      );
    await page
      .getByLabel("License / permission name")
      .fill(genuine ? "Public domain" : "Software fixture only");
    await page
      .getByLabel("Rights evidence reference")
      .fill(
        genuine
          ? "https://www.jfklibrary.org/asset-viewer/archives/jfkwha-001"
          : "scripts/make_browser_fixtures.py",
      );
    await page
      .getByLabel("Attribution", { exact: true })
      .fill(
        genuine
          ? "John F. Kennedy Presidential Library and Museum; recording by White House Signal Agency"
          : "Generated tone; not competition data",
      );
    if (genuine)
      await page
        .getByLabel(
          "I have evidence permitting adaptation and public redistribution",
        )
        .check();
    await page
      .getByRole("button", { name: "Import recording", exact: true })
      .click();
    await expect(
      page.getByRole("heading", { name: "Recording metadata", exact: true }),
    ).toBeVisible();
  }
  await fillImport();
  await expect(
    page.getByText("unverified · 0 recorded reviewers"),
  ).toBeVisible();
  if (!genuine) await fillImport(true);
  await page
    .getByRole("button", { name: "Analysis Workspace", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Analysis Workspace", exact: true }),
  ).toBeFocused();
  if (!genuine)
    await page.getByLabel("Participant pair").selectOption({ index: 1 });
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await page
    .getByRole("button", { name: "Rubric and Evidence", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Rubric and Evidence", exact: true }),
  ).toBeFocused();
  await page
    .getByRole("button", { name: "Analysis Workspace", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Analysis Workspace", exact: true }),
  ).toBeFocused();
  await expect
    .poll(
      async () => {
        const list = await (await request.get("/api/v1/analyses")).json();
        if (list[0]?.state === "failed")
          throw new Error(JSON.stringify(list[0].error));
        return list[0]?.state;
      },
      { timeout: 210000 },
    )
    .toBe("completed");
  await expect(page.getByText("Analysis completed: completed.")).toBeVisible({
    timeout: 210000,
  });
  await expect(page.getByText("Overall: Unavailable")).toBeVisible();
  await expect(
    page.getByText(
      "Zero detected regions does not indicate a perfect performance.",
      { exact: false },
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Actual input evidence", exact: true }),
  ).toBeVisible();
  const history = await (await request.get("/api/v1/analyses")).json();
  const job = history[0];
  expect(job.state).toBe("completed");
  const result = await (
    await request.get(`/api/v1/analyses/${job.id}/report`)
  ).json();
  await testInfo.attach("integration-evidence.json", {
    body: JSON.stringify(
      {
        genuine_source: genuine,
        software_fixture: !genuine,
        job_state: job.state,
        job_measurements: job,
        elapsed_job_s:
          (Date.parse(job.updated_at) - Date.parse(job.created_at)) / 1000,
        spectral_frames: result.inputs.map(
          (input: { spectral_frame_count: number }) =>
            input.spectral_frame_count,
        ),
        pitch_valid_fractions: result.inputs.map(
          (input: { pitch_valid_fraction: number }) =>
            input.pitch_valid_fraction,
        ),
        overall_score: result.overall_score,
        eligibility: result.eligibility,
      },
      null,
      2,
    ),
    contentType: "application/json",
  });
  expect(result.overall_score).toBeNull();
  expect(result.inputs[0].spectral_frame_count).toBeGreaterThan(100);
  if (genuine) {
    expect(result.inputs[0].duration_s).toBe(17.3);
    expect(result.inputs[0].pitch_valid_fraction).toBe(0);
    expect(
      job.artifacts[result.inputs[0].provenance.recording_id].alignment,
    ).toBeTruthy();
  }
  const waveform = page.getByRole("img", {
    name: /Measured reference waveform/,
  });
  await expect(waveform).toBeVisible();
  await page.getByLabel("Seek reference", { exact: true }).fill("0.5");
  const audio = page.getByLabel("reference audio", { exact: true });
  await expect
    .poll(() => audio.evaluate((node: HTMLAudioElement) => node.currentTime))
    .toBeCloseTo(0.5, 1);
  await page.getByLabel("Seek reference", { exact: true }).press("ArrowRight");
  await expect
    .poll(() => audio.evaluate((node: HTMLAudioElement) => node.currentTime))
    .toBeGreaterThan(0.5);
  await audio.evaluate((node: HTMLAudioElement) => node.play());
  await expect
    .poll(() => audio.evaluate((node: HTMLAudioElement) => node.currentTime))
    .toBeGreaterThan(0.6);
  await audio.evaluate((node: HTMLAudioElement) => node.pause());
  await page
    .getByRole("button", { name: "Zoom in reference", exact: true })
    .click();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "Export report JSON" }).click();
  const download = await downloadPromise;
  await download.saveAs(testInfo.outputPath("actual-report.json"));
  await page.screenshot({
    path: testInfo.outputPath(
      genuine ? "genuine-workspace.png" : "software-workspace.png",
    ),
    fullPage: true,
  });
  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations).toEqual([]);
  await page
    .getByRole("button", { name: "Rubric and Evidence", exact: true })
    .click();
  await expect(
    page.getByText("delivery-v0 · reference agreement", { exact: true }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page
    .getByRole("button", { name: "Dataset and Evaluation", exact: true })
    .click();
  await expect(page.getByText(/No evaluation results exist/)).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.setViewportSize({ width: 800, height: 1000 });
  await page.screenshot({
    path: testInfo.outputPath("responsive-evaluation.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 320, height: 800 });
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
  }
  await page.screenshot({
    path: testInfo.outputPath("narrow-evaluation.png"),
    fullPage: true,
  });
  // Retry the exact request after genuine cancellation; no mocked lifecycle response.
  await page
    .getByRole("button", { name: "Analysis Workspace", exact: true })
    .click();
  const cancelled = await (
    await request.post("/api/v1/analyses", { data: job.request })
  ).json();
  await request.post(`/api/v1/analyses/${cancelled.id}/cancel`);
  await expect
    .poll(
      async () =>
        (await (await request.get(`/api/v1/analyses/${cancelled.id}`)).json())
          .state,
    )
    .toBe("cancelled");
  await page.getByRole("button", { name: "Refresh workspace" }).click();
  await page
    .getByRole("button", { name: new RegExp(cancelled.id.slice(0, 12)) })
    .click();
  await page.getByRole("button", { name: "Retry this analysis" }).click();
  await expect
    .poll(
      async () => {
        const latest = (
          await (await request.get("/api/v1/analyses")).json()
        )[0];
        if (latest.state === "failed")
          throw new Error(JSON.stringify(latest.error));
        return latest.id !== cancelled.id && latest.state === "completed";
      },
      { timeout: 60000 },
    )
    .toBe(true);
  const cached = (await (await request.get("/api/v1/analyses")).json())[0];
  expect(cached.cache_hits).toContain(`features:${job.request.reference_id}`);
  if (genuine)
    expect(cached.cache_hits).toContain(
      `alignment:${job.request.reference_id}`,
    );
  await testInfo.attach("cached-job.json", {
    body: JSON.stringify(cached, null, 2),
    contentType: "application/json",
  });
  expect(errors).toEqual([]);
});
