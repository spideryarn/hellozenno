import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

// Check if Flask port is specified in environment
const flaskPort = process.env.FLASK_PORT;
if (!flaskPort) {
    console.error('Error: FLASK_PORT environment variable is not set');
    process.exit(1);
}

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [svelte()],

    // Configure build output to Flask's static directory
    build: {
        outDir: '../static/build',
        emptyOutDir: true,
        rollupOptions: {
            input: {
                'helloworld-entry': resolve(__dirname, 'src/entries/helloworld-entry.ts'),
                // Add more entry points as needed for different pages
            },
            output: {
                entryFileNames: 'js/[name].js',
                chunkFileNames: 'js/[name]-[hash].js',
                assetFileNames: 'assets/[name]-[hash][extname]',
            },
        },
    },

    // Development server configuration
    server: {
        port: 5173,
        strictPort: true,
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