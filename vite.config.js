import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: '.',
  publicDir: false,
  appType: 'custom',
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      // Proxy everything to Flask
      '/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        bypass: (req) => {
          // Only let Vite handle its own HMR/module requests
          if (
            req.url.startsWith('/@') ||
            req.url.startsWith('/node_modules') ||
            req.url.startsWith('/frontend') ||
            req.url.includes('.ts') ||
            req.url.includes('.tsx') ||
            req.url.includes('.js?') ||
            req.url.includes('?import')
          ) {
            return req.url;
          }
          // Everything else goes to Flask
          return null;
        }
      }
    }
  },
  build: {
    outDir: 'backend/static/dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: 'frontend/src/index.ts'
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src')
    }
  }
});
