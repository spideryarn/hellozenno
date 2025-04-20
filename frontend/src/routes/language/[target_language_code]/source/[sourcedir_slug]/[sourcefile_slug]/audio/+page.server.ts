import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch, locals: { supabase, session } }) => {
    const { target_language_code, sourcedir_slug, sourcefile_slug } = params;

    try {
        // Fetch text data for basic sourcefile info
        const textResponse = await fetch(
            getApiUrl(
                RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API,
                {
                    target_language_code: target_language_code,
                    sourcedir_slug,
                    sourcefile_slug,
                },
            ),
        );

        // Fetch status data (including stats) - same as text tab
        const statusResponse = await fetch(
            getApiUrl(
              RouteName.SOURCEFILE_PROCESSING_API_SOURCEFILE_STATUS_API,
              {
                target_language_code: target_language_code,
                sourcedir_slug,
                sourcefile_slug
              }
            ),
        );

        if (!textResponse.ok) {
            throw new Error(
                `Failed to fetch text data: ${textResponse.statusText}`,
            );
        }
        
        if (!statusResponse.ok) {
            throw new Error(
                `Failed to fetch status data: ${statusResponse.statusText}`
            );
        }

        const textData = await textResponse.json();
        const statusData = await statusResponse.json();

        // Extract stats from status data, providing defaults if not present
        const stats = statusData.status ? {
            wordforms_count: statusData.status.wordforms_count ?? 0,
            phrases_count: statusData.status.phrases_count ?? 0,
            incomplete_lemmas: statusData.status.incomplete_lemmas ?? [],
            has_text: statusData.status.has_text ?? false,
            has_translation: statusData.status.has_translation ?? false,
        } : {
            wordforms_count: 0,
            phrases_count: 0,
            incomplete_lemmas: [],
            has_text: false,
            has_translation: false,
        };

        // Empty placeholders to maintain API compatibility
        const wordsData = { wordforms: [] };
        const phrasesData = { phrases: [] };
        const available_sourcedirs = textData.available_sourcedirs || [];

        return {
            sourcefileData: textData,
            textData,
            wordsData,
            phrasesData,
            stats,
            target_language_code,
            language_name: textData.language_name || "",
            sourcedir_slug,
            sourcefile_slug,
            available_sourcedirs,
            // Only pass the session data to the client, not the supabase client
            session
        };
    } catch (err: unknown) {
        console.error("Error loading sourcefile audio:", err);
        const errorMessage = err instanceof Error
            ? err.message
            : "Unknown error";
        throw error(404, {
            message: `Failed to load sourcefile audio: ${errorMessage}`,
        });
    }
};
