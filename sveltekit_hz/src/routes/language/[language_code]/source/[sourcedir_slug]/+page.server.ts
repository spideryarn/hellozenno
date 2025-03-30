import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, sourcedir_slug } = params;

    try {
        // Fetch all sourcefiles for this sourcedir
        const response = await fetch(
            getApiUrl(
                `/api/lang/sourcedir/${language_code}/${sourcedir_slug}/files`,
            ),
        );

        if (!response.ok) {
            throw new Error(
                `Failed to fetch sourcefiles: ${response.statusText}`,
            );
        }

        const data = await response.json();

        return {
            sourcedir: data.sourcedir,
            sourcefiles: data.sourcefiles,
            language_code,
            language_name: data.language_name,
            has_vocabulary: data.has_vocabulary,
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
