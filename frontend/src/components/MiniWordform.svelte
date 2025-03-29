<!--
  MiniWordform.svelte - A compact word display component
  
  Used for displaying words in lists and references throughout the application.
  When used in lists, wrap in a container with:
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  
  Props:
    wordform: string - The word to display
    translation: string | null - Optional translation
    href: string - Link target for the word
    notes: string | null - Optional contextual notes (displayed inline in parentheses)
-->

<!-- Declare types for Tippy -->
<script lang="ts" context="module">
  declare global {
    interface Window {
      tippy: any; // We could make this more specific if needed
    }
    interface Element {
      _tippy?: any;
    }
  }
</script>

<!-- Define the props -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { RouteName, resolveRoute } from '../../../static/js/generated/routes';

  export let wordform: string;
  export let translation: string | null = null;
  export let href: string;
  export let notes: string | null = null;

  let wordformLink: HTMLElement;

  onMount(() => {
    console.log('MiniWordform component mounted!', { wordform, href });
    
    // Check if Tippy.js is loaded
    if (!window.tippy) {
      console.error("Tippy.js is not loaded! This will cause errors.");
      return;
    }
    
    // Extract language code from href (handles both /el/... and /lang/el/... formats)
    const pathParts = href.split('/');
    const langCode = pathParts[1] === 'lang' ? pathParts[2] : pathParts[1];
    console.log('Extracted language code:', langCode);

    // Initialize Tippy for this wordform
    window.tippy(wordformLink, {
      content: 'Loading...',
      allowHTML: true,
      theme: 'light',
      placement: 'bottom',
      touch: true,
      touchHold: true,
      interactive: true,
      appendTo: document.body,
      maxWidth: 300,
      delay: [200, 0],
      onShow(instance: any) {
        // Hide all other tooltips when showing a new one
        document.querySelectorAll('[data-tippy-root]').forEach(tooltip => {
          const tippyInstance = tooltip._tippy;
          if (tippyInstance && tippyInstance !== instance) {
            tippyInstance.hide();
          }
        });

        console.log(`Fetching preview for word: "${wordform}" in language: ${langCode}`);

        // Fetch preview data from API using URL registry
        const previewUrl = resolveRoute(RouteName.WORDFORM_API_WORD_PREVIEW_API, {
          target_language_code: langCode,
          word: wordform
        });
        
        fetch(previewUrl)
          .then(r => {
            if (!r.ok) {
              throw new Error(`API request failed: ${r.status}`);
            }
            return r.json();
          })
          .then(data => {
            console.log(`Preview data for "${wordform}":`, data);
            instance.setContent(`
              <div class="p-2">
                <h4 class="mb-2">${data.lemma}</h4>
                ${data.translation ? `<p class="mb-1 text-muted">Translation: ${data.translation}</p>` : ''}
                ${data.etymology ? `<p class="mb-0 text-muted">Etymology: ${data.etymology}</p>` : ''}
              </div>
            `);
          })
          .catch(error => {
            console.error(`Error fetching preview for "${wordform}":`, error);
            instance.setContent('<div class="p-2">Error loading preview</div>');
          });
      }
    });
  });
</script>

<!-- Component template -->
<div class="mini-wordform card mb-2">
  <a {href} class="wordform-link p-2" bind:this={wordformLink}>
    <div class="wordform-content">
      <span class="wordform fw-medium">{wordform}</span>
      {#if translation}
        <span class="translation text-muted ms-1">- {translation}</span>
      {/if}
      {#if notes}
        <span class="notes text-muted fst-italic ms-1">({notes})</span>
      {/if}
    </div>
  </a>
</div>

<!-- Component styles -->
<style>
  .mini-wordform {
    display: inline-block;
    margin-right: 1rem;
    transition: transform 0.2s ease;
    border-color: var(--color-border);
    background-color: var(--color-surface);
  }

  .mini-wordform:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .wordform-link {
    text-decoration: none;
    color: inherit;
    display: block;
  }

  .wordform {
    color: var(--color-primary);
  }

  .translation {
    font-size: 0.875rem;
  }

  .notes {
    font-size: 0.875rem;
  }
</style> 