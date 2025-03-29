import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { get_api_url } from "$lib/utils";

export const load: PageServerLoad = async ({ params, fetch, url }) => {
    const { language_code } = params;

    // Get query parameters for filtering
    const sourcefile = url.searchParams.get("sourcefile");
    const sourcedir = url.searchParams.get("sourcedir");

    // Build URL for API fetch with appropriate query parameters
    let apiPath = `lang/${language_code}/flashcards/landing`;

    if (sourcefile) {
        apiPath += `?sourcefile=${sourcefile}`;
    } else if (sourcedir) {
        apiPath += `?sourcedir=${sourcedir}`;
    }

    try {
        const response = await fetch(get_api_url(apiPath));

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
