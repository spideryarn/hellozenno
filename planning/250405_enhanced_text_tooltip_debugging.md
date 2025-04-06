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

### Initial Debugging and First Fix

Our initial diagnosis revealed several issues:

1. Missing `language_code` propagation through component hierarchy
2. References to undefined variables (`lang` instead of `language_code`)
3. Potential issues with URL construction and encoding
4. Limited error handling and debugging information

We implemented a more robust word data fetching process with dedicated `fetchWordData` function that:

1. Constructs the URL manually to ensure proper encoding of Greek characters
2. Uses specific fetch options to ensure proper CORS handling
3. Provides better error handling for failed requests
4. Adds detailed logging for debugging

The initial fixed version:

```typescript
// Function to fetch word data directly from the API
async function fetchWordData(word: string, lang: string): Promise<any> {
  return new Promise((resolve, reject) => {
    console.log(`EnhancedText Debug:`);
    console.log(`- API_BASE_URL: ${API_BASE_URL}`);
    console.log(`- Language Code: ${lang}`);
    console.log(`- Word to fetch: "${word}"`);
    
    // IMPORTANT: Check if we have a valid language code
    if (!lang) {
      console.error(`- ERROR: Missing language code. This is required for API calls.`);
      reject(new Error('Missing language code'));
      return;
    }
    
    // Use the direct manual URL that we know works in the browser
    const encodedWord = encodeURIComponent(word);
    const url = `${API_BASE_URL}/api/lang/word/${lang}/${encodedWord}/preview`;
    console.log(`- Using URL: ${url}`);
    
    // Try direct fetch with appropriate CORS settings
    fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      mode: 'cors'
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error(`Fetch API test failed with status: ${response.status}`);
      }
    })
    .then(data => {
      console.log(`- Direct fetch API test succeeded:`, data);
      resolve(data);
    })
    .catch(error => {
      console.error(`- Direct fetch API test failed:`, error);
      // Fallback mechanism with XMLHttpRequest if needed
      // ...
    });
  }).catch(error => {
    console.error('Error in all fetch attempts:', error);
    // Provide a fallback result
    return {
      lemma: word,
      translation: "(translation not available)",
      etymology: null
    };
  });
}
```

### Critical Bug Fix: Reference Error

After deploying the initial fix, we encountered a `ReferenceError: lang is not defined` error. This occurred because there were still references to the undefined variable `lang` in the tooltip rendering code:

```typescript
// Error locations:
const wordApiUrl = `${API_BASE_URL}/api/lang/word/${lang}/${encodeURIComponent(word)}/preview`;

// In debug info sections:
API: ${API_BASE_URL}/api/lang/word/${lang}/${encodeURIComponent(word)}/preview
```

We fixed these references by replacing all instances of `lang` with the correct `language_code` prop, and added detailed logging to track the component lifecycle.

### Type-Safe URL Integration

After fixing the immediate issues, we enhanced the component to use the type-safe URL generation machinery from `routes.ts`. This approach:

1. Aligns with the app's URL management strategy
2. Provides type safety for API endpoints
3. Centralizes URL structure definitions
4. Ensures consistent parameter encoding

The updated implementation now:
- Generates both direct and type-safe URLs for comparison
- Displays both URLs in debug tooltips
- Shows whether the URLs match
- Uses the type-safe URL approach for all API calls

```typescript
// Generate a type-safe URL using the routes.ts machinery
const typeSafeUrl = getApiUrl(RouteName.WORDFORM_API_WORD_PREVIEW_API, { 
  target_language_code: language_code, 
  word: word
});

// Sample debug output in tooltips:
<div class="debug-info">
  <strong>URLs:</strong><br>
  <span style="opacity: 0.7;">Direct: ${API_BASE_URL}/api/lang/word/${language_code}/${encodeURIComponent(word)}/preview</span><br>
  <span style="font-weight: bold;">Type-safe: ${data._debug?.typeSafeUrl || 'N/A'}</span> ← Using this<br>
  <strong>URL Match:</strong> ${data._debug?.directUrl === data._debug?.typeSafeUrl ? 'Yes ✓' : 'No ✗'}<br>
  <strong>Details:</strong><br>
  Language code: ${language_code}<br>
  Word: ${word}
</div>
```

Our testing confirmed that both URL construction methods produce identical results, giving us confidence to standardize on the type-safe approach.

### Comprehensive Error Handling

The final implementation includes robust error handling at multiple levels:

