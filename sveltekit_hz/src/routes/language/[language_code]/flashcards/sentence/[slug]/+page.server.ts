import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { get_api_url } from "$lib/utils";

export const load: PageServerLoad = async ({ params, fetch, url }) => {
    const { language_code, slug } = params;
    console.log(`Loading flashcard sentence: ${language_code}/${slug}`);

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
        const apiUrl = get_api_url(apiPath);
        console.log(`Fetching flashcard sentence from API: ${apiUrl}`);

        const response = await fetch(apiUrl);

        if (!response.ok) {
            // If API returns an error, handle it
            const errorText = await response.text();
            console.error(`API error (${response.status}): ${errorText}`);

            try {
                const errorData = JSON.parse(errorText);
                throw error(
                    response.status,
                    errorData.error || "Failed to load sentence",
                );
            } catch (parseError) {
                throw error(
                    500,
                    `Failed to parse API error response: ${errorText}`,
                );
            }
        }

        // Return the sentence data
        const data = await response.json();
        console.log(`Received data from API:`, data);

        // Fix audio URL to include the full host if it's a relative path
        if (data.audio_url && data.audio_url.startsWith("/api")) {
            data.audio_url = `http://localhost:3000${data.audio_url}`;
            console.log(`Fixed audio URL: ${data.audio_url}`);
        }

        return data;
    } catch (err) {
        console.error("Error fetching sentence data:", err);
        throw error(500, "Failed to load sentence data");
    }
};
