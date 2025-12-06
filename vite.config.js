import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: 'frontend/src',
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        bypass: (req) => {
          if (req.headers.accept && req.headers.accept.includes('html')) {
            return false; // Let Flask handle HTML
          }
        }
      }
    }
  },
  build: {
    outDir: '../../backend/static/dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: 'frontend/src/index.js'
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src')
    }
  }
});