1. **Input Validation**: Checks for missing or invalid language code
2. **API Request Errors**: Handles network failures, timeouts, and HTTP errors
3. **Parsing Errors**: Properly catches and reports JSON parsing issues
4. **Fallback Content**: Provides meaningful fallback content when data can't be loaded
5. **Debug Information**: Includes extensive debug info in development mode

### Mobile Experience Improvements

For mobile users, we improved the touch interaction by:

1. Detecting touch devices with feature detection
2. Using 'click' trigger on touch devices instead of hover
3. Preventing default click behavior to show tooltip instead
4. Allowing Ctrl/Cmd+click to open in new tab if desired
5. Making tooltips interactive and dismissible

```typescript
// For touch devices, prevent the default click behavior to allow tooltip to show
if (isTouchDevice()) {
  wordElem.addEventListener('click', (e) => {
    // Only prevent default if modifier keys aren't pressed
    // This allows opening in new tab with Ctrl/Cmd+click
    if (!e.ctrlKey && !e.metaKey) {
      e.preventDefault();
    }
  });
}

// Configure tooltips differently for touch devices
const instance = tippy(wordElem, {
  // ...other options
  interactive: true,
  touch: true,
  trigger: isTouchDevice() ? 'click' : 'mouseenter focus', // Use click on touch devices
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

1. **Component Prop Validation**: Always validate required props early and provide clear error messages. The `language_code` prop was critical for API calls but wasn't being properly validated, leading to silent failures.

2. **Variable References Matter**: The `ReferenceError: lang is not defined` highlighted the importance of consistent variable naming. This type of error is particularly critical as it can break the entire component rendering.

3. **Type-Safe URL Generation**: The type-safe URL generation from `routes.ts` provides significant advantages:
   - Centralizes URL structure definitions
   - Provides automatic type checking for parameters
   - Handles encoding consistently
   - Creates a maintainable API surface

4. **Debug Information in Development**: Adding detailed debug information to tooltips in development mode was invaluable for diagnosing issues. This approach allows developers to see exactly what's happening without needing to open browser dev tools.

5. **Progressive Enhancement**: We implemented a layered approach that tries multiple strategies and degrades gracefully:
   - Try fetch API first with appropriate CORS settings
   - Fall back to XMLHttpRequest if needed
   - Provide fallback content if all API calls fail
   - Show helpful debug info in development mode

6. **URL Parameter Encoding**: Special care must be taken when encoding non-Latin characters (like Greek) in URLs. The `encodeURIComponent()` function was essential for handling these characters correctly.

7. **Component Design for Multiple Devices**: The EnhancedText component now has specific adaptations for mobile:
   - Different trigger events (click vs. hover)
   - Custom event handling to prevent default link behavior
   - Interactive tooltips that are touch-friendly

8. **Debugging with Both Approaches**: By implementing both direct and type-safe URL construction and comparing them, we were able to confirm they produced identical results, giving us confidence to standardize on the type-safe approach.

## Technical Details for Future Reference

### Parameter Names in Routes

The type-safe URL generation required using `target_language_code` rather than `language_code` due to how the route parameters are defined in the generated `routes.ts`:

```typescript
[RouteName.WORDFORM_API_WORD_PREVIEW_API]: { target_language_code: string; word: string };
```

This parameter naming must match exactly what the backend API expects.

### URL Construction Comparison

Direct URL:
```
http://localhost:3000/api/lang/word/el/βράχια/preview
```

Type-safe URL:
```
getApiUrl(RouteName.WORDFORM_API_WORD_PREVIEW_API, { 
  target_language_code: 'el', 
  word: 'βράχια' 
});
// Results in: http://localhost:3000/api/lang/word/el/βράχια/preview
```

Both approaches properly encode the Greek characters, which was verified by the debug output showing "URL Match: Yes ✓" in the tooltip.

### Browser Compatibility

The solution works across browsers due to:
1. Feature detection for touch devices
2. Fallback to XMLHttpRequest if fetch fails
3. Appropriate CORS settings for cross-origin requests
4. Conservative use of modern JS features

### Final Implementation

The final implementation in EnhancedText.svelte combines:
1. Type-safe URL generation from routes.ts
2. Comprehensive error handling and fallbacks
3. Detailed debug information during development
4. Device-specific adaptations for touch vs. mouse
5. Proper parameter validation and encoding

This fix not only resolves the immediate issue but also improves maintainability, robustness, and the overall user experience.