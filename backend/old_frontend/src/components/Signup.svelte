<script lang="ts">
  import { authStore, authError, isLoading } from '../lib/auth-store';
  
  export let onSuccess: () => void = () => {};
  
  // Form state
  let email: string = '';
  let password: string = '';
  let confirmPassword: string = '';
  let formError: string = '';
  let successMessage: string = '';
  
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
    // Reset messages
    formError = '';
    successMessage = '';
    
    // Basic validation
    if (!email) {
      formError = 'Email is required';
      return;
    }
    
    if (!password) {
      formError = 'Password is required';
      return;
    }
    
    if (password.length < 6) {
      formError = 'Password must be at least 6 characters';
      return;
    }
    
    if (password !== confirmPassword) {
      formError = 'Passwords do not match';
      return;
    }
    
    // Clear previous errors
    formError = '';
    
    // Sign up with email and password
    const result = await authStore.signUp(email, password);
    
    if (result.success) {
      if (result.needsConfirmation) {
        successMessage = 'Please check your email for a confirmation link';
      } else {
        console.log('Signup successful');
        onSuccess();
      }
    } else {
      formError = result.message || 'Signup failed';
    }
  }
</script>

<div class="signup-form">
  <h2>Create Account</h2>
  
  {#if formError}
    <div class="error-message">
      {formError}
    </div>
  {/if}
  
  {#if successMessage}
    <div class="success-message">
      {successMessage}
    </div>
  {/if}
  
  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="signup-email">Email</label>
      <input 
        type="email" 
        id="signup-email" 
        bind:value={email} 
        placeholder="Email address" 
        autocomplete="email"
        disabled={loading || !!successMessage}
      />
    </div>
    
    <div class="form-group">
      <label for="signup-password">Password</label>
      <input 
        type="password" 
        id="signup-password" 
        bind:value={password} 
        placeholder="Password (min 6 characters)" 
        autocomplete="new-password"
        disabled={loading || !!successMessage}
      />
    </div>
    
    <div class="form-group">
      <label for="confirm-password">Confirm Password</label>
      <input 
        type="password" 
        id="confirm-password" 
        bind:value={confirmPassword} 
        placeholder="Confirm password" 
        autocomplete="new-password"
        disabled={loading || !!successMessage}
      />
    </div>
    
    <button 
      type="submit" 
      class="button primary-button" 
      disabled={loading || !!successMessage}
    >
      {loading ? 'Creating account...' : 'Create Account'}
    </button>
  </form>
</div>

<style>
  .signup-form {
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
  
  .success-message {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background-color: #d1fae5;
    border-radius: 4px;
    color: #047857;
  }
</style>