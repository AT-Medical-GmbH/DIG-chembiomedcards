<script lang="ts">
  // Rücksprung von Authentik: Code tauschen, dann zur ursprünglichen Seite.
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { api } from '#lib/api.ts';
  import { handleCallback, type AuthConfig } from '#lib/oidc.ts';
  import { session } from '#lib/session.svelte.ts';

  let error = $state<string | null>(null);

  (async () => {
    try {
      const cfg = await api<{ mode: 'local' } | AuthConfig>('/api/auth/config');
      if (cfg.mode !== 'oidc') { await goto('/', { replaceState: true }); return; }
      session.authMode = 'oidc';
      session.authConfig = cfg;
      const returnTo = await handleCallback(cfg, page.url);
      session.needsLogin = false;
      await goto(returnTo, { replaceState: true });   // Code/State aus der Adresszeile entfernen
      session.version += 1;
    } catch (e) {
      error = (e as Error).message;
    }
  })();
</script>

{#if error}
  <div class="panel">
    <h1>Anmeldung nicht abgeschlossen</h1>
    <p class="banner" role="alert">{error}</p>
    <a class="btn primary" href="/">Zur Startseite</a>
  </div>
{:else}
  <p class="muted">Anmeldung wird abgeschlossen …</p>
{/if}
