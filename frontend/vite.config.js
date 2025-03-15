import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';
import preprocess from 'svelte-preprocess';
import fs from 'fs';

// No custom plugin needed - we're using server-side rendering in production

// Check if Flask port is specified in environment, but only in dev mode
const flaskPort = process.env.FLASK_PORT;
if (process.env.NODE_ENV !== 'production' && !flaskPort) {
    console.error('Error: FLASK_PORT environment variable is not set');
    process.exit(1);
}

// Define entry points
const entries = {
    'sentence': resolve(__dirname, 'src/entries/sentence.ts'),
    'minisentence': resolve(__dirname, 'src/entries/minisentence.ts'),
    'miniwordform': resolve(__dirname, 'src/entries/miniwordform.ts'),
    'minilemma': resolve(__dirname, 'src/entries/minilemma.ts'),
    'miniwordformlist': resolve(__dirname, 'src/entries/miniwordformlist.ts'),
    'miniphrase': resolve(__dirname, 'src/entries/miniphrase.ts'),
    'flashcardapp': resolve(__dirname, 'src/entries/flashcardapp.ts'),
};

// Custom plugin to set correct MIME types
function correctMimeTypes() {
    return {
        name: 'correct-mime-types',
        configureServer(server) {
            server.middlewares.use((req, res, next) => {
                // Set correct MIME types for Svelte and TypeScript files
                if (req.url.endsWith('.svelte')) {
                    res.setHeader('Content-Type', 'application/javascript');
                } else if (req.url.endsWith('.ts')) {
                    res.setHeader('Content-Type', 'application/javascript');
                }
                next();
            });
        }
    };
}

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        correctMimeTypes(),
        svelte({
            // Enable TypeScript preprocessing
            preprocess: preprocess(),
            // Configure Svelte compiler options
            compilerOptions: {
                // Generate code that works in SSR and non-SSR environments
                hydratable: true,
                // Generate TypeScript definitions
                dev: process.env.NODE_ENV !== 'production'
            },
            // Ensure emitCss is true to extract CSS
            emitCss: true,
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
        // Ensure source maps are generated for easier debugging
        sourcemap: true,

        // Configure library mode for component building
        lib: {
            // Use a single entry point that exports all components
            entry: resolve(__dirname, 'src/entries/index.ts'),
            name: 'HzComponents',
            formats: ['es'],
            fileName: (format) => `js/hz-components.${format}.js`
        },

        rollupOptions: {
            // Make sure to externalize deps that shouldn't be bundled
            external: ['svelte'],
            output: {
                // Global variables to use in UMD build for externalized deps
                globals: {
                    svelte: 'Svelte'
                },
                // Preserve directory structure for component CSS
                assetFileNames: 'assets/[name]-[hash][extname]',
            }
        }
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
        }
    },

    // Resolve paths
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
}); 