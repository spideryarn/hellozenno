<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import Card from '$lib/components/Card.svelte';
  import Alert from '$lib/components/Alert.svelte';
  import { AudioPlayer } from '$lib';
  import { API_BASE_URL } from '$lib/config';
  import { apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import LemmaContent from '$lib/components/LemmaContent.svelte';
  import CaretLeft from 'phosphor-svelte/lib/CaretLeft';
  import CaretRight from 'phosphor-svelte/lib/CaretRight';

  // No exported props required for this page in MVP

  let loadingSummary = true;
  let summaryError: string | null = null;
  let lemmas: Array<any> = [];
  let ignoredLemmas: Set<string> = new Set();
  let sourcefileWordforms: Record<string, string[]> = {};
  let sourceText: string = '';

  // One-at-a-time navigation for priority words
  let currentLemmaIndex = 0;
  $: visibleLemmas = lemmas.filter((x) => !ignoredLemmas.has(x.lemma));
  $: { if (currentLemmaIndex >= visibleLemmas.length) currentLemmaIndex = Math.max(0, visibleLemmas.length - 1); }

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

  // Background preparation of practice deck
  let preparing = false;
  let preparedCards: typeof cards = [];
  let preparedError: string | null = null;
  let preloadedAudios: HTMLAudioElement[] = [];

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
        const wordforms = td?.wordforms || [];
        // Build map of lemma -> forms present in this sourcefile
        sourcefileWordforms = {};
        for (const wf of wordforms) {
          const lemma = wf?.lemma;
          const form = wf?.wordform;
          if (lemma && form) {
            if (!sourcefileWordforms[lemma]) sourcefileWordforms[lemma] = [];
            if (!sourcefileWordforms[lemma].includes(form)) sourcefileWordforms[lemma].push(form);
          }
        }
      }

      // Fetch ignored lemmas for the current user; ignore errors silently
      try {
        const ignored = await apiFetch({
          supabaseClient: ($page.data as any).supabase ?? null,
          routeName: RouteName.LEMMA_API_GET_IGNORED_LEMMAS_API,
          params: { target_language_code },
          options: { method: 'GET' },
        });
        if (Array.isArray(ignored)) {
          ignoredLemmas = new Set(ignored.map((x: any) => x.lemma));
        }
      } catch (e) {
        // not logged in or API error; proceed without filtering
      }
    } catch (e: any) {
      summaryError = e?.message || 'Failed to load summary';
    } finally {
      loadingSummary = false;
    }
    // Kick off background preparation once summary is available
    if (!summaryError && lemmas.length > 0) {
      preparePracticeInBackground();
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
        lemmas: lemmas
          .map((l) => l.lemma)
          .filter((lm) => !ignoredLemmas.has(lm))
          .slice(0, 20),
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
  function prevLemma() {
    if (visibleLemmas.length === 0) return;
    if (currentLemmaIndex > 0) currentLemmaIndex -= 1;
  }
  function nextLemma() {
    if (visibleLemmas.length === 0) return;
    if (currentLemmaIndex < visibleLemmas.length - 1) currentLemmaIndex += 1;
  }
  function nextCard() {
    if (currentIndex < cards.length - 1) {
      currentIndex += 1;
      currentStage = 1;
    }
  }

  function preloadAudioDataUrls(urls: string[]) {
    try {
      for (const url of urls) {
        const a = new Audio();
        a.src = url;
        a.preload = 'auto';
        a.load();
        preloadedAudios.push(a);
      }
    } catch (e) {
      // Non-fatal; ignore
    }
  }

  async function preparePracticeInBackground() {
    if (preparing || generating) return;
    if (!visibleLemmas.length) return;
    preparing = true;
    preparedError = null;
    preparedCards = [];
    try {
      const url = `${API_BASE_URL}/api/lang/learn/sourcefile/${encodeURIComponent(target_language_code)}/${encodeURIComponent(sourcedir_slug)}/${encodeURIComponent(sourcefile_slug)}/generate`;
      const body = {
        lemmas: visibleLemmas.map((l) => l.lemma).slice(0, 20),
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
        throw new Error(err?.message || `Preparation failed (${res.status})`);
      }
      const js = await res.json();
      preparedCards = js?.sentences || [];
      // Preload audio data URLs
      preloadAudioDataUrls(preparedCards.map((c: any) => c.audio_data_url).filter(Boolean));
    } catch (e: any) {
      preparedError = e?.message || 'Failed to prepare practice set';
    } finally {
      preparing = false;
    }
  }

  function startOrShowPractice() {
    if (preparedCards.length > 0 && !preparing) {
      cards = preparedCards;
      currentIndex = 0;
      currentStage = 1;
      return;
    }
    startPractice();
  }

  // For complete keyboard shortcuts reference, see frontend/docs/KEYBOARD_SHORTCUTS.md
  function handleKeyDown(event: KeyboardEvent) {
    // If practice hasn't started yet, use arrows to browse priority words
    if (cards.length === 0) {
      if (event.key === 'ArrowRight') nextLemma();
      else if (event.key === 'ArrowLeft') prevLemma();
      return;
    }
    // During practice, keep flashcard shortcuts
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

  async function ignoreLemma(lemma: string) {
    try {
      await apiFetch({
        supabaseClient: ($page.data as any).supabase ?? null,
        routeName: RouteName.LEMMA_API_IGNORE_LEMMA_API,
        params: { target_language_code, lemma },
        options: { method: 'POST' },
      });
      ignoredLemmas.add(lemma);
      // Remove from current list without refetch
      lemmas = lemmas.filter((x) => x?.lemma !== lemma);
    } catch (e: any) {
      alert(e?.message || 'Failed to ignore lemma');
    }
  }
</script>

<svelte:head>
  <title>Learn from sourcefile (MVP)</title>
  <meta name="robots" content="noindex" />
  <meta name="description" content="Priority words and generated audio flashcards" />
</svelte:head>

<div class="container my-4">
  <!-- Top actions bar -->
  <div class="d-flex align-items-center justify-content-between flex-wrap mb-3 top-actions">
    <div class="small text-muted">
      {#if preparing}
        Preparing practice set…
      {:else if preparedCards.length}
        Practice ready ({preparedCards.length} cards)
      {:else if preparedError}
        <span class="text-danger">{preparedError}</span>
      {/if}
    </div>
    <div class="d-flex align-items-center gap-2">
      <button class="btn btn-primary py-2" on:click={startOrShowPractice} disabled={generating || preparing || !lemmas.length}>
        {preparing ? 'Preparing…' : 'Start practice'}
      </button>
    </div>
  </div>

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
          <!-- Compact list of priority words with translations -->
          <div class="top-lemma-list mb-3">
            {#each visibleLemmas as l, i}
              <button
                class="btn btn-sm btn-secondary text-on-light me-2 mb-2 {currentLemmaIndex === i ? 'active' : ''}"
                title={(l.translations && l.translations.length) ? l.translations.join(', ') : ''}
                on:click={() => currentLemmaIndex = i}
              >
                <span class="hz-foreign-text">{l.lemma}</span>
                {#if l.translations && l.translations.length}
                  <span class="ms-1">{l.translations[0]}</span>
                {/if}
              </button>
            {/each}
          </div>

          <!-- One-at-a-time lemma viewer with nav buttons -->
          <div class="d-flex align-items-center justify-content-between mb-2">
            <button class="btn btn-outline-secondary" on:click={prevLemma} disabled={currentLemmaIndex <= 0} aria-label="Previous word">
              <CaretLeft size={18} weight="bold" />
            </button>
            <div class="small text-muted">({visibleLemmas.length ? currentLemmaIndex + 1 : 0}/{visibleLemmas.length})</div>
            <button class="btn btn-outline-secondary" on:click={nextLemma} disabled={currentLemmaIndex >= visibleLemmas.length - 1} aria-label="Next word">
              <CaretRight size={18} weight="bold" />
            </button>
          </div>

          {#if visibleLemmas.length}
            <div class="priority-words one-at-a-time">
              <LemmaContent
                lemma_metadata={visibleLemmas[currentLemmaIndex]}
                target_language_code={target_language_code}
                showFullLink={false}
                isAuthError={false}
                context_sentence={getContextSentence(sourceText, visibleLemmas[currentLemmaIndex]?.lemma)}
                source_wordforms={sourcefileWordforms[visibleLemmas[currentLemmaIndex]?.lemma] || []}
                showIgnore={true}
                on:ignore={(e) => ignoreLemma(e.detail.lemma)}
              />
            </div>
          {/if}
        {/if}
      </Card>

      {#if generateError}
        <div class="mt-2"><Alert type="danger">{generateError}</Alert></div>
      {/if}
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

  /* Remove hover accent from Card headers inside priority words list to avoid thicker dividers */
  .priority-words :global(.lemma-details-card.card::before) { display: none; }
  .priority-words :global(.lemma-details-card.card:hover) { transform: none; box-shadow: none; }
</style>


