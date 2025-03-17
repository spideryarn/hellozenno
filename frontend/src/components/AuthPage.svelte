<script lang="ts">
  import { onMount } from 'svelte';
  import { isAuthenticated, authStore } from '../lib/auth-store';
  import Login from './Login.svelte';
  import Signup from './Signup.svelte';
  
  // Component props
  export let redirectUrl: string = '/';
  export let showSignup: boolean = false;
  
  // Component state
  let activeTab: 'login' | 'signup' = showSignup ? 'signup' : 'login';
  
  // Initialize auth on mount
  onMount(() => {
    authStore.init();
  });
  
  // Handle successful auth
  function handleAuthSuccess() {
    // Redirect to specified URL or home page
    let url = redirectUrl || '/';
    
    // Prevent trailing slashes on auth URLs, but preserve specific paths
    if (url.endsWith('/') && url !== '/') {
      url = url.slice(0, -1);
    }
    
    window.location.href = url;
  }
  
  // Change the active tab
  function setActiveTab(tab: 'login' | 'signup') {
    activeTab = tab;
  }
  
  // Redirect if already authenticated
  $: if ($isAuthenticated) {
    handleAuthSuccess();
  }
</script>

<div class="auth-container">
  <div class="auth-tabs">
    <button 
      class="tab-button {activeTab === 'login' ? 'active' : ''}" 
      on:click={() => setActiveTab('login')}
    >
      Sign In
    </button>
    <button 
      class="tab-button {activeTab === 'signup' ? 'active' : ''}" 
      on:click={() => setActiveTab('signup')}
    >
      Create Account
    </button>
  </div>
  
  <div class="auth-content">
    {#if activeTab === 'login'}
      <Login onSuccess={handleAuthSuccess} />
    {:else}
      <Signup onSuccess={() => setActiveTab('login')} />
    {/if}
  </div>
</div>

<style>
  .auth-container {
    max-width: 500px;
    margin: 2rem auto;
    padding: 1rem;
    background-color: #f9fafb;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .auth-tabs {
    display: flex;
    margin-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .tab-button {
    flex: 1;
    padding: 0.75rem;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 1rem;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .tab-button.active {
    color: #3b82f6;
    border-bottom-color: #3b82f6;
  }
  
  .tab-button:hover:not(.active) {
    color: #4b5563;
    background-color: #f3f4f6;
  }
  
  .auth-content {
    padding: 1rem 0;
  }
</style>