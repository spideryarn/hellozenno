# Hello Zenno - Language Learning Assistant

A web application for learning languages through interactive content.

## Features

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

Copy `.env.example` to `.env.local` and fill in your credentials to get started. 