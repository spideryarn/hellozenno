<script lang="ts">
  import type { PageData } from './$types';
  import Sentence from '$lib/components/Sentence.svelte';
  import { SITE_NAME } from '$lib/config';
  import { truncate } from '$lib/utils';
  
  // Data from server-side load function
  export let data: PageData;
</script>

<svelte:head>
  <title>{truncate(data.sentence.text, 30)} | Sentence | {data.sentence.target_language_code} | {SITE_NAME}</title>
  <meta name="description" content="{data.sentence.translation || data.sentence.text}">
</svelte:head>

<div class="sentence-view">
  <div class="breadcrumbs">
    <a href="/">Home</a> » 
    <a href="/languages">Languages</a> » 
    <a href="/language/{data.sentence.target_language_code}/sources">
      {data.sentence.target_language_code}
    </a> » 
    <span>Sentence</span>
  </div>
  
  <Sentence 
    sentence={data.sentence}
    metadata={data.metadata}
    enhanced_sentence_text={data.enhanced_sentence_text}
  />
</div>

<style>
  .sentence-view {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  .breadcrumbs {
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
    color: #666;
  }
  
  .breadcrumbs a {
    color: #333;
    text-decoration: none;
  }
  
  .breadcrumbs a:hover {
    text-decoration: underline;
  }
</style> 