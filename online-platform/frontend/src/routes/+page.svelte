<script lang="ts">
  import { api } from '#lib/api.ts';
  import { session } from '#lib/session.svelte.ts';

  type Stats = {
    gesamt: Record<string, number>; heute_bewertet: number; tagesziel: number;
    kategorien: { slug: string; name: string; gesamt: number; neu?: number; in_arbeit?: number; beherrscht?: number; faellig?: number }[];
  };
  type SetInfo = { slug: string; name: string; total?: number };

  let stats = $state<Stats | null>(null);
  let contentSets = $state<SetInfo[]>([]);
  let userSets = $state<SetInfo[]>([]);
  let error = $state<string | null>(null);

  async function load() {
    try {
      const [s, sets] = await Promise.all([
        api<Stats>('/api/stats'),
        api<{ content_sets: SetInfo[]; user_sets: SetInfo[] }>('/api/sets')
      ]);
      stats = s;
      const count = (x: SetInfo) => api<{ total: number }>(`/api/learn/queue?set=${x.slug}&limit=1`)
        .then((q) => ({ ...x, total: q.total }));
      // parallel laden, damit die Kacheln gemeinsam erscheinen (kein Springen der Seite)
      [contentSets, userSets] = await Promise.all([
        Promise.all(sets.content_sets.map(count)), Promise.all(sets.user_sets.map(count))]);
    } catch (e) {
      error = (e as Error).message;
    }
  }
  load();

  const pct = (a = 0, b = 0) => (b ? Math.round((a / b) * 100) : 0);
  let goal = $derived(stats ? Math.min(100, pct(stats.heute_bewertet, stats.tagesziel)) : 0);
</script>

<h1>Übersicht</h1>
{#if error}
  <p class="banner" role="alert">{error}</p>
{:else if stats}
  {#if stats.gesamt.gesamt === undefined || stats.gesamt.gesamt === 0}
    <div class="panel empty">
      <h2>Noch keine freigegebenen Karten</h2>
      <p>Karten werden erst nach dem fachlichen Review für Lernende freigeschaltet.
        {#if session.authMode === 'local'}Zum Ausprobieren oben eine Review-Rolle als Test-Identität wählen.{/if}</p>
    </div>
  {:else}
    <section class="grid kpis" aria-label="Lernstand">
      <div class="panel kpi"><span class="muted small">Heute bewertet</span>
        <strong>{stats.heute_bewertet} / {stats.tagesziel}</strong>
        <div class="progress" aria-label="Tagesziel {goal} %"><span style:width="{goal}%"></span></div></div>
      <div class="panel kpi"><span class="muted small">Fällig</span><strong>{stats.gesamt.faellig ?? 0}</strong></div>
      <div class="panel kpi"><span class="muted small">Beherrscht</span><strong>{stats.gesamt.beherrscht ?? 0}</strong></div>
      <div class="panel kpi"><span class="muted small">Karten</span><strong>{stats.gesamt.gesamt}</strong></div>
    </section>

    <h2 class="h">Lernen starten</h2>
    <div class="grid cols-auto">
      {#each [...userSets.filter((s) => ['faellig', 'neu', 'unsicher'].includes(s.slug)), ...contentSets] as s (s.slug)}
        <a class="panel tile" class:disabled={!s.total} href={s.total ? `/lernen?set=${s.slug}` : undefined}
          aria-disabled={!s.total}>
          <span>{s.name}</span><strong>{s.total ?? '–'}</strong>
        </a>
      {/each}
    </div>

    <h2 class="h">Markiert</h2>
    <div class="grid cols-auto">
      {#each userSets.filter((s) => !['faellig', 'neu', 'unsicher'].includes(s.slug)) as s (s.slug)}
        <a class="panel tile" class:disabled={!s.total} href={s.total ? `/lernen?set=${s.slug}` : undefined}
          aria-disabled={!s.total}><span>{s.name}</span><strong>{s.total ?? '–'}</strong></a>
      {/each}
    </div>

    <h2 class="h">Fortschritt nach Kategorie</h2>
    <div class="panel">
      <table>
        <thead><tr><th scope="col">Kategorie</th><th scope="col">Karten</th><th scope="col">beherrscht</th><th scope="col">fällig</th><th scope="col" class="bar-col">Fortschritt</th></tr></thead>
        <tbody>
          {#each stats.kategorien as k (k.slug)}
            <tr>
              <th scope="row"><a href="/lernen?set=alle&category={k.slug}">{k.name}</a></th>
              <td>{k.gesamt}</td><td>{k.beherrscht ?? 0}</td><td>{k.faellig ?? 0}</td>
              <td class="bar-col"><div class="progress" aria-label="{pct(k.beherrscht, k.gesamt)} % beherrscht">
                <span style:width="{pct(k.beherrscht, k.gesamt)}%"></span></div></td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
{:else}
  <p class="muted">Lade Lernstand …</p>
{/if}

<style>
  .kpis { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin-bottom: var(--sp-3); }
  .kpi { display: flex; flex-direction: column; gap: 6px; }
  .kpi strong { font-size: 1.6rem; }
  .h { margin-top: var(--sp-4); }
  .tile { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-2);
    text-decoration: none; color: var(--app-text); font-weight: 600; min-height: 64px; }
  .tile strong { font-size: 1.3rem; color: var(--app-primary); }
  .tile:hover { border-color: #b9c4c9; }
  .tile.disabled { opacity: .55; pointer-events: none; }
  .empty { max-width: 640px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid var(--app-line); }
  thead th { font-size: .8rem; color: var(--app-text-soft); text-transform: uppercase; letter-spacing: .03em; }
  tbody th { font-weight: 600; }
  .bar-col { width: 32%; }
  @media (max-width: 640px) { .bar-col { display: none; } }
</style>
