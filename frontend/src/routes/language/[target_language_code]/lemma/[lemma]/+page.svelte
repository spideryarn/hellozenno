<script lang="ts">
  import type { PageData } from './$types';  
  import { Card, LemmaCard, MetadataCard } from '$lib';
  import SentenceCard from '$lib/components/SentenceCard.svelte';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { page } from '$app/stores'; // Import page store for current URL
  // import Alert from '$lib/components/Alert.svelte'; // TODO: Fix path or create component
  // import UserDisplay from '$lib/components/UserDisplay.svelte'; // TODO: Fix path or create component
  
  export let data: PageData;
  const { lemmaData, authError, target_language_code, target_language_name, metadata } = data;
  
  // Handle potential partial data in case of auth error
  // The actual full metadata is nested within lemmaData if successful
  const lemma_metadata = lemmaData?.lemma_metadata || lemmaData || {};

  // Define login URL with redirect back to current page
  $: loginUrl = `/auth?next=${encodeURIComponent($page.url.pathname + $page.url.search)}`;

  // Generate API URL for delete action (only if lemma exists properly)
  const deleteUrl: string | undefined = lemma_metadata?.lemma ? getApiUrl(RouteName.LEMMA_VIEWS_DELETE_LEMMA_VW, {
    target_language_code,
    lemma: lemma_metadata.lemma
  }) : undefined;
  
  function handleDeleteSubmit(event: SubmitEvent) {
    const confirmed = confirm('Are you sure you want to delete this lemma? All associated wordforms will also be deleted. This action cannot be undone.');
    if (!confirmed) {
      event.preventDefault();
    }
  }
</script>

