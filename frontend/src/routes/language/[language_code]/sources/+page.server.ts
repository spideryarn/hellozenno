import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch, url }) => {
    const { language_code } = params;
    const target_language_code = language_code;

    try {
        // Get sort parameter (default to 'alpha')
        const sort = url.searchParams.get("sort") || "alpha";

        // Use the typed API utility for type-safe URL generation
        const apiUrl = getApiUrl(
            RouteName.SOURCEDIR_API_GET_SOURCEDIRS_FOR_LANGUAGE_API,
            { target_language_code },
        );

        // Fetch sources data from our API endpoint
        const sourcesResponse = await fetch(apiUrl);

        if (!sourcesResponse.ok) {
            throw new Error(
                `Failed to fetch sources: ${sourcesResponse.statusText}`,
            );
        }

        const sourcesData = await sourcesResponse.json();

        return {
            languageCode: sourcesData.language_code,
            languageName: sourcesData.language_name,
            sources: sourcesData.sources,
            currentSort: sort,
        };
    } catch (err) {
        console.error("Failed to load sources:", err);
        throw error(500, "Failed to load sources");
    }
};
