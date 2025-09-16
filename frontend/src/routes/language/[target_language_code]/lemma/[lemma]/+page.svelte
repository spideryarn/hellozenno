<script lang="ts">
  import type { PageData } from './$types';  
  import { Card, LemmaCard, MetadataCard, LemmaContent } from '$lib';
  import { apiFetch, getApiUrl } from '$lib/api'; // Import apiFetch
  import { RouteName } from '$lib/generated/routes';
  import { page } from '$app/stores'; // Import page store for current URL
  import { SITE_NAME, LEMMA_AUDIO_SAMPLES } from '$lib/config';
  import { truncate, generateMetaDescription } from '$lib/utils';
  import { goto } from '$app/navigation';
  import SpeakerSimpleHigh from 'phosphor-svelte/lib/SpeakerSimpleHigh';
  import PQueue from 'p-queue';
  
  export let data: PageData;
  // Destructure lemmaResult which contains the API response, and the separately passed params
  // Also get the supabase client instance passed from +layout.ts
  const { lemmaResult, target_language_code, lemma: lemmaParam, supabase: supabaseClient } = data; 
  
  // Extract the actual lemma data and potential error from lemmaResult
  const lemma_metadata = lemmaResult?.lemma_metadata || lemmaResult?.partial_lemma_metadata || {};
  const authError = lemmaResult?.authentication_required_for_generation 
                      ? lemmaResult.description 
                      : null;
  const notFoundError = lemmaResult?.error === 'Not Found'; // Check for 404 specifically
  
  // Extract the server-provided metadata (created/updated timestamps)
  const metadata = lemmaResult?.metadata;

  // Define login URL with redirect back to current page
  $: loginUrl = `/auth?next=${encodeURIComponent($page.url.pathname + $page.url.search)}`;

  // Debugging logs
  $: console.log('Lemma Page - data prop:', data);
  $: console.log('Lemma Page - supabaseClient from data:', supabaseClient);
  $: console.log('Lemma Page - lemma_metadata:', lemma_metadata);
  $: console.log('Lemma Page - target_language_code:', target_language_code);
  $: console.log('Lemma Page - lemma_metadata.lemma value for URL:', lemma_metadata?.lemma);
  // deleteUrl is now constructed inside handleDeleteSubmit if using apiFetch directly with RouteName

  async function handleDeleteSubmit(event: SubmitEvent) {
    event.preventDefault();

    const confirmed = confirm('Are you sure you want to delete this lemma? All associated wordforms will also be deleted. This action cannot be undone.');
    if (!confirmed) return;

    if (!lemma_metadata?.lemma) {
      console.error('Lemma value missing – cannot delete lemma.');
      alert('Cannot delete lemma: lemma data is missing.');
      return;
    }
    
    if (!supabaseClient) {
      console.error('Supabase client is not available for API call.');
      alert('Authentication context not available. Please try refreshing the page.');
      return;
    }

    try {
      await apiFetch({
        supabaseClient: supabaseClient, // Pass the client instance
        routeName: RouteName.LEMMA_API_DELETE_LEMMA_API,
        params: {
          target_language_code: target_language_code,
          lemma: lemma_metadata.lemma
        },
        options: { method: 'POST' } // apiFetch sets Content-Type and handles auth header
      });

      // apiFetch throws on non-ok responses, so if we reach here, it was successful (or 204)
      goto(`/language/${target_language_code}/lemmas`);
    } catch (err: any) {
      console.error('Error deleting lemma (via apiFetch):', err);
      alert(`Failed to delete lemma: ${err.message || 'An unknown error occurred.'}`);
    }
  }
  // Audio state
  let isGeneratingAudio = false;
  let isPlayingAudio = false;
  let playIndex = 0;
  let lastVariantUrls: string[] | null = null;
  let showLoginToast = false;
  let progressCount = 0;

  async function fetchVariants(): Promise<
    { id: number; provider: string; metadata: Record<string, any>; url: string }[]
  > {
    const res = await apiFetch({
      supabaseClient: null, // public endpoint
      routeName: RouteName.LEMMA_API_GET_LEMMA_AUDIO_VARIANTS_API,
      params: {
        target_language_code,
        lemma: lemma_metadata.lemma,
      },
      options: { method: 'GET' }
    });
    return Array.isArray(res) ? res : [];
  }

  async function ensureVariants(n: number): Promise<void> {
    // Requires auth; will no-op if already present
    await apiFetch({
      supabaseClient: supabaseClient,
      routeName: RouteName.LEMMA_API_ENSURE_LEMMA_AUDIO_API,
      params: {
        target_language_code,
        lemma: lemma_metadata.lemma,
      },
      options: { method: 'POST' },
      searchParams: { n }
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
    playIndex = 0;
    progressCount = 0;

    // Preload with concurrency equal to the number of samples (3 by default)
    const queue = new PQueue({ concurrency: Math.max(1, LEMMA_AUDIO_SAMPLES) });
    const audioElems: HTMLAudioElement[] = [];
    await Promise.all(
      urls.map((u) =>
        queue.add(async () => {
          const a = new Audio(u);
          a.preload = 'auto';
          audioElems.push(a);
        })
      )
    );

    const playNext = () => {
      if (playIndex >= audioElems.length) {
        isPlayingAudio = false;
        progressCount = 3;
        return;
      }
      const a = audioElems[playIndex];
      playIndex += 1;
      progressCount = playIndex; // 1..3
      a.onended = playNext;
      a.onerror = playNext;
      a.play().catch(() => playNext());
    };
    playNext();
  }

  async function handlePlayLemmaAudio() {
    try {
      isGeneratingAudio = true;

      // 1) Get existing variants
      let variants = await fetchVariants();

      // 2) Ensure up to configured number exist if needed
      const needed = LEMMA_AUDIO_SAMPLES - variants.length;
      if (needed > 0 && supabaseClient) {
        await ensureVariants(LEMMA_AUDIO_SAMPLES); // server selects voices; idempotent
        variants = await fetchVariants();
      }

      // 3) Build URLs and optionally shuffle order
      const urls = variants.slice(0, LEMMA_AUDIO_SAMPLES).map((v) => v.url);
      lastVariantUrls = urls;

      // 4) Play sequence (shuffle order on each click if already cached)
      const toPlay = lastVariantUrls && lastVariantUrls.length === LEMMA_AUDIO_SAMPLES ? shuffle(lastVariantUrls) : urls;
      await playSequential(toPlay);
    } catch (e) {
      console.warn('Lemma audio error:', e);
      // If unauthorized on ensure, guide login
      showLoginToast = true;
    } finally {
      isGeneratingAudio = false;
    }
  }
</script>

<svelte:head>
  <title>{truncate(lemma_metadata?.lemma || lemmaParam, 30)} | Lemma | {lemmaResult?.target_language_name || target_language_code} | {SITE_NAME}</title>
  <meta name="description" content="{generateMetaDescription(
    lemma_metadata?.translations?.join('; ') || '',
    `${lemma_metadata?.lemma || lemmaParam} - ${lemmaResult?.target_language_name || target_language_code} lemma`
  )}">
