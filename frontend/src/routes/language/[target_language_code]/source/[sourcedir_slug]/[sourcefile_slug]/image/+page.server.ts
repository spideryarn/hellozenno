import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { target_language_code, sourcedir_slug, sourcefile_slug } = params;

    try {
        // Fetch text data for basic sourcefile info
        const textResponse = await fetch(
            getApiUrl(
                RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API,
                {
                    target_language_code: target_language_code,
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

        // Empty placeholders to maintain API compatibility
        const wordsData = { wordforms: [] };
        const phrasesData = { phrases: [] };
        const available_sourcedirs = textData.available_sourcedirs || [];

        return {
            sourcefileData: textData,
            textData,
            wordsData,
            phrasesData,
            target_language_code,
            language_name: textData.language_name || "",
            sourcedir_slug,
            sourcefile_slug,
            available_sourcedirs,
        };
    } catch (err: unknown) {
        console.error("Error loading sourcefile image:", err);
        const errorMessage = err instanceof Error
            ? err.message
            : "Unknown error";
        throw error(404, {
            message: `Failed to load sourcefile image: ${errorMessage}`,
        });
    }
};
