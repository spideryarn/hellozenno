<script lang="ts">
  import type { PageData } from './$types';  
  import { Card, LemmaCard, MetadataCard } from '$lib';
  import SentenceCard from '$lib/components/SentenceCard.svelte';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  
  export let data: PageData;
  const { lemmaData } = data;
  
  // Unwrap the data from the response
  const lemma_metadata = lemmaData.lemma_metadata;
  const target_language_code = lemmaData.target_language_code;
  const target_language_name = lemmaData.target_language_name;
  const metadata = lemmaData.metadata;
  
  // Generate API URL for delete action
  const deleteUrl = getApiUrl(RouteName.LEMMA_VIEWS_DELETE_LEMMA_VW, {
    target_language_code,
    lemma: lemma_metadata.lemma
  });
  
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
          <li class="breadcrumb-item"><a href="/">Languages</a></li>
          <li class="breadcrumb-item"><a href="/language/{target_language_code}/sources">{target_language_name}</a></li>
          <li class="breadcrumb-item"><a href="/language/{target_language_code}/lemmas">Lemmas</a></li>
          <li class="breadcrumb-item active" aria-current="page">{lemma_metadata.lemma}</li>
        </ol>
      </nav>
    </div>
  </div>
  
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

  <div class="mb-4">
    <form action={deleteUrl} method="POST" 
          on:submit={handleDeleteSubmit}>
      <button type="submit" class="btn btn-danger">Delete lemma</button>
    </form>
  </div>
  
  <Card title="Lemma Details">
    <div class="translations mb-3">
      <p><strong>Translation:</strong> 
        {#if lemma_metadata.translations && lemma_metadata.translations.length > 0}
          {lemma_metadata.translations.join('; ')}
        {:else}
          No translation available
        {/if}
      </p>
    </div>
    
    <p><strong>Part of Speech:</strong> {lemma_metadata.part_of_speech || 'Not available'}</p>
    
    <div class="etymology mb-3">
      <p><strong>Etymology:</strong> {lemma_metadata.etymology || 'Not available'}</p>
    </div>
    
    <div class="commonality mb-3">
      <p><strong>Commonality:</strong> {Math.round((lemma_metadata.commonality || 0) * 100)}%</p>
    </div>
    
    <div class="guessability mb-3">
      <p><strong>Guessability:</strong> {Math.round((lemma_metadata.guessability || 0) * 100)}%</p>
    </div>
    
    <div class="register mb-3">
      <p><strong>Register:</strong> {lemma_metadata.register || 'Not available'}</p>
    </div>
  </Card>
  
  {#if lemma_metadata.example_usage && lemma_metadata.example_usage.length > 0}
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
  
  {#if lemma_metadata.mnemonics && lemma_metadata.mnemonics.length > 0}
  <Card title="Mnemonics" className="mt-4">
    <ul class="list-group">
      {#each lemma_metadata.mnemonics as mnemonic}
        <li class="list-group-item">{mnemonic}</li>
      {/each}
    </ul>
  </Card>
  {/if}
  
  {#if lemma_metadata.related_words_phrases_idioms && lemma_metadata.related_words_phrases_idioms.length > 0}
  <Card title="Related Words, Phrases & Idioms" className="mt-4">
    <div class="row row-cols-1 row-cols-md-2 g-3">
      {#each lemma_metadata.related_words_phrases_idioms as related}
        <div class="col">
          <LemmaCard 
            lemma={related} 
            target_language_code={target_language_code} 
            showDetails={false} 
          />
        </div>
      {/each}
    </div>
  </Card>
  {/if}
  
  {#if lemma_metadata.synonyms && lemma_metadata.synonyms.length > 0}
  <Card title="Synonyms" className="mt-4">
    <div class="row row-cols-1 row-cols-md-2 g-3">
      {#each lemma_metadata.synonyms as synonym}
        <div class="col">
          <LemmaCard 
            lemma={synonym} 
            target_language_code={target_language_code} 
            showDetails={false} 
          />
        </div>
      {/each}
    </div>
  </Card>
  {/if}
  
  {#if lemma_metadata.antonyms && lemma_metadata.antonyms.length > 0}
  <Card title="Antonyms" className="mt-4">
    <div class="row row-cols-1 row-cols-md-2 g-3">
      {#each lemma_metadata.antonyms as antonym}
        <div class="col">
          <LemmaCard 
            lemma={antonym}
            target_language_code={target_language_code} 
            showDetails={false} 
          />
        </div>
      {/each}
    </div>
  </Card>
  {/if}
  
  {#if lemma_metadata.example_wordforms && lemma_metadata.example_wordforms.length > 0}
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
  
  {#if lemma_metadata.cultural_context}
  <Card title="Cultural Context" className="mt-4">
    <p>{lemma_metadata.cultural_context}</p>
  </Card>
  {/if}
  
  {#if lemma_metadata.easily_confused_with && lemma_metadata.easily_confused_with.length > 0 && lemma_metadata.easily_confused_with[0].lemma}
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
                slug=""
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
                slug=""
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