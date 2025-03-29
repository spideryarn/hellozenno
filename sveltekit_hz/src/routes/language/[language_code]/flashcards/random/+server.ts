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
        const apiUrl = get_api_url(apiPath);
        console.log(`Fetching random flashcard from API: ${apiUrl}`);

        const response = await fetch(apiUrl);

        if (!response.ok) {
            // If API returns an error, handle it
            const errorText = await response.text();
            console.error(`API error (${response.status}): ${errorText}`);

            try {
                const errorData = JSON.parse(errorText);
                throw new Error(
                    errorData.error || `API error: ${response.status}`,
                );
            } catch (parseError) {
                throw new Error(
                    `Failed to parse API error response: ${errorText}`,
                );
            }
        }

        // Get the data and redirect to the sentence page
        const data = await response.json();
        console.log(`Received data from API:`, data);

        if (!data.slug) {
            console.error(`No slug found in API response:`, data);
            throw new Error("API response missing slug field");
        }

        // Fix audio URL if present
        if (data.audio_url && data.audio_url.startsWith("/api")) {
            data.audio_url = `http://localhost:3000${data.audio_url}`;
            console.log(`Fixed audio URL: ${data.audio_url}`);
        }

        // Build the redirect URL with the same query parameters
        let redirectUrl =
            `/language/${language_code}/flashcards/sentence/${data.slug}`;

        if (queryParams.toString()) {
            redirectUrl += `?${queryParams.toString()}`;
        }

        console.log(`Redirecting to: ${redirectUrl}`);

        // Test a direct redirect instead of using the kit redirect
        return new Response(null, {
            status: 302,
            headers: {
                Location: redirectUrl,
            },
        });
    } catch (err) {
        // If it's already a redirect, just pass it through
        if (err instanceof Response && err.status === 302) {
            throw err;
        }

        // Otherwise, redirect to the flashcards landing page with an error
        console.error("Error fetching random flashcard:", err);

        return new Response(null, {
            status: 302,
            headers: {
                Location:
                    `/language/${language_code}/flashcards?error=no_sentences_found`,
            },
        });
    }
};
