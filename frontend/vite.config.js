import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

// Check if Flask port is specified in environment, but only in dev mode
const flaskPort = process.env.FLASK_PORT;
if (process.env.NODE_ENV !== 'production' && !flaskPort) {
    console.error('Error: FLASK_PORT environment variable is not set');
    process.exit(1);
}

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        svelte({
            // Treat warnings as errors in development
            onwarn: (warning, handler) => {
                // Log the warning for debugging
                console.error('Svelte warning:', warning.message);

                // In development, throw errors for warnings
                if (process.env.NODE_ENV !== 'production') {
                    throw new Error(warning.message);
                }

                // In production, handle warnings normally
                handler(warning);
            }
        })
    ],

    // Configure build output to Flask's static directory
    build: {
        outDir: '../static/build',
        emptyOutDir: true,
        manifest: true,
        cssCodeSplit: true,
        lib: {
            entry: resolve(__dirname, 'src/entries/sentence-entry.ts'),
            name: 'SentenceComponent',
            fileName: 'js/sentence-entry',
            formats: ['es'],
        },
    },

    // Development server configuration
    server: {
        port: 5173,
        strictPort: true,
        origin: 'http://localhost:5173',
        // Proxy API requests to Flask during development
        proxy: {
            '/api': {
                target: `http://localhost:${flaskPort}`,
                changeOrigin: true,
            },
        },
    },

    // Resolve paths
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
}); 