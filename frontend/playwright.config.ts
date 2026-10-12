import { defineConfig } from "@playwright/test";
import path from "node:path";
import { cpSync, mkdirSync } from "node:fs";

const repository = path.resolve(import.meta.dirname, "..");
const duration = process.env.TAKETWO_DURATION_SMOKE === "1";
const genuine = process.env.TAKETWO_REAL_SMOKE === "1" || duration;
const pilot = process.env.TAKETWO_PILOT_SMOKE === "1";
const workspace = duration
  ? path.join(repository, "local-data", `browser-duration-${Date.now()}`)
  : path.join(
      repository,
      "local-data",
      `${pilot ? "browser-pilot" : genuine ? "browser-real" : "browser-software"}-${Date.now()}`,
    );
if (duration) {
  // Copy immutable inputs, never cached stages, history, locks or reviews.
  mkdirSync(workspace);
  for (const entry of ["manifest.jsonl", "originals", "normalized"]) {
    cpSync(
      path.join(repository, "local-data/duration45-matched", entry),
      path.join(workspace, entry),
      { recursive: true, errorOnExist: true, force: false },
    );
  }
}
export default defineConfig({
  testDir: "./tests",
  testMatch: duration
    ? ["duration.spec.ts"]
    : pilot
      ? ["pilot.spec.ts", "zoom.spec.ts"]
      : ["workspace.spec.ts", "zoom.spec.ts"],
  timeout: genuine ? 360000 : 240000,
  workers: 1,
  fullyParallel: false,
  use: {
    baseURL: "http://127.0.0.1:8765",
    headless: true,
    viewport: { width: 1600, height: 1000 },
    trace: "retain-on-failure",
  },
  webServer: {
    command: `"${path.join(repository, ".venv/Scripts/python.exe")}" -m taketwo.web.cli --workspace "${workspace}"${genuine ? ` --alignment-config "${path.join(repository, "local-data/acquisition/final-alignment-config.json")}"` : ""}`,
    cwd: repository,
    url: "http://127.0.0.1:8765/api/v1/health",
    reuseExistingServer: false,
    timeout: 30000,
  },
});
