<script lang="ts">
  // Import any common components or global styles here
  import { user } from '$lib/stores/authStore';
  import { supabase } from '$lib/supabaseClient';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores'; // Import the page store
  // import Dropdown from 'bootstrap/js/dist/dropdown'; // Remove Bootstrap JS import
  // import { onMount } from 'svelte'; // Remove onMount if only used for dropdown

  async function handleLogout() {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error('Error logging out:', error);
        alert('Logout failed: ' + error.message);
      } else {
        console.log('User logged out');
        // Optionally redirect after logout
        // await goto('/'); 
      }
    } catch (error) {
      console.error('Unexpected error during logout:', error);
      alert('An unexpected error occurred during logout.');
    }
  }

  // // Remove dropdown initialization
  // onMount(() => {
  //   const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
  //   dropdownElementList.map(function (dropdownToggleEl) {
  //     return new Dropdown(dropdownToggleEl);
  //   });
  // });

  let isMenuOpen = false;

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

  // TODO: Add click outside handler if needed

</script>

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
</style>

<div class="d-flex flex-column min-vh-100">
  <header class="bg-dark py-3">
    <nav class="container">
      <div class="d-flex justify-content-between align-items-center">
        <a href="/" class="text-decoration-none" title="Hello Zenno">
          <img src="/logo.png" alt="Hello Zenno" class="logo-image" />
        </a>
        <div class="d-flex align-items-center">
          <a href="/languages" class="text-decoration-none text-white ms-3">Languages</a>
          
          <!-- Auth Status -->
          {#if $user}
            <!-- Custom Svelte Dropdown for logged-in user -->
            <div class="profile-dropdown ms-3"> <!-- Use custom class -->
              <button
                class="btn btn-sm btn-secondary"
                type="button"
                aria-haspopup="true"
                aria-expanded={isMenuOpen}
                on:click={toggleMenu}
              >
                <i class="fas fa-user"></i> Profile
              </button>
              {#if isMenuOpen} <!-- Conditionally render menu -->
              <ul class="profile-menu" aria-labelledby="profileDropdownMenuButton"> <!-- Use custom class -->
                <li><h6 class="dropdown-header">{$user.email}</h6></li>
                <li><a class="dropdown-item" href="/profile">Edit Profile</a></li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <button class="dropdown-item" type="button" on:click={() => { handleLogout(); isMenuOpen = false; }}> <!-- Close menu on logout click -->
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
  
  <footer class="bg-dark py-3 text-center text-white-50">
    <div class="container">
      <p class="mb-0">Hello Zenno - Learn foreign words with a magical AI dictionary</p>
    </div>
  </footer>
</div>

<!-- Remove the global style as it's now in our CSS files --> 