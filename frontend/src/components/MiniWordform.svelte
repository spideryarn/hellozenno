<!-- Define the props -->
<script lang="ts">
  import { onMount } from 'svelte';

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

  let wordformLink: HTMLElement;

  onMount(() => {
    // Extract language code from href (assumes URL format like /el/wordform/...)
    const langCode = href.split('/')[1];

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

        // Fetch preview data from API
        fetch(`/api/word-preview/${langCode}/${encodeURIComponent(wordform)}`)
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
</style> 