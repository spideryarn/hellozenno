<script lang="ts">
  import type { PageData } from './$types';
  import { MetadataCard } from '$lib';
  import SourcefileHeader from '../components/SourcefileHeader.svelte';
  import SourcefileText from '../components/SourcefileText.svelte';
  
  export let data: PageData;
  
  const { sourcefileData, textData, wordsData, phrasesData, language_code, sourcedir_slug, sourcefile_slug, language_name } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
</script>

<svelte:head>
  <title>{sourcefile.filename} | {sourcedir.path}</title>
</svelte:head>

<div class="container py-4">
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="/">Home</a></li>
      <li class="breadcrumb-item"><a href="/languages">Languages</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/sources">{language_name || language_code}</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/source/{sourcedir_slug}">{sourcedir.path}</a></li>
      <li class="breadcrumb-item"><a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text">{sourcefile.filename}</a></li>
      <li class="breadcrumb-item active" aria-current="page">Text</li>
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
    <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text" class="tab active">Text</a>
    <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/words" class="tab">
      Words <small>({stats.wordforms_count || wordsData.wordforms.length || 0})</small>
    </a>
    <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/phrases" class="tab">
      Phrases <small>({stats.phrases_count || phrasesData.phrases.length || 0})</small>
    </a>
  </div>

  <SourcefileText 
    {sourcefile}
    enhanced_text={sourcefile.enhanced_text}
    text_target={sourcefile.text_target}
    text_english={sourcefile.text_english}
  />
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
</style> 