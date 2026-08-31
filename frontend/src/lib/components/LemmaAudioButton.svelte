<script lang="ts">
  import { onDestroy } from 'svelte';
  import SpeakerHigh from 'phosphor-svelte/lib/SpeakerHigh';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { apiFetch, resolveApiPath } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import type { SupabaseClient } from '@supabase/supabase-js';
  import { LEMMA_AUDIO_SAMPLES } from '$lib/config';
  import { shuffle, playAudioSequence, type PlaybackHandle } from '$lib/audioSequence';

  export let target_language_code: string;
  export let lemma: string;
  export let supabaseClient: SupabaseClient | null = null;
  export let className: string = '';
  export let iconSize: number = 18;

  let isGeneratingAudio = false;
  let isPlayingAudio = false;
  let progressCount = 0;
  let totalToPlay = LEMMA_AUDIO_SAMPLES;
  let errorMessage: string | null = null;
  let playbackHandle: PlaybackHandle | null = null;

  onDestroy(() => {
    playbackHandle?.cancel();
  });

  type Variant = { id: number; provider: string; metadata: Record<string, any>; url: string };

  async function fetchVariants(skipCache = false): Promise<Variant[]> {
    const res = await apiFetch({
      supabaseClient: null, // public endpoint
      routeName: RouteName.LEMMA_API_GET_LEMMA_AUDIO_VARIANTS_API,
      params: { target_language_code, lemma },
      // no-store: this list is publicly cacheable, so a read straight after
      // generating would otherwise be served the pre-generation empty list.
      options: { method: 'GET', cache: skipCache ? 'no-store' : 'default' },
    });
    return Array.isArray(res) ? res : [];
  }

  async function ensureVariants(
    n: number,
  ): Promise<{ success: boolean; isAuthError: boolean; variants: Variant[] | null }> {
    try {
      const res = await apiFetch({
        supabaseClient: supabaseClient,
        routeName: RouteName.LEMMA_API_ENSURE_LEMMA_AUDIO_API,
        params: { target_language_code, lemma },
        options: { method: 'POST' },
        searchParams: { n },
        timeoutMs: 90000, // 90s for audio generation (3 samples × ~10s each)
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
      console.warn('LemmaAudioButton: failed to ensure audio', isAuthError ? '(auth required)' : '', e);
      return { success: false, isAuthError, variants: null };
    }
  }

  async function handleClick() {
    if (!lemma || !target_language_code) return;
    errorMessage = null;
    progressCount = 0;
    totalToPlay = LEMMA_AUDIO_SAMPLES;
    isGeneratingAudio = true;
    
    try {
      // 1) Get existing variants
      let variants = await fetchVariants();
      
      // 2) Ensure up to N exist if needed (best-effort, don't block playback on failure)
      const needed = LEMMA_AUDIO_SAMPLES - variants.length;
      if (needed > 0) {
        if (supabaseClient) {
          const { success, isAuthError, variants: ensured } = await ensureVariants(LEMMA_AUDIO_SAMPLES);
          if (success) {
            // Only reached against a backend too old to return the variants
            // itself; skip the cache so that fallback can't read the stale list.
            variants = ensured ?? (await fetchVariants(true));
          } else if (variants.length === 0) {
            errorMessage = isAuthError ? 'Login required to generate audio.' : 'Failed to generate audio.';
            isGeneratingAudio = false;
            return;
          }
        } else if (variants.length === 0) {
          errorMessage = 'Login required to generate audio.';
          isGeneratingAudio = false;
          return;
        }
      }
      
      // 3) Build URLs and play
      const urls = variants.slice(0, LEMMA_AUDIO_SAMPLES).map((v) => resolveApiPath(v.url));
      if (!urls.length) {
        errorMessage = 'No audio available.';
        isGeneratingAudio = false;
        return;
      }
      
      const toPlay = urls.length >= LEMMA_AUDIO_SAMPLES ? shuffle(urls) : urls;
      isGeneratingAudio = false;
      isPlayingAudio = true;
      totalToPlay = toPlay.length;
      
      let playbackFailures = 0;
      playbackHandle = playAudioSequence(toPlay, {
        onProgress: (current, total) => {
          progressCount = current;
        },
        onError: (err, index) => {
          // Without this the sequence advances silently, so a run of failed
          // loads looks identical to successful playback with no sound.
          playbackFailures += 1;
          console.warn(`LemmaAudioButton: playback failed for variant ${index}`, err);
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
      console.warn('LemmaAudioButton error:', e);
      errorMessage = 'Failed to load audio.';
      isGeneratingAudio = false;
    }
  }
</script>

<button
  class="btn btn-outline-light btn-sm d-inline-flex align-items-center {className}"
  on:click|preventDefault={handleClick}
  disabled={isGeneratingAudio || isPlayingAudio}
  aria-label="Play pronunciations"
  title={errorMessage || "Play pronunciations"}
>
  {#if isGeneratingAudio}
    <LoadingSpinner size="sm" />
  {/if}
  <SpeakerHigh size={iconSize} />
  {#if isGeneratingAudio || isPlayingAudio}
    <span class="badge bg-success ms-2">{progressCount}/{totalToPlay}</span>
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
