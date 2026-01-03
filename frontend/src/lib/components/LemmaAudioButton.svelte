<script lang="ts">
  import { onDestroy } from 'svelte';
  import SpeakerHigh from 'phosphor-svelte/lib/SpeakerHigh';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { apiFetch } from '$lib/api';
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

  async function fetchVariants(): Promise<
    { id: number; provider: string; metadata: Record<string, any>; url: string }[]
  > {
    const res = await apiFetch({
      supabaseClient: null, // public endpoint
      routeName: RouteName.LEMMA_API_GET_LEMMA_AUDIO_VARIANTS_API,
      params: { target_language_code, lemma },
      options: { method: 'GET' },
    });
    return Array.isArray(res) ? res : [];
  }

  async function ensureVariants(n: number): Promise<{ success: boolean; isAuthError: boolean }> {
    try {
      await apiFetch({
        supabaseClient: supabaseClient,
        routeName: RouteName.LEMMA_API_ENSURE_LEMMA_AUDIO_API,
        params: { target_language_code, lemma },
        options: { method: 'POST' },
        searchParams: { n },
        timeoutMs: 90000, // 90s for audio generation (3 samples × ~10s each)
      });
      return { success: true, isAuthError: false };
    } catch (e: any) {
      const isAuthError = e?.status === 401;
      console.warn('LemmaAudioButton: failed to ensure audio', isAuthError ? '(auth required)' : '', e);
      return { success: false, isAuthError };
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
          const { success, isAuthError } = await ensureVariants(LEMMA_AUDIO_SAMPLES);
          if (success) {
            variants = await fetchVariants();
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
      const urls = variants.slice(0, LEMMA_AUDIO_SAMPLES).map((v) => v.url);
      if (!urls.length) {
        errorMessage = 'No audio available.';
        isGeneratingAudio = false;
        return;
      }
      
      const toPlay = urls.length >= LEMMA_AUDIO_SAMPLES ? shuffle(urls) : urls;
      isGeneratingAudio = false;
      isPlayingAudio = true;
      totalToPlay = toPlay.length;
      
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
