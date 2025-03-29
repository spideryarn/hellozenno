# CSS rewrite with Bootstrap

## References

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

## Actions

### 1. Setup Project Structure
- [x] Analyze existing CSS structure
  - [x] Identify `static/css/extern/light.css` - Tippy.js styling (to be renamed)
  - [x] Identify `static/css/extern/phosphor/` - Icon library CSS files
  - [x] Note that `base.css` is referenced in `base.jinja` but doesn't exist
  - [x] Identify `frontend/src/styles/global.css` - Contains CSS variables and base styles
- [x] Analyze existing JS resources
  - [x] Identify `static/js/extern/phosphor.js`
  - [x] Identify `static/js/extern/popper.min.js`
  - [x] Identify `static/js/extern/tippy-bundle.umd.min.js`
- [x] Download Bootstrap 5.3 (latest stable) files
  - [x] Download minified CSS and JS files
  - [x] Create `static/css/extern/bootstrap/` directory
  - [x] Create `static/js/extern/bootstrap/` directory
  - [x] Store `bootstrap.min.css` in CSS directory
  - [x] Store `bootstrap.bundle.min.js` in JS directory
- [x] Create custom CSS files
  - [x] Create `static/css/theme.css` for dark mode customization
  - [x] Create `static/css/components.css` for custom component overrides
  - [x] Create `static/css/base.css` as the main CSS file that imports others
- [x] Setup file references
  - [x] Rename `light.css` to `tippy.css`
  - [x] Update references in `base.jinja` and other files

### 2. Implement Core Theme
- [x] Implement dark mode Bootstrap
  - [x] Add `data-bs-theme="dark"` to the HTML element
  - [x] Define dark theme variables in `theme.css`
  - [x] Override Bootstrap variables with our custom colors
- [x] Define typography and spacing
  - [x] Set up font family variables
  - [x] Configure spacing variables for consistent layout
- [x] Create custom component classes
  - [x] Create `.hz-card` for content cards
  - [x] Create `.hz-btn-primary`, `.hz-btn-secondary` for buttons
  - [x] Create `.hz-language-item` for language cards
  - [x] Create `.hz-sentence` for sentence containers
  - [x] Create `.hz-foreign-text` for foreign language styling
  - [x] Create `.hz-metadata` for metadata display

### 3. Update Base Template
- [x] Update `base.jinja` with Bootstrap references
  - [x] Add Bootstrap CSS and JS imports
  - [x] Include custom CSS files
  - [x] Set appropriate meta tags for proper rendering
- [x] Style navigation and breadcrumbs
  - [x] Convert existing nav to Bootstrap navbar
  - [x] Implement responsive navigation behavior
- [x] Style common UI elements
  - [x] Style flash messages using Bootstrap alerts
  - [x] Convert reusable modal to Bootstrap modal
  - [x] Ensure consistent container structure for pages

### 4. Style Pages and Components
- [x] Style Languages List page (`languages.jinja`)
  - [x] Convert `.languages-list` to Bootstrap cards grid
  - [x] Replace inline styles with Bootstrap classes and custom CSS
  - [x] Apply `.hz-language-item` class to language cards
  - [x] Implement hover effects and proper spacing
  - [x] Make layout fully responsive with appropriate breakpoints
- [x] Style Sentence Component (`Sentence.svelte`)
  - [x] Replace `.card` and `.sentence-container` with Bootstrap card styles
  - [x] Update CSS variables to match the theme
  - [x] Style audio player and controls
  - [x] Format text and spacing consistently
  - [x] Update mounting in `sentence.jinja` template
- [x] Style Wordform pages
  - [x] Update `wordform.jinja` with Bootstrap grid and card styling
  - [x] Style sort options with Bootstrap button group
  - [x] Update MiniWordform component with Bootstrap classes
  - [x] Fix TypeScript linter error in MiniWordform component

### 5. Final Testing and Review
- [ ] Test site responsiveness
  - [ ] Verify layout on mobile devices
  - [ ] Test different screen resolutions
  - [ ] Ensure proper spacing on all device sizes
- [ ] Check for FOUC issues
  - [ ] Verify dark theme applies immediately
  - [ ] Check for smooth loading of styled components
- [ ] Final consistency review
  - [ ] Verify all pages follow the same styling pattern
  - [ ] Ensure custom component classes are used consistently
  - [ ] Check for any missed elements or edge cases

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

Final structure:
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
        ├── phosphor.js
        ├── popper.min.js
        ├── tippy-bundle.umd.min.js
        └── other JS files...
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