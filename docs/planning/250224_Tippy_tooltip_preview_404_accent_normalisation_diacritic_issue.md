# Greek Diacritics Issue in Word Preview API

## Goal & Context

Investigate and fix the 404 error when hovering over the Greek word "τροφή" (food) to display a tooltip preview. The error occurs at:

```
Error fetching preview for "τροφή": Error: API request failed: 404
    at base.js:102:31
```

This happens on the page at `https://hz-app-web.fly.dev/el/250216-iliad-book-1/screenshot-2025-02-17-at-01-36-48-png` when hovering over "τροφή" within the text.

The issue appears to be related to character encoding or diacritic normalization when the tooltip system tries to fetch data from the API endpoint.

## Principles

- Understand the root cause before implementing a fix
- Ensure any fix maintains compatibility with existing data
- Follow the guidance in PROJECT_MANAGEMENT.md

## Current Findings

1. **Database state:**
   - The word "τροφή" exists in the database (ID 66)
   - Direct database query by ID works, but exact match query fails:
     - `SELECT * FROM wordform WHERE id = 66` ✅
     - `SELECT * FROM wordform WHERE wordform = 'τροφή'` ❌

2. **API behavior:**
   - API endpoint returns 404 for both direct and URL-encoded versions:
     - `curl -s "https://hz-app-web.fly.dev/api/word-preview/el/τροφή"` ❌
     - `curl -s "https://hz-app-web.fly.dev/api/word-preview/el/%CF%84%CF%81%CE%BF%CF%86%CE%AE"` ❌
   - Other accented Greek words like "θυμό" work correctly

3. **Normalization differences:**
   - Unicode normalization removes accents:
     - "τροφή" → "τροφη"
     - "θυμό" → "θυμο"
   - But only "θυμό" works in the API, not "τροφή"

4. **Character encoding:**
   - Database hex encoding: `cf84cf81cebfcf86ceb7cc81`
   - Python hex representation: `3c43c13bf3c63ae`
   - Suggests difference in how the accented 'ή' character is encoded

5. **Code review findings:**
   - **Two normalization paths:**
     - **Creating links:** In `vocab_llm_utils.py`, words are normalized using `normalize_text()` to match normalized wordform database entries, then displayed with their original diacritics in the HTML links
     - **Tooltip lookup:** In `base.js`, when a tooltip is triggered, it uses the raw text from the link (with diacritics) for the API call
     - **API word lookup:** In `word_utils.py`, `get_word_preview()` tries three approaches:
       1. Exact match (with diacritics)
       2. Case-insensitive match (still with diacritics)
       3. Normalized match (removing diacritics using `normalize_text()`)
  
   - **Critical issue:** The exact match and case-insensitive match SQL queries are failing for "τροφή" but work for "θυμό". This suggests that the specific character "ή" (eta with tonos) in "τροφή" might be stored in the database using a different Unicode representation than what's being sent in the API request.

   - **Greek characters with multiple equivalent forms:**
     - Greek characters with diacritics can be represented in multiple Unicode forms
     - Some characters like "ή" might be stored in composed form (single code point) vs. decomposed form (base character + combining mark)
     - PostgreSQL collation rules may handle these differently than Python's Unicode handling

6. **Root cause identified:**
   - **Inconsistent Unicode normalization forms:**
     - The word "τροφή" is stored in the database in Normalization Form D (NFD):
       - NFD representation: `τ ρ ο φ η ´` (6 characters, with separate combining accent)
       - PostgreSQL hex: `cf84cf81cebfcf86ceb7cc81`
     - The word "θυμό" is stored in Normalization Form C (NFC):
       - NFC representation: `θ υ μ ό` (4 characters, with accent as part of the letter)
     - The API lookup in `get_word_preview()` is using the form that's provided in the request,
       which might be different from what's stored
   - The differences in Unicode normalization forms:
     ```
     τροφή (NFC): [0x3c4, 0x3c1, 0x3bf, 0x3c6, 0x3ae]  (5 characters)
     τροφή (NFD): [0x3c4, 0x3c1, 0x3bf, 0x3c6, 0x3b7, 0x301]  (6 characters)
     ```
   - The third lookup in `get_word_preview()` using `normalize_text()` works correctly because 
     it removes diacritics entirely, making the normalization form differences irrelevant

