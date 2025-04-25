<script lang="ts">
  // Import necessary functions and stores
  import { onMount, setContext } from 'svelte';
  import { invalidateAll } from '$app/navigation'; // Use invalidateAll for simplicity
  import { page } from '$app/stores'; 
  import type { LayoutData } from './$types'; // Import the type for LayoutData
  import { SITE_NAME, TAGLINE, CONTACT_EMAIL } from '$lib/config'; // Added Import
  import NebulaBackground from '$lib/components/NebulaBackground.svelte';

  // Get data passed from +layout.ts
  export let data: LayoutData;
  $: ({ supabase, session } = data); // Destructure supabase and session reactively
  
  // Set Supabase client in context for child components to access
  $: if (supabase) {
    setContext('supabase', supabase);
  }

  // Handle auth state changes on the client
  onMount(() => {
    const { data: { subscription } } = supabase?.auth.onAuthStateChange((event, newSession) => {
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

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }
</script>

<!-- Add the svelte:head block for the title -->
<svelte:head>
  <title>{SITE_NAME} - {TAGLINE}</title>
</svelte:head>

<style>
  /* Add basic styles for custom dropdown */
  .profile-dropdown {
    position: relative; /* Needed for absolute positioning of menu */
  }

  .profile-menu {
    position: absolute;
    top: 100%; /* Position below the button */
    right: 0; /* Align to the right */
    z-index: 1000; /* Ensure it's above other content */
    display: block; /* Override Bootstrap's default display: none */
    min-width: 10rem;
    padding: 0.5rem 0;
    margin: 0.125rem 0 0; /* Slight separation */
    font-size: 1rem;
    color: #212529;
    text-align: left;
    list-style: none;
    background-color: #fff;
    background-clip: padding-box;
    border: 1px solid rgba(0,0,0,.15);
    border-radius: 0.25rem;
  }

  /* Reuse Bootstrap styles for items if available or add custom ones */
  .profile-menu .dropdown-header { /* Assuming Bootstrap CSS is still linked */
      display: block;
      padding: 0.5rem 1rem;
      margin-bottom: 0;
      font-size: 0.875rem;
      color: #6c757d;
      white-space: nowrap;
  }
  .profile-menu .dropdown-item {
      display: block;
      width: 100%;
      padding: 0.25rem 1rem;
      clear: both;
      font-weight: 400;
      color: #212529;
      text-align: inherit;
      white-space: nowrap;
      background-color: transparent;
      border: 0;
      text-decoration: none; /* Added for links */
  }
  .profile-menu .dropdown-item:hover,
  .profile-menu .dropdown-item:focus {
      color: #1e2125;
      background-color: #e9ecef;
  }
  .profile-menu .dropdown-divider {
    height: 0;
    margin: 0.5rem 0;
    overflow: hidden;
    border-top: 1px solid rgba(0,0,0,.15);
  }

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
            <a href="/languages" class="text-decoration-none text-white ms-3">Languages</a>
            <a href="/about" class="text-decoration-none text-white ms-3">About</a>
            
            <!-- Auth Status: Use reactive `session` from data -->
            {#if session}
              <!-- Custom Svelte Dropdown for logged-in user -->
              <div class="profile-dropdown ms-3"> 
                <button
                  class="btn btn-sm btn-secondary"
                  type="button"
                  aria-haspopup="true"
                  aria-expanded={isMenuOpen}
                  on:click={toggleMenu}
                >
                  <i class="fas fa-user"></i> Profile
                </button>
                {#if isMenuOpen} 
                <ul class="profile-menu" aria-labelledby="profileDropdownMenuButton"> 
                  <!-- Use session.user.email -->
                  <li><h6 class="dropdown-header">{session.user.email}</h6></li>
                  <li><a class="dropdown-item" href="/auth/profile">Edit Profile</a></li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <button class="dropdown-item" type="button" on:click={() => { handleLogout(); isMenuOpen = false; }}>
                      Logout
                    </button>
                  </li>
                </ul>
                {/if}
              </div>
            {:else}
              <!-- Login Button for logged-out user -->
              <a href={`/auth?next=${encodeURIComponent($page.url.pathname)}`} class="btn btn-sm btn-primary ms-3">Login / Sign Up</a>
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