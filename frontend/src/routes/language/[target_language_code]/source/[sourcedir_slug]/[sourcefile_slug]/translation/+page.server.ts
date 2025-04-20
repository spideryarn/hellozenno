import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch, locals: { supabase, session } }) => {
    const { target_language_code, sourcedir_slug, sourcefile_slug } = params;

    try {
        // Fetch sourcefile translation data with a single API call
        const translationResponse = await fetch(
            getApiUrl(
                RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TRANSLATION_API,
                {
                    target_language_code: target_language_code,
                    sourcedir_slug,
                    sourcefile_slug,
                },
            ),
        );

        if (!translationResponse.ok) {
            throw new Error(
                `Failed to fetch translation data: ${translationResponse.statusText}`,
            );
        }

        const translationData = await translationResponse.json();

        // Empty placeholders for TypeScript - these aren't needed but kept for compatibility
        const wordsData = { wordforms: [] };
        const phrasesData = { phrases: [] };
        
        // Extract available sourcedirs
        const available_sourcedirs = translationData.available_sourcedirs || [];

        // Use translationData for everything since it contains all the necessary info
        return {
            sourcefileData: translationData,
            textData: translationData,
            wordsData,
            phrasesData,
            target_language_code,
            language_name: translationData.language_name,
            sourcedir_slug,
            sourcefile_slug,
            available_sourcedirs, // Add available sourcedirs for dropdown
            session, // Add session for auth data (not the supabase client)
        };
    } catch (err: unknown) {
        console.error("Error loading sourcefile:", err);
        const errorMessage = err instanceof Error
            ? err.message
            : "Unknown error";
        throw error(404, {
            message: `Failed to load sourcefile: ${errorMessage}`,
        });
    }
}; 