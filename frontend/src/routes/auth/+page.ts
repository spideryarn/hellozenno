import type { PageLoad } from './$types';

const AUTH_PATH = '/auth';
const DEFAULT_REDIRECT = '/profile';

export const load = (({ url }) => {
    const nextParam = url.searchParams.get('next');
    let validatedNextUrl = DEFAULT_REDIRECT; // Default to safe path

    // Check if nextParam exists, starts with '/', doesn't start with '//', and isn't the auth path itself
    if (nextParam && nextParam.startsWith('/') && !nextParam.startsWith('//') && nextParam !== AUTH_PATH) {
        validatedNextUrl = nextParam; // Use the validated relative path
    }
    // Otherwise, validatedNextUrl remains DEFAULT_REDIRECT

    return {
        nextUrl: validatedNextUrl
    };
}) satisfies PageLoad; 