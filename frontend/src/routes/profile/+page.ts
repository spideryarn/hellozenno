import type { PageLoad } from './$types';
import { fetchAuthenticated } from '$lib/apiClient';
import { user } from '$lib/stores/authStore';
import { get } from 'svelte/store';
import { redirect } from '@sveltejs/kit';

export const load: PageLoad = async ({ fetch: sveltekitFetch }) => {
    // Ensure user is logged in client-side before proceeding
    // We rely on the authStore being initialized
    if (!get(user)) {
        // Redirect to login, adding the current page as 'next'
        throw redirect(307, '/auth?next=/profile'); 
    }

    try {
        // Fetch profile data and available languages in parallel
        // fetchAuthenticated uses the global fetch, which SvelteKit patches client-side
        const [profileResponse, languagesResponse] = await Promise.all([
            fetchAuthenticated('/api/profile'), // Don't pass sveltekitFetch here
            fetchAuthenticated('/api/lang/languages') // Don't pass sveltekitFetch here
        ]);

        if (!profileResponse.ok) {
            throw new Error(`Failed to fetch profile: ${profileResponse.statusText}`);
        }
        if (!languagesResponse.ok) {
            throw new Error(`Failed to fetch languages: ${languagesResponse.statusText}`);
        }

        const profileData = await profileResponse.json();
        const languagesData = await languagesResponse.json();

        return {
            profile: profileData,
            availableLanguages: languagesData.languages || [] // Assuming API returns { languages: [...] }
        };
    } catch (error) {
        console.error('Error loading profile page data:', error);
        return {
            error: 'Could not load profile data. Please try again later.'
        };
    }
};

// Ensure this load function runs only on the client, 
// as we need access to the auth token from the store via fetchAuthenticated.
export const ssr = false; 