<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import KeyReturn from 'phosphor-svelte/lib/KeyReturn';
  import XCircle from 'phosphor-svelte/lib/XCircle';
  import { getPageUrl } from '$lib/navigation';
import { getApiUrl, apiFetch } from '$lib/api';
  import { page } from '$app/stores'; // Import page store for current URL
  import Alert from '$lib/components/Alert.svelte'; // Import Alert
  import { RouteName } from '$lib/generated/routes';
  
  export let data;
  
  // Define login URL with redirect back to current page
  $: loginUrl = `/auth?next=${encodeURIComponent($page.url.pathname + $page.url.search)}`;
  
  let currentStage = 1; // 1: Audio only, 2: Show sentence, 3: Show translation
  let isIgnoring = false; // Track if we're currently ignoring a lemma
  let ignoreError = ''; // Store any error messages during ignore operation
  let ignoreSuccess = ''; // Store success message after ignoring
  
  function nextStage() {
    if (currentStage < 3) {
      currentStage += 1;
    }
  }
  
  function playAudio() {
    const audioElement = document.getElementById('audio-player') as HTMLAudioElement;
    if (audioElement) {
      // Only restart if audio is not currently playing
      if (audioElement.paused || audioElement.ended) {
        audioElement.currentTime = 0; // Restart from beginning
        audioElement.play().catch(err => {
          console.error('Failed to play audio:', err);
        });
      }
    }
  }

  function prevStage() {
    if (currentStage > 1) {
      currentStage -= 1;
    }
    playAudio();
  }
  
  function nextSentence() {
    // Get parameters for the URL
    const params = new URLSearchParams(window.location.search);
    const baseUrl = `/language/${data.metadata.target_language_code}/flashcards/random`;
    
    if (params.toString()) {
      window.location.href = `${baseUrl}?${params.toString()}`;
    } else {
      window.location.href = baseUrl;
    }
  }
  
  // Function to ignore a lemma
  async function ignoreLemma(lemma: string) {
    try {
      // Reset status messages
      ignoreError = '';
      ignoreSuccess = '';
      isIgnoring = true;
      
      // Get the supabase client from parent layout data
      const supabaseClient = $page.data.supabase;
      
      try {
        // Use apiFetch to handle auth properly per the AUTH.md pattern
        const result = await apiFetch({
          supabaseClient,
          routeName: RouteName.LEMMA_API_IGNORE_LEMMA_API,
          params: {
            target_language_code: data.metadata.target_language_code,
            lemma: lemma
          },
          options: {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          }
        });
        
        // Success! Show message briefly and then load next sentence
        ignoreSuccess = result.message || `☑️ Ignored "${lemma}" successfully`;
        
        // After a short delay, load a new flashcard
        setTimeout(() => {
          nextSentence();
        }, 500);
      } catch (error: any) {
        // Handle 401 unauthorized error
        if (error.status === 401) {
          ignoreError = 'Please login to ignore words';
          setTimeout(() => {
            window.location.href = loginUrl;
          }, 1500);
          return;
        }
        throw error;
      }
    } catch (error) {
      console.error('Error ignoring lemma:', error);
      ignoreError = error instanceof Error ? error.message : 'Failed to ignore lemma';
    } finally {
      isIgnoring = false;
    }
  }
  
  // Handle keyboard shortcuts
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'ArrowRight') {
      nextStage();
    } else if (event.key === 'ArrowLeft') {
      if (currentStage === 1) {
        playAudio();
      } else {
        prevStage(); // This already plays audio via the prevStage function
      }
    } else if (event.key === 'Enter') {
      nextSentence();
    }
  }
  
  onMount(() => {
    // Autoplay audio on load ONLY if login is not required
    if (!data.audio_requires_login) {
      const audioElement = document.getElementById('audio-player') as HTMLAudioElement;
      if (audioElement) {
        audioElement.play().catch(err => {
          console.error('Failed to autoplay audio:', err);
        });
      }
    }
    
    // Add keyboard event listener
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  });
</script>

<svelte:head>
  <title>Flashcard | {data.metadata.language_name}</title>
</svelte:head>

