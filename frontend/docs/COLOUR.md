# Colour

This document defines the colour system used across the Hello Zenno frontend. It covers the palette, CSS variables, Bootstrap mappings, and usage guidelines to maintain consistency, readability, and accessibility in our dark theme.

## See also

- [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md) — Overall visual system, components, and CSS structure
- [ACCESSIBILITY.md](./ACCESSIBILITY.md) — Colour contrast, states, and screen reader considerations
- [ICONS_SYMBOLS.md](./ICONS_SYMBOLS.md) — Icon usage and alignment with colour accents
- `../static/css/theme-variables.css` — Canonical definition of colour variables
- `../static/css/theme.css` — Theme-specific rules that apply variables to components

## Principles, key decisions

- Use CSS variables exclusively (`--hz-color-*`); avoid hardcoded hex, rgb, or named colours.
- Optimise for readability on a dark background; ensure sufficient contrast (see Accessibility).
- Keep semantic intent: choose variables by meaning (surface, text, accent), not by hex.
- Map semantic colours to Bootstrap roles (primary, secondary, etc.) centrally in CSS.
- Prefer gentle, pastel accents for highlights; avoid large areas of saturated colour.

## Palette

Defined in `../static/css/theme-variables.css`. Values shown here are the current defaults.

### Core

| Variable | Hex | Description |
|---|---|---|
| `--hz-color-primary-green` | `#669A73` | Primary brand colour (links, primary actions) |
| `--hz-color-primary-green-light` | `#80B890` | Hover/active variant |
| `--hz-color-primary-green-dark` | `#537E5C` | Pressed/focus/strong emphasis |
| `--hz-color-background` | `#0b0b0e` | App background |
| `--hz-color-surface` | `#1e1e1e` | Card and panel surfaces |
| `--hz-color-border` | `#333333` | Subtle borders |
| `--hz-color-text-main` | `#f8f9fa` | Main text |
| `--hz-color-text-secondary` | `#d7dadd` | Secondary text |

### Accents (Pastel)

| Variable | Hex | Typical usage |
|---|---|---|
| `--hz-color-accent-peach` | `#F5B8A8` | Secondary emphasis, badges |
| `--hz-color-accent-lavender` | `#D0C0E8` | Secondary buttons, subtle highlights |
| `--hz-color-accent-sky-blue` | `#A8D8F0` | Informational accents |
| `--hz-color-accent-gold` | `#F8DDA8` | Warnings, soft alerts |

## Semantic mapping

- Surfaces: `--hz-color-background`, `--hz-color-surface`, `--hz-color-border`
- Text: `--hz-color-text-main`, `--hz-color-text-secondary`
- Primary actions: `--hz-color-primary-green` (+ light/dark variants)
- Secondary/emphasis: pastel accents as appropriate to context

## Bootstrap mapping

- Primary: `.btn-primary`, links, and key CTAs map to `--hz-color-primary-green`.
- Secondary: `.btn-secondary` maps to `--hz-color-accent-lavender`.
- Important: When using lavender backgrounds (e.g., `.btn-secondary`, badges), also apply `.text-on-light` to ensure dark text with sufficient contrast.

## Usage guidelines

- Do
  - Use variables from `theme-variables.css` everywhere (Svelte, CSS, inline styles as needed).
  - Keep text on surfaces near-white, and avoid low-contrast pairings.
  - Use accents for small areas and highlights; keep large backgrounds neutral.
- Avoid
  - Hardcoded colours, inline hex/rgb, or mixing random accent colours.
  - Applying accents to large containers unless there is a clear visual reason.

### Examples

```css
.feature-card {
  background: var(--hz-color-surface);
  border: 1px solid var(--hz-color-border);
}

.link-primary {
  color: var(--hz-color-primary-green);
}
```

```svelte
<button class="btn btn-secondary text-on-light">Secondary</button>
```

## Accessibility

- Follow contrast ratios per WCAG 2.1 AA; aim for at least 4.5:1 for body text.
- Use `.text-on-light` when applying light/pastel backgrounds to ensure readable text.
- Validate contrast when introducing new accents or when overlaying text on images.
- See [ACCESSIBILITY.md](./ACCESSIBILITY.md) for full guidance.

## Gotchas

- Missing variable effect usually indicates CSS import order issues; ensure `base.css` imports `theme-variables.css` before `theme.css`.
- Accents on large backgrounds can reduce readability in dark theme; prefer surfaces for containers.
- Custom components must not hardcode colours; create props or use utility classes bound to variables.

## Troubleshooting

- Colour mismatch with Bootstrap component: confirm the theme mapping in `theme.css`.
- New colour not applied: check for caching and verify variables are defined in `theme-variables.css`.
- Contrast warnings: switch to `--hz-color-text-main` on surfaces or apply `.text-on-light` on light backgrounds.


