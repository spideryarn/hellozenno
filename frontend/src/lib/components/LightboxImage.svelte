<script lang="ts">
  /**
   * A custom lightbox component that displays images in a fullscreen modal.
   * The lightbox can be dismissed by clicking outside or pressing ESC.
   */
  
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  
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
  export let loading: 'lazy' | 'eager' = 'lazy';
  // Optional image styles
  export let imageStyle: string = '';
  
  let isOpen = false;
  let modalElement: HTMLDivElement;
  
  // Create inline style string for the thumbnail
  let inlineStyles = '';
  if (width) inlineStyles += `width: ${width};`;
  if (height) inlineStyles += `height: ${height};`;
  if (imageStyle) inlineStyles += imageStyle;

  function openLightbox(event: Event) {
    // Don't interfere with link behavior
    if (href) return;
    
    // Prevent event bubbling to avoid immediate click-outside detection
    event.stopPropagation();
    
    isOpen = true;
    
    // Prevent scrolling when lightbox is open
    if (browser) {
      document.body.style.overflow = 'hidden';
      
      // Use setTimeout to ensure the modal is fully rendered before focusing
      setTimeout(() => {
        if (modalElement) {
          modalElement.focus();
        }
      }, 10);
    }
  }

  function closeLightbox() {
    isOpen = false;
    // Restore scrolling
    if (browser) {
      document.body.style.overflow = '';
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    // Only process Escape key when lightbox is open
    if (isOpen && event.key === 'Escape') {
      event.preventDefault();
      closeLightbox();
    }
  }

  // Prevent multiple clicks from triggering rapid open/close cycles
  let isHandlingClick = false;

  function handleOutsideClick(event: MouseEvent) {
    if (isOpen && modalElement && event.target === modalElement && !isHandlingClick) {
      isHandlingClick = true;
      closeLightbox();
      // Reset after a short delay to prevent multiple events
      setTimeout(() => {
        isHandlingClick = false;
      }, 100);
    }
  }

  onMount(() => {
    // No need to add keydown listener manually since we use <svelte:window>
  });

  onDestroy(() => {
    // Ensure we restore scrolling if component is destroyed while open
    if (browser && isOpen) {
      document.body.style.overflow = '';
    }
  });

  /**
   * Portal action — moves the node to document.body so it is not affected by
   * ancestor transforms (e.g., hover effects) that create new containing blocks
   * for position: fixed elements.
   */
  function portal(node: HTMLElement) {
    if (!browser) return {};
    document.body.appendChild(node);
    return {
      destroy() {
        node.remove();
      }
    };
  }
</script>

{#if href}
  <!-- If href is provided, make the image a regular link -->
  <a {href} class="lightbox-wrapper {className}">
    <img {src} {alt} loading={loading} style={inlineStyles} class="img-fluid">
  </a>
{:else}
  <!-- Otherwise, make it a lightbox -->
  <div 
    class="lightbox-wrapper {className}" 
    on:click={openLightbox} 
    on:keydown={(e) => e.key === 'Enter' && openLightbox(e)} 
    role="button" 
    tabindex="0"
    aria-haspopup="dialog"
  >
    <img {src} {alt} loading={loading} style={inlineStyles} class="img-fluid">
  </div>
{/if}

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div
    use:portal
    class="lightbox-modal"
    bind:this={modalElement}
    on:click={handleOutsideClick}
    on:keydown={handleKeydown}
    role="dialog"
    tabindex="-1"
    aria-modal="true"
    aria-label={alt}
  >
    <div class="lightbox-content">
      <button 
        class="close-button" 
        on:click={closeLightbox} 
        aria-label="Close lightbox"
        autofocus
      >
        ×
      </button>
      <img src={src} alt={alt} class="lightbox-image">
    </div>
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
    /* Subtle primary-green outline to indicate clickability (without overriding existing shadows) */
    outline: 2px solid var(--hz-color-primary-green);
    outline-offset: 2px;
  }
  
  /* Ensure images have proper border radius consistent with your site */
  .lightbox-wrapper img {
    border-radius: 0.375rem;
  }

  /* Modal overlay */
  .lightbox-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    backdrop-filter: blur(2px);
    animation: fade-in 0.2s ease;
    will-change: opacity;
    outline: none;
  }
  
  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .lightbox-content {
    position: relative;
    max-width: 90vw;
    max-height: 90vh;
    animation: scale-in 0.3s ease;
    will-change: transform;
  }
  
  @keyframes scale-in {
    from { transform: scale(0.9); }
    to { transform: scale(1); }
  }

  .lightbox-image {
    max-width: 100%;
    max-height: 90vh;
    object-fit: contain;
    display: block;
    border-radius: 4px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    pointer-events: none; /* Prevent flickering from image events */
  }

  .close-button {
    position: absolute;
    top: -40px;
    right: -40px;
    width: 40px;
    height: 40px;
    background: rgba(0, 0, 0, 0.5);
    border: none;
    border-radius: 50%;
    color: white;
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .close-button:hover {
    background-color: rgba(0, 0, 0, 0.8);
  }

  @media (max-width: 768px) {
    .close-button {
      top: -30px;
      right: -10px;
    }
  }
</style>