<script lang="ts">
  import type { PageData } from './$types';
  import { MetadataCard } from '$lib';
  import SourcefileHeader from './components/SourcefileHeader.svelte';
  import SourcefileText from './components/SourcefileText.svelte';
  import SourcefileWords from './components/SourcefileWords.svelte';
  import SourcefilePhrases from './components/SourcefilePhrases.svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  export let data: PageData;
  
  const { sourcefileData, textData, wordsData, phrasesData, language_code, sourcedir_slug, sourcefile_slug, language_name } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
  
  // Determine active tab from URL path
  $: activeTab = $page.url.pathname.endsWith('/text') 
    ? 'text' 
    : $page.url.pathname.endsWith('/words')
      ? 'words'
      : $page.url.pathname.endsWith('/phrases')
        ? 'phrases'
        : 'text';

  // Function to handle tab clicks and update URL
  function handleTabClick(tab: string) {
    const baseUrl = `/language/${language_code}/source/${sourcedir_slug}/${sourcefile_slug}`;
    goto(`${baseUrl}/${tab}`);
  }

  // If we're at the base URL without a tab, redirect to the text tab
  $: if (!$page.url.pathname.includes('/text') && 
         !$page.url.pathname.includes('/words') && 
         !$page.url.pathname.includes('/phrases') && 
         sourcefile_slug) {
    const baseUrl = `/language/${language_code}/source/${sourcedir_slug}/${sourcefile_slug}`;
    goto(`${baseUrl}/text`, { replaceState: true });
  }
</script>

<svelte:head>
  <title>{sourcefile.filename} | {sourcedir.path}</title>
</svelte:head>

<div class="container">
  <div class="row mb-4">
    <div class="col">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/">Home</a></li>
          <li class="breadcrumb-item"><a href="/language">Languages</a></li>
          <li class="breadcrumb-item"><a href="/language/{language_code}/sources">{language_name || language_code}</a></li>
          <li class="breadcrumb-item"><a href="/language/{language_code}/source/{sourcedir_slug}">{sourcedir.path}</a></li>
          <li class="breadcrumb-item active" aria-current="page">{sourcefile.filename}</li>
        </ol>
      </nav>
    </div>
  </div>

  <div class="row mb-3">
    <div class="col-md-8">
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
    </div>
    <div class="col-md-4 text-md-end">
      <MetadataCard {metadata} />
    </div>
  </div>
  
  <div class="tabs">
    <a 
      href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text" 
      class="tab {activeTab === 'text' ? 'active' : ''}" 
      on:click|preventDefault={() => handleTabClick('text')}
    >
      Text
    </a>
    <a 
      href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/words" 
      class="tab {activeTab === 'words' ? 'active' : ''}" 
      on:click|preventDefault={() => handleTabClick('words')}
    >
      Words <small>({stats.wordforms_count})</small>
    </a>
    <a 
      href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/phrases" 
      class="tab {activeTab === 'phrases' ? 'active' : ''}" 
      on:click|preventDefault={() => handleTabClick('phrases')}
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
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
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