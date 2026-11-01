import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';

// SvelteKit 3: Konfiguration im Vite-Plugin (svelte.config.js wird nicht mehr gelesen).
// Statische SPA: wird von nginx (pharma-web) ausgeliefert, /api geht an pharma-api.
export default defineConfig({
  plugins: [
    sveltekit({
      preprocess: vitePreprocess(),
      adapter: adapter({ fallback: 'index.html' }),
      paths: { relative: false },
      // CSP mit Hashes: das von SvelteKit erzeugte Inline-Script wird per Hash erlaubt,
      // fremde Scripts nie. frame-ancestors setzt nginx (Moodle-/WordPress-Einbettung).
      csp: {
        mode: 'hash',
        directives: {
          'default-src': ['self'],
          'script-src': ['self'],
          'style-src': ['self', 'unsafe-inline'],
          'img-src': ['self', 'data:', 'blob:'],
          'connect-src': ['self'],
          'object-src': ['none'],
          'base-uri': ['self']
        }
      }
    })
  ],
  server: {
    // Lokale Entwicklung: API-Aufrufe an das FastAPI-Backend weiterreichen
    proxy: { '/api': 'http://127.0.0.1:8000' }
  }
});
