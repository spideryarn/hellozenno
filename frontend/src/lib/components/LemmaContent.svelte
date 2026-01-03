<script lang="ts">
  import { Card, LemmaAudioButton } from '$lib';
  import SentenceCard from '$lib/components/SentenceCard.svelte';
  import LemmaCard from '$lib/components/LemmaCard.svelte';
  import { createEventDispatcher } from 'svelte';
  import { page } from '$app/stores';
  import type { Lemma } from '$lib/types';
  
  // Accept either a full Lemma, partial Lemma data, or null
  // Partial is used when data comes from LemmaDetails which may have incomplete data
  export let lemma_metadata: Lemma | Partial<Lemma> | null;
  export let target_language_code: string;
  export let showFullLink: boolean = false; // Whether to show the "View Full Lemma Page" link
  export let isAuthError: boolean = false; // To hide sections if auth error exists
  export let context_sentence: string | undefined = undefined; // Optional context from sourcefile
  export let context_sentence_full: string | undefined = undefined; // Full sentence for tooltip
  export let source_wordforms: string[] = []; // Wordforms for this lemma present in the current sourcefile
  export let showIgnore: boolean = false; // Show an ignore button (dispatches 'ignore')
  export let source_sentences: string[] = []; // Sentences/snippets from source containing lemma or wordforms
  export let source_sentences_full: string[] = []; // Full sentences aligned to source_sentences for tooltips
  
  // Supabase client is provided via root layout data
  $: supabaseClient = $page?.data?.supabase ?? null;

  const dispatch = createEventDispatcher();
  let lemmaHref: string | undefined = undefined;
  $: lemmaHref = (lemma_metadata?.lemma && target_language_code)
    ? `/language/${target_language_code}/lemma/${encodeURIComponent(lemma_metadata.lemma)}`
    : undefined;

  function handleIgnore() {
    if (lemma_metadata?.lemma) {
      dispatch('ignore', { lemma: lemma_metadata.lemma });
    }
  }
</script>

