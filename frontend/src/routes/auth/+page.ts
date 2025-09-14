import type { PageLoad } from './$types';
import { redirect } from '@sveltejs/kit';

const AUTH_PATH = '/auth';
const DEFAULT_REDIRECT = '/auth/profile';

export const load = (({ url, parent }) => {
    // First check if the user is already logged in
    return parent().then(({ session }) => {
        // If user is already logged in, redirect them
        if (session) {
            const nextParam = url.searchParams.get('next');
            let redirectUrl = DEFAULT_REDIRECT; // Default to safe path
            
            // Check if nextParam exists, starts with '/', doesn't start with '//', and isn't the auth path itself
            if (nextParam && nextParam.startsWith('/') && !nextParam.startsWith('//') && nextParam !== AUTH_PATH) {
                redirectUrl = nextParam; // Use the validated relative path
            }
            
            throw redirect(303, redirectUrl);
        }
        
        // If not logged in, proceed with normal auth page load
        const nextParam = url.searchParams.get('next');
        let validatedNextUrl = DEFAULT_REDIRECT; // Default to safe path

        // Check if nextParam exists, starts with '/', doesn't start with '//', and isn't the auth path itself
        if (nextParam && nextParam.startsWith('/') && !nextParam.startsWith('//') && nextParam !== AUTH_PATH) {
            validatedNextUrl = nextParam; // Use the validated relative path
        }
        
        return {
            session,
            nextUrl: validatedNextUrl
        };
    });
}) satisfies PageLoad; 