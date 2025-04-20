import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch, locals: { supabase, session } }) => {
    const { target_language_code, sourcedir_slug, sourcefile_slug } = params;

    try {
        // Fetch words data with a single API call (which now includes all necessary data)
        const wordsResponse = await fetch(
            getApiUrl(
                RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_WORDS_API,
                {
                    target_language_code: target_language_code,
                    sourcedir_slug,
                    sourcefile_slug,
                },
            ),
        );

        if (!wordsResponse.ok) {
            throw new Error(
                `Failed to fetch words data: ${wordsResponse.statusText}`,
            );
        }

        const wordsData = await wordsResponse.json();

        // Empty placeholders as needed
        const phrasesData = { phrases: [] };
        
        // Extract available sourcedirs
        const available_sourcedirs = wordsData.available_sourcedirs || [];

        return {
            sourcefileData: wordsData, // Use wordsData for sourcefileData too
            textData: wordsData, // Use wordsData for textData too
            wordsData,
            phrasesData, // Added for consistency with other tabs
            target_language_code,
            language_name: wordsData.language_name || "",
            sourcedir_slug,
            sourcefile_slug,
            available_sourcedirs, // Add available sourcedirs for dropdown
            session, // Add session for auth data (not the supabase client)
        };
    } catch (err: unknown) {
        console.error("Error loading words data:", err);
        const errorMessage = err instanceof Error
            ? err.message
            : "Unknown error";
        throw error(404, {
            message: `Failed to load words data: ${errorMessage}`,
        });
    }
};
