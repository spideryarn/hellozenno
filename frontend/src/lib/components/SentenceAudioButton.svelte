<script lang="ts">
  import SpeakerHigh from 'phosphor-svelte/lib/SpeakerHigh';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { apiFetch, getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import type { SupabaseClient } from '@supabase/supabase-js';
  import { SENTENCE_AUDIO_SAMPLES } from '$lib/config';

  export let target_language_code: string;
  export let sentenceId: string | number | undefined = undefined;
  export let sentenceSlug: string;
  export let hasAudio: boolean | undefined = undefined;
  export let supabaseClient: SupabaseClient | null = null;
  export let className: string = '';
  export let iconSize: number = 18;

  let isGeneratingAudio = false;
  let isPlayingAudio = false;
  let progressCount = 0; // 0..n
  let variantCountDisplay = SENTENCE_AUDIO_SAMPLES;
  let resolvedSentenceId: string | null = null;
  let lastVariantUrls: string[] | null = null;

  async function ensureSentenceInfo(): Promise<{ id: string; has_audio: boolean } | null> {
    // Use provided id/hasAudio if available
    if ((sentenceId !== undefined && sentenceId !== null) && (hasAudio !== undefined && hasAudio !== null)) {
      return { id: String(sentenceId), has_audio: Boolean(hasAudio) };
    }

    // Fetch sentence by slug to obtain id and has_audio
    try {
      const data = await apiFetch({
        supabaseClient: null, // public endpoint
        routeName: RouteName.SENTENCE_API_GET_SENTENCE_BY_SLUG_API,
        params: { target_language_code, slug: sentenceSlug },
        options: { method: 'GET' },
      });
      const id = String(data?.sentence?.id ?? '');
      const has_audio = Boolean(data?.sentence?.has_audio);
      if (!id) return null;
      resolvedSentenceId = id;
      return { id, has_audio };
    } catch (e) {
      console.warn('SentenceAudioButton: failed to fetch sentence info', e);
      return null;
    }
  }

  async function ensureVariants(slug: string): Promise<boolean> {
    if (!supabaseClient) {
      alert('Login required to generate audio.');
      return false;
    }
    try {
      await apiFetch({
        supabaseClient,
        routeName: RouteName.SENTENCE_API_ENSURE_SENTENCE_AUDIO_API,
        params: { target_language_code, slug },
        options: { method: 'POST' },
        searchParams: { n: SENTENCE_AUDIO_SAMPLES },
      });
      return true;
    } catch (e) {
      console.warn('SentenceAudioButton: failed to ensure audio (auth required?)', e);
      return false;
    }
  }

  function buildVariantUrls(
    sentence_id: string,
    variants: { url: string }[],
  ): string[] {
    return variants
      .slice(0, SENTENCE_AUDIO_SAMPLES)
      .map((v) => v.url ?? getApiUrl(RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_API, {
        target_language_code,
        sentence_id,
      }));
  }

  function shuffle<T>(arr: T[]): T[] {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  async function playSequential(urls: string[]): Promise<void> {
    if (!urls.length) return;
    isPlayingAudio = true;
    progressCount = 0;
    let idx = 0;

    const audioElems = urls.map((u) => {
      const audio = new Audio(u);
      audio.preload = 'auto';
      return audio;
    });

    const playNext = () => {
      if (idx >= audioElems.length) {
        isPlayingAudio = false;
        progressCount = urls.length;
        return;
      }
      const audio = audioElems[idx];
      idx += 1;
      progressCount = idx;
      audio.onended = playNext;
      audio.onerror = playNext;
      audio.play().catch(() => playNext());
    };

    playNext();
  }

  async function handleClick() {
    if (!target_language_code || !sentenceSlug) return;
    isGeneratingAudio = true;
    try {
      const info = await ensureSentenceInfo();
      if (!info) return;

      const { id, has_audio } = info;

      let variants = await apiFetch({
        supabaseClient: null,
        routeName: RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_VARIANTS_API,
        params: { target_language_code, sentence_id: id },
        options: { method: 'GET' },
      });

      if ((!Array.isArray(variants) || variants.length < SENTENCE_AUDIO_SAMPLES) && !has_audio) {
        const ensured = await ensureVariants(sentenceSlug);
        if (!ensured) {
          return;
        }
        variants = await apiFetch({
          supabaseClient: null,
          routeName: RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_VARIANTS_API,
          params: { target_language_code, sentence_id: id },
          options: { method: 'GET' },
        });
      }

      const variantList = Array.isArray(variants) ? variants : [];
      if (!variantList.length) {
        console.warn('SentenceAudioButton: no audio variants available');
        return;
      }

      const urls = buildVariantUrls(id, variantList);
      variantCountDisplay = Math.min(urls.length, SENTENCE_AUDIO_SAMPLES);
      lastVariantUrls = urls;
      const toPlay =
        lastVariantUrls && lastVariantUrls.length === urls.length
          ? shuffle(lastVariantUrls)
          : urls;
      await playSequential(toPlay);
    } finally {
      isGeneratingAudio = false;
    }
  }
</script>

<button
  class="btn btn-outline-light btn-sm d-inline-flex align-items-center {className}"
  on:click|preventDefault|stopPropagation={handleClick}
  disabled={isGeneratingAudio || isPlayingAudio}
  aria-label="Play sentence"
  title="Play sentence"
>
  {#if isGeneratingAudio}
    <LoadingSpinner size="sm" />
  {/if}
  <SpeakerHigh size={iconSize} />
  {#if isGeneratingAudio || isPlayingAudio}
    <span class="badge bg-success ms-2">{progressCount}/{variantCountDisplay}</span>
  {/if}
</button>

<style>
  .btn:disabled {
    opacity: 0.7;
  }
</style>
