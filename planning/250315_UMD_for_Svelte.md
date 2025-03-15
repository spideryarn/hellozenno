# DRAFT - Standardizing on UMD for All Svelte Components

I HAVEN'T DECIDED WHETHER TO FOLLOW THIS OR NOT

## 1. Current State

We currently have two approaches for loading Svelte components:

1. **Original Method**: Using ES modules via Vite development server and ES module imports in production
   - Used by components like `MiniLemma`, `MiniSentence`, etc.
   - Relies on the `load_svelte_component` macro in `base_svelte.jinja`

2. **UMD Method**: Using Universal Module Definition with bundled dependencies
   - Used by `FlashcardApp` and `FlashcardLanding`
   - Set with `{% set svelte_umd_mode = True %}` in templates
   - Components accessed via `HzComponents.default.componentname`

## 2. Goals and Benefits

By standardizing on the UMD approach for all components, we aim to achieve:

1. **Consistency**: A single, unified pattern for all Svelte components
2. **Simplicity**: Easier to maintain with one approach rather than two
3. **Reliability**: Eliminate module loading issues and MIME type problems
4. **Reduced External Dependencies**: No reliance on CDN services
5. **Browser Compatibility**: Works in older browsers without modern ES module support

## 3. Implementation Plan

### 3.1 Update Build Configuration

Enhance the current Vite configuration to ensure all Svelte components are bundled properly in UMD format:

```javascript
// vite.config.js updates
export default defineConfig({
  // ... existing config
  build: {
    // ... existing build options
    lib: {
      entry: resolve(__dirname, 'src/entries/index.ts'),
      name: 'HzComponents',
      formats: ['es', 'umd'],
      fileName: (format) => `js/hz-components.${format}.js`
    },
    rollupOptions: {
      // Bundle all dependencies, including Svelte
      external: [],
      output: {
        // No globals needed since we're bundling everything
        globals: {},
        // Ensure assets have consistent names
        assetFileNames: 'assets/[name]-[hash][extname]',
      }
    }
  }
});
```

### 3.2 Update Base Template

Modify `base.jinja` to always include the UMD bundle for all pages:

```jinja
{# base.jinja #}
{% block late_script_imports %}
    <!-- Base scripts -->
    <script src="{{ url_for('static', filename='js/base.js') }}" defer></script>

    <!-- Always include the UMD bundle -->
    <script src="{{ url_for('static', filename='build/js/hz-components.umd.js') }}"></script>
{% endblock late_script_imports %}
```

### 3.3 Create a New UMD Component Loading Macro

Add a new macro to `base_svelte.jinja` specifically for UMD component loading:

