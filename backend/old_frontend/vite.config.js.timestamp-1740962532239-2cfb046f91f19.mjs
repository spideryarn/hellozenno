// vite.config.js
import { defineConfig } from "file:///Users/greg/Dropbox/dev/experim/hellozenno/frontend/node_modules/vite/dist/node/index.js";
import { svelte } from "file:///Users/greg/Dropbox/dev/experim/hellozenno/frontend/node_modules/@sveltejs/vite-plugin-svelte/src/index.js";
import { resolve } from "path";
var __vite_injected_original_dirname = "/Users/greg/Dropbox/dev/experim/hellozenno/frontend";
var flaskPort = process.env.FLASK_PORT;
if (process.env.NODE_ENV !== "production" && !flaskPort) {
  console.error("Error: FLASK_PORT environment variable is not set");
  process.exit(1);
}
var entries = {
  "sentence-entry": resolve(__vite_injected_original_dirname, "src/entries/sentence-entry.ts"),
  "minisentence-entry": resolve(__vite_injected_original_dirname, "src/entries/minisentence-entry.ts"),
  "miniwordform-entry": resolve(__vite_injected_original_dirname, "src/entries/miniwordform-entry.ts")
};
var vite_config_default = defineConfig({
  plugins: [
    svelte({
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
    rollupOptions: {
      input: entries,
      output: {
        entryFileNames: "js/[name].js",
        chunkFileNames: "js/[name]-[hash].js",
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
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMvZ3JlZy9Ecm9wYm94L2Rldi9leHBlcmltL2hlbGxvemVubm8vZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIi9Vc2Vycy9ncmVnL0Ryb3Bib3gvZGV2L2V4cGVyaW0vaGVsbG96ZW5uby9mcm9udGVuZC92aXRlLmNvbmZpZy5qc1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vVXNlcnMvZ3JlZy9Ecm9wYm94L2Rldi9leHBlcmltL2hlbGxvemVubm8vZnJvbnRlbmQvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJztcbmltcG9ydCB7IHN2ZWx0ZSB9IGZyb20gJ0BzdmVsdGVqcy92aXRlLXBsdWdpbi1zdmVsdGUnO1xuaW1wb3J0IHsgcmVzb2x2ZSB9IGZyb20gJ3BhdGgnO1xuXG4vLyBDaGVjayBpZiBGbGFzayBwb3J0IGlzIHNwZWNpZmllZCBpbiBlbnZpcm9ubWVudCwgYnV0IG9ubHkgaW4gZGV2IG1vZGVcbmNvbnN0IGZsYXNrUG9ydCA9IHByb2Nlc3MuZW52LkZMQVNLX1BPUlQ7XG5pZiAocHJvY2Vzcy5lbnYuTk9ERV9FTlYgIT09ICdwcm9kdWN0aW9uJyAmJiAhZmxhc2tQb3J0KSB7XG4gICAgY29uc29sZS5lcnJvcignRXJyb3I6IEZMQVNLX1BPUlQgZW52aXJvbm1lbnQgdmFyaWFibGUgaXMgbm90IHNldCcpO1xuICAgIHByb2Nlc3MuZXhpdCgxKTtcbn1cblxuLy8gRGVmaW5lIGVudHJ5IHBvaW50c1xuY29uc3QgZW50cmllcyA9IHtcbiAgICAnc2VudGVuY2UtZW50cnknOiByZXNvbHZlKF9fZGlybmFtZSwgJ3NyYy9lbnRyaWVzL3NlbnRlbmNlLWVudHJ5LnRzJyksXG4gICAgJ21pbmlzZW50ZW5jZS1lbnRyeSc6IHJlc29sdmUoX19kaXJuYW1lLCAnc3JjL2VudHJpZXMvbWluaXNlbnRlbmNlLWVudHJ5LnRzJyksXG4gICAgJ21pbml3b3JkZm9ybS1lbnRyeSc6IHJlc29sdmUoX19kaXJuYW1lLCAnc3JjL2VudHJpZXMvbWluaXdvcmRmb3JtLWVudHJ5LnRzJyksXG59O1xuXG4vLyBodHRwczovL3ZpdGVqcy5kZXYvY29uZmlnL1xuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgICBwbHVnaW5zOiBbXG4gICAgICAgIHN2ZWx0ZSh7XG4gICAgICAgICAgICAvLyBUcmVhdCB3YXJuaW5ncyBhcyBlcnJvcnMgaW4gZGV2ZWxvcG1lbnRcbiAgICAgICAgICAgIG9ud2FybjogKHdhcm5pbmcsIGhhbmRsZXIpID0+IHtcbiAgICAgICAgICAgICAgICAvLyBMb2cgdGhlIHdhcm5pbmcgZm9yIGRlYnVnZ2luZ1xuICAgICAgICAgICAgICAgIGNvbnNvbGUuZXJyb3IoJ1N2ZWx0ZSB3YXJuaW5nOicsIHdhcm5pbmcubWVzc2FnZSk7XG5cbiAgICAgICAgICAgICAgICAvLyBJbiBkZXZlbG9wbWVudCwgdGhyb3cgZXJyb3JzIGZvciB3YXJuaW5nc1xuICAgICAgICAgICAgICAgIGlmIChwcm9jZXNzLmVudi5OT0RFX0VOViAhPT0gJ3Byb2R1Y3Rpb24nKSB7XG4gICAgICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcih3YXJuaW5nLm1lc3NhZ2UpO1xuICAgICAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgICAgIC8vIEluIHByb2R1Y3Rpb24sIGhhbmRsZSB3YXJuaW5ncyBub3JtYWxseVxuICAgICAgICAgICAgICAgIGhhbmRsZXIod2FybmluZyk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pXG4gICAgXSxcblxuICAgIC8vIENvbmZpZ3VyZSBidWlsZCBvdXRwdXQgdG8gRmxhc2sncyBzdGF0aWMgZGlyZWN0b3J5XG4gICAgYnVpbGQ6IHtcbiAgICAgICAgb3V0RGlyOiAnLi4vc3RhdGljL2J1aWxkJyxcbiAgICAgICAgZW1wdHlPdXREaXI6IHRydWUsXG4gICAgICAgIG1hbmlmZXN0OiB0cnVlLFxuICAgICAgICBjc3NDb2RlU3BsaXQ6IHRydWUsXG4gICAgICAgIHJvbGx1cE9wdGlvbnM6IHtcbiAgICAgICAgICAgIGlucHV0OiBlbnRyaWVzLFxuICAgICAgICAgICAgb3V0cHV0OiB7XG4gICAgICAgICAgICAgICAgZW50cnlGaWxlTmFtZXM6ICdqcy9bbmFtZV0uanMnLFxuICAgICAgICAgICAgICAgIGNodW5rRmlsZU5hbWVzOiAnanMvW25hbWVdLVtoYXNoXS5qcycsXG4gICAgICAgICAgICAgICAgYXNzZXRGaWxlTmFtZXM6ICdhc3NldHMvW25hbWVdLVtoYXNoXVtleHRuYW1lXSdcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH0sXG5cbiAgICAvLyBEZXZlbG9wbWVudCBzZXJ2ZXIgY29uZmlndXJhdGlvblxuICAgIHNlcnZlcjoge1xuICAgICAgICBwb3J0OiA1MTczLFxuICAgICAgICBzdHJpY3RQb3J0OiB0cnVlLFxuICAgICAgICBvcmlnaW46ICdodHRwOi8vbG9jYWxob3N0OjUxNzMnLFxuICAgICAgICAvLyBQcm94eSBBUEkgcmVxdWVzdHMgdG8gRmxhc2sgZHVyaW5nIGRldmVsb3BtZW50XG4gICAgICAgIHByb3h5OiB7XG4gICAgICAgICAgICAnL2FwaSc6IHtcbiAgICAgICAgICAgICAgICB0YXJnZXQ6IGBodHRwOi8vbG9jYWxob3N0OiR7Zmxhc2tQb3J0fWAsXG4gICAgICAgICAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgfSxcbiAgICB9LFxuXG4gICAgLy8gUmVzb2x2ZSBwYXRoc1xuICAgIHJlc29sdmU6IHtcbiAgICAgICAgYWxpYXM6IHtcbiAgICAgICAgICAgICdAJzogcmVzb2x2ZShfX2Rpcm5hbWUsICdzcmMnKSxcbiAgICAgICAgfSxcbiAgICB9LFxufSk7ICJdLAogICJtYXBwaW5ncyI6ICI7QUFBMlUsU0FBUyxvQkFBb0I7QUFDeFcsU0FBUyxjQUFjO0FBQ3ZCLFNBQVMsZUFBZTtBQUZ4QixJQUFNLG1DQUFtQztBQUt6QyxJQUFNLFlBQVksUUFBUSxJQUFJO0FBQzlCLElBQUksUUFBUSxJQUFJLGFBQWEsZ0JBQWdCLENBQUMsV0FBVztBQUNyRCxVQUFRLE1BQU0sbURBQW1EO0FBQ2pFLFVBQVEsS0FBSyxDQUFDO0FBQ2xCO0FBR0EsSUFBTSxVQUFVO0FBQUEsRUFDWixrQkFBa0IsUUFBUSxrQ0FBVywrQkFBK0I7QUFBQSxFQUNwRSxzQkFBc0IsUUFBUSxrQ0FBVyxtQ0FBbUM7QUFBQSxFQUM1RSxzQkFBc0IsUUFBUSxrQ0FBVyxtQ0FBbUM7QUFDaEY7QUFHQSxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUN4QixTQUFTO0FBQUEsSUFDTCxPQUFPO0FBQUE7QUFBQSxNQUVILFFBQVEsQ0FBQyxTQUFTLFlBQVk7QUFFMUIsZ0JBQVEsTUFBTSxtQkFBbUIsUUFBUSxPQUFPO0FBR2hELFlBQUksUUFBUSxJQUFJLGFBQWEsY0FBYztBQUN2QyxnQkFBTSxJQUFJLE1BQU0sUUFBUSxPQUFPO0FBQUEsUUFDbkM7QUFHQSxnQkFBUSxPQUFPO0FBQUEsTUFDbkI7QUFBQSxJQUNKLENBQUM7QUFBQSxFQUNMO0FBQUE7QUFBQSxFQUdBLE9BQU87QUFBQSxJQUNILFFBQVE7QUFBQSxJQUNSLGFBQWE7QUFBQSxJQUNiLFVBQVU7QUFBQSxJQUNWLGNBQWM7QUFBQSxJQUNkLGVBQWU7QUFBQSxNQUNYLE9BQU87QUFBQSxNQUNQLFFBQVE7QUFBQSxRQUNKLGdCQUFnQjtBQUFBLFFBQ2hCLGdCQUFnQjtBQUFBLFFBQ2hCLGdCQUFnQjtBQUFBLE1BQ3BCO0FBQUEsSUFDSjtBQUFBLEVBQ0o7QUFBQTtBQUFBLEVBR0EsUUFBUTtBQUFBLElBQ0osTUFBTTtBQUFBLElBQ04sWUFBWTtBQUFBLElBQ1osUUFBUTtBQUFBO0FBQUEsSUFFUixPQUFPO0FBQUEsTUFDSCxRQUFRO0FBQUEsUUFDSixRQUFRLG9CQUFvQixTQUFTO0FBQUEsUUFDckMsY0FBYztBQUFBLE1BQ2xCO0FBQUEsSUFDSjtBQUFBLEVBQ0o7QUFBQTtBQUFBLEVBR0EsU0FBUztBQUFBLElBQ0wsT0FBTztBQUFBLE1BQ0gsS0FBSyxRQUFRLGtDQUFXLEtBQUs7QUFBQSxJQUNqQztBQUFBLEVBQ0o7QUFDSixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
