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

<div class="section py-5">
  <div class="container">
    <div class="card">
      <div class="card-content">
        <!-- Source filter info banner -->
        {#if sourcefile || sourcedir}
          <div class="notification is-info is-light mb-5">
            <button class="delete" on:click={() => window.location.href = resolveRoute(RouteName.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW, {
              target_language_code: targetLanguageCode
            })} aria-label="delete"></button>
            <div class="is-flex is-align-items-center">
              <span class="icon">
                <i class="ph-fill ph-filter"></i>
              </span>
              <span class="ml-2">
                Filtered by {sourcedir ? 'directory' : 'file'}: 
                <strong>{sourcedir || sourcefile}</strong>
                {#if lemmaCount !== null}
                  <span class="has-text-grey ml-2">({lemmaCount} words)</span>
                {/if}
              </span>
            </div>
          </div>
        {/if}

        <div class="content mb-6">
          <h1 class="title is-4 has-text-centered mb-5">{targetLanguageName} Flashcards</h1>
          
          <div class="columns">
            <div class="column is-8 is-offset-2">
              <p class="has-text-centered mb-4">
                Practice your {targetLanguageName} vocabulary with interactive flashcards.
                Each flashcard has three stages:
              </p>
              
              <div class="box has-background-white-ter">
                <ol class="ml-5">
                  <li class="mb-2">Listen to the audio</li>
                  <li class="mb-2">View the {targetLanguageName} sentence</li>
                  <li>See the translation</li>
                </ol>
              </div>
              
              <div class="has-text-centered mt-5">
                <p class="has-text-grey is-size-7 mb-3">
                  <strong>Keyboard shortcuts:</strong>
                </p>
                <div class="tags is-centered are-small mb-2">
                  <span class="tag is-light has-family-monospace">←</span> Previous stage
                  <span class="tag is-light has-family-monospace">→</span> Next stage
                  <span class="tag is-light has-family-monospace">Enter</span> New sentence
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="has-text-centered mt-6 pt-4">
          <a href={startUrl} class="button is-primary is-large" on:keydown={handleKeydown}>
            <span class="icon">
              <i class="fas fa-play"></i>
            </span>
            <span>Start Flashcards</span>
            <span class="tag is-primary is-light ml-2 has-family-monospace">Enter</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  /* Some minor custom styles to enhance Bulma */
  :global(.notification .delete) {
    top: 0.85rem;
  }
  
  :global(.card) {
    box-shadow: 0 0.5em 1em -0.125em rgba(10, 10, 10, 0.1), 0 0 0 1px rgba(10, 10, 10, 0.05);
    border-radius: 8px;
  }
</style>