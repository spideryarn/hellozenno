import { redirect } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const GET: RequestHandler = async ({ params, url, fetch }) => {
    const { language_code } = params;

    // Get query parameters for filtering
    const sourcefile = url.searchParams.get("sourcefile");
    const sourcedir = url.searchParams.get("sourcedir");

    // Build query parameters
    let queryParams = new URLSearchParams();

    if (sourcefile) {
        queryParams.append("sourcefile", sourcefile);
    } else if (sourcedir) {
        queryParams.append("sourcedir", sourcedir);
    }

    try {
        // Make the API request using type-safe URL generation
        const apiUrl = getApiUrl(RouteName.FLASHCARD_API_RANDOM_FLASHCARD_API, {
            language_code: language_code,
        });

        // Add query parameters if any
        const fullUrl = queryParams.toString()
            ? `${apiUrl}?${queryParams.toString()}`
            : apiUrl;

        console.log(`Fetching random flashcard from API: ${fullUrl}`);

        const response = await fetch(fullUrl);

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
