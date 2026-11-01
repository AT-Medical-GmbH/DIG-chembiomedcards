<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';
  import { api } from '$lib/api';
  import { DEV_USERS, session } from '$lib/session.svelte';

  let { children } = $props();
  let ready = $state(false);
  let startError = $state<string | null>(null);

  $effect(() => {
    void session.version;  // bei Identitätswechsel neu laden
    api<{ auth_mode: 'local' | 'oidc' }>('/api/health')
      .then((h) => { session.authMode = h.auth_mode; return api<typeof session.me>('/api/me'); })
      .then((me) => { session.me = me; ready = true; })
      .catch((e) => (startError = e.message));
  });

  const nav = [
    { href: '/', label: 'Übersicht' },
    { href: '/lernen', label: 'Lernen' },
    { href: '/karten', label: 'Karten' },
    { href: '/antidote', label: 'Antidote' },
    { href: '/notizen', label: 'Notizen' }
  ];
  const active = (href: string) => (href === '/' ? page.url.pathname === '/' : page.url.pathname.startsWith(href));
</script>

<a class="skip" href="#main">Zum Inhalt springen</a>
<header class="top">
  <div class="container bar">
    <a class="brand" href="/" aria-label="Pharma Cards – Übersicht">
      <span class="mark" aria-hidden="true">PH</span>
      <span><strong>Pharma Cards</strong><span class="by muted small">AT Medical</span></span>
    </a>
    <nav aria-label="Hauptnavigation">
      {#each nav as item}
        <a href={item.href} aria-current={active(item.href) ? 'page' : undefined}>{item.label}</a>
      {/each}
    </nav>
    {#if session.authMode === 'local'}
      <label class="dev small">
        <span class="muted">Test-Identität</span>
        <select value={session.user.subject}
          onchange={(e) => session.setUser(DEV_USERS.find((u) => u.subject === (e.currentTarget as HTMLSelectElement).value)!)}>
          {#each DEV_USERS as u}<option value={u.subject}>{u.label}</option>{/each}
        </select>
      </label>
    {/if}
  </div>
</header>

{#if session.me?.dev_show_unreviewed}
  <div class="container devwarn">
    <p class="banner small" role="status"><strong>Entwicklungsmodus:</strong>&nbsp;Ungeprüfte Entwürfe sind für alle sichtbar. In Produktion ist das gesperrt.</p>
  </div>
{/if}

<main id="main" class="container">
  {#if startError}
    <p class="banner" role="alert">Die Anwendung konnte nicht starten: {startError}</p>
  {:else if ready}
    {#key session.version}{@render children()}{/key}
  {:else}
    <p class="muted">Lade …</p>
  {/if}
</main>

<footer class="container foot muted small">
  <p>Pharma Cards ist <strong>Ausbildungs- und Lernmaterial – keine Therapieanweisung.</strong>
    Dosierungen und klinische Entscheidungen richten sich nach aktuellen Leitlinien und Fachinformationen.</p>
  <p>© 2026 Andreas Tremml · AT Medical GmbH</p>
</footer>

<style>
  .skip { position: absolute; left: -999px; top: 8px; background: #fff; padding: 8px 12px; border-radius: 6px; z-index: 10; }
  .skip:focus { left: 8px; }
  .top { background: var(--app-surface); border-bottom: 1px solid var(--app-line); position: sticky; top: 0; z-index: 5; }
  .bar { display: flex; align-items: center; gap: var(--sp-3); padding-top: 10px; padding-bottom: 10px; flex-wrap: wrap; }
  .brand { display: flex; align-items: center; gap: 10px; text-decoration: none; color: var(--app-text); }
  .brand .by { display: block; line-height: 1; }
  .mark { display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 8px;
    background: var(--app-primary); color: #fff; font-weight: 800; font-size: .85rem;
    box-shadow: inset 0 -3px 0 var(--app-ph); }
  nav { display: flex; gap: 2px; flex-wrap: wrap; }
  nav a { padding: 8px 12px; border-radius: 8px; text-decoration: none; color: var(--app-text-soft); font-weight: 600; }
  nav a:hover { background: var(--app-surface-2); color: var(--app-text); }
  nav a[aria-current='page'] { background: var(--app-surface-2); color: var(--app-text); }
  .dev { margin-left: auto; display: flex; align-items: center; gap: 8px; }
  .dev select { min-height: 36px; width: auto; padding: 4px 8px; }
  .devwarn { padding-bottom: 0; }
  .foot { padding-top: 0; border-top: 1px solid var(--app-line); margin-top: var(--sp-4); padding-top: var(--sp-3); }
  @media (max-width: 640px) { .dev { margin-left: 0; width: 100%; } }
</style>
