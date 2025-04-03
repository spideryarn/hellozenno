/**
 * Configuration for the SvelteKit application
 */

// Check if we're in a production-like environment (Vercel)
const isProduction = import.meta.env.PROD;

// In production, ensure VITE_API_URL is set or throw an error
// I had to add this explicitly in the dashboard
// https://vercel.com/greg-detre/hz_frontend/settings/environment-variables
if (isProduction && !import.meta.env.VITE_API_URL) {
    const env = import.meta.env;
    console.log("env", env);
    throw new Error('VITE_API_URL environment variable is required in production');
}

// Base URL for API requests - from environment variables
export const API_BASE_URL = import.meta.env.VITE_API_URL || 
    (isProduction ? undefined : "http://localhost:3000");

// If we get here in production and API_BASE_URL is undefined, 
// something went wrong with the environment variables
if (isProduction && !API_BASE_URL) {
    throw new Error('API_BASE_URL is undefined in production. Check environment variables.');
}
