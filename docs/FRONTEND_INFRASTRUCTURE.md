# Frontend Infrastructure

This document describes the frontend infrastructure for Hello Zenno, including the tools, build process, and development workflow. For the implementation plan, see [Vite + Svelte + Tailwind Integration Plan](../planning/250302_Vite_Svelte_Tailwind_plan.md).

## Overview

Our frontend infrastructure combines modern tools with our existing Flask application to enable incremental adoption of new technologies while maintaining a simple production deployment.

### Key Components

- **Flask + Jinja**: Primary server-side rendering and routing
- **Vite**: Modern build tool for frontend assets
- **Svelte**: Component framework for interactive UI elements
- **TypeScript**: Type-safe JavaScript for better developer experience
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Supabase JS Client**: For realtime database features

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| **Vite** | Fast development server and build tool that handles HMR (Hot Module Replacement) |
| **Svelte** | Reactive component framework that compiles to vanilla JavaScript |
| **TypeScript** | Typed superset of JavaScript for better code quality and IDE support |
| **Tailwind CSS** | Utility-first CSS framework that generates only the CSS you use |
| **PostCSS** | Tool for transforming CSS with plugins like Autoprefixer |
| **Supabase JS** | Client library for interacting with Supabase services |

## Project Structure

```
/
├── frontend/                  # Frontend source code
│   ├── src/
│   │   ├── components/        # Svelte components
│   │   ├── entries/           # Entry points for different pages
│   │   ├── lib/               # Shared TypeScript utilities
│   │   └── styles/            # Tailwind and other styles
│   ├── vite.config.js         # Vite configuration
│   ├── tsconfig.json          # TypeScript configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
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
3. Compiles Tailwind CSS to optimized CSS
4. Bundles and minifies all assets
5. Outputs to the `static/build` directory

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

- **Tailwind Prefix**: All Tailwind classes use the `tw-` prefix to avoid conflicts with existing CSS
- **Isolated Components**: Svelte components are mounted to specific DOM elements
- **Gradual Adoption**: New technologies can be adopted page by page or component by component

## Tailwind Migration Guide

### Converting Jinja Templates to Tailwind

1. **Template Setup**
   - Extend from `base_with_tailwind.jinja` instead of `base.jinja`
   - Add a Vite entry point if the page needs JavaScript:
     ```jinja
     {% set vite_entry = 'your-page-entry' %}
     ```

2. **Common Patterns**
   - Use `tw-container-prose` for content-heavy pages (max-width optimized for reading)
   - Use `tw-container-wide` for full-width layouts
   - Wrap main content in appropriate container:
     ```jinja
     <div class="tw-container-prose">
       <!-- Your content -->
     </div>
     ```

3. **Component Classes**
   - Cards/Sections: `tw-content-section` for white background panels
   - Lists: `tw-list` with `tw-list-item` children
   - Buttons: `tw-btn` with modifiers like `tw-btn-danger`
   - Metadata: `tw-metadata` for timestamp displays
   - Links: `tw-word-link` for dictionary/lemma links

4. **Layout Patterns**
   - Two-column grid:
     ```html
     <div class="tw-grid tw-grid-cols-2 tw-gap-6">
       <div>Left column</div>
       <div>Right column</div>
     </div>
     ```
   - Card grid (e.g., languages page):
     ```html
     <div class="tw-grid tw-grid-cols-3 tw-gap-6">
       <!-- Card items -->
     </div>
     ```

5. **Typography**
   - Main headings: `tw-text-4xl tw-font-normal tw-mb-8`
   - Section headings: `tw-text-2xl tw-font-normal tw-mb-4`
   - Subsection headings: `tw-text-xl tw-font-normal tw-mb-3`
   - Body text uses Times New Roman by default
   - Monospace text (e.g., metadata): `tw-font-mono`

6. **Interactive Elements**
   - Buttons: `tw-btn` base class with modifiers
   - Hover effects: Most interactive elements have built-in hover states
   - Forms: Use `tw-` prefixed form classes for inputs and controls

7. **Responsive Design**
   - Grid columns automatically stack on mobile
   - Use Tailwind's responsive prefixes for custom breakpoints:
     ```html
     <div class="tw-grid tw-grid-cols-1 md:tw-grid-cols-2 lg:tw-grid-cols-3">
     ```

8. **Migration Strategy**
   - Convert one template at a time
   - Start with simpler, self-contained templates
   - Test thoroughly on mobile and desktop
   - Keep existing CSS classes until fully migrated

### Common Gotchas

1. **CSS Conflicts**
   - Always use the `tw-` prefix
   - Remove conflicting styles from `base.css`
   - Check browser dev tools for competing styles

2. **Layout Issues**
   - Use `tw-container-prose` or `tw-container-wide` at the top level
   - Mind the top padding (`tw-pt-24`) for the fixed navigation
   - Use `tw-space-y-{size}` for consistent vertical spacing

3. **Component Integration**
   - Wrap Svelte mount points in appropriate Tailwind containers
   - Use consistent class patterns across templates
   - Follow the established component hierarchy

## Troubleshooting

### Common Issues

- **Missing Assets**: Ensure Vite is building to the correct directory (`static/build`)
- **TypeScript Errors**: Run `npm run check` in the frontend directory to check for TypeScript errors
- **Styling Conflicts**: Use the `tw-` prefix for all Tailwind classes to avoid conflicts
- **Environment Variables**: Ensure `FLASK_PORT` is set before running development scripts - see `.env.local`

For more details on the implementation plan, see [Vite + Svelte + Tailwind Integration Plan](../planning/250302_Vite_Svelte_Tailwind_plan.md).
