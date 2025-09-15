# Frontend Testing

This guide covers end-to-end (Playwright) and unit/component (Vitest) testing for the SvelteKit frontend.

## Commands

- Run end-to-end tests (Playwright):
  ```bash
  cd frontend
  npm run test:e2e
  ```

- Run unit/component tests (Vitest):
  ```bash
  cd frontend
  npm run test:unit
  ```

- Run both suites:
  ```bash
  cd frontend
  npm test
  ```

## Locations and configs

- E2E tests live in `frontend/e2e/` and use `playwright.config.ts`.
- Unit/component tests colocate with source under `frontend/src/**` using `*.test.ts` files.
- JSDOM and browser shims: `vitest-setup-client.ts`, `vitest.shims.d.ts`.

## Playwright guidance

- Prefer user-centric flows that reflect expected usage.
- Use `page.getByRole`/`getByText` over brittle selectors.
- Keep tests short and independent; reset state between tests.
- Record videos/screenshots only when debugging to keep CI fast.

Common flags:
```bash
npx playwright test --ui
npx playwright test -g "Sourcefile text renders"
```

## Vitest guidance

- Use Testing Library for Svelte (`@testing-library/svelte`).
- Avoid testing internal implementation details; assert visible behavior.
- Mock network calls with `vi.fn()` or lightweight stubs near the component.

Example:
```ts
import { render, screen } from '@testing-library/svelte'
import EnhancedText from '$lib/components/EnhancedText.svelte'

test('renders recognized words', () => {
  render(EnhancedText, {
    text: 'Ο σεισμός κομμάτιασε',
    recognizedWords: [{ word: 'σεισμός', start: 2, end: 8, lemma: 'σεισμός', translations: [] }],
    target_language_code: 'el'
  })
  expect(screen.getByText('σεισμός')).toBeInTheDocument()
})
```

## Troubleshooting

- Port conflicts: stop dev servers before running Playwright, or set a fixed `baseURL`.
- Flaky E2E: add `await page.waitForURL(...)` or expect-based waits; avoid arbitrary timeouts.
- Module resolution: ensure `svelte-kit sync` has been run; `npm run check` helps catch type issues.

## Related docs

- Backend testing: `../../backend/docs/BACKEND_TESTING.md`
- Reference signpost: `../../docs/reference/TESTING.md`

### Frontend testing

- **Unit tests**: Vitest is configured. Run non-interactively so output is piped (avoid watch prompts):

```bash
cd frontend
npm run test:unit -- --run | cat
```

- **All tests (unit + e2e stub)**:
```bash
cd frontend
npm run test | cat
```

- **Why pipe to cat?** Some runners can enter watch/interactive mode. Piping to `cat` ensures the command exits cleanly in scripted or headless environments.

- **Troubleshooting**
  - If you see re-optimization messages from Vite, that’s normal on first run.
  - For DOM-based tests, we use jsdom via `vitest-setup-client.ts`.
  - If Storybook tests appear in the run, they’re executed via the Vitest browser runner and should pass quickly.
