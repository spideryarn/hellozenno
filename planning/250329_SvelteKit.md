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
- Don't number or add headings to the Actions stages, so it's easy to reorder them

## Decisions from User

- Development: Run Flask (port 3000) and Vite (port 5173) servers separately
- State management: Not too complex yet, but will integrate Supabase frontend library later
- Styling: Start with minimal CSS, discuss Bootstrap integration later
- Auth: Supabase will handle auth
- Migration priority: Start with languages.jinja, then Sentence.svelte
- TypeScript: Use typing fairly strictly for IDE benefits, not purist
- SvelteKit features: Yes to server-side rendering

## Plan: Small Stages

Project Setup & Configuration
- [x] Create SvelteKit project (done: renamed to `sveltekit_hz`)
- [x] Configure SvelteKit routes and basic layout structure
- [x] Setup basic API connection to Flask backend
- [x] Test a simple API call from SvelteKit to Flask

Languages Page - Basic
- [x] Create minimal Languages route
- [x] Fetch languages data from API
- [x] Display basic languages list without styling
- [x] Test route works and displays data correctly

Languages Page - Styling
- [x] Add CSS similar to original languages.jinja
- [x] Implement responsive grid layout
- [x] Ensure links work correctly 

API Integration
- [x] Refine SvelteKit-to-Flask API interactions
- [x] Create language name lookup API endpoint
- [x] Use backend API for translations and language information

Docs
- [ ] Write up `sveltekit_hz/README.md` in detail

Create any missing Flask APIs
- [ ] Write a list of all the current Flask Jinja views in an Appendix at the bottom, with checkboxes next to each
- [ ] For each Jinja view, we'll need to create a corresponding API that we can call from SvelteKit, e.g. if we have `views/blah_views.py blah_vw()`, we'll need to create/update `views/blah_api.py` and add `blah_api()`, we might need to update the Blueprints with the new `blah_api`. We want to reuse code, so we'll probably need to abstract out what's common to the Jinja-view and API functions into a `blah_utils.py blah_core()` that they can both call. see `views/languages_views.py get_languages_api()` as an example.
- [ ] Create all the new API views, stopping to discuss after each one.

Sentence Component - Basic Structure
- [x] Create Sentence component with minimal functionality
- [x] Define TypeScript interfaces for sentence data
- [x] Set up basic layout without complex features

Sentence Component - Enhanced Features
- [x] Implement word highlighting
- [x] Add translations display
- [x] Set up metadata section

Sentence Component - Audio Integration
- [x] Add audio player functionality
- [x] Implement playback controls
- [ ] Add audio generation capability

Authentication Integration
- [ ] Discuss Supabase auth approach
- [ ] Plan auth integration in SvelteKit
- [ ] Implement basic authentication flow

Later Stages (To Discuss)
- [ ] Enhance styling and user experience - discuss CSS framework decision (Bootstrap vs alternatives)
- [ ] Set up deployment configuration
- [ ] Discuss form handling approach in SvelteKit
- [ ] Supabase realtime updates integration
- [ ] Deployment strategy for Vercel
- [ ] Implement authentication

## Actions & Progress

### Completed
- [x] Create SvelteKit project
- [x] Set up basic layout and routing structure
- [x] Implement the languages page with server-side data fetching
- [x] Create placeholder for language/[language_code]/sources route
- [x] Connect Flask API with SvelteKit frontend
- [x] Create sentence component skeleton
- [x] Successfully implement and test Sentence component
- [x] Fixed API routes for better coordination between Flask and SvelteKit
- [x] Enhanced backend APIs by adding language name lookup endpoint
- [x] Improved SvelteKit server-side rendering with proper fetch handling

### In Progress
- [ ] Enhance sentence component with more features
- [ ] Implement remaining language-specific routes

## Questions

- Best practice for API route structure between SvelteKit and Flask?
- How to handle environment configuration across both services?
- Deployment strategy details for Vercel?


