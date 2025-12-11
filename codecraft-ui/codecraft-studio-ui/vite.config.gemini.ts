import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
// Gemini version - runs on port 9090
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 9090,
    proxy: {
      '/api': {
        target: 'http://localhost:9090',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      // Alias api.ts to api.gemini.ts for Gemini version
      "@/services/api$": path.resolve(__dirname, "./src/services/api.gemini.ts"),
    },
  },
  define: {
    'import.meta.env.VITE_USE_GEMINI': JSON.stringify('true'),
  },
}));
