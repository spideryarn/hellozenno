<script lang="ts">
  import { onDestroy } from 'svelte';
  import SpeakerHigh from 'phosphor-svelte/lib/SpeakerHigh';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { apiFetch, getApiUrl, resolveApiPath } from '$lib/api';
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

  async function ensureVariants(
    slug: string,
  ): Promise<{ success: boolean; isAuthError: boolean; variants: { url: string }[] | null }> {
    if (!supabaseClient) {
      return { success: false, isAuthError: true, variants: null };
    }
    try {
      const res = await apiFetch({
        supabaseClient,
        routeName: RouteName.SENTENCE_API_ENSURE_SENTENCE_AUDIO_API,
        params: { target_language_code, slug },
        options: { method: 'POST' },
        searchParams: { n: SENTENCE_AUDIO_SAMPLES },
        timeoutMs: 90000, // 90s for audio generation
      });
      // The ensure response carries the full list. Re-reading the variants
      // endpoint here instead would hit a stale, publicly-cached empty list -
      // that GET is anonymous and browser-cacheable for 60s, so a read straight
      // after this write reports "no audio" for audio we just generated.
      // null (rather than []) means an older backend that doesn't send them yet.
      const variants = Array.isArray(res?.variants) ? res.variants : null;
      return { success: true, isAuthError: false, variants };
    } catch (e: any) {
      const isAuthError = e?.status === 401;
      console.warn('SentenceAudioButton: failed to ensure audio', isAuthError ? '(auth required)' : '', e);
      return { success: false, isAuthError, variants: null };
    }
  }

  function buildVariantUrls(
    sentence_id: string,
    variants: { url: string }[],
  ): string[] {
    return variants
      .slice(0, SENTENCE_AUDIO_SAMPLES)
      .map((v) => v.url ? resolveApiPath(v.url) : getApiUrl(RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_API, {
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

      const { id } = info;

      let variants = await apiFetch({
        supabaseClient: null,
        routeName: RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_VARIANTS_API,
        params: { target_language_code, sentence_id: id },
        options: { method: 'GET' },
      });

      // The variants list is the authority. has_audio only means "at least one
      // row exists", so letting it veto generation both left users staring at
      // "No audio available." when the list was empty, and stopped a
      // one-variant sentence ever reaching the full set.
      const variantsSoFar = Array.isArray(variants) ? variants.length : 0;
      if (variantsSoFar < SENTENCE_AUDIO_SAMPLES) {
        const { success, isAuthError, variants: ensured } = await ensureVariants(sentenceSlug);
        if (success) {
          // Only reached against a backend too old to return the variants
          // itself; no-store keeps that fallback off the stale cached list.
          variants = ensured ?? (await apiFetch({
            supabaseClient: null,
            routeName: RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_VARIANTS_API,
            params: { target_language_code, sentence_id: id },
            options: { method: 'GET', cache: 'no-store' },
          }));
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
      
      let playbackFailures = 0;
      playbackHandle = playAudioSequence(toPlay, {
        onProgress: (current, total) => {
          progressCount = current;
        },
        onError: (err, index) => {
          // Without this the sequence advances silently, so a run of failed
          // loads looks identical to successful playback with no sound.
          playbackFailures += 1;
          console.warn(`SentenceAudioButton: playback failed for variant ${index}`, err);
        },
        onComplete: () => {
          isPlayingAudio = false;
          playbackHandle = null;
          if (playbackFailures === toPlay.length) {
            errorMessage = 'Audio failed to play.';
          }
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
