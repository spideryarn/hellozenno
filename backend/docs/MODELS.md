# Database Models

This document provides a concise overview of the main database models in HelloZenno, their key fields, and relationships.

Based on the full model declaration in `backend/db_models.py` 

see `backend/docs/DATABASE.md` for more information on connecting to the database.

## Core Models

### BaseModel
- Base class for all models with timestamps (`created_at`, `updated_at`)
- Provides `update_or_create` pattern implementation

### Lemma
Dictionary form entries for words
- Key fields:
  - `lemma` (text): Dictionary form
  - `target_language_code` (text)
  - `part_of_speech` (text)
  - `translations` (jsonb)
  - `register` (text, optional)
  - `commonality` (real, optional)
  - `guessability` (real, optional)
  - `language_level` (text, optional)
  - `is_complete` (boolean)
  - Enrichment (optional): `etymology` (text), `cultural_context` (text), `synonyms` (jsonb), `antonyms` (jsonb), `related_words_phrases_idioms` (jsonb), `mnemonics` (jsonb), `easily_confused_with` (jsonb), `example_usage` (jsonb)
  - Audit: `created_by_id` (uuid → `auth.users.id`)
  - Timestamps: `created_at`, `updated_at`
- Relationships:
  - `wordforms` (1:N via `wordform.lemma_entry_id`)
  - `example_sentences` (N:M via `lemmaexamplesentence` and `sentence`)

### LemmaAudio
Pronunciation audio for lemmas
- Key fields:
  - `lemma_id` (fk → `lemma.id`)
  - `provider` (text), `voice_name` (text)
  - `audio_data` (bytea, MP3)
  - Audit: `created_by_id` (uuid → `auth.users.id`)
  - Timestamps: `created_at`, `updated_at`

### Wordform
Individual word forms and inflections
- Key fields:
  - `wordform` (text)
  - `lemma_entry_id` (fk → `lemma.id`, optional)
  - `target_language_code` (text)
  - `part_of_speech` (text, optional)
  - `translations` (jsonb, optional)
  - `inflection_type` (text, optional)
  - `possible_misspellings` (jsonb, optional)
  - `is_lemma` (boolean)
  - Audit: `created_by_id` (uuid → `auth.users.id`)
  - Timestamps: `created_at`, `updated_at`

### Sentence
Example sentences in the target language
- Key fields:
  - `target_language_code` (text)
  - `sentence` (text)
  - `translation` (text)
  - `audio_data` (bytea, optional)
  - `slug` (text)
  - `lemma_words` (jsonb, optional)
  - `language_level` (text, optional)
  - Audit: `created_by_id` (uuid → `auth.users.id`)
  - Timestamps: `created_at`, `updated_at`
- Relationships:
  - `lemmas` (N:M via `sentencelemma`)

### Phrase
Multi-word expressions and idioms
- Key fields:
  - `target_language_code` (text)
  - `canonical_form` (text)
  - `raw_forms` (jsonb)
  - `translations` (jsonb)
  - `part_of_speech` (text)
  - `register` (text, optional)
  - `commonality` (real, optional)
  - `guessability` (real, optional)
  - `etymology` (text, optional)
  - `cultural_context` (text, optional)
  - `mnemonics` (jsonb, optional)
  - `component_words` (jsonb, optional)
  - `usage_notes` (text, optional)
  - `difficulty_level` (text, optional)
  - `slug` (text, optional)
  - `literal_translation` (text, optional)
  - `language_level` (text, optional)
  - Audit: `created_by_id` (uuid → `auth.users.id`)
  - Timestamps: `created_at`, `updated_at`

## Source Content Models

### Sourcedir
Directories containing learning materials
- Key fields:
  - `path` (text)
  - `target_language_code` (text)
  - `slug` (text)
  - `description` (text, optional)
  - Audit: `created_by_id` (uuid → `auth.users.id`)
  - Timestamps: `created_at`, `updated_at`

### Sourcefile
Individual learning materials
- Key fields:
  - `sourcedir_id` (fk → `sourcedir.id`)
  - `filename` (text)
  - `text_target` (text)
  - `text_english` (text)
  - `slug` (text)
  - `sourcefile_type` (text)
  - `metadata` (jsonb)
  - Optional: `image_data` (bytea), `audio_data` (bytea), `audio_filename` (text), `description` (text), `publication_date` (timestamp), `num_words` (int), `language_level` (text), `url` (text), `title_target` (text)
  - Flags: `ai_generated` (boolean)
  - Audit: `created_by_id` (uuid → `auth.users.id`)
  - Timestamps: `created_at`, `updated_at`

## Junction Tables

