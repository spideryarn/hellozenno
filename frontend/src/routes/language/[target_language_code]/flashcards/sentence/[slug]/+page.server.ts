import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { apiFetch } from "$lib/api";
import { RouteName } from "$lib/generated/routes";
import { API_BASE_URL } from "$lib/config";

export const load: PageServerLoad = async ({ params, url, locals }) => {
    const { target_language_code, slug } = params;
    console.log(`Loading flashcard sentence: ${target_language_code}/${slug}`);

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
        // Call API via shared helper to automatically attach Supabase auth header
        const data = await apiFetch({
            supabaseClient: locals.supabase,
            routeName: RouteName.FLASHCARD_API_FLASHCARD_SENTENCE_API,
            params: {
                target_language_code: target_language_code,
                slug: slug,
            },
            options: { method: "GET" },
            searchParams: {
                ...(sourcefile ? { sourcefile } : {}),
                ...(sourcedir ? { sourcedir } : {}),
            },
        });
        console.log(`Received data from API:`, data);

        // Fix audio URL to include the full host if it's a relative path
        if (data.audio_url && data.audio_url.startsWith("/api")) {
            data.audio_url = `${API_BASE_URL}${data.audio_url}`;
            console.log(`Fixed audio URL: ${data.audio_url}`);
        }

        return data;
    } catch (err) {
        console.error("Error fetching sentence data:", err);
        throw error(500, "Failed to load sentence data");
    }
};
