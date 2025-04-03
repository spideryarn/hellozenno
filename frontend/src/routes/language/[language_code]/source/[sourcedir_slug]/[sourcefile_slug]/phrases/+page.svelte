<script lang="ts">
  import type { PageData } from './$types';
  import { PhraseCard } from '$lib';
  import SourcefileHeader from '../components/SourcefileHeader.svelte';
  
  export let data: PageData;
  
  const { sourcefileData, textData, phrasesData, language_code, sourcedir_slug, sourcefile_slug, language_name } = data;
  
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

<div class="container py-4">
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="/">Home</a></li>
      <li class="breadcrumb-item"><a href="/languages">Languages</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/sources">{language_name || language_code}</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/source/{sourcedir_slug}">{sourcedir.path}</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text">{sourcefile.filename}</a></li>
      <li class="breadcrumb-item active" aria-current="page">Phrases</li>
    </ol>
  </nav>
  
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
    <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/words" class="tab">
      Words <small>({stats.wordforms_count || 0})</small>
    </a>
    <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/phrases" class="tab active">
      Phrases <small>({stats.phrases_count || phrases.length})</small>
    </a>
  </div>

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