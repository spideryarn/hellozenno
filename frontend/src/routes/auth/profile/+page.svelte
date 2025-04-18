<script lang="ts">
    import type { PageData } from './$types';
    import { fetchAuthenticated } from '$lib/apiClient';
    import { user } from '$lib/stores/authStore';
    import { goto } from '$app/navigation';
    import { invalidateAll } from '$app/navigation';

    export let data: PageData;

    let selectedLanguage: string | null | undefined = data.profile?.target_language_code;
    let isLoading = false;
    let errorMessage: string | null = null;
    let successMessage: string | null = null;

    // Redirect if load function encountered an error or user became unauthenticated
    $: {
        if (data.error && typeof window !== 'undefined') {
            // Handle error from load function (e.g., show message, redirect)
            console.error("Load error:", data.error);
            alert("Could not load profile data.");
            // Optionally redirect to home or another page
            // goto('/');
        } else if (!$user && typeof window !== 'undefined') {
            // User logged out while on the page
            goto('/auth?next=/profile');
        }
        // Update local state if profile data changes (e.g., after save)
        selectedLanguage = data.profile?.target_language_code;
    }

    async function saveProfile() {
        isLoading = true;
        errorMessage = null;
        successMessage = null;

        try {
            const response = await fetchAuthenticated('/api/profile', {
                method: 'PUT',
                body: JSON.stringify({ 
                    target_language_code: selectedLanguage 
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Failed to save profile: ${response.statusText}`);
            }

            successMessage = 'Profile saved successfully!';
            // Re-run load function to get fresh data after saving
            await invalidateAll(); 

        } catch (error) {
            console.error('Error saving profile:', error);
            errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
        } finally {
            isLoading = false;
            // Clear success message after a delay
            if (successMessage) {
                setTimeout(() => successMessage = null, 3000);
            }
        }
    }

</script>

<div class="container mt-4">
    {#if data.error}
        <div class="alert alert-danger">{data.error}</div>
    {:else if data.profile}
        <h1>User Profile</h1>
        <p>Email: {$user?.email}</p> 

        <form on:submit|preventDefault={saveProfile}>
            <div class="mb-3">
                <label for="targetLanguage" class="form-label">Preferred Target Language</label>
                <select 
                    id="targetLanguage"
                    class="form-select"
                    bind:value={selectedLanguage}
                    disabled={isLoading}
                >
                    <option value={null}>-- Select a Language --</option>
                    {#each data.availableLanguages || [] as lang}
                        <option value={lang.code}>{lang.name}</option>
                    {/each}
                </select>
                <div class="form-text">Select the language you are primarily learning.</div>
            </div>

            {#if errorMessage}
                <div class="alert alert-danger">{errorMessage}</div>
            {/if}
            {#if successMessage}
                <div class="alert alert-success">{successMessage}</div>
            {/if}

            <button type="submit" class="btn btn-primary" disabled={isLoading}>
                {#if isLoading}Saving...{:else}Save Profile{/if}
            </button>
        </form>
    {:else}
        <p>Loading profile...</p> 
    {/if}
</div> 