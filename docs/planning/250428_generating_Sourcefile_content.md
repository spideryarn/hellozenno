# Generating Sourcefile Content

## Goal
Create a Python CLI tool using Typer (`backend/utils/generate_sourcefiles.py`) that generates new language learning content for HelloZenno in various languages. The tool should support configurable language levels and work seamlessly with our existing database models and LLM integration.

## Context
HelloZenno needs a way to generate more language learning content, especially for languages that have few or no existing Sourcefiles. This will help expand the platform's content offering without requiring manual content creation for every language.

## Key Requirements
- CLI with input parameters for target language, sourcedir, title, and CEFR language level
- Ability to pick a random language with no Sourcefiles if target language is not specified
- Generation of 150-500 word content (longer for more advanced language levels)
- Content should be a mix of fiction and non-fiction appropriate for adult learners
- Integration with existing database models and LLM functions
- Content should be stored using the existing `_create_text_sourcefile()` function

## Key Decisions
- We will implement a CLI tool using Typer for argument parsing and commands
- We will require the title parameter to define the content topic/theme in the initial implementation
- We will use a Jinja template for the LLM prompt, following the pattern of existing prompt templates
- Content generation will be done in a single step for the initial implementation, with potential for a two-step approach (generate topics, then content) in the future
- We will use existing database functions to store the generated content
- We will adjust the content length based on the CEFR language level (A1-A2: 150-250 words, B1-B2: 250-350 words, C1-C2: 350-500 words)

## Useful References
- `backend/utils/vocab_llm_utils.py` - Contains the `extract_tricky_words()` function that shows how to call the LLM with a prompt template (HIGH)
- `backend/utils/sourcefile_utils.py` - Contains the `_create_text_sourcefile()` function that we'll use to store generated content (HIGH)
- `backend/docs/MODELS.md` - Database model documentation showing relationships between Sourcedir, Sourcefile, etc. (MEDIUM)
- `backend/prompt_templates/extract_tricky_wordforms.jinja` - Example of a prompt template structure (MEDIUM)

## Actions

### Create Prompt Template
- [ ] Create `backend/prompt_templates/generate_sourcefiles.jinja` template
  - [ ] Include parameters for target language, title, and CEFR level
  - [ ] Structure the prompt to generate appropriate content for language learners
  - [ ] Include guidance on content length based on language level
  - [ ] Ensure the prompt produces culturally relevant, level-appropriate content

### Implement CLI Tool
- [ ] Create `backend/utils/generate_sourcefiles.py` file
  - [ ] Set up Typer app with appropriate command-line arguments
  - [ ] Implement logic to validate input parameters
  - [ ] Implement function to select a random language if needed
  - [ ] Implement function to get or create the appropriate Sourcedir
  - [ ] Implement main content generation function that calls the LLM
  - [ ] Use `_create_text_sourcefile()` to store the generated content

### Language Selection Logic
- [ ] Implement function to find languages with no Sourcefiles
  - [ ] Query database to find languages with no Sourcefiles
  - [ ] If all languages have Sourcefiles, select the language with the fewest
  - [ ] Return the selected language code and name

### Testing and Validation
- [ ] Test generation of content in various languages and at different CEFR levels
  - [ ] Verify content quality and appropriate difficulty level
  - [ ] Ensure proper database storage and relationships
  - [ ] Check that appropriate metadata is stored with the Sourcefile

### Documentation
- [ ] Add docstrings to all functions
- [ ] Add README section or command help text explaining tool usage
- [ ] Add example commands

## Future Enhancements
- Two-step content generation (generate topics first, then content)
- Ability to specify content type/genre (story, dialogue, article, etc.)
- Batch generation of multiple related Sourcefiles
- Automatic generation of exercises or comprehension questions
- Integration with workflow to automatically extract wordforms and phrases after generation

## Implementation Details

