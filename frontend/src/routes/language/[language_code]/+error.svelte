<script lang="ts">
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { get_language_name } from '$lib/utils';
  import { dev } from '$app/environment';
  
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
      
      {#if dev && page.error}
        <div class="card-footer bg-dark border-top border-danger p-0">
          <div class="accordion" id="errorDetails">
            <div class="accordion-item bg-dark text-white border-0">
              <h2 class="accordion-header" id="headingOne">
                <button 
                  class="accordion-button bg-dark text-white collapsed" 
                  type="button" 
                  data-bs-toggle="collapse" 
                  data-bs-target="#collapseErrorDetails" 
                  aria-expanded="false" 
                  aria-controls="collapseErrorDetails"
                >
                  Developer Error Details
                </button>
              </h2>
              <div 
                id="collapseErrorDetails" 
                class="accordion-collapse collapse" 
                aria-labelledby="headingOne" 
                data-bs-parent="#errorDetails"
              >
                <div class="accordion-body">
                  <h5>Error:</h5>
                  <pre class="bg-dark text-danger p-3 rounded">{page.status}: {page.error.message}</pre>
                  
                  {#if page.error.stack}
                    <h5 class="mt-3">Stack Trace:</h5>
                    <pre class="bg-dark text-light p-3 rounded" style="overflow-x: auto; max-height: 300px;">{page.error.stack}</pre>
                  {/if}
                  
                  <h5 class="mt-3">Route Information:</h5>
                  <ul>
                    <li><strong>URL:</strong> {page.url.toString()}</li>
                    <li><strong>Path:</strong> {page.url.pathname}</li>
                    <li><strong>Route ID:</strong> {page.route.id}</li>
                    <li><strong>Status:</strong> {page.status}</li>
                  </ul>
                  
                  {#if Object.keys(page.params).length > 0}
                    <h5 class="mt-3">Route Parameters:</h5>
                    <pre class="bg-dark text-light p-3 rounded">{JSON.stringify(page.params, null, 2)}</pre>
                  {/if}
                  
                  {#if Object.keys(page.data).length > 0}
                    <h5 class="mt-3">Page Data:</h5>
                    <pre class="bg-dark text-light p-3 rounded" style="overflow-x: auto; max-height: 300px;">{JSON.stringify(page.data, null, 2)}</pre>
                  {/if}
                </div>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>