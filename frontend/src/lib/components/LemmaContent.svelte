<script lang="ts">
  import { Card } from '$lib';
  import SentenceCard from '$lib/components/SentenceCard.svelte';
  import LemmaCard from '$lib/components/LemmaCard.svelte';
  
  export let lemma_metadata: any;
  export let target_language_code: string;
  export let showFullLink: boolean = false; // Whether to show the "View Full Lemma Page" link
  export let isAuthError: boolean = false; // To hide sections if auth error exists
</script>

{#if showFullLink && lemma_metadata?.lemma}
  <!-- Link to full lemma page -->
  <div class="text-center mb-4">
    <a href="/language/{target_language_code}/lemma/{lemma_metadata.lemma}" 
      class="btn btn-primary hz-foreign-text fw-bold">
      View Full Lemma Page: {lemma_metadata.lemma}
    </a>
  </div>
{/if}

<!-- Basic Lemma Details -->
<Card title="Lemma Details" className="lemma-details-card">
  <div class="translations mb-3">
    <p><strong>Translation:</strong> 
      {#if lemma_metadata?.translations && lemma_metadata.translations.length > 0}
        {lemma_metadata.translations.join('; ')}
      {:else}
        <span class="text-muted">No translation available</span>
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
          <a href="/language/{target_language_code}/wordform/{form}" 
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
{/if}

<style>
  .hz-foreign-text {
    font-style: italic;
    font-family: "Times New Roman", Times, serif;
  }
  
  .lemma-details-card {
    border-top: 3px solid var(--bs-primary);
    background-color: rgba(var(--bs-primary-rgb), 0.03);
  }
</style>