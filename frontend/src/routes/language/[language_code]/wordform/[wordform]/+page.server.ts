import { error, redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getWordformWithSearch } from "$lib/api";
import type { SearchResults } from "$lib/types";

export const load: PageServerLoad = async ({ params }) => {
    const { language_code, wordform } = params;

    try {
        // Use our enhanced search function to handle various result types
        const data = await getWordformWithSearch(language_code, wordform);

        // Handle different response types based on status
        if (data.status === 'found') {
            // Direct wordform match found - return the data as is
            return {
                wordformData: data.data || data,
            };
        } else if (data.status === 'multiple_matches') {
            // Multiple matches found - redirect to search results page
            throw redirect(302, `/language/${language_code}/search/${encodeURIComponent(wordform)}`);
        } else if (data.status === 'redirect') {
            // Should redirect to another wordform
            throw redirect(302, `/language/${language_code}/wordform/${encodeURIComponent(data.redirect_to)}`);
        } else if (data.status === 'invalid') {
            // Invalid word - redirect to search to show the error
            throw redirect(302, `/language/${language_code}/search/${encodeURIComponent(wordform)}`);
        } else {
            // For older API responses that don't have a status field
            return {
                wordformData: data,
            };
        }
    } catch (err) {
        if (err instanceof Response && err.status === 302) {
            // This is our redirect, pass it through
            throw err;
        }
        
        console.error("Error loading wordform:", err);
        
        // If it's a 404, redirect to search page to show not found
        if (err instanceof Error && err.message.includes('404')) {
            throw redirect(302, `/language/${language_code}/search/${encodeURIComponent(wordform)}`);
        }
        
        throw error(
            500,
            `Failed to load wordform: ${
                err instanceof Error ? err.message : String(err)
            }`,
        );
    }
};
