import { redirect } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { getApiUrl, apiFetch } from "$lib/api";
import { RouteName } from "$lib/generated/routes";
import { API_BASE_URL } from "$lib/config";

export const GET: RequestHandler = async ({ params, url, locals, fetch }) => {
    const { target_language_code } = params;

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
        // Create params object for apiFetch
        const apiParams: any = { target_language_code };
        if (sourcefile) apiParams.sourcefile = sourcefile;
        if (sourcedir) apiParams.sourcedir = sourcedir;

        console.log(`Fetching random flashcard from API using apiFetch`);

        // Use apiFetch instead of raw fetch
        const data = await apiFetch({
            supabaseClient: locals.supabase, // Server-side Supabase client from locals
            routeName: RouteName.FLASHCARD_API_RANDOM_FLASHCARD_API,
            params: { target_language_code },
            searchParams: {
                ...(sourcefile ? { sourcefile } : {}),
                ...(sourcedir ? { sourcedir } : {}),
            },
            options: { method: 'GET' }
        });

        console.log(`Received data from API:`, data);

        if (!data.slug) {
            console.error(`No slug found in API response:`, data);
            throw new Error("API response missing slug field");
        }

        // Fix audio URL if present
        if (data.audio_url && data.audio_url.startsWith("/api")) {
            data.audio_url = `${API_BASE_URL}${data.audio_url}`;
            console.log(`Fixed audio URL: ${data.audio_url}`);
        }

        // Build the redirect URL with the same query parameters
        let redirectUrl =
            `/language/${target_language_code}/flashcards/sentence/${data.slug}`;

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
    } catch (err: any) {
        // If it's already a redirect, just pass it through
        if (err instanceof Response && err.status === 302) {
            throw err;
        }

        // Otherwise, redirect to the flashcards landing page with a structured error
        console.error("Error fetching random flashcard:", err);

        const errorCode = err?.body?.error_code || 'unknown_error';
        const details = err?.body?.details || {};

        const redirectParams = new URLSearchParams();
        redirectParams.set('error_code', String(errorCode));
        if (details.sourcedir_slug || details.sourcedir) {
            redirectParams.set('sourcedir', String(details.sourcedir_slug || details.sourcedir));
        }
        if (details.sourcefile_slug || details.sourcefile) {
            redirectParams.set('sourcefile', String(details.sourcefile_slug || details.sourcefile));
        }
        if (typeof details.lemma_count === 'number') {
            redirectParams.set('lemma_count', String(details.lemma_count));
        }

        const location = `/language/${target_language_code}/flashcards` + (redirectParams.toString() ? `?${redirectParams.toString()}` : '');

        return new Response(null, {
            status: 302,
            headers: { Location: location },
        });
    }
};
