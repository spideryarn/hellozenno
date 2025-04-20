<script lang="ts">
  import type { PageData } from './$types';
  import SourcefileAudioTab from '../components/SourcefileAudioTab.svelte';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  
  export let data: PageData;
  
  const { 
    sourcefileData, 
    textData, 
    target_language_code, 
    sourcedir_slug, 
    sourcefile_slug, 
    language_name,
    available_sourcedirs 
  } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;

  // Generate URLs for view and download - audio file
  $: audioUrl = getApiUrl(
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
</script>

<svelte:head>
  <title>{sourcefile.filename} | Audio | {sourcedir.path}</title>
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
  activeTab="audio"
  {data}
>
  <SourcefileAudioTab 
    {audioUrl}
    {downloadUrl}
    filename={sourcefile.filename}
  />
</SourcefileLayout>