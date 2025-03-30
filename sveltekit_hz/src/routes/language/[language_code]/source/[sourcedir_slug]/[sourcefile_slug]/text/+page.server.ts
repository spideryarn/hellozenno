import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params }) => {
    const { language_code, sourcedir_slug, sourcefile_slug } = params;

    // Redirect to the main sourcefile page
    throw redirect(
        307,
        `/language/${language_code}/source/${sourcedir_slug}/${sourcefile_slug}`,
    );
};
