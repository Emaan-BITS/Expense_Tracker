import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Where the FastAPI backend is listening. Override it if port 8000 is taken,
// or when the e2e suite runs its own backend on a different port:
//
//     VITE_API_TARGET=http://127.0.0.1:8001 npm run dev
const API_TARGET = process.env.VITE_API_TARGET || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    // The frontend is on :5173 and the API on :8000 — two origins, which would
    // normally mean setting up CORS. Proxying instead means the browser only
    // ever calls its own origin, so there's nothing to configure.
    proxy: {
      '/api': API_TARGET,
    },
  },
})
