# Database Models

This document provides a concise overview of the main database models in HelloZenno, their key fields, and relationships.

Based on the full model declaration in `backend/db_models.py` 

## Core Models

### BaseModel
- Base class for all models with timestamps (`created_at`, `updated_at`)
- Provides `update_or_create` pattern implementation

### Lemma
Dictionary form entries for words
- `lemma`: The dictionary form of the word
- `target_language_code`: Language code (e.g., "el" for Greek)
- `is_complete`: boolean for whether we have populated only the essential fields, or all of them
- `translations`: List of English translations (JSONField)
- `part_of_speech`: Grammatical category (verb, noun, etc.)
- `commonality`: How common the word is (0-1 scale)
- `guessability`: How easy to guess for English speakers (0-1 scale)
- Relationships:
  - `wordforms`: Different forms of this lemma
  - `example_sentences`: Example sentences containing this lemma
- ...

### Wordform
Individual word forms and inflections
- `wordform`: The actual word form
- `lemma_entry`: Foreign key to the dictionary form (Lemma)
- `target_language_code`: Language code
- `part_of_speech`: Grammatical category
- `translations`: List of English translations (JSONField)
- `inflection_type`: Description of the inflection (e.g., "plural")
- `is_lemma`: Whether this is also a dictionary form

### Sentence
Example sentences in the target language
- `target_language_code`: Language code
- `sentence`: The actual sentence text
- `translation`: English translation
- `audio_data`: MP3 audio data for the sentence (BlobField)
- `slug`: URL-friendly version of the sentence
- Relationships:
  - `lemmas`: Junction to associated lemmas (via SentenceLemma)

### Phrase
Multi-word expressions and idioms
- `target_language_code`: Language code
- `canonical_form`: Standard form of the phrase
- `raw_forms`: Alternative forms (JSONField)
- `translations`: English translations (JSONField)
- `literal_translation`: Word-for-word translation
- `component_words`: Individual words in the phrase (JSONField)
- `slug`: URL-friendly version of the canonical form

## Source Content Models

### Sourcedir
Directories containing learning materials
- `path`: Directory path
- `target_language_code`: Language code
- `slug`: URL-friendly version of the path
- `description`: Description of the directory content

### Sourcefile
Individual learning materials
- `sourcedir`: Foreign key to the parent directory
- `filename`: File name
- `description`: Description of the file content
- `text_target`: Source text in target language
- `text_english`: English translation
- `sourcefile_type`: Type of source ("text", "image", "audio", "youtube_audio")
- `slug`: URL-friendly version of the filename
- Optional fields:
  - `image_data`: Original image (BlobField)
  - `audio_data`: MP3 audio (BlobField)
  - `metadata`: Additional metadata (JSONField)

## Junction Tables

### SentenceLemma
Connects sentences to lemmas
- `sentence`: Foreign key to Sentence
- `lemma`: Foreign key to Lemma

### LemmaExampleSentence
Connects lemmas to their example sentences
- `lemma`: Foreign key to Lemma
- `sentence`: Foreign key to Sentence

### PhraseExampleSentence
Connects phrases to their example sentences
- `phrase`: Foreign key to Phrase
- `sentence`: Foreign key to Sentence
- `context`: Optional context about usage

### SourcefileWordform
Maps wordforms to source files
- `sourcefile`: Foreign key to Sourcefile
- `wordform`: Foreign key to Wordform
- `centrality`: Importance of the word in the file (0-1 scale)
- `ordering`: Display order in the sourcefile

### SourcefilePhrase
Maps phrases to source files
- `sourcefile`: Foreign key to Sourcefile
- `phrase`: Foreign key to Phrase
- `centrality`: Importance of the phrase in the file (0-1 scale)
- `ordering`: Display order in the sourcefile

### RelatedPhrase
Connects related phrases
- `from_phrase`: Foreign key to source Phrase
- `to_phrase`: Foreign key to related Phrase
- `relationship_type`: Type of relationship (e.g., "similar", "opposite")

## User Management

### Profile
User profiles linked to Supabase authentication
- `user_id`: References Supabase auth.users.id
- `target_language_code`: User's preferred language