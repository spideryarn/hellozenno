<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import tippy, { type Instance, hideAll } from 'tippy.js';
  import 'tippy.js/dist/tippy.css';
  import 'tippy.js/themes/light.css';
  import { getApiUrl } from '../api';
  import { API_BASE_URL } from '../config';
  import { RouteName } from '../generated/routes';
  import type { WordPreview } from '../types';

  export let html: string | null = null;
  export let target_language_code: string;

  let tippyInstances: Instance[] = [];
  let container: HTMLElement;
  
  // Function to detect mobile/touch devices
  function isTouchDevice(): boolean {
    return (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0
    );
  }
  
  // API fetch function using type-safe URL generation and async/await
  async function fetchWordData(word: string, lang: string): Promise<WordPreview> {
    console.log(`EnhancedText Debug:`);
    console.log(`- API_BASE_URL: ${API_BASE_URL}`);
    console.log(`- Language Code: ${lang}`);
    console.log(`- Word to fetch: "${word}"`);
    
    // IMPORTANT: Check if we have a valid language code
    if (!lang) {
      console.error(`- ERROR: Missing language code. This is required for API calls.`);
      return {
        lemma: word,
        translation: "(translation not available - missing language code)",
        etymology: null,
        _debug: {
          error: "Missing language code"
        }
      } as WordPreview;
    }
    
    // Generate the type-safe URL using routes.ts machinery
    let url;
    try {
      url = getApiUrl(RouteName.WORDFORM_API_WORD_PREVIEW_API, { 
        target_language_code: lang, 
        word: word
      });
      console.log(`- Using type-safe URL: ${url}`);
    } catch (error) {
      console.error(`- Error generating type-safe URL:`, error);
      return {
        lemma: word,
        translation: "(translation not available - URL generation error)",
        etymology: null,
        _debug: {
          error: `URL generation error: ${error.message}`
        }
      } as WordPreview;
    }
    
    try {
      // Make the API request
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        mode: 'cors'
      });
      
      if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`- API request succeeded:`, data);
      
      // Add URL to the data for debugging
      data._debug = {
        url,
      };
      
      return data;
    } catch (error) {
      console.error(`- API request failed:`, error);
      
      // Return a fallback result
      return {
        lemma: word,
        translation: "(translation not available)",
        etymology: null,
        _debug: {
          url,
          error: error.message
        }
      } as WordPreview;
    }
  }

  // Initialize tooltips after the component mounts
  onMount(() => {
    console.log(`EnhancedText component mounted with target_language_code: ${target_language_code}`);
    
    if (!container) {
      console.error("Container element not found");
      return;
    }
    
    // Find all word links in the enhanced text
    const wordLinks = container.querySelectorAll('.word-link');
    console.log(`Found ${wordLinks.length} word links in enhanced text`);
    
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
      
      // URL is constructed in fetchWordData and in the debug sections
      // Preload the data before showing tooltip - much more reliable
      let preloadedData = null;
      let preloadError = null;
      
      // Start the data fetch immediately (not waiting for hover)
      fetchWordData(word, target_language_code)
        .then(data => {
          preloadedData = data;
          console.log(`Preloaded data for "${word}":`, data);
        })
        .catch(error => {
          preloadError = error;
          console.error(`Error preloading data for "${word}":`, error);
        });
      
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
          
          console.log(`Showing tooltip for word: "${word}" in language: ${target_language_code}`);
          
          // Set initial content
          instance.setContent('Loading...');
          
          // Use preloaded data if available, otherwise fetch
          if (preloadedData) {
            console.log(`Using preloaded data for "${word}"`);
            renderTooltipContent(preloadedData);
          } else if (preloadError) {
            console.log(`Using preloaded error for "${word}"`);
            renderErrorContent();
          } else {
            console.log(`Fetching data on-demand for "${word}"`);
            // No preloaded data yet, fetch it now
            fetchWordData(word, target_language_code)
              .then(data => renderTooltipContent(data))
              .catch(error => renderErrorContent(error));
          }
          
          // Helper function to render tooltip content
          function renderTooltipContent(data: WordPreview) {
            // Always create a tooltip, even if data is minimal or missing
            let content = `
              <div class="tippy-content">
                <h4>${data?.lemma || word}</h4>
            `;
            
            if (data?.translations && data.translations.length > 0) {
              content += `<p class="translation">${data.translations.join('; ')}</p>`;
            } else if (data?.translation) {
              content += `<p class="translation">${data.translation}</p>`;
            } else {
              // Show a default message if no translation available
              content += `<p class="translation"><em>(translation not available)</em></p>`;
            }
            
            if (data?.etymology) {
              content += `<p class="etymology">${data.etymology}</p>`;
            }
            
            // Only add debug info in non-production environments
            if (import.meta.env.DEV) {
              const debugInfo = `
                <div class="debug-info" style="font-size: 9px; color: #999; margin-top: 8px; border-top: 1px dotted #ddd; padding-top: 4px;">
                  <strong>URL:</strong><br>
                  <span style="font-weight: bold;">${data._debug?.url || 'N/A'}</span><br>
                  <strong>Details:</strong><br>
                  Language code: ${target_language_code}<br>
                  Word: ${word}
                </div>
              `;
              content += debugInfo;
            }
            
            content += '</div>';
            
            instance.setContent(content);
            
            // If we got a response but it's incomplete, log this
            if (data && (!data.lemma || !data.translation)) {
              console.log(`Incomplete word data for "${word}":`, data);
            }
          }
          
          // Helper function to render error content
          function renderErrorContent(error?: any) {
            console.error(`Error fetching preview for "${word}":`, error);
            
            // Show a more helpful error message with the word itself
            let errorContent = `
              <div class="tippy-content">
                <h4>${word}</h4>
                <p class="translation"><em>Error loading word information</em></p>
            `;
            
            // Only add debug info in non-production environments
            if (import.meta.env.DEV) {
              // Try to regenerate the URL for the debug info
              let urlForDebug = "";
              try {
                urlForDebug = getApiUrl(RouteName.WORDFORM_API_WORD_PREVIEW_API, { 
                  target_language_code: target_language_code, 
                  word: word 
                });
              } catch (urlError) {
                urlForDebug = `Error: ${urlError.message}`;
              }
              
              // No need for this anymore as we're using the url variable directly
              
              errorContent += `
                <div class="debug-info" style="font-size: 9px; color: #999; margin-top: 8px; border-top: 1px dotted #ddd; padding-top: 4px;">
                  <strong>URL:</strong><br>
                  <span style="font-weight: bold;">${urlForDebug || url}</span><br>
                  <strong>Details:</strong><br>
                  Language code: ${target_language_code}<br>
                  Word: ${word}
                  ${error ? `<br>Error: ${error.message}` : ''}
                </div>
              `;
            }
            
            errorContent += `</div>`;
            instance.setContent(errorContent);
          }
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