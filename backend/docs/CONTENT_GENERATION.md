# Content Generation

HelloZenno includes an AI-powered content generation tool that creates text-based learning materials for various languages and CEFR levels.

## Overview

The `utils.generate_sourcefiles` module uses Claude Sonnet to generate educational content including:
- Relevant topics for specific languages and proficiency levels
- Native language text with appropriate complexity
- Automatic tagging (fiction, history, food, travel, culture)
- Database entries with metadata for the learning platform

## Usage

### Basic Commands

```bash
# Fully automatic - selects underrepresented language and level
python -m utils.generate_sourcefiles generate

# Specify language and level
python -m utils.generate_sourcefiles generate --target-language-code es --language-level B1

# Custom topic
python -m utils.generate_sourcefiles generate --title "Spanish Cuisine Traditions"

# Full specification
python -m utils.generate_sourcefiles generate \
  --target-language-code fr \
  --language-level B2 \
  --title "French Literature" \
  --sourcedir "Advanced Reading"
```

### Command Line Arguments

- `--target-language-code`: Language code (e.g., 'es', 'fr', 'el'). If not provided, automatically selects the language with the fewest existing sourcefiles
- `--language-level`: CEFR level (A2, B1, B2, C1, C2). If not provided, selects the level with least content for the chosen language
- `--title`: Content title/topic. If not provided, generates one automatically using the LLM
- `--sourcedir`: Source directory name (default: "AI-generated examples")

## Examples

### Generate Spanish B1 Content
```bash
python -m utils.generate_sourcefiles generate \
  --target-language-code es \
  --language-level B1
```

### Generate Content for Underrepresented Languages
```bash
# This will automatically find languages with minimal content
python -m utils.generate_sourcefiles generate
```

### Create Themed Content
```bash
python -m utils.generate_sourcefiles generate \
  --target-language-code it \
  --language-level B2 \
  --title "Italian Renaissance Art"
```

## How It Works

1. **Language Selection**: Automatically selects languages with minimal existing content or uses specified language
2. **Level Selection**: Chooses CEFR levels (A2-B2) that are underrepresented for the target language
3. **Topic Generation**: Uses LLM to create culturally relevant topics if not specified
4. **Content Creation**: Generates native language text using prompt templates
5. **Database Storage**: Creates Sourcefile entries with metadata, tags, and learning platform integration

## Output

The tool creates:
- Database entries in the Sourcefile and Sourcedir tables
- Automatic URL generation for web access
- Content tagging for categorization
- Metadata including generation model and timestamp

Success output includes:
- Sourcefile ID
- Generated tags
- Platform path
- Full URL for immediate access

## Automation Features

- **Smart Language Selection**: Prioritizes languages with fewer learning materials
- **Level Balancing**: Ensures even distribution across CEFR levels
- **Topic Relevance**: Generates culturally appropriate topics for each language
- **Automatic Tagging**: Categorizes content based on title keywords
