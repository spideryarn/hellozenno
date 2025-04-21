<script lang="ts">
  import type { PageData } from './$types';
  import { WordformCard } from '$lib';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  import SourcefileWords from '../components/SourcefileWords.svelte';
  import { SITE_NAME } from '$lib/config';
  import { truncate } from '$lib/utils';
  
  export let data: PageData;
  
  const { sourcefileData, textData, wordsData, target_language_code, sourcedir_slug, sourcefile_slug, language_name, available_sourcedirs } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
  const wordforms = wordsData.wordforms || [];
</script>

<svelte:head>
  <title>{truncate(sourcefile.filename, 30)} | Words | {language_name} | {SITE_NAME}</title>
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
  activeTab="words"
  {data}
>
  <SourcefileWords
    {wordforms}
    {target_language_code}
    {navigation}
    {sourcedir_slug}
    {sourcefile_slug}
  />
</SourcefileLayout>

<style>
  /* Removed unused styles - handled by child component SourcefileWords */
</style> 