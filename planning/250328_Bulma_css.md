# Integrating Bulma CSS Framework

This document outlines the plan for integrating the Bulma CSS framework into our Flask + Svelte application.

## Approach: NPM Installation with Vite Bundling

We'll use the NPM approach to install and bundle Bulma with our application, avoiding CDN dependencies and ensuring consistent styling across both Jinja templates and Svelte components.

## Implementation Stages

### Stage 1: Initial Setup and Installation ✅

1. Install Bulma via NPM:
   ```bash
   cd frontend
   npm install bulma
   ```

2. Create a CSS imports file for Bulma:
   ```bash
   # Create the file
   touch frontend/src/styles/bulma-imports.css
   ```

3. Add Bulma import to the new file:
   ```css
   /* Import Bulma CSS */
   @import 'bulma/css/bulma.min.css';
   
   /* Font overrides for Bulma */
   :root {
     --font-serif: Georgia, 'Times New Roman', Times, serif;
     --font-mono: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
     --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
   }
   
   /* Typography overrides */
   body, .content, p, .title, .subtitle, h1, h2, h3, h4, h5, h6 {
     font-family: var(--font-serif) !important;
   }
   
   .button, .input, .select, .textarea {
     font-family: var(--font-sans) !important;
   }
   
   code, pre, .has-family-monospace, .metadata {
     font-family: var(--font-mono) !important;
   }
   
   /* Color overrides */
   .is-primary {
     background-color: #2563eb !important;
   }
   
   .has-text-primary {
     color: #2563eb !important;
   }
   ```

### Stage 2: First Test with Sentence Component ✅

We tested Bulma integration with the Sentence component:

1. Modified `Sentence.svelte` to import Bulma styles:
   ```svelte
   <script lang="ts">
     import type { SentenceProps } from '../lib/types';
     import '../styles/global.css';
     import '../styles/bulma-imports.css'; // Import Bulma
     import MiniLemma from './MiniLemma.svelte';
     // Rest of the script
   </script>
   ```

2. Converted elements to use Bulma classes:
   - Updated the sentence container to use Bulma's card component
   - Used Bulma's button styles with proper font classes
   - Implemented Bulma's layout classes for spacing and alignment
   - Added Bulma's utility classes for text formatting

3. Used Bulma font class overrides to maintain our original font styling:
   - Added `has-family-monospace` to elements that should use monospace
   - Preserved our existing font variable usage where needed

### Stage 3: Jinja Template Integration ✅

1. Updated `sentence.jinja` to include Bulma classes for layout structure:
   ```jinja
   {% block breadcrumbs %}
   <nav class="breadcrumb has-arrow-separator" aria-label="breadcrumbs">
     <ul>
       <li><a href="{{ url_for('core_views.languages_list_vw') }}">Languages</a></li>
       <li><a href="{{ url_for('sourcedir_views.sourcedirs_for_language_vw', target_language_code=target_language_code) }}">{{ target_language_name }}</a></li>
       <li><a href="{{ url_for('sentence_views.sentences_list_vw', target_language_code=target_language_code) }}">Sentences</a></li>
       <li class="is-active"><a href="#" aria-current="page">{{ sentence.sentence }}</a></li>
     </ul>
   </nav>
   {% endblock breadcrumbs %}
   
   {% block content %}
   <section class="section">
     <div class="container">
       <!-- Component mount point and loading code -->
       {{ load_svelte_component('Sentence', {
           'sentence': sentence,
           'metadata': metadata,
           'enhanced_sentence_text': enhanced_sentence_text
       }, component_id='sentence-component-mount') }}
     </div>
   </section>
   {% endblock content %}
   ```

### Stage 4: Global Integration ✅

1. Updated our main entry point to include Bulma styles for all components:
   ```js
   // In frontend/src/entries/index.ts
   
   // Import global styles first
   import '../styles/bulma-imports.css';
   import '../styles/global.css';
   
   // Import all component classes
   import MiniLemma from '../components/MiniLemma.svelte';
   // ...
   ```

2. Added font overrides in `bulma-imports.css` to handle potential conflicts.

