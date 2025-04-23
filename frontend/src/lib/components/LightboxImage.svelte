<script lang="ts">
  /**
   * A wrapper component for svelte-lightbox library that provides a consistent 
   * interface for displaying images in a lightbox throughout the app.
   * 
   * This component automatically handles showing a thumbnail that opens a fullscreen 
   * lightbox when clicked. The lightbox can be dismissed by clicking outside, 
   * using the close button, or pressing ESC.
   */
  
  import { Lightbox } from 'svelte-lightbox';
  
  // Props for the component
  // Image source URL (required)
  export let src: string;
  // Alt text for accessibility (required)
  export let alt: string;
  // Optional CSS class for the thumbnail container
  export let className: string = '';
  // Optional href for the image to link somewhere (if provided, disables lightbox)
  export let href: string | null = null;
  // Optional image width
  export let width: string | null = null;
  // Optional image height
  export let height: string | null = null;
  // Optional loading attribute (lazy, eager, auto)
  export let loading: 'lazy' | 'eager' | 'auto' = 'lazy';
  // Optional image styles
  export let imageStyle: string = '';
  
  // Create inline style string
  let inlineStyles = '';
  if (width) inlineStyles += `width: ${width};`;
  if (height) inlineStyles += `height: ${height};`;
  if (imageStyle) inlineStyles += imageStyle;
</script>

{#if href}
  <!-- If href is provided, make the image a regular link -->
  <a {href} class="lightbox-wrapper {className}">
    <img {src} {alt} loading={loading} style={inlineStyles} class="img-fluid">
  </a>
{:else}
  <!-- Otherwise, wrap it in the lightbox component -->
  <div class="lightbox-wrapper {className}">
    <Lightbox>
      <img {src} {alt} loading={loading} style={inlineStyles} class="img-fluid">
    </Lightbox>
  </div>
{/if}

<style>
  /* Styling for the wrapper */
  .lightbox-wrapper {
    display: inline-block;
    cursor: pointer;
    transition: transform 0.2s ease;
  }
  
  .lightbox-wrapper:hover {
    transform: scale(1.02);
  }
  
  /* Ensure images have proper border radius consistent with your site */
  .lightbox-wrapper :global(img) {
    border-radius: 0.375rem;
  }
</style>