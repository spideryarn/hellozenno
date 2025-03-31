/**
 * Configuration for the SvelteKit application
 */

// Base URL for API requests - from environment variables
export const API_BASE_URL = import.meta.env.VITE_API_URL ||
    "http://localhost:3000";
