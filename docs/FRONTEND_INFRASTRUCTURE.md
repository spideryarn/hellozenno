# Frontend Infrastructure

see `docs/FRONTEND_TESTING.md`

This document describes the frontend infrastructure for Hello Zenno, including the tools, build process, and development workflow. see `250302_Vite_Svelte_Tailwind_plan.md` (though we've decided to ditch Tailwind)

We combine Svelte & TypeScript with our existing Python Flask application for incremental adoption of modern technologies while maintaining simple deployment.

## Tools & Technologies

- **Flask + Jinja** | Server-side rendering and routing
- **Vite** | Development server and build tool with HMR
- **Svelte** | Reactive component framework
- **TypeScript** | Type-safe JavaScript
- **Base CSS** | Custom styling framework
- **Supabase JS** | Client for database interactions


## Project Structure

```
/
├── frontend/                  # Frontend source code
│   ├── src/
│   │   ├── components/        # Svelte components
│   │   ├── entries/           # Entry points for different pages
│   │   ├── lib/               # Shared TypeScript utilities
│   │   └── styles/            # CSS styles
│   ├── vite.config.js         # Vite configuration
│   ├── tsconfig.json          # TypeScript configuration
│   └── package.json           # Frontend dependencies
├── static/
│   └── build/                 # Output directory for built assets
└── templates/                 # Jinja templates
```

## Development & Deployment

### Development
1. Set `FLASK_PORT` environment variable (e.g., 5000)
2. Run Flask (assume the user has already done this): `source .env.local && ./scripts/local/run_flask.sh`
3. Run Vite (assume the user has already done this): `source .env.local && ./scripts/local/run_frontend_dev.sh`
4. Visit `http://localhost:$FLASK_PORT`

Flask serves templates/API endpoints while Vite handles assets with HMR.

### Build & Deploy
- Build: `./scripts/prod/build-frontend.sh`
- Vite compiles, processes, and outputs to `static/build`
- `deploy.sh` runs the build script before deployment

## Integration & CSS

- Components mount to specific DOM elements
- Extend from `base.jinja` for templates
- For JS functionality: `{% set vite_entries = ['your-component'] %}`

## Troubleshooting

- **Missing Assets**: Check Vite output directory (`static/build`)
- **TypeScript Errors**: Run `npm run check` in frontend directory
- **Styling Conflicts**: Check `base.css` before adding new styles
- **Environment Variables**: Set `FLASK_PORT` before running dev scripts (see `.env.local`)
- **Module Loading Issues**: For components with loading issues, consider using the UMD pattern (see flashcards2 implementation)
- **Fix the root cause** - if there is a problem, we should fix it, rather than applying a bandaid or just replacing with a fallback (e.g. to hard-coded HTML)
- **Avoid CDN dependencies** - All JavaScript libraries should be bundled or stored locally in `/static/js/extern/` to prevent reliance on external services

## Creating New Svelte Components

### Quick Steps
1. **Component File** (`frontend/src/components/YourComponent.svelte`)
   ```typescript
   <script lang="ts">
     export let myProp: string;
   </script>
   <div><!-- Template HTML --></div>
   <style>/* Scoped styles */</style>
   ```

2. **Entry Point** (`frontend/src/entries/yourcomponent.ts`)
   ```typescript
   import YourComponent from '../components/YourComponent.svelte';
   export { YourComponent };
   export default function(target: HTMLElement, props: any) {
     return new YourComponent({ target, props });
   }
   ```

3. **Register Component** in the central registry (`frontend/src/entries/index.ts`)
   ```typescript
   // Import the new component
   import YourComponent from '../components/YourComponent.svelte';
   
   // Add to exports
   export {
     // existing components...
     YourComponent
   };
   
   // Add to component registry
   const components = {
     // existing components...
     yourcomponent: (target: HTMLElement, props: any) => new YourComponent({ target, props })
   };
   ```

4. **Template Integration**
   ```jinja
   {% extends "base.jinja" %}
   {% from "base_svelte.jinja" import load_svelte_component %}
   {% set vite_entries = ['yourcomponent'] %}
   
   {% block content %}
     <div id="your-component-1"></div>
     {{ load_svelte_component('YourComponent', {
         'prop1': value1
     }, component_id='your-component-1') }}
   {% endblock %}
   ```

> **IMPORTANT:** After creating a new component, make sure to add it to the central registry in `index.ts`. This is required for components to work in the production build.

### Best Practices & Gotchas
- Use TypeScript for props and conditional rendering for optional props
- Keep components focused with scoped styles
- Entry filename must match vite_entries value (e.g., 'mycomponent' → 'mycomponent.ts') - no '-entry' suffix is needed
- Always use an array for vite_entries: `{% set vite_entries = ['componentname'] %}`
- Use unique IDs for multiple component instances
- Test in both development and production builds

## Debugging Svelte Components

When working with Svelte components, follow these best practices to ensure smooth integration and easier debugging:

### File Naming Convention
- IMPORTANT: Name entry files WITHOUT the "-entry" suffix: `minilemma.ts` (not `minilemma-entry.ts`)
- Make sure your vite_entries value matches the base name: `{% set vite_entries = ['minilemma'] %}`
- In vite.config.js, define entries with the same base name: `'minilemma': resolve(__dirname, 'src/entries/minilemma.ts')`
- Component naming should follow PascalCase: `MiniLemma.svelte`
- Consistency between filename, entry point name, and import is critical

### Component Development Workflow
1. Start with a minimal working component before adding complexity
2. Create both the component and entry files
3. Create a dedicated test route/page for the component
4. Add debugging tools to the test page
5. Test the component with the simplest possible props before adding complexity

### Debugging Techniques
- Add debug info to your test template:
  ```html
  <button onclick="debugSvelte()">Run Debug Check</button>
  <div id="debug-output"></div>
  
  <script>
  function debugSvelte() {
      const output = document.getElementById('debug-output');
      const mountPoint = document.getElementById('your-component-id');
      
      let debugInfo = '';
      
      // Check mount point
      debugInfo += `Mount point exists: ${mountPoint !== null}\n`;
      if (mountPoint) {
          debugInfo += `Mount point HTML: ${mountPoint.outerHTML}\n`;
          debugInfo += `Mount point children: ${mountPoint.children.length}\n`;
      }
      
      // Check for Svelte-generated elements
      const svelteElements = document.querySelectorAll('.your-component-class');
      debugInfo += `\nElements with component class: ${svelteElements.length}\n`;
      
      output.textContent = debugInfo;
  }
  </script>
  ```

- Create a "non-Svelte" HTML version of your component for comparison
- Monitor console logs for import and mounting errors
- Set breakpoints in your browser's dev tools
- Check network requests to ensure Vite server is accessible

### Common Issues and Solutions
- **Component not rendering**: Verify correct entry file naming and vite_entries value
- **Import errors**: 
  - Check that the Vite server is running on the correct port
  - Ensure entry file names don't have the "-entry" suffix (file should be `minisentence.ts`, not `minisentence-entry.ts`)
  - Verify that `vite_entries` in templates match the entry file names (without "-entry" suffix)
  - Check vite.config.js to ensure the entries object uses the same key names as in templates
  - After making changes to entry file names, restart the Vite development server
- **Module Loading / MIME Type issues**: 
  - If facing persistent issues with module loading, consider using the UMD pattern
  - Set `{% set svelte_umd_mode = True %}` in your template
  - Access components via `HzComponents.default.componentname` 
  - See flashcards2 implementation for details
- **Props not working**: Verify correct prop types and default values
- **Styling issues**: Check for CSS conflicts with global styles
- **Multiple instances**: Ensure unique component IDs when mounting multiple instances
- **Performance problems**: Keep components focused and avoid expensive operations

### Enhancing Component Loading
Consider enhancing the `base_svelte.jinja` template with better error handling and debugging:

```jinja
{% macro load_svelte_component(component_name, props={}, component_id='') %}
  <div id="{{ component_id if component_id else component_name | lower + '-component' }}" data-svelte-component="{{ component_name }}"></div>
  {% if not config.IS_PRODUCTION %}
    {# Development mode - use Vite dev server #}
    <script type="module">
      // Debug flags
      const SVELTE_DEBUG = true;
      const debugLog = (msg, ...args) => SVELTE_DEBUG && console.log(`[SVELTE DEBUG] ${msg}`, ...args);
      
      // Log initial attempt
      debugLog(`Starting mount for ${JSON.stringify({
        component: "{{ component_name }}",
        mountPoint: "{{ component_id if component_id else component_name | lower + '-component' }}",
        props: {{ props | tojson | safe }}
      })}`);
      
      // Immediately log what we're going to try to import
      const importUrl = 'http://localhost:5173/src/entries/{{ component_name | lower }}.ts';
      debugLog("Import URL:", importUrl);
      
      try {
        // Dynamic import with proper error handling
        import(importUrl)
          .then(module => {
            debugLog("Module imported successfully");
            
            if (!module.default) {
              throw new Error(`Module doesn't have a default export`);
            }
            
            // Find target element
            const targetId = '{{ component_id if component_id else component_name | lower + "-component" }}';
            const targetElement = document.getElementById(targetId);
            debugLog("Target element:", targetElement);
            
            if (!targetElement) {
              throw new Error(`Target element #${targetId} not found`);
            }
            
            // Mount component
            const props = {{ props | tojson | safe }};
            const component = module.default(targetElement, props);
            debugLog("Component mounted successfully");
          })
          .catch(error => {
            console.error(`Failed to import ${importUrl}:`, error);
          });
      } catch (error) {
        console.error(`Error loading Svelte component {{ component_name }}:`, error);
      }
    </script>
  {% else %}
    {# Production mode implementation #}
    ...
  {% endif %}
{% endmacro %}

### Testing with Playwright
- Use Playwright to test components in an actual browser environment
- Add console logs with `page.on("console", log => console.log(log.text()))`
- Take screenshots for visual inspection with `page.screenshot()`
- Test loading time and performance issues
- See `docs/FRONTEND_TESTING.md` for more details

### Using browser-tools-mcp
The Model Context Protocol browser-tools give you access to browser logs and screenshots during component development:

```python
# Get console logs
mcp__browser-tools-mcp__getConsoleLogs()

# Get console errors specifically
mcp__browser-tools-mcp__getConsoleErrors()

# Clear logs for a fresh start
mcp__browser-tools-mcp__wipeLogs()

# Take a screenshot to see the current state
mcp__browser-tools-mcp__takeScreenshot()

# Run various audits
mcp__browser-tools-mcp__runAccessibilityAudit()
mcp__browser-tools-mcp__runPerformanceAudit()
```

This provides a direct way to see what's happening in the browser when developing components with AI assistance.

## External Dependencies

### Avoiding CDN Dependencies

All external JavaScript dependencies should be either:
1. Bundled into our application code
2. Stored locally in `/static/js/extern/`

This approach provides several benefits:
- **Reliability**: No dependency on external services that may change or go down
- **Performance**: Eliminates network requests to third-party domains
- **Offline capability**: Application works without internet access
- **Privacy**: Reduces tracking from third-party domains
- **Security**: Full control over all loaded JavaScript

### Implementation Approaches

1. **Bundling with Dependencies**:
   ```javascript
   // In vite.config.js
   export default defineConfig({
     build: {
       rollupOptions: {
         // Do not externalize deps - bundle them instead
         external: [],
       }
     }
   });
   ```

2. **Local Files for Libraries**:
   - Store library files in `/static/js/extern/`
   - Reference with `{{ url_for('static', filename='js/extern/library.min.js') }}`

3. **NPM Scripts for Downloading**:
   - For libraries needed in both development and production, add scripts to download them on project setup
   - Use version pinning to ensure consistency

### Example: Svelte Integration
For Svelte components, we bundle the Svelte runtime into our UMD build rather than loading it from a CDN. This is configured in the vite.config.js file:

```javascript
// In vite.config.js
rollupOptions: {
  // Do not externalize deps - bundle them instead
  external: [],
  output: {
    // No global variables needed since we're not using CDN
    globals: {}
  }
}
```

This approach ensures our Svelte components work reliably in all environments and don't depend on external CDN availability.
