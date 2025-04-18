<script lang="ts">
    import type { PageData } from './$types';
    import { supabase } from '$lib/supabaseClient';
    import { goto } from '$app/navigation';
    import { AuthApiError } from '@supabase/supabase-js';

    export let data: PageData;

    let email = '';
    let password = '';
    let confirmPassword = '';
    let errorMessage: string | null = null;
    let loading = false;

    async function handleLogin() {
        loading = true;
        errorMessage = null;
        try {
            const { error } = await supabase.auth.signInWithPassword({
                email,
                password,
            });

            if (error) {
                if (error instanceof AuthApiError && error.status === 400) {
                    errorMessage = 'Invalid credentials';
                } else {
                    errorMessage = error.message;
                }
                console.error('Login error:', error);
            } else {
                // Login successful, redirect
                await goto(data.nextUrl);
            }
        } catch (err: any) {
            errorMessage = err.message || 'An unexpected error occurred during login.';
            console.error('Unexpected login error:', err);
        } finally {
            loading = false;
        }
    }

    async function handleSignup() {
        if (password !== confirmPassword) {
            errorMessage = 'Passwords do not match';
            return;
        }
        loading = true;
        errorMessage = null;
        try {
            const { error } = await supabase.auth.signUp({
                email,
                password,
            });

            if (error) {
                 if (error instanceof AuthApiError && error.status === 400) {
                    errorMessage = 'Invalid email or password (must be at least 6 characters).';
                 } else if (error instanceof AuthApiError && error.status === 429) {
                    errorMessage = 'Too many signup attempts. Please try again later.';
                 } else if (error instanceof AuthApiError && error.status === 422) {
                     errorMessage = 'User already exists.'; // More specific handling might be needed
                 } else {
                    errorMessage = error.message;
                }
                console.error('Signup error:', error);
            } else {
                // Signup successful (Supabase may require email confirmation)
                // For now, redirect immediately. Consider adding a message about email confirmation.
                alert('Signup successful! Check your email for confirmation if required.');
                await goto(data.nextUrl);
            }
        } catch (err: any) {
            errorMessage = err.message || 'An unexpected error occurred during signup.';
            console.error('Unexpected signup error:', err);
        } finally {
            loading = false;
        }
    }

</script>

<h1>Authentication</h1>

<p>(Attempting redirect to: {data.nextUrl})</p>

{#if errorMessage}
    <p class="error">Error: {errorMessage}</p>
{/if}

<div class="auth-container">
    <div class="login-section">
        <h2>Login</h2>
        <form on:submit|preventDefault={handleLogin}>
            <label>
                Email:
                <input type="email" bind:value={email} required disabled={loading} />
            </label>
            <label>
                Password:
                <input type="password" bind:value={password} required disabled={loading} />
            </label>
            <button type="submit" disabled={loading}>
                {#if loading}Logging in...{:else}Login{/if}
            </button>
        </form>
    </div>

    <div class="signup-section">
        <h2>Sign Up</h2>
        <form on:submit|preventDefault={handleSignup}>
            <label>
                Email:
                <input type="email" bind:value={email} required disabled={loading} />
            </label>
            <label>
                Password:
                <input type="password" bind:value={password} required minlength="6" disabled={loading} />
            </label>
             <label>
                Confirm Password:
                <input type="password" bind:value={confirmPassword} required minlength="6" disabled={loading} />
            </label>
            <button type="submit" disabled={loading}>
                 {#if loading}Signing up...{:else}Sign Up{/if}
            </button>
        </form>
    </div>
</div>

<style>
    .auth-container {
        display: flex;
        gap: 2rem;
        margin-top: 1rem;
    }
    .login-section, .signup-section {
        border: 1px solid #ccc;
        padding: 1rem;
        flex: 1;
    }
    label {
        display: block;
        margin-bottom: 0.5rem;
    }
    input {
        width: 100%;
        margin-top: 0.2rem;
    }
    button {
         margin-top: 1rem;
    }
    .error {
        color: red;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style> 