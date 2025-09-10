# Speeding Up Sourcefile Pages

## Problem Identified

Sourcefile pages, especially those with many words, have been loading very slowly in production (often taking 5-6+ seconds). This was particularly noticeable on pages with 50+ words.

## Investigation

### Methodology

We used timing measurements on various API endpoints to identify where the bottlenecks occur:

```bash
curl -s -w "\nTime to connect: %{time_connect}s\nTime to first byte: %{time_starttransfer}s\nTotal time: %{time_total}s\n" "https://api.hellozenno.com/api/lang/sourcefile/el/250309-jason-ch-11/1000011000-jpg"
```

### Results

| API Endpoint | Time to First Byte | Total Time |
|--------------|-------------------|------------|
| Basic Sourcefile Info | 1.66s | 1.67s |
| Words List | 1.59s | 1.60s |
| Phrases List | 1.69s | 1.69s |

### Analysis

1. **High Baseline Latency**: Each API call has a consistent ~1.6s latency regardless of data size, suggesting a connection/setup overhead rather than data volume problem.

2. **Multiple API Calls**: Each tab (e.g., the Words tab) makes multiple API calls:
   - Basic sourcefile info: `/api/lang/sourcefile/...`
   - Text data: `/api/lang/sourcefile/.../text`
   - Tab-specific data: `/api/lang/sourcefile/.../words`

3. **Redundant Data Loading**: The current implementation loads all data (words, phrases, enhanced text) for almost every API call through `get_sourcefile_details()`, regardless of what's actually needed.

4. **Compounding Latency**: With 3+ API calls per page, each incurring ~1.6s latency, the total page load time easily exceeds 5 seconds.

5. **Database Connection Costs**: The consistent high latency across different endpoints suggests each database connection incurs significant overhead in production.

## Current Data Flow

Below is a diagram of the current data flow when loading a sourcefile page (e.g., Words tab):

```
Frontend                                  Backend                               Database
(SvelteKit)                             (Flask API)                            (PostgreSQL)
    |                                        |                                       |
    |--- User visits words tab ----------→   |                                       |
    |                                        |                                       |
    |--- Load words/+page.server.ts ----→   |                                       |
    |                                        |                                       |
    |--- Fetch basic sourcefile info ---→   |                                       |
    |                                     inspect_sourcefile_api                     |
    |                                        |--- get_sourcefile_details() -----→   |
    |                                        |      |                                |
    |                                        |      |--- _get_navigation_info() -→   |
    |                                        |      |                                |
    |                                        |      |--- _get_wordforms_data() --→   |
    |                                        |      |                                |
    |                                        |      |--- _get_phrases_data() ----→   |
    |                                        |      |                                |
    |                                        |      |--- create_interactive_word_links() |
    |                                        |                                       |
    |←-- Return basic data ----------------|                                       |
    |                                        |                                       |
    |--- Fetch text data ---------------→   |                                       |
    |                                     inspect_sourcefile_text_api                |
    |                                        |--- get_sourcefile_details() -----→   |
    |                                        |      | [Repeat similar DB queries]    |
    |                                        |                                       |
    |←-- Return text data ----------------|                                       |
    |                                        |                                       |
    |--- Fetch words data --------------→   |                                       |
    |                                     inspect_sourcefile_words_api               |
    |                                        |--- get_sourcefile_details() -----→   |
    |                                        |      | [Repeat similar DB queries]    |
    |                                        |                                       |
    |←-- Return words data ---------------|                                       |
    |                                        |                                       |
    |--- Render the words tab using data-    |                                       |
```

## Solution

### Approach

1. **Selective Data Loading**: Modify `get_sourcefile_details()` to only fetch the data needed for a specific purpose.

2. **Purpose-Based API Endpoints**: Keep separate endpoints for each tab, but make them fetch only what they need.

3. **Single API Call Per Tab**: Update frontend to make a single API call per tab, eliminating redundant requests.

### Implementation Details

#### 1. Modify `get_sourcefile_details()` in `backend/utils/sourcefile_utils.py`:

