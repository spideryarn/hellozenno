import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const load: PageLoad = async ({ params, fetch }) => {
    // Use target_language_code for API calls, mapping from the route parameter language_code
    const { language_code, slug } = params;
    const target_language_code = language_code;

    try {
        // Use the typed API utility for better type safety and refactoring support
        const url = getApiUrl(RouteName.PHRASE_API_GET_PHRASE_METADATA_API, {
            target_language_code,
            slug,
        });

        const response = await fetch(url);

        if (!response.ok) {
            const errorData = await response.json();
            throw error(
                response.status,
                errorData.description ||
                    `Failed to load phrase with slug "${slug}"`,
            );
        }

        const phraseData = await response.json();

        return {
            phrase: phraseData,
            language_code,
        };
    } catch (err) {
        console.error("Error in load function:", err);
        throw error(500, "Failed to load phrase data");
    }
};
