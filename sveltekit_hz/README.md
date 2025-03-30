# Hello Zenno SvelteKit Frontend

Hello Zenno is a web application for learning languages. A modern SvelteKit frontend, designed to work with the existing Flask API backend.

## Documentation

This project's documentation is organized into the following sections:

- [Architecture](./docs/ARCHITECTURE.md) - System architecture and migration strategy
- [Setup and Development](./docs/SETUP.md) - Installation and development instructions
- [UI and Styling](./docs/STYLING.md) - Styling system and component usage
- [API Integration](./docs/API_INTEGRATION.md) - How to interact with the Flask backend, e.g. using `get_api_url()`

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
