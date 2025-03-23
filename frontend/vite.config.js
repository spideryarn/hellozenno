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
    'flashcardlanding': resolve(__dirname, 'src/entries/flashcardlanding.ts'),
    'auth': resolve(__dirname, 'src/entries/auth.ts'),
    'userstatus': resolve(__dirname, 'src/entries/userstatus.ts'),
};

// Custom plugin to set correct MIME types
function correctMimeTypes() {
    return {
        name: 'correct-mime-types',
        configureServer(server) {
            server.middlewares.use((req, res, next) => {
                // Modify response headers after processing but before sending
                const originalWriteHead = res.writeHead;

                res.writeHead = function (statusCode, statusMessage, headers) {
                    // Set correct MIME types for Svelte and TypeScript files
                    if (req.url.endsWith('.svelte') || req.url.endsWith('.ts')) {
                        if (headers) {
                            headers['Content-Type'] = 'application/javascript';
                        } else {
                            res.setHeader('Content-Type', 'application/javascript');
                        }
                    }
                    return originalWriteHead.apply(this, arguments);
                };

                next();
            });
        }
    };
}

// Helper to create a manifest JS file with info about built files
function createManifestHelperPlugin() {
    return {
        name: 'create-manifest-helper',
        writeBundle: {
            sequential: true,
            handler(options, bundle) {
                // Copy manifest to a place where Flask can easily access it
                const manifestPath = resolve(__dirname, '../static/build/.vite/manifest.json');
                const manifestOutPath = resolve(__dirname, '../static/build/manifest.json');

                if (fs.existsSync(manifestPath)) {
                    fs.copyFileSync(manifestPath, manifestOutPath);
                    console.log('✓ Copied manifest.json to static/build/ for better accessibility');
                }

                // Create a helper JS file with mappings from non-hashed to hashed filenames
                const manifestData = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

                // Extract CSS files
                const cssFiles = {};
                for (const key in manifestData) {
                    if (key.endsWith('.css')) {
                        const fileInfo = manifestData[key];
                        const originalName = key.split('/').pop();
                        cssFiles[originalName] = fileInfo.file;
                    }
                }

                // Create a JS file that provides helper functions
                const helperJs = `
// Auto-generated helper for loading hashed assets
window.loadHashedAsset = function(originalName) {
    const assetMap = ${JSON.stringify(cssFiles, null, 2)};
    return assetMap[originalName] || originalName;
};
`.trim();

                fs.writeFileSync(
                    resolve(__dirname, '../static/build/asset-helper.js'),
                    helperJs
                );

                console.log('✓ Created asset-helper.js for resolving hashed filenames');
            }
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
            // Handle compiler warnings
            onwarn: (warning, handler) => {
                // Log the warning for debugging
                console.error('Svelte warning:', warning.message);

                // Don't treat unused export property warnings as errors
                if (warning.code === 'unused-export-let') {
                    handler(warning);
                    return;
                }

                // In development, throw errors for other warnings
                if (process.env.NODE_ENV !== 'production') {
                    throw new Error(warning.message);
                }

                // In production, handle warnings normally
                handler(warning);
            }
        }),
        createManifestHelperPlugin()
    ],

    // Define environment variables
    define: {
        'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(process.env.VITE_SUPABASE_URL),
        'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify(process.env.VITE_SUPABASE_ANON_KEY),
    },

    // Configure build output to Flask's static directory
    build: {
        outDir: '../static/build',
        emptyOutDir: true,
        manifest: true, // Generate a manifest.json
        cssCodeSplit: false, // Disable code splitting for CSS to create a single CSS file
        // Ensure source maps are generated for easier debugging
        sourcemap: true,

        // Configure library mode for component building
        lib: {
            // Use a single entry point that exports all components
            entry: resolve(__dirname, 'src/entries/index.ts'),
            name: 'HzComponents',
            formats: ['es'], // Only use ES modules, not UMD
            fileName: (format) => `js/hz-components.${format}.js`
        },

        rollupOptions: {
            // Do not externalize Svelte to avoid CDN dependencies
            external: [],
            output: {
                // Global variables to use in UMD build for externalized deps
                globals: {},
                // Fixed asset naming without hashes to make them easier to reference
                assetFileNames: (assetInfo) => {
                    if (assetInfo.name === 'style.css') {
                        return 'assets/style.css';
                    }
                    return 'assets/[name]-[hash][extname]';
                },
                // Make sure the manifest includes CSS files
                manualChunks: undefined
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