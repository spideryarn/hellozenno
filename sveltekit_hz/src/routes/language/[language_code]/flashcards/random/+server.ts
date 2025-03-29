import { redirect } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { get_api_url } from "$lib/utils";

export const GET: RequestHandler = async ({ params, url, fetch }) => {
    const { language_code } = params;

    // Get query parameters for filtering
    const sourcefile = url.searchParams.get("sourcefile");
    const sourcedir = url.searchParams.get("sourcedir");

    // Build API path with query parameters
    let apiPath = `lang/${language_code}/flashcards/random`;
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
            throw new Error(errorData.error || "Failed to get random sentence");
        }

        // Get the data and redirect to the sentence page
        const data = await response.json();

        // Build the redirect URL with the same query parameters
        let redirectUrl =
            `/language/${language_code}/flashcards/sentence/${data.slug}`;

        if (queryParams.toString()) {
            redirectUrl += `?${queryParams.toString()}`;
        }

        throw redirect(302, redirectUrl);
    } catch (err) {
        // If it's already a redirect, just pass it through
        if (err instanceof Response && err.status === 302) {
            throw err;
        }

        // Otherwise, redirect to the flashcards landing page with an error
        console.error("Error fetching random flashcard:", err);
        throw redirect(
            302,
            `/language/${language_code}/flashcards?error=no_sentences_found`,
        );
    }
};
