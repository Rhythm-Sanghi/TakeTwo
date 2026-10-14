import { navigateWorkspace, openHistory } from "./navigation";
import { test, expect, request as http } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import type { Recording, Job, FeatureWindow } from "../src/api";

// Real generated oscillators, real CPU extraction. No speech or human reviews.
function tone(duration: number, frequency: number) {
  const samples = 16000 * duration;
  const wav = Buffer.alloc(44 + samples * 2);
  wav.write("RIFF");
  wav.writeUInt32LE(wav.length - 8, 4);
  wav.write("WAVEfmt ", 8);
  wav.writeUInt32LE(16, 16);
  wav.writeUInt16LE(1, 20);
  wav.writeUInt16LE(1, 22);
  wav.writeUInt32LE(16000, 24);
  wav.writeUInt32LE(32000, 28);
  wav.writeUInt16LE(2, 32);
  wav.writeUInt16LE(16, 34);
  wav.write("data", 36);
  wav.writeUInt32LE(samples * 2, 40);
  for (let i = 0; i < samples; i++)
    wav.writeInt16LE(
      Math.round(
        5000 *
          Math.sin((2 * Math.PI * frequency * i) / 16000) *
          (0.7 + 0.3 * Math.sin(i / 16000)),
      ),
      44 + i * 2,
    );
  return wav;
}

