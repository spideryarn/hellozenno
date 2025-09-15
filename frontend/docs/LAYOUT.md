# Layout

This document describes the frontend layout architecture and conventions in the SvelteKit app. It explains how the root layout works, how pages compose within it, and the patterns for containers, grids, spacing, and width for readable, responsive pages.

## See also

- [FRONTEND_SVELTEKIT_ARCHITECTURE.md](./FRONTEND_SVELTEKIT_ARCHITECTURE.md) — How routing and nested layouts compose in SvelteKit
- [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md) — Theme variables, Bootstrap usage, and component styling
- [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) — Readability guidelines, page scaffolding, and tone
- [ACCESSIBILITY.md](./ACCESSIBILITY.md) — Semantics, contrast, keyboard, and ARIA guidance
- [PAGE_TITLES_SEO.md](./PAGE_TITLES_SEO.md) — Title/meta patterns and SEO rules
- [ICONS_SYMBOLS.md](./ICONS_SYMBOLS.md) — Icon system and navbar icon guidelines
- [ENHANCED_TEXT.md](./ENHANCED_TEXT.md) — Classes for foreign-language text and emphasis
- [DATAGRID.md](./DATAGRID.md) — Patterns for data-dense pages and tables

## Principles, key decisions

- Prefer composition: the root layout provides shell (background, header, footer); each page owns its containers and grid.
- Use Bootstrap grid and utilities; custom CSS should live in theme files and reusable components.
- Enforce readability: constrain text content to a comfortable width, especially on large screens.
- Use theme variables (`--hz-color-*`, fonts, shadows) rather than hardcoded colors or ad-hoc styles.
- Keep the shell stable: header/footer are consistent; nav items are minimal, with Admin shown only when authorised.
- Avoid wrapping the entire app in a fixed container so full-bleed sections remain possible; add containers per page where appropriate.

## Architecture overview

- Root layout files:
  - `../src/routes/+layout.server.ts` — Fetches `profile` and `is_admin` when authenticated
  - `../src/routes/+layout.ts` — Creates browser Supabase client and passes `session`, `user`, `profile`
  - `../src/routes/+layout.svelte` — Sets `supabase` in context, renders shell (Nebula background, header, footer), and `<slot />`
- Background: the entire app is wrapped by `NebulaBackground`, with header/footer placed above it using `z-index`.
- Navigation: header shows `Languages`, `About`, an `Admin` link when `is_admin` is true, and either a profile dropdown (logged in) or a Login button.
- Auth reactivity: the root layout listens for Supabase auth state changes and calls `invalidateAll()` so nested routes refresh.

## Containers, grids, and widths

- Root `main` is not wrapped by a `.container` so pages can choose between full-bleed and constrained layouts.
- Standard content pages should add their own container and a centered column for readability:

```svelte
<section class="py-4">
  <div class="container">
    <div class="row">
      <div class="col-xl-8 col-lg-10 mx-auto">
        <!-- Page content -->
      </div>
    </div>
  </div>
  <!-- Optional secondary sections below -->
</section>
```

- Data-dense views (e.g., tables) may use `.container-fluid` or wider columns, but still prefer consistent spacing (`g-3`, `gy-3`). See [DATAGRID.md](./DATAGRID.md).
- Use Bootstrap breakpoints (`sm`, `md`, `lg`, `xl`, `xxl`) to tailor column widths. Avoid deep grids; keep nesting shallow.
- For hero/marketing sections, full-bleed is fine. Use a container inside to constrain text where needed.

## Header and footer

- Implemented in `../src/routes/+layout.svelte`.
- Header: dark background, logo, primary nav, conditional Admin link, and auth dropdown via `DropdownButton`.
- Footer: dark background, centered links, and tagline. Both are above the nebula background via `position: relative; z-index: 100`.
- To add or reorder navigation links, edit the navbar section in `+layout.svelte`. Keep link text short and avoid overcrowding.

## Spacing and sections

- Use vertical rhythm with Bootstrap utilities: `py-4`/`py-5` for major sections; `mb-3`/`mb-4` for intra-section spacing.
- Prefer sectioned pages using `<section>` with headings (`.hz-section-header`) for scanability.
- Group related content in cards (`.card` or component equivalents) for clarity.

## Full‑bleed and backgrounds

- The nebula background is applied globally by the root layout. Avoid local full-screen background layers that compete with it.
- When a full-bleed band is needed, create a section that spans width and add a container inside for text:

```svelte
<section class="py-5 nebula-bg">
  <div class="container">
    <!-- Headline and content -->
  </div>
  <!-- Optional image or illustration can be full-bleed within this section -->
</section>
```

## Accessibility and SEO

- Use semantic markup and correct heading order. Provide `alt` text for images and labels for interactive elements.
- Set page-specific titles and metadata per [PAGE_TITLES_SEO.md](./PAGE_TITLES_SEO.md). The root layout sets a default title using site constants.

## Gotchas

- The root `main` does not include a `.container`; remember to add one in your page for standard content.
- Maintain contrast by using theme variables; if you use lavender surfaces (`.btn-secondary`), also use `.text-on-light`.
- Z-index: header and footer assume `z-index: 100`. If adding positioned elements, avoid overlapping the navbar/footer.
- Auth reactivity: if a nested layout or page relies on auth state, ensure it declares `depends('supabase:auth')` in its load function.

## Troubleshooting

- Changes not reflected after login/logout: ensure your page or nested layout `load` function uses `depends('supabase:auth')`. The root triggers `invalidateAll()` on auth changes.
- Layout shifts or overflow: check grid nesting and container usage; ensure columns are inside a `.row` and that full-bleed sections don't introduce horizontal scroll.

### Ultra‑wide screens

- Perceived narrowness can happen when a page shifts from `col-12` at medium widths to a fractional column (e.g., `col-xl-5`) at `xl` while still using a capped `.container`. If the companion column is empty, the visible column feels too narrow.
- Pattern: make the primary column full‑width until the secondary content exists, then apply the wider grid (e.g., `class:col-xl-5={cards.length > 0}`). Keep scroll anchors outside grid containers so smooth scroll lands correctly regardless of layout.