<div class="container my-4">
  <div class="row justify-content-center">
    <div class="col-12 col-lg-10">
      <Card>
        <div class="text-center mb-4">
          <h2>{data.metadata.language_name} Flashcard</h2>
          
          {#if data.sourcefile}
            <p class="text-muted">
              From sourcefile: <a href={getPageUrl('sourcefile', {
                target_language_code: data.metadata.target_language_code,
                sourcedir_slug: data.sourcefile.sourcedir_slug,
                sourcefile_slug: data.sourcefile.slug
              })}>{data.sourcefile.name}</a>
            </p>
          {:else if data.sourcedir}
            <p class="text-muted">
              From sourcedir: <a href={getPageUrl('sourcedir', {
                target_language_code: data.metadata.target_language_code,
                sourcedir_slug: data.sourcedir.slug
              })}>{data.sourcedir.name}</a>
            </p>
          {/if}
        </div>
        
        <div class="row align-items-center mb-4">
          <div class="col-12">
            <!-- Audio player (always visible, but may be disabled) -->
            {#if data.audio_requires_login}
              <Alert type="info" className="mb-3">
                Audio generation requires login.
                <a href={loginUrl} class="btn btn-sm btn-primary ms-2">Login</a>
              </Alert>
              <!-- Render a disabled-looking player without controls -->
              <audio id="audio-player" src={data.audio_url} class="w-100 mb-3" style="opacity: 0.5; pointer-events: none;"></audio>
            {:else}
              <audio id="audio-player" src={data.audio_url} controls class="w-100 mb-3"></audio>
            {/if}
            
            <!-- Sentence (visible in stage 2+) -->
            {#if currentStage >= 2}
              <!-- Replaced alert with a styled div -->
              <div class="flashcard-content-box border rounded p-4 mb-3 bg-body-tertiary">
                <h3 class="text-center font-weight-bold fs-2 mb-0">{data.text}</h3>
              </div>
            {/if}
            
            <!-- Translation (visible in stage 3) -->
            {#if currentStage >= 3}
              <!-- Replaced alert with a styled div -->
              <div class="flashcard-content-box border rounded p-3 mb-3 bg-body-tertiary">
                <p class="text-center mb-0 fs-4">{data.translation}</p>
                <div class="text-center mt-3">
                  <a href={`/language/${data.metadata.target_language_code}/sentence/${data.slug}`} class="btn btn-sm btn-outline-secondary">
                    View full sentence page
                  </a>
                  
                  <!-- Status messages for ignoring lemmas -->
                  {#if ignoreError}
                    <div class="alert alert-danger mt-3">{ignoreError}</div>
                  {/if}
                  
                  {#if ignoreSuccess}
                    <div class="alert alert-success mt-3">{ignoreSuccess}</div>
                  {/if}
                  
                  <!-- Show lemma words with ignore buttons (Revised Style) -->
                  {#if data.lemma_words && data.lemma_words.length > 0}
                    <div class="mt-4 pt-3 border-top">
                      <p class="mb-2 text-muted small">Words in this sentence:</p>
                      <div class="d-flex flex-wrap justify-content-center align-items-center gap-3">
                        {#each data.lemma_words as lemma, i}
                          <div class="d-inline-flex align-items-center">
                            <span class="fs-6 me-1">{lemma}</span>
                            <button
                              class="btn btn-link p-0 border-0 text-secondary lh-1 ignore-btn"
                              title={`Ignore "${lemma}" in future flashcards`}
                              on:click={() => ignoreLemma(lemma)}
                              disabled={isIgnoring}
                            >
                              {#if isIgnoring}
                                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                              {:else}
                                <XCircle size={16} weight="regular" />
                              {/if}
                            </button>
                          </div>
                          <!-- Optional: Add separator if needed, e.g., if not wrapping well -->
                          <!-- {#if i < data.lemma_words.length - 1}
                            <span class="text-muted mx-1">•</span>
                          {/if} -->
                        {/each}
                      </div>
                    </div>
                  {/if}
                </div>
              </div>
            {/if}
          </div>
        </div>
        
        <div class="row g-3 mt-3">
          <!-- Navigation buttons -->
          <div class="col-4">
            <button 
              class="btn btn-secondary w-100 py-3" 
              on:click={currentStage === 1 ? playAudio : prevStage}
              disabled={data.audio_requires_login}>
              {currentStage === 1 ? 'Play audio (←)' : currentStage === 2 ? 'Play audio (←)' : 'Show sentence (←)'}
            </button>
          </div>
          
          <div class="col-4">
            <button 
              class="btn btn-primary w-100 py-3" 
              on:click={nextSentence}>
              New sentence <KeyReturn size={18} weight="bold" class="ms-1" />
            </button>
          </div>
          
          <div class="col-4">
            <button 
              class="btn btn-secondary w-100 py-3" 
              on:click={nextStage}
              disabled={currentStage === 3}>
              {currentStage === 1 ? 'Show sentence (→)' : currentStage === 2 ? 'Show translation (→)' : 'Next step (→)'}
            </button>
          </div>
        </div>
        
        <div class="text-center mt-4">
          <p class="text-muted small">
            Press ← → arrow keys to navigate, ENTER for next sentence
          </p>
        </div>
      </Card>
    </div>
  </div>
</div>

<style>
  .ignore-btn {
    opacity: 0.6;
    transition: opacity 0.2s ease-in-out;
  }
  .ignore-btn:hover,
  .ignore-btn:focus {
    opacity: 1;
    color: var(--bs-danger) !important; /* Use theme danger color on hover */
  }
  /* Optional: Style for the content boxes if needed beyond Bootstrap */
  .flashcard-content-box {
    /* Add custom styles if bg-body-tertiary and border aren't enough */
  }
</style> 