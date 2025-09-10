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
- [ ] Analyze existing CSS structure
  - [ ] Identify `static/css/extern/light.css` - Tippy.js styling (to be renamed)
  - [ ] Identify `static/css/extern/phosphor/` - Icon library CSS files
  - [ ] Note that `base.css` is referenced in `base.jinja` but doesn't exist
  - [ ] Identify `frontend/src/styles/global.css` - Contains CSS variables and base styles
- [ ] Analyze existing JS resources
  - [ ] Identify `static/js/extern/phosphor.js`
  - [ ] Identify `static/js/extern/popper.min.js`
  - [ ] Identify `static/js/extern/tippy-bundle.umd.min.js`
- [ ] Download Bootstrap 5.3 (latest stable) files
  - [ ] Download minified CSS and JS files
  - [ ] Create `static/css/extern/bootstrap/` directory
  - [ ] Create `static/js/extern/bootstrap/` directory
  - [ ] Store `bootstrap.min.css` in CSS directory
  - [ ] Store `bootstrap.bundle.min.js` in JS directory
- [ ] Create custom CSS files
  - [ ] Create `static/css/theme.css` for dark mode customization
  - [ ] Create `static/css/components.css` for custom component overrides
  - [ ] Create `static/css/base.css` as the main CSS file that imports others
- [ ] Setup file references
  - [ ] Rename `light.css` to `tippy.css`
  - [ ] Update references in `base.jinja` and other files

### 2. Implement Core Theme
- [ ] Implement dark mode Bootstrap
  - [ ] Add `data-bs-theme="dark"` to the HTML element
  - [ ] Define dark theme variables in `theme.css`
  - [ ] Override Bootstrap variables with our custom colors
- [ ] Define typography and spacing
  - [ ] Set up font family variables
  - [ ] Configure spacing variables for consistent layout
- [ ] Create custom component classes
  - [ ] Create `.hz-card` for content cards
  - [ ] Create `.hz-btn-primary`, `.hz-btn-secondary` for buttons
  - [ ] Create `.hz-language-item` for language cards
  - [ ] Create `.hz-sentence` for sentence containers
  - [ ] Create `.hz-foreign-text` for foreign language styling
  - [ ] Create `.hz-metadata` for metadata display

### 3. Update Base Template
- [ ] Update `base.jinja` with Bootstrap references
  - [ ] Add Bootstrap CSS and JS imports
  - [ ] Include custom CSS files
  - [ ] Set appropriate meta tags for proper rendering
- [ ] Style navigation and breadcrumbs
  - [ ] Convert existing nav to Bootstrap navbar
  - [ ] Implement responsive navigation behavior
- [ ] Style common UI elements
  - [ ] Style flash messages using Bootstrap alerts
  - [ ] Convert reusable modal to Bootstrap modal
  - [ ] Ensure consistent container structure for pages

### 4. Style Pages and Components
- [ ] Style Languages List page (`languages.jinja`)
  - [ ] Convert `.languages-list` to Bootstrap cards grid
  - [ ] Replace inline styles with Bootstrap classes and custom CSS
  - [ ] Apply `.hz-language-item` class to language cards
  - [ ] Implement hover effects and proper spacing
  - [ ] Make layout fully responsive with appropriate breakpoints
- [ ] Style Sentence Component (`Sentence.svelte`)
  - [ ] Replace `.card` and `.sentence-container` with Bootstrap card styles
  - [ ] Update CSS variables to match the theme
  - [ ] Style audio player and controls
  - [ ] Format text and spacing consistently
  - [ ] Update mounting in `sentence.jinja` template
- [ ] Style Wordform pages
  - [ ] Update `wordform.jinja` with Bootstrap grid and card styling
  - [ ] Style sort options with Bootstrap button group
  - [ ] Update MiniWordform component with Bootstrap classes
  - [ ] Fix TypeScript linter error in MiniWordform component

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