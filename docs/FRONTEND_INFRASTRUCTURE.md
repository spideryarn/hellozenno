# Frontend Infrastructure

see `docs/FRONTEND_TESTING.md`

This document describes the frontend infrastructure for Hello Zenno, including the tools, build process, and development workflow. see `250302_Vite_Svelte_Tailwind_plan.md` (though we've decided to ditch Tailwind)

## Overview

Our frontend infrastructure combines modern tools with our existing Flask application to enable incremental adoption of new technologies while maintaining a simple production deployment.

### Key Components

- **Flask + Jinja**: Primary server-side rendering and routing
- **Vite**: Modern build tool for frontend assets
- **Svelte**: Component framework for interactive UI elements
- **TypeScript**: Type-safe JavaScript for better developer experience
- **Base CSS**: Custom CSS framework for consistent styling
- **Supabase JS Client**: For realtime database features

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| **Vite** | Fast development server and build tool that handles HMR (Hot Module Replacement) |
| **Svelte** | Reactive component framework that compiles to vanilla JavaScript |
| **TypeScript** | Typed superset of JavaScript for better code quality and IDE support |
| **Base CSS** | Custom CSS framework that provides consistent styling across the application |
| **Supabase JS** | Client library for interacting with Supabase services |

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

## Development Workflow

1. Set the Flask port environment variable:
   ```bash
   export FLASK_PORT=5000  # Or any other available port
   ```

2. Run Flask server in one terminal:
   ```bash
   ./scripts/local/run_flask.sh
   ```

3. Run Vite dev server in another terminal:
   ```bash
   ./scripts/local/run_frontend_dev.sh
   ```

4. Visit `http://localhost:$FLASK_PORT` in your browser

During development:
- Flask serves the HTML templates and API endpoints
- Vite serves the JavaScript, CSS, and other assets
- Changes to frontend code are immediately reflected via HMR
- Changes to Flask routes or templates require a page refresh

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_PORT` | Yes | The port on which Flask will run (e.g., 5000) |

## Build Process

The frontend build process is handled by Vite, which:

1. Compiles Svelte components to JavaScript
2. Processes TypeScript to JavaScript
3. Bundles and minifies all assets
4. Outputs to the `static/build` directory

To build for production:
```bash
./scripts/prod/build-frontend.sh
```

## Deployment

For production deployment:

1. The frontend assets are built using `build-frontend.sh`
2. The built assets are included in the Flask application
3. Flask serves the static assets from the `static/build` directory

The `deploy.sh` script runs `build-frontend.sh` before deploying to ensure the latest frontend assets are included.

## Integration with Existing Code

- **Isolated Components**: Svelte components are mounted to specific DOM elements
- **Gradual Adoption**: New technologies can be adopted page by page or component by component

## CSS Guidelines

### Using Base CSS Classes

1. **Template Setup**
   - Extend from `base.jinja` for all templates
   - Add a Vite entry point if the page needs JavaScript:
     ```jinja
     {% set vite_entry = 'your-page-entry' %}
     ```

2. **Common Patterns**
   - Use `container` for main content wrappers
   - Use `word-metadata` for content sections
   - Use `button-group` for button containers
   - Use `card` and `card-title` for card components

3. **Component Classes**
   - Cards/Sections: `word-metadata` for white background panels
   - Lists: `phrases-list` with `phrase-item` children
   - Buttons: `button` with modifiers like `delete-btn`
   - Metadata: `metadata-display` for timestamp displays
   - Links: `word-link` for dictionary/lemma links

4. **Layout Patterns**
   - Two-column grid: Use `lemma-details` for grid layouts
   - Card grid: Use `phrases-list` with `phrase-item` children
   - Responsive design: Use media queries in `base.css`

5. **Typography**
   - Main headings: `h1` with default styling
   - Section headings: `h2` with default styling
   - Subsection headings: `h3` with default styling
   - Body text uses Times New Roman by default
   - Monospace text: Use `metadata-display` for timestamps

6. **Interactive Elements**
   - Buttons: `button` base class with modifiers
   - Hover effects: Built into base CSS classes
   - Forms: Use standard form elements with base styling

7. **Responsive Design**
   - Grid layouts automatically stack on mobile
   - Use media queries in `base.css` for custom breakpoints

8. **Component Integration**
   - Wrap Svelte mount points in appropriate containers
   - Use consistent class patterns across templates
   - Follow the established component hierarchy

## Troubleshooting

### Common Issues

- **Missing Assets**: Ensure Vite is building to the correct directory (`static/build`)
- **TypeScript Errors**: Run `npm run check` in the frontend directory to check for TypeScript errors
- **Styling Conflicts**: Check `base.css` for existing styles before adding new ones
- **Environment Variables**: Ensure `FLASK_PORT` is set before running development scripts - see `.env.local`

## Creating New Svelte Components


### Component Creation Checklist

1. **Create the Component**
   - Create a new `.svelte` file in `frontend/src/components/`
   - Define props using TypeScript:
     ```typescript
     <script lang="ts">
       export let myProp: string;
     </script>
     ```
   - Add component template and styles
   - Keep styles scoped to the component
   - see e.g. `frontend/src/components/MiniSentence.svelte` (as used in `templates/lemma.jinja`)

2. **Create the Entry Point**
   - Create a new entry file in `frontend/src/entries/` named `your-component-entry.ts`
   - Export both named and default exports:
     ```typescript
     import YourComponent from '../components/YourComponent.svelte';
     export { YourComponent };
     export default function(target: HTMLElement, props: any) {
       return new YourComponent({ target, props });
     }
     ```

3. **Update the Template**
   - Add the Vite entry point at the top of your Jinja template:
     ```jinja
     {% set vite_entry = 'your-component-entry' %}
     ```
   - Create a mount point with a unique ID:
     ```html
     <div id="your-component-1"></div>
     ```
   - Use the `load_svelte_component` macro to mount the component:
     ```jinja
     {{ load_svelte_component('YourComponent', {
         'prop1': value1,
         'prop2': value2
     }, component_id='your-component-1') }}
     ```

4. **Component Best Practices**
   - Use TypeScript for prop definitions
   - Add conditional rendering for optional props
   - Keep components focused and single-purpose
   - Use scoped styles to avoid conflicts
   - Follow existing styling patterns from `base.css`
   - Add hover states and transitions for interactive elements

5. **Testing**
   - Verify component renders in development mode
   - Check browser console for prop warnings
   - Test with different prop combinations
   - Verify HMR works correctly
   - see `docs/FRONTEND_TESTING.md` (and `tests/frontend/test_lemma_page.py` as an example, and `tests/fixtures_for_tests.py`)

### Example Component Integration

```jinja
{# template.jinja #}
{% extends "base.jinja" %}
{% from "base_svelte.jinja" import load_svelte_component %}

{% set vite_entry = 'my-component-entry' %}

{% block content %}
<div class="container">
    <div id="my-component-1"></div>
    {{ load_svelte_component('MyComponent', {
        'title': 'Hello',
        'content': 'World'
    }, component_id='my-component-1') }}
</div>
{% endblock %}
```

```typescript
// frontend/src/components/MyComponent.svelte
<script lang="ts">
  export let title: string;
  export let content: string;
</script>

<div class="my-component">
  <h2>{title}</h2>
  <p>{content}</p>
</div>

<style>
  .my-component {
    padding: 1rem;
    border: 1px solid #e2e8f0;
  }
</style>
```

```typescript
// frontend/src/entries/my-component-entry.ts
import MyComponent from '../components/MyComponent.svelte';
export { MyComponent };
export default function(target: HTMLElement, props: any) {
  return new MyComponent({ target, props });
}
```

### Common Gotchas

1. **Missing Entry Point**: Always create an entry file and set `vite_entry` in the template
2. **Prop Type Errors**: Define all props with TypeScript types
3. **Style Conflicts**: Use scoped styles and follow `base.css` patterns
4. **HMR Issues**: Check Vite dev server is running and port is correct
5. **Production Build**: Test component works in production build
6. **Multiple Instances**: Use unique IDs for each component instance
7. **Props Validation**: Handle optional props with conditional rendering
