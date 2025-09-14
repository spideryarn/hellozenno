import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const load: PageLoad = async ({ params, fetch, parent }) => {
    // Use target_language_code for API calls, mapping from the route parameter
    const { target_language_code, slug } = params;

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
        const { session } = await parent();

        return {
            phrase: phraseData,
            target_language_code,
            session,
        };
    } catch (err) {
        console.error("Error in load function:", err);
        throw error(500, "Failed to load phrase data");
    }
};
