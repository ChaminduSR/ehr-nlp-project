import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: '.',
  publicDir: false,
  appType: 'custom',

  server: {
    port: 5173,
    strictPort: true,
    warmup: {
      clientFiles: ['./frontend/src/index.ts']
    },
    proxy: {
      '/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        bypass: (req) => {
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
          return null;
        }
      }
    }
  },

  build: {
    outDir: 'backend/static/dist',
    emptyOutDir: true,
    sourcemap: true,
    // Vite 7 default: targets chrome107, edge107, firefox104, safari16
    target: 'baseline-widely-available',
    // Vite 7: faster CSS minification with LightningCSS
    cssMinify: 'lightningcss',
    rollupOptions: {
      input: 'frontend/src/index.ts',
      output: {
        entryFileNames: 'index.js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src')
    }
  },

  optimizeDeps: {
    include: ['alpinejs', 'htmx.org', 'konva', 'date-fns']
  }
});
