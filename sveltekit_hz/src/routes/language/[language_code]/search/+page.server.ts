import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getSearchLandingData } from "$lib/api";

export const load: PageServerLoad = async ({ params, url }) => {
    const { language_code } = params;
    const query = url.searchParams.get("q");

    try {
        // Fetch landing page data from API
        const data = await getSearchLandingData(language_code);

        return {
            target_language_code: language_code,
            target_language_name: data.target_language_name,
            query: query || "",
            has_query: !!query,
        };
    } catch (err) {
        console.error("Error loading search page data:", err);
        throw error(500, "Failed to load search page data");
    }
};
