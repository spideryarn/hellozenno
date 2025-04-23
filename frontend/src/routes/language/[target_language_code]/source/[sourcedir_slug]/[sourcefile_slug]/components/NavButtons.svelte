<script lang="ts">
  import { getPageUrl } from '$lib/navigation';
  import CaretDoubleLeft from 'phosphor-svelte/lib/CaretDoubleLeft';
  import CaretDoubleRight from 'phosphor-svelte/lib/CaretDoubleRight';
  import CaretLeft from 'phosphor-svelte/lib/CaretLeft';
  import CaretRight from 'phosphor-svelte/lib/CaretRight';
  import ArrowUp from 'phosphor-svelte/lib/ArrowUp';
  import type { Navigation } from '$lib/types/sourcefile';
  import type { PageType } from '$lib/navigation';
  
  export let navigation: Navigation;
  export let target_language_code: string;
  export let sourcedir_slug: string;
  export let view: string = 'text'; // Default view is 'text', can be 'words', 'phrases', etc.
  
  // Generate navigation URLs using getPageUrl
  $: sourcedirUrl = getPageUrl('sourcedir', {
    target_language_code,
    sourcedir_slug
  });

  // Determine the route name based on the view
  $: routeName = 
    view === 'words' ? 'sourcefile_words' :
    view === 'phrases' ? 'sourcefile_phrases' :
    view === 'translation' ? 'sourcefile_translation' :
    view === 'image' ? 'sourcefile_image' :
    view === 'audio' ? 'sourcefile_audio' :
    'sourcefile_text'; // Default to text view

  // Prepare navigation URLs only if the corresponding slugs exist
  $: firstSourcefileUrl = navigation?.first_slug ? 
    getPageUrl(routeName as PageType, {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.first_slug
    }) : undefined;
    
  $: prevSourcefileUrl = navigation?.prev_slug ? 
    getPageUrl(routeName as PageType, {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.prev_slug
    }) : undefined;
    
  $: nextSourcefileUrl = navigation?.next_slug ? 
    getPageUrl(routeName as PageType, {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.next_slug
    }) : undefined;
    
  $: lastSourcefileUrl = navigation?.last_slug ? 
    getPageUrl(routeName as PageType, {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.last_slug
    }) : undefined;
</script>

<div class="navigation-buttons">
  {#if navigation.is_first}
    <span class="button disabled" title="First file">
      <CaretDoubleLeft size={16} weight="bold" />
    </span>
  {:else if firstSourcefileUrl}
    <a 
      href={firstSourcefileUrl}
      class="button"
      data-sveltekit-reload
      title="First file: '{navigation.first_filename || 'Unknown'}'"
    >
      <CaretDoubleLeft size={16} weight="bold" />
    </a>
  {/if}
  
  {#if navigation.is_first}
    <span class="button disabled" title="Previous file">
      <CaretLeft size={16} weight="bold" />
    </span>
  {:else if prevSourcefileUrl}
    <a 
      href={prevSourcefileUrl}
      class="button"
      data-sveltekit-reload
      title="Previous file: '{navigation.prev_filename || 'Unknown'}'"
    >
      <CaretLeft size={16} weight="bold" />
    </a>
  {/if}
  
  <a 
    href={sourcedirUrl}
    class="button"
    data-sveltekit-reload
    title="Up to directory: '{navigation.sourcedir_path || sourcedir_slug}'"
  >
    <ArrowUp size={16} weight="bold" />
  </a>
  
  {#if navigation.is_last}
    <span class="button disabled" title="Next file">
      <CaretRight size={16} weight="bold" />
    </span>
  {:else if nextSourcefileUrl}
    <a 
      href={nextSourcefileUrl}
      class="button"
      data-sveltekit-reload
      title="Next file: '{navigation.next_filename || 'Unknown'}'"
    >
      <CaretRight size={16} weight="bold" />
    </a>
  {/if}

  {#if navigation.is_last}
    <span class="button disabled" title="Last file">
      <CaretDoubleRight size={16} weight="bold" />
    </span>
  {:else if lastSourcefileUrl}
    <a 
      href={lastSourcefileUrl}
      class="button"
      data-sveltekit-reload
      title="Last file: '{navigation.last_filename || 'Unknown'}'"
    >
      <CaretDoubleRight size={16} weight="bold" />
    </a>
  {/if}
  
  <span class="file-position">({navigation.current_position}/{navigation.total_files})</span>
</div>

<style>
  .navigation-buttons {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .button {
    background-color: var(--hz-color-primary-green);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    white-space: nowrap;
  }
  
  .button.disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .file-position {
    margin-left: 0.5rem;
    white-space: nowrap;
  }
  
  /* Responsive styling for different screen sizes */
  @media (max-width: 768px) {
    .navigation-buttons {
      flex-wrap: wrap;
      justify-content: center;
    }
  }
</style>