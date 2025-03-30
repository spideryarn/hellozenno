import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, sourcedir_slug, sourcefile_slug } = params;

    try {
        // First fetch basic sourcefile data for the header
        const sourcefileResponse = await fetch(
            getApiUrl(
                RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_API,
                {
                    target_language_code: language_code,
                    sourcedir_slug,
                    sourcefile_slug,
                },
            ),
        );

        if (!sourcefileResponse.ok) {
            throw new Error(
                `Failed to fetch sourcefile: ${sourcefileResponse.statusText}`,
            );
        }

        const sourcefileData = await sourcefileResponse.json();

        // Fetch text data for metadata and basic info
        const textResponse = await fetch(
            getApiUrl(
                RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API,
                {
                    target_language_code: language_code,
                    sourcedir_slug,
                    sourcefile_slug,
                },
            ),
        );

        if (!textResponse.ok) {
            throw new Error(
                `Failed to fetch text data: ${textResponse.statusText}`,
            );
        }

        const textData = await textResponse.json();

        // Fetch words data specifically
        const wordsResponse = await fetch(
            getApiUrl(
                RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_WORDS_API,
                {
                    target_language_code: language_code,
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

        // Get language name from API response
        const language_name = sourcefileData.language_name ||
            textData.language_name;

        return {
            sourcefileData,
            textData,
            wordsData,
            language_code,
            language_name,
            sourcedir_slug,
            sourcefile_slug,
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
