import { error, redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getWordformWithSearch } from "$lib/api";
import type { SearchResult } from "$lib/types";

export const load: PageServerLoad = async ({ params, locals }) => {
    const { target_language_code, wordform } = params;
    const { supabase, session } = locals;

    try {
        // Pass the access token from locals.session to avoid double getSession() calls
        const apiResponse = await getWordformWithSearch(
            supabase, 
            target_language_code, 
            wordform,
            session?.access_token
        );
        
        if (apiResponse.status === 'found') {
            if (!apiResponse.data || !apiResponse.data.wordform_metadata || !apiResponse.data.wordform_metadata.wordform) {
                console.error("Search 'found' status received, but wordform_metadata is missing in data:", apiResponse);
                throw error(500, "Search error: Missing wordform data for 'found' status.");
            }
            throw redirect(302, `/language/${target_language_code}/wordform/${encodeURIComponent(apiResponse.data.wordform_metadata.wordform)}`);
        } else if (apiResponse.status === 'redirect') {
            if (!apiResponse.data || !apiResponse.data.redirect_to) {
                console.error("Search 'redirect' status received, but redirect_to field is missing in data:", apiResponse);
                throw error(500, "Search redirect error: Missing redirect target.");
            }
            throw redirect(302, `/language/${target_language_code}/wordform/${encodeURIComponent(apiResponse.data.redirect_to)}`);
        } else if (apiResponse.status === 'multiple_matches' || apiResponse.status === 'invalid'){
            // For these statuses, the API response's 'data' field contains the details.
            // We need to construct the SearchResult object for the page.
            const pageSearchResults: SearchResult = {
                status: apiResponse.status,
                query: apiResponse.data?.search_term || wordform, // Fallback to wordform from params if not in data
                target_language_code: apiResponse.data?.target_language_code || target_language_code,
                target_language_name: apiResponse.data?.target_language_name || "", // Page will try to fill this from layout
                data: apiResponse.data, // The actual payload with matches or error details
                error: apiResponse.status === 'invalid' ? (apiResponse.data?.error || "Invalid word") : undefined
            };
            return {
                searchResults: pageSearchResults
            };
        } else {
            console.warn("Unexpected search status:", apiResponse.status, apiResponse);
            const errorSearchResults: SearchResult = {
                status: 'error',
                query: wordform,
                target_language_code,
                target_language_name: "",
                data: {},
                error: "Unexpected search result status from API."
            };
            return {
                searchResults: errorSearchResults
            };
        }
    } catch (err) {
        if (err instanceof Response && err.status === 302) {
            throw err;
        }
        console.error(`Error on search page for '${wordform}':`, err);
        const fallbackErrorResult: SearchResult = {
            status: 'error',
            query: wordform,
            target_language_code: target_language_code,
            target_language_name: "",
            data: {},
            error: err instanceof Error ? err.message : "Failed to search for word"
        };
        return {
            searchResults: fallbackErrorResult
        };
    }
};
