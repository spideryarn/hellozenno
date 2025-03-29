import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getWordformsForLanguage } from "$lib/api";
import { get_language_name } from "$lib/utils";

export const load: PageServerLoad = async ({ params }) => {
    const { language_code } = params;

    try {
        // Fetch wordforms for the specified language
        const wordforms = await getWordformsForLanguage(language_code);

        // Get language name for the title
        const language_name = await get_language_name(language_code);

        return {
            language_code,
            language_name,
            wordforms,
        };
    } catch (err) {
        console.error("Error loading wordforms:", err);
        throw error(404, "Could not load wordforms for this language");
    }
};
