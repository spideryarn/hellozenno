<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { page } from '$app/stores';
  import Card from '$lib/components/Card.svelte';
  import Alert from '$lib/components/Alert.svelte';
  import { AudioPlayer } from '$lib';
  import { API_BASE_URL, LEARN_DEFAULT_TOP_WORDS, LEARN_DEFAULT_NUM_CARDS, LEARN_DEFAULT_CEFR, SITE_NAME } from '$lib/config';
  import { apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import LemmaContent from '$lib/components/LemmaContent.svelte';
  import CaretLeft from 'phosphor-svelte/lib/CaretLeft';
  import CaretRight from 'phosphor-svelte/lib/CaretRight';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { truncate } from '$lib/utils';
  // Use dynamic import for p-queue to avoid build-time type resolution issues

  // Parallelism settings - tuned for DB pool pressure
  // Keep generous lookahead so spending time on a card allows buffering ahead
  // But use concurrency=1 to avoid overwhelming the connection pool
  const AUDIO_PREFETCH_LOOKAHEAD = 3;  // Current + next N cards (buffer ahead)
  const LEMMA_WARM_INITIAL = 5;        // Initial lemmas to warm on load
  const LEMMA_WARM_LOOKAHEAD = 3;      // Lemmas to warm on navigation
  const WARMING_QUEUE_CONCURRENCY = 1; // Max concurrent backend requests (KEY SETTING)

  // No exported props required for this page in MVP

  let loadingSummary = true;
  let summaryError: string | null = null;
  let lemmas: Array<any> = [];
  let ignoredLemmas: Set<string> = new Set();
  let sourcefileWordforms: Record<string, string[]> = {};
  let sourceText: string = '';
  let sourcefileLevel: string | null = null;
  let sourcefileFilename: string = '';

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
    audio_data_url: string | null;  // null when audio not yet loaded
    audio_status?: 'pending' | 'loading' | 'ready' | 'error';
    sentence_id?: number;  // Needed for ensure-audio calls
  }> = [];

  let currentIndex = 0;
  let currentStage = 1; // 1: audio; 2: sentence; 3: translation
  let audioPlayer: any;

  // Highlight segments for the current sentence (computed when card changes)
  type HighlightSegment = { text: string; isHighlight: boolean };
  let currentSentenceSegments: HighlightSegment[] = [];

  // Compute highlight segments for a sentence given target lemmas and their wordforms
  // Uses Unicode-aware boundary detection with manual validation (since \b doesn't work for Greek/Cyrillic)
  function computeHighlightSegments(
    sentence: string,
    usedLemmas: string[],
    wordformsMap: Record<string, string[]>
  ): HighlightSegment[] {
    if (!sentence || !usedLemmas?.length) {
      return [{ text: sentence || '', isHighlight: false }];
    }

    // Expand lemmas with their known wordforms for better matching
    const allTerms = new Set<string>();
    for (const lemma of usedLemmas) {
      const trimmed = lemma?.trim();
      if (trimmed) allTerms.add(trimmed);
      const forms = wordformsMap[lemma] || [];
      for (const form of forms) {
        const trimmedForm = form?.trim();
        if (trimmedForm) allTerms.add(trimmedForm);
      }
    }

    if (allTerms.size === 0) {
      return [{ text: sentence, isHighlight: false }];
    }

    // Sort by length descending to match longer terms first (avoid partial matches)
    const sortedTerms = Array.from(allTerms).sort((a, b) => b.length - a.length);

    // Escape regex special characters and build alternation pattern
    const escaped = sortedTerms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const pattern = new RegExp(`(${escaped.join('|')})`, 'giu');

    // Unicode word character check: letters + combining marks (for proper boundary detection)
    const isWordChar = (char: string): boolean => /[\p{L}\p{M}]/u.test(char);

    const segments: HighlightSegment[] = [];
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = pattern.exec(sentence)) !== null) {
      const matchStart = match.index;
      const matchEnd = matchStart + match[0].length;
      const matchedText = match[0];

      // Get adjacent characters
      const charBefore = matchStart > 0 ? sentence[matchStart - 1] : '';
      const charAfter = matchEnd < sentence.length ? sentence[matchEnd] : '';
      const firstMatchChar = matchedText[0] || '';
      const lastMatchChar = matchedText[matchedText.length - 1] || '';

      // Boundary logic: require boundary only if both sides are word characters
      // This handles elision (τ'αγάπη) where the term ends with non-letter
      const needsBoundaryBefore = isWordChar(firstMatchChar);
      const needsBoundaryAfter = isWordChar(lastMatchChar);

      const isValidBefore = !needsBoundaryBefore || !charBefore || !isWordChar(charBefore);
      const isValidAfter = !needsBoundaryAfter || !charAfter || !isWordChar(charAfter);

      if (isValidBefore && isValidAfter) {
        // Add non-matching text before this match
        if (matchStart > lastIndex) {
          segments.push({ text: sentence.slice(lastIndex, matchStart), isHighlight: false });
        }
        // Add the matching text
        segments.push({ text: matchedText, isHighlight: true });
        lastIndex = matchEnd;
      }
    }

    // Add remaining text after last match
    if (lastIndex < sentence.length) {
      segments.push({ text: sentence.slice(lastIndex), isHighlight: false });
    }

    return segments.length > 0 ? segments : [{ text: sentence, isHighlight: false }];
  }

  // Reactively compute segments when card changes
  $: {
    const card = cards[currentIndex];
    if (card) {
      currentSentenceSegments = computeHighlightSegments(
        card.sentence,
        card.used_lemmas,
        sourcefileWordforms
      );
    } else {
      currentSentenceSegments = [];
    }
  }

  // Audio prefetch tracking
  // We use a Map to track request state per sentence_id, keyed by the sentence_id
  // This allows retry after errors and proper deck reset handling
  let audioRequestState = new Map<number, 'pending' | 'loading' | 'done' | 'error'>();
  // Track which sentence_id is currently loading for the current card (for spinner)
  let audioLoadingForSentenceId: number | null = null;

  // Background preparation of practice deck
  let preparing = false;
  let preparedCards: typeof cards = [];
  let preparedMeta: any = null;
  let preparedError: string | null = null;
  let preloadedAudios: HTMLAudioElement[] = [];
  let loadingLemmaMap: Record<string, boolean> = {};
  let warmingQueue: any = null;
  let prepareAbortCtrl: AbortController | null = null;
  let summaryAbortCtrl: AbortController | null = null;
  let summaryRequestId = 0;
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

  // Build absolute API URL for audio when backend returns a relative path
  function toAbsoluteApiUrl(path: string | null | undefined): string {
    if (!path) return '';
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    // Ensure we prefix with API_BASE_URL for production (different domain)
    return `${API_BASE_URL}${path}`;
  }

  // Reactive current audio src for the active card, always absolute
  $: currentAudioSrc = toAbsoluteApiUrl(cards?.[currentIndex]?.audio_data_url);
  $: hasAudioForCurrentCard = !!cards?.[currentIndex]?.audio_data_url;

  // Prefetch audio for current and next cards when practice starts or card changes
  // Uses AUDIO_PREFETCH_LOOKAHEAD constant for generous buffering with concurrency=1
  $: if (cards.length > 0 && currentIndex >= 0) {
    // Generate indices for current + next N cards
    const indicesToPrefetch = Array.from(
      {length: AUDIO_PREFETCH_LOOKAHEAD + 1}, 
      (_, i) => currentIndex + i
    ).filter(i => i < cards.length && cards[i]?.sentence_id);

    for (const idx of indicesToPrefetch) {
      const sentenceId = cards[idx].sentence_id!;
      const state = audioRequestState.get(sentenceId);
      // Skip loading/done/error states - errors are only retried via manual button
      // This prevents infinite retry loops when server persistently fails
      if (state === 'loading' || state === 'done' || state === 'error') continue;
      // Skip if already has audio
      if (cards[idx].audio_data_url && cards[idx].audio_status === 'ready') continue;
      
      audioRequestState.set(sentenceId, 'loading');
      if (idx === currentIndex) {
        // Current card - blocking (show loading spinner)
        audioLoadingForSentenceId = sentenceId;
        prefetchAudioForCard(idx, sentenceId).finally(() => {
          // Only clear if we're still waiting for this specific sentence
          if (audioLoadingForSentenceId === sentenceId) {
            audioLoadingForSentenceId = null;
          }
        });
      } else {
        // Future cards - queue in background with error handling
        ensureWarmingQueue().then((queue) => {
          if (queue) {
            queue.add(() => prefetchAudioForCard(idx, sentenceId), { priority: 0 });
          } else {
            // Queue init failed - revert state to allow retry later
            audioRequestState.set(sentenceId, 'pending');
          }
        }).catch(() => {
          audioRequestState.set(sentenceId, 'pending');
        });
      }
    }
  }
  
  // Check if current card's audio is loading (for UI spinner)
  $: isCurrentCardAudioLoading = audioLoadingForSentenceId !== null && 
    cards[currentIndex]?.sentence_id === audioLoadingForSentenceId;

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

  // Fetch audio for a specific card on-demand
  // originalSentenceId is passed to validate the card hasn't changed during fetch
  async function prefetchAudioForCard(cardIndex: number, originalSentenceId: number): Promise<void> {
    // Helper to safely update card if it still matches
    function updateCardIfValid(updates: Partial<typeof cards[0]>) {
      if (cardIndex < cards.length && cards[cardIndex]?.sentence_id === originalSentenceId) {
        Object.assign(cards[cardIndex], updates);
        cards = [...cards];
      }
    }

    const card = cards[cardIndex];
    if (!card?.sentence_id || card.sentence_id !== originalSentenceId) return;
    if (card.audio_data_url && card.audio_status === 'ready') {
      audioRequestState.set(originalSentenceId, 'done');
      return;
    }

    // Mark as loading
    updateCardIfValid({ audio_status: 'loading' });

    try {
      // Note: Page requires auth (server-side redirect), so supabase is always available
      const supabase = ($page.data as any).supabase;
      
      // Construct URL manually since route may not be generated yet
      const url = `${API_BASE_URL}/api/lang/learn/sentence/${originalSentenceId}/ensure-audio`;
      
      // Get token via session (apiFetch handles refresh, but we need raw fetch for abort)
      const sessionData = await supabase.auth.getSession();
      const token = sessionData?.data?.session?.access_token;
      
      if (!token) {
        // This shouldn't happen with server-side auth gate, but handle gracefully
        console.warn('Audio prefetch: unexpected missing session token');
        audioRequestState.set(originalSentenceId, 'error');
        updateCardIfValid({ audio_status: card.audio_data_url ? 'ready' : 'error' });
        return;
      }
      
      // Use AbortController for timeout (15s)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000);
      
      let response: Response;
      try {
        response = await fetch(url, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          signal: controller.signal,
        });
      } finally {
        clearTimeout(timeoutId);
      }

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        console.warn('Audio prefetch failed:', response.status, errData);
        audioRequestState.set(originalSentenceId, 'error');
        updateCardIfValid({ audio_status: 'error' });
        return;
      }

      const result = await response.json();
      audioRequestState.set(originalSentenceId, 'done');
      updateCardIfValid({ audio_data_url: result.audio_data_url, audio_status: 'ready' });
    } catch (e: any) {
      if (e?.name === 'AbortError') {
        console.warn('Audio prefetch timed out for sentence:', originalSentenceId);
      } else {
        console.warn('Audio prefetch failed:', e);
      }
      audioRequestState.set(originalSentenceId, 'error');
      updateCardIfValid({ audio_status: 'error' });
    }
  }

  async function ensureWarmingQueue() {
    if (warmingQueue) return warmingQueue;
    try {
      const mod = await import('p-queue');
      const PQueue = (mod as any).default ?? (mod as any);
      warmingQueue = new PQueue({ concurrency: WARMING_QUEUE_CONCURRENCY });
    } catch (e) {
      // Fallback minimal queue with concurrency 1 (matches WARMING_QUEUE_CONCURRENCY)
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
  let language_name: string = '';
  $: language_name = ($page.data as any)?.language_name || target_language_code;

  async function fetchSummary() {
    // Abort any in-flight request and track this request's ID
    if (summaryAbortCtrl) {
      summaryAbortCtrl.abort();
    }
    summaryAbortCtrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
    const thisRequestId = ++summaryRequestId;

    loadingSummary = true;
    summaryError = null;
    try {
      // Authenticated request so backend can generate lemma metadata on-demand
      const js = await apiFetch({
        supabaseClient: ($page.data as any).supabase ?? null,
        routeName: RouteName.LEARN_API_LEARN_SOURCEFILE_SUMMARY_API,
        params: { target_language_code, sourcedir_slug, sourcefile_slug },
        options: {
          method: 'GET',
          ...(summaryAbortCtrl ? { signal: summaryAbortCtrl.signal as any } : {}),
        },
        searchParams: { top: settingTopK },
        timeoutMs: 60000,
      });

      // Only apply state if this is still the latest request
      if (thisRequestId !== summaryRequestId) return;

      lemmas = js?.lemmas || [];
      summaryMeta = js?.meta || null;
      if (summaryMeta?.durations) {
        console.log('Learn summary durations', summaryMeta.durations);
      }

      // Also fetch the original source text for context sentence extraction
      const textRes = await fetch(
        `${API_BASE_URL}/api/lang/sourcefile/${encodeURIComponent(target_language_code)}/${encodeURIComponent(sourcedir_slug)}/${encodeURIComponent(sourcefile_slug)}/text`,
        summaryAbortCtrl ? { signal: summaryAbortCtrl.signal } : {}
      );
      if (thisRequestId !== summaryRequestId) return;
      if (textRes.ok) {
        const td = await textRes.json();
        sourceText = td?.sourcefile?.text_target || td?.text_data?.text_target || '';
        sourcefileLevel = (td?.sourcefile?.language_level || '').toUpperCase() || null;
        sourcefileFilename = td?.sourcefile?.filename || sourcefile_slug;
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
        if (thisRequestId !== summaryRequestId) return;
        if (Array.isArray(ignored)) {
          ignoredLemmas = new Set(ignored.map((x: any) => x.lemma));
        }
      } catch (e) {
        // not logged in or API error; proceed without filtering
      }
    } catch (e: any) {
      if (e?.name === 'AbortError') return; // Request was cancelled, don't update state
      if (thisRequestId !== summaryRequestId) return;
      summaryError = e?.message || 'Failed to load summary';
    } finally {
      if (thisRequestId === summaryRequestId) {
        loadingSummary = false;
      }
    }
    // Kick off background preparation once summary is available
    if (!summaryError && lemmas.length > 0) {
      await ensureWarmingQueue();
      // Warm currently visible lemma and a small lookahead in background
      warmTopLemmasInBackground(visibleLemmas.slice(0, LEMMA_WARM_INITIAL).map((l) => l.lemma));
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
        skip_audio: true,  // Audio loaded on-demand via prefetch
      };
      // Note: Page requires auth (server-side redirect), so 401 errors won't occur here
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
  
  // Retry audio for current card (called via manual retry button)
  function retryCurrentCardAudio() {
    const card = cards[currentIndex];
    if (!card?.sentence_id) return;
    // Reset state to 'pending' to allow the reactive prefetch to pick it up
    audioRequestState.set(card.sentence_id, 'pending');
    cards[currentIndex].audio_status = 'pending';
    cards = [...cards];  // Trigger reactive update
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

  function clearPreloadedAudios() {
    // Release references to preloaded audio elements to avoid memory leaks
    for (const a of preloadedAudios) {
      try {
        a.src = '';
        a.load();
      } catch {}
    }
    preloadedAudios = [];
  }

  function preloadAudioDataUrls(urls: string[]) {
    try {
      // Clear old preloads before adding new ones to cap memory usage
      if (preloadedAudios.length > 10) {
        clearPreloadedAudios();
      }
      // Limit concurrent preloads to reduce DB pressure
      const limited = urls.slice(0, 2);
      for (const url of limited) {
        const a = new Audio();
        a.preload = 'metadata';
        a.src = toAbsoluteApiUrl(url);
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
        skip_audio: true,  // Audio loaded on-demand via prefetch
      };
      // Create a controller to allow cancellation
      prepareAbortCtrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
      // Note: Page requires auth (server-side redirect), so 401 errors won't occur here
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
    const lookahead = LEMMA_WARM_LOOKAHEAD;
    const toWarm: string[] = [];
    for (let i = 0; i < lookahead && currentLemmaIndex + i < visibleLemmas.length; i++) {
      const lm = visibleLemmas[currentLemmaIndex + i]?.lemma;
      if (lm) toWarm.push(lm);
    }
    warmTopLemmasInBackground(toWarm);
  }

  // For complete keyboard shortcuts reference, see frontend/docs/KEYBOARD_SHORTCUTS.md
  function handleKeyDown(event: KeyboardEvent) {
    // Check if user is in an editable element (shared across all modes)
    const active = (document.activeElement as HTMLElement | null);
    const tag = active?.tagName?.toLowerCase();
    const isEditable = active?.isContentEditable || tag === 'input' || tag === 'textarea' || tag === 'select';
    if (isEditable) return;

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
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('beforeunload', saveSessionAnalyticsToLocalStorage);
      summaryAbortCtrl?.abort();
      prepareAbortCtrl?.abort();
      clearPreloadedAudios();
    };
  });

  function snippetAroundTerm(text: string, matchStart: number, matchLength: number, before: number = 100, after: number = 100): string {
    const from = Math.max(0, matchStart - before);
    const to = Math.min(text.length, matchStart + matchLength + after);
    const prefix = from > 0 ? '…' : '';
    const suffix = to < text.length ? '…' : '';
    return `${prefix}${text.slice(from, to)}${suffix}`;
  }

  function getContextSentence(text: string, lemma: string | undefined): string | undefined {
    if (!text || !lemma) return undefined;
    const sentences = text.split(/(?<=[.!?;··])\s+/);
    for (const s of sentences) {
      const pos = s.indexOf(lemma);
      if (pos !== -1) {
        return snippetAroundTerm(s, pos, lemma.length, 100, 100);
      }
    }
    return undefined;
  }

  function getContextSentenceFull(text: string, lemma: string | undefined): string | undefined {
    if (!text || !lemma) return undefined;
    const sentences = text.split(/(?<=[.!?;··])\s+/);
    for (const s of sentences) {
      if (s.includes(lemma)) return s;
    }
    return undefined;
  }

  function getAllContextSentences(text: string, lemma: string | undefined, forms: string[]): string[] {
    if (!text) return [];
    const searchTerms = new Set<string>();
    if (lemma) searchTerms.add(lemma);
    for (const f of forms || []) if (f) searchTerms.add(f);
    const sentences = text.split(/(?<=[.!?;··])\s+/);
    const result: string[] = [];
    const terms = Array.from(searchTerms);
    for (const s of sentences) {
      let bestIdx = -1;
      let bestTerm = '';
      for (const term of terms) {
        const pos = s.indexOf(term);
        if (pos !== -1 && (bestIdx === -1 || pos < bestIdx)) {
          bestIdx = pos;
          bestTerm = term;
        }
      }
      if (bestIdx !== -1) {
        result.push(snippetAroundTerm(s, bestIdx, bestTerm.length, 100, 100));
      }
    }
    // Deduplicate while preserving order
    return Array.from(new Set(result));
  }

  function getAllContextSentencesFull(text: string, lemma: string | undefined, forms: string[]): string[] {
    if (!text) return [];
    const searchTerms = new Set<string>();
    if (lemma) searchTerms.add(lemma);
    for (const f of forms || []) if (f) searchTerms.add(f);
    const sentences = text.split(/(?<=[.!?;··])\s+/);
    const result: string[] = [];
    for (const s of sentences) {
      for (const term of searchTerms) {
        if (s.indexOf(term) !== -1) { result.push(s); break; }
      }
    }
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
    clearPreloadedAudios();
    // Clear audio request state so prefetch can run for new deck
    audioRequestState.clear();
    audioLoadingForSentenceId = null;
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
  <title>{truncate(sourcefileFilename || sourcefile_slug, 30)} | Learn | {language_name} | {SITE_NAME}</title>
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
                  context_sentence_full={getContextSentenceFull(sourceText, visibleLemmas[currentLemmaIndex]?.lemma)}
                  source_wordforms={sourcefileWordforms[visibleLemmas[currentLemmaIndex]?.lemma] || []}
                  source_sentences={getAllContextSentences(
                    sourceText,
                    visibleLemmas[currentLemmaIndex]?.lemma,
                    sourcefileWordforms[visibleLemmas[currentLemmaIndex]?.lemma] || []
                  )}
                  source_sentences_full={getAllContextSentencesFull(
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
                <button class="btn btn-secondary w-100 py-3" on:click={currentStage === 1 ? playAudio : prevStage} disabled={!hasAudioForCurrentCard && currentStage === 1} title={!hasAudioForCurrentCard && currentStage === 1 ? 'No audio available for this card' : ''}>
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
              {#if isCurrentCardAudioLoading || cards[currentIndex]?.audio_status === 'loading'}
                <div class="text-center py-3">
                  <LoadingSpinner /> <span class="ms-2">Loading audio...</span>
                </div>
              {:else if hasAudioForCurrentCard}
                <AudioPlayer bind:this={audioPlayer} src={currentAudioSrc} downloadUrl={currentAudioSrc} autoplay={true} showControls={true} showSpeedControls={true} showDownload={false} />
              {:else}
                <Alert type="warning">
                  No audio available for this card.
                  {#if cards[currentIndex]?.audio_status === 'error'}
                    <button class="btn btn-sm btn-outline-warning ms-2" on:click={retryCurrentCardAudio}>
                      Retry
                    </button>
                  {/if}
                </Alert>
              {/if}
            </div>

          {#if currentStage >= 2}
            <div class="flashcard-box sentence-box">
              <h3 class="hz-foreign-text text-center mb-0">
                {#each currentSentenceSegments as seg}
                  {#if seg.isHighlight}
                    <mark class="target-lemma">{seg.text}</mark>
                  {:else}
                    {seg.text}
                  {/if}
                {/each}
              </h3>
              {#if cards[currentIndex].used_lemmas?.length}
                <div class="text-muted small text-center mt-2">
                  Practicing: <span class="hz-foreign-text">{cards[currentIndex].used_lemmas.join(', ')}</span>
                </div>
              {/if}
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

  /* Highlight for target lemmas in practice sentences */
  .sentence-box :global(.target-lemma) {
    background-color: var(--hz-color-accent, rgba(255, 193, 7, 0.25));
    border-radius: 3px;
    padding: 0.1em 0.2em;
    color: inherit;
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


