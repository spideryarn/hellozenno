<script lang="ts">
  import { RouteName, resolveRoute } from '../../../static/js/generated/routes';
  import '../styles/bulma-imports.css'; // Import Bulma CSS
  
  export let targetLanguageCode: string;
  export let targetLanguageName: string;
  export let sourcefile: string | null = null;
  export let sourcedir: string | null = null;
  export let lemmaCount: number | null = null;

  // Build the URL for starting the flashcards using route registry
  const baseUrl = resolveRoute(RouteName.FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW, {
    target_language_code: targetLanguageCode
  });
  
  // Add query parameters if we have source filtering
  let startUrl = baseUrl;
  if (sourcefile) {
    startUrl += `?sourcefile=${sourcefile}`;
  } else if (sourcedir) {
    startUrl += `?sourcedir=${sourcedir}`;
  }

  // Handle keyboard shortcut (Enter to start)
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      window.location.href = startUrl;
    }
  }
</script>

<div class="section">
  <div class="container">
    <!-- Source filter info banner -->
    {#if sourcefile || sourcedir}
      <div class="notification is-primary is-light">
        <div class="level">
          <div class="level-left">
            <div class="level-item">
              <span class="icon">
                <i class="ph-fill ph-filter"></i>
              </span>
              Filtered by {sourcedir ? 'directory' : 'file'}: 
              <strong class="ml-1">{sourcedir || sourcefile}</strong>
              {#if lemmaCount !== null}
                <span class="has-text-grey ml-2">({lemmaCount} words)</span>
              {/if}
            </div>
          </div>
          <div class="level-right">
            <div class="level-item">
              <a href={resolveRoute(RouteName.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW, {
                target_language_code: targetLanguageCode
              })} class="delete">
              </a>
            </div>
          </div>
        </div>
      </div>
    {/if}

    <div class="content mb-5">
      <p>
        Practice your {targetLanguageName} vocabulary with interactive flashcards.
        Each flashcard has three stages:
      </p>
      <ol>
        <li>Listen to the audio</li>
        <li>View the {targetLanguageName} sentence</li>
        <li>See the translation</li>
      </ol>
      
      <p class="has-text-grey is-size-7 mt-4">
        <strong>Keyboard shortcuts:</strong>
        <span class="tag is-light has-family-monospace">←</span> Previous stage
        <span class="tag is-light has-family-monospace ml-1">→</span> Next stage
        <span class="tag is-light has-family-monospace ml-1">Enter</span> New sentence
      </p>
    </div>
    
    <div class="has-text-centered">
      <a href={startUrl} class="button is-primary is-large" on:keydown={handleKeydown}>
        Start Flashcards <span class="is-size-7 ml-2">(Enter)</span>
      </a>
    </div>
  </div>
</div>

<style>
  /* Remove custom styles that are replaced by Bulma classes */
</style>