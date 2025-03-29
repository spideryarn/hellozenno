import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { get_api_url } from "$lib/utils";

export const load: PageServerLoad = async ({ params, fetch, url }) => {
    const { language_code, slug } = params;

    // Get query parameters for filtering
    const sourcefile = url.searchParams.get("sourcefile");
    const sourcedir = url.searchParams.get("sourcedir");

    // Build API path with query parameters
    let apiPath = `lang/${language_code}/flashcards/sentence/${slug}`;
    let queryParams = new URLSearchParams();

    if (sourcefile) {
        queryParams.append("sourcefile", sourcefile);
    } else if (sourcedir) {
        queryParams.append("sourcedir", sourcedir);
    }

    if (queryParams.toString()) {
        apiPath += `?${queryParams.toString()}`;
    }

    try {
        // Make the API request
        const response = await fetch(get_api_url(apiPath));

        if (!response.ok) {
            // If API returns an error, handle it
            const errorData = await response.json();
            throw error(
                response.status,
                errorData.error || "Failed to load sentence",
            );
        }

        // Return the sentence data
        const data = await response.json();
        return data;
    } catch (err) {
        console.error("Error fetching sentence data:", err);
        throw error(500, "Failed to load sentence data");
    }
};
