/**
 * Configuration for the SvelteKit application
 */

// Check if we're in a production-like environment (Vercel)
const isProduction = import.meta.env.PROD;

// In production, ensure VITE_API_URL is set or throw an error
// This must be added explicitly in the Vercel dashboard
// https://vercel.com/greg-detre/hz_frontend/settings/environment-variables
if (isProduction && !import.meta.env.VITE_API_URL) {
    console.error("Environment variables:", import.meta.env);
    throw new Error('VITE_API_URL environment variable is required in production');
}

// Base URL for API requests - from environment variables
// Only allow fallback to localhost in development
export const API_BASE_URL = import.meta.env.VITE_API_URL || 
    (isProduction ? undefined : "http://localhost:3000");

// Double-check API_BASE_URL is defined before exporting
if (!API_BASE_URL) {
    throw new Error('API_BASE_URL is undefined. In production, check that VITE_API_URL is set in environment variables.');
}

export const SITE_NAME = "Hello Zenno";
export const TAGLINE = "AI-powered dictionary & listening practice";
export const CONTACT_EMAIL = "hello@hellozenno.com";
export const GITHUB_ISSUES_URL = "https://github.com/spideryarn/hellozenno/issues";