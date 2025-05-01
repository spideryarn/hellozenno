import { error, redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getWordformWithSearch } from "$lib/api";
import type { SearchResult } from "$lib/types";

export const load: PageServerLoad = async ({ params, locals }) => {
    const { target_language_code, wordform } = params;
    const { supabase, session } = locals;

    try {
        // Use our enhanced search function to handle various result types
        
        // Set a reasonable timeout for server-side rendering
        // This is important since we now wait for wordform generation to complete
        const data = await getWordformWithSearch(
            supabase,
            target_language_code,
            wordform,
            session?.access_token ?? null
        );

        // Check if authentication is required for generation and propagate the 401 status code
        if (data.authentication_required_for_generation) {
            throw error(401, {
                message: data.description || 'Authentication required to generate wordform data',
                body: data // Include original error data for the error page
            });
        }

        // Handle different response types based on status
        if (data.status === 'found') {
            // Direct wordform match found - return the data as is
            // This now includes newly generated wordforms too
            console.log(`Wordform found: ${wordform}`);
            return {
                session,
                wordformData: data.data || data,
            };
        } else if (data.status === 'multiple_matches') {
            // Multiple matches found - redirect to search results page
            console.log(`Multiple matches found for: ${wordform}, redirecting to search`);
            throw redirect(302, `/language/${target_language_code}/search/${encodeURIComponent(wordform)}`);
        } else if (data.status === 'redirect') {
            // Should redirect to another wordform
            // This is now only used as a fallback
            console.log(`Redirecting to: ${data.redirect_to}`);
            throw redirect(302, `/language/${target_language_code}/wordform/${encodeURIComponent(data.redirect_to)}`);
        } else if (data.status === 'invalid') {
            // Invalid word - redirect to search to show the error
            console.log(`Invalid word: ${wordform}, redirecting to search`);
            throw redirect(302, `/language/${target_language_code}/search/${encodeURIComponent(wordform)}`);
        } else {
            // For older API responses that don't have a status field
            // console.log(`No status field, using data as is:`, data);
            return {
                session,
                wordformData: data,
            };
        }
    } catch (err: any) {
        if (err.status === 401) {
            // Already handled above, just re-throw
            throw err;
        }

        if (err instanceof Response && err.status === 302) {
            // This is our redirect, pass it through
            throw err;
        }
        
        console.error("Error loading wordform:", err);
        
        // Handle timeout errors specifically
        if (err instanceof Error && err.message.includes('timed out')) {
            // If we time out during wordform generation, still return a loading state
            // The client-side JS will retry fetching the data
            console.log("Request timed out, returning empty wordform data for client-side handling");
            return {
                session,
                wordformData: null,
            };
        }
        
        // If it's a 404, redirect to search page to show not found
        if (err instanceof Error && err.message.includes('404')) {
            throw redirect(302, `/language/${target_language_code}/search/${encodeURIComponent(wordform)}`);
        }
        
        // Throw SvelteKit error for unexpected issues
        throw error(
            err.status || 500, // Use status from error if available
            {
                message: `Failed to load wordform: ${err.message || String(err)}`,
                // If there's a body from the API, include it
                ...(err.body ? { body: err.body } : {})
            }
        );
    }
};
