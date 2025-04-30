import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getLemmaMetadata } from "$lib/api"; // Import the new helper

export const load: PageServerLoad = async ({ params, locals }) => {
    const { target_language_code, lemma } = params;

    // Get the supabase client and session from locals (populated by hooks)
    const { supabase, session } = locals;

    try {
        // Call the helper function, passing the server client instance
        const lemmaResult = await getLemmaMetadata(supabase, target_language_code, lemma);

        // Check if authentication is required for generation and propagate the 401 status code
        if (lemmaResult.authentication_required_for_generation) {
            throw error(401, {
                message: lemmaResult.description || 'Authentication required to generate lemma data',
                body: lemmaResult // Include original error data for the error page
            });
        }

        // Only reach here for successful results
        return {
            session: session, // Pass session for UI state
            lemmaResult: lemmaResult, // Pass the result (data or error body)
            target_language_code: target_language_code, // Keep passing this for clarity
            lemma: lemma, // Keep passing this for clarity
        };

    } catch (err: any) {
        // If the error already has status and body, pass it through
        if (err.status === 401) {
            // Already handled above, just re-throw
            throw err;
        }
        
        // Handle other errors from getLemmaMetadata
        console.error("Error loading lemma in +page.server.ts:", err);
        // Throw SvelteKit error for unexpected issues
        throw error(
            err.status || 500, // Use status from error if available
            {
                message: `Failed to load lemma: ${err.message || String(err)}`,
                // If there's a body from the API, include it
                ...(err.body ? { body: err.body } : {})
            }
        );
    }
};
