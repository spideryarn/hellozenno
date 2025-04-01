// vite.config.js
import { defineConfig } from "file:///Users/greg/Dropbox/dev/experim/hellozenno/frontend/node_modules/vite/dist/node/index.js";
import { svelte } from "file:///Users/greg/Dropbox/dev/experim/hellozenno/frontend/node_modules/@sveltejs/vite-plugin-svelte/src/index.js";
import { resolve } from "path";
var __vite_injected_original_dirname = "/Users/greg/Dropbox/dev/experim/hellozenno/frontend";
var flaskPort = process.env.FLASK_PORT;
if (!flaskPort) {
  console.error("Error: FLASK_PORT environment variable is not set");
  process.exit(1);
}
var vite_config_default = defineConfig({
  plugins: [svelte()],
  // Configure build output to Flask's static directory
  build: {
    outDir: "../static/build",
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        "helloworld-entry": resolve(__vite_injected_original_dirname, "src/entries/helloworld-entry.ts"),
        "styles": resolve(__vite_injected_original_dirname, "src/styles/tailwind.css")
        // Add more entry points as needed for different pages
      },
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
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMvZ3JlZy9Ecm9wYm94L2Rldi9leHBlcmltL2hlbGxvemVubm8vZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIi9Vc2Vycy9ncmVnL0Ryb3Bib3gvZGV2L2V4cGVyaW0vaGVsbG96ZW5uby9mcm9udGVuZC92aXRlLmNvbmZpZy5qc1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vVXNlcnMvZ3JlZy9Ecm9wYm94L2Rldi9leHBlcmltL2hlbGxvemVubm8vZnJvbnRlbmQvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJztcbmltcG9ydCB7IHN2ZWx0ZSB9IGZyb20gJ0BzdmVsdGVqcy92aXRlLXBsdWdpbi1zdmVsdGUnO1xuaW1wb3J0IHsgcmVzb2x2ZSB9IGZyb20gJ3BhdGgnO1xuXG4vLyBDaGVjayBpZiBGbGFzayBwb3J0IGlzIHNwZWNpZmllZCBpbiBlbnZpcm9ubWVudFxuY29uc3QgZmxhc2tQb3J0ID0gcHJvY2Vzcy5lbnYuRkxBU0tfUE9SVDtcbmlmICghZmxhc2tQb3J0KSB7XG4gICAgY29uc29sZS5lcnJvcignRXJyb3I6IEZMQVNLX1BPUlQgZW52aXJvbm1lbnQgdmFyaWFibGUgaXMgbm90IHNldCcpO1xuICAgIHByb2Nlc3MuZXhpdCgxKTtcbn1cblxuLy8gaHR0cHM6Ly92aXRlanMuZGV2L2NvbmZpZy9cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gICAgcGx1Z2luczogW3N2ZWx0ZSgpXSxcblxuICAgIC8vIENvbmZpZ3VyZSBidWlsZCBvdXRwdXQgdG8gRmxhc2sncyBzdGF0aWMgZGlyZWN0b3J5XG4gICAgYnVpbGQ6IHtcbiAgICAgICAgb3V0RGlyOiAnLi4vc3RhdGljL2J1aWxkJyxcbiAgICAgICAgZW1wdHlPdXREaXI6IHRydWUsXG4gICAgICAgIG1hbmlmZXN0OiB0cnVlLFxuICAgICAgICByb2xsdXBPcHRpb25zOiB7XG4gICAgICAgICAgICBpbnB1dDoge1xuICAgICAgICAgICAgICAgICdoZWxsb3dvcmxkLWVudHJ5JzogcmVzb2x2ZShfX2Rpcm5hbWUsICdzcmMvZW50cmllcy9oZWxsb3dvcmxkLWVudHJ5LnRzJyksXG4gICAgICAgICAgICAgICAgJ3N0eWxlcyc6IHJlc29sdmUoX19kaXJuYW1lLCAnc3JjL3N0eWxlcy90YWlsd2luZC5jc3MnKSxcbiAgICAgICAgICAgICAgICAvLyBBZGQgbW9yZSBlbnRyeSBwb2ludHMgYXMgbmVlZGVkIGZvciBkaWZmZXJlbnQgcGFnZXNcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICBvdXRwdXQ6IHtcbiAgICAgICAgICAgICAgICBlbnRyeUZpbGVOYW1lczogJ2pzL1tuYW1lXS5qcycsXG4gICAgICAgICAgICAgICAgY2h1bmtGaWxlTmFtZXM6ICdqcy9bbmFtZV0tW2hhc2hdLmpzJyxcbiAgICAgICAgICAgICAgICBhc3NldEZpbGVOYW1lczogJ2Fzc2V0cy9bbmFtZV0tW2hhc2hdW2V4dG5hbWVdJyxcbiAgICAgICAgICAgIH0sXG4gICAgICAgIH0sXG4gICAgfSxcblxuICAgIC8vIERldmVsb3BtZW50IHNlcnZlciBjb25maWd1cmF0aW9uXG4gICAgc2VydmVyOiB7XG4gICAgICAgIHBvcnQ6IDUxNzMsXG4gICAgICAgIHN0cmljdFBvcnQ6IHRydWUsXG4gICAgICAgIG9yaWdpbjogJ2h0dHA6Ly9sb2NhbGhvc3Q6NTE3MycsXG4gICAgICAgIC8vIFByb3h5IEFQSSByZXF1ZXN0cyB0byBGbGFzayBkdXJpbmcgZGV2ZWxvcG1lbnRcbiAgICAgICAgcHJveHk6IHtcbiAgICAgICAgICAgICcvYXBpJzoge1xuICAgICAgICAgICAgICAgIHRhcmdldDogYGh0dHA6Ly9sb2NhbGhvc3Q6JHtmbGFza1BvcnR9YCxcbiAgICAgICAgICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICAgICAgICB9LFxuICAgICAgICB9LFxuICAgIH0sXG5cbiAgICAvLyBSZXNvbHZlIHBhdGhzXG4gICAgcmVzb2x2ZToge1xuICAgICAgICBhbGlhczoge1xuICAgICAgICAgICAgJ0AnOiByZXNvbHZlKF9fZGlybmFtZSwgJ3NyYycpLFxuICAgICAgICB9LFxuICAgIH0sXG59KTsgIl0sCiAgIm1hcHBpbmdzIjogIjtBQUEyVSxTQUFTLG9CQUFvQjtBQUN4VyxTQUFTLGNBQWM7QUFDdkIsU0FBUyxlQUFlO0FBRnhCLElBQU0sbUNBQW1DO0FBS3pDLElBQU0sWUFBWSxRQUFRLElBQUk7QUFDOUIsSUFBSSxDQUFDLFdBQVc7QUFDWixVQUFRLE1BQU0sbURBQW1EO0FBQ2pFLFVBQVEsS0FBSyxDQUFDO0FBQ2xCO0FBR0EsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDeEIsU0FBUyxDQUFDLE9BQU8sQ0FBQztBQUFBO0FBQUEsRUFHbEIsT0FBTztBQUFBLElBQ0gsUUFBUTtBQUFBLElBQ1IsYUFBYTtBQUFBLElBQ2IsVUFBVTtBQUFBLElBQ1YsZUFBZTtBQUFBLE1BQ1gsT0FBTztBQUFBLFFBQ0gsb0JBQW9CLFFBQVEsa0NBQVcsaUNBQWlDO0FBQUEsUUFDeEUsVUFBVSxRQUFRLGtDQUFXLHlCQUF5QjtBQUFBO0FBQUEsTUFFMUQ7QUFBQSxNQUNBLFFBQVE7QUFBQSxRQUNKLGdCQUFnQjtBQUFBLFFBQ2hCLGdCQUFnQjtBQUFBLFFBQ2hCLGdCQUFnQjtBQUFBLE1BQ3BCO0FBQUEsSUFDSjtBQUFBLEVBQ0o7QUFBQTtBQUFBLEVBR0EsUUFBUTtBQUFBLElBQ0osTUFBTTtBQUFBLElBQ04sWUFBWTtBQUFBLElBQ1osUUFBUTtBQUFBO0FBQUEsSUFFUixPQUFPO0FBQUEsTUFDSCxRQUFRO0FBQUEsUUFDSixRQUFRLG9CQUFvQixTQUFTO0FBQUEsUUFDckMsY0FBYztBQUFBLE1BQ2xCO0FBQUEsSUFDSjtBQUFBLEVBQ0o7QUFBQTtBQUFBLEVBR0EsU0FBUztBQUFBLElBQ0wsT0FBTztBQUFBLE1BQ0gsS0FBSyxRQUFRLGtDQUFXLEtBQUs7QUFBQSxJQUNqQztBQUFBLEVBQ0o7QUFDSixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
