<script lang="ts">
  import type { PageData } from './$types';
  import { PhraseCard } from '$lib';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  import SourcefilePhrases from '../components/SourcefilePhrases.svelte';
  import { SITE_NAME } from '$lib/config';
  import { truncate } from '$lib/utils';
  
  export let data: PageData;
  
  const { sourcefileData, textData, phrasesData, target_language_code, sourcedir_slug, sourcefile_slug, language_name, available_sourcedirs } = data;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
  const phrases = phrasesData.phrases || [];
</script>

<svelte:head>
  <title>{truncate(sourcefile.filename, 30)} | Phrases | {language_name} | {SITE_NAME}</title>
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
  activeTab="phrases"
  {data}
>
  <SourcefilePhrases
    {phrases}
    {target_language_code}
    {navigation}
    {sourcedir_slug}
    {sourcefile_slug}
  />
</SourcefileLayout>

<style>
  /* Removed unused styles - handled by child component SourcefilePhrases */
</style> 