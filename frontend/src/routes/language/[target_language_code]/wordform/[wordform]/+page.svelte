<script lang="ts">
  import type { PageData } from './$types';  
  import { Card, MetadataCard, LemmaDetails } from '$lib';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { SITE_NAME } from '$lib/config';
  import { truncate, generateMetaDescription } from '$lib/utils';
  import { page } from '$app/stores'; // To access auth session
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  
  export let data: PageData;

  $: wordformData = data.wordformData;
  $: target_language_code = data.target_language_code;
  $: language_name = data.language_name; // From root layout
  $: ({ supabase, session, user } = data); // from root layout

  // Client-side logging to inspect wordformData
  $: if (browser && wordformData) {
    console.log('WF page data received by client (+page.svelte):', JSON.parse(JSON.stringify(wordformData)));
  }
  
  // Make sure we have valid data before unwrapping
  // After backend and server.ts changes, wordformData should directly contain metadata if found
  $: isValidData = !!wordformData?.wordform_metadata;
  // Check if we specifically need authentication for generation
  $: requiresAuthForGeneration = !!wordformData?.authentication_required_for_generation;
  
  // Unwrap the data from the response
  $: wordform_metadata = isValidData 
    ? wordformData.wordform_metadata 
    : null;
  $: lemma_metadata = isValidData 
    ? wordformData.lemma_metadata 
    : null;
  // Assume target_language_code and target_language_name are always top-level for now
  // If issues persist, these might need similar checks.
  $: target_language_name = wordformData?.target_language_name ?? '';
  // metadata might be a different field, let's check what it refers to.
  // It seems metadata was a general purpose field in some older structures.
  // If wordform_metadata contains everything, we might not need a separate 'metadata' field.
  // For now, let's assume it might come from wordformData directly if not part of wordform_metadata
  $: metadata = isValidData 
    ? (wordformData.metadata ?? wordformData.wordform_metadata) // If metadata is distinct, check it, else default to wordform_metadata
    : null;
  
  // Generate API URL for delete action only if we have valid data
  $: deleteUrl = isValidData ? getApiUrl(RouteName.WORDFORM_API_DELETE_WORDFORM_API, {
    target_language_code: target_language_code,
    wordform: wordform_metadata.wordform
  }) : '';
  
  async function handleDeleteSubmit(event: SubmitEvent) {
    // Always prevent the default browser form submission so we can handle the
    // redirect ourselves (otherwise the browser will follow the 302 to the API
    // domain, which is not what we want).
    event.preventDefault();

    const confirmed = confirm('Are you sure you want to delete this wordform? This action cannot be undone.');
    if (!confirmed) {
      return;
    }

    try {
      const res = await fetch(deleteUrl, {
        method: 'POST',
        credentials: 'include'
      });

      if (!res.ok && res.status !== 302 && res.status !== 204) {
        console.error('Failed to delete wordform:', res.status, await res.text());
        alert('Failed to delete wordform.');
        return;
      }

      // After successful deletion, navigate to the lemmas list page (handled by the
      // Svelte frontend and therefore on the correct domain).
      goto(`/language/${target_language_code}/lemmas`);
    } catch (err) {
      console.error('Error deleting wordform:', err);
      alert('An error occurred while deleting the wordform.');
    }
  }
</script>

<svelte:head>
  <title>{truncate(isValidData ? wordform_metadata.wordform : '', 30)} | Wordform | {target_language_name || target_language_code} | {SITE_NAME}</title>
  {#if isValidData && wordform_metadata.translations}
    <meta name="description" content="{generateMetaDescription(
      wordform_metadata.translations.join('; '),
      `${wordform_metadata.wordform} - ${target_language_name || target_language_code} wordform`
    )}">
  {/if}
</svelte:head>

