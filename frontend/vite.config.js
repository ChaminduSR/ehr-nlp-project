import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: '.',
  server: {
    port: 5173,
    proxy: {
      // Proxy API calls to the backend running on port 8000
      '/api': {
        // use explicit IPv4 loopback to avoid localhost resolving to IPv6 ::1
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      }
    }
  },
  build: {
    manifest: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('konva') || id.includes('react-konva')) return 'konva'
            if (id.includes('react') || id.includes('react-dom')) return 'react-vendor'
            return 'vendor'
          }
        }
      }
    }
  }
})
