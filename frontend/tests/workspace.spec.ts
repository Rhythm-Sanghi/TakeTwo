import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";
import { readFileSync } from "node:fs";

const repository = path.resolve(import.meta.dirname, "../..");
const genuine = process.env.TAKETWO_REAL_SMOKE === "1";
// Native MFA/extraction has a 600 s service deadline; genuine acceptance must
// observe its terminal state rather than timing out at the tone-fixture budget.
const processingTimeout = genuine ? 630000 : 210000;

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
    await page
      .getByLabel("Recording type")
      .selectOption(participant ? "human_participant" : "public_reference");
    if (participant) {
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
      .getByLabel(
        "I have permission to store and process this recording locally",
      )
      .check();
    await page
      .getByLabel("Audio file", { exact: true })
      .setInputFiles(
        genuine
          ? path.join(process.env.TAKETWO_GENUINE_FIXTURES!, "archive.wav")
          : path.join(
              repository,
              `local-data/browser-fixtures/generated-${participant ? "participant" : "reference"}.wav`,
            ),
      );
    await page
      .getByLabel("Spoken transcript")
      .fill(
        genuine
          ? readFileSync(
              path.join(
                process.env.TAKETWO_GENUINE_FIXTURES!,
                "transcript.txt",
              ),
              "utf8",
            ).trim()
          : "Generated signal fixture only.",
      );
    if (!(await page.getByLabel("Speaker label (optional)").isVisible()))
      await page.getByText("Source and provenance", { exact: true }).click();
    await page
      .getByLabel("Speaker label (optional)")
      .fill(
        genuine
          ? "john-f-kennedy"
          : `software-fixture-${participant ? "participant" : "reference"}`,
      );
    await page
      .getByLabel("Recording title (optional)")
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
    if (participant)
      await page
        .getByLabel("Consent evidence reference")
        .fill("TEST ONLY; generated tone, no human speaker or consent claim");
    else
      await page
        .getByLabel("Reference selection rationale (optional)")
        .fill(
          genuine
            ? "Public-domain archival candidate for real acoustic inspection; transcript and excerpt remain independently unreviewed."
            : "TEST ONLY; generated signal is not an effective public speaker",
        );
    if (!(await page.getByLabel("Rights holder").isVisible()))
      await page.getByText("Rights and permissions", { exact: true }).click();
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
    const imported = page.waitForResponse(
      (r) =>
        r.url().endsWith("/api/v1/recordings") &&
        r.request().method() === "POST",
    );
    await page
      .getByRole("button", { name: "Import recording", exact: true })
      .click();
    expect((await imported).status()).toBe(201);
    await expect(
      page.getByText(
        participant ? "2 recordings · 1 pairs" : "1 recordings · 0 pairs",
        { exact: true },
      ),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Recording metadata", exact: true }),
    ).toBeVisible();
  }
  await page.getByLabel("Audio file", { exact: true }).setInputFiles({
    name: "damaged.wav",
    mimeType: "audio/wav",
    buffer: Buffer.from("not decoded audio"),
  });
  await page
    .getByLabel("Spoken transcript")
    .fill("Generated signal fixture only.");
  await page
    .getByLabel("I have permission to store and process this recording locally")
    .check();
  const invalidResponse = page.waitForResponse(
    (r) =>
      r.url().endsWith("/api/v1/recordings") && r.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: "Import recording", exact: true })
    .click();
  expect((await invalidResponse).status()).toBe(422);
  await expect(page.getByRole("alert")).toBeVisible();
  expect(await (await request.get("/api/v1/recordings")).json()).toHaveLength(
    0,
  );
  await fillImport();
  await expect(
    page.getByText("unverified · 0 recorded reviewers"),
  ).toBeVisible();
  if (!genuine) {
    await page.getByLabel("Recording type").selectOption("human_participant");
    await page.getByLabel("Compare with reference").selectOption({ index: 1 });
    await page
      .getByLabel("Audio file", { exact: true })
      .setInputFiles(
        path.join(
          repository,
          "local-data/browser-fixtures/generated-participant.wav",
        ),
      );
    await page
      .getByLabel("Spoken transcript")
      .fill("Mismatched fixture words.");
    await page
      .getByLabel(
        "I intend this take to contain the same words as the selected reference",
      )
      .check();
    await page
      .getByLabel(
        "I have permission to store and process this recording locally",
      )
      .check();
    await page
      .getByRole("button", { name: "Import recording", exact: true })
      .click();
    await expect(page.getByRole("alert")).toContainText(
      "transcript/family differs",
    );
    expect(await (await request.get("/api/v1/recordings")).json()).toHaveLength(
      1,
    );
    await fillImport(true);
  }
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
      { timeout: processingTimeout },
    )
    .toBe("completed");
  await expect(page.getByText("Analysis completed: completed.")).toBeVisible({
    timeout: processingTimeout,
  });
  // Completion publishes artifacts; report delivery still validates bound evidence.
  await expect(page.getByText("Overall: Unavailable")).toBeVisible({
    timeout: 30000,
  });
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
    const alignment = await (
      await request.get(
        `/api/v1/analyses/${job.id}/alignments/${job.request.reference_id}`,
      )
    ).json();
    expect(alignment.status).toBe("succeeded");
    expect(alignment.words).toHaveLength(19);
    expect(alignment.phones.length).toBeGreaterThan(0);
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
    await page.screenshot({
      path: testInfo.outputPath(`narrow-${area.replaceAll(" ", "-")}.png`),
      fullPage: true,
    });
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
  if (!genuine) {
    await page.setViewportSize({ width: 1600, height: 1000 });
    await page
      .getByRole("button", { name: "Recording Library", exact: true })
      .click();
    await page
      .getByLabel("Recording type")
      .selectOption("controlled_reference");
    await page
      .getByLabel("Audio file", { exact: true })
      .setInputFiles(
        path.join(
          repository,
          "local-data/browser-fixtures/generated-controlled-reference.wav",
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
    await expect(
      page.getByRole("heading", {
        name: "generated-controlled-reference.wav",
        exact: true,
      }),
    ).toBeVisible();
    const controlled = (
      await (await request.get("/api/v1/recordings")).json()
    ).find(
      (r: { original_filename: string }) =>
        r.original_filename === "generated-controlled-reference.wav",
    );
    expect(controlled.origin).toBe("self_recorded");
    expect(controlled.provenance.rights.holder).toBeNull();
    // Unrelated import must not destroy the persisted report's bound input context.
    expect(
      await (await request.get(`/api/v1/analyses/${job.id}/report`)).json(),
    ).toEqual(result);
    await page
      .getByRole("button", { name: "Add participant", exact: true })
      .click();
    await expect(page.getByLabel("Compare with reference")).toHaveValue(
      controlled.id,
    );
    await page
      .getByLabel("Audio file", { exact: true })
      .setInputFiles(
        path.join(
          repository,
          "local-data/browser-fixtures/generated-controlled-participant.wav",
        ),
      );
    await page
      .getByLabel(
        "I intend this take to contain the same words as the selected reference",
      )
      .check();
    await page
      .getByLabel(
        "I have permission to store and process this recording locally",
      )
      .check();
    await page
      .getByRole("button", { name: "Import recording", exact: true })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "generated-controlled-participant.wav",
        exact: true,
      }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Analysis Workspace", exact: true })
      .click();
    await expect(page.getByLabel("Participant pair")).not.toHaveValue("");
    await page
      .getByRole("button", { name: "Run analysis", exact: true })
      .click();
    await expect(page.getByText("Analysis completed: completed.")).toBeVisible({
      timeout: 60000,
    });
    await expect(page.getByText("Overall: Unavailable")).toBeVisible();
    await page
      .getByRole("button", { name: "Recording Library", exact: true })
      .click();
    await page
      .getByText("Correct this pairing safely", { exact: true })
      .click();
    await page
      .getByLabel("Correct reference")
      .selectOption(job.request.reference_id);
    await page
      .getByRole("button", { name: "Prepare corrected version", exact: true })
      .click();
    await expect(
      page.getByText(/New two-recording dataset version prepared/),
    ).toBeVisible();
    expect(await (await request.get("/api/v1/recordings")).json()).toHaveLength(
      4,
    );
    expect(
      await (
        await request.get("/api/v1/analyses/" + job.id + "/export")
      ).json(),
    ).toEqual(result);
    expect(errors).toEqual([]);
    // Explicit fixture excerpts exercise the browser recovery path without guessing real speech cuts.
    await page
      .getByRole("button", { name: "Analysis Workspace", exact: true })
      .click();
    await page.getByLabel("reference selection start (s)").fill("0.2");
    await page.getByLabel("reference selection end (s)").fill("1.8");
    await page
      .getByRole("region", { name: "reference timeline" })
      .getByText("Save selection as an analysis excerpt")
      .click();
    const referenceCut = page.getByRole("form", { name: "reference excerpt" });
    await referenceCut
      .getByLabel("Exact excerpt transcript")
      .fill("Generated signal fixture only.");
    await referenceCut.getByRole("button", { name: "Save excerpt" }).click();
    await expect(
      page.getByRole("combobox", { name: "Reference recording", exact: true }),
    ).not.toHaveValue(controlled.id);
    const cutId = await page
      .getByRole("combobox", { name: "Reference recording", exact: true })
      .inputValue();
    await page
      .getByRole("button", { name: /^generated-controlled-participant.wav/ })
      .click();
    await page.getByLabel("participant selection start (s)").fill("0.3");
    await page.getByLabel("participant selection end (s)").fill("1.7");
    await page
      .getByRole("region", { name: "participant timeline" })
      .getByText("Save selection as an analysis excerpt")
      .click();
    const participantCut = page.getByRole("form", {
      name: "participant excerpt",
    });
    await participantCut.getByLabel("Excerpt reference").selectOption(cutId);
    await participantCut
      .getByLabel("Exact excerpt transcript")
      .fill("Generated signal fixture only.");
    await participantCut.getByRole("button", { name: "Save excerpt" }).click();
    await expect(
      page.getByRole("combobox", { name: "Reference recording", exact: true }),
    ).toHaveValue(cutId);
    await expect(page.getByLabel("Participant pair")).not.toHaveValue("");
    expect(await (await request.get("/api/v1/recordings")).json()).toHaveLength(
      6,
    );
    expect(errors).toEqual([]);
  }
});

test("all five workspaces retain controls at desktop, laptop, tablet and narrow widths", async ({
  page,
}, testInfo) => {
  await page.goto("/");
  for (const [width, height] of [
    [1920, 1080],
    [1366, 768],
    [800, 1000],
    [390, 844],
    [320, 740],
  ]) {
    await page.setViewportSize({ width, height });
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
      await page.screenshot({
        path: testInfo.outputPath(`${width}-${area.replaceAll(" ", "-")}.png`),
        fullPage: true,
      });
      const overflow = await page.locator("main *").evaluateAll((elements) =>
        elements
          .filter(
            (element) => element.getBoundingClientRect().right > innerWidth + 1,
          )
          .map((element) => ({
            tag: element.tagName,
            className: element.className,
            right: element.getBoundingClientRect().right,
            text: element.textContent?.slice(0, 100),
          })),
      );
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        `${width}px ${area}: ${JSON.stringify(overflow)}`,
      ).toBe(true);
    }
  }
});
