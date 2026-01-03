<script lang="ts">
  import type { PageData } from './$types';
  import SourcefileText from '../components/SourcefileText.svelte';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  import { SITE_NAME } from '$lib/config';
  import { truncate, generateMetaDescription } from '$lib/utils';
  import { page } from '$app/stores';
  
  export let data: PageData;
  
  const { 
    sourcefileData, 
    textData, 
    wordsData, 
    phrasesData, 
    target_language_code, 
    sourcedir_slug, 
    sourcefile_slug, 
    recognizedWords,  // New structured data
    enhanced_text,    // Legacy HTML data
    available_sourcedirs // Available sourcedirs for dropdown
  } = data;
  
  // Use language_name from parent layout data (via page store)
  const language_name = $page.data.language_name || target_language_code;
  
  // Extract needed data
  const sourcefile = textData.sourcefile;
  const sourcedir = textData.sourcedir;
  const metadata = textData.metadata;
  const navigation = textData.navigation;
  const stats = textData.stats;
  
  // Debug flag - set to true to see data structure in the console
  const debug = import.meta.env.DEV && false;
  if (debug) {
    console.log('Enhanced Text Page Data:', {
      recognizedWords: recognizedWords?.length,
      sampleWord: recognizedWords?.[0],
      enhanced_text: enhanced_text?.substring(0, 100) + '...',
      text_target: sourcefile.text_target?.substring(0, 100) + '...'
    });
  }
</script>

<svelte:head>
  <title>{truncate(sourcefile.filename, 30)} | Text | {language_name} | {SITE_NAME}</title>
  <meta name="description" content="{generateMetaDescription(
    sourcefile.text_english || sourcefile.text_target || '',
    `${sourcefile.filename} - ${language_name} text source`
  )}">
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
  {data}
  activeTab="text"
>
  <SourcefileText 
    {sourcefile}
    enhanced_text={enhanced_text || sourcefile.enhanced_text}
    text_target={sourcefile.text_target}
    text_english={sourcefile.text_english}
    recognized_words={recognizedWords}
    {target_language_code}
    {navigation}
    {sourcedir_slug}
    {sourcefile_slug}
  />
</SourcefileLayout> 