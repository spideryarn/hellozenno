<script lang="ts">
  import { onMount, tick } from 'svelte';
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
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  // Use dynamic import for p-queue to avoid build-time type resolution issues

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
  let loadingLemmaMap: Record<string, boolean> = {};
  let warmingQueue: any = null;
  let showWordsPanel = true;
  let practiceSectionEl: HTMLElement | null = null;
  
  
  function shuffleArray<T>(input: T[]): T[] {
    const arr = input.slice();
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }
  async function ensureWarmingQueue() {
    if (warmingQueue) return warmingQueue;
    try {
      const mod = await import('p-queue');
      const PQueue = (mod as any).default ?? (mod as any);
      warmingQueue = new PQueue({ concurrency: 2 });
    } catch (e) {
      // Fallback minimal queue with concurrency 1
      const tasks: Array<() => Promise<any>> = [];
      let running = false;
      const runNext = async () => {
        if (running) return;
        running = true;
        while (tasks.length) {
          const t = tasks.shift()!;
          try { await t(); } finally {}
        }
        running = false;
      };
      warmingQueue = {
        add(fn: () => Promise<any>) { tasks.push(fn); runNext(); return Promise.resolve(); },
        onIdle() { return Promise.resolve(); }
      };
    }
    return warmingQueue;
  }

  $: target_language_code = $page.params.target_language_code;
  $: sourcedir_slug = $page.params.sourcedir_slug;
  $: sourcefile_slug = $page.params.sourcefile_slug;

  async function fetchSummary() {
    loadingSummary = true;
    summaryError = null;
    try {
      // Authenticated request so backend can generate lemma metadata on-demand
      const js = await apiFetch({
        supabaseClient: ($page.data as any).supabase ?? null,
        routeName: RouteName.LEARN_API_LEARN_SOURCEFILE_SUMMARY_API,
        params: { target_language_code, sourcedir_slug, sourcefile_slug },
        options: { method: 'GET' },
        searchParams: { top: 20 },
        timeoutMs: 60000,
      });
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
      await ensureWarmingQueue();
      // Warm currently visible lemma and a small lookahead in background
      warmTopLemmasInBackground(visibleLemmas.slice(0, 5).map((l) => l.lemma));
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
      const body = {
        lemmas: lemmas
          .map((l) => l.lemma)
          .filter((lm) => !ignoredLemmas.has(lm))
          .slice(0, 20),
        num_sentences: 10,
        language_level: null,
      };
      const js = await apiFetch({
        supabaseClient: ($page.data as any).supabase ?? null,
        routeName: RouteName.LEARN_API_LEARN_SOURCEFILE_GENERATE_API,
        params: { target_language_code, sourcedir_slug, sourcefile_slug },
        options: {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
        timeoutMs: 120000,
      });
      cards = shuffleArray(js?.sentences || []);
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
      const body = {
        lemmas: visibleLemmas.map((l) => l.lemma).slice(0, 20),
        num_sentences: 10,
        language_level: null,
      };
      const js = await apiFetch({
        supabaseClient: ($page.data as any).supabase ?? null,
        routeName: RouteName.LEARN_API_LEARN_SOURCEFILE_GENERATE_API,
        params: { target_language_code, sourcedir_slug, sourcefile_slug },
        options: {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
        timeoutMs: 120000,
      });
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
      cards = shuffleArray(preparedCards);
      currentIndex = 0;
      currentStage = 1;
      return;
    }
    startPractice();
  }

  async function startPracticeAndNavigate() {
    showWordsPanel = false;
    await tick();
    startOrShowPractice();
    await tick();
    if (practiceSectionEl) {
      practiceSectionEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function warmTopLemmasInBackground(lemmasToWarm: string[]) {
    if (!lemmasToWarm || lemmasToWarm.length === 0) return;
    const supabase = ($page.data as any).supabase ?? null;
    for (const lemma of lemmasToWarm) {
      if (!lemma) continue;
      if (loadingLemmaMap[lemma]) continue;
      loadingLemmaMap[lemma] = true;
      loadingLemmaMap = { ...loadingLemmaMap };
      // Queue each warming task with low priority
      ensureWarmingQueue().then(() => warmingQueue.add(async () => {
        try {
          await apiFetch({
            supabaseClient: supabase,
            routeName: RouteName.LEMMA_API_GET_LEMMA_METADATA_API,
            params: { target_language_code, lemma },
            options: { method: 'GET' },
            timeoutMs: 60000,
          });
        } catch (e) {
          // ignore
        } finally {
          loadingLemmaMap[lemma] = false;
          loadingLemmaMap = { ...loadingLemmaMap };
        }
      }, { priority: 0 }));
    }
  }

  // Warm the current lemma and a small lookahead whenever the selection changes
  $: if (visibleLemmas.length) {
    const lookahead = 3;
    const toWarm: string[] = [];
    for (let i = 0; i < lookahead && currentLemmaIndex + i < visibleLemmas.length; i++) {
      const lm = visibleLemmas[currentLemmaIndex + i]?.lemma;
      if (lm) toWarm.push(lm);
    }
    warmTopLemmasInBackground(toWarm);
  }

  // For complete keyboard shortcuts reference, see frontend/docs/KEYBOARD_SHORTCUTS.md
  function handleKeyDown(event: KeyboardEvent) {
    // If practice hasn't started yet, use arrows to browse priority words
    if (cards.length === 0) {
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
        event.preventDefault();
        event.stopPropagation();
        if (event.key === 'ArrowRight') nextLemma();
        else prevLemma();
      }
      return;
    }
    // During practice, keep flashcard shortcuts
    const active = (document.activeElement as HTMLElement | null);
    const tag = active?.tagName?.toLowerCase();
    const isEditable = active?.isContentEditable || tag === 'input' || tag === 'textarea' || tag === 'select';
    if (isEditable) return;

    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      event.stopPropagation();
      if (event.key === 'ArrowRight') nextStage();
      else prevStage();
    } else if (event.key === 'Enter') {
      // Avoid double advance if Next button is focused (let click handler fire)
      if (active && active.id === 'next-card-btn') return;
      event.preventDefault();
      event.stopPropagation();
      nextCard();
    }
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

  function getAllContextSentences(text: string, lemma: string | undefined, forms: string[]): string[] {
    if (!text) return [];
    const searchTerms = new Set<string>();
    if (lemma) searchTerms.add(lemma);
    for (const f of forms || []) if (f) searchTerms.add(f);
    const sentences = text.split(/(?<=[.!?;··])\s+/);
    const result: string[] = [];
    for (const s of sentences) {
      for (const term of searchTerms) {
        if (s.includes(term)) { result.push(s); break; }
      }
    }
    // Deduplicate while preserving order
    return Array.from(new Set(result));
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
      // Invalidate any prepared deck and re-prepare with the updated lemma set
      preparedCards = [];
      preparedError = null;
      if (!generating) {
        preparePracticeInBackground();
      }
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

<div class="container my-4 learn-container">
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
      <button class="btn btn-primary py-2" on:click={startPracticeAndNavigate} disabled={generating || preparing || !lemmas.length}>
        {preparing ? 'Preparing…' : 'Start practice'}
      </button>
      <button class="btn btn-outline-secondary py-2" on:click={() => showWordsPanel = !showWordsPanel}>
        {showWordsPanel ? 'Hide words' : 'Show words'}
      </button>
    </div>
  </div>

  <!-- Anchor for smooth scroll when starting practice -->
  <div id="learn-practice-section" bind:this={practiceSectionEl}></div>

  <div class="row g-4">
    <div class="col-12" class:col-xl-5={cards.length > 0}>
      {#if showWordsPanel}
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
              {#if loadingLemmaMap[visibleLemmas[currentLemmaIndex]?.lemma]}
                <div class="d-flex justify-content-center py-4"><LoadingSpinner /></div>
              {:else}
                <LemmaContent
                  lemma_metadata={visibleLemmas[currentLemmaIndex]}
                  target_language_code={target_language_code}
                  showFullLink={false}
                  isAuthError={false}
                  context_sentence={getContextSentence(sourceText, visibleLemmas[currentLemmaIndex]?.lemma)}
                  source_wordforms={sourcefileWordforms[visibleLemmas[currentLemmaIndex]?.lemma] || []}
                  source_sentences={getAllContextSentences(
                    sourceText,
                    visibleLemmas[currentLemmaIndex]?.lemma,
                    sourcefileWordforms[visibleLemmas[currentLemmaIndex]?.lemma] || []
                  )}
                  showIgnore={true}
                  on:ignore={(e) => ignoreLemma(e.detail.lemma)}
                />
              {/if}
            </div>
          {/if}
          
        {/if}
      </Card>
      {/if}

      {#if generateError}
        <div class="mt-2"><Alert type="danger">{generateError}</Alert></div>
      {/if}
    </div>

    {#if cards.length > 0}
    <div class="col-12 col-xl-7">
      {#if cards.length > 0}
      <Card title="Practice">
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
                <button class="btn btn-primary w-100 py-3" on:click={() => { if (currentIndex < cards.length - 1) { currentIndex += 1; currentStage = 1; } }} disabled={currentIndex >= cards.length - 1}>
                  Next card (Enter)
                </button>
              </div>
            </div>
          </div>

          {#key currentIndex}
            <div class="mb-3">
              <AudioPlayer bind:this={audioPlayer} src={cards[currentIndex].audio_data_url} autoplay={true} showControls={true} showSpeedControls={true} showDownload={false} />
            </div>

          {#if currentStage >= 2}
            <div class="flashcard-box sentence-box">
              <h3 class="hz-foreign-text text-center mb-0">{cards[currentIndex].sentence}</h3>
            </div>
          {/if}
          {/key}

          {#if currentStage >= 3}
            <div class="flashcard-box translation-box">
              <p class="text-center mb-0 fs-4">{cards[currentIndex].translation}</p>
            </div>
          {/if}
      </Card>
      {/if}
    </div>
    {/if}
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

  /* Match wider layout on large screens (like other sourcefile pages) */
  @media (min-width: 992px) {
    .learn-container {
      max-width: 90%;
      margin-left: auto;
      margin-right: auto;
    }
  }
</style>


