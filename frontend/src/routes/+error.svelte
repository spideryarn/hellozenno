<script lang="ts">
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { get_language_name } from '$lib/utils';
  
  let languageName = '';
  let languageCode = '';
  
  // Check if we're in a language path
  const isLanguagePath = page.url.pathname.startsWith('/language/');
  
  // Extract language code from URL if in a language path
  if (isLanguagePath) {
    const parts = page.url.pathname.split('/');
    if (parts.length >= 3 && parts[1] === 'language') {
      languageCode = parts[2];
    }
  }
  
  onMount(async () => {
    if (languageCode) {
      try {
        languageName = await get_language_name(languageCode);
      } catch (e) {
        languageName = languageCode.toUpperCase();
      }
    }
  });
</script>

<svelte:head>
  <title>{page.status} - {page.error?.message || 'Page Not Found'} - Hello Zenno</title>
</svelte:head>

<div class="container">
  <div class="row justify-content-center mt-5">
    <div class="col-md-8">
      <div class="card bg-dark text-white border-danger">
        <div class="card-header bg-danger text-white">
          <h2 class="mb-0">{page.status} - {page.error?.message || 'Page Not Found'}</h2>
        </div>
        <div class="card-body">
          <p class="lead">Sorry, the page you're looking for doesn't exist.</p>
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
            {#if languageCode}
              <li>
                <a href="/language/{languageCode}/sources" class="btn btn-info">
                  <i class="ph ph-arrow-left me-2"></i>Back to {languageName || languageCode.toUpperCase()} language page
                </a>
              </li>
            {/if}
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>