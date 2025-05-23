<script lang="ts">
  import type { Sourcefile, Sourcedir, Metadata, Navigation, Stats } from '$lib/types/sourcefile';
  import SourcefileHeader from '../../routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte';
  import { NavTabs } from '$lib';
  
  export let sourcefile: Sourcefile;
  export let sourcedir: Sourcedir;
  export let metadata: Metadata;
  export let navigation: Navigation;
  export let stats: Stats;
  export let target_language_code: string;
  export let sourcedir_slug: string;
  export let sourcefile_slug: string;
  export let language_name: string;
  export let available_sourcedirs: any[] = [];
  export let activeTab: 'text' | 'words' | 'phrases' | 'translation' | 'image' | 'audio';
  export let data: any;
  
  // Determine if this is an image or audio file
  $: isImageFile = sourcefile.sourcefile_type === 'image';
  $: isAudioFile = sourcefile.sourcefile_type === 'audio' || 
                  sourcefile.sourcefile_type === 'youtube_audio';
                  
  // Set up tabs for navigation
  $: tabs = [
    {
      label: 'Text',
      href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/text`,
      active: activeTab === 'text'
    },
    {
      label: 'Translation',
      href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/translation`,
      active: activeTab === 'translation'
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
    // Conditional tabs based on file type
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

<div class="container py-4">
  <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2 mb-3">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb mb-0">
        <li class="breadcrumb-item"><a href="/">Home</a></li>
        <li class="breadcrumb-item"><a href="/languages">Languages</a></li>
        <li class="breadcrumb-item"><a href="/language/{target_language_code}/sources">{language_name || target_language_code}</a></li>
        <li class="breadcrumb-item"><a href="/language/{target_language_code}/source/{sourcedir_slug}">{sourcedir.path}</a></li>
        <li class="breadcrumb-item"><a href="/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text">{sourcefile.filename}</a></li>
        <li class="breadcrumb-item active" aria-current="page">{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</li>
      </ol>
    </nav>
    
    <!-- Search box is now provided by the parent language layout -->
  </div>
  
  <SourcefileHeader 
    {sourcefile}
    {sourcedir}
    {metadata}
    {navigation}
    {stats}
    {target_language_code}
    {sourcedir_slug}
    {sourcefile_slug}
    {available_sourcedirs}
    data={{ ...data, session: data.session, supabase: data.supabase }}
  />
  
  <NavTabs {tabs} />

  <slot />
</div>

<style>
  .breadcrumb {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
  }
  
  .container {
    max-width: 100%;
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  /* For larger screens, constrain width for better readability */
  @media (min-width: 992px) {
    .container {
      max-width: 90%;
      margin: 0 auto;
    }
  }
  
  /* For mobile devices, maximize content width */
  @media (max-width: 768px) {
    .container {
      padding-left: 10px;
      padding-right: 10px;
    }
  }
</style> 