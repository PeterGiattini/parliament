import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/debate': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/agents': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/panels': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/export': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/import': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}) 
