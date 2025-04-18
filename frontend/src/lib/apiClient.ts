import { sessionToken } from '$lib/stores/authStore';
import { get } from 'svelte/store';
// import { PUBLIC_BACKEND_URL } from '$env/static/public'; // Use Vite's env handling instead

// Utility function to make authenticated API requests
export async function fetchAuthenticated(path: string, options: RequestInit = {}): Promise<Response> {
    const token = get(sessionToken); // Get the current token from the store

    const headers = new Headers(options.headers || {});
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    // Use import.meta.env for VITE_ prefixed variables
    const backendUrl = import.meta.env.VITE_API_URL;
    if (!backendUrl) {
        throw new Error('VITE_API_URL is not defined in environment variables');
    }
    const url = `${backendUrl}${path}`; // Construct full URL
    
    console.log(`fetchAuthenticated: ${options.method || 'GET'} ${url}`);

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });
        return response;
    } catch (error) {
        console.error(`API request failed for ${url}:`, error);
        throw error; // Re-throw the error to be handled by the caller
    }
} 