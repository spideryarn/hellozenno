# Vite + Svelte + Tailwind Integration Plan

> For detailed documentation on the implemented frontend infrastructure, see [Frontend Infrastructure](../docs/FRONTEND_INFRASTRUCTURE.md).

## Goal & Context

Integrate modern frontend technologies into our existing Flask application while minimizing complexity and maintaining continuous functionality. Specifically:

1. Add Tailwind CSS for styling
2. Integrate Svelte (TypeScript) for interactive components
3. Implement Supabase realtime syncing
4. Keep Flask as the primary router

Current stack:
- Backend: Flask + Peewee ORM
- Database: Supabase (PostgreSQL)
- Templates: Jinja
- Frontend: Vanilla JavaScript and CSS
- Hosting: Fly.io for web servers, Supabase for database

## Principles

- Incremental adoption: Make changes gradually so the app works throughout the process
- Minimize complexity: No separate frontend server in production
- Follow project management practices from `docs/PROJECT_MANAGEMENT.md`
- Maintain backward compatibility during transition

## Actions

### Stage: Initial Setup

**DONE: Set up project structure**
- Create a `frontend/` directory at the project root
- Initialize a Node.js project with `package.json`
- Install Vite, Svelte, TypeScript, and Tailwind CSS
- Configure Vite to output to Flask's static directory
- Update `.gitignore` and `.cursorignore` for frontend tooling

**DONE: Configure Vite with Svelte and Tailwind**
- Create `vite.config.js` with Svelte plugin
- Set up Tailwind CSS configuration
- Configure TypeScript for Svelte components
- Create build scripts for development and production

**DONE: Create integration mechanism**
- Develop a system for mounting Svelte components in Jinja templates
- Create shared TypeScript utilities for reuse across components
- Set up a development workflow that runs both Flask and Vite

**DONE: Create Hello World sandbox**
- Create a dedicated Flask route for experimenting with new technologies
- Create a Jinja template for the sandbox
- Create a simple Svelte component
- Set up Tailwind CSS demo

### Stage: Tailwind CSS Integration

**TODO: Set up Tailwind alongside existing CSS**
- Create a new base Jinja template that includes Tailwind
- Configure Tailwind to respect existing styles
- Create a strategy for incremental CSS migration
- Test Tailwind styles on a simple component

**TODO: Create migration path for existing CSS**
- Identify common patterns in existing CSS
- Create Tailwind components/utilities that match current styling
- Document approach for converting CSS to Tailwind

### Stage: Svelte Component Integration

**TODO: Create first Svelte component**
- Identify a simple, isolated UI element for first conversion
- Create a Svelte component with TypeScript
- Implement mounting mechanism in Jinja template
- Test component functionality

**TODO: Develop shared utilities**
- Create TypeScript utility functions for common operations
- Set up a structure for sharing code between components
- Document usage patterns for the team

### Stage: Supabase Realtime Integration

**TODO: Set up Supabase client**
- Install Supabase JS client
- Configure authentication with existing Flask auth
- Create TypeScript interfaces for database models
- Test basic database operations

**TODO: Implement realtime features**
- Create a Svelte component that uses Supabase realtime
- Set up subscription to relevant database tables
- Implement UI updates based on realtime events
- Test realtime functionality

### Stage: Production Build Process

**TODO: Configure production build**
- Set up Vite build for production
- Configure asset optimization (minification, tree-shaking)
- Create a build script for CI/CD pipeline
- Test production build locally

**TODO: Update deployment process**
- Update deployment scripts to include frontend build
- Document new deployment process
- Test deployment to staging environment

### Stage: Documentation and Training

**TODO: Create documentation**
- Document the new architecture
- Create guidelines for developing new features
- Document common patterns and best practices
- Update README with setup instructions

**TODO: Knowledge sharing**
- Create examples of common patterns
- Document migration strategy for existing features
- Create a troubleshooting guide
