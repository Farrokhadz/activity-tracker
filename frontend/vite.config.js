import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // In development, requests to /api are forwarded to the Django server,
    // so the frontend can call the API without dealing with CORS.
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