```jinja
{% macro load_svelte_umd_component(component_name, props={}, component_id='') %}
  {# Create div with a unique ID for the component to mount to #}
  <div id="{{ component_id if component_id else component_name | lower + '-component' }}" data-svelte-component="{{ component_name }}"></div>
  
  <script>
    document.addEventListener("DOMContentLoaded", function() {
      try {
        // Get component factory from UMD bundle
        const componentName = '{{ component_name | lower }}';
        const componentFactory = HzComponents.default[componentName];
        
        if (typeof componentFactory !== 'function') {
          console.error(`Component ${componentName} not found in HzComponents bundle`);
          return;
        }
        
        // Find target element
        const targetElement = document.getElementById('{{ component_id if component_id else component_name | lower + "-component" }}');
        if (!targetElement) {
          console.error(`Target element #{{ component_id if component_id else component_name | lower + "-component" }} not found`);
          return;
        }
        
        // Mount component
        const props = {{ props | tojson | safe }};
        const component = componentFactory(targetElement, props);
        console.log(`Component ${componentName} mounted successfully`);
      } catch (error) {
        console.error(`Error mounting component {{ component_name }}:`, error);
      }
    });
  </script>
{% endmacro %}
```

### 3.4 Update Template Usage

Convert all templates to use the UMD pattern:

```jinja
{# Example: minilemma_test.jinja #}
{% extends "base.jinja" %}
{% from "base_svelte.jinja" import load_svelte_umd_component %}

{# No longer needed as the UMD bundle is loaded in base.jinja #}
{# {% set vite_entries = ['minilemma'] %} #}

{% block content %}
<div class="container">
    <div class="content-box">
        <h1>MiniLemma Component Test</h1>
        
        <!-- MiniLemma Svelte component mount point -->
        <div id="mini-lemma-test"></div>
        {{ load_svelte_umd_component('MiniLemma', sample_lemma, component_id='mini-lemma-test') }}
        
        <!-- Rest of content -->
    </div>
</div>
{% endblock content %}
```

### 3.5 Transition Strategy

To ensure a smooth transition:

1. **Create a new UMD macro** but keep the existing one for backward compatibility
2. **Convert templates gradually**, starting with test pages
3. **Monitor for issues** in both development and production environments
4. **Update documentation** to reflect the new standard approach
5. **Remove the old approach** once all components are migrated

## 4. Development Workflow Changes

### 4.1 Local Development

In development mode, components will be loaded from the pre-built UMD bundle. To support live reloading:

1. Add a watch task in the frontend package.json:
   ```json
   "scripts": {
     "dev:umd": "vite build --watch --mode development",
     "dev": "vite",
     // other scripts
   }
   ```

2. Update the development script to run both the Vite server and the UMD watch task:
   ```bash
   # scripts/local/run_frontend_dev.sh
   npm run dev & npm run dev:umd
   ```

### 4.2 Testing

Enhanced testing support:

1. Add debug logging to the UMD component loader for easier troubleshooting
2. Create a debug helper function accessible in the global scope
3. Ensure test pages include component debugging tools

## 5. Technical Considerations

### 5.1 Bundle Size

The UMD approach will result in a slightly larger initial download, but it's negligible for an online-only application:

- One larger bundle instead of many small ones
- Svelte runtime included only once
- Browser caching will mitigate the size impact after first load

### 5.2 Backwards Compatibility

During the transition period:

1. Keep both loading mechanisms working in parallel
2. Add comments in templates indicating which approach is being used
3. Update FRONTEND_INFRASTRUCTURE.md to explain both approaches and the transition plan

### 5.3 Code Splitting

If needed later, we can consider:

1. Creating multiple UMD bundles for different sections of the app
2. Using dynamic imports within the UMD bundle for rarely used components

## 6. Documentation Updates

Update `FRONTEND_INFRASTRUCTURE.md` to explain:

1. The standardized UMD approach for all components
2. How to create and use new Svelte components
3. The development workflow with UMD
4. Debugging tips specific to UMD components

## 7. Alternative Approaches Considered

### 7.1 Keep Dual Approaches

We could maintain both ES modules and UMD approaches:
- **Pros**: No migration needed, flexibility to choose per component
- **Cons**: Increased complexity, inconsistent patterns, ongoing maintenance burden

### 7.2 Move Everything to ES Modules

We could fix the ES modules approach instead:
- **Pros**: Better alignment with modern JavaScript, potentially smaller bundles
- **Cons**: More complex loading, browser compatibility issues, external dependencies

### 7.3 Server-Side Rendering with Hydration

We could use Svelte's SSR capabilities with hydration:
- **Pros**: Better performance, no loading flash
- **Cons**: Significantly more complex setup, major architecture change

## 8. Timeline and Milestones

1. **Phase 1** (Week 1):
   - Update build configuration
   - Create new UMD loading macro
   - Convert test pages

2. **Phase 2** (Week 2):
   - Convert all remaining templates
   - Verify in development and production environments
   - Update documentation

3. **Phase 3** (Week 3):
   - Clean up legacy code
   - Remove dual-loading support
   - Final testing and validation

## 9. Conclusion

Standardizing on UMD offers a more consistent, reliable approach for all Svelte components. While it introduces a slight performance tradeoff, the benefits in simplicity, reliability, and maintainability outweigh the costs, especially for an online-only application where simplicity is prioritized over performance optimization.

The UMD approach has already proven successful with the Flashcards2 implementation, demonstrating its reliability in production. By extending this pattern to all components, we'll reduce complexity and ensure a more consistent development and user experience.