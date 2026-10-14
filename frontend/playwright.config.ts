import { defineConfig } from "@playwright/test";
import path from "node:path";
import { cpSync, existsSync, mkdirSync } from "node:fs";

const repository = path.resolve(import.meta.dirname, "..");
const port = Number(process.env.TAKETWO_BROWSER_PORT ?? 8765);
if (!Number.isInteger(port) || port < 1 || port > 65535)
  throw new Error("TAKETWO_BROWSER_PORT must be an integer from 1 to 65535.");
const baseURL = `http://127.0.0.1:${port}`;
const duration = process.env.TAKETWO_DURATION_SMOKE === "1";
const genuine = process.env.TAKETWO_REAL_SMOKE === "1" || duration;
const pilot = process.env.TAKETWO_PILOT_SMOKE === "1";
const reviewPilot = process.env.TAKETWO_REVIEW_PILOT === "1";
const inheritedWorkspace = process.env.TAKETWO_BROWSER_WORKSPACE;
const workspace =
  inheritedWorkspace ??
  (reviewPilot
    ? path.join(repository, "local-data", `browser-review-pilot-${Date.now()}`)
    : duration
      ? path.join(repository, "local-data", `browser-duration-${Date.now()}`)
      : path.join(
          repository,
          "local-data",
          `${pilot ? "browser-pilot" : genuine ? "browser-real" : "browser-software"}-${Date.now()}`,
        ));
const fixtureRoot = process.env.TAKETWO_GENUINE_FIXTURES;
const alignmentConfig = process.env.TAKETWO_TEST_ALIGNMENT_CONFIG;
const realMode = genuine || pilot || reviewPilot;
if (realMode) {
  if (!fixtureRoot || !alignmentConfig) {
    throw new Error(
      "Genuine browser tests are not configured. Run scripts/prepare_genuine_fixtures.py, then set TAKETWO_GENUINE_FIXTURES and TAKETWO_TEST_ALIGNMENT_CONFIG. Private fixtures are never supplied by CI.",
    );
  }
  const required = [alignmentConfig];
  if (pilot)
    required.push(
      ...["reference", "natural", "slow", "uneven", "near-perfect"].map(
        (name) => path.join(fixtureRoot, "pilot", name + ".wav"),
      ),
    );
  if (genuine && !duration)
    required.push(
      path.join(fixtureRoot, "archive.wav"),
      path.join(fixtureRoot, "transcript.txt"),
    );
  if (duration || reviewPilot) {
    const source = path.join(
      fixtureRoot,
      duration ? "duration-workspace" : "review-workspace",
    );
    required.push(
      ...["manifest.jsonl", "originals", "normalized"].map((entry) =>
        path.join(source, entry),
      ),
    );
    for (const entry of required)
      if (!existsSync(entry))
        throw new Error(
          "Missing genuine fixture: " +
            entry +
            ". Re-run the documented fixture preparation step.",
        );
    if (!inheritedWorkspace) {
      mkdirSync(workspace);
      for (const entry of ["manifest.jsonl", "originals", "normalized"])
        cpSync(path.join(source, entry), path.join(workspace, entry), {
          recursive: true,
          errorOnExist: true,
          force: false,
        });
    }
  }
  for (const entry of required)
    if (!existsSync(entry))
      throw new Error(
        "Missing genuine fixture: " +
          entry +
          ". Re-run the documented fixture preparation step.",
      );
}
process.env.TAKETWO_BROWSER_WORKSPACE = workspace;
export default defineConfig({
  testDir: "./tests",
  testMatch: reviewPilot
    ? ["review-pilot.spec.ts"]
    : duration
      ? ["duration.spec.ts"]
      : pilot
        ? ["pilot.spec.ts", "zoom.spec.ts"]
        : [
            "workspace.spec.ts",
            "zoom.spec.ts",
            "zy-presentation.spec.ts",
            "zy-readiness.spec.ts",
            "zz-experience.spec.ts",
            "zz-inspection.spec.ts",
            "zz-mobile.spec.ts",
            "zz-review.spec.ts",
          ],
  timeout: genuine || reviewPilot ? 900000 : 240000,
  workers: 1,
  fullyParallel: false,
  use: {
    actionTimeout: 15000,
    baseURL,
    headless: true,
    viewport: { width: 1600, height: 1000 },
    trace: "retain-on-failure",
  },
  webServer: {
    command: `"${path.join(repository, ".venv/Scripts/python.exe")}" -m taketwo.web.cli --port ${port} --workspace "${workspace}"${realMode ? ` --alignment-config "${alignmentConfig}"` : ""}`,
    cwd: repository,
    url: `${baseURL}/api/v1/health`,
    reuseExistingServer: false,
    timeout: 30000,
  },
});
