import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { get_api_url, get_language_name } from "$lib/utils";

export const load: PageServerLoad = async ({ params, fetch, url }) => {
    const { language_code } = params;

    try {
        // Get sort parameter (default to 'alpha')
        const sort = url.searchParams.get("sort") || "alpha";

        // Use the get_api_url helper to generate the correct API URL
        const apiUrl = get_api_url(
            `lang/sourcedir/${language_code}/sources?sort=${sort}`,
        );

        // Fetch sources data from our new API endpoint
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
