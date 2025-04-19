<script lang="ts">
  import type { PageData } from './$types';
  import { page } from '$app/stores';
  import { NavTabs } from '$lib';
  import SourcefileHeader from './components/SourcefileHeader.svelte';
  import SourcefileText from './components/SourcefileText.svelte';
  import SourcefileWords from './components/SourcefileWords.svelte';
  import SourcefilePhrases from './components/SourcefilePhrases.svelte';
  import SourcefileImageTab from './components/SourcefileImageTab.svelte';
  import SourcefileAudioTab from './components/SourcefileAudioTab.svelte';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  
  export let data: PageData;
  
  // Destructure the original data structure
  const { 
    sourcefileData, 
    textData, 
    wordsData, 
    phrasesData, 
    target_language_code, 
    sourcedir_slug, 
    sourcefile_slug, 
    language_name 
  } = data;
  
  // Extract nested data needed by child components from textData
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  
  // Explicitly get stats from the top-level data object
  const stats = data.stats;
  
  // Determine active tab based on URL path
  $: path = $page.url.pathname;
  $: activeTab = 
    path.endsWith('/words') ? 'words' :
    path.endsWith('/phrases') ? 'phrases' :
    path.endsWith('/image') ? 'image' :
    path.endsWith('/audio') ? 'audio' :
    'text';
  
  // Generate URLs for view and download
  $: viewUrl = getApiUrl(
    RouteName.SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW,
    {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug
    }
  );

  $: downloadUrl = getApiUrl(
    RouteName.SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW,
    {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug
    }
  );
  
  // Determine if this is an image or audio file
  $: isImageFile = sourcefile.sourcefile_type === 'image';
  $: isAudioFile = sourcefile.sourcefile_type === 'audio' || 
                  sourcefile.sourcefile_type === 'youtube_audio';
  
  // Build tabs array with conditional tabs based on file type
  $: tabs = [
    { 
      label: 'Text', 
      href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/text`,
      active: activeTab === 'text' 
    },
    { 
      label: 'Words', 
      href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/words`,
      count: stats.wordforms_count,
      active: activeTab === 'words' 
    },
    { 
      label: 'Phrases', 
      href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/phrases`,
      count: stats.phrases_count,
      active: activeTab === 'phrases' 
    },
    ...(isImageFile ? [{ 
      label: 'Image', 
      href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/image`,
      active: activeTab === 'image' 
    }] : []),
    
    ...(isAudioFile ? [{ 
      label: 'Audio', 
      href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/audio`,
      active: activeTab === 'audio' 
    }] : [])
  ];
</script>

<svelte:head>
  <title>{sourcefile.filename} | {sourcedir.path}</title>
</svelte:head>

<div class="container">
  <nav class="breadcrumb">
    <a href="/">Home</a>
    » <a href="/languages">Languages</a>
    » <a href="/language/{target_language_code}/sources">{language_name || target_language_code}</a>
    » <a href="/language/{target_language_code}/source/{sourcedir_slug}">{sourcedir.path}</a>
    » {sourcefile.filename}
  </nav>

  <SourcefileHeader 
    {sourcefile}
    {sourcedir}
    {metadata}
    {navigation}
    {stats}
    {target_language_code}
    {sourcedir_slug}
    {sourcefile_slug}
    available_sourcedirs={sourcefileData.available_sourcedirs || []}
  />
  
  <NavTabs {tabs} />
  
  <div class="tab-content">
    {#if activeTab === 'text'}
      <SourcefileText 
        enhanced_text={sourcefile.enhanced_text}
        text_target={sourcefile.text_target}
        {target_language_code}
      />
    {:else if activeTab === 'words'}
      <SourcefileWords 
        wordforms={wordsData.wordforms || []}
        {target_language_code}
      />
    {:else if activeTab === 'phrases'}
      <SourcefilePhrases 
        phrases={phrasesData.phrases || []}
        {target_language_code}
      />
    {:else if activeTab === 'image' && isImageFile}
      <SourcefileImageTab 
        {viewUrl}
        {downloadUrl}
        filename={sourcefile.filename}
      />
    {:else if activeTab === 'audio' && isAudioFile}
      <SourcefileAudioTab 
        audioUrl={viewUrl}
        {downloadUrl}
        filename={sourcefile.filename}
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
  
  .tab-content {
    margin-top: 1.5rem;
    padding-bottom: 2rem;
  }
</style>