import { error, redirect } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, sourcedir_slug, sourcefile_slug } = params;

    // Redirect to the text tab
    throw redirect(
        307,
        `/language/${language_code}/source/${sourcedir_slug}/${sourcefile_slug}/text`,
    );
};
