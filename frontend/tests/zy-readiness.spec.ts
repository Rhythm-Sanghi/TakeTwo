import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
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
