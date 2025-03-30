import type { LayoutServerLoad } from "./$types";
import { get_language_name } from "$lib/utils";

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    const { language_code } = params;

    // Get the language name for the header and search form
    const language_name = await get_language_name(language_code, fetch);

    return {
        language_code,
        language_name,
    };
};
