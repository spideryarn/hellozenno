# Visual Design and Styling

This document covers the visual design system, theming, and core styling patterns for the Hello Zenno application. The application uses Bootstrap 5.3.2 for styling with a custom dark theme.

## Related Documentation

- [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) - User experience guidelines
- [ICONS_SYMBOLS.md](./ICONS_SYMBOLS.md) - Icon system and usage
- [ANIMATION.md](./ANIMATION.md) - Animation patterns and guidelines
- [ACCESSIBILITY.md](./ACCESSIBILITY.md) - Accessibility requirements
- [PAGE_TITLES_SEO.md](./PAGE_TITLES_SEO.md) - Page titles and SEO best practices

## CSS Structure

```
static/css/
├── base.css               # Main CSS file that imports others
├── theme-variables.css    # Theme variables (colors, fonts, etc.)
├── theme.css              # Theme-specific styling
├── components.css         # Component-specific styles (use sparingly)
└── extern/
    └── bootstrap/
        └── bootstrap.min.css  # Bootstrap core CSS
```

## Theming

The app uses a dark theme with a "friendly elegant pastel" color palette defined in `theme-variables.css`. Colours are defined using CSS variables prefixed with `--hz-color-`.

**Important:** Always use the defined `--hz-color-*` variables from [`theme-variables.css`](../static/css/theme-variables.css) for styling. Avoid using hardcoded hex codes, RGB values, or named colours (like `white`, `black`, `green`) directly in component styles or other CSS files. This ensures consistency and maintainability.

### Core Palette

| Variable Name                   | Hex       | Description                       |
|---------------------------------|-----------|-----------------------------------|
| `--hz-color-primary-green`        | `#669A73` | Primary Brand Green (Logo)      |
| `--hz-color-primary-green-light`  | `#80B890` | Lighter Green (Hover/Link Hover)|
| `--hz-color-primary-green-dark`   | `#537E5C` | Darker Green (Active/Focus)     |
| `--hz-color-background`         | `#0b0b0e` | Near-black Background (`body`)  |
| `--hz-color-surface`            | `#1e1e1e` | Dark Gray Surface (Cards)       |
| `--hz-color-border`             | `#333333` | Subtle Border (Cards)           |
| `--hz-color-text-main`          | `#f8f9fa` | Near-white Main Text            |
| `--hz-color-text-secondary`     | `#d7dadd` | Light Gray Secondary Text       |

### Accent Palette (Pastel)

| Variable Name                   | Hex       | Description                       |
|---------------------------------|-----------|-----------------------------------|
| `--hz-color-accent-peach`       | `#F5B8A8` | Soft Peach Accent (Secondary)   |
| `--hz-color-accent-lavender`    | `#D0C0E8` | Gentle Lavender Accent (Tertiary)|
| `--hz-color-accent-sky-blue`    | `#A8D8F0` | Muted Sky Blue Accent (Info)    |
| `--hz-color-accent-gold`        | `#F8DDA8` | Soft Gold Accent (Alert/Warning)|

**Note:** When using lavender (`--hz-color-accent-lavender`) as a background color (e.g., in buttons or badges), use the `.text-on-light` class for consistent dark text styling. This ensures proper contrast and consistent appearance across UI elements.

### UI Effects

- Shadow (Primary): `var(--hz-shadow-primary-green)` - `0 4px 12px rgba(102, 154, 115, 0.25)`
- Shadow (Primary Large): `var(--hz-shadow-primary-green-lg)` - `0 6px 16px rgba(102, 154, 115, 0.35)`

### Font families

Defined as CSS variables:
- Main text (`--hz-font-main`): Georgia, serif - Warm and readable serif font
- Foreign language text (`--hz-font-foreign`): Times New Roman, serif - Used with `font-style: italic` via `.hz-foreign-text` class
- Monospace (`--hz-font-monospace`): Menlo, Monaco, Courier New - For code and metadata

## Component Library

We provide reusable Svelte components to maintain consistent styling:

- `Card.svelte`: For card-based layouts with title, subtitle, and optional link
- `SourceItem.svelte`: For displaying source items
- `Sentence.svelte`: For displaying sentences with translations
- `WordformCard.svelte`: For displaying word forms
- `LemmaCard.svelte`: For displaying lemmas
- `PhraseCard.svelte`: For displaying phrases
- `SentenceCard.svelte`: For displaying sentence cards
- `MetadataCard.svelte`: For displaying metadata information
- `CollapsibleHeader.svelte`: Expandable header component with toggle functionality
- `LoadingSpinner.svelte`: For displaying a loading indicator
- `LightboxImage.svelte`: For displaying images that can be clicked to view in a fullscreen lightbox overlay
- `DropdownButton.svelte`: Reusable dropdown menu component with tooltip support and click-outside behavior

## Custom CSS Classes

### New Homepage-Specific Classes

- `.hero-section`: For full-width hero areas with background images
- `.nebula-bg`: For sections with the space nebula background
- `.text-primary-green`: For primary green text highlights (replaces `.text-mint`)
- `.animate-float`: For gentle floating animation (used on logo)
- `.feature-card`: For feature highlight cards with hover effects
- `.feature-item`: For feature list items with icons
- `.getting-started-step`: For step-by-step instruction displays
- `.final-note-card`: For call-out information cards
- `.footer-link`: For footer navigation links

### Standard Classes

