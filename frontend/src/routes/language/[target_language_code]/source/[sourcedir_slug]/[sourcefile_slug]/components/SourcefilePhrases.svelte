<script lang="ts">
  import PhraseCard from '$lib/components/PhraseCard.svelte';
  
  interface Phrase {
    id: number;
    phrase: string;
    translation: string;
    frequency: number;
    new_in_file: boolean;
  }
  
  export let phrases: Phrase[] = [];
  export let target_language_code: string;
</script>

<div class="phrases-container">
  <h2>Phrases ({phrases.length})</h2>
  
  {#if phrases.length === 0}
    <p class="no-content"><em>No phrases available for this file yet. Try processing the file first.</em></p>
  {:else}
    <div class="phrase-grid">
      {#each phrases as phrase}
        <div class={phrase.new_in_file ? 'new-phrase' : ''}>
          <PhraseCard
            phrase={phrase.phrase}
            translations={[phrase.translation]}
            slug={phrase.id.toString()}
            {target_language_code}
          />
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .phrases-container {
    margin-top: 1rem;
  }
  
  .phrase-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.25rem;
    margin-top: 1rem;
  }
  
  .new-phrase {
    position: relative;
  }
  
  .new-phrase::before {
    content: "New";
    position: absolute;
    top: -0.5rem;
    right: -0.5rem;
    background-color: #4CAD53;
    color: white;
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
    border-radius: 1rem;
    z-index: 1;
  }
  
  .no-content {
    color: #666;
    font-style: italic;
    margin-top: 1rem;
  }
</style> 