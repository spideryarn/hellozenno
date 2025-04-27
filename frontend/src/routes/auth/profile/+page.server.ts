import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
// Assume these helpers exist in api.ts or create them later
// They should accept supabaseClient as the first argument
import { getLanguages } from '$lib/api'; 
import { API_BASE_URL } from '$lib/config'; // Need base URL for placeholder
import { apiFetch } from '$lib/api'; // Import apiFetch for placeholder
import { RouteName } from '$lib/generated/routes'; // Import RouteName

// Get profile data from the API
async function getProfile(supabaseClient: any) { 
    try {
        // Using the correct PROFILE_API_GET_CURRENT_PROFILE_API
        const response = await apiFetch({
            supabaseClient: supabaseClient, // Pass the server client
            routeName: RouteName.PROFILE_API_GET_CURRENT_PROFILE_API, 
            params: {},
            options: { method: 'GET' }
        });
        
        // Extract and return just the profile object from the API response
        if (response && response.success && response.profile) {
            console.log("Successfully retrieved profile with target_language_code:", response.profile.target_language_code);
            return response.profile;
        } else {
            console.error("Unexpected profile API response format:", response);
            throw new Error("Invalid profile data format");
        }
    } catch (err: any) {
         console.error("getProfile failed:", err);
         // Throw SvelteKit error to be caught by the main load function's catch block
         throw error(err.status || 500, err.message || 'Failed to fetch profile');
    }
}

export const load: PageServerLoad = async ({ locals }) => {
    const { supabase, session, user } = locals;

    // Redirect to login if not authenticated
    if (!session || !user) {
        throw redirect(307, '/auth?next=/auth/profile');
    }

    try {
        // Fetch profile and available languages in parallel
        const [profileData, languagesData] = await Promise.all([
            getProfile(supabase),
            getLanguages(supabase) 
        ]);

        return {
            profile: profileData, 
            availableLanguages: languagesData || [],
            error: null // Explicitly return error as null on success
        };
    } catch (err: any) {
        console.error('Error loading profile page server data:', err);
        // Let SvelteKit handle the thrown error from getProfile or getLanguages
        // This will automatically render the nearest +error.svelte
        // No need to return an error object here, just re-throw
        throw err; 
    }
}; 