# Add Sentence Slug View

## Goal Statement
Add a dedicated view for individual sentences using URL slugs, similar to the phrase view structure, i.e. use the slug in the user-facing URL, but otherwise prefer to use the primary key for querying/identifying Sentences. Follow the sourcefile UI, e.g. for rename buttons, audio player. But get the simplest thing working first. This will enable direct linking to sentences and provide a foundation for sentence-specific features.

## Current Status
- Sentence model has slug field added
- Basic view and template implemented
- Added action buttons and audio player
- Added API endpoints for sentence management
- Added tests for all functionality

## Tasks

### Stage 1: Basic View Implementation (v1)
DONE:
1. Create new route in sentence_views.py:
   - URL pattern: `/<language_code>/sentence/<slug>`
   - Get sentence by slug and language_code
   - Return 404 if not found
   - Pass sentence data to template

2. Create sentence.jinja template:
   - Extend base.jinja
   - Add breadcrumbs: Home » Languages » [Language] » Sentences » [Sentence]
   - Display sentence text, translation, lemma words
   - Add audio player if audio_data exists

3. Add link to sentence view in sentences.jinja:
   - Update sentence list to link each sentence to its dedicated view

4. Add tests in test_sentence_views.py:
   - Test successful retrieval using slug
   - Test 404 for non-existent slug
   - Test correct language code
   - Test wrong language code
   - Test with and without audio data

5. Add action buttons and API endpoints:
   - Delete sentence
   - Generate/regenerate audio
   - Edit sentence/translation
   - Add JavaScript functionality for audio playback and actions

### Stage 2: Enhanced Features (Next)
TODO:
1. Add word linking:
   - Make words in sentence clickable
   - Make words in "Words" section clickable
   - Show word definitions on hover (like in Sourcefile)
   - Link to word detail pages (probably to the lemma pages, right?)


## Acceptance Criteria
DONE:
- Can access individual sentences via slug URLs
- 404 returned for invalid slugs/language codes
- Audio plays if available
- All tests pass
- Links from sentence list work correctly
- Breadcrumb navigation works
- Can edit sentence text
- Can delete sentences
- Can generate audio


## Notes
- Following URL structure pattern from phrase_views.py
- Using UI patterns from sourcefile.jinja
- Stage 1 complete with basic functionality
- Moving on to enhanced features in Stage 2
