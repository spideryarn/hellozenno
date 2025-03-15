import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';
import preprocess from 'svelte-preprocess';
import fs from 'fs';

// Custom plugin to ensure proper component exports
function ensureSvelteExports() {
  return {
    name: 'ensure-svelte-exports',
    // Run after build to check and potentially fix output files
    closeBundle: async () => {
      console.log('Checking Svelte component exports...');
      const outDir = resolve(__dirname, '../static/build/js');
      
      // Process each entry file
      for (const entryName in entries) {
        const outFile = resolve(outDir, `${entryName}.js`);
        
        // Check if file exists and is empty/minimal
        if (fs.existsSync(outFile)) {
          const content = fs.readFileSync(outFile, 'utf-8');
          
          // If file only imports index but doesn't export anything useful
          if (content.trim().startsWith('import') && !content.includes('export default')) {
            console.log(`Fixing exports for ${entryName}...`);
            
            // Extract component name (assuming PascalCase for components)
            const componentName = entryName.charAt(0).toUpperCase() + 
                                  entryName.slice(1).replace(/([A-Z])/g, ' $1').trim().replace(/ /g, '');
            
            // Create a proper module that exports the component factory function
            const newContent = `import { ${componentName} } from "${entries[entryName].replace(__dirname, '.').replace('.ts', '')}";
export { ${componentName} };
export default function(target, props) {
  return new ${componentName}({ target, props });
}
`;
            
            // Write the fixed content
            fs.writeFileSync(outFile, newContent, 'utf-8');
            console.log(`Fixed ${entryName}`);
          }
        }
      }
    }
  };
}

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
};

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
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
        }),
        // Add our custom plugin to ensure component exports
        ensureSvelteExports()
    ],

    // Configure build output to Flask's static directory
    build: {
        outDir: '../static/build',
        emptyOutDir: true,
        manifest: true,
        cssCodeSplit: true,
        // Ensure source maps are generated for easier debugging
        sourcemap: true,
        rollupOptions: {
            input: entries,
            output: {
                entryFileNames: 'js/[name].js',
                chunkFileNames: 'js/[name]-[hash].js',
                assetFileNames: 'assets/[name]-[hash][extname]',
                // Use ES module format to ensure compatibility with modern browsers
                format: 'es',
                // Ensure exports are properly named
                exports: 'named'
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
        },
    },

    // Resolve paths
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
}); 