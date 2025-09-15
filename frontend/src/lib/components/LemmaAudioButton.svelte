<script lang="ts">
  import SpeakerHigh from 'phosphor-svelte/lib/SpeakerHigh';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import type { SupabaseClient } from '@supabase/supabase-js';

  export let target_language_code: string;
  export let lemma: string;
  export let supabaseClient: SupabaseClient | null = null;
  export let className: string = '';
  export let iconSize: number = 18;

  let isGeneratingAudio = false;
  let isPlayingAudio = false;
  let progressCount = 0;
  let lastVariantUrls: string[] | null = null;

  async function fetchVariants(): Promise<{ provider: string; voice_name: string; url: string }[]> {
    const res = await apiFetch({
      supabaseClient: null, // public endpoint
      routeName: RouteName.LEMMA_API_GET_LEMMA_AUDIO_VARIANTS_API,
      params: { target_language_code, lemma },
      options: { method: 'GET' },
    });
    return Array.isArray(res) ? res : [];
  }

  async function ensureVariants(n: number): Promise<void> {
    await apiFetch({
      supabaseClient: supabaseClient,
      routeName: RouteName.LEMMA_API_ENSURE_LEMMA_AUDIO_API,
      params: { target_language_code, lemma },
      options: { method: 'POST' },
      searchParams: { n },
    });
  }

  function shuffle<T>(arr: T[]): T[] {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  async function playSequential(urls: string[]) {
    if (!urls.length) return;
    isPlayingAudio = true;
    progressCount = 0;
    let index = 0;

    const audioElems: HTMLAudioElement[] = urls.map((u) => {
      const a = new Audio(u);
      a.preload = 'auto';
      return a;
    });

    const playNext = () => {
      if (index >= audioElems.length) {
        isPlayingAudio = false;
        progressCount = 3;
        return;
      }
      const a = audioElems[index];
      index += 1;
      progressCount = index; // 1..3
      a.onended = playNext;
      a.onerror = playNext;
      a.play().catch(() => playNext());
    };
    playNext();
  }

  async function handleClick() {
    if (!lemma || !target_language_code) return;
    try {
      isGeneratingAudio = true;
      // 1) Get existing variants
      let variants = await fetchVariants();
      // 2) Ensure up to 3 exist if needed
      const needed = 3 - variants.length;
      if (needed > 0 && supabaseClient) {
        await ensureVariants(3);
        variants = await fetchVariants();
      }
      // 3) Build URLs and optionally shuffle order
      const urls = variants.slice(0, 3).map((v) => v.url);
      lastVariantUrls = urls;
      const toPlay = lastVariantUrls && lastVariantUrls.length === 3 ? shuffle(lastVariantUrls) : urls;
      await playSequential(toPlay);
    } catch (e) {
      // Swallow error; upstream pages may show login prompts
      console.warn('LemmaAudioButton error:', e);
    } finally {
      isGeneratingAudio = false;
    }
  }
</script>

<button
  class="btn btn-outline-light btn-sm d-inline-flex align-items-center {className}"
  on:click|preventDefault={handleClick}
  disabled={isGeneratingAudio || isPlayingAudio}
  aria-label="Play pronunciations"
  title="Play pronunciations"
>
  {#if isGeneratingAudio}
    <LoadingSpinner size="sm" />
  {:else}
    <SpeakerHigh size={iconSize} />
  {/if}
  {#if isGeneratingAudio || isPlayingAudio}
    <span class="badge bg-success ms-2">{progressCount}/3</span>
  {/if}
</button>

<style>
  .btn:disabled {
    opacity: 0.7;
  }
</style>


