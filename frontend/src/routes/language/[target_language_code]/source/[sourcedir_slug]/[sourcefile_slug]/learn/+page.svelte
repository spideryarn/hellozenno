<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { page } from '$app/stores';
  import Card from '$lib/components/Card.svelte';
  import Alert from '$lib/components/Alert.svelte';
  import { AudioPlayer } from '$lib';
  import { API_BASE_URL, LEARN_DEFAULT_TOP_WORDS, LEARN_DEFAULT_NUM_CARDS, LEARN_DEFAULT_CEFR } from '$lib/config';
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
  let sourcefileLevel: string | null = null;

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
  let preparedMeta: any = null;
  let preparedError: string | null = null;
  let preloadedAudios: HTMLAudioElement[] = [];
  let loadingLemmaMap: Record<string, boolean> = {};
  let warmingQueue: any = null;
  let prepareAbortCtrl: AbortController | null = null;
  let showWordsPanel = true;
  let showOptions = false;
  let showWordsHelp = false;
  let showKbHelp = false;
  let practiceSectionEl: HTMLElement | null = null;
  let lemmaSectionEl: HTMLElement | null = null;
  // Settings
  let settingTopK: number = LEARN_DEFAULT_TOP_WORDS;
  let settingNumSentences: number = LEARN_DEFAULT_NUM_CARDS;
  let settingLanguageLevel: string = LEARN_DEFAULT_CEFR; // '' means Any; 'sourcefile' to use sourcefile level
  let summaryMeta: any = null;

  type CardMetrics = {
    replayCount: number;
    startedAt: number | null;
    revealSentenceAt: number | null;
    revealTranslationAt: number | null;
  };
  let cardMetrics: CardMetrics[] = [];
  let sessionSaved = false;
  // Collapsible word chips list (workaround to keep lemma section visible)
  let showWordChips = false;
  function scrollToLemmaSection() {
    if (lemmaSectionEl) {
      lemmaSectionEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  
  
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
        searchParams: { top: settingTopK },
        timeoutMs: 60000,
      });
      lemmas = js?.lemmas || [];
      summaryMeta = js?.meta || null;
      if (summaryMeta?.durations) {
        console.log('Learn summary durations', summaryMeta.durations);
      }

      // Also fetch the original source text for context sentence extraction
      const textRes = await fetch(`${API_BASE_URL}/api/lang/sourcefile/${encodeURIComponent(target_language_code)}/${encodeURIComponent(sourcedir_slug)}/${encodeURIComponent(sourcefile_slug)}/text`);
      if (textRes.ok) {
        const td = await textRes.json();
        sourceText = td?.sourcefile?.text_target || td?.text_data?.text_target || '';
        sourcefileLevel = (td?.sourcefile?.language_level || '').toUpperCase() || null;
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
      let langLevel = settingLanguageLevel ? settingLanguageLevel : null;
      if (settingLanguageLevel === 'sourcefile') {
        langLevel = sourcefileLevel || null;
      }
      const body = {
        lemmas: lemmas
          .map((l) => l.lemma)
          .filter((lm) => !ignoredLemmas.has(lm))
          .slice(0, 20),
        num_sentences: settingNumSentences,
        language_level: langLevel,
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
      const sentences = js?.sentences || [];
      const meta = js?.meta || {};
      if (meta?.durations) {
        console.log('Learn generate durations (on-demand)', meta.durations);
      }
      const keepOrder = typeof meta?.new_count === 'number' ? meta.new_count > 0 : false;
      cards = keepOrder ? sentences : shuffleArray(sentences);
      currentIndex = 0;
      currentStage = 1;
      resetMetricsForNewDeck(cards);
      markCardStartedIfNeeded();
    } catch (e: any) {
      generateError = e?.message || 'Failed to generate practice set';
    } finally {
      generating = false;
    }
  }

  function playAudio() {
    if (audioPlayer && cards.length > 0) {
      // Count replay only when on stage 1 (audio-only)
      try {
        if (currentStage === 1 && cardMetrics[currentIndex]) {
          cardMetrics[currentIndex].replayCount += 1;
          cardMetrics = [...cardMetrics];
        }
      } catch {}
      audioPlayer.play();
    }
  }
  function nextStage() {
    if (currentStage < 3) {
      const prev = currentStage;
      currentStage += 1;
      // Record first reveal timestamps
      try {
        const m = cardMetrics[currentIndex];
        const now = Date.now();
        if (prev === 1 && currentStage === 2 && m && m.revealSentenceAt == null) m.revealSentenceAt = now;
        if (prev === 2 && currentStage === 3 && m && m.revealTranslationAt == null) m.revealTranslationAt = now;
        cardMetrics = [...cardMetrics];
      } catch {}
    }
  }
  function prevStage() {
    if (currentStage > 1) currentStage -= 1; else playAudio();
  }
  async function prevLemma() {
    if (visibleLemmas.length === 0) return;
    if (currentLemmaIndex > 0) {
      currentLemmaIndex -= 1;
      await tick();
      scrollToLemmaSection();
    }
  }
  async function nextLemma() {
    if (visibleLemmas.length === 0) return;
    if (currentLemmaIndex < visibleLemmas.length - 1) {
      currentLemmaIndex += 1;
      await tick();
      scrollToLemmaSection();
    }
  }
  async function goToLemma(index: number) {
    if (index < 0 || index >= visibleLemmas.length) return;
    currentLemmaIndex = index;
    await tick();
    scrollToLemmaSection();
  }
  function nextCard() {
    if (currentIndex < cards.length - 1) {
      currentIndex += 1;
      currentStage = 1;
      markCardStartedIfNeeded();
    }
  }

  function preloadAudioDataUrls(urls: string[]) {
    try {
      // Limit concurrent preloads to reduce DB pressure
      const limited = urls.slice(0, 2);
      for (const url of limited) {
        const a = new Audio();
        a.preload = 'metadata';
        a.src = url;
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
    preparedMeta = null;
    try {
      let langLevel = settingLanguageLevel ? settingLanguageLevel : null;
      if (settingLanguageLevel === 'sourcefile') {
        langLevel = sourcefileLevel || null;
      }
      const body = {
        lemmas: visibleLemmas.map((l) => l.lemma).slice(0, 20),
        num_sentences: settingNumSentences,
        language_level: langLevel,
      };
      // Create a controller to allow cancellation
      prepareAbortCtrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
      const js = await apiFetch({
        supabaseClient: ($page.data as any).supabase ?? null,
        routeName: RouteName.LEARN_API_LEARN_SOURCEFILE_GENERATE_API,
        params: { target_language_code, sourcedir_slug, sourcefile_slug },
        options: {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
          ...(prepareAbortCtrl ? { signal: prepareAbortCtrl.signal as any } : {}),
        },
        timeoutMs: 120000,
      });
      preparedCards = js?.sentences || [];
      preparedMeta = js?.meta || null;
      if (preparedMeta?.durations) {
        console.log('Learn generate durations (prepared)', preparedMeta.durations);
      }
      // Preload audio data URLs
      preloadAudioDataUrls(preparedCards.map((c: any) => c.audio_data_url).filter(Boolean));
    } catch (e: any) {
      if (e?.name === 'AbortError') {
        preparedError = 'Preparation cancelled';
      } else {
        preparedError = e?.message || 'Failed to prepare practice set';
      }
    } finally {
      preparing = false;
      prepareAbortCtrl = null;
    }
  }

  function startOrShowPractice() {
    if (preparedCards.length > 0 && !preparing) {
      const keepOrder = typeof preparedMeta?.new_count === 'number' ? preparedMeta.new_count > 0 : false;
      cards = keepOrder ? preparedCards : shuffleArray(preparedCards);
      currentIndex = 0;
      currentStage = 1;
      resetMetricsForNewDeck(cards);
      markCardStartedIfNeeded();
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
    window.addEventListener('beforeunload', saveSessionAnalyticsToLocalStorage);
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
      preparedMeta = null;
      preparedError = null;
      if (!generating) {
        preparePracticeInBackground();
      }
    } catch (e: any) {
      alert(e?.message || 'Failed to ignore lemma');
    }
  }

  function resetMetricsForNewDeck(deck: typeof cards) {
    cardMetrics = deck.map(() => ({ replayCount: 0, startedAt: null, revealSentenceAt: null, revealTranslationAt: null }));
    sessionSaved = false;
  }

  function markCardStartedIfNeeded() {
    try {
      if (cards.length && cardMetrics[currentIndex] && cardMetrics[currentIndex].startedAt == null) {
        cardMetrics[currentIndex].startedAt = Date.now();
        cardMetrics = [...cardMetrics];
      }
    } catch {}
  }

  // Derived analytics for current session
  function computeAnalytics() {
    const seenCount = Math.min(cards.length, currentIndex + 1);
    let totalReplays = 0;
    const difficulties: number[] = [];
    const lemmaFreq: Record<string, number> = {};
    const cefrCounts: Record<string, number> = {};
    for (let i = 0; i < cards.length; i++) {
      const m = cardMetrics[i];
      if (!m) continue;
      if (i < seenCount) totalReplays += (m.replayCount || 0);
      const start = m.startedAt ?? 0;
      const end = m.revealTranslationAt ?? (i < currentIndex ? Date.now() : 0);
      const timeToTranslationMs = start && end ? Math.max(0, end - start) : 0;
      const diffScore = (m.replayCount || 0) + (timeToTranslationMs / 2000);
      difficulties.push(diffScore);
      const used = cards[i]?.used_lemmas || [];
      for (const u of used) { if (!u) continue; lemmaFreq[u] = (lemmaFreq[u] || 0) + 1; }
      const lvl = (cards[i]?.language_level || '').toUpperCase();
      if (lvl) cefrCounts[lvl] = (cefrCounts[lvl] || 0) + 1;
    }
    const avgReplays = seenCount ? (totalReplays / seenCount) : 0;
    const uniqueLemmasCovered = Object.keys(lemmaFreq).length;
    const hardestIndices = [...Array(cards.length).keys()].sort((a, b) => {
      const ma = cardMetrics[a];
      const mb = cardMetrics[b];
      const sa = (ma?.replayCount || 0) + (((ma?.revealTranslationAt ?? 0) - (ma?.startedAt ?? 0)) / 2000);
      const sb = (mb?.replayCount || 0) + (((mb?.revealTranslationAt ?? 0) - (mb?.startedAt ?? 0)) / 2000);
      return sb - sa;
    }).slice(0, 3);
    return { seenCount, avgReplays, lemmaFreq, uniqueLemmasCovered, cefrCounts, hardestIndices };
  }

  function continuePracticeFromAnalytics() {
    const scored = cards.map((c, i) => {
      const m = cardMetrics[i];
      const tt = (m?.revealTranslationAt ?? 0) - (m?.startedAt ?? 0);
      const score = (m?.replayCount || 0) + (Math.max(0, tt) / 2000);
      return { i, score };
    }).sort((a, b) => b.score - a.score);
    const next = scored.slice(0, Math.min(settingNumSentences, scored.length)).map((s) => cards[s.i]);
    if (next.length) {
      cards = next;
      currentIndex = 0;
      currentStage = 1;
      resetMetricsForNewDeck(cards);
      markCardStartedIfNeeded();
    }
  }

  function saveSessionAnalyticsToLocalStorage() {
    if (!cards.length || sessionSaved === true) return;
    const analytics = computeAnalytics();
    const entry = {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug,
      ts: Date.now(),
      total_cards: cards.length,
      seen_cards: analytics.seenCount,
      avg_replays: analytics.avgReplays,
      cefr_counts: analytics.cefrCounts,
      unique_lemmas_covered: analytics.uniqueLemmasCovered,
    };
    try {
      const key = 'hz_learn_sessions';
      const prev = JSON.parse(localStorage.getItem(key) || '[]');
      prev.unshift(entry);
      while (prev.length > 50) prev.pop();
      localStorage.setItem(key, JSON.stringify(prev));
      sessionSaved = true;
    } catch {}
  }

  function applySettings() {
    // Invalidate prepared deck and refetch summary
    cancelPreparation();
    preparedCards = [];
    preparedMeta = null;
    preparedError = null;
    fetchSummary();
  }

  function cancelPreparation() {
    try {
      if (prepareAbortCtrl) {
        prepareAbortCtrl.abort();
      }
    } catch {}
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
        <span class="me-2">Preparing deck…</span><LoadingSpinner />
      {:else if preparedCards.length}
        Practice ready ({preparedCards.length} cards)
      {:else if preparedError}
        <span class="text-danger">{preparedError}</span>
      {/if}
      <!-- Chip-style summary -->
      {#if preparedCards.length}
        <span class="badge bg-secondary me-2">Ready: {preparedCards.length}</span>
      {/if}
    </div>
    <div class="d-flex align-items-center gap-2">
      <button class="btn btn-outline-light py-2" on:click={() => showOptions = !showOptions} aria-expanded={showOptions} aria-controls="learn-options">
        {showOptions ? 'Hide options' : 'Options'}
      </button>
      {#if cards.length === 0}
        <button class="btn btn-primary py-2" on:click={startPracticeAndNavigate} disabled={generating || preparing || !lemmas.length}>
          {preparing ? 'Preparing…' : 'Start practice'}
        </button>
      {/if}
      <button class="btn btn-outline-secondary py-2" on:click={() => showWordsPanel = !showWordsPanel}>
        {showWordsPanel ? 'Hide priority words' : 'Show priority words'}
      </button>
      {#if preparing}
        <button class="btn btn-outline-light py-2" on:click={cancelPreparation}>Cancel</button>
      {/if}
    </div>
  </div>

  {#if showOptions}
  <div id="learn-options" class="mb-3">
    <div class="card card-body py-3">
      <div class="text-muted small mb-2">Tune your session. You can change these anytime.</div>
      <div class="d-flex align-items-center gap-2 flex-wrap">
        <div class="input-group input-group-sm" style="width: 140px;">
          <span class="input-group-text" title="How many top-priority words to consider from the sourcefile.">Top words</span>
          <input class="form-control" type="number" min="5" max="100" bind:value={settingTopK} title="Higher = consider more words when generating practice." />
        </div>
        <div class="input-group input-group-sm" style="width: 150px;">
          <span class="input-group-text" title="How many flashcards to generate for this session.">Cards</span>
          <input class="form-control" type="number" min="1" max="20" bind:value={settingNumSentences} title="Number of sentence cards to include in the deck." />
        </div>
        <div class="input-group input-group-sm" style="width: 220px;">
          <span class="input-group-text" title="Target difficulty level (Common European Framework). 'Any' does not force a level; 'Sourcefile' uses this file's level if known.">CEFR</span>
          <select class="form-select" bind:value={settingLanguageLevel} title={`Any = no fixed CEFR. Sourcefile = use ${sourcefileLevel || 'file level if known'}; if unknown, behaves like Any.`}>
            <option value="">Any (no constraint)</option>
            <option value="sourcefile">Sourcefile{sourcefileLevel ? ` (${sourcefileLevel})` : ''}</option>
            <option value="A1">A1</option>
            <option value="A2">A2</option>
            <option value="B1">B1</option>
            <option value="B2">B2</option>
            <option value="C1">C1</option>
            <option value="C2">C2</option>
          </select>
        </div>
        <button type="button" class="btn btn-sm btn-outline-secondary" on:click={applySettings} disabled={loadingSummary} title="Apply settings now. If preparation is running, it will be cancelled and restarted.">Apply</button>
      </div>
      {#if summaryMeta?.durations || preparedMeta?.durations}
        <div class="small text-muted mt-2">
          <span class="me-2">Diagnostics:</span>
          {#if summaryMeta?.durations}
            <span class="badge bg-secondary me-2">Summary: {summaryMeta?.durations?.total_s?.toFixed?.(1) || ''}s</span>
            {#if summaryMeta?.durations?.lemma_warmup_total_s}
              <span class="badge bg-secondary me-2">Warm: {summaryMeta.durations.lemma_warmup_total_s.toFixed(1)}s</span>
            {/if}
          {/if}
          {#if preparedMeta?.durations}
            <span class="badge bg-secondary me-2">Gen: {preparedMeta.durations.total_s?.toFixed?.(1) || ''}s</span>
          {/if}
        </div>
      {/if}
    </div>
  </div>
  {/if}

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
          <!-- Compact list of priority words with translations (collapsible) -->
          <div class="d-flex align-items-center justify-content-between mb-2">
            <div class="small text-muted">Word list</div>
            <button type="button" class="btn btn-sm btn-outline-secondary" on:click={() => showWordChips = !showWordChips}>
              {showWordChips ? 'Hide list' : 'Show list'}
            </button>
          </div>
          {#if showWordChips}
            <div class="top-lemma-list mb-3">
              {#each visibleLemmas as l, i}
                <button
                  type="button"
                  class="btn btn-sm btn-secondary text-on-light me-2 mb-2 {currentLemmaIndex === i ? 'active' : ''}"
                  title={(l.translations && l.translations.length) ? l.translations.join(', ') : ''}
                  on:click={() => goToLemma(i)}
                >
                  <span class="hz-foreign-text">{l.lemma}</span>
                  {#if l.translations && l.translations.length}
                    <span class="ms-1">{l.translations[0]}</span>
                  {/if}
                </button>
              {/each}
            </div>
          {/if}

          <!-- One-at-a-time lemma viewer with nav buttons -->
          <div class="d-flex align-items-center justify-content-between mb-2">
            <button type="button" class="btn btn-outline-secondary" on:click={prevLemma} disabled={currentLemmaIndex <= 0} aria-label="Previous word">
              <CaretLeft size={18} weight="bold" />
            </button>
            <div class="small text-muted">Word {visibleLemmas.length ? currentLemmaIndex + 1 : 0} of {visibleLemmas.length}</div>
            <button type="button" class="btn btn-outline-secondary" on:click={nextLemma} disabled={currentLemmaIndex >= visibleLemmas.length - 1} aria-label="Next word">
              <CaretRight size={18} weight="bold" />
            </button>
          </div>

          {#if visibleLemmas.length}
            <div id="learn-lemma-section" bind:this={lemmaSectionEl}></div>
            <div class="priority-words one-at-a-time">
              <div class="small text-muted mb-2">
                <button class="btn btn-sm btn-link p-0" on:click={() => showWordsHelp = !showWordsHelp}>{showWordsHelp ? 'Hide' : 'What am I seeing?'}</button>
                {#if showWordsHelp}
                  <div>These are words likely to be tricky in this text. Ignore any you already know.</div>
                {/if}
              </div>
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
              <div class="col-12 d-flex justify-content-end">
                <button class="btn btn-sm btn-link text-decoration-none" on:click={() => showKbHelp = !showKbHelp} aria-expanded={showKbHelp}>Keyboard help</button>
              </div>
              {#if showKbHelp}
                <div class="col-12 small text-muted">
                  Shortcuts: Left = replay/previous stage, Right = next stage, Enter = next card.
                </div>
              {/if}
              <div class="col-12 mt-2">
                <button id="next-card-btn" class="btn btn-primary w-100 py-3" on:click={() => { if (currentIndex < cards.length - 1) { currentIndex += 1; currentStage = 1; } }} disabled={currentIndex >= cards.length - 1}>
                  Next card (Enter)
                </button>
              </div>
              {#if currentIndex >= cards.length - 1}
                <div class="col-12 mt-2">
                  <button class="btn btn-outline-primary w-100 py-3" on:click={() => { saveSessionAnalyticsToLocalStorage(); continuePracticeFromAnalytics(); }} disabled={cards.length === 0}>
                    Continue practice (prioritize hard items)
                  </button>
                </div>
              {/if}
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

  {#if cards.length > 0 && currentIndex >= cards.length - 1}
  <div class="row mt-3">
    <div class="col-12 col-xl-7 offset-xl-5">
      <Card title="Session stats">
        {#if cards.length}
          {#key currentIndex}
          {#await Promise.resolve(computeAnalytics()) then a}
            <div class="row g-2 small">
              <div class="col-6">Seen: {a.seenCount}/{cards.length}</div>
              <div class="col-6">Avg replays/card: {a.avgReplays.toFixed(2)}</div>
              <div class="col-6">Unique lemmas covered: {a.uniqueLemmasCovered}</div>
              <div class="col-6">
                CEFR: {#each Object.entries(a.cefrCounts) as kv, idx}
                  <span class="badge bg-secondary me-1">{kv[0]} {kv[1]}</span>
                {/each}
              </div>
            </div>
          {/await}
          {/key}
        {/if}
      </Card>
    </div>
  </div>
  {/if}
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


