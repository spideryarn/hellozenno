import { redirect } from '@sveltejs/kit';

/**
 * This is a catch-all for redirecting the base sourcefile URL to the text tab.
 */
export function load({ params }) {
    const { language_code, sourcedir_slug, sourcefile_slug } = params;
    throw redirect(307, `/language/${language_code}/source/${sourcedir_slug}/${sourcefile_slug}/text`);
} 