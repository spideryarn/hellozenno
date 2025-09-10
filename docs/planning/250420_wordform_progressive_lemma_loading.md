# Wordform Page Progressive Lemma Loading

## Goal

Enhance the Wordform detail page to display full Lemma details in-place with progressive loading:
1. Show wordform details immediately (already working)
2. Show partial lemma details immediately if available
3. Display a loading spinner when fetching/generating complete lemma data
4. Handle all edge cases gracefully (including NULL lemma associations)
5. Respect authentication requirements for lemma generation
6. Maintain a clear visual distinction between wordform and lemma sections

## Context

When users visit a Wordform page, they often want to see the related Lemma (dictionary form) details without navigating away. Currently, this requires clicking through to the Lemma page, which can take time to load if the lemma needs to be generated.

The Wordform API already returns lemma_metadata if available, but:
- It may be partially complete (is_complete=false)
- It may be entirely missing (lemma_entry is NULL)
- The full lemma generation can take time and requires login

The backend uses `@api_auth_optional` on `get_wordform_metadata_api()` to handle authentication for wordform generation. For lemma generation, we need to respect a similar pattern:
- Show complete lemma data if it exists, regardless of login status
- Only attempt to generate/complete lemma data if the user is logged in
- Show appropriate login prompt if generation is needed but the user isn't logged in

## Key Decisions

- Use progressive enhancement: display what we have immediately, then fetch complete data
- Handle the lemma data states with authentication in mind:
  1. Complete lemma (show all details, no generation needed)
  2. Partial lemma + logged in (show what we have, fetch the rest)
  3. Partial lemma + not logged in (show what we have, display login prompt)
  4. Missing lemma + logged in (show loading spinner, fetch everything)
  5. Missing lemma + not logged in (show prompt to login)
- Reuse the same components from the Lemma page for consistency
- Add a "loading" state with Phosphor spinner component
- Retain a link to the full Lemma page for those who want to see it in isolation
- Use visual styling to clearly separate Wordform and Lemma sections

## Useful References

- `/frontend/src/routes/language/[target_language_code]/wordform/[wordform]/+page.svelte` - Current Wordform page (HIGH)
- `/frontend/src/routes/language/[target_language_code]/lemma/[lemma]/+page.svelte` - Lemma page with components to reuse (HIGH)
- `/frontend/src/lib/components/LemmaCard.svelte` - Existing lemma card component (MEDIUM)
- `/backend/utils/word_utils.py` - Contains get_wordform_metadata function (MEDIUM)
- `/frontend/docs/STYLING.md` - Documentation for Phosphor icons (MEDIUM)
- `/backend/views/wordform_api.py` - Contains the API_auth_optional decorator usage (HIGH)
- `/planning/250418_Supabase_auth_SvelteKit.md` - Implementation of auth system (MEDIUM)

## Actions

- [x] Stage 1: Basic component structure
  - [x] Create a LemmaDetails.svelte component in $lib/components
    - [x] Add basic loading state with Phosphor CircleNotch spinner
    - [x] Include structure for displaying partial lemma data
    - [x] Add prominent "View Full Lemma" button to link to the dedicated lemma page
    - [x] Add visual styling to distinguish it from wordform data
  - [x] Update wordform/+page.svelte to use the new component
    - [x] Pass existing lemma_metadata to the component
    - [x] Handle null/undefined gracefully

- [x] Stage 2: Basic authentication integration
  - [x] Pass session info to LemmaDetails component from wordform page
  - [x] Add conditional UI elements based on auth state:
    - [x] If lemma_metadata exists and is complete, show all data
    - [x] If lemma_metadata exists but is incomplete and session exists, show loading state
    - [x] If lemma_metadata exists but is incomplete and no session, show "Login to see complete details" prompt
    - [x] If no lemma_metadata and session exists, show loading state
    - [x] If no lemma_metadata and no session, show "Login to generate" prompt
  - [x] Add "Login" button with properly formatted return URL

