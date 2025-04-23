import type { LayoutServerLoad } from "./$types";
import { get_language_name } from "$lib/language-utils";

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    const { target_language_code } = params;

    // Get the language name for the header and search form
    // This now uses the static data when possible, falling back to API only if needed
    const language_name = await get_language_name(target_language_code, fetch);

    return {
        target_language_code,
        language_name,
    };
};
