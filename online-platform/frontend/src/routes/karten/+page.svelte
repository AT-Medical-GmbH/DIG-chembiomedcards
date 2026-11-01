<script lang="ts">
  // Kartenübersicht: Suche (Wirkstoff, Klasse, Indikation, Nebenwirkung, Antidot, Toxidrom) und
  // Filter nach Kategorie, Wirkstoffgruppe, Tag und Warnlevel.
  import { api, statusLabel, warnLabel, type CardSummary } from '$lib/api';

  type Opt = { slug: string; name: string; count?: number };
  let meta = $state<{ categories: Opt[]; drug_classes: Opt[]; tags: Opt[] } | null>(null);
  let q = $state('');
  let category = $state('');
  let drugClass = $state('');
  let tag = $state('');
  let warning = $state('');
  let cards = $state<CardSummary[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let timer: ReturnType<typeof setTimeout> | undefined;

  api<typeof meta>('/api/meta').then((m) => (meta = m)).catch((e) => (error = e.message));

  $effect(() => {
    const params = new URLSearchParams();
    if (q.trim()) params.set('q', q.trim());
    if (category) params.set('category', category);
    if (drugClass) params.set('drug_class', drugClass);
    if (tag) params.set('tag', tag);
    if (warning) params.set('warning_level', warning);
    clearTimeout(timer);
    timer = setTimeout(() => {
      loading = true;
      api<{ cards: CardSummary[] }>(`/api/cards?${params}`)
        .then((r) => { cards = r.cards; error = null; })
        .catch((e) => (error = e.message))
        .finally(() => (loading = false));
    }, 200);
  });
</script>

<h1>Karten</h1>
<div class="panel filters" role="search">
  <label class="q"><span class="sr-only">Suche</span>
    <input type="search" bind:value={q} placeholder="Suche: Wirkstoff, Klasse, Indikation, Nebenwirkung, Antidot …" /></label>
  <label><span class="small muted">Kategorie</span>
    <select bind:value={category}><option value="">alle</option>
      {#each meta?.categories ?? [] as c}<option value={c.slug}>{c.name} ({c.count})</option>{/each}</select></label>
  <label><span class="small muted">Wirkstoffgruppe</span>
    <select bind:value={drugClass}><option value="">alle</option>
      {#each meta?.drug_classes ?? [] as d}<option value={d.slug}>{d.name}</option>{/each}</select></label>
  <label><span class="small muted">Tag</span>
    <select bind:value={tag}><option value="">alle</option>
      {#each meta?.tags ?? [] as t}<option value={t.slug}>{t.name}</option>{/each}</select></label>
  <label><span class="small muted">Warnlevel</span>
    <select bind:value={warning}><option value="">alle</option>
      {#each ['low', 'moderate', 'high', 'critical'] as w}<option value={w}>{warnLabel[w]}</option>{/each}</select></label>
</div>

{#if error}<p class="banner" role="alert">{error}</p>{/if}
<p class="muted small" aria-live="polite">{loading ? 'Suche …' : `${cards.length} Karte(n)`}</p>

<ul class="list">
  {#each cards as c (c.card_id)}
    <li class="panel row">
      <a href="/karten/{c.card_id}">
        <span class="id muted small">{c.card_id}</span>
        <span class="title"><strong>{c.title}</strong>{#if c.subtitle}<span class="muted small"> · {c.subtitle}</span>{/if}</span>
      </a>
      <span class="chips">
        <span class="chip {c.warning_level}">{warnLabel[c.warning_level]}</span>
        {#if c.draft}<span class="chip draft">Entwurf</span>{/if}
        {#if c.progress}<span class="chip">{statusLabel[c.progress.status] ?? c.progress.status}</span>{/if}
      </span>
    </li>
  {/each}
</ul>

<style>
  .filters { display: grid; gap: var(--sp-2); grid-template-columns: 2fr repeat(4, 1fr); align-items: end; margin-bottom: var(--sp-3); }
  .filters label { display: flex; flex-direction: column; gap: 4px; }
  @media (max-width: 900px) { .filters { grid-template-columns: 1fr 1fr; } .q { grid-column: 1 / -1; } }
  .list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
  .row { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-2); padding: 12px 16px; flex-wrap: wrap; }
  .row a { display: flex; gap: 12px; align-items: baseline; text-decoration: none; color: var(--app-text); flex: 1 1 320px; }
  .row a:hover strong { text-decoration: underline; }
  .id { font-family: ui-monospace, monospace; min-width: 56px; }
  .chips { display: flex; gap: 6px; flex-wrap: wrap; }
</style>
