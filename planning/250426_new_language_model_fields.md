# Implementation Plan for New Language Model Fields

This document outlines the implementation plan for new fields added in migrations 032 and 033, which add fields related to user ownership, language level, and additional metadata to various models.

## Overview of New Fields

### Migration 032 (Fields for Language Information)
- Added to **Lemma** and **Sentence**: `language_level`
- Added to **Sourcefile**: 
  - `publication_date`
  - `num_words`
  - `language_level`
  - `url`
  - `title_target`

### Migration 033 (User Reference Fields)
- Added `created_by_id` field as UUID reference to `auth.users` table for:
  - **Lemma**
  - **Wordform**
  - **Phrase**
  - **Sentence**
  - **Sourcedir**
  - **Sourcefile**

## Implementation Requirements

1. When uploading a Sourcefile from URL, store the source URL in the dedicated `url` field
2. When creating new entities (lemmas, phrases, sentences, sourcefiles, etc.), record the currently logged-in user in the `created_by_id` field
3. Count words in sourcefiles using a simple approach
4. When translating a sourcefile, also translate the title (filename) to fill the `title_target` field
5. When processing content, estimate and set the CEFR `language_level` field
6. Display all new fields in the appropriate UI components

## Detailed Implementation Plan

### 1. Backend Changes

#### 1.1 User Attribution (created_by_id)

```python
# Update _create_text_sourcefile() in sourcefile_utils.py
def _create_text_sourcefile(
    sourcedir_entry, filename, text_target, description, metadata, 
    sourcefile_type="text", created_by_id=None
):
    # Calculate word count
    num_words = count_words(text_target, sourcedir_entry.target_language_code)
    
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir_entry,
        filename=filename,
        text_target=text_target,
        text_english="",  # Initialize empty
        metadata=metadata,
        description=description,
        sourcefile_type=sourcefile_type,
        created_by_id=created_by_id,  # Set creator ID
        num_words=num_words  # Set word count
    )
    return sourcefile
```

Pass user ID from Flask's `g.user_id` to all functions that create database records:

```python
@sourcefile_api_bp.route("/<target_language_code>/<sourcedir_slug>/create_from_text", methods=["POST"])
@api_auth_required  # This sets g.user_id
def create_sourcefile_from_text_api(target_language_code, sourcedir_slug):
    # ...existing code...
    
    sourcefile = _create_text_sourcefile(
        sourcedir_entry=sourcedir_entry,
        filename=filename,
        text_target=text_target,
        description=description,
        metadata=metadata,
        sourcefile_type="text",
        created_by_id=g.user_id,  # Pass the user ID
    )
    
    # ...rest of function...
```

#### 1.2 URL Storage

Update `create_sourcefile_from_url_api` to use the dedicated URL field:

```python
@sourcefile_api_bp.route("/<target_language_code>/<sourcedir_slug>/create_from_url", methods=["POST"])
@api_auth_required
def create_sourcefile_from_url_api(target_language_code, sourcedir_slug):
    # ...existing code...
    
    url = data.get("url", "").strip()
    
    # ...fetch and process HTML...
    
    # Create sourcefile
    sourcefile = _create_text_sourcefile(...)
    
    # Set URL directly on the model instead of just in metadata
    sourcefile.url = url
    sourcefile.save()
    
    return jsonify({...})
```

DO NOT fall back to `metadata` for backward compatibility.

#### 1.3 Word Counting

Based on the discussion, we'll implement a simple word counting function that balances simplicity with accuracy:

```python
def count_words(text, language_code=None):
    """Count words in text using a simple approach.
    
    Args:
        text: The text to count words in
        language_code: Optional language code to handle special cases
    
    Returns:
        int: Approximate word count
    """
    if not text:
        return 0
    
    # Special handling for languages without spaces between words
    if language_code in ['zh', 'ja', 'th']:
        # For Chinese, Japanese, Thai - character count is a rough approximation
        # Could be replaced with specialized tokenizers if needed
        return len(text)
    
    # For most languages, splitting on whitespace works reasonably well
    # Clean text of common punctuation that might affect counts
    clean_text = text.replace(',', ' ').replace('.', ' ').replace(';', ' ')
    words = [w for w in clean_text.split() if w]
    return len(words)
```

