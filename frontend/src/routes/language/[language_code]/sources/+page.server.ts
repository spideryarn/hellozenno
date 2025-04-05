import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch, url, depends }) => {
    // Register dependency on the query parameters (specifically the sort parameter)
    depends('url:sort');
    
    const { language_code } = params;
    const target_language_code = language_code;

    try {
        // Get sort parameter (default to 'date')
        const sort = url.searchParams.get("sort") || "date";
        console.log('Server load - URL sort parameter:', sort);

        // Use the typed API utility for type-safe URL generation
        const apiUrl = getApiUrl(
            RouteName.SOURCEDIR_API_GET_SOURCEDIRS_FOR_LANGUAGE_API,
            { target_language_code },
        );
        
        // Add the sort parameter to the API URL
        const apiUrlWithParams = `${apiUrl}?sort=${sort}`;
        console.log('Server load - API URL with params:', apiUrlWithParams);

        // Fetch sources data from our API endpoint
        const sourcesResponse = await fetch(apiUrlWithParams, {
            // Ensure no caching
            headers: {
                'Cache-Control': 'no-cache'
            }
        });

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
