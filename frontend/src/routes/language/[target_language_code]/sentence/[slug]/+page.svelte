<script lang="ts">
  import type { PageData } from './$types';
  import Sentence from '$lib/components/Sentence.svelte';
  import { Breadcrumbs } from '$lib';
  import type { BreadcrumbItem } from '$lib';
  import { SITE_NAME } from '$lib/config';
  import { truncate } from '$lib/utils';
  
  // Data from server-side load function
  export let data: PageData;
  // Destructure supabase and session from data to pass to the Sentence component
  const { supabase, session } = data;
  
  // Build breadcrumb items reactively
  $: items = [
    { label: 'Home', href: '/' },
    { label: 'Languages', href: '/languages' },
    { label: data.sentence?.target_language_code ?? 'Language', href: `/language/${data.sentence?.target_language_code}/sources` },
    { label: 'Sentences', href: `/language/${data.sentence?.target_language_code}/sentences` },
    { label: 'Sentence' }
  ] as BreadcrumbItem[];
</script>

<svelte:head>
  <title>{truncate(data.sentence.text, 30)} | Sentence | {data.sentence.target_language_code} | {SITE_NAME}</title>
  <meta name="description" content="{data.sentence.translation || data.sentence.text}">
</svelte:head>

<div class="sentence-view">
  <Breadcrumbs {items} />
  
  <Sentence 
    sentence={data.sentence}
    metadata={data.metadata}
    enhanced_sentence_text={data.enhanced_sentence_text}
    supabase={supabase}
    session={session}
  />
</div>

<style>
  .sentence-view {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
</style> 