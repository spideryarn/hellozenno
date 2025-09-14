import { expect, test } from '@playwright/test';

test('home page has expected h1', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('h1')).toBeVisible();
});

test('generate AI content flow (smoke)', async ({ page }) => {
  const email = process.env.PLAYWRIGHT_TEST_EMAIL;
  const password = process.env.PLAYWRIGHT_TEST_PASSWORD;
  test.skip(!email || !password, 'No test credentials provided');

  await page.goto('/auth');
  await page.fill('input[type="email"]', email!);
  await page.fill('input[type="password"]', password!);
  await page.getByRole('button', { name: /login/i }).click();

  await page.goto('/language/el/sources');
  // Click first row if table exists
  const firstRow = page.locator('table tbody tr').first();
  if (await firstRow.count()) {
    await firstRow.click();
  }

  // Open Add Files → Generate AI Content
  const addFilesBtn = page.getByRole('button').filter({ hasText: /^\+/ });
  await addFilesBtn.click();
  // Use text selector fallback for menu item inside dropdown
  await page.locator('.dropdown-menu >> text=Generate AI Content').click();

  // Submit (leave defaults)
  await page.getByRole('button', { name: /^generate$/i }).click();

  await page.waitForURL(/\/language\/el\/source\/[^/]+\/[^/]+\/text/);
});
