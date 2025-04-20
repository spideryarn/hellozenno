<script lang="ts">
  import type { PageData } from './$types';
  import SourcefileTranslation from '../components/SourcefileTranslation.svelte';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  import { SITE_NAME } from '$lib/config';
  import { truncate } from '$lib/utils';
  
  export let data: PageData;
  
  const { sourcefileData, textData, wordsData, phrasesData, target_language_code, sourcedir_slug, sourcefile_slug, language_name, available_sourcedirs } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
</script>

<svelte:head>
  <title>{truncate(sourcefile.filename, 30)} | Translation | {language_name} | {SITE_NAME}</title>
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
  activeTab="translation"
  {data}
>
  <SourcefileTranslation 
    {sourcefile}
    text_english={sourcefile.text_english}
    {navigation}
    {target_language_code}
    {sourcedir_slug}
    {sourcefile_slug}
  />
</SourcefileLayout> 