### SentenceLemma
Connects sentences to lemmas
- `sentence_id` (fk → `sentence.id`)
- `lemma_id` (fk → `lemma.id`)

### LemmaExampleSentence
Connects lemmas to their example sentences
- `lemma_id` (fk → `lemma.id`)
- `sentence_id` (fk → `sentence.id`)

### PhraseExampleSentence
Connects phrases to their example sentences
- `phrase_id` (fk → `phrase.id`)
- `sentence_id` (fk → `sentence.id`)
- `context` (text, optional)

### SourcefileWordform
Maps wordforms to source files
- `sourcefile_id` (fk → `sourcefile.id`)
- `wordform_id` (fk → `wordform.id`)
- `centrality` (real, optional)
- `ordering` (int, optional)

### SourcefilePhrase
Maps phrases to source files
- `sourcefile_id` (fk → `sourcefile.id`)
- `phrase_id` (fk → `phrase.id`)
- `centrality` (real, optional)
- `ordering` (int, optional)

### RelatedPhrase
Connects related phrases
- `from_phrase_id` (fk → `phrase.id`)
- `to_phrase_id` (fk → `phrase.id`)
- `relationship_type` (text)

## User Content and Profiles

### Profile
User profiles linked to Supabase authentication
- `user_id` (string/uuid): References Supabase `auth.users.id`
- `target_language_code` (text, optional)
- `admin_granted_at` (timestamp, optional)
- Timestamps: `created_at`, `updated_at`

### UserLemma
Maps user learning state to lemmas
- `user_id` (uuid → `auth.users.id`)
- `lemma_id` (fk → `lemma.id`)
- `ignored_dt` (timestamp, optional)
- Timestamps: `created_at`, `updated_at`

## Documents and AI

### Document
Rich content documents that can be chatted about
- Key fields:
  - `title` (text)
  - `html_content` (text)
  - `plaintext_content` (text)
  - `slug` (text, unique)
  - `language_code` (char, default 'en')
  - Optional: `created_by` (uuid → `auth.users.id`), `source_url` (text), `original_file_type` (text), `word_count` (int), `is_public` (boolean, default false), `storage_path` (text)
  - Timestamps: `created_at`, `updated_at`
- Constraints:
  - Unique: `slug`

### DocumentEnhancement
LLM-generated enhancements attached to a document
- `document_id` (fk → `documents.id`)
- `ai_call_id` (fk → `ai_calls.id`, optional)
- `type` (text), `subtype` (text, optional)
- `content` (jsonb)
- `extra` (jsonb, optional)
- Timestamps: `created_at`, `updated_at`
- Constraints: unique (`document_id`, `type`, `subtype`)

### AIModel
Registered AI models and their capabilities/costs
- `provider` (text), `model_id` (text), `version` (text)
- `display_name` (text)
- Optional: `description` (text), `context_window` (int), `max_output_tokens` (int), `supports_thinking` (boolean), `input_token_cost` (numeric), `output_token_cost` (numeric), `extra` (jsonb)
- Timestamps: `created_at`, `updated_at`
- Constraints: unique (`provider`, `model_id`, `version`)

### AICall
Recorded LLM invocations and their results
- Foreign keys: `model_id` (fk → `ai_models.id`), `document_id` (fk → `documents.id`, optional), `created_by` (uuid → `auth.users.id`, optional)
- Prompt/response: `prompt_type` (text), `prompt_template` (text, optional), `prompt_input` (text), `response_text` (text, optional), `status` (text), `finish_reason` (text, optional)
- Usage/metrics: `prompt_tokens` (int, optional), `completion_tokens` (int, optional), `total_tokens` (int, optional), `reasoning_tokens` (int, optional), `latency_ms` (int, optional), `extra` (jsonb, optional), `extra_usage` (jsonb, optional)
- Timestamps: `created_at`, `completed_at` (optional)

### ChatThread
Top-level conversation thread for a document or free-form chat
- Foreign keys: `document_id` (fk → `documents.id`, optional), `model_id` (fk → `ai_models.id`, optional), `created_by` (uuid → `auth.users.id`, optional)
- Fields: `title` (text, optional), `extra` (jsonb, optional)
- Timestamps: `created_at`, `updated_at`

### ChatMessage
Ordered messages within a chat thread
- Foreign keys: `thread_id` (fk → `chat_threads.id`), `ai_call_id` (fk → `ai_calls.id`, optional)
- Fields: `role` (text), `content` (text), `sequence_number` (int), `extra` (jsonb, optional)
- Timestamps: `created_at`
- Constraints: unique (`thread_id`, `sequence_number`)

## Internal

### MigrateHistory
Tracks executed migrations (internal bookkeeping)

### TestModel
Small table used for testing