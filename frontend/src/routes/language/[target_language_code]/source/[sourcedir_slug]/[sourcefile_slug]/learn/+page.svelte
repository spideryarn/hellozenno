<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import Card from '$lib/components/Card.svelte';
  import Alert from '$lib/components/Alert.svelte';
  import { AudioPlayer } from '$lib';
  import { API_BASE_URL } from '$lib/config';
  import LemmaContent from '$lib/components/LemmaContent.svelte';

  // No exported props required for this page in MVP

  let loadingSummary = true;
  let summaryError: string | null = null;
  let lemmas: Array<any> = [];
  let sourceText: string = '';

  let generating = false;
  let generateError: string | null = null;
  let cards: Array<{
    sentence: string;
    translation: string;
    used_lemmas: string[];
    language_level?: string;
    audio_data_url: string;
  }> = [];

  let currentIndex = 0;
  let currentStage = 1; // 1: audio; 2: sentence; 3: translation
  let audioPlayer: any;

  $: target_language_code = $page.params.target_language_code;
  $: sourcedir_slug = $page.params.sourcedir_slug;
  $: sourcefile_slug = $page.params.sourcefile_slug;

  async function fetchSummary() {
    loadingSummary = true;
    summaryError = null;
    try {
      const url = `${API_BASE_URL}/api/lang/learn/sourcefile/${encodeURIComponent(target_language_code)}/${encodeURIComponent(sourcedir_slug)}/${encodeURIComponent(sourcefile_slug)}/summary?top=20`;
      const res = await fetch(url);
      if (!res.ok) {
        const err = await safeJson(res);
        throw new Error(err?.message || `Failed summary (${res.status})`);
      }
      const js = await res.json();
      lemmas = js?.lemmas || [];

      // Also fetch the original source text for context sentence extraction
      const textRes = await fetch(`${API_BASE_URL}/api/lang/sourcefile/${encodeURIComponent(target_language_code)}/${encodeURIComponent(sourcedir_slug)}/${encodeURIComponent(sourcefile_slug)}/text`);
      if (textRes.ok) {
        const td = await textRes.json();
        sourceText = td?.sourcefile?.text_target || td?.text_data?.text_target || '';
      }
    } catch (e: any) {
      summaryError = e?.message || 'Failed to load summary';
    } finally {
      loadingSummary = false;
    }
  }

  async function safeJson(res: Response) {
    try { return await res.json(); } catch { return {}; }
  }

  async function startPractice() {
    generateError = null;
    generating = true;
    currentIndex = 0;
    currentStage = 1;
    cards = [];
    try {
      const url = `${API_BASE_URL}/api/lang/learn/sourcefile/${encodeURIComponent(target_language_code)}/${encodeURIComponent(sourcedir_slug)}/${encodeURIComponent(sourcefile_slug)}/generate`;
      const body = {
        lemmas: lemmas.map((l) => l.lemma).slice(0, 20),
        num_sentences: 10,
        language_level: null,
      };
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await safeJson(res);
        throw new Error(err?.message || `Generation failed (${res.status})`);
      }
      const js = await res.json();
      cards = js?.sentences || [];
      currentIndex = 0;
      currentStage = 1;
    } catch (e: any) {
      generateError = e?.message || 'Failed to generate practice set';
    } finally {
      generating = false;
    }
  }

  function playAudio() {
    if (audioPlayer && cards.length > 0) {
      audioPlayer.play();
    }
  }
  function nextStage() {
    if (currentStage < 3) currentStage += 1;
  }
  function prevStage() {
    if (currentStage > 1) currentStage -= 1; else playAudio();
  }
  function nextCard() {
    if (currentIndex < cards.length - 1) {
      currentIndex += 1;
      currentStage = 1;
    }
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (cards.length === 0) return;
    if (event.key === 'ArrowRight') nextStage();
    else if (event.key === 'ArrowLeft') prevStage();
    else if (event.key === 'Enter') nextCard();
  }

  onMount(() => {
    fetchSummary();
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  });

  function getContextSentence(text: string, lemma: string | undefined): string | undefined {
    if (!text || !lemma) return undefined;
    const sentences = text.split(/(?<=[.!?])\s+/);
    const idx = sentences.findIndex(s => s.includes(lemma));
    if (idx >= 0) return sentences[idx];
    return undefined;
  }
