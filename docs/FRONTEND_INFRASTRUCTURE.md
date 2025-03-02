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

## Troubleshooting

### Common Issues

- **Missing Assets**: Ensure Vite is building to the correct directory (`static/build`)
- **TypeScript Errors**: Run `npm run check` in the frontend directory to check for TypeScript errors
- **Styling Conflicts**: Use the `tw-` prefix for all Tailwind classes to avoid conflicts
- **Environment Variables**: Ensure `FLASK_PORT` is set before running development scripts - see `.env.local`

For more details on the implementation plan, see [Vite + Svelte + Tailwind Integration Plan](../planning/250302_Vite_Svelte_Tailwind_plan.md).
