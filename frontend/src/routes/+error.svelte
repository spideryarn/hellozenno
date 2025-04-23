<script lang="ts">
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { get_language_name } from '$lib/utils';
  import { dev } from '$app/environment';
  import { SITE_NAME } from '$lib/config';
  import MultilingualApology from '$lib/components/MultilingualApology.svelte';
  import ContactButton from '$lib/components/ContactButton.svelte';
  
  let languageName = '';
  let languageCode = '';
  
  // Check if we're in a language path or use route params
  const isLanguagePath = page.url.pathname.startsWith('/language/');
  
  // Get language code either from URL path or route params
  if (isLanguagePath) {
    const parts = page.url.pathname.split('/');
    if (parts.length >= 3 && parts[1] === 'language') {
      languageCode = parts[2];
    }
  } else if (page.params.target_language_code) {
    // This handles the case when the error is thrown from a language-specific route
    languageCode = page.params.target_language_code;
  }
  
  // Define error-specific data
  const errorInfo = {
    401: {
      title: 'Authentication Required',
      message: 'Login required to access this content',
      icon: 'ph-lock-key',
      actionText: 'Login or Sign Up',
      actionUrl: `/auth?next=${encodeURIComponent(page.url.pathname)}`,
      actionIcon: 'ph-sign-in',
      class: 'border-warning',
      headerClass: 'bg-warning text-dark'
    },
    403: {
      title: 'Access Forbidden',
      message: 'You do not have permission to access this content',
      icon: 'ph-prohibit',
      class: 'border-danger',
      headerClass: 'bg-danger text-white'
    },
    404: {
      title: 'Page Not Found',
      message: 'The page you requested does not exist',
      icon: 'ph-question',
      class: 'border-danger',
      headerClass: 'bg-danger text-white'
    },
    500: {
      title: 'Server Error',
      message: 'Something went wrong on our side',
      icon: 'ph-warning-circle',
      class: 'border-danger',
      headerClass: 'bg-danger text-white'
    }
  };
  
  // Get the appropriate error information or fall back to default
  const currentError = errorInfo[page.status] || {
    title: 'Error',
    message: 'An unexpected error occurred',
    icon: 'ph-warning-circle',
    class: 'border-danger',
    headerClass: 'bg-danger text-white'
  };
  
  // Check for authentication_required_for_generation flag in error body
  const isAuthRequiredForGeneration = page.error?.body?.authentication_required_for_generation || 
                                     page.error?.body?.audio_requires_login;
  
  // Override with auth-required details if detected
  if (isAuthRequiredForGeneration) {
    Object.assign(currentError, errorInfo[401]);
    currentError.message = 'Login required to generate AI content';
  }
  
  // Prepare error details for email
  const errorDetails = `
Error Details:
- Status: ${page.status}
- URL: ${page.url.toString()}
- User Agent: ${typeof navigator !== 'undefined' ? navigator.userAgent : 'Unknown'}
- Time: ${new Date().toISOString()}
- Message: ${page.error?.message || currentError.title}
${page.error?.stack ? '\nStack Trace:\n' + page.error.stack : ''}
  `.trim();
  
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
  <title>{page.status} | {currentError.title} | {SITE_NAME}</title>
</svelte:head>

<div class="container">
  <div class="row justify-content-center mt-5">
    <div class="col-md-8">
      <div class={`card bg-dark text-white ${currentError.class}`}>
        <div class={`card-header ${currentError.headerClass}`}>
          <h2 class="mb-0">
            <i class={`${currentError.icon} me-2`}></i>
            {page.status} - {page.error?.message || currentError.title}
          </h2>
        </div>
        <div class="card-body">
          <!-- Multilingual apology component -->
          <MultilingualApology className="mb-3" />
          
          <!-- Show appropriate error message based on context -->
          {#if languageCode && page.error?.message?.includes('Failed to search') || page.url.pathname.includes('/search')}
            <p class="lead">Sorry, something went wrong while accessing {languageName || languageCode.toUpperCase() || 'language'} content.</p>
          {/if}
          
          <div class="mt-4 mb-5 text-center report-links">
            <a 
              href="https://github.com/spideryarn/hellozenno/issues/new" 
              target="_blank" 
              rel="noopener noreferrer" 
              class="report-link"
              title="Create an issue on GitHub"
            >
              <img 
                src="/img/extern/GitHub-logo.png" 
                alt="Create a GitHub issue" 
                class="report-image " 
                width="97"
                height="auto"
              />
              <span class="report-caption">Open GitHub Issue</span>
            </a>

            <a 
              href={`mailto:hellozenno@gregdetre.com?subject=${encodeURIComponent(`${SITE_NAME} Error Report: ${page.status} on ${page.url.pathname}`)}&body=${encodeURIComponent(errorDetails)}`}
              class="report-link"
              title="Email us about this error"
            >
              <img 
                src="/img/email_contact_envelope.png" 
                alt="Report this issue via email" 
                class="report-image email-image" 
                width="150"
                height="auto"
              />
              <span class="report-caption">Report via Email</span>
            </a>
        </div>
          
          <p>You might also want to:</p>
          <ul class="list-unstyled">
            {#if currentError.actionText && currentError.actionUrl}
              <li class="mb-2">
                <a href={currentError.actionUrl} class="btn btn-warning">
                  <i class={`${currentError.actionIcon} me-2`}></i>{currentError.actionText}
                </a>
              </li>
            {/if}
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
                <a href="/language/{languageCode}/sources" class="btn btn-primary">
                  <i class="ph ph-arrow-left me-2"></i>Back to {languageName || languageCode.toUpperCase()} language page
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
                    
                    {#if page.error.body}
                      <h5 class="mt-3">Error Body:</h5>
                      <pre class="bg-dark text-light p-3 rounded" style="overflow-x: auto; max-height: 300px;">{JSON.stringify(page.error.body, null, 2)}</pre>
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
</div>

<style>
  .report-links {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 2rem;
  }
  
  .report-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-decoration: none;
    color: var(--hz-color-text-secondary);
    transition: all 0.3s ease;
    padding: 0.5rem;
    border-radius: 10px;
  }
  
  .report-link:hover {
    transform: translateY(-5px);
    color: var(--hz-color-text-main);
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  .report-image {
    max-width: 150px;
    border-radius: 8px;
    transition: all 0.3s ease;
    margin-bottom: 0.75rem;
  }
  
  .email-image {
    width: 150px;
  }
  
  .github-image {
    width: 120px;
    background-color: white;
    padding: 10px;
  }
  
  .report-caption {
    font-size: 1rem;
    font-weight: 500;
  }
</style>