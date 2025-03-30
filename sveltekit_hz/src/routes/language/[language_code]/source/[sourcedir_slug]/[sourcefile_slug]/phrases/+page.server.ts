import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, sourcedir_slug, sourcefile_slug } = params;

    try {
        // First fetch basic sourcefile data for the header
        const sourcefileResponse = await fetch(
            getApiUrl(
                `/api/lang/sourcefile/${language_code}/${sourcedir_slug}/${sourcefile_slug}`,
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
                `/api/lang/sourcefile/${language_code}/${sourcedir_slug}/${sourcefile_slug}/text`,
            ),
        );

        if (!textResponse.ok) {
            throw new Error(
                `Failed to fetch text data: ${textResponse.statusText}`,
            );
        }

        const textData = await textResponse.json();

        // Fetch phrases data specifically
        const phrasesResponse = await fetch(
            getApiUrl(
                `/api/lang/sourcefile/${language_code}/${sourcedir_slug}/${sourcefile_slug}/phrases`,
            ),
        );

        if (!phrasesResponse.ok) {
            throw new Error(
                `Failed to fetch phrases data: ${phrasesResponse.statusText}`,
            );
        }

        const phrasesData = await phrasesResponse.json();

        // Get language name from API response
        const language_name = sourcefileData.language_name ||
            textData.language_name;

        return {
            sourcefileData,
            textData,
            phrasesData,
            language_code,
            language_name,
            sourcedir_slug,
            sourcefile_slug,
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
