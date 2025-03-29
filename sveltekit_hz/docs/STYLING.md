# UI and Styling

The application uses Bootstrap 5.3.2 for styling, with a custom dark theme. The styling system is organized as follows:

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

## Component Library

We provide reusable Svelte components to maintain consistent styling:

- `Card.svelte`: For card-based layouts (used in language listings)
- `SourceItem.svelte`: For displaying source items
- `Sentence.svelte`: For displaying sentences with translations

## How to Use

1. Import components directly from `$lib`:

```svelte
<script>
  import { Card, SourceItem } from '$lib';
</script>
```

2. Use Bootstrap classes with our custom styling:

```svelte
<div class="card hz-language-item">
  <!-- Card content -->
</div>
```

3. Use custom CSS classes for consistent styling:
   - `.hz-language-item`: For language cards
   - `.hz-foreign-text`: For foreign language text
   - `.hz-source-item`: For source items 