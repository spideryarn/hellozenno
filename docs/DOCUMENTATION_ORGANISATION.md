# Documentation Organisation

This guide helps you navigate HelloZenno's documentation structure.

## Quick Start

- **New to the project?** Start with [README.md](../README.md) then [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Setting up development?** See [backend/docs/DEVOPS.md](../backend/docs/DEVOPS.md)
- **Working with AI assistants?** Begin with [AGENTS.md](../AGENTS.md)
- **Frontend development?** Start with [frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md](../frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md)

## Core Documentation

### Project Overview
- **[README.md](../README.md)** (⭐ START HERE) - Project introduction and quick start
- **[AGENTS.md](../AGENTS.md)** - AI agent instructions and signposts to key docs
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Directory structure and data flow overview
- [docs/instructions/CODING-PRINCIPLES.md](instructions/CODING-PRINCIPLES.md) - Core coding principles

### Setup & Infrastructure
- **[backend/docs/DEVOPS.md](../backend/docs/DEVOPS.md)** (⭐ SETUP) - Complete development environment setup
- [backend/docs/DATABASE.md](../backend/docs/DATABASE.md) - Database configuration and management
- [backend/docs/MIGRATIONS.md](../backend/docs/MIGRATIONS.md) - Database migration procedures
- [frontend/docs/SETUP.md](../frontend/docs/SETUP.md) - Frontend-specific setup notes

### Architecture & Design
- **[frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md](../frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md)** - Frontend architecture overview
- [backend/docs/MODELS.md](../backend/docs/MODELS.md) - Database schema and models
- [backend/docs/URL_REGISTRY.md](../backend/docs/URL_REGISTRY.md) - API URL pattern system
- [frontend/docs/BACKEND_FLASK_API_INTEGRATION.md](../frontend/docs/BACKEND_FLASK_API_INTEGRATION.md) - Type-safe API integration

### Authentication & Security
- **[frontend/docs/AUTH.md](../frontend/docs/AUTH.md)** - Comprehensive auth implementation guide
- Authentication decorators in `backend/utils/auth_utils.py`

### Frontend Development
- [frontend/docs/ENHANCED_TEXT.md](../frontend/docs/ENHANCED_TEXT.md) - Interactive text with hover tooltips
- [frontend/docs/SOURCEFILE_PAGES.md](../frontend/docs/SOURCEFILE_PAGES.md) - Core content pages implementation
- [frontend/docs/STYLING.md](../frontend/docs/STYLING.md) - CSS variables and Bootstrap theming
- [frontend/docs/SITE_ORGANISATION.md](../frontend/docs/SITE_ORGANISATION.md) - Site structure and navigation
- [frontend/docs/DATAGRID.md](../frontend/docs/DATAGRID.md) - DataGrid component usage
- [frontend/docs/SEARCH.md](../frontend/docs/SEARCH.md) - Unified search implementation

### Backend Development
- [backend/docs/CODING_PYTHON.md](../backend/docs/CODING_PYTHON.md) - Python style guidelines
- [backend/docs/CONTENT_GENERATION.md](../backend/docs/CONTENT_GENERATION.md) - AI content generation
- [backend/docs/FLASHCARDS.md](../backend/docs/FLASHCARDS.md) - Flashcard system implementation
- [backend/docs/REFACTORING_PYTHON.md](../backend/docs/REFACTORING_PYTHON.md) - Python refactoring patterns

### Testing & Debugging
- [backend/docs/DEBUGGING.md](../backend/docs/DEBUGGING.md) - Backend debugging tips
- [backend/docs/TESTING.md](../backend/docs/TESTING.md) - Testing patterns (needs update)
- [frontend/docs/FRONTEND_DEBUGGING.md](../frontend/docs/FRONTEND_DEBUGGING.md) - Frontend debugging guide

### User Experience
- [frontend/docs/USER_EXPERIENCE.md](../frontend/docs/USER_EXPERIENCE.md) - UX principles and patterns
- [frontend/docs/AUDIO.md](../frontend/docs/AUDIO.md) - Audio functionality documentation
- [frontend/docs/SITEMAP.md](../frontend/docs/SITEMAP.md) - Site structure and pages

## Planning & History

### Active Planning
Recent planning documents in [docs/planning/](planning/) track ongoing work and design decisions.

### Completed Work
- [docs/planning/finished/](planning/finished/) - Successfully implemented features and migrations
- Notable completions: Supabase migration, SvelteKit adoption, authentication system

### Obsolete Plans
- [docs/planning/obsolete/](planning/obsolete/) - Superseded or abandoned plans
- Kept for historical context

## By User Type

### New Developer
1. [README.md](../README.md)
2. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. [backend/docs/DEVOPS.md](../backend/docs/DEVOPS.md)
4. [docs/instructions/CODING-PRINCIPLES.md](instructions/CODING-PRINCIPLES.md)

### AI Assistant
1. [AGENTS.md](../AGENTS.md)
2. [docs/instructions/](instructions/) - Special modes and workflows
3. [backend/docs/DEBUGGING.md](../backend/docs/DEBUGGING.md)

### Frontend Developer
1. [frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md](../frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md)
2. [frontend/docs/STYLING.md](../frontend/docs/STYLING.md)
3. [frontend/docs/BACKEND_FLASK_API_INTEGRATION.md](../frontend/docs/BACKEND_FLASK_API_INTEGRATION.md)

### Backend Developer
1. [backend/docs/MODELS.md](../backend/docs/MODELS.md)
2. [backend/docs/MIGRATIONS.md](../backend/docs/MIGRATIONS.md)
3. [backend/docs/URL_REGISTRY.md](../backend/docs/URL_REGISTRY.md)

## Documentation Maintenance

- Follow evergreen documentation principles
- Keep information in one canonical location
- Cross-reference rather than duplicate
- Update promptly when implementation changes