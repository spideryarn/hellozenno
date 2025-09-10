# Sentence Component CSS Issues in Production

## Problem Description

The `Sentence.svelte` component renders differently in production compared to local development. Specifically:

1. In **local development**: The sentence text displays properly with correct spacing and styling for word links.
2. In **production**: The sentence text appears with poor formatting:
   - Spacing issues around words
   - Possible incorrect text alignment
   - Word links may not be styled correctly

This affects page URLs like:
- https://hz-app-web.fly.dev/el/sentence/o-agamemnon-etan-o-arkhegos-ton-akhaion-ston-troiko-polemo (broken in production)
- http://localhost:3000/el/sentence/oi-amphoreis-khresimopoiountan-gia-ten-apothekeuse-krasiou-kai-ladiou (works correctly in development)

## Technical Context

### Component Architecture

The Sentence component structure:
- Uses `{@html enhanced_sentence_text}` to render HTML content with interactive word links
- CSS styles target these injected HTML elements via `:global()` selectors
- Component styling is managed by Svelte's scoped CSS

### Development vs. Production Environments

1. **Development Environment**:
   - Components loaded directly via Vite dev server
   - Component URL: `http://localhost:5173/src/entries/sentence.ts`
   - CSS is processed on-the-fly

2. **Production Environment**:
   - Components bundled into a single ES module: `static/build/js/hz-components.es.js`
   - CSS is bundled into `static/build/assets/index-[hash].css`
   - CSS class names are hashed by Svelte for scoping (e.g., `svelte-abnumw`)

### Relevant Files

- `/frontend/src/components/Sentence.svelte` - Main component with styling
- `/frontend/vite.config.js` - Build configuration
- `/frontend/src/entries/sentence.ts` - Entry point
- `/frontend/src/entries/index.ts` - Component registry for production

## Investigation Details

### CSS in Sentence.svelte

Original CSS selectors in the component:
```css
.target-lang-text :global(p) {
  margin: 0;
  padding: 0;
}

.target-lang-text :global(.word-link) {
  color: var(--color-primary);
  text-decoration: none;
  margin: 0 var(--spacing-1);
}

.target-lang-text :global(br) {
  display: block;
  content: "";
  margin-top: 0.5rem;
}
```

### Attempted Fixes

1. **First Approach**: Changed nested selectors to top-level global ones
```css
:global(.target-lang-text p) {
  margin: 0;
  padding: 0;
}

:global(.word-link) {
  color: var(--color-primary);
  text-decoration: none;
  margin: 0 var(--spacing-1);
}

:global(.target-lang-text br) {
  display: block;
  content: "";
  margin-top: 0.5rem;
}
```

2. **Second Approach**: Made selectors completely global with no parent selector
```css
:global(p) {
  margin: 0;
  padding: 0;
}

:global(.word-link) {
  color: var(--color-primary);
  text-decoration: none;
  margin: 0 var(--spacing-1);
}

:global(br) {
  display: block;
  content: "";
  margin-top: 0.5rem;
}
```

### DOM Inspection Results

1. In production, the DOM structure includes:
```html
<div class="target-lang-text svelte-abnumw">
  <p>
    Ο Αγαμέμνων ήταν ο <a target="_blank" href="/el/lemma/αρχηγός" class="word-link">αρχηγός</a> των <a target="_blank" href="/el/lemma/Αχαιός" class="word-link">Αχαιών</a> <a target="_blank" href="/el/lemma/σε τον" class="word-link">στον</a> Τρωικό πόλεμο.
  </p>
</div>
```

2. In production CSS, our generated CSS shows the styles are present:
```css
p{margin:0;padding:0}
.word-link{color:var(--color-primary);text-decoration:none;margin:0 var(--spacing-1)}
br{display:block;content:"";margin-top:.5rem}
```

## Hypotheses

1. **CSS Loading Order**: Production CSS may be loaded in a different order, causing specificity conflicts with base styles.

2. **Caching Issues**: Browser or CDN caching could be preventing updates to CSS from being applied.

3. **DOM Structure Differences**: The actual DOM structure might differ slightly between environments.

4. **Svelte CSS Processing**: Svelte's CSS handling in production might process `:global()` selectors differently than in development.

5. **CSS Variables**: The CSS variables (like `--color-primary`) might not be properly defined in the production context.

6. **Bundle Configuration**: The Vite build configuration might not correctly include or process component styles.

## Conclusions

Despite multiple attempted fixes, the CSS issue in production persists. While our approaches followed Svelte best practices for global styles, something in the production environment is preventing proper style application to the injected HTML content.

The most likely cause is related to CSS specificity, processing order, or how Svelte handles scoped styles in the production bundle. We may need to consider more fundamental changes to how styles are organized in the application.

## Next Steps

1. **Alternative Solution Approaches**:
   - Move styling for injected HTML to a separate, non-scoped CSS file loaded directly in base templates
   - Create a new component that doesn't use `{@html}` but builds the DOM structure programmatically
   - Inject the CSS for these elements directly in the Flask template

2. **Further Investigation**:
   - Inspect CSS cascade and specificity in production using browser dev tools
   - Test with browser cache disabled and hard refresh
   - Compare computed styles between dev and prod environments
   - Test different production build configurations
   - Compare bundle CSS between two recent builds to identify differences

3. **Documentation**:
   - Document this issue for future reference
   - Add notes about potential workarounds for similar components

4. **Project Structure Considerations**:
   - Consider moving global styles used by multiple components to a centralized location
   - Evaluate alternative approaches to rendering HTML content in Svelte components

This issue highlights the challenges of mixing server-generated HTML with Svelte's component model, particularly when styling is involved. A more robust long-term solution may involve rethinking how text with embedded links is handled throughout the application.