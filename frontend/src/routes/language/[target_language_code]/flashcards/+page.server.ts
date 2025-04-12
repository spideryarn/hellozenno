import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch, url }) => {
    const { target_language_code } = params;

    // Get query parameters for filtering
    const sourcefile = url.searchParams.get("sourcefile");
    const sourcedir = url.searchParams.get("sourcedir");

    // Create query parameters
    let queryParams = new URLSearchParams();

    if (sourcefile) {
        queryParams.append("sourcefile", sourcefile);
    } else if (sourcedir) {
        queryParams.append("sourcedir", sourcedir);
    }

    try {
        // Generate type-safe API URL
        const apiUrl = getApiUrl(
            RouteName.FLASHCARD_API_FLASHCARD_LANDING_API,
            {
                target_language_code: target_language_code,
            },
        );

        // Add query parameters if any
        const fullUrl = queryParams.toString()
            ? `${apiUrl}?${queryParams.toString()}`
            : apiUrl;

        const response = await fetch(fullUrl);

        if (!response.ok) {
            const errorData = await response.json();
            throw error(
                response.status,
                errorData.error || "Failed to load flashcard data",
            );
        }

        const data = await response.json();
        return data;
    } catch (err) {
        console.error("Error fetching flashcard data:", err);
        throw error(500, "Failed to load flashcard data");
    }
};