```python
def get_sourcefile_details(
    sourcefile_entry: Sourcefile, 
    target_language_code: str,
    purpose="basic"  # "basic", "text", "words", "phrases", or "translation"
):
    """Get details for a sourcefile based on the specific purpose needed.
    
    Args:
        sourcefile_entry: The Sourcefile object
        target_language_code: The language code
        purpose: What the data will be used for
        
    Returns:
        A dictionary with the data needed for the specified purpose
    """
    # ... implementation with purpose-specific loading
```

The function should:
- Always load basic data (navigation, metadata, counts)
- Load text content for "text" and "translation" purposes
- Generate enhanced text only for "text" purpose (needs wordforms)
- Load wordforms only for "words" or "text" purposes (text tab needs wordforms for enhanced text)
- Load phrases only for "phrases" purpose

#### 2. Update API Endpoints in `backend/views/sourcefile_api.py`:

Update these functions to use the purpose parameter:
- `inspect_sourcefile_api`: purpose="basic"
- `inspect_sourcefile_text_api`: purpose="text"
- `inspect_sourcefile_words_api`: purpose="words"
- `inspect_sourcefile_phrases_api`: purpose="phrases"
- (Add if missing) `inspect_sourcefile_translation_api`: purpose="translation" or purpose="basic"

#### 3. Update Frontend Components:

Each tab's server component (`+page.server.ts`) should be modified to make only a single API call:

- **Words Tab** (`frontend/src/routes/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/words/+page.server.ts`):
  - Only call `inspect_sourcefile_words_api`
  - Format the response to match what `SourcefileWords.svelte` expects

- **Text Tab** (`frontend/src/routes/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text/+page.server.ts`):
  - Only call `inspect_sourcefile_text_api` (which now returns words data for enhanced text)
  - Format the response to match what `SourcefileText.svelte` expects

- **Phrases Tab** (`frontend/src/routes/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/phrases/+page.server.ts`):
  - Only call `inspect_sourcefile_phrases_api`
  - Format the response to match what `SourcefilePhrases.svelte` expects

### Purpose-Specific Data Requirements

| Purpose | Basic Info | Text Content | Enhanced Text | Wordforms | Phrases |
|---------|------------|--------------|--------------|-----------|---------|
| basic | ✅ | ❌ | ❌ | ❌ | ❌ |
| text | ✅ | ✅ | ✅ | ✅* | ❌ |
| words | ✅ | ❌ | ❌ | ✅ | ❌ |
| phrases | ✅ | ❌ | ❌ | ❌ | ✅ |
| translation | ✅ | ✅ | ❌ | ❌ | ❌ |

*Wordforms are needed for text tab to generate enhanced text with clickable word links - see `frontend/docs/ENHANCED_TEXT.md`.

### Optimized Data Flow

After these changes, the data flow for loading the words tab will be:

```
Frontend                                  Backend                               Database
(SvelteKit)                             (Flask API)                            (PostgreSQL)
    |                                        |                                       |
    |--- User visits words tab ----------→   |                                       |
    |                                        |                                       |
    |--- Load words/+page.server.ts ----→   |                                       |
    |                                        |                                       |
    |--- Fetch words data only ----------→   |                                       |
    |                                     inspect_sourcefile_words_api               |
    |                                        |--- get_sourcefile_details() -----→   |
    |                                        |      | purpose="words"                |
    |                                        |      |                                |
    |                                        |      |--- _get_navigation_info() -→   |
    |                                        |      |                              Sourcedir
    |                                        |      |←-- Return navigation info --   |
    |                                        |      |                                |
    |                                        |      |--- Get wordforms counts ---→   |
    |                                        |      |                            SourcefileWordform
    |                                        |      |←-- Return counts ----------   |
    |                                        |      |                                |
    |                                        |      |--- Get phrases counts ----→   |
    |                                        |      |                            SourcefilePhrase
    |                                        |      |←-- Return counts ----------   |
    |                                        |      |                                |
    |                                        |      |--- _get_wordforms_data() --→   |
    |                                        |      |                            Wordform,SourcefileWordform
    |                                        |      |←-- Return all wordforms ----   |
    |                                        |                                       |
    |←-- Return all necessary data ---------|                                       |
    |                                        |                                       |
    |--- Render the words tab using data-    |                                       |
```

