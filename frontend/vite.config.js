import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The dev server forwards API and docs paths to FastAPI, so the browser sees one origin.
const api = process.env.API_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: Object.fromEntries(['/api', '/v1', '/docs', '/redoc', '/openapi.json'].map((p) => [p, api])),
  },
})
