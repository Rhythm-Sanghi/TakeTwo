import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("initial service outage keeps operator views locked and offers a real reconnect action", async ({
  page,
}) => {
  await page.route("**/api/v1/**", (route) => route.abort("connectionfailed"));
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText(
    "Local workspace could not be opened",
  );
  await expect(page.locator(".library")).toHaveCount(0);
  await expect(
    page.getByRole("navigation", { name: "Workspace areas" }),
  ).toHaveCount(0);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.unroute("**/api/v1/**");
  await page
    .getByRole("button", { name: "Retry opening local workspace", exact: true })
    .click();
  await expect(page.locator(".app-header [role=status]")).toHaveText(
    "Local workspace ready",
  );
  await expect(page.locator(".library")).toContainText(
    /\d+ recordings · \d+ pairs/,
  );
});

test("unavailable API during initial load does not fabricate an empty library", async ({
  page,
}) => {
  await page.route("**/api/v1/**", (route) =>
    route.request().url().endsWith("/review-workspace/mode")
      ? route.continue()
      : route.abort("connectionfailed"),
  );
  await page.goto("/");
  await expect(page.locator(".app-header [role=status]")).toHaveText(
    "Local service unavailable. Retry refresh.",
  );
  await expect(page.locator(".library")).toContainText(
    "Current recording and history inventory is unavailable",
  );
  await expect(page.locator(".library")).not.toContainText("0 recordings");
  await expect(page.locator(".library")).not.toContainText("Library is empty");
  await expect(page.locator(".library")).not.toContainText(
    "No analyses have run",
  );
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.unroute("**/api/v1/**");
  await page.getByRole("button", { name: "Reconnect / refresh" }).click();
  await expect(page.locator(".app-header [role=status]")).toHaveText(
    "Local workspace ready",
  );
  await expect(page.locator(".library")).not.toContainText(
    "inventory is unavailable",
  );
  await expect(page.locator(".library")).toContainText(
    /\d+ recordings · \d+ pairs/,
  );
});

