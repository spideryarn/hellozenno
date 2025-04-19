import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
// Remove API_BASE_URL if no longer needed directly
// import { API_BASE_URL } from "$lib/config"; 
import { getLemmaMetadata } from "$lib/api"; // Import the new helper

export const load: PageServerLoad = async ({ params, locals }) => {
    const { target_language_code, lemma } = params;

    // Get the supabase client and session from locals (populated by hooks)
    const { supabase, session } = locals;

    try {
        // Call the helper function, passing the server client instance
        const lemmaResult = await getLemmaMetadata(supabase, target_language_code, lemma);

        // The helper function returns the data directly if successful,
        // or returns the specific error body for 401/404 cases.
        // We just need to pass this result to the page.
        return {
            session: session, // Pass session for UI state
            lemmaResult: lemmaResult, // Pass the result (data or error body)
            // No need for separate authError, target_language_code, etc. 
            // if they are included within lemmaResult (either in lemma_metadata or error body)
            // Verify the structure returned by getLemmaMetadata in both success/error cases.
            // If needed, extract specific fields here, e.g.:
            target_language_code: target_language_code, // Keep passing this for clarity
            lemma: lemma, // Keep passing this for clarity
        };

    } catch (err: any) {
        // Catch errors *thrown* by getLemmaMetadata (i.e., not the handled 401/404)
        console.error("Error loading lemma in +page.server.ts:", err);
        // Throw SvelteKit error for unexpected issues
        throw error(
            err.status || 500, // Use status from error if available
            `Failed to load lemma: ${err.message || String(err)}`,
        );
    }
};
