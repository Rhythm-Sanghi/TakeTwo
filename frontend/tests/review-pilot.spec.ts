import { navigateWorkspace } from "./navigation";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync } from "node:fs";
import path from "node:path";

test("genuine private pilot: native MFA suggestions, playback and draft boundary editing", async ({
  page,
  request,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const key = readFileSync(
    path.join(process.env.TAKETWO_BROWSER_WORKSPACE!, ".review-operator-key"),
    "utf8",
  );
  const recordings = await (await request.get("/api/v1/recordings")).json();
  expect(recordings).toHaveLength(5);
  const reference = recordings.find(
    (r: { role: string }) => r.role === "reference",
  );
  const submitted = await request.post("/api/v1/analyses", {
    data: { reference_id: reference.id, align: true },
  });
  expect(submitted.status()).toBe(202);
  const id = (await submitted.json()).id;
  await expect
    .poll(
      async () =>
        (
          await (
            await request.get(`/api/v1/analyses/${id}`, { maxRetries: 1 })
          ).json()
        ).state,
      { timeout: 610000, intervals: [1000] },
    )
    .toBe("completed");
  const job = await (
    await request.get(`/api/v1/analyses/${id}`, { maxRetries: 1 })
  ).json();
  await info.attach("actual-pilot-job", {
    body: JSON.stringify(job),
    contentType: "application/json",
  });
  const alignment = await (
    await request.get(`/api/v1/analyses/${id}/alignments/${reference.id}`, {
      maxRetries: 1,
    })
  ).json();
  expect(alignment.status).toBe("succeeded");
  await page.goto("/");
  await navigateWorkspace(page, "Review Workspace");
  await page.getByLabel("Operator key", { exact: true }).fill(key);
  await page
    .getByLabel("Recording", { exact: true })
    .selectOption(reference.id);
  await page
    .getByLabel("Reviewer identifier")
    .fill("automated-draft-check-not-human-review");
  await page.getByLabel("Review activity").selectOption("timing");
  await page.getByLabel("Original MFA suggestion artifact").selectOption(id);
  await page.getByRole("button", { name: "Start reviewer handoff" }).click();
  await expect(
    page.getByRole("heading", { name: "Recording and native timeline" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Load MFA suggestions for manual inspection" })
    .click();
  const originalStart = Math.round(alignment.words[0].start_s * 1000);
  await page.getByLabel("Word start (ms)").fill(String(originalStart + 1));
  await page
    .getByLabel("Phrase end word numbers", { exact: false })
    .fill(String(alignment.words.length));
  await page
    .getByLabel("Listening notes and uncertainty")
    .fill(
      "Automated draft UI verification only. No human boundary approval or ground truth.",
    );
  await page
    .getByLabel("Evidence reference")
    .fill("Playwright real-audio draft software check");
  await page.getByRole("button", { name: "Replay selected word" }).click();
  await expect
    .poll(
      () =>
        page.locator("audio").evaluate((a: HTMLAudioElement) => a.currentTime),
      { timeout: 5000 },
    )
    .toBeGreaterThan(alignment.words[0].start_s);
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(
    page.getByText("Draft saved locally.", { exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Word start (ms)")).toHaveValue(
    String(originalStart + 1),
  );
  await expect(
    page.getByRole("button", { name: "Submit review", exact: true }),
  ).toBeDisabled();
  await page.getByLabel("Word end (ms)").focus();
  await page.keyboard.press("ArrowDown");
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(
    page.getByText("Draft saved locally.", { exact: true }),
  ).toBeVisible();
  for (const width of [1600, 800, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.screenshot({
      path: info.outputPath(`pilot-review-${width}.png`),
      fullPage: true,
    });
  }
  await page.getByText("Operator: end handoff", { exact: true }).click();
  await page.getByLabel("Local operator key").fill(key);
  await page
    .getByRole("button", { name: "End handoff and return to operator" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Recording Library", exact: true }),
  ).toBeVisible();
  expect(await (await request.get("/api/v1/reviews")).json()).toEqual([]);
  // Prepare only explicitly labeled automated DRAFTS on copies, never completed human evidence.
  for (const recording of recordings.filter(
    (r: { id: string }) => r.id !== reference.id,
  )) {
    await navigateWorkspace(page, "Review Workspace");
    await page.getByLabel("Operator key", { exact: true }).fill(key);
    await page
      .getByLabel("Recording", { exact: true })
      .selectOption(recording.id);
    await page
      .getByLabel("Reviewer identifier")
      .fill("automated-draft-check-not-human-review");
    await page.getByLabel("Review activity").selectOption("flaws");
    await page.getByRole("button", { name: "Start reviewer handoff" }).click();
    await expect(
      page.getByRole("heading", { name: "Recording and native timeline" }),
    ).toBeVisible();
    await expect(page.getByLabel("Reference context playback")).toBeVisible();
    await page
      .getByLabel("Reference context playback")
      .evaluate((a: HTMLAudioElement) => a.play());
    await page.getByLabel("Selection start (ms)").fill("1000");
    await page.getByLabel("Selection end (ms)").fill("2000");
    await page.getByRole("button", { name: "Replay selection" }).click();
    await expect
      .poll(() =>
        page
          .getByLabel("Reference context playback")
          .evaluate((a: HTMLAudioElement) => a.paused),
      )
      .toBe(true);
    await expect
      .poll(
        () =>
          page
            .getByLabel("Assigned recording playback")
            .evaluate((a: HTMLAudioElement) => a.currentTime),
        { timeout: 5000 },
      )
      .toBeGreaterThan(1);
    await page
      .getByLabel("Annotation rationale")
      .fill(
        "Automated draft CRUD check only; not a detected or human-judged flaw.",
      );
    await page
      .getByRole("button", { name: "Add annotation", exact: true })
      .click();
    await page.getByRole("button", { name: "Save draft", exact: true }).click();
    await expect(
      page.getByText("Draft saved locally.", { exact: true }),
    ).toBeVisible();
    await page.getByRole("button", { name: /^Edit annotation/ }).click();
    await page.getByLabel("Severity", { exact: true }).selectOption("2");
    await page
      .getByRole("button", { name: "Update annotation", exact: true })
      .click();
    await page.getByRole("button", { name: "Save draft", exact: true }).click();
    await expect(
      page.getByText("Draft saved locally.", { exact: true }),
    ).toBeVisible();
    await page.getByRole("button", { name: /^Delete annotation/ }).click();
    await page.getByRole("button", { name: "Save draft", exact: true }).click();
    await expect(
      page.getByText("Draft saved locally.", { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Submit review", exact: true }),
    ).toBeDisabled();
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.getByText("Operator: end handoff", { exact: true }).click();
    await page.getByLabel("Local operator key").fill(key);
    await page
      .getByRole("button", { name: "End handoff and return to operator" })
      .click();
    await expect(
      page.getByRole("heading", { name: "Recording Library", exact: true }),
    ).toBeVisible();
  }
  expect(await (await request.get("/api/v1/reviews")).json()).toEqual([]);
  expect(errors).toEqual([]);
});
