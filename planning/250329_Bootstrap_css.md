# CSS rewrite with Bootstrap

# References

see:
- example Svelte component: `Sentence.svelte` in `sentence.jinja`, served by `sentence_views.py`
- example plain html/Jinja: `languages.jinja` from `languages_list_vw`

## Goals

- Keep things simple and minimal
- Avoid frontend infrastructure complexity, e.g. avoid a preprocessor for CSS, host locally rather than CDN
- Avoid inconsistency between the parts that are Jinja/HTML and the in-page Svelte components
- Aim to create a simple base/core theme and pattern language that we can reuse
- Only/always dark mode
- Use the Bootstrap built-ins where we can, overriding lightly, to keep our CSS minimal
- Use Phosphor for icons - see `static/css/extern/phosphor`
- We're using Tippy.js for tooltips - see `light.css` - we should rename this to `tippy.css`, and/or reuse existing CSS
- Completely avoid Flash of Unstyled Content (FOUC)
- We don't care about backwards compatibility or optimising performance

## Implementation Plan

### Stage 1: Setup Bootstrap Framework (Foundation)
- [ ] Download Bootstrap 5.3 (latest stable) files
  - Get minified CSS and JS files
  - Store in `static/css/extern/bootstrap/` and `static/js/extern/bootstrap/`
- [ ] Create initial dark theme architecture
  - Create `static/css/theme.css` for dark mode customization
  - Create `static/css/components.css` for custom component overrides
- [ ] Update `base.jinja` to include Bootstrap and our custom CSS
  - Replace existing CSS includes with Bootstrap and our custom CSS
  - Add appropriate meta tags for proper rendering

### Stage 2: Core Page Structure & Navigation 
- [ ] Implement dark mode Bootstrap
  - Set `data-bs-theme="dark"` on the HTML element
  - Override Bootstrap variables in `theme.css`
- [ ] Style navigation and breadcrumbs
  - Convert existing nav to Bootstrap navbar
  - Implement responsive behavior
- [ ] Implement container structure for pages
  - Use Bootstrap grid system
  - Create consistent page padding

### Stage 3: Languages List Page
- [ ] Style languages list page (`languages.jinja`)
  - Convert list to Bootstrap cards grid
  - Implement hover effects and proper spacing
- [ ] Implement mobile-responsive layouts
  - Test different screen sizes
  - Ensure proper spacing on mobile

### Stage 4: Sentence Component
- [ ] Style sentence component (`Sentence.svelte`)
  - Apply Bootstrap card styles
  - Style audio controls
  - Format text and spacing
- [ ] Ensure Svelte compatibility
  - Update Svelte component styles to use Bootstrap classes
  - Test component in page context

### Stage 5: Common Components & Final Touches
- [ ] Style the reusable modal
  - Use Bootstrap modal component
  - Ensure proper styling for inputs and buttons
- [ ] Style buttons and form elements
  - Consistent styling for all interactive elements
  - Apply custom colors from our theme
- [ ] Test full site experience
  - Check for FOUC issues
  - Test user flows across pages

## Color Scheme

- Background: Near-black (`#121212`)
- Main font: Near-white (`#e9e9e9`)
- Primary: Bright green (`#4CAD53`) - for highlights, buttons, active elements
- Secondary: Complementary orange (`#D97A27`) - for accents, secondary actions

## Typography

- Primary: Georgia
- Foreign target language: Times New Roman italic
- Metadata: Monospace (Menlo, Monaco, 'Courier New')

## CSS File Structure

```
static/
├── css/
│   ├── extern/
│   │   ├── bootstrap/
│   │   │   └── bootstrap.min.css
│   │   ├── phosphor/
│   │   └── tippy.css (renamed from light.css)
│   ├── theme.css       (variables, colors, base dark theme)
│   ├── components.css  (custom styling for specific components)
│   └── base.css        (main CSS file, imports others)
└── js/
    └── extern/
        ├── bootstrap/
        │   └── bootstrap.bundle.min.js
        └── existing JS files...
```

## Bootstrap Component Usage

Only use these Bootstrap components to keep things minimal:
- Grid system
- Cards
- Buttons
- Nav/Navbar
- Modal
- Forms
- Utilities (spacing, flexbox, etc.)

## Custom Component Classes

Create these custom classes for consistent styling:
- `.hz-card` - Base style for content cards
- `.hz-btn-primary`, `.hz-btn-secondary` - Button styles
- `.hz-language-item` - Individual language card
- `.hz-sentence` - Sentence container
- `.hz-foreign-text` - Foreign language text styling
- `.hz-metadata` - Metadata information display

## Implementation Notes

- Focus first on making the Languages List page (`/lang`) and Sentence page functional
- Avoid rewriting the entire CSS at once; build incrementally by section
- Test thoroughly between changes to avoid UI regressions
- Maintain a consistent look between Jinja templates and Svelte components