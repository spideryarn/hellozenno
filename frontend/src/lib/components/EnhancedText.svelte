<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import tippy, { type Instance, hideAll } from 'tippy.js';
  import 'tippy.js/dist/tippy.css';
  // No need to import light theme as we'll use custom styling
  import { getApiUrl } from '../api';
  import { API_BASE_URL } from '../config';
  import { RouteName } from '../generated/routes';
  import type { WordPreview } from '../types';

  // Support different input modes - either HTML string or structured data
  export let html: string | null = null;
  export let text: string | null = null;
  export let recognizedWords: Array<{
    word: string;
    start: number;
    end: number;
    lemma: string;
    translations: string[];
    part_of_speech?: string;
    inflection_type?: string;
  }> = [];
  export let target_language_code: string;

  let tippyInstances: Instance[] = [];
  let container: HTMLElement;
  
  // Function to detect mobile/touch devices
  function isTouchDevice(): boolean {
    // Check if we're in browser environment
    if (typeof window === 'undefined' || typeof navigator === 'undefined') {
      return false; // Default to false during SSR
    }
    
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
    } catch (error: unknown) {
      console.error(`- Error generating type-safe URL:`, error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        lemma: word,
        translation: "(translation not available - URL generation error)",
        etymology: null,
        _debug: {
          error: `URL generation error: ${errorMessage}`
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
      // Ensure errorMessage is derived safely from the unknown error type
      const errorMessage = (error instanceof Error) ? error.message : String(error);
      // Return a fallback result
      return {
        lemma: word,
        translation: "(translation not available)",
        etymology: null,
        _debug: {
          url,
          error: errorMessage // Use processed error message
        }
      } as WordPreview;
    }
  }

  // Helper to create tooltip content
  function createTooltipContent(data: WordPreview, word: string) {
    // Get the lemma from data or default to the word
    const lemma = data?.lemma || word;
    
    // Create link to the WORD page - ensure proper encoding for URLs
    const wordformLink = `/language/${target_language_code}/wordform/${encodeURIComponent(word)}`;
    
    // Always create a tooltip, even if data is minimal or missing
    let content = `
      <div class="tippy-content">
        <h4><a href="${wordformLink}" class="tooltip-lemma-link" target="_blank">${lemma}</a></h4>
    `;
    
    // Show the wordform translation instead of lemma translation
    if (data?.translations && data.translations.length > 0) {
      content += `<p class="translation">${data.translations.join('; ')}</p>`;
    } else if (data?.translation) {
      content += `<p class="translation">${data.translation}</p>`;
    } else {
      // Show a default message if no translation available
      content += `<p class="translation"><em>(translation not available)</em></p>`;
    }
    
    // Show the inflection type if available
    if (data?.inflection_type) {
      content += `<p class="inflection-type"><em>${data.inflection_type}</em></p>`;
    }
    
    if (data?.etymology) {
      content += `<p class="etymology">${data.etymology}</p>`;
    }
    
    // Add a view details link at the bottom
    content += `<p class="view-details"><a href="${wordformLink}" target="_blank">View details for '${word}' →</a></p>`;
    
    // Only add debug info in non-production environments
    if (import.meta.env.DEV) {
      const debugInfo = `
        <div class="debug-info" style="font-size: 9px; color: var(--hz-color-text-secondary); margin-top: 8px; border-top: 1px dotted var(--hz-color-border); padding-top: 4px;">
          <strong>URL:</strong><br>
          <span style="font-weight: bold;">${data._debug?.url || 'N/A'}</span><br>
          <strong>Details:</strong><br>
          Language code: ${target_language_code}<br>
          Word: ${word}
          ${data._debug?.error ? `<br>Error: ${data._debug.error}` : ''}
        </div>
      `;
      content += debugInfo;
    }
    
    content += '</div>';
    return content;
  }

  // Helper to create error tooltip content  
  function createErrorContent(word: string, error?: unknown) {
    // Create link to the WORD page - even for error cases, link to the word itself
    const wordformLink = `/language/${target_language_code}/wordform/${encodeURIComponent(word)}`;
    
    // Show a more helpful error message with the word itself
    let errorContent = `
      <div class="tippy-content">
        <h4><a href="${wordformLink}" class="tooltip-lemma-link" target="_blank">${word}</a></h4>
        <p class="translation error"><em>Error loading word information</em></p>
        <p class="view-details"><a href="${wordformLink}" target="_blank">Try view details for '${word}' →</a></p>
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
      } catch (urlError: unknown) {
        const urlErrorMessage = (urlError instanceof Error) ? urlError.message : String(urlError);
        urlForDebug = `Error: ${urlErrorMessage}`; // Use processed error message
      }
      
      errorContent += `
        <div class="debug-info" style="font-size: 9px; color: var(--hz-color-text-secondary); margin-top: 8px; border-top: 1px dotted var(--hz-color-border); padding-top: 4px;">
          <strong>URL:</strong><br>
          <span style="font-weight: bold;">${urlForDebug}</span><br>
          <strong>Details:</strong><br>
          Language code: ${target_language_code}<br>
          Word: ${word}
          ${error ? `<br>Error: ${(error instanceof Error) ? error.message : String(error)}` : ''}
        </div>
      `;
    }
    
    errorContent += `</div>`;
    return errorContent;
  }

  // Function to attach tippy to an element  
  function attachTippy(element: HTMLElement, word: string) {
    // For touch devices, prevent the default click behavior to allow tooltip to show
    if (isTouchDevice()) {
      element.addEventListener('click', (e) => {
        // Only prevent default if modifier keys aren't pressed
        // This allows opening in new tab with Ctrl/Cmd+click
        if (!e.ctrlKey && !e.metaKey) {
          e.preventDefault();
        }
      });
    }
    
    const instance = tippy(element, {
      content: '<div class="hz-tooltip-loading"><div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Loading...</div>',
      allowHTML: true,
      theme: 'hz-dark',
      placement: 'bottom',
      delay: [200, 0], // Delay before showing tooltip
      maxWidth: 300,
      interactive: true,
      appendTo: typeof document !== 'undefined' ? document.body : 'parent', // Use parent if document not available
      touch: true,
      trigger: isTouchDevice() ? 'click' : 'mouseenter', // Use click on touch, ONLY mouseenter on desktop
      onShow(instance) {
        // Hide all other tooltips
        hideAll({ exclude: instance });
        
        console.log(`Showing tooltip for word: "${word}" in language: ${target_language_code}`);
        
        // Set initial loading content with spinner
        instance.setContent('<div class="hz-tooltip-loading"><div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Loading...</div>');
        
        // Fetch data on-demand when the tooltip is shown
        console.log(`Fetching data on-demand for "${word}"`);
        fetchWordData(word, target_language_code)
          .then(data => instance.setContent(createTooltipContent(data, word)))
          .catch(error => instance.setContent(createErrorContent(word, error)));
      }
    });
    
    return instance;
  }

  // Initialize HTML-based tooltips (legacy mode)
  function initializeHTMLBasedTooltips() {
    if (!container) {
      console.error("Container element not found");
      return;
    }
    
    // Find all word links in the enhanced text
    const wordLinks = container.querySelectorAll('.word-link');
    console.log(`Found ${wordLinks.length} word links in enhanced text (HTML mode)`);
    
    // Create Tippy instances for each word link
    wordLinks.forEach((link) => {
      const wordElem = link as HTMLElement;
      const word = wordElem.textContent?.trim() || '';
      const instance = attachTippy(wordElem, word);
      tippyInstances.push(instance);
    });
  }

  // Initialize structured-data-based tooltips (new mode)
  function initializeStructuredDataTooltips() {
    if (!container || !text || recognizedWords.length === 0) {
      console.log("Skipping structured data tooltip initialization: missing data");
      return;
    }
    
    // Get the container's text nodes and create a map to track spans we've inserted
    const wordSpans = new Map<string, HTMLElement>();
    
    // Find all the word spans we created
    const spans = container.querySelectorAll('.word-link');
    spans.forEach(span => {
      const wordElem = span as HTMLElement;
      const word = wordElem.textContent?.trim() || '';
      wordSpans.set(word, wordElem);
    });
    
    console.log(`Found ${spans.length} interactive words in structured data mode`);
    
    // Create Tippy instances for each word span
    for (const [word, element] of wordSpans.entries()) {
      const instance = attachTippy(element, word);
      tippyInstances.push(instance);
    }
  }

  // Function to reinitialize tooltips
  export function refreshTooltips() {
    console.log('Refreshing tooltips in EnhancedText component');
    
    // First, clean up any existing tooltips
    tippyInstances.forEach((instance) => instance.destroy());
    tippyInstances = [];
    
    // Then reinitialize based on current content mode
    if (html) {
      initializeHTMLBasedTooltips();
    } else if (text && recognizedWords.length > 0) {
      initializeStructuredDataTooltips();
    }
  }
  
  // Watch for changes to recognized words and refresh tooltips when they change
  $: if (recognizedWords) {
    // Use setTimeout to ensure the DOM has been updated before refreshing tooltips
    if (typeof document !== 'undefined' && container) {
      setTimeout(() => refreshTooltips(), 0);
    }
  }
  
  // Initialize tooltips after the component mounts
  onMount(() => {
    console.log(`EnhancedText component mounted with target_language_code: ${target_language_code}`);
    
    if (html) {
      // Legacy HTML mode - the HTML already has links embedded
      initializeHTMLBasedTooltips();
    } else if (text && recognizedWords.length > 0) {
      // Structured data mode - we rendered spans in the template
      initializeStructuredDataTooltips();
    }
  });
  
  // Clean up Tippy instances when the component is destroyed
  onDestroy(() => {
    tippyInstances.forEach((instance) => instance.destroy());
    tippyInstances = [];
  });

  /**
   * Process the text with recognized words to segment it for rendering
   * This allows us to split the text into spans and plain text segments
   * Handles line breaks: single newlines become <br/>, double newlines become paragraph breaks
   */
  function processTextWithWords() {
    if (!text || !recognizedWords || recognizedWords.length === 0) {
      return [];
    }
    
    const segments = [];
    let lastPos = 0;
    
    // Sort recognized words by position
    const sortedWords = [...recognizedWords].sort((a, b) => a.start - b.start);
    
    // Process each word
    for (const word of sortedWords) {
      // Add text segment before this word, if any
      if (word.start > lastPos) {
        const beforeText = text.substring(lastPos, word.start);
        
        // Process line breaks in the text segment
        const processedText = processLineBreaks(beforeText);
        segments.push({
          type: 'text',
          text: processedText
        });
      }
      
      // Add the word segment
      segments.push({
        type: 'word',
        text: text.substring(word.start, word.end),
        word: word.word,
        lemma: word.lemma,
        translations: word.translations || [],
      });
      
      // Update lastPos
      lastPos = word.end;
    }
    
    // Add any remaining text after the last word
    if (lastPos < text.length) {
      const afterText = text.substring(lastPos);
      
      // Process line breaks in the remaining text
      const processedText = processLineBreaks(afterText);
      segments.push({
        type: 'text',
        text: processedText
      });
    }
    
    return segments;
  }
  
  /**
   * Process line breaks in text: 
   * - Convert double newlines to paragraph breaks (<p>)
   * - Convert single newlines to line breaks (<br>)
   */
  function processLineBreaks(text: string): string {
    // Simple conversion: keep all spaces, convert all newlines to <br>.
    // Double newlines naturally become <br><br>, avoiding paragraph wrappers
    // that could split around inline word links.
    return text.replace(/\n/g, '<br>');
  }
</script>

<div class="enhanced-text" bind:this={container}>
  {#if html}
    <!-- Legacy Mode: Using HTML with pre-generated links -->
    {@html html}
  {:else if text && recognizedWords?.length > 0}
    <!-- New Structured Mode: Using text and recognized words data -->
    {#each processTextWithWords() as segment}
      {#if segment.type === 'word'}
        <a
          href={`/language/${target_language_code}/wordform/${encodeURIComponent(segment.word ?? '')}`}
          class="word-link"
          data-word={segment.word}
          data-lemma={segment.lemma ?? ''}
          target="_blank"
        >
          {segment.text}
        </a>
      {:else}
        {@html segment.text}
      {/if}
    {/each}
  {:else}
    <!-- Fallback for no content -->
    <slot />
  {/if}
</div>

<style>
  .enhanced-text {
    line-height: 1.4; /* Reduced from 1.6 to tighten line spacing */
    max-width: 70ch; /* Ensure maximum of ~65 characters per line for readability */
    font-size: 1.2rem; /* Larger font size for better readability */
    white-space: normal; /* Don't preserve literal whitespace */
  }
  
  /* Ensure paragraphs have proper spacing */
  .enhanced-text :global(p) {
    margin-bottom: 1.3rem; /* Reduced from 1rem to tighten paragraph spacing */
  }
  
  /* Ensure <br> elements create appropriate line breaks */
  .enhanced-text :global(br) {
    display: block;
    content: "";
    margin-top: 0.3rem; /* Reduced from 0.5rem to tighten line break spacing */
  }
  
  .enhanced-text :global(a.word-link),
  .enhanced-text a.word-link {
    color: var(--hz-color-primary-green); /* Use theme primary color */
    text-decoration: none;
    border-bottom: 1px dotted var(--hz-color-primary-green); /* Use theme primary color */
    cursor: pointer;
    transition: background-color 0.15s ease-in-out;
  }
  
  .enhanced-text :global(a.word-link:hover),
  .enhanced-text a.word-link:hover {
    /* Use primary color with low opacity for subtle hover */
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.1); /* Updated variable */
  }
  
  /* Tippy custom styles - dark theme using theme variables */
  :global(.tippy-box[data-theme~='hz-dark']) {
    background-color: var(--hz-color-surface); /* Use theme surface color */
    border: 1px solid var(--hz-color-border); /* Use theme border color */
    color: var(--hz-color-text-main); /* Use theme main text color */
    box-shadow: var(--hz-shadow-primary-green); /* Use theme shadow */
  }
  
  :global(.tippy-box[data-theme~='hz-dark'] .tippy-arrow) {
    color: var(--hz-color-surface); /* Match background */
  }
  
  :global(.tippy-content) {
    padding: 10px 14px;
  }
  
  :global(.tippy-content h4) {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--hz-color-primary-green); /* Use theme primary color */
  }
  
  :global(.tippy-content p) {
    margin: 4px 0;
    font-size: 14px;
  }
  
  :global(.tippy-content .translation) {
    color: var(--hz-color-text-main); /* Use theme main text color */
  }
  
  :global(.tippy-content .inflection-type) {
    /* Consider using a different accent or secondary text */
    color: var(--hz-color-accent-lavender); /* Example: Lavender accent */
    font-style: italic;
    font-size: 13px;
    margin-top: 2px;
  }
  
  :global(.tippy-content .etymology) {
    color: var(--hz-color-text-secondary); /* Use theme secondary text color */
    font-style: italic;
    font-size: 13px;
  }
  
  :global(.hz-tooltip-loading) {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px;
    color: var(--hz-color-text-secondary); /* Use theme secondary text color */
  }
  
  :global(.tippy-content .translation.error) {
    color: var(--hz-color-accent-gold); /* Use gold accent for errors/warnings */
  }
  
  /* Tooltip link styles */
  :global(.tippy-content .tooltip-lemma-link) {
    color: var(--hz-color-primary-green); /* Use theme primary color */
    text-decoration: none;
    font-weight: 600;
  }
  
  :global(.tippy-content .tooltip-lemma-link:hover) {
    text-decoration: underline;
  }
  
  :global(.tippy-content .view-details) {
    margin-top: 8px;
    font-size: 13px;
    text-align: right;
  }
  
  :global(.tippy-content .view-details a) {
    color: var(--hz-color-primary-green); /* Use theme primary color */
    text-decoration: none;
  }
  
  :global(.tippy-content .view-details a:hover) {
    text-decoration: underline;
  }

  /* Debug info styling */
  :global(.tippy-content .debug-info) {
    font-size: 9px;
    color: var(--hz-color-text-secondary);
    margin-top: 8px;
    border-top: 1px dotted var(--hz-color-border); /* Use correct border variable */
    padding-top: 4px;
  }
  
  :global(.tippy-content .debug-info strong) {
     font-weight: bold;
     color: var(--hz-color-text-main); /* Make labels slightly more prominent */
  }
  
  :global(.tippy-content .debug-info span[style*="bold"]) {
      font-weight: bold;
      color: var(--hz-color-text-main);
  }
  
  /* Responsive styling for different screen sizes */
  @media (max-width: 768px) {
    .enhanced-text {
      padding: 0 5px; /* Minimal padding on mobile */
    }
  }
</style> 