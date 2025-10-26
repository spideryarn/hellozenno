import { defineConfig } from '@playwright/test';

// Run e2e tests against an already-running dev server on :5173
export default defineConfig({
  use: {
    baseURL: 'http://localhost:5173',
  },
  testDir: 'e2e',
});