test("failed health refresh does not announce cached readiness and recovers", async ({
  page,
}) => {
  await page.goto("/");
  const serviceStatus = page.locator(".app-header [role=status]");
  await expect(serviceStatus).toHaveText("Local workspace ready");
  await page.route("**/api/v1/health", (route) =>
    route.abort("connectionfailed"),
  );
  await page
    .getByRole("button", { name: "Refresh workspace", exact: true })
    .click();
  await expect(serviceStatus).toHaveText(
    "Local service unavailable. Retry refresh.",
  );
  await expect(
    page.getByRole("button", { name: "Reconnect / refresh" }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.unroute("**/api/v1/health");
  await page.getByRole("button", { name: "Reconnect / refresh" }).click();
  await expect(serviceStatus).toHaveText("Local workspace ready");
  await expect(
    page.getByRole("button", { name: "Reconnect / refresh" }),
  ).not.toBeVisible();
});

test("evaluation inventory failure is unavailable, then recovers to an authoritative empty state", async ({
  page,
}) => {
  await page.route("**/api/v1/evaluations", (route) =>
    route.fulfill({
      status: 503,
      json: {
        error: {
          code: "software_failure_probe",
          message: "Evaluation store unavailable.",
          recovery: "Retry refresh.",
        },
      },
    }),
  );
  await page.goto("/");
  await navigateWorkspace(page, "Dataset and Evaluation");
  await expect(
    page
      .getByRole("alert")
      .filter({ hasText: "Evaluation inventory is unavailable" }),
  ).toBeVisible();
  await expect(page.getByText(/No evaluation results exist/)).not.toBeVisible();
  await page.unroute("**/api/v1/evaluations");
  await page
    .getByRole("button", { name: "Refresh workspace", exact: true })
    .click();
  await expect(page.getByText(/No evaluation results exist/)).toBeVisible();
  await expect(page.locator(".readiness-requirements > li")).toHaveCount(6);
  await page.evaluate(() => {
    window.print = () => {
      throw new Error("Software print failure probe");
    };
  });
  await page
    .getByRole("button", {
      name: "Export Dataset Readiness / save PDF",
      exact: true,
    })
    .click();
  await expect(
    page
      .getByRole("alert")
      .filter({ hasText: "Browser printing could not open" }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => document.body.dataset.reportMode),
  ).toBeUndefined();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.emulateMedia({ media: "print" });
  await expect(page.locator(".readiness-requirements > li")).toHaveCount(6);
  await expect(
    page.getByText("Import independent review evidence", { exact: true }),
  ).not.toBeVisible();
  await expect(
    page.getByRole("combobox", { name: "Readiness recording", exact: true }),
  ).not.toBeVisible();
  await expect(page.locator(".readiness-identity")).toContainText("dataset");
  await page.emulateMedia({ media: null });
});
import { navigateWorkspace } from "./navigation";

test("readiness recovers independently from request, access and partial-data failures", async ({
  page,
  request,
}, info) => {
  const summary = await (await request.get("/api/v1/dataset")).json();
  await page.route("**/api/v1/reviews", (route) =>
    route.fulfill({
      status: 503,
      json: {
        error: {
          code: "software_fault",
          message: "Review service unavailable.",
          recovery: "Retry.",
        },
      },
    }),
  );
  await page.goto("/");
  await expect(page.locator(".recording-button")).toHaveCount(
    summary.recordings,
  );
  await navigateWorkspace(page, "Dataset and Evaluation");
  await expect(
    page.getByText(`${summary.recordings} takes`, { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Open Review Workspace", exact: true }),
  ).toBeVisible();
  await page.unroute("**/api/v1/reviews");
  await page.route("**/api/v1/dataset", (route) =>
    route.fulfill({
      status: 503,
      json: {
        error: {
          code: "storage_unavailable",
          message: "Dataset storage unavailable.",
          recovery: "Check storage and retry.",
        },
      },
    }),
  );
  await page
    .getByRole("button", { name: "Refresh workspace", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Retry dataset readiness", exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/last successful request/)).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Open Review Workspace", exact: true }),
  ).toHaveCount(0);
  await page.unroute("**/api/v1/dataset");
  await page
    .getByRole("button", { name: "Retry dataset readiness", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Open Review Workspace", exact: true }),
  ).toBeVisible();
  await page.route("**/api/v1/dataset", (route) =>
    route.fulfill({
      json: {
        ...summary,
        inventory_counts: {
          ...summary.inventory_counts,
          submitted_independent_assertions: undefined,
        },
        review_readiness: [],
        readiness_diagnostic: {
          code: "review_evidence_unavailable",
          message:
            "Recording inventory loaded; review evidence is unavailable.",
          recovery: "Validate and retry.",
        },
      },
    }),
  );
  await page
    .getByRole("button", { name: "Refresh workspace", exact: true })
    .click();
  await expect(
    page.getByText("Unknown assertions", { exact: true }),
  ).toBeVisible();
  await page.setViewportSize({ width: 320, height: 740 });
  await page.screenshot({
    path: info.outputPath("partial-readiness-320.png"),
    fullPage: true,
  });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.unroute("**/api/v1/dataset");
  await page.route("**/api/v1/dataset", (route) =>
    route.fulfill({
      status: 403,
      json: {
        error: {
          code: "handoff_active",
          message: "Restricted during handoff.",
          recovery: "Use the operator workflow.",
        },
      },
    }),
  );
  await page
    .getByRole("button", { name: "Retry dataset readiness", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText(
    "restricted during reviewer handoff",
  );
  await page.unroute("**/api/v1/dataset");
  await page
    .getByRole("button", { name: "Retry dataset readiness", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Open Review Workspace", exact: true }),
  ).toBeVisible();
});
