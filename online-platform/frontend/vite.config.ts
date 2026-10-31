import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    // Lokale Entwicklung: API-Aufrufe an das FastAPI-Backend weiterreichen
    proxy: { '/api': 'http://127.0.0.1:8000' }
  }
});
