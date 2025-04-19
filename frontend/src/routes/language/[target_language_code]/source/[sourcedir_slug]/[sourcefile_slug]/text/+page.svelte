<script lang="ts">
  import type { PageData } from './$types';
  import SourcefileText from '../components/SourcefileText.svelte';
  import SourcefileLayout from '$lib/components/SourcefileLayout.svelte';
  
  export let data: PageData;
  
  const { 
    sourcefileData, 
    textData, 
    wordsData, 
    phrasesData, 
    target_language_code, 
    sourcedir_slug, 
    sourcefile_slug, 
    language_name,
    recognizedWords,  // New structured data
    enhanced_text,    // Legacy HTML data
    available_sourcedirs // Available sourcedirs for dropdown
  } = data;
  
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
  <title>{sourcefile.filename} | {sourcedir.path}</title>
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
  />
</SourcefileLayout> 