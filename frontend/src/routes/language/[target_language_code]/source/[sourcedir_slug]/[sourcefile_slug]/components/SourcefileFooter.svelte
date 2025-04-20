<script lang="ts">
  import type { Navigation } from '$lib/types/sourcefile';
  import NavButtons from './NavButtons.svelte';
  import { onMount } from 'svelte';
  
  export let navigation: Navigation;
  export let target_language_code: string;
  export let sourcedir_slug: string;
  export let sourcefile_slug: string;
  export let view: string = 'text'; // The current view (text, words, phrases, etc.)
  export let contentRef: HTMLElement | null = null; // Reference to the content element
  
  // Default threshold for when to show the footer (in pixels)
  export let minContentHeight: number = 800;
  
  // State for whether to show the footer navigation
  let showFooterNav = false;
  
  // Check if content is tall enough to warrant footer navigation
  function checkContentHeight() {
    if (contentRef) {
      showFooterNav = contentRef.offsetHeight > minContentHeight;
    }
  }
  
  onMount(() => {
    // Add a slight delay to ensure content is fully rendered
    setTimeout(checkContentHeight, 200);
    
    // Add resize listener to handle window size changes
    window.addEventListener('resize', checkContentHeight);
    
    // Cleanup on destroy
    return () => {
      window.removeEventListener('resize', checkContentHeight);
    };
  });
</script>

{#if showFooterNav}
  <div class="sourcefile-footer">
    <NavButtons 
      {navigation}
      {target_language_code}
      {sourcedir_slug}
      {sourcefile_slug}
      {view}
    />
  </div>
{/if}

<style>
  .sourcefile-footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  @media (max-width: 768px) {
    .sourcefile-footer {
      margin-top: 1.5rem;
    }
  }
</style>