<div class="container py-4">
  {#if requiresAuthForGeneration}
    <div class="alert alert-warning" role="alert">
      <div class="d-flex align-items-center">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-exclamation-triangle-fill flex-shrink-0 me-3" viewBox="0 0 16 16" role="img" aria-label="Warning:">
          <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
        </svg>
        <div>
          <h4 class="alert-heading mb-1">Authentication Required</h4>
          <p class="mb-0">
            We haven't processed the wordform "<span class="fw-bold">{wordformData.wordform}</span>" yet.
            Please <a href="/auth?next={$page.url.pathname}" class="alert-link">log in or sign up</a> to generate its details.
          </p>
        </div>
      </div>
    </div>
  {:else if !isValidData}
    <div class="alert alert-info" role="alert">
      <div class="d-flex align-items-center">
        <div class="spinner-border spinner-border-sm me-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <div>
          <h4 class="alert-heading mb-1">Loading Wordform Data...</h4>
          <p class="mb-0">Please wait while we load or generate the wordform information.</p>
        </div>
      </div>
    </div>
  {:else}
    <div class="row mb-4">
      <div class="col">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="/">Languages</a></li>
            <li class="breadcrumb-item"><a href="/language/{target_language_code}/sources">{target_language_name}</a></li>
            <li class="breadcrumb-item"><a href="/language/{target_language_code}/wordforms">Wordforms</a></li>
            <li class="breadcrumb-item active" aria-current="page">{wordform_metadata.wordform}</li>
          </ol>
        </nav>
      </div>
    </div>
    
    <div class="row mb-3">
      <div class="col-md-8">
        <h1 class="display-4 mb-3 hz-foreign-text">{wordform_metadata.wordform}</h1>
      </div>
      <div class="col-md-4 text-md-end">
        {#if metadata}
        <MetadataCard {metadata} />
        {/if}
      </div>
    </div>

    <div class="row mb-4">
      <div class="col">
        <form action={deleteUrl} method="POST" 
              on:submit={handleDeleteSubmit}>
          <button type="submit" class="btn btn-sm btn-danger">Delete wordform</button>
        </form>
      </div>
    </div>
    
    <div class="row">
      <div class="col-md-6">
        <Card title="Wordform Details">
          <div class="translations mb-3">
            <p><strong>Translation:</strong> 
              {#if wordform_metadata.translations && wordform_metadata.translations.length > 0}
                {#each wordform_metadata.translations as translation}
                  <span class="badge bg-secondary me-1">{translation}</span>
                {/each}
              {:else}
                <span class="text-muted">No translation available</span>
              {/if}
            </p>
          </div>
          
          <p><strong>Part of Speech:</strong> <span class="badge rounded-pill bg-light-subtle me-1">{wordform_metadata.part_of_speech || 'Unknown'}</span></p>
          
          <div class="mb-3">
            <p class="mb-2"><strong>Inflection Type:</strong></p> 
            {#if wordform_metadata.inflection_types && wordform_metadata.inflection_types.length > 0}
              {#each wordform_metadata.inflection_types as inflection_type}
                <span class="badge bg-light-subtle me-1 mb-1">{inflection_type}</span>
              {/each}
            {:else if wordform_metadata.inflection_type}
              <span class="badge bg-light-subtle me-1">{wordform_metadata.inflection_type}</span>
            {:else}
              <span class="text-muted">Not available</span>
            {/if}
          </div>
          
          <p>
            <strong>Is Dictionary Form:</strong> 
            {#if wordform_metadata.is_lemma}
              <span class="text-success">Yes</span>
            {:else}
              <span class="text-warning">No</span>
            {/if}
          </p>
        </Card>
      </div>
      
      <div class="col-md-6">
        <!-- Show possible misspellings if they exist -->
        {#if wordform_metadata && wordform_metadata.possible_misspellings && wordform_metadata.possible_misspellings.length > 0}
          <Card title="Possible Corrections" className="mb-4">
            <ul class="list-group">
              {#each wordform_metadata.possible_misspellings as misspelling}
                <li class="list-group-item hz-foreign-text">{misspelling}</li>
              {/each}
            </ul>
          </Card>
        {/if}
      </div>
    </div>
    
    <!-- Lemma details shown below the wordform details -->
    {#if lemma_metadata}
      <LemmaDetails 
        lemma_metadata={lemma_metadata} 
        {target_language_code}
        {session}
      />
    {/if}
  {/if}
</div>

<style>
  .hz-foreign-text {
    font-family: 'Times New Roman', Times, serif;
    font-style: italic;
  }
  
  .breadcrumb {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
  }
  
  .badge {
    font-weight: normal;
    padding: 0.5em 0.8em;
  }
</style> 