This keeps things simple while still handling the main edge cases. We avoid adding NLTK or other complex dependencies, which aligns with the preference for simplicity. If more accurate word counting is needed in the future, this function can be enhanced.

#### 1.4 Language Level Estimation

We'll use the existing `DEFAULT_LANGUAGE_LEVEL` from config.py as the default when not provided. For estimating language levels with LLMs, add to prompt templates:

```jinja
<!-- In extract_tricky_wordforms.jinja -->
{
    "wordforms": [
        {
            "wordform": str,
            ...
            "language_level": str,  # CEFR level (A1, A2, B1, B2, C1, C2) based on word difficulty
        }
    ]
}
```

Update the Lemma metadata template as well:

```jinja
<!-- In metadata_for_lemma.jinja -->
{
    "lemma": str,
    ...
    "language_level": str,  # CEFR level (A1-C2) estimation based on word complexity, frequency, and usage
}
```

#### 1.5 Title Translation

Add functionality to translate the title during processing:

```python
def process_sourcefile(sourcefile_entry, ...):
    # After text translation is complete
    if sourcefile_entry.text_english and not sourcefile_entry.title_target:
        target_language_name = get_language_name(sourcefile_entry.sourcedir.target_language_code)
        # Use existing translation function but for the filename
        title_target, _ = translate_to_english(
            sourcefile_entry.filename, target_language_name, verbose=1
        )
        sourcefile_entry.title_target = title_target
        sourcefile_entry.save()
```

### 2. Frontend Changes

#### 2.1 Display New Fields in SourcefileHeader.svelte

Update the MetadataSection component to show the new fields:

```html
<!-- Add new fields to MetadataSection component -->
<div class="metadata-item">
  <span class="metadata-label">Language Level:</span>
  <span class="metadata-value">{sourcefile.language_level || 'Not specified'}</span>
</div>

<div class="metadata-item">
  <span class="metadata-label">Word Count:</span>
  <span class="metadata-value">{sourcefile.num_words || 'Unknown'}</span>
</div>

{#if sourcefile.created_by_id}
<div class="metadata-item">
  <span class="metadata-label">Created By:</span>
  <span class="metadata-value">{getUserEmail(sourcefile.created_by_id)}</span>
</div>
{/if}

{#if sourcefile.url}
<div class="metadata-item">
  <span class="metadata-label">Source URL:</span>
  <span class="metadata-value">
    <a href={sourcefile.url} target="_blank" rel="noopener noreferrer">{sourcefile.url}</a>
  </span>
</div>
{/if}

{#if sourcefile.title_target}
<div class="metadata-item">
  <span class="metadata-label">Original Title:</span>
  <span class="metadata-value">{sourcefile.title_target}</span>
</div>
{/if}

{#if sourcefile.publication_date}
<div class="metadata-item">
  <span class="metadata-label">Publication Date:</span>
  <span class="metadata-value">
    {new Date(sourcefile.publication_date).toLocaleDateString()}
  </span>
</div>
{/if}
```

#### 2.2 User Email Lookup Function

Add a function to get the user's email from their ID:

```javascript
async function getUserEmail(userId) {
  if (!userId) return 'Unknown';
  
  try {
    const response = await fetch(
      getApiUrl(RouteName.USER_API_GET_USER_EMAIL, { user_id: userId })
    );
    
    if (!response.ok) {
      return 'Unknown';
    }
    
    const data = await response.json();
    return data.email || 'Unknown';
  } catch (error) {
    console.error('Error fetching user email:', error);
    return 'Unknown';
  }
}
```

### 3. API Additions

#### 3.1 Get User Email by ID

Add a new API endpoint in backend/views/profile_api.py:

```python
@profile_api_bp.route("/user/<user_id>/email", methods=["GET"])
@api_auth_required
def get_user_email_api(user_id):
    """Get a user's email address by ID."""
    try:
        # Security check - require authentication
        if not g.user:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Query Supabase auth.users table
        # Implementation depends on your Supabase setup
        user_email = get_user_email_from_supabase(user_id)
        
        if not user_email:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({"email": user_email}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 4. Broader Updates to Implement the Changes

#### 4.1 Modify Functions That Create Database Objects

Update all functions that create Lemma, Wordform, Phrase, and Sentence objects to pass and set creator ID:

```python
def _store_word_in_database(
    sourcefile_entry, word_d, ordering, target_language_code, created_by_id=None
):
    """Store a wordform and its lemma in the database."""
    lemma, is_new_lemma = Lemma.update_or_create(
        lookup={...},
        updates={
            ...
            "language_level": word_d.get("language_level", DEFAULT_LANGUAGE_LEVEL),
            # Only set created_by_id for new records
            **({"created_by_id": created_by_id} if is_new_lemma and created_by_id else {})
        },
    )
    
    wordform, is_new_wordform = Wordform.update_or_create(
        lookup={...},
        updates={
            ...
            # Only set created_by_id for new records
            **({"created_by_id": created_by_id} if is_new_wordform and created_by_id else {})
        },
    )
    
    # ...rest of function...
