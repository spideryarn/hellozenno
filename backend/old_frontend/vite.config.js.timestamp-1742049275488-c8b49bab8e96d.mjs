// vite.config.js
import { defineConfig } from "file:///Users/greg/Dropbox/dev/experim/hellozenno/frontend/node_modules/vite/dist/node/index.js";
import { svelte } from "file:///Users/greg/Dropbox/dev/experim/hellozenno/frontend/node_modules/@sveltejs/vite-plugin-svelte/src/index.js";
import { resolve } from "path";
import preprocess from "file:///Users/greg/Dropbox/dev/experim/hellozenno/frontend/node_modules/svelte-preprocess/dist/index.js";
var __vite_injected_original_dirname = "/Users/greg/Dropbox/dev/experim/hellozenno/frontend";
var flaskPort = process.env.FLASK_PORT;
if (process.env.NODE_ENV !== "production" && !flaskPort) {
  console.error("Error: FLASK_PORT environment variable is not set");
  process.exit(1);
}
var entries = {
  "sentence": resolve(__vite_injected_original_dirname, "src/entries/sentence.ts"),
  "minisentence": resolve(__vite_injected_original_dirname, "src/entries/minisentence.ts"),
  "miniwordform": resolve(__vite_injected_original_dirname, "src/entries/miniwordform.ts"),
  "minilemma": resolve(__vite_injected_original_dirname, "src/entries/minilemma.ts"),
  "miniwordformlist": resolve(__vite_injected_original_dirname, "src/entries/miniwordformlist.ts"),
  "miniphrase": resolve(__vite_injected_original_dirname, "src/entries/miniphrase.ts"),
  "flashcardapp": resolve(__vite_injected_original_dirname, "src/entries/flashcardapp.ts")
};
var vite_config_default = defineConfig({
  plugins: [
    svelte({
      // Enable TypeScript preprocessing
      preprocess: preprocess(),
      // Configure Svelte compiler options
      compilerOptions: {
        // Generate code that works in SSR and non-SSR environments
        hydratable: true,
        // Generate TypeScript definitions
        dev: process.env.NODE_ENV !== "production"
      },
      // Ensure emitCss is true to extract CSS
      emitCss: true,
      // Treat warnings as errors in development
      onwarn: (warning, handler) => {
        console.error("Svelte warning:", warning.message);
        if (process.env.NODE_ENV !== "production") {
          throw new Error(warning.message);
        }
        handler(warning);
      }
    })
  ],
  // Configure build output to Flask's static directory
  build: {
    outDir: "../static/build",
    emptyOutDir: true,
    manifest: true,
    cssCodeSplit: true,
    // Ensure source maps are generated for easier debugging
    sourcemap: true,
    // Configure library mode for component building
    lib: {
      // Use a single entry point that exports all components
      entry: resolve(__vite_injected_original_dirname, "src/entries/index.ts"),
      name: "HzComponents",
      formats: ["es"],
      fileName: (format) => `js/hz-components.${format}.js`
    },
    rollupOptions: {
      // Make sure to externalize deps that shouldn't be bundled
      external: ["svelte"],
      output: {
        // Global variables to use in UMD build for externalized deps
        globals: {
          svelte: "Svelte"
        },
        // Preserve directory structure for component CSS
        assetFileNames: "assets/[name]-[hash][extname]"
      }
    }
  },
  // Development server configuration
  server: {
    port: 5173,
    strictPort: true,
    origin: "http://localhost:5173",
    // Proxy API requests to Flask during development
    proxy: {
      "/api": {
        target: `http://localhost:${flaskPort}`,
        changeOrigin: true
      }
    }
  },
  // Resolve paths
  resolve: {
    alias: {
      "@": resolve(__vite_injected_original_dirname, "src")
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMvZ3JlZy9Ecm9wYm94L2Rldi9leHBlcmltL2hlbGxvemVubm8vZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIi9Vc2Vycy9ncmVnL0Ryb3Bib3gvZGV2L2V4cGVyaW0vaGVsbG96ZW5uby9mcm9udGVuZC92aXRlLmNvbmZpZy5qc1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vVXNlcnMvZ3JlZy9Ecm9wYm94L2Rldi9leHBlcmltL2hlbGxvemVubm8vZnJvbnRlbmQvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJztcbmltcG9ydCB7IHN2ZWx0ZSB9IGZyb20gJ0BzdmVsdGVqcy92aXRlLXBsdWdpbi1zdmVsdGUnO1xuaW1wb3J0IHsgcmVzb2x2ZSB9IGZyb20gJ3BhdGgnO1xuaW1wb3J0IHByZXByb2Nlc3MgZnJvbSAnc3ZlbHRlLXByZXByb2Nlc3MnO1xuaW1wb3J0IGZzIGZyb20gJ2ZzJztcblxuLy8gTm8gY3VzdG9tIHBsdWdpbiBuZWVkZWQgLSB3ZSdyZSB1c2luZyBzZXJ2ZXItc2lkZSByZW5kZXJpbmcgaW4gcHJvZHVjdGlvblxuXG4vLyBDaGVjayBpZiBGbGFzayBwb3J0IGlzIHNwZWNpZmllZCBpbiBlbnZpcm9ubWVudCwgYnV0IG9ubHkgaW4gZGV2IG1vZGVcbmNvbnN0IGZsYXNrUG9ydCA9IHByb2Nlc3MuZW52LkZMQVNLX1BPUlQ7XG5pZiAocHJvY2Vzcy5lbnYuTk9ERV9FTlYgIT09ICdwcm9kdWN0aW9uJyAmJiAhZmxhc2tQb3J0KSB7XG4gICAgY29uc29sZS5lcnJvcignRXJyb3I6IEZMQVNLX1BPUlQgZW52aXJvbm1lbnQgdmFyaWFibGUgaXMgbm90IHNldCcpO1xuICAgIHByb2Nlc3MuZXhpdCgxKTtcbn1cblxuLy8gRGVmaW5lIGVudHJ5IHBvaW50c1xuY29uc3QgZW50cmllcyA9IHtcbiAgICAnc2VudGVuY2UnOiByZXNvbHZlKF9fZGlybmFtZSwgJ3NyYy9lbnRyaWVzL3NlbnRlbmNlLnRzJyksXG4gICAgJ21pbmlzZW50ZW5jZSc6IHJlc29sdmUoX19kaXJuYW1lLCAnc3JjL2VudHJpZXMvbWluaXNlbnRlbmNlLnRzJyksXG4gICAgJ21pbml3b3JkZm9ybSc6IHJlc29sdmUoX19kaXJuYW1lLCAnc3JjL2VudHJpZXMvbWluaXdvcmRmb3JtLnRzJyksXG4gICAgJ21pbmlsZW1tYSc6IHJlc29sdmUoX19kaXJuYW1lLCAnc3JjL2VudHJpZXMvbWluaWxlbW1hLnRzJyksXG4gICAgJ21pbml3b3JkZm9ybWxpc3QnOiByZXNvbHZlKF9fZGlybmFtZSwgJ3NyYy9lbnRyaWVzL21pbml3b3JkZm9ybWxpc3QudHMnKSxcbiAgICAnbWluaXBocmFzZSc6IHJlc29sdmUoX19kaXJuYW1lLCAnc3JjL2VudHJpZXMvbWluaXBocmFzZS50cycpLFxuICAgICdmbGFzaGNhcmRhcHAnOiByZXNvbHZlKF9fZGlybmFtZSwgJ3NyYy9lbnRyaWVzL2ZsYXNoY2FyZGFwcC50cycpLFxufTtcblxuLy8gaHR0cHM6Ly92aXRlanMuZGV2L2NvbmZpZy9cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gICAgcGx1Z2luczogW1xuICAgICAgICBzdmVsdGUoe1xuICAgICAgICAgICAgLy8gRW5hYmxlIFR5cGVTY3JpcHQgcHJlcHJvY2Vzc2luZ1xuICAgICAgICAgICAgcHJlcHJvY2VzczogcHJlcHJvY2VzcygpLFxuICAgICAgICAgICAgLy8gQ29uZmlndXJlIFN2ZWx0ZSBjb21waWxlciBvcHRpb25zXG4gICAgICAgICAgICBjb21waWxlck9wdGlvbnM6IHtcbiAgICAgICAgICAgICAgICAvLyBHZW5lcmF0ZSBjb2RlIHRoYXQgd29ya3MgaW4gU1NSIGFuZCBub24tU1NSIGVudmlyb25tZW50c1xuICAgICAgICAgICAgICAgIGh5ZHJhdGFibGU6IHRydWUsXG4gICAgICAgICAgICAgICAgLy8gR2VuZXJhdGUgVHlwZVNjcmlwdCBkZWZpbml0aW9uc1xuICAgICAgICAgICAgICAgIGRldjogcHJvY2Vzcy5lbnYuTk9ERV9FTlYgIT09ICdwcm9kdWN0aW9uJ1xuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIC8vIEVuc3VyZSBlbWl0Q3NzIGlzIHRydWUgdG8gZXh0cmFjdCBDU1NcbiAgICAgICAgICAgIGVtaXRDc3M6IHRydWUsXG4gICAgICAgICAgICAvLyBUcmVhdCB3YXJuaW5ncyBhcyBlcnJvcnMgaW4gZGV2ZWxvcG1lbnRcbiAgICAgICAgICAgIG9ud2FybjogKHdhcm5pbmcsIGhhbmRsZXIpID0+IHtcbiAgICAgICAgICAgICAgICAvLyBMb2cgdGhlIHdhcm5pbmcgZm9yIGRlYnVnZ2luZ1xuICAgICAgICAgICAgICAgIGNvbnNvbGUuZXJyb3IoJ1N2ZWx0ZSB3YXJuaW5nOicsIHdhcm5pbmcubWVzc2FnZSk7XG5cbiAgICAgICAgICAgICAgICAvLyBJbiBkZXZlbG9wbWVudCwgdGhyb3cgZXJyb3JzIGZvciB3YXJuaW5nc1xuICAgICAgICAgICAgICAgIGlmIChwcm9jZXNzLmVudi5OT0RFX0VOViAhPT0gJ3Byb2R1Y3Rpb24nKSB7XG4gICAgICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcih3YXJuaW5nLm1lc3NhZ2UpO1xuICAgICAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgICAgIC8vIEluIHByb2R1Y3Rpb24sIGhhbmRsZSB3YXJuaW5ncyBub3JtYWxseVxuICAgICAgICAgICAgICAgIGhhbmRsZXIod2FybmluZyk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pXG4gICAgXSxcblxuICAgIC8vIENvbmZpZ3VyZSBidWlsZCBvdXRwdXQgdG8gRmxhc2sncyBzdGF0aWMgZGlyZWN0b3J5XG4gICAgYnVpbGQ6IHtcbiAgICAgICAgb3V0RGlyOiAnLi4vc3RhdGljL2J1aWxkJyxcbiAgICAgICAgZW1wdHlPdXREaXI6IHRydWUsXG4gICAgICAgIG1hbmlmZXN0OiB0cnVlLFxuICAgICAgICBjc3NDb2RlU3BsaXQ6IHRydWUsXG4gICAgICAgIC8vIEVuc3VyZSBzb3VyY2UgbWFwcyBhcmUgZ2VuZXJhdGVkIGZvciBlYXNpZXIgZGVidWdnaW5nXG4gICAgICAgIHNvdXJjZW1hcDogdHJ1ZSxcbiAgICAgICAgXG4gICAgICAgIC8vIENvbmZpZ3VyZSBsaWJyYXJ5IG1vZGUgZm9yIGNvbXBvbmVudCBidWlsZGluZ1xuICAgICAgICBsaWI6IHtcbiAgICAgICAgICAgIC8vIFVzZSBhIHNpbmdsZSBlbnRyeSBwb2ludCB0aGF0IGV4cG9ydHMgYWxsIGNvbXBvbmVudHNcbiAgICAgICAgICAgIGVudHJ5OiByZXNvbHZlKF9fZGlybmFtZSwgJ3NyYy9lbnRyaWVzL2luZGV4LnRzJyksXG4gICAgICAgICAgICBuYW1lOiAnSHpDb21wb25lbnRzJyxcbiAgICAgICAgICAgIGZvcm1hdHM6IFsnZXMnXSxcbiAgICAgICAgICAgIGZpbGVOYW1lOiAoZm9ybWF0KSA9PiBganMvaHotY29tcG9uZW50cy4ke2Zvcm1hdH0uanNgXG4gICAgICAgIH0sXG4gICAgICAgIFxuICAgICAgICByb2xsdXBPcHRpb25zOiB7XG4gICAgICAgICAgICAvLyBNYWtlIHN1cmUgdG8gZXh0ZXJuYWxpemUgZGVwcyB0aGF0IHNob3VsZG4ndCBiZSBidW5kbGVkXG4gICAgICAgICAgICBleHRlcm5hbDogWydzdmVsdGUnXSxcbiAgICAgICAgICAgIG91dHB1dDoge1xuICAgICAgICAgICAgICAgIC8vIEdsb2JhbCB2YXJpYWJsZXMgdG8gdXNlIGluIFVNRCBidWlsZCBmb3IgZXh0ZXJuYWxpemVkIGRlcHNcbiAgICAgICAgICAgICAgICBnbG9iYWxzOiB7XG4gICAgICAgICAgICAgICAgICAgIHN2ZWx0ZTogJ1N2ZWx0ZSdcbiAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgICAgIC8vIFByZXNlcnZlIGRpcmVjdG9yeSBzdHJ1Y3R1cmUgZm9yIGNvbXBvbmVudCBDU1NcbiAgICAgICAgICAgICAgICBhc3NldEZpbGVOYW1lczogJ2Fzc2V0cy9bbmFtZV0tW2hhc2hdW2V4dG5hbWVdJyxcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH0sXG5cbiAgICAvLyBEZXZlbG9wbWVudCBzZXJ2ZXIgY29uZmlndXJhdGlvblxuICAgIHNlcnZlcjoge1xuICAgICAgICBwb3J0OiA1MTczLFxuICAgICAgICBzdHJpY3RQb3J0OiB0cnVlLFxuICAgICAgICBvcmlnaW46ICdodHRwOi8vbG9jYWxob3N0OjUxNzMnLFxuICAgICAgICAvLyBQcm94eSBBUEkgcmVxdWVzdHMgdG8gRmxhc2sgZHVyaW5nIGRldmVsb3BtZW50XG4gICAgICAgIHByb3h5OiB7XG4gICAgICAgICAgICAnL2FwaSc6IHtcbiAgICAgICAgICAgICAgICB0YXJnZXQ6IGBodHRwOi8vbG9jYWxob3N0OiR7Zmxhc2tQb3J0fWAsXG4gICAgICAgICAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgfSxcbiAgICB9LFxuXG4gICAgLy8gUmVzb2x2ZSBwYXRoc1xuICAgIHJlc29sdmU6IHtcbiAgICAgICAgYWxpYXM6IHtcbiAgICAgICAgICAgICdAJzogcmVzb2x2ZShfX2Rpcm5hbWUsICdzcmMnKSxcbiAgICAgICAgfSxcbiAgICB9LFxufSk7ICJdLAogICJtYXBwaW5ncyI6ICI7QUFBMlUsU0FBUyxvQkFBb0I7QUFDeFcsU0FBUyxjQUFjO0FBQ3ZCLFNBQVMsZUFBZTtBQUN4QixPQUFPLGdCQUFnQjtBQUh2QixJQUFNLG1DQUFtQztBQVN6QyxJQUFNLFlBQVksUUFBUSxJQUFJO0FBQzlCLElBQUksUUFBUSxJQUFJLGFBQWEsZ0JBQWdCLENBQUMsV0FBVztBQUNyRCxVQUFRLE1BQU0sbURBQW1EO0FBQ2pFLFVBQVEsS0FBSyxDQUFDO0FBQ2xCO0FBR0EsSUFBTSxVQUFVO0FBQUEsRUFDWixZQUFZLFFBQVEsa0NBQVcseUJBQXlCO0FBQUEsRUFDeEQsZ0JBQWdCLFFBQVEsa0NBQVcsNkJBQTZCO0FBQUEsRUFDaEUsZ0JBQWdCLFFBQVEsa0NBQVcsNkJBQTZCO0FBQUEsRUFDaEUsYUFBYSxRQUFRLGtDQUFXLDBCQUEwQjtBQUFBLEVBQzFELG9CQUFvQixRQUFRLGtDQUFXLGlDQUFpQztBQUFBLEVBQ3hFLGNBQWMsUUFBUSxrQ0FBVywyQkFBMkI7QUFBQSxFQUM1RCxnQkFBZ0IsUUFBUSxrQ0FBVyw2QkFBNkI7QUFDcEU7QUFHQSxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUN4QixTQUFTO0FBQUEsSUFDTCxPQUFPO0FBQUE7QUFBQSxNQUVILFlBQVksV0FBVztBQUFBO0FBQUEsTUFFdkIsaUJBQWlCO0FBQUE7QUFBQSxRQUViLFlBQVk7QUFBQTtBQUFBLFFBRVosS0FBSyxRQUFRLElBQUksYUFBYTtBQUFBLE1BQ2xDO0FBQUE7QUFBQSxNQUVBLFNBQVM7QUFBQTtBQUFBLE1BRVQsUUFBUSxDQUFDLFNBQVMsWUFBWTtBQUUxQixnQkFBUSxNQUFNLG1CQUFtQixRQUFRLE9BQU87QUFHaEQsWUFBSSxRQUFRLElBQUksYUFBYSxjQUFjO0FBQ3ZDLGdCQUFNLElBQUksTUFBTSxRQUFRLE9BQU87QUFBQSxRQUNuQztBQUdBLGdCQUFRLE9BQU87QUFBQSxNQUNuQjtBQUFBLElBQ0osQ0FBQztBQUFBLEVBQ0w7QUFBQTtBQUFBLEVBR0EsT0FBTztBQUFBLElBQ0gsUUFBUTtBQUFBLElBQ1IsYUFBYTtBQUFBLElBQ2IsVUFBVTtBQUFBLElBQ1YsY0FBYztBQUFBO0FBQUEsSUFFZCxXQUFXO0FBQUE7QUFBQSxJQUdYLEtBQUs7QUFBQTtBQUFBLE1BRUQsT0FBTyxRQUFRLGtDQUFXLHNCQUFzQjtBQUFBLE1BQ2hELE1BQU07QUFBQSxNQUNOLFNBQVMsQ0FBQyxJQUFJO0FBQUEsTUFDZCxVQUFVLENBQUMsV0FBVyxvQkFBb0IsTUFBTTtBQUFBLElBQ3BEO0FBQUEsSUFFQSxlQUFlO0FBQUE7QUFBQSxNQUVYLFVBQVUsQ0FBQyxRQUFRO0FBQUEsTUFDbkIsUUFBUTtBQUFBO0FBQUEsUUFFSixTQUFTO0FBQUEsVUFDTCxRQUFRO0FBQUEsUUFDWjtBQUFBO0FBQUEsUUFFQSxnQkFBZ0I7QUFBQSxNQUNwQjtBQUFBLElBQ0o7QUFBQSxFQUNKO0FBQUE7QUFBQSxFQUdBLFFBQVE7QUFBQSxJQUNKLE1BQU07QUFBQSxJQUNOLFlBQVk7QUFBQSxJQUNaLFFBQVE7QUFBQTtBQUFBLElBRVIsT0FBTztBQUFBLE1BQ0gsUUFBUTtBQUFBLFFBQ0osUUFBUSxvQkFBb0IsU0FBUztBQUFBLFFBQ3JDLGNBQWM7QUFBQSxNQUNsQjtBQUFBLElBQ0o7QUFBQSxFQUNKO0FBQUE7QUFBQSxFQUdBLFNBQVM7QUFBQSxJQUNMLE9BQU87QUFBQSxNQUNILEtBQUssUUFBUSxrQ0FBVyxLQUFLO0FBQUEsSUFDakM7QUFBQSxFQUNKO0FBQ0osQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K