{#if showFullLink && lemma_metadata?.lemma}
  <!-- Link to full lemma page -->
  <div class="text-center mb-4">
    <a href={lemmaHref} 
      class="btn btn-primary hz-foreign-text fw-bold">
      View Full Lemma Page: {lemma_metadata.lemma}
    </a>
  </div>
{/if}

<!-- Basic Lemma Details -->
<Card className="lemma-details-card">
  <svelte:fragment slot="title">
    <div class="d-flex align-items-center justify-content-between gap-2">
      <h2 class="card-title mb-0 d-flex align-items-center gap-2">
        Lemma:
        {#if lemma_metadata?.lemma}
          <a
            href={lemmaHref}
            target="_blank"
            rel="noopener noreferrer"
            class="hz-foreign-text hz-lemma-link ms-1"
          >{lemma_metadata.lemma}</a>
          <!-- Lemma audio icon next to lemma -->
          <LemmaAudioButton
            target_language_code={target_language_code}
            lemma={lemma_metadata.lemma}
            supabaseClient={supabaseClient}
          />
        {:else}
          <span>Lemma</span>
        {/if}
      </h2>
      {#if showIgnore && lemma_metadata?.lemma}
        <button class="btn btn-sm btn-outline-secondary" on:click={handleIgnore} title="Ignore this lemma">
          Ignore
        </button>
      {/if}
    </div>
  </svelte:fragment>
  {#if context_sentence}
    <blockquote class="context-sentence hz-foreign-text" title={context_sentence_full || context_sentence}>{context_sentence}</blockquote>
  {/if}
  <div class="translations mb-3">
    <p>
      <strong>Translation:</strong>
      {#if lemma_metadata?.translations && lemma_metadata.translations.length > 0}
        {lemma_metadata.translations.join('; ')}
      {:else}
        <span class="text-muted">No translation available</span>
      {/if}
      {#if lemma_metadata?.part_of_speech}
        <span class="text-muted small ms-2">({lemma_metadata.part_of_speech})</span>
      {/if}
    </p>
  </div>
  {#if source_sentences && source_sentences.length > 0}
    <div class="mb-3">
      <strong>In this text (sentences):</strong>
      <ul class="mt-2 mb-0">
        {#each source_sentences as s, i}
          <li class="hz-foreign-text" title={(source_sentences_full && source_sentences_full[i]) ? source_sentences_full[i] : s}>{s}</li>
        {/each}
      </ul>
    </div>
  {/if}
  
  {#if source_wordforms && source_wordforms.length > 0}
    <div class="mb-2">
      <strong>In this text:</strong>
      <span class="ms-1">
        {#each source_wordforms as form, i}
          <a
            href={`/language/${target_language_code}/wordform/${encodeURIComponent(form)}`}
            target="_blank"
            rel="noopener noreferrer"
            class="hz-foreign-text text-decoration-underline"
          >{form}</a>{i < source_wordforms.length - 1 ? ', ' : ''}
        {/each}
      </span>
    </div>
  {/if}
  
  <div class="etymology mb-3">
    <p><strong>Etymology:</strong> {lemma_metadata?.etymology || '-'}</p>
  </div>
  
  <slot name="auth-prompt"></slot>
</Card>

{#if !isAuthError}
  <!-- Example Usage Section -->
  {#if lemma_metadata?.example_usage && lemma_metadata.example_usage.length > 0}
    <Card title="Example Usage" className="mt-4">
      <div class="d-flex flex-column gap-3">
        {#each lemma_metadata.example_usage as example}
          <SentenceCard 
            text={example.phrase} 
            translation={example.translation} 
            slug={example.slug || ''} 
            target_language_code={target_language_code}
            supabaseClient={supabaseClient}
          />
        {/each}
      </div>
    </Card>
  {/if}
  
  <!-- Mnemonics Section -->
  {#if lemma_metadata?.mnemonics && lemma_metadata.mnemonics.length > 0}
    <Card title="Mnemonics" className="mt-4">
      <ul class="list-group">
        {#each lemma_metadata.mnemonics as mnemonic}
          <li class="list-group-item">{mnemonic}</li>
        {/each}
      </ul>
    </Card>
  {/if}
  
  <!-- Related Words Section -->
  {#if lemma_metadata?.related_words_phrases_idioms && lemma_metadata.related_words_phrases_idioms.length > 0}
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
  
  <!-- Synonyms Section -->
  {#if lemma_metadata?.synonyms && lemma_metadata.synonyms.length > 0}
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
  
  <!-- Antonyms Section -->
  {#if lemma_metadata?.antonyms && lemma_metadata.antonyms.length > 0}
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
  
  <!-- Example Wordforms Section -->
  {#if lemma_metadata?.example_wordforms && lemma_metadata.example_wordforms.length > 0}
    <Card title="Example Wordforms" className="mt-4">
      <div class="list-group">
        {#each lemma_metadata.example_wordforms as form}
          <a href={`/language/${target_language_code}/wordform/${encodeURIComponent(form)}`} 
             class="list-group-item list-group-item-action hz-foreign-text">
            {form}
          </a>
        {/each}
      </div>
    </Card>
  {/if}
  
  <!-- Cultural Context Section -->
  {#if lemma_metadata?.cultural_context}
    <Card title="Cultural Context" className="mt-4">
      <p>{lemma_metadata.cultural_context}</p>
    </Card>
  {/if}
  
  <!-- Easily Confused With Section -->
  {#if lemma_metadata?.easily_confused_with && lemma_metadata.easily_confused_with.length > 0 && lemma_metadata.easily_confused_with[0].lemma}
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
                  supabaseClient={supabaseClient}
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
                  supabaseClient={supabaseClient}
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
{/if}

<style>
  /* Remove local definition, rely on global hz-foreign-text */
  /* .hz-foreign-text { ... } */

  .context-sentence {
    margin: 0 0 0.75rem 0;
    padding-left: 0.75rem;
    border-left: 3px solid var(--hz-color-primary-green);
    font-size: 1.05rem;
  }

  /* Remove hover accent/animation from Card within Priority Words */
  :global(.lemma-details-card.card::before) {
    display: none;
  }
  :global(.lemma-details-card.card:hover) {
    transform: none;
    box-shadow: none;
  }
  :global(.lemma-details-card .card-title) {
    max-width: 100%;
    min-height: unset;
  }
</style>