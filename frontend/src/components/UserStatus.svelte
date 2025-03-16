<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore, user, isAuthenticated, isLoading } from '../lib/auth-store';
  
  // Component state
  let dropdownOpen = false;
  let redirectToLogin = false;
  
  // Initialize auth on mount
  onMount(() => {
    authStore.init();
  });
  
  // Toggle dropdown menu
  function toggleDropdown() {
    dropdownOpen = !dropdownOpen;
  }
  
  // Close dropdown when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.user-status')) {
      dropdownOpen = false;
    }
  }
  
  // Set up click outside handler
  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
  
  // Handle logout
  async function handleLogout() {
    const result = await authStore.signOut();
    if (result.success) {
      // Redirect to home page after logout
      window.location.href = '/';
    }
  }
  
  // Redirect to login page
  function goToLogin() {
    window.location.href = '/auth';
  }
</script>

<svelte:window on:click={handleClickOutside} />

<div class="user-status">
  {#if $isLoading}
    <div class="loading-indicator">
      <span class="loading-dot"></span>
      <span class="loading-dot"></span>
      <span class="loading-dot"></span>
    </div>
  {:else if $isAuthenticated && $user}
    <button class="user-button" on:click={toggleDropdown}>
      <div class="user-avatar">
        {$user.email?.[0]?.toUpperCase() || 'U'}
      </div>
    </button>
    
    {#if dropdownOpen}
      <div class="dropdown-menu">
        <div class="user-info">
          <span class="user-email">{$user.email}</span>
        </div>
        <div class="dropdown-divider"></div>
        <button class="dropdown-item" on:click={() => {
            // Use direct navigation to profile without redirection risk
            try {
              fetch('/profile', { method: 'HEAD' }).then(response => {
                if (response.ok) {
                  window.location.href = '/profile';
                }
              });
            } catch (e) {
              // Fallback if fetch fails
              window.location.href = '/profile';  
            }
          }}>
          My Profile
        </button>
        <button class="dropdown-item" on:click={handleLogout}>
          Sign Out
        </button>
      </div>
    {/if}
  {:else}
    <button class="sign-in-button" on:click={goToLogin}>
      Sign In
    </button>
  {/if}
</div>

<style>
  .user-status {
    position: relative;
    display: inline-block;
  }
  
  .user-button {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
  }
  
  .user-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: #3b82f6;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 14px;
  }
  
  .dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    width: 200px;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 100;
    overflow: hidden;
    margin-top: 4px;
  }
  
  .user-info {
    padding: 12px 16px;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .user-email {
    font-size: 14px;
    color: #374151;
    word-break: break-all;
  }
  
  .dropdown-divider {
    height: 1px;
    background-color: #e5e7eb;
  }
  
  .dropdown-item {
    display: block;
    width: 100%;
    padding: 10px 16px;
    text-align: left;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
    color: #4b5563;
  }
  
  .dropdown-item:hover {
    background-color: #f3f4f6;
    color: #1f2937;
  }
  
  .sign-in-button {
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
  }
  
  .sign-in-button:hover {
    background-color: #2563eb;
  }
  
  .loading-indicator {
    display: flex;
    gap: 4px;
    align-items: center;
    justify-content: center;
    padding: 8px;
  }
  
  .loading-dot {
    width: 6px;
    height: 6px;
    background-color: #9ca3af;
    border-radius: 50%;
    animation: pulse 1.4s infinite ease-in-out;
  }
  
  .loading-dot:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  .loading-dot:nth-child(3) {
    animation-delay: 0.4s;
  }
  
  @keyframes pulse {
    0%, 100% {
      opacity: 0.3;
      transform: scale(0.8);
    }
    50% {
      opacity: 1;
      transform: scale(1.2);
    }
  }
</style>