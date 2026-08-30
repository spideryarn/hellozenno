import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
    const { target_language_code, sourcedir_slug } = params;

    // Forward the access token (already validated in hooks.server.ts via
    // safeGetSession, so this costs no extra round-trip). Without it an
    // editor's SSR request looks anonymous to the CDN and can be served the
    // shared cached copy of a listing they just changed.
    const headers = new Headers();
    const { session } = locals;
    if (session?.access_token) {
        headers.set('Authorization', `Bearer ${session.access_token}`);
    }

    try {
        // Fetch all sourcefiles for this sourcedir using type-safe route resolution
        const response = await fetch(
            getApiUrl(
                RouteName.SOURCEDIR_API_SOURCEFILES_FOR_SOURCEDIR_API,
                {
                    target_language_code: target_language_code,
                    sourcedir_slug,
                },
            ),
            { headers },
        );

        if (!response.ok) {
            throw new Error(
                `Failed to fetch sourcefiles: ${response.statusText}`,
            );
        }

        const data = await response.json();
        // console.log("API response data:", data);

        // Default fallback for supported languages if not provided
        const supported_languages = data.supported_languages || [
            { code: target_language_code, name: data.language_name }
        ];

        // Generate metadata object for the sourcedir similar to how it's done for sourcefiles
        const metadata = {
            created_at: data.sourcedir.created_at || 'Unknown',
            updated_at: data.sourcedir.updated_at || 'Unknown'
        };

        return {
            sourcedir: data.sourcedir,
            sourcefiles: data.sourcefiles,
            target_language_code,
            language_name: data.language_name,
            has_vocabulary: data.has_vocabulary,
            supported_languages,
            metadata, // Add metadata to the page data
        };
    } catch (err: unknown) {
        console.error("Error loading sourcedir:", err);
        const errorMessage = err instanceof Error
            ? err.message
            : "Unknown error";
        throw error(404, {
            message: `Failed to load sourcedir: ${errorMessage}`,
        });
    }
};
