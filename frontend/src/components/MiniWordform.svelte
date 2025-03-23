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

<!-- Define the props -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { RouteName, resolveRoute } from '../../../static/js/generated/routes';

  // Declare types for Tippy
  declare global {
    interface Window {
      tippy: any; // We could make this more specific if needed
    }
    interface Element {
      _tippy?: any;
    }
  }

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
              <h4>${data.lemma}</h4>
              ${data.translation ? `<p class="translation">Translation: ${data.translation}</p>` : ''}
              ${data.etymology ? `<p class="etymology">Etymology: ${data.etymology}</p>` : ''}
            `);
          })
          .catch(error => {
            console.error(`Error fetching preview for "${wordform}":`, error);
            instance.setContent('Error loading preview');
          });
      }
    });
  });
</script>

<!-- Component template -->
<div class="mini-wordform">
  <a {href} class="wordform-link" bind:this={wordformLink}>
    <div class="wordform-content">
      <span class="wordform">{wordform}</span>
      {#if translation}
        <span class="translation">- {translation}</span>
      {/if}
      {#if notes}
        <span class="notes">({notes})</span>
      {/if}
    </div>
  </a>
</div>

<!-- Component styles -->
<style>
  .mini-wordform {
    margin: 0.25rem 0;
    display: inline-block;
    margin-right: 1rem;
  }

  .wordform-link {
    text-decoration: none;
    color: inherit;
    display: block;
  }

  .wordform-content {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    transition: all 0.2s;
  }

  .wordform-content:hover {
    background-color: #f8fafc;
  }

  .wordform {
    font-size: 1rem;
    line-height: 1.4;
  }

  .translation {
    font-size: 0.875rem;
    color: #64748b;
    margin-left: 0.25rem;
  }

  .notes {
    font-size: 0.875rem;
    color: #64748b;
    font-style: italic;
    margin-left: 0.25rem;
  }
</style> 