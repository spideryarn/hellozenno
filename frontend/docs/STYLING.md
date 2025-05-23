# UI and Styling

The application uses Bootstrap 5.3.2 for styling, with a custom dark theme. The styling system is organized as follows:

For user experience guidelines, see [USER_EXPERIENCE.md](./USER_EXPERIENCE.md).

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

## Page Titles

Page titles should follow a consistent structure for better SEO and user experience:

### Title Structure Patterns

- **Language-specific pages**: `[Specific Content] | [Page Type] | [Language Name] | [Site Name]`
  - Example: `καλημέρα | Lemma | Greek | Hello Zenno`
  - Example: `Sources | Greek | Hello Zenno`

- **General pages**: `[Page Name] | [Site Name]`
  - Example: `Languages | Hello Zenno`
  - Example: `FAQ | Hello Zenno`

- **Home page**: `[Site Name] - [Tagline]`
  - Example: `Hello Zenno - AI-powered dictionary & listening practice`

### Implementation Guidelines

- Use the constants `SITE_NAME` and `TAGLINE` from `frontend/src/lib/config.ts` for consistency
- Long content titles (like sentences) should be truncated using the `truncate()` utility function
- Set titles within a `<svelte:head>` tag in your component
- Title information should be passed from server to client components as needed
- URL trailing slashes are set to `never` so canonical URLs don't have trailing slashes

## Icons

The application uses Phosphor icons for a consistent iconography system. 

### Using Phosphor Icons

We use the `phosphor-svelte` package (version 3.0.1) for icons. The "fill" weight is preferred for homepage and marketing materials to create a more substantial, friendly look.

**Important Note for Svelte 5**: For best compatibility with Svelte 5, import icons using the path import syntax rather than named imports:

```svelte
<!-- RECOMMENDED: Use direct path imports like this -->
import PencilSimple from 'phosphor-svelte/lib/PencilSimple';

<!-- AVOID: Named imports can cause issues with Svelte 5 -->
import { PencilSimple } from 'phosphor-svelte';
```

Common icons used throughout the application:
- `PencilSimple`: For edit operations
- `Trash`: For delete operations
- `Download`: For download actions
- `FolderOpen`: For folder/directory operations
- `ChevronUp`/`ChevronDown`: For expand/collapse UI elements
- `BookOpen`: For dictionary/reading features
- `MagnifyingGlass`: For search functions
- `Translate`: For translation features
- `Globe`: For language selection
- `SpeakerHigh`: For audio playback
- `BrainCircuit`: For AI-powered features
- `Lightbulb`: For tips and insights

### Icon Properties

```svelte
<PencilSimple size={16} weight="bold" />
```

- `size`: Controls the icon size (typically 16px for small icons, 24px for navigation icons)
- `weight`: Icon style variants: "regular" (default), "bold", "fill", "duotone", "thin", "light"

For icon usage in buttons with tooltips and accessibility best practices, see [USER_EXPERIENCE.md](./USER_EXPERIENCE.md#icons-and-buttons).

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

## Animation Guidelines

Use subtle animations to enhance user experience without being distracting:

- `.animate-float`: 3-second gentle floating animation (for logo and key elements)
- Card hover effects: Small scale and shadow changes on hover
- Button hover effects: Color change, slight translation, and shadow enlargement
- Transition durations: 0.2s-0.3s for most UI elements

## Accessibility Guidelines

1. Elements with event handlers:
   - Add appropriate ARIA roles to non-interactive elements that have event handlers
   - Example: `<div role="dialog" on:keydown={handler}>`

2. Close buttons and icon-only buttons:
   - Always add an aria-label to buttons without visible text
   - Example: `<button class="btn-close" aria-label="Close"></button>`

3. Modal dialogs:
   - Use `role="dialog"` on the modal container
   - Associate the modal with its title using `aria-labelledby`
   - Example: 
     ```svelte
     <div role="dialog" aria-labelledby="modal-title">
       <h5 id="modal-title">Modal Title</h5>
     </div>
     ```
   - For modal keyboard shortcuts and user interaction patterns, see [USER_EXPERIENCE.md](./USER_EXPERIENCE.md#modal-dialogs).

4. Form elements and focus management:
   - When using autofocus, add a svelte-ignore comment to avoid accessibility warnings
   - Prefer making autofocus configurable via props rather than hardcoded
   - Ensure autofocus is only used on the main content area of a page, not in modals or popups
   - For implementation patterns and best practices for autofocus, see [USER_EXPERIENCE.md](./USER_EXPERIENCE.md#input-focus)

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