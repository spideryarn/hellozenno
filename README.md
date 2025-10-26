# Hello Zenno - Language Learning Assistant

An open-source web application for intermediate and advanced language learners, designed to assist with vocabulary acquisition and listening practice through AI-generated content.

## About Hello Zenno

Hello Zenno helps you learn languages by:
- Assisting you in reading texts in your target language
- Creating AI-generated dictionary entries with rich metadata
- Highlighting unfamiliar words with interactive hover explanations
- Generating audio dictation exercises with words in different contexts
- Supporting vocabulary acquisition through contextual learning

Built by a co-founder of Memrise, Hello Zenno fills the gap in language learning apps by providing deeper context and richer dictionary information tailored to what you're reading.

## Features

### AI-Enhanced Learning
- Rich AI-generated dictionary with detailed metadata and examples
- Dynamic audio generation for hearing words in various contexts
- Interactive text highlighting for quick vocabulary lookup
- Etymology explanations and contextual usage examples
- Dictation flashcards for listening practice

### Source Files
Source files are the primary way to add learning content. They can be created in two ways:

1. **Text Input**
   - Paste or type text directly into the application
   - Perfect for copying text from articles, books, or other sources
   - Text is processed immediately without OCR
   - Creates a .txt file in your source directory

2. **Image Upload**
   - Upload images containing text (e.g., photos of books, signs, etc.)
   - OCR is used to extract text from the images
   - Original image is preserved for reference
   - Supports common image formats (jpg, png, etc.)

Both types of source files support:
- Automatic translation to English
- Vocabulary extraction
- Interactive word linking
- Practice sentence generation

## Quick Start for Developers

### Prerequisites
- Docker Desktop app installed and running
- Node.js and npm installed
- Python 3.10+ installed
- Supabase CLI installed (`brew install supabase/tap/supabase`)

### Setup Steps

1. **Start Docker and Supabase:**
   ```bash
   # Make sure Docker Desktop app is running first
   supabase start
   ```

2. **Configure environment:**
   ```bash
   # Copy the example environment file
   cp .env.example .env.local
   # Edit .env.local and fill in your credentials
   ```

3. **Run the backend (Terminal 1):**
   ```bash
   source .env.local
   export FLASK_PORT=3000
   ./scripts/local/run_backend.sh
   ```
   The Flask API will run on http://localhost:3000

4. **Run the frontend (Terminal 2):**
   ```bash
   source .env.local
   ./scripts/local/run_frontend.sh
   ```
   The SvelteKit app will run on http://localhost:5173

5. **View the application:**
   Open http://localhost:5173 in your browser

Tip:
- If another app is using port 5173, free it with `lsof -ti:5173 | xargs kill -9` or run the frontend on 5174 using `cd frontend && PORT=5174 npm run dev`, then open http://localhost:5174

### Detailed Documentation

For more detailed setup and development information:
- `backend/docs/DEVOPS.md` - Full development setup and infrastructure details
- `backend/docs/DATABASE.md` - Database configuration and management
- `backend/docs/MIGRATIONS.md` - Database migration procedures
- `frontend/docs/AUTHENTICATION_AUTHORISATION.md` - Authentication setup with Supabase
- `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md` - Frontend architecture overview
- `.env.example` - Required environment variables reference
- [Changelog](/changelog) - Recent updates and changes 