</script>

<svelte:head>
  <title>Learn from sourcefile (MVP)</title>
  <meta name="robots" content="noindex" />
  <meta name="description" content="Priority words and generated audio flashcards" />
</svelte:head>

<div class="container my-4">
  <div class="row g-4">
    <div class="col-12 col-xl-5">
      <Card title="Priority words">
        {#if loadingSummary}
          <div class="text-center py-3">Loading…</div>
        {:else if summaryError}
          <Alert type="danger">{summaryError}</Alert>
        {:else if !lemmas.length}
          <Alert type="warning">No lemmas found for this sourcefile.</Alert>
        {:else}
          <div class="d-flex flex-column gap-3">
            {#each lemmas as l}
              <LemmaContent lemma_metadata={l} target_language_code={target_language_code} showFullLink={false} isAuthError={false} context_sentence={getContextSentence(sourceText, l?.lemma)} />
            {/each}
          </div>
        {/if}
      </Card>

      <div class="mt-3">
        <button class="btn btn-primary w-100 py-3" on:click={startPractice} disabled={generating || !lemmas.length}>
          {generating ? 'Preparing practice…' : 'Start practice'}
        </button>
        {#if generateError}
          <div class="mt-2"><Alert type="danger">{generateError}</Alert></div>
        {/if}
      </div>
    </div>

    <div class="col-12 col-xl-7">
      <Card title="Practice">
        {#if cards.length === 0}
          <div class="text-center py-4 text-muted">Click "Start practice" to generate flashcards.</div>
        {:else}
          <div class="mb-3">
            <div class="row g-2">
              <div class="col-6">
                <button class="btn btn-secondary w-100 py-3" on:click={currentStage === 1 ? playAudio : prevStage}>
                  {currentStage === 1 ? 'Play audio (←)' : currentStage === 2 ? 'Play audio (←)' : 'Show sentence (←)'}
                </button>
              </div>
              <div class="col-6">
                {#if currentStage < 3}
                  <button class="btn btn-secondary w-100 py-3" on:click={nextStage}>
                    {currentStage === 1 ? 'Show sentence (→)' : 'Show translation (→)'}
                  </button>
                {:else}
                  <div class="invisible w-100 py-3"></div>
                {/if}
              </div>
              <div class="col-12 mt-2">
                <button class="btn btn-primary w-100 py-3" on:click={nextCard} disabled={currentIndex >= cards.length - 1}>
                  Next card (Enter)
                </button>
              </div>
            </div>
          </div>

          <div class="mb-3">
            <AudioPlayer bind:this={audioPlayer} src={cards[currentIndex].audio_data_url} autoplay={true} showControls={true} showSpeedControls={true} showDownload={false} />
          </div>

          {#if currentStage >= 2}
            <div class="flashcard-box sentence-box">
              <h3 class="hz-foreign-text text-center mb-0">{cards[currentIndex].sentence}</h3>
            </div>
          {/if}

          {#if currentStage >= 3}
            <div class="flashcard-box translation-box">
              <p class="text-center mb-0 fs-4">{cards[currentIndex].translation}</p>
            </div>
          {/if}
        {/if}
      </Card>
    </div>
  </div>
</div>

<style>
  .flashcard-box {
    border: 1px solid var(--hz-color-border);
    border-radius: 8px;
    padding: 1rem;
    background-color: var(--bs-body-tertiary, #2b2b2b);
  }
  .sentence-box {
    margin-bottom: 0.75rem;
  }
</style>


