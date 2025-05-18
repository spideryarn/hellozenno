<script lang="ts">
  import type { PageData } from './$types';  
  import { Card, LemmaCard, MetadataCard, LemmaContent } from '$lib';
  import { apiFetch, getApiUrl } from '$lib/api'; // Import apiFetch
  import { RouteName } from '$lib/generated/routes';
  import { page } from '$app/stores'; // Import page store for current URL
  import { SITE_NAME } from '$lib/config';
  import { truncate, generateMetaDescription } from '$lib/utils';
  import { goto } from '$app/navigation';
  
  export let data: PageData;
  // Destructure lemmaResult which contains the API response, and the separately passed params
  // Also get the supabase client instance passed from +layout.ts
  const { lemmaResult, target_language_code, lemma: lemmaParam, supabase: supabaseClient } = data; 
  
  // Extract the actual lemma data and potential error from lemmaResult
  const lemma_metadata = lemmaResult?.lemma_metadata || lemmaResult?.partial_lemma_metadata || {};
  const authError = lemmaResult?.authentication_required_for_generation 
                      ? lemmaResult.description 
                      : null;
  const notFoundError = lemmaResult?.error === 'Not Found'; // Check for 404 specifically
  
  // Extract the server-provided metadata (created/updated timestamps)
  const metadata = lemmaResult?.metadata;

  // Define login URL with redirect back to current page
  $: loginUrl = `/auth?next=${encodeURIComponent($page.url.pathname + $page.url.search)}`;

  // Debugging logs
  $: console.log('Lemma Page - data prop:', data);
  $: console.log('Lemma Page - supabaseClient from data:', supabaseClient);
  $: console.log('Lemma Page - lemma_metadata:', lemma_metadata);
  $: console.log('Lemma Page - target_language_code:', target_language_code);
  $: console.log('Lemma Page - lemma_metadata.lemma value for URL:', lemma_metadata?.lemma);
  // deleteUrl is now constructed inside handleDeleteSubmit if using apiFetch directly with RouteName

  async function handleDeleteSubmit(event: SubmitEvent) {
    event.preventDefault();

    const confirmed = confirm('Are you sure you want to delete this lemma? All associated wordforms will also be deleted. This action cannot be undone.');
    if (!confirmed) return;

    if (!lemma_metadata?.lemma) {
      console.error('Lemma value missing – cannot delete lemma.');
      alert('Cannot delete lemma: lemma data is missing.');
      return;
    }
    
    if (!supabaseClient) {
      console.error('Supabase client is not available for API call.');
      alert('Authentication context not available. Please try refreshing the page.');
      return;
    }

    try {
      await apiFetch({
        supabaseClient: supabaseClient, // Pass the client instance
        routeName: RouteName.LEMMA_API_DELETE_LEMMA_API,
        params: {
          target_language_code: target_language_code,
          lemma: lemma_metadata.lemma
        },
        options: { method: 'POST' } // apiFetch sets Content-Type and handles auth header
      });

      // apiFetch throws on non-ok responses, so if we reach here, it was successful (or 204)
      goto(`/language/${target_language_code}/lemmas`);
    } catch (err: any) {
      console.error('Error deleting lemma (via apiFetch):', err);
      alert(`Failed to delete lemma: ${err.message || 'An unknown error occurred.'}`);
    }
  }
</script>

<svelte:head>
  <title>{truncate(lemma_metadata?.lemma || lemmaParam, 30)} | Lemma | {lemmaResult?.target_language_name || target_language_code} | {SITE_NAME}</title>
  <meta name="description" content="{generateMetaDescription(
    lemma_metadata?.translations?.join('; ') || '',
    `${lemma_metadata?.lemma || lemmaParam} - ${lemmaResult?.target_language_name || target_language_code} lemma`
  )}">
</svelte:head>

<div class="container">
  <div class="row mb-4">
    <div class="col">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/languages">Languages</a></li>
          <li class="breadcrumb-item"><a href="/language/{target_language_code}/sources">{lemmaResult?.target_language_name || target_language_code}</a></li>
          <li class="breadcrumb-item"><a href="/language/{target_language_code}/lemmas">Lemmas</a></li>
          <li class="breadcrumb-item active" aria-current="page">{lemma_metadata?.lemma || 'Lemma'}</li>
        </ol>
      </nav>
    </div>
  </div>
  
  {#if authError}
  <!-- <Alert type="warning" class="mb-4">
    { authError }
    <a href={loginUrl} class="btn btn-sm btn-primary ms-2">Login to generate</a>
  </Alert> -->
  <div class="alert alert-warning mb-4" role="alert">
    { authError }
    <a href={loginUrl} class="btn btn-sm btn-primary ms-2">Login to generate</a>
  </div>
  {/if}

  <div class="row mb-3">
    <div class="col-md-8">
      <h1 class="mb-4">{lemma_metadata.lemma}</h1>
    </div>
    <div class="col-md-4 text-md-end">
      {#if metadata}
      <MetadataCard {metadata} />
      {/if}
    </div>
  </div>

  {#if lemma_metadata?.lemma} <!-- Only show delete if we have a lemma to delete -->
  <div class="mb-4">
    <form on:submit={handleDeleteSubmit}> <!-- Removed action and method, handled by JS -->
      <button type="submit" class="btn btn-danger">Delete lemma</button>
    </form>
  </div>
  {/if}
  
  <!-- Use the shared LemmaContent component -->
  <LemmaContent 
    lemma_metadata={lemma_metadata}
    {target_language_code}
    showFullLink={false}
    isAuthError={!!authError}
  />
</div>

<style>
  .breadcrumb {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
  }
</style> 