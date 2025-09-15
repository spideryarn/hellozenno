<script lang="ts">
  // Import necessary functions and stores
  import { onMount, setContext } from 'svelte';
  import { invalidateAll } from '$app/navigation'; // Use invalidateAll for simplicity
  import { page } from '$app/stores'; 
  import type { LayoutData } from './$types'; // Import the type for LayoutData
  import { SITE_NAME, TAGLINE, CONTACT_EMAIL } from '$lib/config'; // Added Import
  import { getPageUrl } from '$lib/navigation';
  import { getLanguageName } from '$lib/generated/languages';
  import NebulaBackground from '$lib/components/NebulaBackground.svelte';
  import DropdownButton from '$lib/components/DropdownButton.svelte';
  import PencilSimple from 'phosphor-svelte/lib/PencilSimple';
  import User from 'phosphor-svelte/lib/User';
  import ShieldCheck from 'phosphor-svelte/lib/ShieldCheck';

  // Get data passed from +layout.ts
  export let data: LayoutData;
  $: ({ supabase, session } = data); // Destructure supabase and session reactively
  $: isAdmin = (data as any)?.is_admin === true;
  
  // Extract target language from profile (handle both envelope and direct shapes)
  $: targetLanguageCode = (data as any)?.profile?.profile?.target_language_code 
    || (data as any)?.profile?.target_language_code 
    || null;
  $: myLanguageUrl = targetLanguageCode 
    ? getPageUrl('sources', { target_language_code: targetLanguageCode }) 
    : null;
  $: myLanguageText = targetLanguageCode 
    ? `My Language: ${getLanguageName(targetLanguageCode)}` 
    : null;
  
  // Set Supabase client in context for child components to access
  $: if (supabase) {
    setContext('supabase', supabase);
  }

  // Handle auth state changes on the client
  onMount(() => {
    const { data: { subscription } } = supabase?.auth.onAuthStateChange((event: any, newSession: any) => {
      // Important: Check if the session has actually changed to avoid infinite loops
      if (newSession?.access_token !== session?.access_token) {
        console.log('Auth state changed detected in root layout, invalidating...');
        invalidateAll(); // Re-run all load functions
      }
    }) ?? { data: { subscription: null } }; // Handle null supabase during SSR

    // Cleanup subscription on component unmount
    return () => subscription?.unsubscribe();
  });

  async function handleLogout() {
    if (!supabase) return; // Should not happen in browser, but safety check
    try {
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error('Error logging out:', error);
        alert('Logout failed: ' + error.message);
      } else {
        console.log('User logged out successfully');
        // invalidateAll() will handle UI update via onAuthStateChange
      }
    } catch (error) {
      console.error('Unexpected error during logout:', error);
      alert('An unexpected error occurred during logout.');
    }
  }

  let isMenuOpen = false;
  
  // Build dropdown items reactively so we can include the language shortcut when available
  $: dropdownItems = [
    { type: 'header' as const, text: session?.user?.email || '' },
    ...(myLanguageUrl 
      ? [
          { type: 'divider' as const },
          { type: 'link' as const, text: myLanguageText || '', href: myLanguageUrl },
          { type: 'divider' as const },
        ] 
      : []),
    { type: 'link' as const, text: 'Edit Profile', href: '/auth/profile' },
    { type: 'divider' as const },
    { type: 'button' as const, text: 'Logout', onClick: handleLogout }
  ];
</script>

<!-- Add the svelte:head block for the title -->
<svelte:head>
  <title>{SITE_NAME} - {TAGLINE}</title>
</svelte:head>