### CLI Interface Structure
```
Usage: python -m backend.utils.generate_sourcefiles [OPTIONS]

Options:
  --target-language-code TEXT     Language code (e.g., 'el' for Greek)
  --sourcedir TEXT                Source directory name [default: AI-generated]
  --title TEXT                    Content title/topic [required]
  --language-level TEXT           CEFR level (A1, A2, B1, B2, C1, C2)
  --help                          Show this message and exit.
```

### Prompt Template Structure
```jinja
You are a language teacher creating authentic content for {{ target_language_name }} learners at {{ language_level if language_level else "mixed" }} level.

Please write a {{ text_type if text_type else "short passage" }} about "{{ title }}" that would be appropriate for language learners. 

Guidelines:
- Length: {{ "150-250" if language_level in ["A1", "A2"] else "250-350" if language_level in ["B1", "B2"] else "350-500" }} words
- Use vocabulary and grammar appropriate for {{ language_level if language_level else "intermediate" }} learners
- Include culturally relevant content if applicable
- Create engaging, interesting content for adult learners
- Mix dialog and narrative if appropriate for the topic
- Avoid using slashes (/) in the text as they cause URL routing issues

Only output the text content in {{ target_language_name }}, with no additional commentary, introduction, or translation.
```

## Appendix - example prompts from the user from a previous version for inspiration (these will need modification to be usable here)

### Prompt 1: Generating Diverse Language Learning Topics

Generate 20 diverse, engaging topics for short articles suitable for adult B1-level learners of[TARGET_LANGUAGE]. Include:

1. Everyday situations (doctor visits, shopping, finding housing)
2. Cultural traditions and celebrations unique to [TARGET_CULTURE]
3. Food and culinary experiences with cultural significance
4. Brief biographies of interesting but lesser-known figures from [TARGET_CULTURE]
5. Historical events or places with simple narratives
6. Practical guides (simple recipes, directions, etc.)
7. Surprising facts or "things you didn't know" about [TARGET_CULTURE]
8. Modern life topics (technology, social media, work)
9. Travel-related topics specific to regions where [TARGET_LANGUAGE] is spoken
10. Holiday traditions and how they differ from Western celebrations

For each topic, provide:
- A title in [TARGET_LANGUAGE] with English translation
- 1-2 sentences explaining why this topic would engage adult language learners
- Key vocabulary areas that would be practiced (5-8 words)

Ensure topics are culturally authentic, avoid stereotypes, and are appropriate for B1 learners (limited complex
grammar, common vocabulary with some specialized terms).

### Generating B1-Level Stories from Topics

Create an engaging short article in [TARGET_LANGUAGE] on the topic: "[SELECTED_TOPIC]"

Guidelines:
- Length: 300-500 words
- Language level: B1 (intermediate)
- Include 10-15 useful vocabulary items that B1 learners might not know yet (highlight these in bold)
- Use simple sentence structures with some compound sentences
- Include cultural context where relevant
- Add 2-3 comprehension questions at the end
- Include a mini-glossary with definitions in [TARGET_LANGUAGE]

Writing style:
- Conversational and friendly tone
- Clear paragraph structure
- Concrete examples rather than abstract concepts
- Mix of present, past, and future tenses appropriate to B1 level
- Some idiomatic expressions (but not too complex)
- Avoid complex subordinate clauses or highly specialized vocabulary

The article should be authentic and culturally appropriate, teaching language in context while maintaining 
  readability for intermediate learners.

### Prompt for searching for content on the internet

Find a dozen fiction stories, podcasts or articles of varying difficulty in Finnish.

Aim for about 20, diverse, short (perhaps a few hundred words or so), and ranging in difficulty from A2 to C1.

Prefer public domain, or at least web-readable without needing Javascript or captchas to render.

This is for a language learning website, so we'll use these to help the student learn. It would be great if they would be at least somewhat interesting to an adult, e.g. if they're entertaining, or famous myths from that culture, or interesting history/culture, or tell some kind of story, or provide useful facts/information/news.

Provide them as JSON, in the following schema:

```json
{
  “url”: str,
  “description”: str,
  “language_level”: str, # e.g. “B2”,
  “text”: str,
}
```
