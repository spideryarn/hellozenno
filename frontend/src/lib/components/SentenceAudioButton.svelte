<script lang="ts">
  import SpeakerHigh from 'phosphor-svelte/lib/SpeakerHigh';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { apiFetch, getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import type { SupabaseClient } from '@supabase/supabase-js';

  export let target_language_code: string;
  export let sentenceId: string | number | undefined = undefined;
  export let sentenceSlug: string;
  export let hasAudio: boolean | undefined = undefined;
  export let supabaseClient: SupabaseClient | null = null;
  export let className: string = '';
  export let iconSize: number = 18;

  let isGeneratingAudio = false;
  let isPlayingAudio = false;
  let progressCount = 0; // 0 or 1
  let resolvedSentenceId: string | null = null;
  let resolvedHasAudio: boolean | null = null;

  function buildAudioUrl(id: string | number): string {
    return getApiUrl(RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_API, {
      target_language_code,
      sentence_id: String(id),
    });
  }

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
      resolvedHasAudio = has_audio;
      return { id, has_audio };
    } catch (e) {
      console.warn('SentenceAudioButton: failed to fetch sentence info', e);
      return null;
    }
  }

  async function generateAudio(slug: string): Promise<boolean> {
    if (!supabaseClient) {
      return false;
    }
    try {
      await apiFetch({
        supabaseClient,
        routeName: RouteName.SENTENCE_API_GENERATE_SENTENCE_AUDIO_API,
        params: { target_language_code, slug },
        options: { method: 'POST' },
      });
      return true;
    } catch (e) {
      console.warn('SentenceAudioButton: failed to generate audio (auth required?)', e);
      return false;
    }
  }

  async function playAudio(url: string): Promise<void> {
    isPlayingAudio = true;
    progressCount = 0;
    try {
      const audio = new Audio(url);
      audio.preload = 'auto';
      await audio.play();
      progressCount = 1;
    } catch (e) {
      console.warn('SentenceAudioButton: playback failed', e);
    } finally {
      isPlayingAudio = false;
    }
  }

  async function handleClick() {
    if (!target_language_code || !sentenceSlug) return;
    isGeneratingAudio = true;
    try {
      const info = await ensureSentenceInfo();
      if (!info) return;

      let { id, has_audio } = info;

      if (!has_audio) {
        // Attempt to generate if we have auth
        const generated = await generateAudio(sentenceSlug);
        if (!generated) {
          // No auth; nothing more we can do here
          return;
        }
        // Assume audio now exists
        has_audio = true;
      }

      if (has_audio) {
        await playAudio(buildAudioUrl(id));
      }
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
    <span class="badge bg-success ms-2">{progressCount}/1</span>
  {/if}
</button>

<style>
  .btn:disabled {
    opacity: 0.7;
  }
</style>