<div class="container">
  <div class="row mb-4">
    <div class="col">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/languages">Languages</a></li>
          <li class="breadcrumb-item"><a href="/language/{target_language_code}/sources">{target_language_name || target_language_code}</a></li>
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

  {#if deleteUrl} <!-- Only show delete if we have a valid URL -->
  <div class="mb-4">
    <form action={deleteUrl} method="POST" 
          on:submit={handleDeleteSubmit}>
      <button type="submit" class="btn btn-danger">Delete lemma</button>
    </form>
  </div>
  {/if}
  
  <Card title="Lemma Details">
    <div class="translations mb-3">
      <p><strong>Translation:</strong> 
        {#if lemma_metadata?.translations && lemma_metadata.translations.length > 0}
          {lemma_metadata.translations.join('; ')}
        {:else}
          {#if !authError}No translation available{/if} <!-- Show nothing if auth error -->
        {/if}
      </p>
    </div>
    
    <p><strong>Part of Speech:</strong> {lemma_metadata?.part_of_speech || '-'}</p>
    
    <div class="etymology mb-3">
      <p><strong>Etymology:</strong> {lemma_metadata?.etymology || '-'}</p>
    </div>
    
    <div class="commonality mb-3">
      <p><strong>Commonality:</strong> {lemma_metadata?.commonality ? Math.round((lemma_metadata.commonality) * 100) + '%' : '-'}</p>
    </div>
    
    <div class="guessability mb-3">
      <p><strong>Guessability:</strong> {lemma_metadata?.guessability ? Math.round((lemma_metadata.guessability) * 100) + '%' : '-'}</p>
    </div>
    
    <div class="register mb-3">
      <p><strong>Register:</strong> {lemma_metadata?.register || '-'}</p>
    </div>
  </Card>
  
  {#if !authError && lemma_metadata?.example_usage && lemma_metadata.example_usage.length > 0}
  <Card title="Example Usage" className="mt-4">
    <div class="d-flex flex-column gap-3">
      {#each lemma_metadata.example_usage as example}
        <SentenceCard 
          text={example.phrase} 
          translation={example.translation} 
          slug={example.slug || ''} 
          target_language_code={target_language_code}
        />
      {/each}
    </div>
  </Card>
  {/if}
  
  {#if !authError && lemma_metadata?.mnemonics && lemma_metadata.mnemonics.length > 0}
  <Card title="Mnemonics" className="mt-4">
    <ul class="list-group">
      {#each lemma_metadata.mnemonics as mnemonic}
        <li class="list-group-item">{mnemonic}</li>
      {/each}
    </ul>
  </Card>
  {/if}
  
  {#if !authError && lemma_metadata?.related_words_phrases_idioms && lemma_metadata.related_words_phrases_idioms.length > 0}
  <Card title="Related Words, Phrases & Idioms" className="mt-4">
    <div class="row row-cols-1 row-cols-md-2 g-3">
      {#each lemma_metadata.related_words_phrases_idioms as related}
        <div class="col">
          <LemmaCard 
            lemma={{ lemma: related }} 
            target_language_code={target_language_code} 
            showDetails={false} 
          />
        </div>
      {/each}
    </div>
  </Card>
  {/if}
  
  {#if !authError && lemma_metadata?.synonyms && lemma_metadata.synonyms.length > 0}
  <Card title="Synonyms" className="mt-4">
    <div class="row row-cols-1 row-cols-md-2 g-3">
      {#each lemma_metadata.synonyms as synonym}
        <div class="col">
          <LemmaCard 
            lemma={{ lemma: synonym }} 
            target_language_code={target_language_code} 
            showDetails={false} 
          />
        </div>
      {/each}
    </div>
  </Card>
  {/if}
  
  {#if !authError && lemma_metadata?.antonyms && lemma_metadata.antonyms.length > 0}
  <Card title="Antonyms" className="mt-4">
    <div class="row row-cols-1 row-cols-md-2 g-3">
      {#each lemma_metadata.antonyms as antonym}
        <div class="col">
          <LemmaCard 
            lemma={{ lemma: antonym }}
            target_language_code={target_language_code} 
            showDetails={false} 
          />
        </div>
      {/each}
    </div>
  </Card>
  {/if}
  
  {#if !authError && lemma_metadata?.example_wordforms && lemma_metadata.example_wordforms.length > 0}
  <Card title="Example Wordforms" className="mt-4">
    <div class="list-group">
      {#each lemma_metadata.example_wordforms as form}
        <a href="/language/{target_language_code}/wordform/{form}" 
           class="list-group-item list-group-item-action hz-foreign-text">
          {form}
        </a>
      {/each}
    </div>
  </Card>
  {/if}
  
  {#if !authError && lemma_metadata?.cultural_context}
  <Card title="Cultural Context" className="mt-4">
    <p>{lemma_metadata.cultural_context}</p>
  </Card>
  {/if}
  
  {#if !authError && lemma_metadata?.easily_confused_with && lemma_metadata.easily_confused_with.length > 0 && lemma_metadata.easily_confused_with[0].lemma}
  <Card title="Easily Confused With" className="mt-4">
    <div class="list-group">
      {#each lemma_metadata.easily_confused_with as confused}
        {#if confused.lemma}
        <div class="list-group-item">
          <div class="d-flex flex-column">
            <div class="mb-3">
              <LemmaCard 
                lemma={{
                  lemma: confused.lemma,
                  translations: confused.translations || [],
                  part_of_speech: confused.part_of_speech || '',
                  commonality: confused.commonality || 0,
                  is_complete: confused.is_complete || false
                }} 
                target_language_code={target_language_code} 
                showDetails={false} 
              />
            </div>
            
            {#if confused.explanation}
            <p><strong>Explanation:</strong> {confused.explanation}</p>
            {/if}
            
            {#if confused.example_usage_this_target && confused.example_usage_this_source}
            <div class="mb-3">
              <p class="mb-1 small text-secondary">This word:</p>
              <SentenceCard
                text={confused.example_usage_this_target}
                translation={confused.example_usage_this_source}
                slug={confused.example_usage_this_slug || ''}
                target_language_code={target_language_code}
              />
            </div>
            {/if}
            
            {#if confused.example_usage_other_target && confused.example_usage_other_source}
            <div class="mb-3">
              <p class="mb-1 small text-secondary">Confused word:</p>
              <SentenceCard
                text={confused.example_usage_other_target}
                translation={confused.example_usage_other_source}
                slug={confused.example_usage_other_slug || ''}
                target_language_code={target_language_code}
              />
            </div>
            {/if}
            
            {#if confused.notes}
            <p><strong>Notes:</strong> {confused.notes}</p>
            {/if}
            
            {#if confused.mnemonic}
            <p><strong>Mnemonic:</strong> {confused.mnemonic}</p>
            {/if}
          </div>
        </div>
        {/if}
      {/each}
    </div>
  </Card>
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
</style> 