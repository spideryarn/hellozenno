import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { target_language_code, sourcedir_slug, sourcefile_slug } = params;

    try {
        // Fetch phrases data with a single API call (which now includes all necessary data)
        const phrasesResponse = await fetch(
            getApiUrl(
                RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_PHRASES_API,
                {
                    target_language_code: target_language_code,
                    sourcedir_slug,
                    sourcefile_slug,
                },
            ),
        );

        if (!phrasesResponse.ok) {
            throw new Error(
                `Failed to fetch phrases data: ${phrasesResponse.statusText}`,
            );
        }

        const phrasesData = await phrasesResponse.json();

        // Empty placeholders as needed
        const wordsData = { wordforms: [] };
        
        // Extract available sourcedirs
        const available_sourcedirs = phrasesData.available_sourcedirs || [];

        return {
            sourcefileData: phrasesData, // Use phrasesData for sourcefileData too
            textData: phrasesData, // Use phrasesData for textData too
            wordsData, // Added for consistency with other tabs
            phrasesData,
            target_language_code,
            language_name: phrasesData.language_name || "",
            sourcedir_slug,
            sourcefile_slug,
            available_sourcedirs, // Add available sourcedirs for dropdown
        };
    } catch (err: unknown) {
        console.error("Error loading phrases data:", err);
        const errorMessage = err instanceof Error
            ? err.message
            : "Unknown error";
        throw error(404, {
            message: `Failed to load phrases data: ${errorMessage}`,
        });
    }
};