- `.hz-language-item`: For language cards
- `.hz-foreign-text`: For foreign language text (uses `var(--hz-font-foreign)` and `italic`)
- `.hz-source-item`: For source items
- `.hz-sentence-item`: For sentence displays
- `.hz-section-header`: For section headings
- `.hz-btn-primary`: For primary buttons (uses `var(--hz-color-primary-green)`)

## Page Titles and SEO

For page title structure, meta tags, and SEO best practices, see [PAGE_TITLES_SEO.md](./PAGE_TITLES_SEO.md).

## Icons and Symbols

For the Phosphor icon system, usage guidelines, and symbol standards, see [ICONS_SYMBOLS.md](./ICONS_SYMBOLS.md).

## Button Styling

### Primary Buttons

Primary action buttons use the primary green color. Rounded pill shape is often used for marketing calls-to-action.

```html
<a href="/languages" class="btn btn-primary btn-lg px-5 py-3 rounded-pill">
  Try Hello Zenno
</a>
```

Style properties (defined in `theme.css` using variables):
- Background: `var(--hz-color-primary-green)`
- Hover background: `var(--hz-color-primary-green-light)`
- Text color: White (`#fff` generally, ensure contrast)
- Box shadow on hover: `var(--hz-shadow-primary-green-lg)`
- Border radius: `rounded-pill` for marketing CTAs, standard Bootstrap `rounded` for general app UI

### Secondary Buttons

Secondary buttons use the lavender accent color (`--hz-color-accent-lavender`) via the standard Bootstrap `.btn-secondary` class (which is mapped in `theme-variables.css`).

```html
<!-- Always use the text-on-light class with btn-secondary -->
<button class="btn btn-secondary text-on-light">
  Secondary Button
</button>
```

Style properties:
- Background: `var(--hz-color-accent-lavender)` 
- Text color: Dark (`#212529`) using `.text-on-light` class
- Hover: Slightly darker lavender with dark text

## Static Assets

### Images & Icons

The application's static images are organized in the following structure:

```
static/
├── favicon.ico, favicon.png, site.webmanifest   # favicons etc
├── img/
│   ├── logo.png
│   ├── email_contact_envelope.png               # Contact icon
│   ├── extern/                                  # External/third-party images
│   └── marketing/                               # for homepage, about, hero images, etc
└── js/, css/                                    # Other static assets
```

When referencing images in components, always use the full path from the static directory:

```svelte
<img src="/img/logo.png" alt="Hello Zenno" />
```

For new images, follow these guidelines:
- Store application-wide images like the logo in `/static/img/`
- Place feature-specific images in appropriate subdirectories
- Use external logos etc in `/static/img/extern/`
- see also `phosphor-svelte`

## Animations

For animation patterns, transitions, and performance guidelines, see [ANIMATION.md](./ANIMATION.md).

## Accessibility

For accessibility requirements, ARIA attributes, and screen reader support, see [ACCESSIBILITY.md](./ACCESSIBILITY.md).

## How to Use

1. Import components directly from `$lib`:

```svelte
<script>
  import { Card, SourceItem, Sentence } from '$lib';
</script>
```

2. Use Bootstrap classes with our custom styling:

```svelte
<div class="card hz-language-item">
  <!-- Card content -->
</div>
```

3. For foreign language text:

```svelte
<span class="hz-foreign-text">Γειά σου κόσμε</span>
```

4. For primary accent text:

```svelte
<span class="text-primary-green">highlighted text</span>
```

5. For cards with hover effects:

```svelte
<div class="feature-card">
  <!-- Feature content -->
</div>
```

6. For lightbox images:

```svelte
<script>
  import LightboxImage from '$lib/components/LightboxImage.svelte';
</script>

<!-- Basic usage - clicking opens fullscreen lightbox -->
<LightboxImage 
  src="/path/to/image.png" 
  alt="Descriptive alt text" 
  className="feature-img" />
```

**Important Note**: The LightboxImage component should only be used for screenshots and detailed images where it's important for users to see the full-size version. It works best for non-clickable images - if you need the image to be a link, use a regular `<a>` tag with an `<img>` instead.

7. For dropdown menus:

```svelte
<script>
  import DropdownButton from '$lib/components/DropdownButton.svelte';
  // Import Phosphor icon if needed
  import User from 'phosphor-svelte/lib/User';
  
  // Create your items array
  const dropdownItems = [
    { type: 'header', text: 'Menu Title' },
    { type: 'link', text: 'Profile', href: '/profile' },
    { type: 'divider' },
    { type: 'button', text: 'Logout', onClick: handleLogout }
  ];
  
  let isOpen = false;
</script>

<!-- Basic usage -->
<DropdownButton 
  buttonText="Menu" 
  buttonClass="btn btn-sm btn-secondary"
  tooltipText="Optional button tooltip"
  bind:isOpen={isOpen}
  items={dropdownItems}
/>

<!-- With Phosphor icon -->
<DropdownButton 
  buttonText="Profile" 
  buttonSvelteContent={User}
  buttonClass="btn btn-sm btn-secondary"
  tooltipText="User profile menu"
  bind:isOpen={isOpen}
  items={dropdownItems}
/>
```

**Item Types Supported**:
- `header`: Display a non-interactive header text
- `link`: Standard link with href
- `button`: Clickable button with onClick handler
- `divider`: Horizontal divider line