</svelte:head>

<div class="container">
  <div class="row mb-4">
    <div class="col">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/languages">Languages</a></li>
          <li class="breadcrumb-item"><a href="/language/{target_language_code}/sources">{lemmaResult?.target_language_name || target_language_code}</a></li>
          <li class="breadcrumb-item"><a href="/language/{target_language_code}/lemmas">Lemmas</a></li>
          <li class="breadcrumb-item active" aria-current="page">{lemma_metadata?.lemma || 'Lemma'}</li>
        </ol>
      </nav>
    </div>
  </div>
  
  {#if authError}
  <!-- <Alert type="warning" class="mb-4">
    { authError }
    <a href={loginUrl} class="btn btn-sm btn-primary ms-2">Login to generate</a>
  </Alert> -->
  <div class="alert alert-warning mb-4" role="alert">
    { authError }
    <a href={loginUrl} class="btn btn-sm btn-primary ms-2">Login to generate</a>
  </div>
  {/if}

  <div class="row mb-3">
    <div class="col-md-8">
      <div class="d-flex align-items-center gap-2 mb-4 position-relative">
        <h1 class="mb-0">{lemma_metadata.lemma}</h1>
        <button
          class="btn btn-outline-light btn-sm d-inline-flex align-items-center"
          on:click|preventDefault={handlePlayLemmaAudio}
          disabled={isGeneratingAudio || isPlayingAudio}
          aria-label="Play pronunciations"
          title="Play pronunciations"
        >
          <SpeakerSimpleHigh size={20} />
          {#if isGeneratingAudio || isPlayingAudio}
            <span class="badge bg-success ms-2">{progressCount}/{LEMMA_AUDIO_SAMPLES}</span>
          {/if}
        </button>
      </div>
    </div>
    <div class="col-md-4 text-md-end">
      {#if metadata}
      <MetadataCard {metadata} />
      {/if}
    </div>
  </div>

  {#if lemma_metadata?.lemma} <!-- Only show delete if we have a lemma to delete -->
  <div class="mb-4">
    <form on:submit={handleDeleteSubmit}> <!-- Removed action and method, handled by JS -->
      <button type="submit" class="btn btn-danger">Delete lemma</button>
    </form>
  </div>
  {/if}
  
  <!-- Use the shared LemmaContent component -->
  <LemmaContent 
    lemma_metadata={lemma_metadata}
    {target_language_code}
    showFullLink={false}
    isAuthError={!!authError}
  />
</div>

<style>
  .breadcrumb {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
  }
  .toast-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1055;
  }
</style> 

{#if showLoginToast}
  <div class="toast-container">
    <div class="toast show align-items-center text-bg-warning border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          Login required to generate pronunciation audio.
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" aria-label="Close" on:click={() => showLoginToast = false}></button>
      </div>
    </div>
  </div>
{/if}
