import type { Page } from "@playwright/test";

export async function navigateWorkspace(page: Page, name: string) {
  await page
    .getByRole("navigation", { name: "Workspace areas", exact: true })
    .waitFor();
  const selector = page.getByRole("combobox", {
    name: "Workspace",
    exact: true,
  });
  if (await selector.isVisible()) await selector.selectOption(name);
  else await page.getByRole("button", { name, exact: true }).click();
}

export async function openHistory(page: Page, jobPrefix: string) {
  await navigateWorkspace(page, "Recording Library");
  await page
    .locator(".library")
    .getByRole("button")
    .filter({ hasText: jobPrefix })
    .click();
}
