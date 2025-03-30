<script lang="ts">
  import type { PageData } from './$types';
  import SourcefileHeader from './components/SourcefileHeader.svelte';
  import SourcefileText from './components/SourcefileText.svelte';
  import SourcefileWords from './components/SourcefileWords.svelte';
  import SourcefilePhrases from './components/SourcefilePhrases.svelte';
  
  export let data: PageData;
  
  const { sourcefileData, textData, wordsData, phrasesData, language_code, sourcedir_slug, sourcefile_slug, language_name } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
  
  // Active tab (default to 'text')
  let activeTab = 'text';
</script>

<svelte:head>
  <title>{sourcefile.filename} | {sourcedir.path}</title>
</svelte:head>

<div class="container">
  <nav class="breadcrumb">
    <a href="/">Home</a>
    » <a href="/languages">Languages</a>
    » <a href="/language/{language_code}/sources">{language_name || language_code}</a>
    » <a href="/language/{language_code}/source/{sourcedir_slug}">{sourcedir.path}</a>
    » {sourcefile.filename}
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
  
  <div class="tabs">
    <a 
      href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}" 
      class="tab {activeTab === 'text' ? 'active' : ''}" 
      on:click|preventDefault={() => activeTab = 'text'}
    >
      Text
    </a>
    <a 
      href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/words" 
      class="tab {activeTab === 'words' ? 'active' : ''}"
    >
      Words <small>({stats.wordforms_count})</small>
    </a>
    <a 
      href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/phrases" 
      class="tab {activeTab === 'phrases' ? 'active' : ''}"
    >
      Phrases <small>({stats.phrases_count})</small>
    </a>
  </div>
  
  <div class="tab-content">
    {#if activeTab === 'text'}
      <SourcefileText 
        {sourcefile}
        enhanced_text={sourcefile.enhanced_text}
        text_target={sourcefile.text_target}
        text_english={sourcefile.text_english}
      />
    {:else if activeTab === 'words'}
      <SourcefileWords 
        wordforms={wordsData.wordforms || []}
        {language_code}
      />
    {:else if activeTab === 'phrases'}
      <SourcefilePhrases 
        phrases={phrasesData.phrases || []}
        {language_code}
      />
    {/if}
  </div>
</div>

<style>
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  .breadcrumb {
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
  }
  
  .breadcrumb a {
    text-decoration: none;
  }
  
  .breadcrumb a:hover {
    text-decoration: underline;
  }
  
  .tabs {
    display: flex;
    margin: 2rem 0 0.5rem;
    border-bottom: 1px solid #ccc;
  }
  
  .tab {
    padding: 0.5rem 1rem;
    margin-right: 0.5rem;
    border: 1px solid #ccc;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    text-decoration: none;
  }
  
  .tab.active {
    background-color: #4CAD53;
    color: white;
    border-color: #4CAD53;
  }
  
  .tab-content {
    margin-top: 1.5rem;
    padding-bottom: 2rem;
  }
</style> 