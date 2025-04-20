# Hello Zenno SvelteKit Frontend

Hello Zenno is a web application for learning languages. A modern SvelteKit frontend, designed to work with the existing Flask API backend.

## Documentation

This project's documentation is organized into the following sections:

- [Architecture](./docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md) - System architecture and migration strategy
- [Setup and Development](./docs/SETUP.md) - Installation and development instructions
- [UI and Styling](./docs/STYLING.md) - Styling system and component usage
- [API Integration](./docs/BACKEND_FLASK_API_INTEGRATION.md) - How to interact with the Flask backend, e.g. using `getApiUrl()`
- [Authentication](./docs/AUTH.md) - Supabase authentication integration with SvelteKit
- [Site Organization](./docs/SITE_ORGANISATION.md) - Overall site structure and routing
- [Sourcefile Pages](./docs/SOURCEFILE_PAGES.md) - Structure and implementation of sourcefile pages
- [Enhanced Text](./docs/ENHANCED_TEXT.md) - Interactive text with word tooltips
- [Search](./docs/SEARCH.md) - Unified search implementation across site

## Project Status and Roadmap

See [planning/250329_SvelteKit.md](../planning/250329_SvelteKit.md) for the detailed migration plan from using Flask/Jinja to SvelteKit.

## Related Resources

- [Main Project README](../README.md) - Overview of the entire Hello Zenno project
- [Flask API Entry Point](../api/index.py) - Details of the Flask API setup
- [Database Documentation](../docs/DATABASE.md) - Database configuration information

## Quickstart

```bash
# Install dependencies
npm install

# Start the development server
./run_sveltekit.sh
```

For more detailed setup instructions, see the [Setup and Development](./docs/SETUP.md) guide.
