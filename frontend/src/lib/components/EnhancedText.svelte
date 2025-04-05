<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import tippy, { type Instance, hideAll } from 'tippy.js';
  import 'tippy.js/dist/tippy.css';
  import 'tippy.js/themes/light.css';
  import { getApiUrl } from '../api';
  import { RouteName } from '../generated/routes';

  export let html: string | null = null;
  export let language_code: string;

  let tippyInstances: Instance[] = [];
  let container: HTMLElement;
  
  // Function to detect mobile/touch devices
  function isTouchDevice(): boolean {
    return (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0
    );
  }

  // Initialize tooltips after the component mounts
  onMount(() => {
    if (!container) return;
    
    // Find all word links in the enhanced text
    const wordLinks = container.querySelectorAll('.word-link');
    
    // Create Tippy instances for each word link
    wordLinks.forEach((link) => {
      const wordElem = link as HTMLElement;
      const word = wordElem.textContent?.trim() || '';
      
      // For touch devices, prevent the default click behavior to allow tooltip to show
      if (isTouchDevice()) {
        wordElem.addEventListener('click', (e) => {
          // Only prevent default if modifier keys aren't pressed
          // This allows opening in new tab with Ctrl/Cmd+click
          if (!e.ctrlKey && !e.metaKey) {
            e.preventDefault();
          }
        });
      }
      
      const instance = tippy(wordElem, {
        content: 'Loading...',
        allowHTML: true,
        theme: 'light',
        placement: 'bottom',
        delay: [200, 0], // Delay before showing tooltip
        maxWidth: 300,
        interactive: true,
        appendTo: document.body,
        touch: true,
        trigger: isTouchDevice() ? 'click' : 'mouseenter focus', // Use click on touch devices
        onShow(instance) {
          // Hide all other tooltips
          hideAll({ exclude: instance });
          
          console.log(`Fetching preview for word: "${word}" in language: ${language_code}`);
          
          // Use type-safe API URL generation
          const apiUrl = getApiUrl(RouteName.WORDFORM_API_WORD_PREVIEW_API, {
            target_language_code: language_code,
            word: word
          });
          
          // Fetch preview data from API
          fetch(apiUrl)
            .then(response => {
              if (!response.ok) {
                console.error(`API request failed: ${response.status}`);
                return Promise.reject(`API request failed: ${response.status}`);
              }
              return response.json();
            })
            .then(data => {
              console.log(`Preview data for "${word}":`, data);
              
              if (data && data.lemma) {
                let content = `
                  <div class="tippy-content">
                    <h4>${data.lemma || word}</h4>
                `;
                
                if (data.translations && data.translations.length > 0) {
                  content += `<p class="translation">${data.translations.join('; ')}</p>`;
                } else if (data.translation) {
                  content += `<p class="translation">${data.translation}</p>`;
                }
                
                if (data.etymology) {
                  content += `<p class="etymology">${data.etymology}</p>`;
                }
                
                content += '</div>';
                
                instance.setContent(content);
              } else {
                instance.setContent('No data available');
              }
            })
            .catch(error => {
              console.error(`Error fetching preview for "${word}":`, error);
              instance.setContent('Error loading preview');
            });
        }
      });
      
      tippyInstances.push(instance);
    });
  });
  
  // Clean up Tippy instances when the component is destroyed
  onDestroy(() => {
    tippyInstances.forEach((instance) => instance.destroy());
    tippyInstances = [];
  });
</script>

<div class="enhanced-text" bind:this={container}>
  {#if html}
    {@html html}
  {:else}
    <slot />
  {/if}
</div>

<style>
  .enhanced-text {
    line-height: 1.6;
    max-width: 65ch; /* Ensure maximum of ~65 characters per line for readability */
  }
  
  .enhanced-text :global(a.word-link) {
    color: #4CAD53;
    text-decoration: none;
    border-bottom: 1px dotted #4CAD53;
  }
  
  .enhanced-text :global(a.word-link:hover) {
    background-color: rgba(76, 173, 83, 0.1);
  }
  
  /* Tippy custom styles */
  :global(.tippy-content) {
    padding: 8px 12px;
  }
  
  :global(.tippy-content h4) {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
  }
  
  :global(.tippy-content p) {
    margin: 4px 0;
    font-size: 14px;
  }
  
  :global(.tippy-content .translation) {
    color: #333;
  }
  
  :global(.tippy-content .etymology) {
    color: #666;
    font-style: italic;
    font-size: 13px;
  }
  
  /* Responsive styling for different screen sizes */
  @media (max-width: 768px) {
    .enhanced-text {
      padding: 0 5px; /* Minimal padding on mobile */
    }
  }
</style> 