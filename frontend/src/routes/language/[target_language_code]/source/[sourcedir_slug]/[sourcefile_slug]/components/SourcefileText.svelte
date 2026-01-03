<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { Sourcefile, Navigation } from '$lib/types/sourcefile';
  import EnhancedText from '$lib/components/EnhancedText.svelte';
  import { getPageUrl } from '$lib/navigation';
  import SourcefileFooter from './SourcefileFooter.svelte';
  
  export const sourcefile: Sourcefile = undefined as unknown as Sourcefile;
  export let enhanced_text: string | null = null;
  export let text_target: string | null = null;
  export let recognized_words: Array<{
    word: string;
    start: number;
    end: number;
    lemma: string;
    translations: string[];
    part_of_speech?: string;
    inflection_type?: string;
  }> = [];
  export const text_english: string | null = null;
  // VERY IMPORTANT: target_language_code is required by EnhancedText for generating API URLs
  // Previously named target_language_code, renamed for consistency with API
  export let target_language_code: string;
  // Add navigation props for bottom navigation
  export let navigation: Navigation = undefined as unknown as Navigation;
  export let sourcedir_slug: string = '';
  export let sourcefile_slug: string = '';

  // Debug flag - set to true to see what data is available
  const debug = import.meta.env.DEV && false;
  
  // Reference to the EnhancedText component instance
  let enhancedTextComponent: EnhancedText;
  // Show bottom navigation only when text is long enough
  let showBottomNav = false;
  let textContentElement: HTMLElement;
  
  // Function to handle the processing complete event
  function handleProcessingComplete(event: CustomEvent) {
    if (import.meta.env.DEV) console.log('Received processingComplete event in SourcefileText', event);
    const newData = event.detail;
    
    if (newData) {
      let dataUpdated = false;
      
      // Update the recognized words and text data (allow empty array to reset state)
      if (newData.recognized_words) {
        recognized_words = newData.recognized_words;
        if (import.meta.env.DEV) console.log(`Updated recognized_words with ${recognized_words.length} items`);
        dataUpdated = true;
      }
      
      // Update the text content if needed (check nested path first, then fallback)
      if (newData.sourcefile?.text_target || newData.text_target) {
        text_target = newData.sourcefile?.text_target ?? newData.text_target;
        dataUpdated = true;
      }
      
      // Update enhanced_text for legacy mode if needed
      if (newData.enhanced_text) {
        enhanced_text = newData.enhanced_text;
        dataUpdated = true;
      }
      
      // Check if we need to show bottom navigation after content update
      // Note: Tooltip refresh is handled reactively by EnhancedText when recognizedWords changes
      if (dataUpdated) {
        setTimeout(() => {
          checkContentHeight();
        }, 200);
      }
    }
  }
  
  // Function to check if content is tall enough to warrant bottom navigation
  function checkContentHeight() {
    if (textContentElement) {
      // Show bottom nav if content height is greater than 800px (arbitrary threshold - adjust as needed)
      const threshold = 800;
      showBottomNav = textContentElement.offsetHeight > threshold;
    }
  }
  
  // Generate navigation URLs using getPageUrl
  $: sourcedirUrl = navigation && getPageUrl('sourcedir', {
    target_language_code,
    sourcedir_slug
  });

  // Prepare navigation URLs only if the corresponding slugs exist
  $: firstSourcefileUrl = navigation?.first_slug ? 
    getPageUrl('sourcefile_text', {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.first_slug
    }) : undefined;
    
  $: prevSourcefileUrl = navigation?.prev_slug ? 
    getPageUrl('sourcefile_text', {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.prev_slug
    }) : undefined;
    
  $: nextSourcefileUrl = navigation?.next_slug ? 
    getPageUrl('sourcefile_text', {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.next_slug
    }) : undefined;
    
  $: lastSourcefileUrl = navigation?.last_slug ? 
    getPageUrl('sourcefile_text', {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.last_slug
    }) : undefined;
  
  // Add and remove event listeners for the custom event
  onMount(() => {
    // Only run in browser environment, not during SSR
    if (typeof document !== 'undefined') {
      document.addEventListener('processingComplete', handleProcessingComplete as EventListener);
      
      // Check if we need to show bottom navigation based on content height
      setTimeout(checkContentHeight, 500);
      
      // Add resize listener to handle window size changes
      window.addEventListener('resize', checkContentHeight);
    }
  });
  
  onDestroy(() => {
    // Only run in browser environment, not during SSR
    if (typeof document !== 'undefined') {
      document.removeEventListener('processingComplete', handleProcessingComplete as EventListener);
      window.removeEventListener('resize', checkContentHeight);
    }
  });
</script>

<div class="text-content" bind:this={textContentElement}>
  <h2>Text</h2>
  
  {#if debug}
    <div class="debug-container">
      <h3>Debug: Available Data</h3>
      <div><strong>HTML Mode:</strong> {enhanced_text ? 'Yes' : 'No'}</div>
      <div><strong>Structured Mode:</strong> {recognized_words?.length ? 'Yes' : 'No'}</div>
      <div><strong>Language Code:</strong> {target_language_code}</div>
      <div><strong>Recognized Words:</strong> {recognized_words?.length || 0}</div>
      <pre>{JSON.stringify(recognized_words?.[0] || {}, null, 2)}</pre>
    </div>
  {/if}

  {#if recognized_words?.length && text_target}
    <!-- Preferred mode: Using the structured data approach for better separation of concerns -->
    <EnhancedText 
      bind:this={enhancedTextComponent}
      text={text_target} 
      recognizedWords={recognized_words} 
      target_language_code={target_language_code} 
    />
  {:else if enhanced_text}
    <!-- DEPRECATED: Legacy HTML-based approach. This mode uses pre-generated HTML from the backend,
         which mixes content with presentation. It should eventually be removed once all
         components are updated to use the structured data approach. -->
    <EnhancedText 
      bind:this={enhancedTextComponent}
      html={enhanced_text} 
      target_language_code={target_language_code} 
    />
  {:else if text_target}
    <!-- Fallback: Just show plain text -->
    <div class="plain-text">
      {#each text_target.split('\n\n') as paragraph}
        {#if paragraph}
          <p>{paragraph}</p>
        {/if}
      {/each}
    </div>
  {:else}
    <p class="no-content">No text available</p>
  {/if}
  
  <SourcefileFooter 
    {navigation}
    {target_language_code}
    {sourcedir_slug}
    {sourcefile_slug}
    view="text"
    contentRef={textContentElement}
  />
</div>

<style>
  .text-content {
    margin-bottom: 2rem;
    max-width: 100%;
    padding: 0;
  }
  
  .plain-text p {
    margin-bottom: 1rem;
    line-height: 1.6;
    max-width: 70ch;
    font-size: 1.2rem;
  }
  
  .no-content {
    color: #666;
    font-style: italic;
  }

  .debug-container {
    margin-bottom: 2rem;
    padding: 1rem;
    border: 1px solid #ddd;
    background-color: #f8f9fa;
    border-radius: 4px;
    font-family: monospace;
  }
  
  
  /* Responsive styling for different screen sizes */
  @media (max-width: 768px) {
    .text-content,
    .plain-text p {
      padding: 0; /* No extra padding on mobile - container handles margins */
    }
    
    .plain-text p {
      line-height: 1.8; /* Match EnhancedText for easier touch targets */
    }
  }
</style>