test("full native chart domains, recording counts, review navigation and paper layout", async ({
  page,
  request,
}, info) => {
  test.setTimeout(900000);
  const before = await (
    await request.get("/api/v1/dataset", { maxRetries: 2 })
  ).json();
  const records: Recording[] = [];
  const jobs: Job[] = [];
  const measurements: unknown[] = [];
  for (const [index, duration] of [15, 29, 30, 40, 45].entries()) {
    // A fresh upload context avoids stale Windows keep-alive sockets after CPU/chart inspection.
    // Do not retry a mutation after an ambiguous connection reset.
    const upload = await http.newContext({ baseURL: info.project.use.baseURL });
    const response = await upload.post("/api/v1/recordings", {
      multipart: {
        audio: {
          name: `software-presentation-${duration}.wav`,
          mimeType: "audio/wav",
          buffer: tone(duration, 200 + index * 20),
        },
        metadata: JSON.stringify({
          recording_type:
            index === 0 ? "controlled_reference" : "human_participant",
          local_permission: true,
          speaker_label: "presentation-oscillator-only",
          transcript: "Software oscillator presentation fixture only.",
          reference_id: index === 0 ? null : records[0].id,
          consent_evidence: "Software tone; no human or consent assertion",
          title: "Generated software fixture, not speech",
        }),
      },
    });
    expect(response.status()).toBe(201);
    const recording: Recording = await response.json();
    await upload.dispose();
    records.push(recording);
    let pairId = null;
    if (index > 0) {
      const pairs = await (await request.get("/api/v1/pairs")).json();
      const pair = pairs.find(
        (p: { participant_id: string }) => p.participant_id === recording.id,
      );
      pairId = pair.id;
    }
    const created = await request.post("/api/v1/analyses", {
      data: { reference_id: records[0].id, pair_id: pairId, align: false },
    });
    expect(created.status()).toBe(202);
    let job: Job = await created.json();
    await expect
      .poll(
        async () => {
          job = await (await request.get(`/api/v1/analyses/${job.id}`)).json();
          if (job.state === "failed")
            throw new Error(JSON.stringify(job.error));
          return job.state;
        },
        { timeout: 210000 },
      )
      .toBe("completed");
    jobs.push(job);
    const responseWindow = await request.get(
      `/api/v1/analyses/${job.id}/features/${recording.id}?name=rms&start_s=0&end_s=${duration}&max_points=1500`,
    );
    expect(responseWindow.status()).toBe(200);
    const data: FeatureWindow = await responseWindow.json();
    expect(data.times_s.at(-1)).toBeGreaterThan(duration - 0.1);
    await page.goto("/");
    await page
      .locator(".library")
      .getByRole("button")
      .filter({ hasText: job.id.slice(0, 12) })
      .click();
    if (
      (page.viewportSize()?.width ?? 1600) <= 800 &&
      recording.role === "participant"
    )
      await page
        .getByRole("button", { name: "Participant audio", exact: true })
        .click();
    const chart = page.getByRole("region", {
      name: `${recording.role} rms chart`,
      exact: true,
    });
    await expect(chart.locator(".chart-plot")).toHaveAttribute(
      "data-domain-end",
      String(duration),
    );
    await expect(chart.locator(".chart-plot")).toHaveAttribute(
      "data-domain-start",
      "0",
    );
    await expect(
      chart.getByText(`Viewing native time: 0.000–${duration.toFixed(3)} s.`, {
        exact: false,
      }),
    ).toBeVisible();
    for (const width of [1920, 1366, 800, 390, 320]) {
      await page.setViewportSize({ width, height: 1000 });
      if (width <= 800 && recording.role === "participant")
        await page
          .getByRole("button", { name: "Participant audio", exact: true })
          .click();
      await expect
        .poll(() =>
          chart.evaluate((n) => {
            const plot = n.querySelector(".uplot")!;
            return plot.getBoundingClientRect().width <= n.clientWidth + 1;
          }),
        )
        .toBe(true);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
    }
    measurements.push({
      duration,
      last_frame_center_s: data.times_s.at(-1),
      points: data.values.length,
      job_id: job.id,
    });
  }
  await page.setViewportSize({ width: 1366, height: 1000 });
  // Read-only requests may safely reconnect after Windows closes an idle socket.
  const counts = await (
    await request.get("/api/v1/dataset", { maxRetries: 2 })
  ).json();
  expect(
    counts.inventory_counts.human_participant_takes -
      before.inventory_counts.human_participant_takes,
  ).toBe(4);
  expect(
    counts.inventory_counts.distinct_speaker_ids -
      before.inventory_counts.distinct_speaker_ids,
  ).toBe(1);
  expect(counts.inventory_counts.verified_transcripts).toBe(
    before.inventory_counts.verified_transcripts,
  );
  await navigateWorkspace(page, "Dataset and Evaluation");
  await page.getByLabel("Readiness recording").selectOption(records[4].id);
  await page
    .getByRole("button", { name: "Open Review Workspace", exact: true })
    .click();
  await expect(page.getByLabel("Recording", { exact: true })).toHaveValue(
    records[4].id,
  );
  await expect(
    page.getByRole("button", { name: "Start reviewer handoff" }),
  ).toBeDisabled();
  expect(
    (
      await request.get("/api/v1/review-workspace/mode", { maxRetries: 2 })
    ).ok(),
  ).toBe(true);
  expect(
    (
      await (
        await request.get("/api/v1/review-workspace/mode", { maxRetries: 2 })
      ).json()
    ).active_session,
  ).toBeNull();
  await openHistory(page, jobs[4].id.slice(0, 12));
  await page
    .getByText("Technical details · scores, coverage and scientific exports", {
      exact: true,
    })
    .click();
  await expect(page.getByText("Overall: Unavailable")).toBeVisible();
  for (const summary of await page
    .locator(".dimension-diagnostics > details > summary")
    .all())
    await summary.click();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  // Printing with every raw-data disclosure open must not print its rows.
  await page
    .locator("details")
    .evaluateAll((nodes) => nodes.forEach((n) => (n.open = true)));
  await page.pdf({
    path: info.outputPath("analysis-summary.pdf"),
    format: "A4",
    printBackground: true,
  });
  await page.emulateMedia({ media: "print" });
  await expect(page.locator(".chart-values").first()).not.toBeVisible();
  await expect(page.locator("nav")).not.toBeVisible();
  await expect(page.locator(".print-chart").first()).toBeVisible();
  expect(
    await page
      .locator(".print-chart")
      .first()
      .evaluate((n: HTMLImageElement) => n.naturalWidth),
  ).toBeGreaterThan(0);
  await page.emulateMedia({ media: "screen" });
  await expect(page.locator(".chart-values").first()).toBeVisible();
  await page.screenshot({
    path: info.outputPath("analysis-after-print.png"),
    fullPage: true,
  });
  await info.attach("native-domain-evidence.json", {
    body: JSON.stringify(measurements, null, 2),
    contentType: "application/json",
  });
});
