import { test, expect } from '@playwright/test';

async function loginIfNeeded(page) {
  const email = process.env.PLAYWRIGHT_TEST_EMAIL;
  const password = process.env.PLAYWRIGHT_TEST_PASSWORD;
  if (!email || !password) return; // allow anonymous run

  await page.goto('/auth');
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.getByRole('button', { name: /login/i }).click();
  // Consider login done when profile button shows or login link disappears
  const profileButton = page.getByRole('button', { name: /profile/i });
  const loginLink = page.getByRole('link', { name: /login \/ sign up/i });
  await Promise.race([
    profileButton.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {}),
    loginLink.waitFor({ state: 'detached', timeout: 10000 }).catch(() => {})
  ]);
}

// Minimal smoke that the Learn page renders and can start practice
test('Learn flow: renders summary and starts practice', async ({ page }) => {
  await loginIfNeeded(page);

  // Navigate directly to a known Learn URL provided by the user
  await page.goto('/language/el/source/251013/1000015419-word-matching-jpg/learn');

  // Expect the Priority words card to appear
  await expect(page.getByRole('heading', { name: /priority words/i })).toBeVisible({ timeout: 30000 });

  // Wait for summary to load or show warning
  const loadingLocator = page.locator('text=Loading…');
  await loadingLocator.waitFor({ state: 'detached', timeout: 30000 }).catch(() => {});

  // If there are lemmas, the Start practice button should be enabled once not preparing
  const startButton = page.getByRole('button', { name: /start practice/i });
  if (await startButton.count()) {
    // If the button is disabled due to preparing, wait briefly then proceed
    if (await startButton.isDisabled()) {
      await page.waitForTimeout(1500);
    }
    // Click Start practice (or rely on pre-prepared deck)
    await startButton.click({ timeout: 30000 }).catch(() => {});
  }

  // After starting (or if prepared deck loads), the Practice card should appear
  await expect(page.getByRole('heading', { name: /practice/i })).toBeVisible({ timeout: 30000 });

  // Reveal sentence
  const showSentence = page.getByRole('button', { name: /show sentence/i });
  await showSentence.click({ timeout: 10000 }).catch(() => {});

  // Reveal translation
  const showTranslation = page.getByRole('button', { name: /show translation/i });
  await showTranslation.click({ timeout: 10000 }).catch(() => {});

  // Next card button should exist
  await expect(page.getByRole('button', { name: /next card/i })).toBeVisible();
});


