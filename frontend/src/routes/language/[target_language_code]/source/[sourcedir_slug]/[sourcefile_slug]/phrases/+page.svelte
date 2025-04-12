<script lang="ts">
  import type { PageData } from './$types';
  import { PhraseCard } from '$lib';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  
  export let data: PageData;
  
  const { sourcefileData, textData, phrasesData, target_language_code, sourcedir_slug, sourcefile_slug, language_name, available_sourcedirs } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
  const phrases = phrasesData.phrases || [];
</script>

<svelte:head>
  <title>Phrases: {sourcefile.filename} | {sourcedir.path}</title>
</svelte:head>

<SourcefileLayout
  {sourcefile}
  {sourcedir}
  {metadata}
  {navigation}
  {stats}
  {target_language_code}
  {sourcedir_slug}
  {sourcefile_slug}
  {language_name}
  {available_sourcedirs}
  activeTab="phrases"
>
  <h2>Phrases ({phrases.length})</h2>
  
  {#if phrases.length === 0}
    <p class="no-content"><em>No phrases available for this file yet. Try processing the file first.</em></p>
  {:else}
    <div class="phrase-grid">
      {#each phrases as phrase}
        <div class={phrase.new_in_file ? 'new-phrase' : ''}>
          <PhraseCard
            phrase={phrase.phrase}
            translations={phrase.translations}
            slug={phrase.slug || phrase.phrase.replace(/\s+/g, '-')}
            target_language_code={target_language_code}
          />
        </div>
      {/each}
    </div>
  {/if}
</SourcefileLayout>

<style>
  .phrase-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
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
    background-color: var(--bs-primary, #4CAD53);
    color: white;
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
    border-radius: 1rem;
    z-index: 1;
  }
  
  .no-content {
    color: var(--bs-secondary, #6c757d);
    font-style: italic;
    margin-top: 1rem;
  }
</style> 