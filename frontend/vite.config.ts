import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    // Explicitly set VITE_BACKEND_API_URL to empty string for production build
    // This will be replaced at build time
    'import.meta.env.VITE_BACKEND_API_URL': JSON.stringify(process.env.VITE_BACKEND_API_URL || ''),
  },
})
