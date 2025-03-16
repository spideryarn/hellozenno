<script lang="ts">
  import { authStore, authError, isLoading } from '../lib/auth-store';
  
  export let onSuccess: () => void = () => {};
  
  // Form state
  let email: string = '';
  let password: string = '';
  let formError: string = '';
  
  // Loading and error state from store
  $: loading = $isLoading;
  $: error = $authError;
  
  // Clear form error when auth error changes
  $: if (error) {
    formError = error;
    authStore.clearError();
  }
  
  // Handle form submission
  async function handleSubmit() {
    // Basic validation
    if (!email) {
      formError = 'Email is required';
      return;
    }
    
    if (!password) {
      formError = 'Password is required';
      return;
    }
    
    // Clear previous errors
    formError = '';
    
    // Sign in with email and password
    const result = await authStore.signIn(email, password);
    
    if (result.success) {
      console.log('Login successful');
      onSuccess();
    } else {
      formError = result.message || 'Login failed';
    }
  }
</script>

<div class="login-form">
  <h2>Sign In</h2>
  
  {#if formError}
    <div class="error-message">
      {formError}
    </div>
  {/if}
  
  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="email">Email</label>
      <input 
        type="email" 
        id="email" 
        bind:value={email} 
        placeholder="Email address" 
        autocomplete="email"
        disabled={loading}
      />
    </div>
    
    <div class="form-group">
      <label for="password">Password</label>
      <input 
        type="password" 
        id="password" 
        bind:value={password} 
        placeholder="Password" 
        autocomplete="current-password"
        disabled={loading}
      />
    </div>
    
    <button 
      type="submit" 
      class="button primary-button" 
      disabled={loading}
    >
      {loading ? 'Signing in...' : 'Sign In'}
    </button>
  </form>
</div>

<style>
  .login-form {
    max-width: 400px;
    margin: 0 auto;
    padding: 1.5rem;
    border-radius: 4px;
    background-color: #fff;
  }
  
  h2 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    text-align: center;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
  }
  
  button {
    width: 100%;
    padding: 0.75rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  button:hover:not(:disabled) {
    background-color: #2563eb;
  }
  
  button:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
  }
  
  .error-message {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background-color: #fee2e2;
    border-radius: 4px;
    color: #b91c1c;
  }
</style>