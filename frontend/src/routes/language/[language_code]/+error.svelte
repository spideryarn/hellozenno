<script lang="ts">
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { get_language_name } from '$lib/utils';
  
  let languageName = '';

  onMount(async () => {
    if (page.params.language_code) {
      try {
        languageName = await get_language_name(page.params.language_code);
      } catch (e) {
        languageName = page.params.language_code.toUpperCase();
      }
    }
  });
</script>

<svelte:head>
  <title>{page.status} - Error - {languageName || page.params.language_code?.toUpperCase() || ''} - Hello Zenno</title>
</svelte:head>

<div class="row justify-content-center mt-5">
  <div class="col-md-8">
    <div class="card bg-dark text-white border-danger">
      <div class="card-header bg-danger text-white">
        <h2 class="mb-0">{page.status} - {page.error?.message || 'Error'}</h2>
      </div>
      <div class="card-body">
        <p class="lead">Sorry, something went wrong while accessing {languageName || page.params.language_code?.toUpperCase() || 'language'} content.</p>
        <p>You might want to:</p>
        <ul class="list-unstyled">
          <li class="mb-2">
            <a href="/" class="btn btn-primary">
              <i class="ph ph-house-line me-2"></i>Go to the homepage
            </a>
          </li>
          <li class="mb-2">
            <a href="/languages" class="btn btn-secondary">
              <i class="ph ph-translate me-2"></i>View available languages
            </a>
          </li>
          {#if page.params.language_code}
            <li>
              <a href="/language/{page.params.language_code}/sources" class="btn btn-info">
                <i class="ph ph-arrow-left me-2"></i>Back to {languageName || page.params.language_code.toUpperCase()} language page
              </a>
            </li>
          {/if}
        </ul>
      </div>
    </div>
  </div>
</div>