- [x] Stage 3: Client-side lemma fetching
  - [x] Add function to fetch complete lemma data (only when logged in)
  - [x] Only trigger fetch when:
    - [x] User is logged in (session exists)
    - [x] Lemma exists but is_complete=false OR lemma is completely missing
  - [x] Handle authentication errors and show appropriate messages
  - [x] Add retry button in case of non-auth errors

- [x] Stage 4: Polish the presentation
  - [x] Enhance styling to clearly separate wordform and lemma sections
    - [x] Add distinct card styling or borders (border-top with primary color)
    - [x] Use different background colors or subtle visual cues (subtle background tint)
    - [x] Move lemma details below wordform details with clear visual separator
  - [x] Improve loading states with animations (CircleNotch spinner with rotation animation)
  - [x] Add clear transitions between states
  - [x] Ensure mobile responsiveness (using Bootstrap's responsive grid)
  - [x] Create shared LemmaContent component used by both pages
  - [ ] Test all possible data and auth state combinations

- [x] Additional Improvements
  - [x] Create shared `LemmaContent.svelte` component
  - [x] Update both Lemma page and LemmaDetails component to use the shared component
  - [x] Ensure code reuse for maximum maintainability

## Implementation Details

### LemmaDetails.svelte Component

This new component will:
1. Accept lemma_metadata props and auth session
2. Handle different states based on data and auth
3. Fetch complete data only when appropriate

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { getLemmaMetadata } from '$lib/api';
  import CircleNotch from 'phosphor-svelte/lib/CircleNotch';
  import { Card } from '$lib';
  
  export let lemma_metadata: any | null;
  export let target_language_code: string;
  export let lemma: string | null = null;
  export let session: any | null = null; // Auth session
  
  let isLoading = false;
  let error: string | null = null;
  let authError = false;
  let completeData: any | null = null;
  
  // Merged data combines the original metadata with fetched complete data
  $: displayData = completeData || lemma_metadata || {};
  $: hasLemma = !!lemma || !!lemma_metadata?.lemma;
  $: lemmaValue = lemma || lemma_metadata?.lemma;
  $: isLoggedIn = !!session;
  $: needsComplete = hasLemma && lemma_metadata && !lemma_metadata.is_complete;
  $: canFetch = isLoggedIn && hasLemma;
  $: loginUrl = `/auth?next=${encodeURIComponent(window.location.pathname)}`;
  
  onMount(async () => {
    if (canFetch && needsComplete) {
      await fetchCompleteData();
    }
  });
  
  async function fetchCompleteData() {
    if (!hasLemma) return;
    
    isLoading = true;
    
    try {
      completeData = await getLemmaMetadata(null, target_language_code, lemmaValue);
      isLoading = false;
    } catch (err) {
      isLoading = false;
      
      if (err.status === 401) {
        authError = true;
      } else {
        error = err.message || 'Failed to load lemma data';
      }
    }
  }
</script>

<Card title="Dictionary Form Details" className="mt-4 lemma-details-card">
  <div class="lemma-details">
    <!-- Always show the link to full lemma page if we have a lemma -->
    {#if hasLemma}
      <div class="text-center mb-3">
        <a href="/language/{target_language_code}/lemma/{lemmaValue}" 
          class="btn btn-primary mb-3 hz-foreign-text fw-bold">
          View Full Lemma Page: {lemmaValue}
        </a>
      </div>
    {/if}
  
    <!-- Different states based on data and auth -->
    {#if isLoading}
      <div class="text-center p-4">
        <CircleNotch size={32} weight="regular" class="spinner text-primary" />
        <p class="mt-2">Loading complete lemma details...</p>
      </div>
    {:else if authError}
      <div class="alert alert-warning">
        Authentication required to generate complete lemma details.
        <a href={loginUrl} class="btn btn-sm btn-primary ms-2">Login</a>
      </div>
    {:else if error}
      <div class="alert alert-danger">
        {error}
        <button class="btn btn-sm btn-primary ms-2" on:click={fetchCompleteData}>
          Retry
        </button>
      </div>
    {:else if hasLemma}
      <!-- Display the lemma data we have -->
      <div class="lemma-content">
        <!-- Display partial data here -->
        
        <!-- If incomplete and not logged in, show login prompt -->
        {#if needsComplete && !isLoggedIn}
          <div class="alert alert-info mt-3">
            <p>Login to see complete lemma details.</p>
            <a href={loginUrl} class="btn btn-sm btn-primary">Login</a>
          </div>
        {/if}
      </div>
    {:else if !isLoggedIn}
      <!-- No lemma and not logged in -->
      <div class="alert alert-info">
        <p>Login to generate lemma information.</p>
        <a href={loginUrl} class="btn btn-sm btn-primary">Login</a>
      </div>
    {:else}
      <!-- No lemma but logged in - unusual state -->
      <div class="alert alert-warning">
        <p>No lemma information available for this wordform.</p>
      </div>
    {/if}
  </div>
</Card>

<style>
  .lemma-details-card {
    border-top: 3px solid var(--bs-primary);
    background-color: rgba(var(--bs-primary-rgb), 0.03);
  }
  
  .spinner {
    animation: spin 1.5s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
```

### Updating Wordform Page

The updated Wordform page will:
1. Pass existing lemma_metadata to the component
2. Pass the auth session to enable conditional UI

```svelte
<!-- Inside wordform/+page.svelte -->
<script>
  // Existing imports
  import { page } from '$app/stores'; // To access auth session
  import { LemmaDetails } from '$lib';
  
  // Existing code...
  
  // Access session from the page store
  $: session = $page.data.session;
</script>

<!-- Add clear visual separation between wordform and lemma sections -->
<div class="row mt-5">
  <div class="col-12">
    <hr class="mb-4" />
    <h2 class="mb-4">Dictionary Form Information</h2>
    
    <LemmaDetails 
      lemma_metadata={lemma_metadata} 
      {target_language_code}
      {session}
    />
  </div>
</div>
```

## Appendix

### API Data Structures

**Wordform API Response:**
```json
{
  "wordform_metadata": {
    "wordform": "ετοιμοθάνατος",
    "part_of_speech": "adjective",
    "translations": ["dying", "about to die"],
    "inflection_type": "nominative singular masculine",
    "is_lemma": true
  },
  "lemma_metadata": {
    "lemma": "ετοιμοθάνατος",
    "is_complete": false,
    "part_of_speech": "adjective",
    "translations": ["dying", "about to die"],
    "etymology": null
    // other fields may be empty or null
  },
  "target_language_code": "el",
  "target_language_name": "Greek",
  "metadata": {
    "created_at": "2023-01-01T12:00:00",
    "updated_at": "2023-01-01T12:00:00"
  }
}
```

**Complete Lemma API Response:**
```json
{
  "lemma_metadata": {
    "lemma": "ετοιμοθάνατος",
    "is_complete": true,
    "part_of_speech": "adjective",
    "translations": ["dying", "about to die"],
    "etymology": "From έτοιμος (ready) + θάνατος (death)",
    "synonyms": [...],
    "example_usage": [...],
    // all fields populated
  },
  "target_language_code": "el",
  "target_language_name": "Greek",
  "metadata": {
    "created_at": "2023-01-01T12:00:00",
    "updated_at": "2023-01-01T13:00:00"
  }
}
```

**Authentication Error Response:**
```json
{
  "error": "Authentication Required",
  "description": "Authentication required to search for or generate lemma details",
  "target_language_code": "el",
  "target_language_name": "Greek",
  "authentication_required_for_generation": true,
  "lemma": "ετοιμοθάνατος",
  "partial_lemma_metadata": {
    // Any partial data available without generation
  }
}
```