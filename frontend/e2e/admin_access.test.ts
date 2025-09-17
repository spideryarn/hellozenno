import { test, expect } from '@playwright/test';

const ADMIN_EMAIL = process.env.PLAYWRIGHT_ADMIN_EMAIL;
const ADMIN_PASSWORD = process.env.PLAYWRIGHT_ADMIN_PASSWORD;
const USER_EMAIL = process.env.PLAYWRIGHT_TEST_EMAIL;
const USER_PASSWORD = process.env.PLAYWRIGHT_TEST_PASSWORD;

async function login(page, email: string, password: string) {
  await page.goto('/auth');
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.getByRole('button', { name: /login/i }).click();
  // Wait for profile dropdown to appear or login link to disappear
  const profileButton = page.getByRole('button', { name: /profile/i });
  const loginLink = page.getByRole('link', { name: /login \/ sign up/i });
  await Promise.race([
    profileButton.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {}),
    loginLink.waitFor({ state: 'detached', timeout: 10000 }).catch(() => {})
  ]);
}

test('admin access: /admin/users allowed', async ({ page }) => {
  test.skip(!ADMIN_EMAIL || !ADMIN_PASSWORD, 'Admin credentials not provided');

  await login(page, ADMIN_EMAIL!, ADMIN_PASSWORD!);
  await page.goto('/admin/users');
  // Confirm we are on the admin users page and not redirected
  await expect(page).toHaveURL(/\/admin\/users$/);
  // Fallback visual cue: look for the Back link present on the page
  await expect(page.getByRole('link', { name: 'Back' })).toBeVisible();
});

test('non-admin access: /admin/users forbidden (redirect to /auth)', async ({ page }) => {
  test.skip(!USER_EMAIL || !USER_PASSWORD, 'Test (non-admin) credentials not provided');

  await login(page, USER_EMAIL!, USER_PASSWORD!);
  await page.goto('/admin/users');
  await expect(page).toHaveURL(/\/auth\?next=\/admin/);
});


