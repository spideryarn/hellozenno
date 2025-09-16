<script lang="ts">
    import type { PageData } from './$types';
    import { goto, invalidateAll } from '$app/navigation';
    import type { SupabaseClient } from '@supabase/supabase-js';
    import { apiFetch } from '$lib/api';
    import { RouteName } from '$lib/generated/routes';
    import { SITE_NAME } from '$lib/config';
    import Card from '$lib/components/Card.svelte';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
    import Alert from '$lib/components/Alert.svelte';
    import Globe from 'phosphor-svelte/lib/Globe';
    import User from 'phosphor-svelte/lib/User';
    import ShieldCheck from 'phosphor-svelte/lib/ShieldCheck';
    import FloppyDisk from 'phosphor-svelte/lib/FloppyDisk';
    import CaretLeft from 'phosphor-svelte/lib/CaretLeft';

    export let data: PageData;
    let supabase: SupabaseClient | null = data.supabase;
    $: supabase = data.supabase;
    let session = data.session;
    $: session = data.session;

    // Initialize with profile value or empty string to match default option
    let selectedLanguage: string | null | undefined = data.profile?.target_language_code || "";
    let isLoading = false;
    let errorMessage: string | null = data.error || null;
    let successMessage: string | null = null;

    $: {
        if (!session && typeof window !== 'undefined') {
            goto('/auth?next=/auth/profile');
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

    // Find language name from code
    function getLanguageName(code: string): string | null {
        const language = data.availableLanguages?.find(lang => lang.code === code);
        return language ? language.name : null;
    }

    // Determine if we should show the back button and with what text
    function getBackButtonInfo() {
        const savedLanguageCode = data.profile?.target_language_code;
        
        // If no language saved or selected is empty, show "Back to languages"
        if (!savedLanguageCode || !selectedLanguage) {
            return { show: true, text: 'Back to languages', link: '/languages' };
        }
        
        // If saved language matches selected language, show "Back to TARGET_LANGUAGE_NAME"
        if (savedLanguageCode === selectedLanguage) {
            const languageName = getLanguageName(savedLanguageCode);
            return { 
                show: true, 
                text: `Back to ${languageName}`, 
                link: `/language/${savedLanguageCode}/sources`
            };
        }
        
        // Otherwise, don't show a button
        return { show: false };
    }
</script>

<svelte:head>
    <title>Profile | {SITE_NAME}</title>
</svelte:head>

<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-lg-8 col-md-10">
            <Card>
                <div slot="title" class="d-flex align-items-center">
                    <User size={24} weight="fill" class="me-2 text-primary-green" />
                    <h1 class="h3 mb-0">User Profile</h1>
                    {#if (data as any)?.is_admin}
                        <span class="badge rounded-pill ms-3" style="background-color: var(--hz-color-primary-green); color: #111;"> 
                            <ShieldCheck size={16} weight="fill" class="me-1" /> Admin
                        </span>
                    {/if}
                </div>
                
                {#if errorMessage}
                    <Alert type="danger" className="mt-3">{errorMessage}</Alert>
                {/if}

                {#if successMessage}
                    <Alert type="success" className="mt-3">{successMessage}</Alert>
                {/if}

                {#if data.profile}
                    <div class="mb-4 mt-3">
                        <div class="d-flex align-items-center">
                            <div class="p-3 rounded-circle me-3" style="background-color: var(--hz-color-surface);">
                                <User size={20} weight="fill" class="text-primary-green" />
                            </div>
                            <div>
                                <div class="text-secondary small">Email</div>
                                <div>{data.profile.email || session?.user?.email}</div>
                            </div>
                        </div>
                    </div>

                    <form on:submit|preventDefault={handleSaveProfile} class="mb-4">
                        <div class="mb-4">
                            <label for="targetLanguage" class="form-label d-flex align-items-center">
                                <Globe size={20} weight="fill" class="me-2 text-primary-green" />
                                <span>Target Language</span>
                            </label>
                            <select 
                                id="targetLanguage" 
                                class="form-select" 
                                bind:value={selectedLanguage} 
                                disabled={isLoading}
                            >
                                <option value="" disabled selected>-- Select Language --</option>
                                {#each data.availableLanguages || [] as lang}
                                    <option value={lang.code}>{lang.name}</option>
                                {/each}
                            </select>
                            <div class="form-text">This will be your default language for study</div>
                        </div>
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <button type="submit" class="btn btn-primary" disabled={isLoading}>
                                {#if isLoading}
                                    <LoadingSpinner size="sm" className="me-2" />
                                    <span>Saving...</span>
                                {:else}
                                    <FloppyDisk size={18} weight="fill" class="me-2" />
                                    <span>Save Profile</span>
                                {/if}
                            </button>
                            
                            {#if getBackButtonInfo().show}
                                <a 
                                    href={getBackButtonInfo().link} 
                                    class="btn btn-secondary text-on-light"
                                >
                                    <CaretLeft size={18} weight="fill" class="me-1" />
                                    {getBackButtonInfo().text}
                                </a>
                            {/if}
                        </div>
                    </form>
                {:else if !errorMessage}
                    <div class="text-center py-4">
                        <LoadingSpinner size="lg" />
                        <p class="mt-3">Loading profile...</p>
                    </div>
                {/if}
            </Card>
        </div>
    </div>
</div>