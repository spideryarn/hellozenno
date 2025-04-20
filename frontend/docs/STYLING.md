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

The app uses a dark theme with a color scheme defined in `theme-variables.css`:
- Background: Near-black (`#121212`)
- Main font: Near-white (`#e9e9e9`)
- Primary: Bright green (`#4CAD53`) - for highlights, buttons, active elements
- Secondary: Complementary orange (`#D97A27`) - for accents, secondary actions

Font families:
- Main text: Georgia, serif
- Foreign language text: Times New Roman, serif (italic)
- Monospace: Menlo, Monaco, Courier New (for code and metadata)

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
- ...

## Icons

The application uses Phosphor icons for a consistent iconography system. 

### Using Phosphor Icons

We use the `phosphor-svelte` package (version 3.0.1) for icons. 

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

### Icon Properties

```svelte
<PencilSimple size={16} weight="bold" />
```

- `size`: Controls the icon size (typically 16px for small icons, 24px for navigation icons)
- `weight`: Icon style variants: "regular" (default), "bold", "fill", "duotone", "thin", "light"

## CSS Classes

Custom CSS classes for consistent styling:
- `.hz-language-item`: For language cards
- `.hz-foreign-text`: For foreign language text
- `.hz-source-item`: For source items
- `.hz-sentence-item`: For sentence displays
- `.hz-section-header`: For section headings
- `.hz-btn-primary`: For primary buttons

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
   - Avoid using `autofocus` attribute as it can be disruptive for screen reader users
   - Instead, use the `use:focusOnMount` action from Svelte or focus elements programmatically
   - Example:
     ```svelte
     <!-- Instead of this -->
     <input autofocus />
     
     <!-- Use this -->
     <script>
       import { onMount } from 'svelte';
       let input;
       onMount(() => input.focus());
     </script>
     <input bind:this={input} />
     ```

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