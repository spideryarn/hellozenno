# Setup and Development

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+ with Flask backend running

## Installation

Install dependencies:

```bash
cd frontend
npm install
```

## Development Commands

Run the development server:

```bash
# Start the SvelteKit development server
npm run dev

# Or open in a browser automatically
npm run dev -- --open
```

The SvelteKit frontend runs on port 5173 by default (see `run_sveltekit.sh`): http://localhost:5173

The Flask backend should be running separately (see `scripts/local/run_backend.sh`) on port 3000: http://localhost:3000

## Build for Production

(We haven't tried this yet)

```bash
npm run build
npm run preview  # Preview the production build locally
```

## Environment Configuration

Create a `.env` file in the SvelteKit root directory with the following variables:

```
PUBLIC_API_BASE=http://localhost:3000/api
```

For production, this will be updated to point to the deployed API endpoint. 