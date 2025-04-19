<script lang="ts">
    import type { PageData } from './$types';
    import { goto, invalidateAll } from '$app/navigation';
    import type { SupabaseClient } from '@supabase/supabase-js';
    import { apiFetch } from '$lib/api';
    import { RouteName } from '$lib/generated/routes';

    export let data: PageData;
    let supabase: SupabaseClient | null = data.supabase;
    $: supabase = data.supabase;
    let session = data.session;
    $: session = data.session;

    let selectedLanguage: string | null | undefined = data.profile?.target_language_code;
    let isLoading = false;
    let errorMessage: string | null = data.error || null;
    let successMessage: string | null = null;

    $: {
        if (!session && typeof window !== 'undefined') {
            goto('/auth?next=/auth/profile');
        }
        if (data.profile?.target_language_code !== selectedLanguage) {
            selectedLanguage = data.profile?.target_language_code;
        }
        if (!data.error && errorMessage) {
            errorMessage = null;
        }
    }

    async function handleSaveProfile() {
        if (!supabase || !session) {
            errorMessage = 'Not authenticated.';
            return;
        }
        if (!selectedLanguage) {
            errorMessage = 'Please select a target language.';
            return;
        }

        isLoading = true;
        errorMessage = null;
        successMessage = null;

        try {
            const response = await apiFetch({
                supabaseClient: supabase,
                routeName: RouteName.PROFILE_API_UPDATE_PROFILE_API,
                params: {},
                options: {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ target_language_code: selectedLanguage })
                }
            });

            successMessage = 'Profile updated successfully!';
            await invalidateAll();

        } catch (err: any) {
            console.error('Error saving profile:', err);
            errorMessage = err.body?.message || err.message || 'Failed to save profile.';
        } finally {
            isLoading = false;
        }
    }

</script>

<h1>User Profile</h1>

{#if errorMessage}
    <div class="alert alert-danger" role="alert">
        {errorMessage}
    </div>
{/if}

{#if successMessage}
    <div class="alert alert-success" role="alert">
        {successMessage}
    </div>
{/if}

{#if data.profile}
    <p>Email: {data.profile.email || session?.user?.email}</p> 

    <form on:submit|preventDefault={handleSaveProfile}>
        <div class="mb-3">
            <label for="targetLanguage" class="form-label">Target Language</label>
            <select 
                id="targetLanguage" 
                class="form-select" 
                bind:value={selectedLanguage} 
                required
                disabled={isLoading}
            >
                <option value="" disabled selected>-- Select Language --</option>
                {#each data.availableLanguages || [] as lang}
                    <option value={lang.code}>{lang.name}</option>
                {/each}
            </select>
        </div>
        <button type="submit" class="btn btn-primary" disabled={isLoading}>
            {#if isLoading}Saving...{:else}Save Profile{/if}
        </button>
    </form>
{:else if !errorMessage}
    <p>Loading profile...</p>
{/if} 