## Key Files and Functions

### Backend

- **`backend/utils/sourcefile_utils.py`**:
  - `get_sourcefile_details()`: The central function that needs to be modified to support purpose-based loading
  - `_get_sourcefile_entry()`: Helper function to retrieve sourcefile entries

- **`backend/views/sourcefile_api.py`**:
  - `inspect_sourcefile_api()`: Basic info endpoint
  - `inspect_sourcefile_text_api()`: Text tab endpoint
  - `inspect_sourcefile_words_api()`: Words tab endpoint
  - `inspect_sourcefile_phrases_api()`: Phrases tab endpoint
  - (May need to add) `inspect_sourcefile_translation_api()`: Translation tab endpoint

- **`utils/vocab_llm_utils.py`**:
  - `create_interactive_word_links()`: Generates enhanced text with clickable links

### Frontend

- **`frontend/src/routes/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/`**:
  - `text/+page.server.ts`: Text tab server component
  - `words/+page.server.ts`: Words tab server component
  - `phrases/+page.server.ts`: Phrases tab server component
  - `translation/+page.server.ts`: Translation tab server component
  - `components/SourcefileText.svelte`: Text tab component
  - `components/SourcefileWords.svelte`: Words tab component
  - `components/SourcefilePhrases.svelte`: Phrases tab component
  - `components/SourcefileTranslation.svelte`: Translation tab component

## Special Considerations

1. **Enhanced Text Generation**: The text tab needs access to wordforms data to generate enhanced text with clickable links. See `frontend/docs/ENHANCED_TEXT.md` for detailed information on how enhanced text works.

2. **Tab Navigation**: All tabs need access to the word/phrase counts for displaying the tab navigation, so this data should always be included.

3. **Translation Tab**: For the translation tab, we can use the "basic" purpose with the addition of retrieving text content. No need for enhanced text or wordforms.

4. **WordformCard Component**: Make sure the frontpage still gets all the data it needs for the `WordformCard` component imported in `SourcefileWords.svelte`.

## Testing Plan

1. Benchmark API endpoints before and after changes:
   ```bash
   curl -s -w "\nTime to connect: %{time_connect}s\nTime to first byte: %{time_starttransfer}s\nTotal time: %{time_total}s\n" "https://api.hellozenno.com/api/lang/sourcefile/el/250309-jason-ch-11/1000011000-jpg/words"
   ```

2. Verify all tab functionality in development:
   - Text tab: Check that enhanced text works correctly with word links
   - Words tab: Ensure all wordforms are displayed correctly
   - Phrases tab: Confirm phrases are displayed
   - Translation tab: Verify text & translation content is shown

3. Measure page load performance in browser dev tools:
   - Network tab timing for API calls
   - Overall page load time

4. Compare production performance after deployment

## Expected Benefits

1. **Dramatic Page Load Improvement**: Reduce page load time from ~5-6s to ~1.7s (the baseline latency of a single API call)
2. **Reduced Server Load**: Eliminate redundant database queries and processing
3. **Simplified Frontend Logic**: Each tab makes exactly one API call
4. **Better User Experience**: Faster page loads lead to better user engagement

## Future Considerations

1. **Database Query Optimizations**: Further optimize database queries for wordforms and phrases
2. **Caching Strategies**: Implement server-side caching for frequently accessed sourcefiles
3. **Pagination**: Add pagination for sourcefiles with very large numbers of words/phrases
4. **Lazy Loading**: Consider lazy loading components for tabs not initially visible
5. **API Response Compression**: Implement gzip/brotli compression for API responses

## References

- [SOURCEFILE_PAGES.md](../frontend/docs/SOURCEFILE_PAGES.md) - Overview of sourcefile page structure
- [ENHANCED_TEXT.md](../frontend/docs/ENHANCED_TEXT.md) - Details on enhanced text implementation
- [FRONTEND_DEBUGGING.md](../frontend/docs/FRONTEND_DEBUGGING.md) - Tools for debugging frontend issues
