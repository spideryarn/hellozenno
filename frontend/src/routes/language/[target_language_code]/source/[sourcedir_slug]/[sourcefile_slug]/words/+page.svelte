<script lang="ts">
  import type { PageData } from './$types';
  import { WordformCard } from '$lib';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  
  export let data: PageData;
  
  const { sourcefileData, textData, wordsData, target_language_code, sourcedir_slug, sourcefile_slug, language_name, available_sourcedirs } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
  const wordforms = wordsData.wordforms || [];
</script>

<svelte:head>
  <title>Words: {sourcefile.filename} | {sourcedir.path}</title>
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
  activeTab="words"
  {data}
>
  <h2>Words ({wordforms.length})</h2>
  
  {#if wordforms.length === 0}
    <p class="no-content"><em>No words available for this file yet. Try processing the file first.</em></p>
  {:else}
    <div class="wordform-grid">
      {#each wordforms as wordform}
        <div class={wordform.new_in_file ? 'new-word' : ''}>
          <WordformCard
            wordform={wordform.wordform}
            translations={wordform.translations}
            part_of_speech={wordform.pos}
            lemma={wordform.lemma}
            target_language_code={target_language_code}
          />
        </div>
      {/each}
    </div>
  {/if}
</SourcefileLayout>

<style>
  .wordform-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .new-word {
    position: relative;
  }
  
  .new-word::before {
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