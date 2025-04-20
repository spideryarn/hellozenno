import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ params }) => {
    // Redirect bare language route to the sources listing page
    const target_language_code = params.target_language_code;
    throw redirect(307, `/language/${target_language_code}/sources`);
};