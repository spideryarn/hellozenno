# Port to SvelteKit

## Goal

We built a Flask/Jinja + Svelte app called "Hello Zenno" in `views/` and `static/`.

We're going to keep Flask for an API (e.g., `views/*_api.py`), but port all user-facing parts to SvelteKit.

## Principles

- Simple, minimal, use robust best practices
- Better to fail with a loud error than run silently with wrong behavior
- SvelteKit for user-facing, Python for API
- Backend database on Supabase, Python serverless hosting on Vercel
- Don't optimize for performance
- Break down into lots of small stages that work on a small slice of functionality, ending each stage with working code
- Start very basic, gradually layer in complexity
- Avoid hacks, fallbacks, and bandaids
- Don't worry about backend compatibility
- Keep the code concise
- Discuss uncertainties rather than guessing

## Decisions from User

- Development: Run Flask (port 3000) and Vite (port 5173) servers separately
- State management: Not too complex yet, but will integrate Supabase frontend library later
- Styling: Start with minimal CSS, discuss Bootstrap integration later
- Auth: Supabase will handle auth
- Migration priority: Start with languages.jinja, then Sentence.svelte
- TypeScript: Use typing fairly strictly for IDE benefits, not purist
- SvelteKit features: Yes to server-side rendering

## Plan: Small Stages

### Stage 1: Project Setup & Configuration
- [x] Create SvelteKit project (done: renamed to `sveltekit_hz`)
- [ ] Configure SvelteKit routes and basic layout structure
- [ ] Setup basic API connection to Flask backend
- [ ] Test a simple API call from SvelteKit to Flask

### Stage 2: Languages Page - Basic
- [ ] Create minimal Languages route
- [ ] Fetch languages data from API
- [ ] Display basic languages list without styling
- [ ] Test route works and displays data correctly

### Stage 3: Languages Page - Styling
- [ ] Add CSS similar to original languages.jinja
- [ ] Implement responsive grid layout
- [ ] Ensure links work correctly 

### Stage 4: Sentence Component - Basic Structure
- [ ] Create Sentence component with minimal functionality
- [ ] Define TypeScript interfaces for sentence data
- [ ] Set up basic layout without complex features

### Stage 5: Sentence Component - Enhanced Features
- [ ] Implement word highlighting
- [ ] Add translations display
- [ ] Set up metadata section

### Stage 6: Sentence Component - Audio Integration
- [ ] Add audio player functionality
- [ ] Implement playback controls
- [ ] Add audio generation capability

### Stage 7: Authentication Integration
- [ ] Discuss Supabase auth approach
- [ ] Plan auth integration in SvelteKit
- [ ] Implement basic authentication flow

### Later Stages (To Discuss)
- [ ] Form handling approach in SvelteKit
- [ ] CSS framework decision (Bootstrap vs alternatives)
- [ ] Supabase realtime updates integration
- [ ] Deployment strategy for Vercel

## Questions

- Best practice for API route structure between SvelteKit and Flask?
- How to handle environment configuration across both services?
- Deployment strategy details for Vercel?


## Actions

- [ ] Ask the user lots of questions to better understand the goals, constraints, and desiderata

- [ ] Update this doc with a more detailed, hierarchical, unnumbered list of actions

- [ ] Rewrite the `languages.jinja` as a new Svelte component in `HelloZenno`

- [ ] Review and create missing Flask API endpoints in `views/*_api.py` to support all SvelteKit frontend functionality



