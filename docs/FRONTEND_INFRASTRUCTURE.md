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

2. **Entry Point** (`frontend/src/entries/yourcomponent-entry.ts`)
   ```typescript
   import YourComponent from '../components/YourComponent.svelte';
   export { YourComponent };
   export default function(target: HTMLElement, props: any) {
     return new YourComponent({ target, props });
   }
   ```

3. **Template Integration**
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

### Best Practices & Gotchas
- Use TypeScript for props and conditional rendering for optional props
- Keep components focused with scoped styles
- Entry filename must match vite_entries value (e.g., 'mycomponent' → 'mycomponent-entry.ts')
- Always use an array for vite_entries: `{% set vite_entries = ['componentname'] %}`
- Use unique IDs for multiple component instances
- Test in both development and production builds
