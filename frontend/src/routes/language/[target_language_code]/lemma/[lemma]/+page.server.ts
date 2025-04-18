import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { API_BASE_URL } from "$lib/config";
import { goto } from "$app/navigation"; // Import goto for potential redirect

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { target_language_code, lemma } = params;

    try {
        // URL encode the lemma parameter to handle non-Latin characters properly
        const encodedLemma = encodeURIComponent(lemma);

        // Fetch lemma metadata from API
        const response = await fetch(
            `${API_BASE_URL}/api/lang/lemma/${target_language_code}/lemma/${encodedLemma}/metadata`,
        );

        const data = await response.json();

        // Check for specific 401 error indicating auth needed for generation
        if (response.status === 401 && data?.authentication_required_for_generation) {
            // Pass the error details and partial data (if any) to the page
            return {
                lemmaData: data.partial_lemma_metadata || { lemma: lemma }, // Use partial or minimal data
                authError: data.description || "Authentication required to generate full details.",
                metadata: data.metadata, // Include metadata if present in error response
                target_language_code: target_language_code, // Ensure these are passed too
                target_language_name: data.target_language_name,
            };
        }

        if (!response.ok) {
            // Throw generic error for other non-ok responses
            throw error(
                response.status,
                `Error fetching lemma data: ${data?.error || response.statusText}`,
            );
        }

        // Successful response
        return {
            lemmaData: data, // Contains lemma_metadata, metadata, etc.
            authError: null,
        };
    } catch (err) {
        console.error("Error loading lemma:", err);
        // Don't re-throw errors already handled by SvelteKit's error function
        if (err instanceof Object && 'status' in err) { throw err; }
        // Throw a generic 500 for other unexpected errors
        throw error(
            500,
            `Failed to load lemma: ${
                err instanceof Error ? err.message : String(err)
            }`,
        );
    }
};
