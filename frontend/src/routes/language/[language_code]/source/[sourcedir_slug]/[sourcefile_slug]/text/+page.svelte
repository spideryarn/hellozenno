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

<div class="container-fluid text-container">
  <div class="row">
    <div class="col-lg-10 col-md-11 col-sm-12 mx-auto px-md-4 px-2">
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
      
      <div class="tabs">
        <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text" class="tab active">
          Text
        </a>
        <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/words" class="tab">
          Words ({stats.wordforms_count})
        </a>
        <a href="/language/{language_code}/source/{sourcedir_slug}/{sourcefile_slug}/phrases" class="tab">
          Phrases ({stats.phrases_count})
        </a>
      </div>
      
      <SourcefileText 
        {sourcefile}
        enhanced_text={sourcefile.enhanced_text}
        text_target={sourcefile.text_target}
        text_english={sourcefile.text_english}
      />
    </div>
  </div>
</div>

<style>
  .text-container {
    max-width: 100%;
    padding: 0;
  }
  
  /* Increase content width and reduce margins */
  @media (min-width: 992px) {
    .text-container .row > div {
      max-width: 90%;
    }
  }
  
  /* For mobile devices, maximize content width */
  @media (max-width: 768px) {
    .text-container .row > div {
      padding-left: 10px;
      padding-right: 10px;
    }
  }
  
  .tabs {
    display: flex;
    margin-bottom: 2rem;
    border-bottom: 1px solid #dee2e6;
  }
  
  .tab {
    padding: 0.5rem 1rem;
    text-decoration: none;
    color: #212529;
    border-bottom: 2px solid transparent;
  }
  
  .tab.active {
    color: #4CAD53;
    border-bottom: 2px solid #4CAD53;
    font-weight: bold;
  }
</style> 