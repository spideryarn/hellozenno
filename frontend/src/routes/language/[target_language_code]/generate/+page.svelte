<script lang="ts">
  import type { PageData } from './$types';
  import { apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { goto } from '$app/navigation';
  // Use the Supabase client provided via root layout data (SSR-aware)

  export let data: PageData;

  $: ({ target_language_code: languageCode, languageName, sourcedirs, session } = data);

  let title: string = '';
  let level: string = '';
  let selectedSourcedir: string = '';
  let useCustomSourcedir = false;
  let newSourcedirName: string = '';
  let isSubmitting = false;
  let errorMessage: string | null = null;

  const LEVELS = ['Auto', 'A1','A2','B1','B2','C1','C2'];

  $: if (!selectedSourcedir && Array.isArray(sourcedirs) && sourcedirs.length > 0) {
    // Default to AI-generated examples if present, else first option
    const preferred = sourcedirs.find((d: any) => d.path === 'AI-generated examples');
    selectedSourcedir = preferred?.path || sourcedirs[0]?.path || 'AI-generated examples';
  }

  async function submitForm() {
    errorMessage = null;
    if (!session) {
      const next = encodeURIComponent(`/language/${languageCode}/generate`);
      await goto(`/auth?next=${next}`);
      return;
    }
    isSubmitting = true;
    try {
      const body: any = {};
      if (title.trim()) body.title = title.trim();
      if (level && level !== 'Auto') body.language_level = level;
      const dirPath = useCustomSourcedir && newSourcedirName.trim() ? newSourcedirName.trim() : selectedSourcedir;
      if (dirPath) body.sourcedir_path = dirPath;

      const resp = await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEFILE_API_GENERATE_SOURCEFILE_API,
        params: { target_language_code: languageCode },
        options: {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        },
        timeoutMs: 120000
      });

      const url = resp?.url_text_tab || `/language/${languageCode}/sources`;
      await goto(url);
    } catch (e: any) {
      errorMessage = e?.message || 'Failed to generate content';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Generate – {languageName}</title>
</svelte:head>

<div class="container mt-4">
  <div class="row mb-4">
    <div class="col">
      <h1 class="mb-3">Generate AI Content</h1>

      <div class="mb-3">
        <nav class="nav nav-pills gap-2">
          <a class="nav-link" href="/language/{languageCode}/sources">Sources</a>
          <a class="nav-link" href="/language/{languageCode}/wordforms">Wordforms</a>
          <a class="nav-link" href="/language/{languageCode}/lemmas">Lemmas</a>
          <a class="nav-link" href="/language/{languageCode}/sentences">Sentences</a>
          <a class="nav-link" href="/language/{languageCode}/phrases">Phrases</a>
          <a class="nav-link" href="/language/{languageCode}/flashcards">Flashcards</a>
          <a class="nav-link active" aria-current="page" href="/language/{languageCode}/generate">Generate</a>
        </nav>
      </div>

      {#if !session}
        <div class="alert alert-warning">
          You must be logged in to generate content.
          <a class="ms-2" href={`/auth?next=${encodeURIComponent(`/language/${languageCode}/generate`)}`}>Login</a>
        </div>
      {/if}

      <form class="card p-3 bg-dark" on:submit|preventDefault={submitForm}>
        <div class="mb-3">
          <label class="form-label" for="fldTitle">Title (optional)</label>
          <input id="fldTitle" class="form-control" bind:value={title} placeholder="e.g. A day at the market" />
        </div>

        <div class="mb-3">
          <label class="form-label" for="fldLevel">Language Level</label>
          <select id="fldLevel" class="form-select" bind:value={level}>
            {#each LEVELS as lvl}
              <option value={lvl}>{lvl}</option>
            {/each}
          </select>
          <div class="form-text">Default is Auto (recommended)</div>
        </div>

        <div class="mb-3">
          <label class="form-label" for="fldSourcedir">Sourcedir</label>
          <div class="d-flex gap-2 align-items-center flex-wrap">
            <select id="fldSourcedir" class="form-select w-auto" bind:value={selectedSourcedir} disabled={useCustomSourcedir}>
              {#if Array.isArray(sourcedirs) && sourcedirs.length > 0}
                {#each sourcedirs as dir}
                  <option value={dir.path}>{dir.path}</option>
                {/each}
              {:else}
                <option value="AI-generated examples">AI-generated examples</option>
              {/if}
            </select>
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="chkCustom" bind:checked={useCustomSourcedir} />
              <label class="form-check-label" for="chkCustom">Other…</label>
            </div>
            {#if useCustomSourcedir}
              <input class="form-control w-auto" placeholder="New sourcedir name" bind:value={newSourcedirName} />
            {/if}
          </div>
        </div>

        {#if errorMessage}
          <div class="alert alert-danger">{errorMessage}</div>
        {/if}

        <div class="d-flex gap-2">
          <button class="btn btn-success" type="submit" disabled={!session || isSubmitting}>
            {#if isSubmitting}Generating…{:else}Generate{/if}
          </button>
          <a class="btn btn-secondary" href={`/language/${languageCode}/sources`}>Cancel</a>
        </div>
      </form>
    </div>
  </div>
</div>

<style>
  .form-text { color: #9aa0a6; }
  .card { border-color: #2a2f36; }
  .nav-link.active { background-color: var(--hz-color-primary-green, #28a745); }
  .form-control, .form-select { max-width: 480px; }
  @media (max-width: 576px) { .form-control, .form-select { max-width: 100%; } }
</style>


