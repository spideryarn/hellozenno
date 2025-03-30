import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, sourcedir_slug, sourcefile_slug } = params;

    try {
        // Fetch sourcefile data
        const sourcfileResponse = await fetch(
            getApiUrl(
                `/api/lang/sourcefile/${language_code}/${sourcedir_slug}/${sourcefile_slug}`,
            ),
        );

        if (!sourcfileResponse.ok) {
            throw new Error(
                `Failed to fetch sourcefile: ${sourcfileResponse.statusText}`,
            );
        }

        const sourcefileData = await sourcfileResponse.json();

        // Now get the text data
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

        // Also fetch words and phrases count data
        const wordsResponse = await fetch(
            getApiUrl(
                `/api/lang/sourcefile/${language_code}/${sourcedir_slug}/${sourcefile_slug}/words`,
            ),
        );

        const phrasesResponse = await fetch(
            getApiUrl(
                `/api/lang/sourcefile/${language_code}/${sourcedir_slug}/${sourcefile_slug}/phrases`,
            ),
        );

        const wordsData = wordsResponse.ok
            ? await wordsResponse.json()
            : { wordforms: [] };
        const phrasesData = phrasesResponse.ok
            ? await phrasesResponse.json()
            : { phrases: [] };

        // Get language name from API response
        const language_name = sourcefileData.language_name ||
            textData.language_name;

        return {
            sourcefileData,
            textData,
            wordsData,
            phrasesData,
            language_code,
            language_name,
            sourcedir_slug,
            sourcefile_slug,
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
