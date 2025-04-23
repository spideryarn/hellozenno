# UI and Styling

The application uses Bootstrap 5.3.2 for styling, with a custom dark theme. The styling system is organized as follows:

For user experience guidelines, see [USER_EXPERIENCE.md](./USER_EXPERIENCE.md).

## CSS Structure

```
static/css/
├── base.css               # Main CSS file that imports others
├── theme-variables.css    # Theme variables (colors, fonts, etc.)
├── theme.css              # Theme-specific styling
├── components.css         # Component-specific styles
└── extern/
    └── bootstrap/
        └── bootstrap.min.css  # Bootstrap core CSS
```

## Theming

The app uses a dark space-themed design with the following color palette defined in `theme-variables.css`:

### Primary Colors

- Background: Near-black (`#0b0b0e`) - Deep space background
- Card background: Dark gray (`#1e1e1e`) - Slightly lighter for UI elements
- Main font: Near-white (`#f8f9fa`) - Clear, readable text
- Secondary text: Light gray (`#d7dadd`) - For less emphasized content

### Accent Colors

- Mint Green (`#45C187`) - Primary brand color for highlights, buttons, active elements
- Mint Light (`#60D3A0`) - Hover state for mint green elements
- Lilac (`#C6A9F0`) - For secondary accents and special features
- Orange (`#FDBF7E`) - For tertiary accents and alerts
- Sky Blue (`#88C9FF`) - For quaternary accents and information

### UI Element Colors

- Card border: Dark gray (`#333`) - Subtle borders for card elements
- Button hover: Darker mint (`#3d8c42`) - For button hover states
- Shadow: Mint shadow (`rgba(69, 193, 135, 0.25)`) - For depth on mint-colored elements

### Font families

- Main text: Georgia, serif - Warm and readable serif font
- Foreign language text: Times New Roman, serif (italic) - Distinguished style for target language
- Monospace: Menlo, Monaco, Courier New - For code and metadata

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

## Custom CSS Classes

### New Homepage-Specific Classes

- `.hero-section`: For full-width hero areas with background images
- `.nebula-bg`: For sections with the space nebula background
- `.text-mint`: For mint green text highlights
- `.animate-float`: For gentle floating animation (used on logo)
- `.feature-card`: For feature highlight cards with hover effects
- `.feature-item`: For feature list items with icons
- `.getting-started-step`: For step-by-step instruction displays
- `.final-note-card`: For call-out information cards
- `.footer-link`: For footer navigation links

### Standard Classes

- `.hz-language-item`: For language cards
- `.hz-foreign-text`: For foreign language text
- `.hz-source-item`: For source items
- `.hz-sentence-item`: For sentence displays
- `.hz-section-header`: For section headings
- `.hz-btn-primary`: For primary buttons

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

## Button Styling

### Primary Buttons

Primary action buttons use the mint green color with rounded pill shape for the homepage:

```html
<a href="/languages" class="btn btn-primary btn-lg px-5 py-3 rounded-pill">
  Try Hello Zenno
</a>
```

Style properties:
- Background: `#45C187` (Mint Green)
- Hover background: `#60D3A0` (Mint Light)
- Text color: White
- Box shadow: `0 4px 12px rgba(69, 193, 135, 0.25)`
- Border radius: `rounded-pill` for marketing CTAs, `rounded` for app UI

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
   - **Keyboard Shortcuts:** Implement common shortcuts like `Escape` to close and `Enter` (or `Ctrl+Enter` for multi-line inputs) to submit the primary action, attached to the modal content element. Ensure event propagation is stopped (`|stopPropagation`) if necessary.

4. Form elements and focus management:
   - When using autofocus (which is sometimes necessary for a good UX), add a svelte-ignore comment to avoid accessibility warnings
   - Example:
     ```svelte
     <script>
       import { onMount } from 'svelte';
       let input;
       export let autofocus = false;
       
       onMount(() => {
         if (autofocus && input) {
           input.focus();
         }
       });
     </script>
     
     <!-- svelte-ignore a11y_autofocus -->
     <input bind:this={input} />
     ```
   - Prefer making autofocus configurable via props rather than hardcoded
   - Ensure autofocus is only used on the main content area of a page, not in modals or popups

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

4. For mint accent text:

```svelte
<span class="text-mint">hear</span>
```

5. For cards with hover effects:

```svelte
<div class="feature-card">
  <!-- Feature content -->
</div>
```