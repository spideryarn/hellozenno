<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import KeyReturn from 'phosphor-svelte/lib/KeyReturn';
  import Prohibit from 'phosphor-svelte/lib/Prohibit';
  import X from 'phosphor-svelte/lib/X';
  import FunnelSimple from 'phosphor-svelte/lib/FunnelSimple';
  import ArrowLeft from 'phosphor-svelte/lib/ArrowLeft';
  import { getPageUrl } from '$lib/navigation';
  import { getApiUrl, apiFetch } from '$lib/api';
  import { page } from '$app/stores'; // Import page store for current URL
  import Alert from '$lib/components/Alert.svelte'; // Import Alert
  import { AudioPlayer } from '$lib';
  import { RouteName } from '$lib/generated/routes';
  import EnhancedText from '$lib/components/EnhancedText.svelte';
  
  export let data;
  
  // Define login URL with redirect back to current page
  $: loginUrl = `/auth?next=${encodeURIComponent($page.url.pathname + $page.url.search)}`;
  
  let currentStage = 1; // 1: Audio only, 2: Show sentence, 3: Show translation
  let isIgnoring = false; // Track if we're currently ignoring a lemma
  let ignoreError = ''; // Store any error messages during ignore operation
  let ignoreSuccess = ''; // Store success message after ignoring
  let audioPlayer: any;
  let audioReplayCount = 0; // Track how many times audio is replayed
  let userSelectedSpeed = false; // Track if user manually changed playback speed
  let autoplayWasBlocked = false; // Track if autoplay was blocked by browser
  
  function nextStage() {
    if (currentStage < 3) {
      currentStage += 1;
    }
  }
  
  function playAudio() {
    if (audioPlayer && !data.audio_requires_login) {
      // Only count replays and auto-adjust in stage 1 (audio only) if user hasn't manually selected a speed
      if (currentStage === 1 && !userSelectedSpeed) {
        audioReplayCount++;
        
        // Gradually slow down playback on repeated plays in stage 1
        if (audioReplayCount === 2) {
          audioPlayer.setPlaybackRate(0.95);
        } else if (audioReplayCount === 3) {
          audioPlayer.setPlaybackRate(0.9);
        } else if (audioReplayCount === 4) {
          audioPlayer.setPlaybackRate(0.85);
        } else if (audioReplayCount >= 5) {
          audioPlayer.setPlaybackRate(0.8);
        }
      }
      
      audioPlayer.play();
    }
  }
  
  // Handle when user changes the playback speed
  function handleSpeedChanged(event: any) {
    userSelectedSpeed = true;
  }
  
  // Handle autoplay blocked event from AudioPlayer
  function handleAutoplayBlocked(event: any) {
    autoplayWasBlocked = true;
    console.log('Autoplay was blocked by browser policy, user needs to interact');
  }

  function prevStage() {
    if (currentStage > 1) {
      currentStage -= 1;
    }
    playAudio();
  }
  
  function nextSentence() {
    // Reset audio replay count, playback speed, and user selection flag
    if (audioPlayer) {
      audioPlayer.setPlaybackRate(1.0);
    }
    audioReplayCount = 0;
    userSelectedSpeed = false;
    
    // Get parameters for the URL
    const params = new URLSearchParams(window.location.search);
    const baseUrl = `/language/${data.metadata.target_language_code}/flashcards/random`;
    
    if (params.toString()) {
      window.location.href = `${baseUrl}?${params.toString()}`;
    } else {
      window.location.href = baseUrl;
    }
  }
  
  // Navigate back to flashcards landing page while preserving query parameters
  function navigateToFlashcards() {
    const params = new URLSearchParams(window.location.search);
    const baseUrl = `/language/${data.metadata.target_language_code}/flashcards`;
    
    if (params.toString()) {
      window.location.href = `${baseUrl}?${params.toString()}`;
    } else {
      window.location.href = baseUrl;
    }
  }
  
  // Function to clear filter and navigate back to all flashcards
  function clearFilter(event: Event) {
    event.preventDefault();
    const baseUrl = `/language/${data.metadata.target_language_code}/flashcards/random`;
    window.location.href = baseUrl;
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
    // Add keyboard event listener
    window.addEventListener('keydown', handleKeyDown);
    
    // Reset the audio replay count, playback speed, and user selection flag for new sentences
    audioReplayCount = 0;
    userSelectedSpeed = false;
    if (audioPlayer) {
      audioPlayer.setPlaybackRate(1.0);
    }
    
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
        <!-- Header with title and back button in same row -->
        <div class="d-flex align-items-center mb-4">
          <a 
            href={`/language/${data.metadata.target_language_code}/flashcards${$page.url.search}`}
            class="btn btn-outline-secondary back-button" 
            aria-label="Back to flashcards"
            title="Back to flashcards">
            <ArrowLeft size={20} weight="bold" />
          </a>
          
          <h2 class="flex-grow-1 text-center mb-0">{data.metadata.language_name} Flashcard</h2>
          
          <!-- Empty div to balance the layout -->
          <div style="width: 46px;"></div>
        </div>
        
        <!-- Navigation buttons moved above audio player -->
        <div class="row g-3 mb-4">
          <!-- First row with left/right navigation -->
          <div class="col-6">
            <button 
              class="btn btn-secondary w-100 py-3 play-audio-btn" 
              on:click={currentStage === 1 ? playAudio : prevStage}
              disabled={data.audio_requires_login}>
              {currentStage === 1 ? 'Play audio (←)' : currentStage === 2 ? 'Play audio (←)' : 'Show sentence (←)'}
            </button>
          </div>
          
          <div class="col-6">
            {#if currentStage < 3}
              <button 
                class="btn btn-secondary w-100 py-3" 
                on:click={nextStage}>
                {currentStage === 1 ? 'Show sentence (→)' : 'Show translation (→)'}
              </button>
            {:else}
              <!-- No button shown on final stage -->
              <div class="invisible w-100 py-3"></div>
            {/if}
          </div>
          
          <!-- New sentence button on second row -->
          <div class="col-12 mt-2">
            <button 
              class="btn btn-primary w-100 py-3" 
              on:click={nextSentence}>
              New sentence <KeyReturn size={18} weight="bold" class="ms-1" />
            </button>
          </div>
        </div>
        
        <div class="row align-items-center mb-3">
          <div class="col-12">
            <!-- Audio player (always visible, but may be disabled) -->
            {#if data.audio_requires_login}
              <Alert type="info" className="mb-3">
                Audio generation requires login.
                <a href={loginUrl} class="btn btn-sm btn-primary ms-2">Login</a>
              </Alert>
              <div class="w-100 mb-3" style="opacity: 0.5; pointer-events: none;">
                <AudioPlayer 
                  src={data.audio_url}
                  showControls={false}
                  showSpeedControls={false}
                  showDownload={false}
                />
              </div>
            {:else}
              <AudioPlayer
                bind:this={audioPlayer}
                src={data.audio_url}
                autoplay={true}
                showControls={true}
                showSpeedControls={true}
                showDownload={false}
                on:speedChanged={handleSpeedChanged}
                on:autoplayBlocked={handleAutoplayBlocked}
              />
            {/if}
            
            
            <!-- Sentence (visible in stage 2+) -->
            {#if currentStage >= 2}
              <!-- Replaced alert with a styled div -->
              <div class="flashcard-content-box border rounded p-4 mt-3 mb-3 bg-body-tertiary">
                <div class="text-center">
                  {#if data.recognized_words && data.recognized_words.length > 0}
                    <!-- Enhanced text with interactive word tooltips for the main sentence.
                         This makes individual words in the sentence hoverable with rich tooltips
                         showing translations, etymology, etc. The backend provides word recognition
                         data with positions, and EnhancedText handles the lazy-loaded tooltips. -->
                    <div class="flashcard-sentence-enhanced">
                      <EnhancedText 
                        text={data.text}
                        recognizedWords={data.recognized_words}
                        target_language_code={data.metadata.target_language_code}
                      />
                    </div>
                  {:else}
                    <!-- Fallback to plain text if no word recognition data -->
                    <a href={`/language/${data.metadata.target_language_code}/sentence/${data.slug}`} class="text-decoration-none">
                      <h3 class="font-weight-bold fs-2 mb-0 hz-foreign-text">{data.text}</h3>
                    </a>
                  {/if}
                </div>
              </div>
            {/if}
            
            <!-- Translation (visible in stage 3) -->
            {#if currentStage >= 3}
              <!-- Replaced alert with a styled div -->
              <div class="flashcard-content-box border rounded p-3 mb-3 bg-body-tertiary">
                <p class="text-center mb-0 fs-4 text-secondary translation-text">{data.translation}</p>
                <div class="text-center mt-3">
                  
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
                            <div class="lemma-enhanced-text me-1">
                              <!-- We reuse the EnhancedText component here to get fancy tooltips for lemmas.
                                   Even though EnhancedText is designed for text with multiple words, we can use it
                                   for individual lemmas by treating each lemma as a single-word "text" with one
                                   recognized word spanning the entire text. This gives us:
                                   - Lazy loading tooltips (data fetched on hover)
                                   - Rich tooltip content (translations, etymology, etc.)
                                   - Consistent styling with other enhanced text in the app
                                   - Automatic linking to the wordform page (which redirects to lemma page)
                                   The wordform API endpoint handles lemmas fine since lemmas ARE wordforms. -->
                              <EnhancedText 
                                text={lemma}
                                recognizedWords={[{
                                  word: lemma,
                                  start: 0,
                                  end: lemma.length,
                                  lemma: lemma,
                                  translations: [], // Will be fetched on hover via the tooltip
                                }]}
                                target_language_code={data.metadata.target_language_code}
                              />
                            </div>
                            <button
                              class="btn btn-link p-0 border-0 text-secondary lh-1 ignore-btn"
                              title={`Ignore "${lemma}" in future flashcards`}
                              on:click={() => ignoreLemma(lemma)}
                              disabled={isIgnoring}
                            >
                              {#if isIgnoring}
                                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                              {:else}
                                <Prohibit size={16} weight="regular" />
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
        
        
        <div class="text-center mt-3 mb-4">
          <p class="text-muted small mb-4">
            Press ← / → arrow keys to navigate, ENTER for next sentence
          </p>
          
          {#if data.sourcefile || data.sourcedir}
            <div class="hz-filter-banner mx-auto" style="max-width: 600px;">
              <span class="d-flex align-items-center me-2" title="This content is filtered to show sentences from a specific source">
                <FunnelSimple size={24} weight="fill" />
              </span>
              <div>
                <p class="mb-0">
                  Filtered by {data.sourcedir ? 'directory' : 'file'}: 
                  {#if data.sourcedir}
                    <strong>
                      <a href={getPageUrl('sourcedir', {
                        target_language_code: data.metadata.target_language_code,
                        sourcedir_slug: data.sourcedir.slug
                      })} class="text-decoration-none">{data.sourcedir.name}</a>
                    </strong>
                  {:else if data.sourcefile}
                    <strong>
                      <a href={getPageUrl('sourcefile', {
                        target_language_code: data.metadata.target_language_code,
                        sourcedir_slug: data.sourcefile.sourcedir_slug,
                        sourcefile_slug: data.sourcefile.slug
                      })} class="text-decoration-none">{data.sourcefile.name}</a>
                    </strong>
                  {/if}
                </p>
              </div>
              <button type="button" on:click={clearFilter} class="ms-auto btn btn-outline-secondary clear-filter d-flex align-items-center justify-content-center" aria-label="Clear filter" title="Remove filter">
                <X size={18} weight="bold" />
              </button>
            </div>
          {/if}
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
  
  /* Lemma enhanced text styling */
  .lemma-enhanced-text {
    display: inline-block;
    font-size: 1rem;
  }
  
  /* Override EnhancedText's default styles for this context */
  .lemma-enhanced-text :global(.enhanced-text) {
    font-size: inherit;
    line-height: inherit;
    max-width: none;
  }
  
  /* Ensure the word links in lemma list have appropriate styling */
  .lemma-enhanced-text :global(.word-link) {
    font-size: 1rem;
    font-family: var(--hz-font-foreign) !important;
    font-style: italic;
  }
  
  /* Flashcard sentence enhanced text styling */
  .flashcard-sentence-enhanced {
    display: block;
    text-align: center;
  }
  
  /* Override EnhancedText's default styles for the main sentence */
  .flashcard-sentence-enhanced :global(.enhanced-text) {
    font-size: 2rem;
    font-weight: normal;
    line-height: 1.2;
    max-width: none;
    text-align: center;
    font-family: var(--hz-font-foreign) !important;
    font-style: italic;
  }
  
  /* Style the word links in the main sentence */
  .flashcard-sentence-enhanced :global(.word-link) {
    font-size: inherit;
    font-weight: inherit;
    font-family: inherit;
    font-style: inherit;
    color: var(--hz-color-primary-green);
    text-decoration: none;
    border-bottom: 2px dotted var(--hz-color-primary-green);
    transition: all 0.2s ease-in-out;
    padding: 0 2px;
    margin: 0 1px;
  }
  
  .flashcard-sentence-enhanced :global(.word-link:hover) {
    color: var(--hz-color-primary-green-light);
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.1);
    border-bottom-color: var(--hz-color-primary-green-light);
  }
  
  /* Typography styles using theme variables */
  .hz-foreign-text {
    font-family: var(--hz-font-foreign) !important;
    font-style: italic;
  }
  
  .translation-text {
    font-family: var(--hz-font-main) !important;
    font-style: normal;
  }
  
  /* Optional: Additional customizations can be added here if needed */
  
  /* Clear filter button styling */
  .clear-filter {
    background-color: transparent;
    border-color: var(--hz-color-border);
    color: var(--hz-color-text-main);
    width: 36px;
    height: 36px;
    padding: 0;
  }
  
  .clear-filter:hover {
    background-color: var(--hz-color-primary-green-dark);
    border-color: var(--hz-color-primary-green);
    color: var(--hz-color-text-main);
  }
  
  /* Back button styling */
  .back-button {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 46px;
    height: 46px;
    padding: 0;
    border-radius: 8px;
  }
  
  /* Add pulsing animation to play button when autoplay fails */
  @keyframes gentle-pulse {
    0% { box-shadow: 0 0 0 0 rgba(var(--hz-color-primary-green-rgb), 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(var(--hz-color-primary-green-rgb), 0); }
    100% { box-shadow: 0 0 0 0 rgba(var(--hz-color-primary-green-rgb), 0); }
  }
  
  /* Apply animation when audio element reports it needs interaction */
  .audio-player-needs-interaction ~ .row .play-audio-btn {
    animation: gentle-pulse 2s infinite;
    background-color: var(--hz-color-primary-green);
    border-color: var(--hz-color-primary-green-dark);
  }
</style> 