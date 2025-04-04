<script lang="ts">
  import type { PageData } from './$types';
  import SourcefileTranslation from '../components/SourcefileTranslation.svelte';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  
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
  <title>Translation: {sourcefile.filename} | {sourcedir.path}</title>
</svelte:head>

<SourcefileLayout
  {sourcefile}
  {sourcedir}
  {metadata}
  {navigation}
  {stats}
  {language_code}
  {sourcedir_slug}
  {sourcefile_slug}
  {language_name}
  activeTab="translation"
>
  <SourcefileTranslation 
    {sourcefile}
    text_english={sourcefile.text_english}
  />
</SourcefileLayout> 