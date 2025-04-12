import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getSentencesForLanguage } from "$lib/api";
import { get_language_name } from "$lib/utils";

export const load: PageServerLoad = async ({ params }) => {
    const { target_language_code } = params;

    try {
        // Fetch sentences for the specified language
        const sentences = await getSentencesForLanguage(target_language_code);

        // Get language name for the title
        const language_name = await get_language_name(target_language_code);

        return {
            target_language_code,
            language_name,
            sentences,
        };
    } catch (err) {
        console.error("Error loading sentences:", err);
        throw error(404, "Could not load sentences for this language");
    }
};
