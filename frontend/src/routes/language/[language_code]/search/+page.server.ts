import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getSearchLandingData } from "$lib/api";

export const load: PageServerLoad = async ({ params, url, fetch }) => {
    const { language_code } = params;
    const query = url.searchParams.get("q");

    try {
        // Fetch landing page data from API
        const data = await getSearchLandingData(language_code);
        
        // Only fetch initial search results if there's a query
        let initialResult = null;
        if (query) {
            try {
                const response = await fetch(
                    `http://localhost:3000/api/lang/${language_code}/unified_search?q=${encodeURIComponent(query)}`
                );
                
                if (response.ok) {
                    initialResult = await response.json();
                    
                    // Handle redirect case at the server level
                    if (initialResult.status === 'redirect') {
                        return {
                            redirect: `/language/${language_code}/wordform/${initialResult.data.redirect_to}`
                        };
                    }
                }
            } catch (err) {
                console.error('Server-side search error:', err);
                // Let the client handle the error case
            }
        }

        return {
            language_code,
            langName: data.target_language_name,
            query: query || "",
            initialResult,
            has_query: !!query,
        };
    } catch (err) {
        console.error("Error loading search page data:", err);
        throw error(500, "Failed to load search page data");
    }
};
