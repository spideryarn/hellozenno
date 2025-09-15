# LAYOUT

## Goal, context

Document core layout conventions used across the SvelteKit frontend so pages feel consistent, responsive, and readable on all breakpoints. Capture decisions about containers, grids, and width constraints, and point developers to styling guidance for colors/typography.

## References

- Visual Design and Styling — see [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md)
  - Defines theme variables, Bootstrap usage, and component styling patterns
- Sourcefile pages layout wrapper: `frontend/src/lib/components/SourcefileLayout.svelte`
  - Provides header, tabs, and a responsive container pattern that constrains width to 90% on ≥992px
- Learn page (MVP): `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte`
  - Uses the standard container with a local `.learn-container` rule to match 90% width at ≥992px

## Principles, key decisions

- Use Bootstrap container-and-grid as the baseline; prefer `.container` with responsive grid (`.row`/`.col-*`).
- Constrain very wide layouts for readability: on large screens (≥992px), target ~90% page width unless a view explicitly needs full-bleed.
- Keep layout rules local to the page when the pattern is specific to that page; centralize into shared layouts (e.g., `SourcefileLayout.svelte`) where appropriate for families of pages.
- Avoid overriding Bootstrap globally for container sizing; instead, apply scoped classes (e.g., `.learn-container`) or shared layout components to reduce regression risk.

## Stages & actions

- [x] Align Learn page width with sourcefile pages at large breakpoints
  - Added `.learn-container` with `max-width: 90%` at `@media (min-width: 992px)`
  - Ensures consistent readability on high-width displays
- [ ] Consolidate page-specific width rules into a shared layout where feasible
  - Candidate: wrap Learn page content in `SourcefileLayout.svelte` when the header/tabs should be present
  - Acceptance: identical container behavior without duplicating CSS

## Notes

- When introducing new pages, default to `.container` and responsive grid. If the page is part of the sourcefile family, use `SourcefileLayout.svelte` to inherit the standard container and header.
- For any local width constraints, prefer minimal, scoped media queries and reference the design system in `VISUAL_DESIGN_STYLING.md` for colors/typography.


