<script lang="ts">
  import type { PageData } from './$types';
  import { WordformCard, MetadataCard } from '$lib';
  import SourcefileHeader from '../components/SourcefileHeader.svelte';
  
  export let data: PageData;
  
  const { sourcefileData, textData, wordsData, language_code, sourcedir_slug, sourcefile_slug, language_name } = data;
  
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

<div class="container py-4">
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="/">Home</a></li>
      <li class="breadcrumb-item"><a href="/language">Languages</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/sources">{language_name || language_code}</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/source/{sourcedir_slug}">{sourcedir.path}</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text">{sourcefile.filename}</a></li>
      <li class="breadcrumb-item active" aria-current="page">Words</li>
    </ol>
  </nav>
  
  <div class="row mb-4">
    <div class="col-md-8">
      <h1 class="mb-3">{sourcefile.filename}</h1>
    </div>
    <div class="col-md-4 text-md-end">
      {#if metadata}
        <MetadataCard {metadata} />
      {/if}
    </div>
  </div>

  <SourcefileHeader 
    {sourcefile}
    {sourcedir}
    {metadata}
    {navigation}
    {stats}
    {language_code}
    {sourcedir_slug}
    {sourcefile_slug}
  />
  
  <div class="tabs mb-4">
    <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text" class="tab">Text</a>
    <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/words" class="tab active">
      Words <small>({stats.wordforms_count || wordforms.length})</small>
    </a>
    <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/phrases" class="tab">
      Phrases <small>({stats.phrases_count || 0})</small>
    </a>
  </div>

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
            language_code={language_code}
          />
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .breadcrumb {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    margin-bottom: 1.5rem;
  }
  
  .tabs {
    display: flex;
    margin: 1.5rem 0 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .tab {
    padding: 0.75rem 1.25rem;
    margin-right: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    text-decoration: none;
    background-color: rgba(255, 255, 255, 0.03);
    color: var(--bs-secondary, #6c757d);
    transition: all 0.2s ease;
  }
  
  .tab:hover {
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  .tab.active {
    background-color: var(--bs-primary, #4CAD53);
    color: white;
    border-color: var(--bs-primary, #4CAD53);
  }
  
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