```

#### 4.2 Update Process Functions to Pass Creator ID

```python
def ensure_tricky_wordforms(
    sourcefile_entry, language_level, max_new_words, created_by_id=None
):
    # ...existing code...
    
    for word_counter, word_d in enumerate(new_wordforms):
        wordform, lemma, _ = _store_word_in_database(
            sourcefile_entry,
            word_d,
            len(existing_wordforms) + word_counter + 1,
            target_language_code,
            created_by_id=created_by_id,  # Pass the creator ID
        )
```

```python
def process_sourcefile(
    sourcefile_entry, language_level, max_new_words, max_new_phrases, 
    verbose=0, created_by_id=None
):
    # ...extraction and translation...
    
    # Set language level on sourcefile if not already set
    if not sourcefile_entry.language_level:
        sourcefile_entry.language_level = language_level
        sourcefile_entry.save()
    
    # Run extractions with creator ID
    ensure_tricky_wordforms(
        sourcefile_entry,
        language_level=language_level,
        max_new_words=max_new_words,
        created_by_id=created_by_id,
    )
    
    ensure_tricky_phrases(
        sourcefile_entry,
        language_level=language_level,
        max_new_phrases=max_new_phrases,
        verbose=verbose,
        created_by_id=created_by_id,
    )
```

#### 4.3 Update API Endpoints to Pass User ID

```python
@sourcefile_api_bp.route("/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process", methods=["POST"])
@api_auth_required
def process_sourcefile_api(target_language_code, sourcedir_slug, sourcefile_slug):
    # ...existing code...
    
    process_sourcefile(
        sourcefile_entry,
        language_level=language_level,
        max_new_words=max_new_words,
        max_new_phrases=max_new_phrases,
        created_by_id=g.user_id,  # Pass the user ID
    )
    
    # ...rest of function...
```

## Edge Cases and Considerations

### 1. Handling Existing Records

All code should handle null values for new fields, as existing records won't have them set.

### 2. Word Counting for Different Languages

We've chosen a simple approach that works well for most languages, with special handling for languages without word spacing. This balances simplicity with reasonable accuracy.

### 3. Authentication in Optional Routes

For routes with `@api_auth_optional`, we should check if `g.user_id` exists before using it:

```python
created_by_id = getattr(g, 'user_id', None)
```


## Documentation Update

Update backend/docs/MODELS.md with information about the new fields:

```markdown
### BaseModel
- `created_at`, `updated_at`: Timestamps for creation and last update

### Lemma
- `language_level`: CEFR level estimation (A1, A2, B1, B2, C1, C2)
- `created_by_id`: Reference to auth.users who created the entry

### Sentence
- `language_level`: CEFR level estimation (A1-C2)
- `created_by_id`: Reference to auth.users who created the sentence

### Sourcefile
- `publication_date`: Original publication date when known
- `num_words`: Count of words in the text content
- `language_level`: CEFR level estimation (A1-C2)
- `url`: Original source URL if imported from web
- `title_target`: Translation of the filename/title to target language
- `created_by_id`: Reference to auth.users who created the file

## User Attribution

Many models now have a `created_by_id` field referencing the Supabase `auth.users` table:
- Used to track which user created each record
- When displaying, the user's email address is typically shown
- Enables future features like:
  - User contributions tracking
  - Content filtering by creator
  - Permission management
```

## Implementation Strategy

The implementation can be done in phases:

1. First update function signatures and models to support the new fields
2. Add the word counting and user ID tracking
3. Implement URL field usage and title translation
4. Update the UI to display the new information
5. Add language level estimation last (most complex)

This phased approach allows for testing at each step.