## Solution: Unicode Normalization Standardization

After careful consideration of the trade-offs between different Unicode normalization forms, we've decided to standardize on **NFC (Normalization Form C)** for the following reasons:

1. **Industry Standard**: NFC is more widely used as the default in most systems
2. **Performance**: NFC is more efficient as it uses fewer code points (5 vs 6 for "τροφή")
3. **Storage**: NFC requires less storage space
4. **Compatibility**: Better compatibility with web frameworks and databases
5. **User Input**: Most systems and user input methods produce NFC by default

Rather than using a temporary fix that handles both forms, we're implementing a comprehensive solution:

1. **Database Consistency**: Create a migration to convert all wordforms to NFC
2. **Input Sanitization**: Normalize all incoming words to NFC before processing
3. **Storage Guarantees**: Update the Wordform model to ensure NFC normalization on save
4. **Testing**: Add tests specifically for Unicode normalization forms

### Implementation Details

1. **New Utility Function**: Add `ensure_nfc()` to standardize text normalization:
   ```python
   def ensure_nfc(text: str) -> str:
       """Ensure text is in NFC (Normalization Form C) for consistent handling."""
       return unicodedata.normalize("NFC", text)
   ```

2. **Update Word Preview Lookup**: Normalize input words to NFC before lookup:
   ```python
   def get_word_preview(target_language_code: str, word: str) -> WordPreview | None:
       # Ensure consistent NFC normalization for lookups
       word = ensure_nfc(word)
       # ... existing lookup logic ...
   ```

3. **Database Model Safeguard**: Ensure all new wordforms are saved in NFC:
   ```python
   def save(self, *args, **kwargs):
       """Override save to ensure wordform is in NFC form."""
       if self.wordform is not None:
           self.wordform = unicodedata.normalize("NFC", str(self.wordform))
       return super().save(*args, **kwargs)
   ```

4. **Migration**: Create a migration to standardize existing data:
   ```python
   def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
       """Standardize all wordforms to NFC normalization."""
       Wordform = migrator.orm['wordform']
       
       for wf in Wordform.select():
           if wf.wordform is not None:
               nfc_form = unicodedata.normalize("NFC", wf.wordform)
               if nfc_form != wf.wordform:
                   wf.wordform = nfc_form
                   wf.save()
   ```

5. **Vocabulary Processing**: Update HTML link generation to use NFC:
   ```python
   def replace_match(match):
       word = match.group(0)
       word = ensure_nfc(word)  # Normalize to NFC first
       # ... rest of matching logic
   ```

6. **Testing**: Add specific tests for Unicode normalization handling:
   ```python
   def test_unicode_normalization(db):
       # Test both NFD and NFC forms of Greek words
       # Verify normalization behavior matches expectations
       # Simulate migration and verify both forms work after standardization
   ```

## Actions

### DONE: Identify root cause of the issue
- ✅ Discovered inconsistency in Unicode normalization forms (NFC vs NFD)
- ✅ Found that "τροφή" is stored in NFD while "θυμό" is in NFC
- ✅ Verified that the lookup method does not account for different normalization forms

### DONE: Decide between NFC and NFD standardization
- ✅ Evaluated trade-offs between NFC and NFD
- ✅ Selected NFC as the standard for better performance, compatibility, and maintainability
- ✅ Created utility function for consistent normalization

### DONE: Implement comprehensive NFC standardization
- ✅ Added NFC normalization to input processing (get_word_preview)
- ✅ Created migration to update all existing wordforms to NFC
- ✅ Added safeguard in Wordform.save() to maintain NFC on all new entries
- ✅ Updated vocabulary processing to use NFC consistently
- ✅ Added tests for Unicode normalization handling

### TODO: Test and deploy the fix
- Run the migration in production environment
- Verify the fix works for all Greek diacritics, not just "ή"
- Monitor for any regressions or other issues

### TODO: Document the solution
- Add documentation about Unicode normalization standards
- Update developer onboarding to explain NFC standardization
- Consider creating a pre-commit hook to verify NFC normalization in new code
