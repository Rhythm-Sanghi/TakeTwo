import { defineConfig } from "@playwright/test";
import path from "node:path";

const repository = path.resolve(import.meta.dirname, "..");
const genuine = process.env.TAKETWO_REAL_SMOKE === "1";
const workspace = path.join(
  repository,
  "local-data",
  `${genuine ? "browser-real" : "browser-software"}-${Date.now()}`,
);
export default defineConfig({
  testDir: "./tests",
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
