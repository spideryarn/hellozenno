# Integrating Bulma CSS Framework

This document outlines the plan for integrating the Bulma CSS framework into our Flask + Svelte application.

## Approach: NPM Installation with Vite Bundling

We'll use the NPM approach to install and bundle Bulma with our application, avoiding CDN dependencies and ensuring consistent styling across both Jinja templates and Svelte components.

## Implementation Stages

### Stage 1: Initial Setup and Installation

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
   ```

### Stage 2: First Test with Sentence Component

We'll start by experimenting with the Sentence component to test Bulma integration:

1. Modify `Sentence.svelte` to import Bulma styles:
   ```diff
   <script lang="ts">
     import type { SentenceProps } from '../lib/types';
     import '../styles/global.css';
   + import '../styles/bulma-imports.css';
     import MiniLemma from './MiniLemma.svelte';
     // Rest of the script
   </script>
   ```

2. Convert some basic elements to use Bulma classes:
   - Update the sentence container to use Bulma's card component
   - Use Bulma's button styles
   - Implement Bulma's layout classes

3. Test rendering in both development and production environments

### Stage 3: Jinja Template Integration

1. Update `sentence.jinja` to include Bulma classes for layout structure:
   - Wrap container with Bulma section and container classes
   - Style breadcrumbs using Bulma's breadcrumb component

2. Add consistent styling for outer layout elements

### Stage 4: Global Integration

1. Update our main entry point to include Bulma styles for all components:
   ```js
   // In frontend/src/entries/index.ts
   import '../styles/bulma-imports.css';
   import '../styles/global.css';
   ```

2. Adjust `global.css` to handle potential conflicts with Bulma:
   - Review and adjust CSS variables
   - Mark certain styles as !important if needed
   - Consider namespacing custom styles

3. Update `vite.config.js` to optimize CSS bundling:
   ```js
   // Ensure proper CSS processing
   build: {
     // Existing config...
     rollupOptions: {
       // Existing config...
       output: {
         // Ensure CSS files are correctly processed
         assetFileNames: (assetInfo) => {
           if (assetInfo.name === 'style.css' || assetInfo.name.endsWith('.css')) {
             return 'assets/[name]-[hash][extname]';
           }
           return 'assets/[name]-[hash][extname]';
         }
       }
     }
   }
   ```

### Stage 5: Customization and Theming

1. Create a Sass customization file (optional):
   ```bash
   # First install Sass
   npm install sass
   
   # Create custom Bulma file
   touch frontend/src/styles/custom-bulma.scss
   ```

2. Add customization to match our color scheme:
   ```scss
   @charset "utf-8";
   
   // Customize Bulma variables
   $primary: #2563eb; // Match our primary blue
   $family-serif: Georgia, 'Times New Roman', Times, serif; // Match our font
   
   // Import full Bulma
   @import "bulma/bulma.sass";
   ```

3. Replace `bulma-imports.css` with the compiled Sass file

### Stage 6: Progressive Component Migration

1. Create a prioritized list of components to migrate:
   - Start with common UI elements (buttons, forms, tables)
   - Move to more complex components (modals, cards)
   - Finally update specialized components

2. Apply Bulma classes consistently across all components

3. Maintain a "Bulma Component Guide" showing examples of styled components

## Testing Approach

For each stage:

1. Test in development mode with Vite dev server
2. Build production assets and test in Flask app
3. Verify styling on different browser sizes
4. Check for CSS conflicts or regressions

## Fallback Plan

If we encounter issues with the NPM bundling approach:

1. Download Bulma CSS directly to `/static/css/extern/bulma.min.css`
2. Include via Jinja template with:
   ```html
   <link rel="stylesheet" href="{{ url_for('static', filename='css/extern/bulma.min.css') }}">
   ```

## Initial Experiment: Sentence Component

Let's start with specific changes to `Sentence.svelte`:

```diff
<div class="sentence-page">
-  <div class="card sentence-container">
+  <div class="card">
+    <div class="card-content sentence-container">
    
    <!-- Metadata -->
    {#if metadata}
-      <div class="metadata-section">
+      <div class="metadata-section is-pulled-right">
       <!-- ... -->
      </div>
    {/if}

-    <div class="main-content">
+    <div class="content main-content">
      <!-- ... -->
      
      <!-- Replace button -->
      {#if !sentence.has_audio}
-        <button class="button" on:click={generateAudio} disabled={isGeneratingAudio}>
+        <button class="button is-primary" on:click={generateAudio} disabled={isGeneratingAudio}>
          {isGeneratingAudio ? 'Generating...' : 'Generate audio'}
        </button>
      {/if}
      
+    </div>
    </div>
  </div>
</div>
```

And for `sentence.jinja`:

```diff
{% block content %}
+ <section class="section">
+   <div class="container">
      <!-- Mount point for Svelte component -->
      <div id="sentence-component-container"></div>
      
      <!-- Component loading code -->
      
      {{ load_svelte_component('Sentence', {
          'sentence': sentence,
          'metadata': metadata,
          'enhanced_sentence_text': enhanced_sentence_text
      }, component_id='sentence-component-mount') }}
+   </div>
+ </section>
{% endblock content %}
```

This progressive, staged approach will allow us to gradually integrate Bulma while ensuring compatibility with our existing components.
