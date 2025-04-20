<script lang="ts">
  import { onMount } from 'svelte';
  import { getLemmaMetadata } from '$lib/api';
  import { LemmaContent, LoadingSpinner } from '$lib';
  import { browser } from '$app/environment';
  import { page } from '$app/stores';
  
  export let lemma_metadata: any | null;
  export let target_language_code: string;
  export let lemma: string | null = null;
  export let session: any | null = null; // Auth session
  
  let isLoading = false;
  let error: string | null = null;
  let authError = false;
  let completeData: any | null = null;
  let generationInProgress = false;
  
  // Merged data combines the original metadata with fetched complete data
  $: displayData = completeData || lemma_metadata || {};
  $: hasLemma = !!lemma || !!lemma_metadata?.lemma;
  $: lemmaValue = lemma || lemma_metadata?.lemma;
  $: isLoggedIn = !!session;
  // Fix for showing empty sections when is_complete is false
  $: needsComplete = hasLemma && lemma_metadata && lemma_metadata.is_complete === false;
  $: canFetch = isLoggedIn && hasLemma;
  // Update generationInProgress when the data indicates it
  $: if (displayData?.generation_in_progress) {
    generationInProgress = true;
    // Set a timer to retry after a delay if generation is in progress
    if (browser && !isLoading) {
      setTimeout(() => {
        console.log('Retrying fetch after delay for in-progress generation');
        fetchCompleteData();
        // We don't need additional code here since fetchCompleteData now always reloads 
        // the page when it gets a response from the backend
      }, 5000); // 5 second delay
    }
  } else {
    generationInProgress = false;
  }
  
  // We'll handle page reloads directly in the fetch handlers
  // Use $page store for SSR-safe URL construction
  $: loginUrl = `/auth?next=${encodeURIComponent($page.url.pathname)}`;
  
  
  onMount(async () => {
    // Try to fetch complete data automatically if the user is logged in
    // and the lemma needs completion
    console.log('LemmaDetails onMount - canFetch:', canFetch, 'needsComplete:', needsComplete, 'browser:', browser);
    
    if (canFetch && needsComplete && browser) {
      console.log('Automatically fetching complete lemma data for:', lemmaValue);
      fetchCompleteData();
      // We don't need to check for success or reload here since fetchCompleteData
      // now handles the page reload after getting a response from the backend
    }
  });
  
  async function fetchCompleteData() {
    if (!hasLemma || !browser) return false;
    
    isLoading = true;
    error = null;
    authError = false;
    
    try {
      // Use page.data.supabase to ensure auth token is included
      const supabaseClient = $page.data.supabase;
      console.log(`Fetching complete data for lemma: ${lemmaValue} (target: ${target_language_code})`);
      
      completeData = await getLemmaMetadata(supabaseClient, target_language_code, lemmaValue);
      console.log('Received lemma data:', completeData);
      
      // If response includes authentication_required_for_generation even with a session,
      // it means the API couldn't verify our token
      if (completeData?.authentication_required_for_generation) {
        console.log('API returned auth required flag despite having session:', completeData);
        authError = true;
        isLoading = false;
        return false;
      }
      
      // IMPORTANT: Always reload the page after we get a response from the backend
      // This ensures we have fresh data from the server
      if (browser && !authError) {
        console.log('Reloading page to show fresh lemma data');
        setTimeout(() => window.location.reload(), 500);
      }
      
      isLoading = false;
      return true; // Signal successful fetch
    } catch (err) {
      console.error('Error fetching lemma details:', err);
      isLoading = false;
      
      if (err.status === 401) {
        console.log('Auth error when fetching lemma details:', err);
        authError = true;
      } else {
        error = err.message || 'Failed to load lemma data';
      }
      
      return false; // Signal failed fetch
    }
  }
</script>

<hr class="mt-5 mb-4" />
<div class="row mb-4">
  <div class="col">
    <h2>Dictionary Form Details</h2>
  </div>
</div>

<!-- Different states based on data and auth -->
{#if isLoading}
  <div class="loading-state p-4 mb-4 text-center">
    <LoadingSpinner />
    <p class="mt-2">Loading complete lemma details...</p>
  </div>
{:else if generationInProgress}
  <div class="loading-state p-4 mb-4 text-center">
    <LoadingSpinner />
    <p class="mt-2">Generating lemma details. This may take some time...</p>
    <p class="small text-muted">Generation is happening on the server. This will automatically update when complete.</p>
  </div>
{:else if authError}
  <div class="alert alert-warning mb-4">
    <p class="mb-2">Authentication required to generate complete lemma details.</p>
    {#if isLoggedIn}
      <p class="small mb-2">You're logged in, but we had trouble authenticating your session with the API.</p>
      <button class="btn btn-sm btn-primary me-2" on:click={fetchCompleteData}>
        Try Again
      </button>
      <a href="/auth?next={encodeURIComponent($page.url.pathname)}" class="btn btn-sm btn-outline-primary">
        Re-login
      </a>
    {:else}
      <a href={loginUrl} class="btn btn-sm btn-primary">Login</a>
    {/if}
  </div>
{:else if error}
  <div class="alert alert-danger mb-4">
    {error}
    <button class="btn btn-sm btn-primary ms-2" on:click={fetchCompleteData}>
      Retry
    </button>
  </div>
{:else if hasLemma && displayData.is_complete === true}
  <!-- Use the shared LemmaContent component - only show if complete or not needing completion -->
  <LemmaContent 
    lemma_metadata={displayData}
    {target_language_code}
    showFullLink={true}
    isAuthError={false}
  >
    <!-- Pass login prompt via slot if needed -->
    <div slot="auth-prompt">
      <!-- We no longer need this since we handle incomplete lemmas separately -->
    </div>
  </LemmaContent>
{:else if hasLemma && !displayData.is_complete}
  <!-- Incomplete lemma - show prompt to complete it -->
  <div class="alert alert-info mb-4">
    <p>Additional lemma details are available.</p>
    <button class="btn btn-sm btn-primary" on:click={() => {
      fetchCompleteData();
    }} disabled={isLoading}>
      {#if isLoading}
        <span style="display: inline-flex; margin-right: 8px; transform: scale(0.5);">
          <LoadingSpinner />
        </span>
        Loading...
      {:else}
        Complete Lemma Details
      {/if}
    </button>
  </div>
{:else if !isLoggedIn}
  <!-- No lemma and not logged in -->
  <div class="alert alert-info mb-4">
    <p>Login to generate lemma information.</p>
    <a href={loginUrl} class="btn btn-sm btn-primary">Login</a>
  </div>
{:else}
  <!-- No lemma but logged in - unusual state -->
  <div class="alert alert-warning mb-4">
    <p>No lemma information available for this wordform.</p>
  </div>
{/if}

<style>
  .loading-state {
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 0.375rem;
    background-color: rgba(var(--bs-primary-rgb), 0.03);
  }
</style>