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

## Getting Started

See the following documentation for setup and development:
- `docs/DEVOPS.md` for development setup and infrastructure details
- `docs/DATABASE.md` for database configuration
- `.env.example` for required environment variables
- [Changelog](/changelog) for recent updates and changes

Copy `.env.example` to `.env.local` and fill in your credentials to get started. 