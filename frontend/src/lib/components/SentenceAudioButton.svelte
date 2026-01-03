<script lang="ts">
  import { onDestroy } from 'svelte';
  import SpeakerHigh from 'phosphor-svelte/lib/SpeakerHigh';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { apiFetch, getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import type { SupabaseClient } from '@supabase/supabase-js';
  import { SENTENCE_AUDIO_SAMPLES } from '$lib/config';
  import { shuffle, playAudioSequence, type PlaybackHandle } from '$lib/audioSequence';

  export let target_language_code: string;
  export let sentenceId: string | number | undefined = undefined;
  export let sentenceSlug: string;
  export let hasAudio: boolean | undefined = undefined;
  export let supabaseClient: SupabaseClient | null = null;
  export let className: string = '';
  export let iconSize: number = 18;

  let isGeneratingAudio = false;
  let isPlayingAudio = false;
  let progressCount = 0;
  let variantCountDisplay = SENTENCE_AUDIO_SAMPLES;
  let resolvedSentenceId: string | null = null;
  let playbackHandle: PlaybackHandle | null = null;
  let errorMessage: string | null = null;

  onDestroy(() => {
    playbackHandle?.cancel();
  });

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

  async function ensureVariants(slug: string): Promise<{ success: boolean; isAuthError: boolean }> {
    if (!supabaseClient) {
      return { success: false, isAuthError: true };
    }
    try {
      await apiFetch({
        supabaseClient,
        routeName: RouteName.SENTENCE_API_ENSURE_SENTENCE_AUDIO_API,
        params: { target_language_code, slug },
        options: { method: 'POST' },
        searchParams: { n: SENTENCE_AUDIO_SAMPLES },
        timeoutMs: 90000, // 90s for audio generation
      });
      return { success: true, isAuthError: false };
    } catch (e: any) {
      const isAuthError = e?.status === 401;
      console.warn('SentenceAudioButton: failed to ensure audio', isAuthError ? '(auth required)' : '', e);
      return { success: false, isAuthError };
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

  async function handleClick() {
    if (!target_language_code || !sentenceSlug) return;
    errorMessage = null;
    isGeneratingAudio = true;
    progressCount = 0;
    
    try {
      const info = await ensureSentenceInfo();
      if (!info) {
        errorMessage = 'Failed to load audio.';
        isGeneratingAudio = false;
        return;
      }

      const { id, has_audio } = info;

      let variants = await apiFetch({
        supabaseClient: null,
        routeName: RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_VARIANTS_API,
        params: { target_language_code, sentence_id: id },
        options: { method: 'GET' },
      });

      if ((!Array.isArray(variants) || variants.length < SENTENCE_AUDIO_SAMPLES) && !has_audio) {
        const { success, isAuthError } = await ensureVariants(sentenceSlug);
        if (success) {
          // Refetch variants after successful generation
          variants = await apiFetch({
            supabaseClient: null,
            routeName: RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_VARIANTS_API,
            params: { target_language_code, sentence_id: id },
            options: { method: 'GET' },
          });
        } else if (!Array.isArray(variants) || variants.length === 0) {
          // Only error if we have no variants to play at all
          errorMessage = isAuthError ? 'Login required to generate audio.' : 'Failed to generate audio.';
          isGeneratingAudio = false;
          return;
        }
        // Otherwise proceed with existing variants (best-effort, don't block playback)
      }

      const variantList = Array.isArray(variants) ? variants : [];
      if (!variantList.length) {
        console.warn('SentenceAudioButton: no audio variants available');
        errorMessage = 'No audio available.';
        isGeneratingAudio = false;
        return;
      }

      const urls = buildVariantUrls(id, variantList);
      variantCountDisplay = Math.min(urls.length, SENTENCE_AUDIO_SAMPLES);
      const toPlay = urls.length >= SENTENCE_AUDIO_SAMPLES ? shuffle(urls) : urls;
      
      isGeneratingAudio = false;
      isPlayingAudio = true;
      
      playbackHandle = playAudioSequence(toPlay, {
        onProgress: (current, total) => {
          progressCount = current;
        },
        onComplete: () => {
          isPlayingAudio = false;
          playbackHandle = null;
        },
        onCancel: () => {
          isPlayingAudio = false;
          playbackHandle = null;
        },
      });
    } catch (e) {
      console.warn('SentenceAudioButton error:', e);
      errorMessage = 'Failed to load audio.';
      isGeneratingAudio = false;
    }
  }
</script>

<button
  class="btn btn-outline-light btn-sm d-inline-flex align-items-center {className}"
  on:click|preventDefault|stopPropagation={handleClick}
  disabled={isGeneratingAudio || isPlayingAudio}
  aria-label="Play sentence"
  title={errorMessage || "Play sentence"}
>
  {#if isGeneratingAudio}
    <LoadingSpinner size="sm" />
  {/if}
  <SpeakerHigh size={iconSize} />
  {#if isGeneratingAudio || isPlayingAudio}
    <span class="badge bg-success ms-2">{progressCount}/{variantCountDisplay}</span>
  {/if}
</button>
{#if errorMessage}
  <span class="text-warning small ms-2" role="alert">{errorMessage}</span>
{/if}

<style>
  .btn:disabled {
    opacity: 0.7;
  }
</style>
