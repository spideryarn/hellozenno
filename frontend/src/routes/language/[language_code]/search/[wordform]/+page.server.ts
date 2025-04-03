import { error, redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { searchWord, getWordformWithSearch } from "$lib/api";
import type { SearchResults } from "$lib/types";

export const load: PageServerLoad = async ({ params }) => {
    const { language_code, wordform } = params;

    try {
        // First try the legacy search API for compatibility
        const simpleSearchData = await searchWord(language_code, wordform);

        // If we have a redirect URL, use it immediately
        if (simpleSearchData.redirect_url) {
            throw redirect(302, simpleSearchData.redirect_url);
        }

        // If we get here, we need to try the more advanced search
        const searchResults = await getWordformWithSearch(language_code, wordform);
        
        // Based on status, decide what to do
        if (searchResults.status === 'found') {
            // We found the wordform directly, return it for display
            return {
                searchResults
            };
        } else if (searchResults.status === 'redirect') {
            // Redirect to the appropriate wordform
            throw redirect(302, `/language/${language_code}/wordform/${encodeURIComponent(searchResults.redirect_to)}`);
        } else {
            // Multiple matches or invalid word case
            return {
                searchResults
            };
        }
    } catch (err) {
        // Handle redirects specially
        if (err instanceof Response && err.status === 302) {
            // This is our redirect, pass it through
            throw err;
        }

        console.error("Error searching word:", err);
        
        // If this is a 404, it means the word wasn't found
        // We'll return a specific error for displaying to the user
        if (err instanceof Error && err.message.includes('404')) {
            return {
                searchResults: {
                    status: 'invalid',
                    target_language_code: language_code,
                    target_language_name: "", // Will be filled client-side
                    search_term: wordform,
                    error: "Word not found"
                } as SearchResults
            };
        }
        
        throw error(500, "Failed to search for word");
    }
};
