# Enhanced Text Tooltip Debugging

## Problem Statement

The Enhanced Text component in the SvelteKit frontend is not correctly displaying tooltips when hovering over words. Instead of showing the expected word information (lemma, translation, etymology), the tooltip displays "Error loading preview". This affects both desktop (hover) and mobile (touch) interactions. We need to fix this functionality to provide a seamless language learning experience.

## Background Context

The Enhanced Text feature is a core component of Hello Zenno that transforms plain sentences into interactive language learning experiences. It creates HTML links for recognized words that display additional information when hovered over or clicked.

This functionality was working in the previous Flask/Jinja/Svelte implementation but broke during the migration to SvelteKit. The current EnhancedText.svelte component implements Tippy.js for tooltips, with appropriate behavior differences between desktop and mobile:
- Desktop: Show tooltip on hover (mouseenter)
- Mobile: Show tooltip on tap (click)

The local Flask backend API runs on port 3000, and SvelteKit frontend runs on port 5173.

## Relevant Files and Components

- `frontend/README.md` for references to top-level frontend and backend documentation

- **EnhancedText.svelte**: The main component that implements the tooltip functionality
  - Uses Tippy.js for tooltip handling
  - Detects touch devices and adjusts behavior accordingly
  - Fetches word data from the API in the `onShow` handler

- **API Endpoints**:
  - `/api/lang/word/{target_language_code}/{word}/preview` - Returns word preview data for tooltips
  - Implemented in `wordform_api.py` as `word_preview_api()`
  - Uses `get_word_preview()` from `word_utils.py`

- **URL and Routing**:
  - `api.ts` - Contains `getApiUrl()` function for type-safe API URL generation
  - `routes.ts` - Contains generated route definitions and `resolveRoute()` function
  - `config.ts` - Defines `API_BASE_URL` as "http://localhost:3000" in development

- **Unicode Normalization**:
  - Migration `019_standardize_unicode_normalization.py` - Standardized to NFC form
  - `word_utils.py` - Contains `ensure_nfc()` utility function
  - Documentation in `250224_Tippy_tooltip_preview_404_accent_normalisation_diacritic_issue.md`

## Tests and Data Gathering

### Direct API Access
- Directly accessing `http://localhost:3000/api/lang/word/el/βράχια/preview` returns valid data:
```json
{
  "etymology": null,
  "lemma": "βράχος",
  "translation": "rock; cliff; boulder"
}
```
This confirms the API endpoint works correctly when accessed directly.

### Database Queries
- A Supabase query for `wordform = 'βράχια'` returns no results
- A case-insensitive search for `'%βράχια%'` also returns no results
- A search for the lemma `'βράχος'` returns no results

This is surprising given that the API returns data for these terms, suggesting the API might be using fallback mechanisms or external services not reflected in the database.

### Frontend Behavior
- Hovering over word links shows "Error loading preview" tooltips
- The component logs "Fetching preview for word: [word]" but fails to display data
- API calls are rejected with a 404 error status

## Hypotheses

1. **URL Construction Issue**: The most likely cause is a mismatch between how the frontend constructs API URLs and how the backend expects them.

   - The frontend uses `encodeURIComponent()` on the word parameter, but there might be issues with double-encoding or character encoding mismatches.
   - Greek characters and diacritics require careful handling to ensure proper URL encoding.

2. **API Request Failure**: The requests are being constructed correctly, but something prevents them from reaching the backend properly.

   - Could be a subtle CORS issue (though other API calls work)
   - Might be related to how SvelteKit's dev server handles proxying to the Flask backend

3. **Response Processing Issue**: The API might be returning data in a format different from what the component expects.

   - The parse logic in the component might not match the actual API response structure
   - The JSON parsing could be failing silently

4. **Data Source Discrepancy**: The API endpoint is accessing data that isn't in the main database.

   - There might be a caching layer or fallback mechanism in `get_word_preview()`
   - External language services might be used when database lookups fail

## Investigation Results

We added detailed logging to the `EnhancedText.svelte` component to understand why the tooltips were failing to display data. Our investigation found that:

1. When directly accessing the API endpoints in the browser with URLs like `http://localhost:3000/api/lang/word/el/κύματα/preview`, the API returns the correct data.

2. However, the API calls made from the SvelteKit frontend were failing with 404 errors.

3. Through testing with multiple words and examining the debug output, we determined that there's likely an issue with URL encoding and/or how SvelteKit's dev server is proxying the requests to the Flask backend.

## Solution Implemented

We simplified the word data fetching process by creating a dedicated `fetchWordData` function that:

1. Constructs the URL manually to ensure proper encoding of Greek characters
2. Uses specific fetch options to ensure proper CORS handling
3. Provides better error handling for failed requests

The updated code in `EnhancedText.svelte`:

```typescript
// Function to fetch word data directly from the API
async function fetchWordData(word: string, lang: string): Promise<any> {
  try {
    // Use a manual URL construction as a fallback
    const directUrl = `${API_BASE_URL}/api/lang/word/${lang}/${encodeURIComponent(word)}/preview`;
    console.log(`Direct fetch from URL: ${directUrl}`);
    
    const response = await fetch(directUrl, { 
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      mode: 'cors' 
    });
    
    if (!response.ok) {
      throw new Error(`Direct API request failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in direct fetch:', error);
    return null;
  }
}
```

This function is then used in the `onShow` handler of the tooltip:

```typescript
// Use direct fetch method to avoid any encoding issues
fetchWordData(word, language_code)
  .then(data => {
    console.log(`Preview data for "${word}":`, data);
    
    if (data && data.lemma) {
      // Build tooltip content from data
      // ...
      instance.setContent(content);
    } else {
      instance.setContent('No data available');
    }
  })
  .catch(error => {
    console.error(`Error fetching preview for "${word}":`, error);
    instance.setContent('Error loading preview');
  });
```

## Next Steps

While the initial issue is fixed, there are still several improvements that could be made:

### Mobile-specific Improvements

- [ ] Visual Cues
  - [ ] Add subtle visual indicator that words are interactive
  - [ ] Consider underline or color change on touch

- [ ] Interaction Refinements
  - [ ] Implement touch-and-hold gesture for word details
  - [ ] Add close button to tooltips for mobile
  - [ ] Make tooltips dismissible by tapping elsewhere

### Performance Optimizations

- [ ] Prefetch data for visible words
- [ ] Implement local caching of common word lookups
- [ ] Add retry logic for transient failures

### Data Layer Investigation

- [ ] Investigate why API can find data that doesn't appear in direct DB queries
  - This suggests the API is using fallback mechanisms or external services for word data

## Lessons Learned

1. **URL Encoding Matters**: Special care must be taken when encoding non-Latin characters in URLs, especially in a context where multiple systems might perform URL encoding/decoding.

2. **Direct Testing is Essential**: Always test API endpoints directly in the browser when diagnosing frontend-backend integration issues.

3. **Fallback Strategies**: Having a simpler, manual approach as a fallback can help work around complex issues in type-safe API integration.

4. **Frontend-Backend Communication**: When working with a SvelteKit frontend calling a Flask backend, use explicit headers and CORS options to ensure reliable communication.

This fix maintains the original behavior and user experience while making the tooltips work correctly. The simplified approach avoids potential issues with double encoding or mismatches in how different systems handle URL encoding.