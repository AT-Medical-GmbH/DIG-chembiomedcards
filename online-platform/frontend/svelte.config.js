import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** Statische SPA: wird von nginx (pharma-web) ausgeliefert, /api geht an pharma-api. */
export default {
  preprocess: vitePreprocess(),
  kit: {
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
  }
};