<style>
  /* Dropdown styles are now handled by the DropdownButton component */

  .logo-image {
    height: 40px;
    transform: rotate(0deg) scale(1);
    transform-origin: center bottom;
  }
  
  @keyframes waggle {
    0% { transform: rotate(0deg) scale(1); }
    15% { transform: rotate(-8deg) scale(1.1); }
    30% { transform: rotate(8deg) scale(1.1); }
    45% { transform: rotate(-8deg) scale(1.1); }
    60% { transform: rotate(8deg) scale(1.1); }
    75% { transform: rotate(-5deg) scale(1.08); }
    90% { transform: rotate(3deg) scale(1.05); }
    100% { transform: rotate(0deg) scale(1.05); }
  }
  
  .logo-image:hover {
    animation: waggle 0.9s ease-in-out forwards;
    transform-origin: center bottom;
  }
  
  @media (max-width: 576px) {
    .logo-image {
      height: 36px;
    }
  }
  
  /* Footer Styles */
  .footer-links {
    color: #6c757d;
    font-size: 0.9rem;
  }
  
  .footer-link {
    color: #6c757d;
    text-decoration: none;
    transition: color 0.2s;
    padding: 0 0.5rem;
  }
  
  .footer-link:hover {
    color: var(--hz-color-primary-green);
    text-decoration: underline;
  }
  
  .footer-divider {
    color: #6c757d;
  }
  
  /* Make sure header and footer are above the nebula background */
  header, footer {
    position: relative;
    z-index: 100;
  }
</style>

<NebulaBackground>
  <div class="d-flex flex-column min-vh-100">
    <header class="bg-dark py-3">
      <nav class="container">
        <div class="d-flex justify-content-between align-items-center">
          <a 
            href="/" 
            class="text-decoration-none" 
            title="Hello Zenno">
            <img src="/img/logo.png" alt="Hello Zenno" class="logo-image" />
          </a>
          <div class="d-flex align-items-center">
            <a href="/languages" class="text-decoration-none text-white ms-4">Languages</a>
            <a href="/about" class="text-decoration-none text-white ms-4">About</a>
            {#if isAdmin}
              <a href="/admin" class="text-decoration-none text-white ms-4">Admin</a>
            {/if}
            
            <!-- Auth Status: Use reactive `session` from data -->
            {#if session}
              <!-- Reusable Dropdown Component for logged-in user -->
              <div class="ms-4">
                <DropdownButton 
                  buttonText={'Profile'} 
                  buttonSvelteContent={isAdmin ? ShieldCheck : User}
                  buttonClass="btn btn-sm btn-secondary text-on-light"
                  tooltipText={`Logged in as ${session.user.email}`}
                  bind:isOpen={isMenuOpen}
                  items={dropdownItems}
                />
              </div>
            {:else}
              <!-- Login Button for logged-out user -->
              <a href={`/auth?next=${encodeURIComponent($page.url.pathname)}`} class="btn btn-sm btn-primary ms-4">Login / Sign Up</a>
            {/if}
          </div>
        </div>
      </nav>
    </header>
    
    <main class="flex-grow-1 py-4">
      <slot />
    </main>
    
    <footer class="bg-dark py-4 text-center">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="footer-links mb-3">
              <a href="/" class="footer-link">Home</a>
              <span class="footer-divider">·</span>
              <a href="/about" class="footer-link">About</a>
              <span class="footer-divider">·</span>
              <a href="/faq" class="footer-link">FAQ</a>
              <span class="footer-divider">·</span>
              <a href="/privacy" class="footer-link">Privacy</a>
              <span class="footer-divider">·</span>
              <a href="/terms" class="footer-link">Terms</a>
              <span class="footer-divider">·</span>
              <!-- This isn't quite ready yet, so we'll uncomment it when it is.  -->
              <!-- <a href="/changelog" class="footer-link">Changelog</a>
              <span class="footer-divider">·</span> -->
              <a href="mailto:{CONTACT_EMAIL}" class="footer-link">Email</a>
              <span class="footer-divider">·</span>
              <a href="https://github.com/spideryarn/hellozenno" target="_blank" rel="noopener" class="footer-link">GitHub</a>
            </div>
            <p class="mb-0 text-white-50"><em>{TAGLINE}</em></p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</NebulaBackground>