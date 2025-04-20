<script lang="ts">
  import { onMount } from 'svelte';
  import { getLemmaMetadata } from '$lib/api';
  import { LemmaContent } from '$lib';
  import { CircleNotch } from 'phosphor-svelte';
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
  
  // Merged data combines the original metadata with fetched complete data
  $: displayData = completeData || lemma_metadata || {};
  $: hasLemma = !!lemma || !!lemma_metadata?.lemma;
  $: lemmaValue = lemma || lemma_metadata?.lemma;
  $: isLoggedIn = !!session;
  $: needsComplete = hasLemma && lemma_metadata && !lemma_metadata.is_complete;
  $: canFetch = isLoggedIn && hasLemma;
  // Use $page store for SSR-safe URL construction
  $: loginUrl = `/auth?next=${encodeURIComponent($page.url.pathname)}`;
  
  
  onMount(async () => {
    if (canFetch && needsComplete && browser) {
      await fetchCompleteData();
    }
  });
  
  async function fetchCompleteData() {
    if (!hasLemma || !browser) return;
    
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

<hr class="mt-5 mb-4" />
<div class="row mb-4">
  <div class="col">
    <h2>Dictionary Form Details</h2>
  </div>
</div>

<!-- Different states based on data and auth -->
{#if isLoading}
  <div class="loading-state p-4 mb-4 text-center">
    <CircleNotch size={32} weight="regular" class="spinner text-primary" />
    <p class="mt-2">Loading complete lemma details...</p>
  </div>
{:else if authError}
  <div class="alert alert-warning mb-4">
    Authentication required to generate complete lemma details.
    <a href={loginUrl} class="btn btn-sm btn-primary ms-2">Login</a>
  </div>
{:else if error}
  <div class="alert alert-danger mb-4">
    {error}
    <button class="btn btn-sm btn-primary ms-2" on:click={fetchCompleteData}>
      Retry
    </button>
  </div>
{:else if hasLemma}
  <!-- Use the shared LemmaContent component -->
  <LemmaContent 
    lemma_metadata={displayData}
    {target_language_code}
    showFullLink={true}
    isAuthError={false}
  >
    <!-- Pass login prompt via slot if needed -->
    <div slot="auth-prompt">
      {#if needsComplete && !isLoggedIn}
        <div class="alert alert-info mt-3">
          <p>Login to see complete lemma details.</p>
          <a href={loginUrl} class="btn btn-sm btn-primary">Login</a>
        </div>
      {/if}
    </div>
  </LemmaContent>
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
  .spinner {
    animation: spin 1.5s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .loading-state {
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 0.375rem;
    background-color: rgba(var(--bs-primary-rgb), 0.03);
  }
</style>