## Progress Review

We've successfully:

1. Installed Bulma via NPM
2. Created a structure for importing Bulma with our font overrides
3. Updated the Sentence component with Bulma styling
4. Made Bulma globally available via the entry point
5. Preserved our original font styling

Screenshots:
- [Original Sentence Component](screenshots/sentence-bulma.png)
- [Sentence Component with Font Fixes](screenshots/sentence-bulma-with-fonts.png)

## Next Steps: Component Migration

### Remaining Components to Update

For each component below, follow these steps:
1. Update the component with Bulma classes
2. Take a screenshot with `cursor-tools browser` to verify appearance
3. Address any styling issues before moving to the next component

#### 1. MiniLemma Component

```bash
# Update MiniLemma component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/lang/el/lemma/όμηρος" --screenshot=screenshots/minilemma-bulma.png
```

#### 2. MiniSentence Component

```bash
# Update MiniSentence component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/lang/el/sentences" --screenshot=screenshots/minisentence-bulma.png
```

#### 3. MiniWordform Component

```bash
# Update MiniWordform component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/lang/el/lemma/όμηρος" --screenshot=screenshots/miniwordform-bulma.png
```

#### 4. MiniWordformList Component

```bash
# Update MiniWordformList component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/lang/el/wordform/ομήρους" --screenshot=screenshots/miniwordformlist-bulma.png
```

#### 5. MiniPhrase Component

```bash
# Update MiniPhrase component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/lang/el/phrase/search" --screenshot=screenshots/miniphrase-bulma.png
```

#### 6. FlashcardApp Component

```bash
# Update FlashcardApp component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/flashcards" --screenshot=screenshots/flashcardapp-bulma.png
```

#### 7. FlashcardLanding Component

```bash
# Update FlashcardLanding component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/flashcards/landing" --screenshot=screenshots/flashcardlanding-bulma.png
```

#### 8. AuthPage Component

```bash
# Update AuthPage component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/auth" --screenshot=screenshots/authpage-bulma.png
```

#### 9. UserStatus Component

```bash
# Update UserStatus component with Bulma
# After updating, take a screenshot
cursor-tools browser open "http://localhost:3000/" --screenshot=screenshots/userstatus-bulma.png
```

### Testing in Production Mode

Before deploying to production, we need to thoroughly test with the production build:

```bash
# Build the frontend for production
cd frontend
npm run build

# Test with production frontend assets
cd ..
source .env.local && ./scripts/local/run_flask.sh --prod-frontend
```

After starting the Flask server with production assets:

```bash
# Take screenshots of key pages with production assets
cursor-tools browser open "http://localhost:3000/lang/el/sentence/oi-tromokrates-kratoun-deka-omerous" --screenshot=screenshots/sentence-prod-bulma.png
cursor-tools browser open "http://localhost:3000/flashcards" --screenshot=screenshots/flashcards-prod-bulma.png
cursor-tools browser open "http://localhost:3000/auth" --screenshot=screenshots/auth-prod-bulma.png
```

Check for:
1. Correct loading of Bulma styles
2. Proper font rendering
3. Layout consistency between dev and prod
4. No JavaScript errors in the console
5. Responsive behavior on different screen sizes

### Final Deployment Checklist

Before merging to main:
- [ ] All components updated with Bulma classes
- [ ] All component screenshots reviewed
- [ ] Production build tested successfully
- [ ] No CSS conflicts or rendering issues
- [ ] Performance impact assessed (CSS bundle size)
- [ ] Consistent styling across all pages

## Customization and Future Improvements

For future development, consider:

1. Creating a complete Sass customization file for deeper Bulma customization
2. Implementing a theming system with CSS variables
3. Setting up a component library showcasing Bulma patterns
4. Adding a CSS purging step to reduce bundle size in production

## Fallback Plan

If issues arise in production:

1. Download Bulma CSS directly to `/static/css/extern/bulma.min.css`
2. Include via Jinja template with:
   ```html
   <link rel="stylesheet" href="{{ url_for('static', filename='css/extern/bulma.min.css') }}">
   ```
